"""
AI Therapy Platform - Alert and Notification System
Breaking Barriers UK 2026 compliant alerting for critical events
"""

import json
import boto3
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from ..config.aws_config import aws_clients
from .logger import logger
from .metrics import metrics

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types of alerts"""
    RED_FLAG = "red_flag"
    SECURITY = "security"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    ERROR = "error"

class AlertManager:
    """
    Centralized alert management system
    Handles notifications for critical events, red flags, and system issues
    """
    
    def __init__(self):
        self.sns = boto3.client('sns')
        self.ses = boto3.client('ses')
        self.default_topic_arn = None  # Will be set from environment
        
    def send_alert(self, alert_type: AlertType, severity: AlertSeverity,
                   title: str, message: str, context: Optional[Dict[str, Any]] = None,
                   recipients: Optional[List[str]] = None):
        """
        Send alert through multiple channels based on severity
        
        Args:
            alert_type: Type of alert
            severity: Alert severity level
            title: Alert title
            message: Alert message
            context: Additional context data
            recipients: Specific recipients (optional)
        """
        try:
            alert_data = {
                'alert_id': f"{alert_type.value}_{int(datetime.utcnow().timestamp())}",
                'type': alert_type.value,
                'severity': severity.value,
                'title': title,
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'context': context or {}
            }
            
            # Log the alert
            logger.critical(
                f"Alert: {title}",
                alert_type=alert_type.value,
                severity=severity.value,
                alert_data=alert_data
            )
            
            # Record alert metric
            metrics.put_metric(
                'AlertsGenerated',
                1,
                dimensions={
                    'AlertType': alert_type.value,
                    'Severity': severity.value
                }
            )
            
            # Send through appropriate channels based on severity
            if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                self._send_immediate_notification(alert_data, recipients)
            
            if severity == AlertSeverity.CRITICAL:
                self._send_emergency_notification(alert_data, recipients)
            
            # Store alert for dashboard/reporting
            self._store_alert(alert_data)
            
        except Exception as e:
            logger.error(
                f"Failed to send alert: {title}",
                error=e,
                alert_type=alert_type.value,
                severity=severity.value
            )
    
    def send_red_flag_alert(self, session_id: str, user_id: str, flag_type: str,
                           severity: str, context: str, therapist_ids: List[str]):
        """
        Send red flag alert to therapists and admins
        
        Args:
            session_id: Session ID where red flag was detected
            user_id: User ID (anonymized for privacy)
            flag_type: Type of red flag detected
            severity: Severity level
            context: Sanitized context (no full transcripts)
            therapist_ids: List of therapist IDs to notify
        """
        alert_context = {
            'session_id': session_id,
            'user_id': user_id,
            'flag_type': flag_type,
            'detection_time': datetime.utcnow().isoformat(),
            'sanitized_context': context[:200] + "..." if len(context) > 200 else context
        }
        
        severity_mapping = {
            'low': AlertSeverity.MEDIUM,
            'medium': AlertSeverity.HIGH,
            'high': AlertSeverity.CRITICAL,
            'critical': AlertSeverity.CRITICAL
        }
        
        self.send_alert(
            alert_type=AlertType.RED_FLAG,
            severity=severity_mapping.get(severity, AlertSeverity.HIGH),
            title=f"Red Flag Detected: {flag_type}",
            message=f"A {severity} severity {flag_type} red flag has been detected in session {session_id}. Immediate attention required.",
            context=alert_context,
            recipients=therapist_ids
        )
    
    def send_security_alert(self, event_type: str, user_id: Optional[str] = None,
                           ip_address: Optional[str] = None, details: Optional[Dict] = None):
        """
        Send security-related alert
        
        Args:
            event_type: Type of security event
            user_id: User ID involved (if applicable)
            ip_address: IP address involved (if applicable)
            details: Additional security event details
        """
        alert_context = {
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'detection_time': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        # Determine severity based on event type
        high_severity_events = [
            'multiple_failed_logins',
            'suspicious_api_access',
            'unauthorized_admin_access',
            'data_breach_attempt'
        ]
        
        severity = AlertSeverity.HIGH if event_type in high_severity_events else AlertSeverity.MEDIUM
        
        self.send_alert(
            alert_type=AlertType.SECURITY,
            severity=severity,
            title=f"Security Event: {event_type}",
            message=f"Security event detected: {event_type}. Please review immediately.",
            context=alert_context
        )
    
    def send_system_alert(self, component: str, issue: str, severity: AlertSeverity,
                         metrics_data: Optional[Dict] = None):
        """
        Send system-related alert
        
        Args:
            component: System component affected
            issue: Description of the issue
            severity: Alert severity
            metrics_data: Related metrics data
        """
        alert_context = {
            'component': component,
            'issue': issue,
            'detection_time': datetime.utcnow().isoformat(),
            'metrics': metrics_data or {}
        }
        
        self.send_alert(
            alert_type=AlertType.SYSTEM,
            severity=severity,
            title=f"System Issue: {component}",
            message=f"System issue detected in {component}: {issue}",
            context=alert_context
        )
    
    def send_performance_alert(self, metric_name: str, current_value: float,
                             threshold: float, component: str):
        """
        Send performance-related alert
        
        Args:
            metric_name: Name of the performance metric
            current_value: Current metric value
            threshold: Threshold that was exceeded
            component: Component affected
        """
        alert_context = {
            'metric_name': metric_name,
            'current_value': current_value,
            'threshold': threshold,
            'component': component,
            'detection_time': datetime.utcnow().isoformat()
        }
        
        # Determine severity based on how much threshold was exceeded
        if current_value > threshold * 2:
            severity = AlertSeverity.HIGH
        elif current_value > threshold * 1.5:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        self.send_alert(
            alert_type=AlertType.PERFORMANCE,
            severity=severity,
            title=f"Performance Alert: {metric_name}",
            message=f"Performance threshold exceeded for {metric_name} in {component}. Current: {current_value}, Threshold: {threshold}",
            context=alert_context
        )
    
    def _send_immediate_notification(self, alert_data: Dict, recipients: Optional[List[str]]):
        """Send immediate notification via SNS/SES"""
        try:
            # For hackathon, we'll log the notification instead of actually sending
            # In production, this would send via SNS/SES
            logger.info(
                "Immediate notification would be sent",
                alert_data=alert_data,
                recipients=recipients,
                notification_type="immediate"
            )
            
            # Simulate SNS notification
            if self.default_topic_arn:
                message = {
                    'default': json.dumps(alert_data),
                    'email': f"ALERT: {alert_data['title']}\n\n{alert_data['message']}\n\nTime: {alert_data['timestamp']}"
                }
                
                # In production, uncomment this:
                # self.sns.publish(
                #     TopicArn=self.default_topic_arn,
                #     Message=json.dumps(message),
                #     MessageStructure='json',
                #     Subject=f"AI Therapy Platform Alert: {alert_data['title']}"
                # )
            
        except Exception as e:
            logger.error("Failed to send immediate notification", error=e)
    
    def _send_emergency_notification(self, alert_data: Dict, recipients: Optional[List[str]]):
        """Send emergency notification for critical alerts"""
        try:
            # For hackathon, we'll log the emergency notification
            # In production, this would send via multiple channels (SMS, email, Slack, etc.)
            logger.critical(
                "Emergency notification would be sent",
                alert_data=alert_data,
                recipients=recipients,
                notification_type="emergency"
            )
            
            # Record emergency alert metric
            metrics.put_metric(
                'EmergencyAlerts',
                1,
                dimensions={
                    'AlertType': alert_data['type']
                }
            )
            
        except Exception as e:
            logger.error("Failed to send emergency notification", error=e)
    
    def _store_alert(self, alert_data: Dict):
        """Store alert in DynamoDB for dashboard and reporting"""
        try:
            # For hackathon, we'll log the storage action
            # In production, this would store in DynamoDB
            logger.info(
                "Alert would be stored in database",
                alert_data=alert_data,
                storage_action="store_alert"
            )
            
            # In production, store in DynamoDB notifications table:
            # table = aws_clients.dynamodb_resource.Table('ai-therapy-notifications')
            # table.put_item(Item=alert_data)
            
        except Exception as e:
            logger.error("Failed to store alert", error=e)

# Global alert manager instance
alert_manager = AlertManager()

# Convenience functions for common alert types
def send_red_flag_alert(session_id: str, user_id: str, flag_type: str,
                       severity: str, context: str, therapist_ids: List[str]):
    """Send red flag alert"""
    alert_manager.send_red_flag_alert(
        session_id, user_id, flag_type, severity, context, therapist_ids
    )

def send_security_alert(event_type: str, user_id: Optional[str] = None,
                       ip_address: Optional[str] = None, details: Optional[Dict] = None):
    """Send security alert"""
    alert_manager.send_security_alert(event_type, user_id, ip_address, details)

def send_system_alert(component: str, issue: str, severity: AlertSeverity,
                     metrics_data: Optional[Dict] = None):
    """Send system alert"""
    alert_manager.send_system_alert(component, issue, severity, metrics_data)

def send_performance_alert(metric_name: str, current_value: float,
                         threshold: float, component: str):
    """Send performance alert"""
    alert_manager.send_performance_alert(metric_name, current_value, threshold, component)