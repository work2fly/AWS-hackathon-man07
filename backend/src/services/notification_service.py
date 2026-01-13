"""
Notification and Escalation Service for AI Therapy Platform
Handles multi-channel notifications, therapist alerts, and escalation logic
🏆 Breaking Barriers UK 2026 compliant
"""

import json
import boto3
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from ..models.notification import Notification, NotificationType, Priority
from ..models.red_flag import RedFlag, RedFlagType, Severity, NotificationRecord, NotificationMethod
from ..data.notification_repository import NotificationRepository
from ..data.red_flag_repository import RedFlagRepository
from ..data.user_repository import UserRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EscalationLevel(str, Enum):
    """Escalation level enumeration"""
    NONE = "none"
    THERAPIST = "therapist"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    EMERGENCY = "emergency"


class NotificationService:
    """Service for managing notifications and escalations"""
    
    def __init__(self):
        self.notification_repo = NotificationRepository()
        self.red_flag_repo = RedFlagRepository()
        self.user_repo = UserRepository()
        
        # Initialize AWS services for hackathon (simplified)
        try:
            self.sns_client = boto3.client('sns', region_name='us-west-2')
            self.ses_client = boto3.client('ses', region_name='us-west-2')
        except Exception as e:
            logger.warning(f"Failed to initialize AWS clients: {str(e)}")
            self.sns_client = None
            self.ses_client = None
        
        # Escalation thresholds
        self._escalation_rules = {
            'multiple_flags_threshold': 3,  # Number of flags to trigger escalation
            'critical_flag_immediate': True,  # Immediate escalation for critical flags
            'time_window_minutes': 60,  # Time window for counting multiple flags
            'max_escalation_attempts': 3,  # Maximum escalation attempts
            'escalation_delay_minutes': 15  # Delay between escalation attempts
        }
    
    def send_red_flag_notification(self, red_flag: RedFlag, client_id: str) -> List[NotificationRecord]:
        """
        Send notifications for a red flag detection
        
        Args:
            red_flag: RedFlag object
            client_id: Client identifier for context
            
        Returns:
            List of notification records sent
        """
        try:
            notifications_sent = []
            
            # Determine notification priority based on severity
            priority = self._severity_to_priority(red_flag.severity)
            
            # Get assigned therapists for the client
            therapists = self._get_assigned_therapists(client_id)
            
            if not therapists:
                logger.warning(f"No therapists assigned to client {client_id}")
                # For hackathon, assign to all therapists
                therapists = self._get_all_therapists()
            
            # Create notification message
            notification_title = f"Red Flag Alert: {red_flag.type.value.replace('_', ' ').title()}"
            notification_message = self._create_red_flag_message(red_flag, client_id)
            
            # Send notifications to therapists
            for therapist in therapists:
                # Create in-app notification
                notification = Notification(
                    recipient_id=therapist['user_id'],
                    type=NotificationType.RED_FLAG,
                    priority=priority,
                    title=notification_title,
                    message=notification_message,
                    related_session_id=red_flag.session_id,
                    related_flag_id=red_flag.flag_id,
                    action_required=red_flag.severity in [Severity.HIGH, Severity.CRITICAL]
                )
                
                # Store in-app notification
                success = self.notification_repo.create_notification(notification)
                if success:
                    notifications_sent.append(NotificationRecord(
                        recipient_id=therapist['user_id'],
                        method=NotificationMethod.IN_APP,
                        sent_at=datetime.utcnow()
                    ))
                
                # Send email notification for high/critical flags
                if red_flag.severity in [Severity.HIGH, Severity.CRITICAL]:
                    email_sent = self._send_email_notification(
                        therapist['email'],
                        notification_title,
                        notification_message,
                        red_flag
                    )
                    
                    if email_sent:
                        notifications_sent.append(NotificationRecord(
                            recipient_id=therapist['user_id'],
                            method=NotificationMethod.EMAIL,
                            sent_at=datetime.utcnow()
                        ))
                
                # Send SMS for critical flags
                if red_flag.severity == Severity.CRITICAL and therapist.get('phone'):
                    sms_sent = self._send_sms_notification(
                        therapist['phone'],
                        f"URGENT: {notification_title}",
                        red_flag
                    )
                    
                    if sms_sent:
                        notifications_sent.append(NotificationRecord(
                            recipient_id=therapist['user_id'],
                            method=NotificationMethod.SMS,
                            sent_at=datetime.utcnow()
                        ))
            
            # Check for escalation
            escalation_level = self._determine_escalation_level(red_flag, client_id)
            if escalation_level != EscalationLevel.NONE:
                escalation_notifications = self._handle_escalation(
                    red_flag, client_id, escalation_level
                )
                notifications_sent.extend(escalation_notifications)
            
            logger.info(f"Sent {len(notifications_sent)} notifications for red flag {red_flag.flag_id}")
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Failed to send red flag notifications: {str(e)}")
            return []
    
    def _severity_to_priority(self, severity: Severity) -> Priority:
        """Convert red flag severity to notification priority"""
        severity_map = {
            Severity.LOW: Priority.LOW,
            Severity.MEDIUM: Priority.MEDIUM,
            Severity.HIGH: Priority.HIGH,
            Severity.CRITICAL: Priority.URGENT
        }
        return severity_map.get(severity, Priority.MEDIUM)
    
    def _get_assigned_therapists(self, client_id: str) -> List[Dict[str, Any]]:
        """Get therapists assigned to a client"""
        try:
            # In production, this would query therapist-client assignments
            # For hackathon, we'll return all therapists
            return self._get_all_therapists()
            
        except Exception as e:
            logger.error(f"Failed to get assigned therapists for client {client_id}: {str(e)}")
            return []
    
    def _get_all_therapists(self) -> List[Dict[str, Any]]:
        """Get all therapist users"""
        try:
            # Get users with therapist role
            therapists = self.user_repo.get_users_by_role('therapist')
            
            therapist_list = []
            for therapist in therapists:
                therapist_data = {
                    'user_id': therapist.user_id,
                    'email': therapist.email,
                    'phone': therapist.profile.phone_number if therapist.profile.phone_number else None,
                    'name': f"{therapist.profile.first_name} {therapist.profile.last_name}"
                }
                therapist_list.append(therapist_data)
            
            return therapist_list
            
        except Exception as e:
            logger.error(f"Failed to get all therapists: {str(e)}")
            return []
    
    def _create_red_flag_message(self, red_flag: RedFlag, client_id: str) -> str:
        """Create notification message for red flag"""
        try:
            flag_type_display = red_flag.type.value.replace('_', ' ').title()
            severity_display = red_flag.severity.value.upper()
            
            message = f"""
Red Flag Detection Alert

Type: {flag_type_display}
Severity: {severity_display}
Session: {red_flag.session_id}
Detected: {red_flag.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Context: {red_flag.context}

This alert requires immediate attention. Please review the session and take appropriate action.

Session ID: {red_flag.session_id}
Flag ID: {red_flag.flag_id}
            """.strip()
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to create red flag message: {str(e)}")
            return f"Red flag detected in session {red_flag.session_id}. Please review immediately."
    
    def _send_email_notification(self, email: str, subject: str, message: str, 
                                red_flag: RedFlag) -> bool:
        """Send email notification using AWS SES"""
        try:
            if not self.ses_client:
                logger.warning("SES client not available, skipping email notification")
                return False
            
            # For hackathon, we'll log the email instead of actually sending
            logger.info(f"EMAIL NOTIFICATION (would send to {email}):")
            logger.info(f"Subject: {subject}")
            logger.info(f"Message: {message}")
            
            # In production, this would use SES:
            # response = self.ses_client.send_email(
            #     Source='noreply@ai-therapy-platform.com',
            #     Destination={'ToAddresses': [email]},
            #     Message={
            #         'Subject': {'Data': subject},
            #         'Body': {'Text': {'Data': message}}
            #     }
            # )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification to {email}: {str(e)}")
            return False
    
    def _send_sms_notification(self, phone: str, message: str, red_flag: RedFlag) -> bool:
        """Send SMS notification using AWS SNS"""
        try:
            if not self.sns_client:
                logger.warning("SNS client not available, skipping SMS notification")
                return False
            
            # For hackathon, we'll log the SMS instead of actually sending
            logger.info(f"SMS NOTIFICATION (would send to {phone}):")
            logger.info(f"Message: {message}")
            
            # In production, this would use SNS:
            # response = self.sns_client.publish(
            #     PhoneNumber=phone,
            #     Message=message
            # )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification to {phone}: {str(e)}")
            return False
    
    def _determine_escalation_level(self, red_flag: RedFlag, client_id: str) -> EscalationLevel:
        """Determine if escalation is needed"""
        try:
            # Immediate escalation for critical flags
            if red_flag.severity == Severity.CRITICAL:
                return EscalationLevel.ADMIN
            
            # Check for multiple flags in time window
            time_window = datetime.utcnow() - timedelta(
                minutes=self._escalation_rules['time_window_minutes']
            )
            
            recent_flags = self.red_flag_repo.get_red_flags_by_session(red_flag.session_id)
            recent_flags = [
                flag for flag in recent_flags 
                if flag.detected_at >= time_window
            ]
            
            # Escalate if multiple flags detected
            if len(recent_flags) >= self._escalation_rules['multiple_flags_threshold']:
                return EscalationLevel.SUPERVISOR
            
            # Escalate high severity flags after delay
            if red_flag.severity == Severity.HIGH:
                # Check if this flag has been unresolved for escalation delay
                if (datetime.utcnow() - red_flag.detected_at).total_seconds() > \
                   self._escalation_rules['escalation_delay_minutes'] * 60:
                    return EscalationLevel.SUPERVISOR
            
            return EscalationLevel.NONE
            
        except Exception as e:
            logger.error(f"Failed to determine escalation level: {str(e)}")
            return EscalationLevel.NONE
    
    def _handle_escalation(self, red_flag: RedFlag, client_id: str, 
                          escalation_level: EscalationLevel) -> List[NotificationRecord]:
        """Handle escalation notifications"""
        try:
            notifications_sent = []
            
            # Get escalation recipients
            recipients = self._get_escalation_recipients(escalation_level)
            
            if not recipients:
                logger.warning(f"No recipients found for escalation level {escalation_level}")
                return notifications_sent
            
            # Create escalation message
            escalation_title = f"ESCALATION: Red Flag Alert - {red_flag.type.value.replace('_', ' ').title()}"
            escalation_message = self._create_escalation_message(red_flag, client_id, escalation_level)
            
            # Send escalation notifications
            for recipient in recipients:
                # Create in-app notification
                notification = Notification(
                    recipient_id=recipient['user_id'],
                    type=NotificationType.RED_FLAG,
                    priority=Priority.URGENT,
                    title=escalation_title,
                    message=escalation_message,
                    related_session_id=red_flag.session_id,
                    related_flag_id=red_flag.flag_id,
                    action_required=True
                )
                
                success = self.notification_repo.create_notification(notification)
                if success:
                    notifications_sent.append(NotificationRecord(
                        recipient_id=recipient['user_id'],
                        method=NotificationMethod.IN_APP,
                        sent_at=datetime.utcnow()
                    ))
                
                # Send email for escalations
                email_sent = self._send_email_notification(
                    recipient['email'],
                    escalation_title,
                    escalation_message,
                    red_flag
                )
                
                if email_sent:
                    notifications_sent.append(NotificationRecord(
                        recipient_id=recipient['user_id'],
                        method=NotificationMethod.EMAIL,
                        sent_at=datetime.utcnow()
                    ))
                
                # Send SMS for admin/emergency escalations
                if escalation_level in [EscalationLevel.ADMIN, EscalationLevel.EMERGENCY] and recipient.get('phone'):
                    sms_sent = self._send_sms_notification(
                        recipient['phone'],
                        f"URGENT ESCALATION: {escalation_title}",
                        red_flag
                    )
                    
                    if sms_sent:
                        notifications_sent.append(NotificationRecord(
                            recipient_id=recipient['user_id'],
                            method=NotificationMethod.SMS,
                            sent_at=datetime.utcnow()
                        ))
            
            logger.info(f"Sent {len(notifications_sent)} escalation notifications for level {escalation_level}")
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Failed to handle escalation: {str(e)}")
            return []
    
    def _get_escalation_recipients(self, escalation_level: EscalationLevel) -> List[Dict[str, Any]]:
        """Get recipients for escalation level"""
        try:
            if escalation_level == EscalationLevel.SUPERVISOR:
                # Get senior therapists or supervisors
                return self._get_all_therapists()  # For hackathon, use all therapists
            
            elif escalation_level in [EscalationLevel.ADMIN, EscalationLevel.EMERGENCY]:
                # Get admin users
                admins = self.user_repo.get_users_by_role('admin')
                
                admin_list = []
                for admin in admins:
                    admin_data = {
                        'user_id': admin.user_id,
                        'email': admin.email,
                        'phone': admin.profile.phone_number if admin.profile.phone_number else None,
                        'name': f"{admin.profile.first_name} {admin.profile.last_name}"
                    }
                    admin_list.append(admin_data)
                
                return admin_list
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get escalation recipients: {str(e)}")
            return []
    
    def _create_escalation_message(self, red_flag: RedFlag, client_id: str, 
                                  escalation_level: EscalationLevel) -> str:
        """Create escalation notification message"""
        try:
            flag_type_display = red_flag.type.value.replace('_', ' ').title()
            severity_display = red_flag.severity.value.upper()
            
            message = f"""
ESCALATION ALERT - Immediate Action Required

Escalation Level: {escalation_level.value.upper()}
Red Flag Type: {flag_type_display}
Severity: {severity_display}
Session: {red_flag.session_id}
Client: {client_id}
Detected: {red_flag.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Context: {red_flag.context}

This alert has been escalated due to:
- High severity level
- Multiple red flags detected
- Unresolved safety concern

IMMEDIATE ACTION REQUIRED. Please review and respond immediately.

Session ID: {red_flag.session_id}
Flag ID: {red_flag.flag_id}
            """.strip()
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to create escalation message: {str(e)}")
            return f"ESCALATION: Red flag in session {red_flag.session_id} requires immediate attention."
    
    def send_session_complete_notification(self, session_id: str, client_id: str, 
                                         sentiment_summary: Dict[str, Any]) -> bool:
        """Send notification when session completes"""
        try:
            # Get assigned therapists
            therapists = self._get_assigned_therapists(client_id)
            
            if not therapists:
                logger.warning(f"No therapists assigned to client {client_id}")
                return False
            
            # Create notification message
            title = "Session Completed"
            message = f"""
Therapy session completed for client {client_id}.

Session ID: {session_id}
Completed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Sentiment Summary:
- Overall Sentiment: {sentiment_summary.get('overall_sentiment', 'Unknown')}
- Risk Level: {sentiment_summary.get('risk_level', 'Unknown')}
- Key Topics: {', '.join(sentiment_summary.get('key_topics', []))}

Please review the session summary when convenient.
            """.strip()
            
            # Send to therapists
            for therapist in therapists:
                notification = Notification(
                    recipient_id=therapist['user_id'],
                    type=NotificationType.SESSION_COMPLETE,
                    priority=Priority.LOW,
                    title=title,
                    message=message,
                    related_session_id=session_id,
                    action_required=False
                )
                
                self.notification_repo.create_notification(notification)
            
            logger.info(f"Sent session complete notifications for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send session complete notification: {str(e)}")
            return False
    
    def send_system_alert(self, alert_type: str, message: str, priority: Priority = Priority.MEDIUM,
                         recipients: Optional[List[str]] = None) -> bool:
        """Send system alert notification"""
        try:
            if not recipients:
                # Send to all admins
                admins = self.user_repo.get_users_by_role('admin')
                recipients = [admin.user_id for admin in admins]
            
            title = f"System Alert: {alert_type}"
            
            # Send to recipients
            for recipient_id in recipients:
                notification = Notification(
                    recipient_id=recipient_id,
                    type=NotificationType.SYSTEM_ALERT,
                    priority=priority,
                    title=title,
                    message=message,
                    action_required=priority in [Priority.HIGH, Priority.URGENT]
                )
                
                self.notification_repo.create_notification(notification)
            
            logger.info(f"Sent system alert '{alert_type}' to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send system alert: {str(e)}")
            return False
    
    def acknowledge_notification(self, recipient_id: str, timestamp: str) -> bool:
        """Acknowledge a notification"""
        try:
            return self.notification_repo.mark_notification_as_read(
                recipient_id=recipient_id,
                timestamp=timestamp,
                read_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to acknowledge notification: {str(e)}")
            return False
    
    def get_notification_summary(self, recipient_id: str) -> Dict[str, Any]:
        """Get notification summary for a user"""
        try:
            # Get unread notifications
            unread_result = self.notification_repo.get_notifications_for_user(
                recipient_id=recipient_id,
                unread_only=True,
                limit=100
            )
            
            unread_notifications = unread_result['notifications']
            
            # Count by priority
            priority_counts = {
                Priority.URGENT.value: 0,
                Priority.HIGH.value: 0,
                Priority.MEDIUM.value: 0,
                Priority.LOW.value: 0
            }
            
            action_required_count = 0
            
            for notification in unread_notifications:
                priority_counts[notification.priority.value] += 1
                if notification.action_required:
                    action_required_count += 1
            
            return {
                'total_unread': len(unread_notifications),
                'by_priority': priority_counts,
                'action_required': action_required_count,
                'has_urgent': priority_counts[Priority.URGENT.value] > 0,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get notification summary: {str(e)}")
            return {
                'total_unread': 0,
                'by_priority': {p.value: 0 for p in Priority},
                'action_required': 0,
                'has_urgent': False,
                'error': str(e)
            }
    
    def process_notification_acknowledgments(self, red_flag: RedFlag, 
                                           notifications_sent: List[NotificationRecord]) -> bool:
        """Process and track notification acknowledgments"""
        try:
            # Add notification records to red flag
            for notification in notifications_sent:
                success = self.red_flag_repo.add_notification_record(
                    session_id=red_flag.session_id,
                    flag_id=red_flag.flag_id,
                    notification=notification
                )
                
                if not success:
                    logger.warning(f"Failed to add notification record for {notification.recipient_id}")
            
            logger.info(f"Processed {len(notifications_sent)} notification acknowledgments for flag {red_flag.flag_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process notification acknowledgments: {str(e)}")
            return False
    
    def cleanup_old_notifications(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old notifications"""
        try:
            deleted_count = self.notification_repo.cleanup_old_notifications(days)
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'retention_days': days,
                'cleanup_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old notifications: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'retention_days': days
            }