"""
Red Flag Management and Resolution Service for AI Therapy Platform
Handles red flag review workflows, case management, and audit trails
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from ..models.red_flag import RedFlag, RedFlagType, Severity
from ..models.notification import Notification, NotificationType, Priority
from ..data.red_flag_repository import RedFlagRepository
from ..data.notification_repository import NotificationRepository
from ..data.user_repository import UserRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ResolutionStatus(str, Enum):
    """Resolution status enumeration"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ESCALATED = "escalated"


class ResolutionAction(str, Enum):
    """Resolution action enumeration"""
    NO_ACTION = "no_action"
    THERAPIST_CONTACT = "therapist_contact"
    EMERGENCY_CONTACT = "emergency_contact"
    REFERRAL = "referral"
    FOLLOW_UP = "follow_up"
    CRISIS_INTERVENTION = "crisis_intervention"


class CaseStatus(str, Enum):
    """Case management status"""
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RedFlagManagementService:
    """Service for managing red flag resolution workflows"""
    
    def __init__(self):
        self.red_flag_repo = RedFlagRepository()
        self.notification_repo = NotificationRepository()
        self.user_repo = UserRepository()
        
        # Resolution workflow configuration
        self._workflow_config = {
            'auto_assign_threshold_minutes': 30,  # Auto-assign after 30 minutes
            'escalation_threshold_hours': 2,      # Escalate after 2 hours unresolved
            'follow_up_intervals': [24, 72, 168], # Follow-up after 1, 3, 7 days (hours)
            'case_closure_days': 30,              # Close resolved cases after 30 days
            'audit_retention_days': 2555          # Keep audit logs for 7 years
        }
    
    def create_case(self, red_flag: RedFlag, assigned_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a case for red flag management
        
        Args:
            red_flag: RedFlag object
            assigned_to: Optional user ID to assign case to
            
        Returns:
            Dictionary with case creation results
        """
        try:
            case_id = f"CASE_{red_flag.flag_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine initial assignment
            if not assigned_to:
                assigned_to = self._auto_assign_case(red_flag)
            
            case_data = {
                'case_id': case_id,
                'red_flag_id': red_flag.flag_id,
                'session_id': red_flag.session_id,
                'flag_type': red_flag.type.value,
                'severity': red_flag.severity.value,
                'status': CaseStatus.ASSIGNED.value if assigned_to else CaseStatus.OPEN.value,
                'assigned_to': assigned_to,
                'created_at': datetime.utcnow().isoformat(),
                'created_by': 'system',
                'priority_score': self._calculate_priority_score(red_flag),
                'resolution_deadline': self._calculate_resolution_deadline(red_flag),
                'workflow_stage': 'initial_review',
                'actions_taken': [],
                'notes': [],
                'audit_trail': [
                    {
                        'timestamp': datetime.utcnow().isoformat(),
                        'action': 'case_created',
                        'user_id': 'system',
                        'details': f"Case created for red flag {red_flag.flag_id}"
                    }
                ]
            }
            
            # Store case data (in production, this would be in a dedicated Cases table)
            logger.info(f"Created case {case_id} for red flag {red_flag.flag_id}")
            
            # Send assignment notification
            if assigned_to:
                self._send_case_assignment_notification(case_data, assigned_to)
            
            # Log audit entry
            self._log_audit_entry(
                case_id=case_id,
                action='case_created',
                user_id='system',
                details=f"Case created for red flag {red_flag.flag_id}",
                metadata={'red_flag_id': red_flag.flag_id, 'severity': red_flag.severity.value}
            )
            
            return {
                'success': True,
                'case_id': case_id,
                'assigned_to': assigned_to,
                'priority_score': case_data['priority_score'],
                'resolution_deadline': case_data['resolution_deadline']
            }
            
        except Exception as e:
            logger.error(f"Failed to create case for red flag {red_flag.flag_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'red_flag_id': red_flag.flag_id
            }
    
    def _auto_assign_case(self, red_flag: RedFlag) -> Optional[str]:
        """Auto-assign case based on workload and expertise"""
        try:
            # Get available therapists
            therapists = self.user_repo.get_users_by_role('therapist')
            
            if not therapists:
                logger.warning("No therapists available for case assignment")
                return None
            
            # For hackathon, assign to first available therapist
            # In production, this would consider:
            # - Current workload
            # - Expertise in flag type
            # - Availability status
            # - Previous case history
            
            selected_therapist = therapists[0]
            logger.info(f"Auto-assigned case to therapist {selected_therapist.user_id}")
            
            return selected_therapist.user_id
            
        except Exception as e:
            logger.error(f"Failed to auto-assign case: {str(e)}")
            return None
    
    def _calculate_priority_score(self, red_flag: RedFlag) -> float:
        """Calculate priority score for case management"""
        try:
            # Base score from severity
            severity_scores = {
                Severity.LOW: 0.25,
                Severity.MEDIUM: 0.5,
                Severity.HIGH: 0.75,
                Severity.CRITICAL: 1.0
            }
            
            base_score = severity_scores.get(red_flag.severity, 0.5)
            
            # Adjust for flag type
            type_multipliers = {
                RedFlagType.SUICIDAL_IDEATION: 1.2,
                RedFlagType.SELF_HARM: 1.1,
                RedFlagType.ABUSE: 1.15,
                RedFlagType.VIOLENCE: 1.1,
                RedFlagType.CRISIS: 1.05
            }
            
            type_multiplier = type_multipliers.get(red_flag.type, 1.0)
            
            # Adjust for time sensitivity (newer flags get higher priority)
            time_factor = 1.0
            age_hours = (datetime.utcnow() - red_flag.detected_at).total_seconds() / 3600
            if age_hours < 1:
                time_factor = 1.2
            elif age_hours < 6:
                time_factor = 1.1
            elif age_hours > 24:
                time_factor = 0.9
            
            priority_score = min(base_score * type_multiplier * time_factor, 1.0)
            
            return round(priority_score, 3)
            
        except Exception as e:
            logger.error(f"Failed to calculate priority score: {str(e)}")
            return 0.5
    
    def _calculate_resolution_deadline(self, red_flag: RedFlag) -> str:
        """Calculate resolution deadline based on severity"""
        try:
            # Deadline hours based on severity
            deadline_hours = {
                Severity.CRITICAL: 2,    # 2 hours
                Severity.HIGH: 8,        # 8 hours
                Severity.MEDIUM: 24,     # 24 hours
                Severity.LOW: 72         # 72 hours
            }
            
            hours = deadline_hours.get(red_flag.severity, 24)
            deadline = datetime.utcnow() + timedelta(hours=hours)
            
            return deadline.isoformat()
            
        except Exception as e:
            logger.error(f"Failed to calculate resolution deadline: {str(e)}")
            return (datetime.utcnow() + timedelta(hours=24)).isoformat()
    
    def _send_case_assignment_notification(self, case_data: Dict[str, Any], assigned_to: str) -> bool:
        """Send notification for case assignment"""
        try:
            title = f"Case Assigned: {case_data['flag_type'].replace('_', ' ').title()}"
            message = f"""
You have been assigned a new red flag case.

Case ID: {case_data['case_id']}
Flag Type: {case_data['flag_type'].replace('_', ' ').title()}
Severity: {case_data['severity'].upper()}
Priority Score: {case_data['priority_score']}
Resolution Deadline: {case_data['resolution_deadline']}

Session ID: {case_data['session_id']}
Red Flag ID: {case_data['red_flag_id']}

Please review and take appropriate action.
            """.strip()
            
            notification = Notification(
                recipient_id=assigned_to,
                type=NotificationType.RED_FLAG,
                priority=Priority.HIGH,
                title=title,
                message=message,
                related_session_id=case_data['session_id'],
                related_flag_id=case_data['red_flag_id'],
                action_required=True
            )
            
            return self.notification_repo.create_notification(notification)
            
        except Exception as e:
            logger.error(f"Failed to send case assignment notification: {str(e)}")
            return False
    
    def update_case_status(self, case_id: str, new_status: CaseStatus, 
                          user_id: str, notes: Optional[str] = None) -> bool:
        """Update case status"""
        try:
            # In production, this would update the Cases table
            # For hackathon, we'll log the status change
            
            update_details = {
                'case_id': case_id,
                'old_status': 'unknown',  # Would be retrieved from database
                'new_status': new_status.value,
                'updated_by': user_id,
                'updated_at': datetime.utcnow().isoformat(),
                'notes': notes
            }
            
            logger.info(f"Case {case_id} status updated to {new_status.value} by {user_id}")
            
            # Log audit entry
            self._log_audit_entry(
                case_id=case_id,
                action='status_updated',
                user_id=user_id,
                details=f"Status changed to {new_status.value}",
                metadata={'notes': notes} if notes else None
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update case status: {str(e)}")
            return False
    
    def add_case_action(self, case_id: str, action: ResolutionAction, 
                       user_id: str, details: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add action taken on a case"""
        try:
            action_record = {
                'action_id': f"ACTION_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'case_id': case_id,
                'action_type': action.value,
                'taken_by': user_id,
                'taken_at': datetime.utcnow().isoformat(),
                'details': details,
                'metadata': metadata or {}
            }
            
            # In production, this would be stored in a CaseActions table
            logger.info(f"Action {action.value} added to case {case_id} by {user_id}")
            
            # Log audit entry
            self._log_audit_entry(
                case_id=case_id,
                action='action_taken',
                user_id=user_id,
                details=f"Action taken: {action.value} - {details}",
                metadata=metadata
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add case action: {str(e)}")
            return False
    
    def resolve_red_flag(self, red_flag_id: str, session_id: str, resolved_by: str,
                        resolution_action: ResolutionAction, resolution_notes: str,
                        case_id: Optional[str] = None) -> bool:
        """Resolve a red flag"""
        try:
            resolved_at = datetime.utcnow()
            
            # Mark red flag as resolved
            success = self.red_flag_repo.resolve_red_flag(
                session_id=session_id,
                flag_id=red_flag_id,
                resolved_by=resolved_by,
                resolved_at=resolved_at
            )
            
            if not success:
                logger.error(f"Failed to mark red flag {red_flag_id} as resolved")
                return False
            
            # Update case if provided
            if case_id:
                self.update_case_status(
                    case_id=case_id,
                    new_status=CaseStatus.RESOLVED,
                    user_id=resolved_by,
                    notes=resolution_notes
                )
                
                self.add_case_action(
                    case_id=case_id,
                    action=resolution_action,
                    user_id=resolved_by,
                    details=resolution_notes,
                    metadata={'resolved_at': resolved_at.isoformat()}
                )
            
            # Log audit entry
            self._log_audit_entry(
                case_id=case_id or f"FLAG_{red_flag_id}",
                action='red_flag_resolved',
                user_id=resolved_by,
                details=f"Red flag resolved with action: {resolution_action.value}",
                metadata={
                    'red_flag_id': red_flag_id,
                    'resolution_action': resolution_action.value,
                    'resolution_notes': resolution_notes
                }
            )
            
            logger.info(f"Red flag {red_flag_id} resolved by {resolved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve red flag {red_flag_id}: {str(e)}")
            return False
    
    def get_case_dashboard(self, user_id: str, user_role: str) -> Dict[str, Any]:
        """Get case management dashboard data"""
        try:
            dashboard_data = {
                'user_id': user_id,
                'user_role': user_role,
                'generated_at': datetime.utcnow().isoformat(),
                'summary': {
                    'total_cases': 0,
                    'open_cases': 0,
                    'assigned_cases': 0,
                    'overdue_cases': 0,
                    'resolved_today': 0
                },
                'recent_cases': [],
                'priority_cases': [],
                'statistics': {}
            }
            
            # Get red flag statistics for dashboard
            stats = self.red_flag_repo.get_red_flag_statistics(
                start_date=datetime.utcnow() - timedelta(days=30)
            )
            
            dashboard_data['summary']['total_cases'] = stats['total_count']
            dashboard_data['summary']['open_cases'] = stats['unresolved_count']
            dashboard_data['summary']['resolved_today'] = stats['resolved_count']
            
            # Get recent unresolved red flags
            recent_flags = self.red_flag_repo.get_unresolved_red_flags(limit=10)
            
            for flag in recent_flags:
                case_info = {
                    'red_flag_id': flag.flag_id,
                    'session_id': flag.session_id,
                    'type': flag.type.value,
                    'severity': flag.severity.value,
                    'detected_at': flag.detected_at.isoformat(),
                    'priority_score': self._calculate_priority_score(flag),
                    'age_hours': (datetime.utcnow() - flag.detected_at).total_seconds() / 3600
                }
                dashboard_data['recent_cases'].append(case_info)
            
            # Get high priority cases
            high_priority_flags = [
                flag for flag in recent_flags 
                if flag.severity in [Severity.HIGH, Severity.CRITICAL]
            ]
            
            for flag in high_priority_flags[:5]:
                priority_case = {
                    'red_flag_id': flag.flag_id,
                    'session_id': flag.session_id,
                    'type': flag.type.value,
                    'severity': flag.severity.value,
                    'detected_at': flag.detected_at.isoformat(),
                    'priority_score': self._calculate_priority_score(flag)
                }
                dashboard_data['priority_cases'].append(priority_case)
            
            dashboard_data['statistics'] = stats
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get case dashboard: {str(e)}")
            return {
                'user_id': user_id,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def generate_case_report(self, start_date: datetime, end_date: datetime,
                           report_type: str = 'summary') -> Dict[str, Any]:
        """Generate case management report"""
        try:
            report_data = {
                'report_type': report_type,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'generated_at': datetime.utcnow().isoformat(),
                'period_days': (end_date - start_date).days,
                'statistics': {},
                'trends': {},
                'performance_metrics': {}
            }
            
            # Get red flag statistics for the period
            stats = self.red_flag_repo.get_red_flag_statistics(
                start_date=start_date,
                end_date=end_date
            )
            
            report_data['statistics'] = stats
            
            # Calculate performance metrics
            total_flags = stats['total_count']
            resolved_flags = stats['resolved_count']
            
            if total_flags > 0:
                resolution_rate = (resolved_flags / total_flags) * 100
                report_data['performance_metrics']['resolution_rate'] = round(resolution_rate, 2)
            else:
                report_data['performance_metrics']['resolution_rate'] = 0.0
            
            # Calculate average resolution time (would need additional data in production)
            report_data['performance_metrics']['average_resolution_hours'] = 24.0  # Placeholder
            
            # Trend analysis
            report_data['trends'] = {
                'flags_per_day': total_flags / max(report_data['period_days'], 1),
                'most_common_type': max(stats['by_type'].items(), key=lambda x: x[1])[0] if stats['by_type'] else 'none',
                'severity_distribution': stats['by_severity']
            }
            
            return report_data
            
        except Exception as e:
            logger.error(f"Failed to generate case report: {str(e)}")
            return {
                'report_type': report_type,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _log_audit_entry(self, case_id: str, action: str, user_id: str, 
                        details: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log audit entry for case management actions"""
        try:
            audit_entry = {
                'audit_id': f"AUDIT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                'case_id': case_id,
                'timestamp': datetime.utcnow().isoformat(),
                'action': action,
                'user_id': user_id,
                'details': details,
                'metadata': metadata or {},
                'ip_address': 'unknown',  # Would be extracted from request context
                'user_agent': 'system'    # Would be extracted from request context
            }
            
            # In production, this would be stored in an AuditLog table
            logger.info(f"AUDIT LOG: {json.dumps(audit_entry)}")
            
        except Exception as e:
            logger.error(f"Failed to log audit entry: {str(e)}")
    
    def get_audit_trail(self, case_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get audit trail for a case"""
        try:
            # In production, this would query the AuditLog table
            # For hackathon, return placeholder data
            
            audit_entries = [
                {
                    'audit_id': f"AUDIT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_001",
                    'case_id': case_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'action': 'case_created',
                    'user_id': 'system',
                    'details': f"Case {case_id} created",
                    'metadata': {}
                }
            ]
            
            if limit:
                audit_entries = audit_entries[:limit]
            
            return audit_entries
            
        except Exception as e:
            logger.error(f"Failed to get audit trail for case {case_id}: {str(e)}")
            return []
    
    def schedule_follow_up(self, case_id: str, follow_up_date: datetime, 
                          assigned_to: str, notes: str) -> bool:
        """Schedule follow-up for a case"""
        try:
            follow_up_data = {
                'follow_up_id': f"FOLLOWUP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'case_id': case_id,
                'scheduled_date': follow_up_date.isoformat(),
                'assigned_to': assigned_to,
                'notes': notes,
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat()
            }
            
            # In production, this would be stored in a FollowUps table
            logger.info(f"Follow-up scheduled for case {case_id} on {follow_up_date.isoformat()}")
            
            # Log audit entry
            self._log_audit_entry(
                case_id=case_id,
                action='follow_up_scheduled',
                user_id=assigned_to,
                details=f"Follow-up scheduled for {follow_up_date.isoformat()}",
                metadata={'notes': notes}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule follow-up: {str(e)}")
            return False
    
    def get_overdue_cases(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get overdue cases"""
        try:
            # Get unresolved red flags
            unresolved_flags = self.red_flag_repo.get_unresolved_red_flags()
            
            overdue_cases = []
            current_time = datetime.utcnow()
            
            for flag in unresolved_flags:
                # Calculate if case is overdue based on severity
                deadline_hours = {
                    Severity.CRITICAL: 2,
                    Severity.HIGH: 8,
                    Severity.MEDIUM: 24,
                    Severity.LOW: 72
                }
                
                hours_limit = deadline_hours.get(flag.severity, 24)
                deadline = flag.detected_at + timedelta(hours=hours_limit)
                
                if current_time > deadline:
                    overdue_case = {
                        'red_flag_id': flag.flag_id,
                        'session_id': flag.session_id,
                        'type': flag.type.value,
                        'severity': flag.severity.value,
                        'detected_at': flag.detected_at.isoformat(),
                        'deadline': deadline.isoformat(),
                        'overdue_hours': (current_time - deadline).total_seconds() / 3600,
                        'priority_score': self._calculate_priority_score(flag)
                    }
                    overdue_cases.append(overdue_case)
            
            # Sort by overdue time (most overdue first)
            overdue_cases.sort(key=lambda x: x['overdue_hours'], reverse=True)
            
            return overdue_cases
            
        except Exception as e:
            logger.error(f"Failed to get overdue cases: {str(e)}")
            return []
    
    def export_case_data(self, case_ids: List[str], format: str = 'json') -> Dict[str, Any]:
        """Export case data for reporting or analysis"""
        try:
            exported_data = {
                'export_type': 'case_data',
                'format': format,
                'exported_at': datetime.utcnow().isoformat(),
                'case_count': len(case_ids),
                'cases': []
            }
            
            # In production, this would retrieve full case data
            # For hackathon, return placeholder structure
            
            for case_id in case_ids:
                case_data = {
                    'case_id': case_id,
                    'exported_at': datetime.utcnow().isoformat(),
                    'status': 'placeholder',
                    'audit_trail': self.get_audit_trail(case_id)
                }
                exported_data['cases'].append(case_data)
            
            logger.info(f"Exported {len(case_ids)} cases in {format} format")
            return exported_data
            
        except Exception as e:
            logger.error(f"Failed to export case data: {str(e)}")
            return {
                'export_type': 'case_data',
                'error': str(e),
                'exported_at': datetime.utcnow().isoformat()
            }