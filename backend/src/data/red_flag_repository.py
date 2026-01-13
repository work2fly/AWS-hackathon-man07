"""
Red Flag repository for DynamoDB operations
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .base import BaseRepository, DynamoDBError
from ..models.red_flag import RedFlag, RedFlagType, Severity, NotificationRecord
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RedFlagRepository(BaseRepository):
    """Repository for RedFlag operations"""
    
    def __init__(self):
        super().__init__("redflags")
    
    def create_red_flag(self, red_flag: RedFlag) -> bool:
        """Create a new red flag"""
        try:
            # Convert to DynamoDB format
            item = red_flag.to_dynamodb_item()
            
            # Use condition to prevent overwriting existing red flags
            condition = "attribute_not_exists(sessionId) AND attribute_not_exists(flagId)"
            
            return self.put_item(item, condition)
            
        except Exception as e:
            logger.error(f"Failed to create red flag {red_flag.flag_id}: {str(e)}")
            return False
    
    def get_red_flag(self, session_id: str, flag_id: str) -> Optional[RedFlag]:
        """Get red flag by session ID and flag ID"""
        try:
            key = {
                'sessionId': session_id,
                'flagId': flag_id
            }
            item = self.get_item(key)
            
            if item:
                return RedFlag.from_dynamodb_item(item)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get red flag {flag_id}: {str(e)}")
            return None
    
    def get_red_flags_by_session(self, session_id: str) -> List[RedFlag]:
        """Get all red flags for a session"""
        try:
            response = self.query(
                key_condition_expression="sessionId = :session_id",
                expression_attribute_values={":session_id": session_id}
            )
            
            red_flags = []
            for item in response.get('Items', []):
                try:
                    red_flag = RedFlag.from_dynamodb_item(item)
                    red_flags.append(red_flag)
                except Exception as e:
                    logger.warning(f"Failed to parse red flag item: {str(e)}")
                    continue
            
            return red_flags
            
        except Exception as e:
            logger.error(f"Failed to get red flags for session {session_id}: {str(e)}")
            return []
    
    def get_red_flags_by_severity(self, severity: Severity, limit: Optional[int] = None,
                                 exclusive_start_key: Optional[Dict[str, Any]] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get red flags by severity level"""
        try:
            key_condition = "GSI1PK = :severity_key"
            expression_values = {":severity_key": f"severity#{severity.value}"}
            
            # Add date range filtering if provided
            if start_date and end_date:
                key_condition += " AND GSI1SK BETWEEN :start_date AND :end_date"
                expression_values[":start_date"] = start_date.isoformat()
                expression_values[":end_date"] = end_date.isoformat()
            elif start_date:
                key_condition += " AND GSI1SK >= :start_date"
                expression_values[":start_date"] = start_date.isoformat()
            elif end_date:
                key_condition += " AND GSI1SK <= :end_date"
                expression_values[":end_date"] = end_date.isoformat()
            
            response = self.query(
                key_condition_expression=key_condition,
                expression_attribute_values=expression_values,
                index_name="SeverityIndex",
                limit=limit,
                scan_index_forward=False,  # Most recent first
                exclusive_start_key=exclusive_start_key
            )
            
            red_flags = []
            for item in response.get('Items', []):
                try:
                    red_flag = RedFlag.from_dynamodb_item(item)
                    red_flags.append(red_flag)
                except Exception as e:
                    logger.warning(f"Failed to parse red flag item: {str(e)}")
                    continue
            
            return {
                'red_flags': red_flags,
                'count': len(red_flags),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
        except Exception as e:
            logger.error(f"Failed to get red flags by severity {severity}: {str(e)}")
            return {'red_flags': [], 'count': 0, 'last_evaluated_key': None}
    
    def get_unresolved_red_flags(self, limit: Optional[int] = None) -> List[RedFlag]:
        """Get all unresolved red flags"""
        try:
            response = self.scan(
                filter_expression="resolved = :resolved",
                expression_attribute_values={":resolved": False},
                limit=limit
            )
            
            red_flags = []
            for item in response.get('Items', []):
                try:
                    red_flag = RedFlag.from_dynamodb_item(item)
                    red_flags.append(red_flag)
                except Exception as e:
                    logger.warning(f"Failed to parse red flag item: {str(e)}")
                    continue
            
            # Sort by severity and detection time
            severity_order = {
                Severity.CRITICAL: 0,
                Severity.HIGH: 1,
                Severity.MEDIUM: 2,
                Severity.LOW: 3
            }
            
            red_flags.sort(key=lambda x: (severity_order.get(x.severity, 4), x.detected_at), reverse=True)
            return red_flags
            
        except Exception as e:
            logger.error(f"Failed to get unresolved red flags: {str(e)}")
            return []
    
    def get_recent_red_flags(self, hours: int = 24, limit: Optional[int] = None) -> List[RedFlag]:
        """Get recent red flags within specified hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            response = self.scan(
                filter_expression="detectedAt >= :cutoff_time",
                expression_attribute_values={":cutoff_time": cutoff_time.isoformat()},
                limit=limit
            )
            
            red_flags = []
            for item in response.get('Items', []):
                try:
                    red_flag = RedFlag.from_dynamodb_item(item)
                    red_flags.append(red_flag)
                except Exception as e:
                    logger.warning(f"Failed to parse red flag item: {str(e)}")
                    continue
            
            # Sort by detection time (most recent first)
            red_flags.sort(key=lambda x: x.detected_at, reverse=True)
            return red_flags
            
        except Exception as e:
            logger.error(f"Failed to get recent red flags: {str(e)}")
            return []
    
    def add_notification_record(self, session_id: str, flag_id: str, 
                               notification: NotificationRecord) -> bool:
        """Add notification record to red flag"""
        try:
            key = {
                'sessionId': session_id,
                'flagId': flag_id
            }
            
            # Convert notification to DynamoDB format
            notification_item = {
                'recipientId': notification.recipient_id,
                'method': notification.method.value,
                'sentAt': notification.sent_at.isoformat(),
                'acknowledged': notification.acknowledged
            }
            
            if notification.acknowledged_at:
                notification_item['acknowledgedAt'] = notification.acknowledged_at.isoformat()
            
            update_expression = "SET notificationsSent = list_append(if_not_exists(notificationsSent, :empty_list), :notification)"
            expression_attribute_values = {
                ":notification": [notification_item],
                ":empty_list": []
            }
            condition = "attribute_exists(sessionId) AND attribute_exists(flagId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to add notification record to red flag {flag_id}: {str(e)}")
            return False
    
    def acknowledge_notification(self, session_id: str, flag_id: str, 
                                recipient_id: str, acknowledged_at: datetime) -> bool:
        """Mark notification as acknowledged"""
        try:
            # First, get the current red flag to find the notification index
            red_flag = self.get_red_flag(session_id, flag_id)
            if not red_flag:
                return False
            
            # Find the notification to acknowledge
            notification_index = None
            for i, notification in enumerate(red_flag.notifications_sent):
                if notification.recipient_id == recipient_id and not notification.acknowledged:
                    notification_index = i
                    break
            
            if notification_index is None:
                logger.warning(f"No unacknowledged notification found for recipient {recipient_id}")
                return False
            
            key = {
                'sessionId': session_id,
                'flagId': flag_id
            }
            
            update_expression = f"SET notificationsSent[{notification_index}].acknowledged = :ack, notificationsSent[{notification_index}].acknowledgedAt = :ack_time"
            expression_attribute_values = {
                ":ack": True,
                ":ack_time": acknowledged_at.isoformat()
            }
            condition = "attribute_exists(sessionId) AND attribute_exists(flagId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to acknowledge notification for red flag {flag_id}: {str(e)}")
            return False
    
    def resolve_red_flag(self, session_id: str, flag_id: str, 
                        resolved_by: str, resolved_at: datetime) -> bool:
        """Mark red flag as resolved"""
        try:
            key = {
                'sessionId': session_id,
                'flagId': flag_id
            }
            
            update_expression = "SET resolved = :resolved, resolvedBy = :resolved_by, resolvedAt = :resolved_at"
            expression_attribute_values = {
                ":resolved": True,
                ":resolved_by": resolved_by,
                ":resolved_at": resolved_at.isoformat()
            }
            condition = "attribute_exists(sessionId) AND attribute_exists(flagId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to resolve red flag {flag_id}: {str(e)}")
            return False
    
    def get_red_flag_statistics(self, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get red flag statistics"""
        try:
            filter_parts = []
            expression_values = {}
            
            if start_date:
                filter_parts.append("detectedAt >= :start_date")
                expression_values[":start_date"] = start_date.isoformat()
            
            if end_date:
                filter_parts.append("detectedAt <= :end_date")
                expression_values[":end_date"] = end_date.isoformat()
            
            filter_expression = " AND ".join(filter_parts) if filter_parts else None
            
            response = self.scan(
                filter_expression=filter_expression,
                expression_attribute_values=expression_values if expression_values else None
            )
            
            # Process statistics
            stats = {
                'total_count': 0,
                'by_type': {},
                'by_severity': {},
                'resolved_count': 0,
                'unresolved_count': 0
            }
            
            for item in response.get('Items', []):
                try:
                    red_flag = RedFlag.from_dynamodb_item(item)
                    stats['total_count'] += 1
                    
                    # Count by type
                    flag_type = red_flag.type.value
                    stats['by_type'][flag_type] = stats['by_type'].get(flag_type, 0) + 1
                    
                    # Count by severity
                    severity = red_flag.severity.value
                    stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
                    
                    # Count resolved/unresolved
                    if red_flag.resolved:
                        stats['resolved_count'] += 1
                    else:
                        stats['unresolved_count'] += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to parse red flag item for statistics: {str(e)}")
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get red flag statistics: {str(e)}")
            return {
                'total_count': 0,
                'by_type': {},
                'by_severity': {},
                'resolved_count': 0,
                'unresolved_count': 0
            }