"""
Notification repository for DynamoDB operations
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .base import BaseRepository, DynamoDBError
from ..models.notification import Notification, NotificationType, Priority
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NotificationRepository(BaseRepository):
    """Repository for Notification operations"""
    
    def __init__(self):
        super().__init__("notifications")
    
    def create_notification(self, notification: Notification) -> bool:
        """Create a new notification"""
        try:
            # Convert to DynamoDB format
            item = notification.to_dynamodb_item()
            
            return self.put_item(item)
            
        except Exception as e:
            logger.error(f"Failed to create notification for {notification.recipient_id}: {str(e)}")
            return False
    
    def get_notifications_for_user(self, recipient_id: str, limit: Optional[int] = None,
                                  exclusive_start_key: Optional[Dict[str, Any]] = None,
                                  unread_only: bool = False) -> Dict[str, Any]:
        """Get notifications for a specific user"""
        try:
            key_condition = "recipientId = :recipient_id"
            expression_values = {":recipient_id": recipient_id}
            
            filter_expression = None
            if unread_only:
                filter_expression = "#read = :read"
                expression_values[":read"] = False
            
            response = self.query(
                key_condition_expression=key_condition,
                expression_attribute_values=expression_values,
                expression_attribute_names={"#read": "read"} if unread_only else None,
                filter_expression=filter_expression,
                limit=limit,
                scan_index_forward=False,  # Most recent first
                exclusive_start_key=exclusive_start_key
            )
            
            notifications = []
            for item in response.get('Items', []):
                try:
                    notification = Notification.from_dynamodb_item(item)
                    notifications.append(notification)
                except Exception as e:
                    logger.warning(f"Failed to parse notification item: {str(e)}")
                    continue
            
            return {
                'notifications': notifications,
                'count': len(notifications),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
        except Exception as e:
            logger.error(f"Failed to get notifications for user {recipient_id}: {str(e)}")
            return {'notifications': [], 'count': 0, 'last_evaluated_key': None}
    
    def get_notifications_by_priority(self, priority: Priority, limit: Optional[int] = None,
                                     exclusive_start_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get notifications by priority level"""
        try:
            response = self.query(
                key_condition_expression="priority = :priority",
                expression_attribute_values={":priority": priority.value},
                index_name="PriorityIndex",
                limit=limit,
                scan_index_forward=False,  # Most recent first
                exclusive_start_key=exclusive_start_key
            )
            
            notifications = []
            for item in response.get('Items', []):
                try:
                    notification = Notification.from_dynamodb_item(item)
                    notifications.append(notification)
                except Exception as e:
                    logger.warning(f"Failed to parse notification item: {str(e)}")
                    continue
            
            return {
                'notifications': notifications,
                'count': len(notifications),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
        except Exception as e:
            logger.error(f"Failed to get notifications by priority {priority}: {str(e)}")
            return {'notifications': [], 'count': 0, 'last_evaluated_key': None}
    
    def mark_notification_as_read(self, recipient_id: str, timestamp: str, 
                                 read_at: datetime) -> bool:
        """Mark notification as read"""
        try:
            key = {
                'recipientId': recipient_id,
                'timestamp': timestamp
            }
            
            update_expression = "SET #read = :read, readAt = :read_at"
            expression_attribute_names = {"#read": "read"}
            expression_attribute_values = {
                ":read": True,
                ":read_at": read_at.isoformat()
            }
            condition = "attribute_exists(recipientId) AND attribute_exists(#timestamp)"
            expression_attribute_names["#timestamp"] = "timestamp"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                expression_attribute_names=expression_attribute_names,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            return False
    
    def mark_all_notifications_as_read(self, recipient_id: str) -> bool:
        """Mark all notifications for a user as read"""
        try:
            # First, get all unread notifications for the user
            unread_notifications = self.get_notifications_for_user(
                recipient_id=recipient_id,
                unread_only=True
            )
            
            read_at = datetime.utcnow()
            success_count = 0
            
            for notification in unread_notifications['notifications']:
                success = self.mark_notification_as_read(
                    recipient_id=recipient_id,
                    timestamp=notification.timestamp.isoformat(),
                    read_at=read_at
                )
                if success:
                    success_count += 1
            
            total_count = len(unread_notifications['notifications'])
            logger.info(f"Marked {success_count}/{total_count} notifications as read for user {recipient_id}")
            
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"Failed to mark all notifications as read for user {recipient_id}: {str(e)}")
            return False
    
    def delete_notification(self, recipient_id: str, timestamp: str) -> bool:
        """Delete notification"""
        try:
            key = {
                'recipientId': recipient_id,
                'timestamp': timestamp
            }
            condition = "attribute_exists(recipientId) AND attribute_exists(#timestamp)"
            expression_attribute_names = {"#timestamp": "timestamp"}
            
            return self.delete_item(key, condition)
            
        except Exception as e:
            logger.error(f"Failed to delete notification: {str(e)}")
            return False
    
    def get_urgent_notifications(self, limit: Optional[int] = None) -> List[Notification]:
        """Get all urgent notifications"""
        try:
            response = self.scan(
                filter_expression="priority = :priority AND #read = :read",
                expression_attribute_names={"#read": "read"},
                expression_attribute_values={
                    ":priority": Priority.URGENT.value,
                    ":read": False
                },
                limit=limit
            )
            
            notifications = []
            for item in response.get('Items', []):
                try:
                    notification = Notification.from_dynamodb_item(item)
                    notifications.append(notification)
                except Exception as e:
                    logger.warning(f"Failed to parse notification item: {str(e)}")
                    continue
            
            # Sort by timestamp (most recent first)
            notifications.sort(key=lambda x: x.timestamp, reverse=True)
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get urgent notifications: {str(e)}")
            return []
    
    def get_notifications_requiring_action(self, limit: Optional[int] = None) -> List[Notification]:
        """Get notifications that require action"""
        try:
            response = self.scan(
                filter_expression="actionRequired = :action_required AND #read = :read",
                expression_attribute_names={"#read": "read"},
                expression_attribute_values={
                    ":action_required": True,
                    ":read": False
                },
                limit=limit
            )
            
            notifications = []
            for item in response.get('Items', []):
                try:
                    notification = Notification.from_dynamodb_item(item)
                    notifications.append(notification)
                except Exception as e:
                    logger.warning(f"Failed to parse notification item: {str(e)}")
                    continue
            
            # Sort by priority and timestamp
            priority_order = {
                Priority.URGENT: 0,
                Priority.HIGH: 1,
                Priority.MEDIUM: 2,
                Priority.LOW: 3
            }
            
            notifications.sort(key=lambda x: (priority_order.get(x.priority, 4), x.timestamp), reverse=True)
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get notifications requiring action: {str(e)}")
            return []
    
    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Clean up old read notifications"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Get old read notifications
            response = self.scan(
                filter_expression="#read = :read AND #timestamp < :cutoff_time",
                expression_attribute_names={
                    "#read": "read",
                    "#timestamp": "timestamp"
                },
                expression_attribute_values={
                    ":read": True,
                    ":cutoff_time": cutoff_time.isoformat()
                }
            )
            
            # Delete old notifications
            deleted_count = 0
            for item in response.get('Items', []):
                try:
                    success = self.delete_notification(
                        recipient_id=item['recipientId'],
                        timestamp=item['timestamp']
                    )
                    if success:
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete old notification: {str(e)}")
                    continue
            
            logger.info(f"Cleaned up {deleted_count} old notifications")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old notifications: {str(e)}")
            return 0
    
    def get_notification_statistics(self, recipient_id: Optional[str] = None,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            filter_parts = []
            expression_values = {}
            expression_names = {}
            
            if recipient_id:
                filter_parts.append("recipientId = :recipient_id")
                expression_values[":recipient_id"] = recipient_id
            
            if start_date:
                filter_parts.append("#timestamp >= :start_date")
                expression_values[":start_date"] = start_date.isoformat()
                expression_names["#timestamp"] = "timestamp"
            
            if end_date:
                filter_parts.append("#timestamp <= :end_date")
                expression_values[":end_date"] = end_date.isoformat()
                expression_names["#timestamp"] = "timestamp"
            
            filter_expression = " AND ".join(filter_parts) if filter_parts else None
            
            response = self.scan(
                filter_expression=filter_expression,
                expression_attribute_values=expression_values if expression_values else None,
                expression_attribute_names=expression_names if expression_names else None
            )
            
            # Process statistics
            stats = {
                'total_count': 0,
                'by_type': {},
                'by_priority': {},
                'read_count': 0,
                'unread_count': 0,
                'action_required_count': 0
            }
            
            for item in response.get('Items', []):
                try:
                    notification = Notification.from_dynamodb_item(item)
                    stats['total_count'] += 1
                    
                    # Count by type
                    notif_type = notification.type.value
                    stats['by_type'][notif_type] = stats['by_type'].get(notif_type, 0) + 1
                    
                    # Count by priority
                    priority = notification.priority.value
                    stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
                    
                    # Count read/unread
                    if notification.read:
                        stats['read_count'] += 1
                    else:
                        stats['unread_count'] += 1
                    
                    # Count action required
                    if notification.action_required:
                        stats['action_required_count'] += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to parse notification item for statistics: {str(e)}")
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get notification statistics: {str(e)}")
            return {
                'total_count': 0,
                'by_type': {},
                'by_priority': {},
                'read_count': 0,
                'unread_count': 0,
                'action_required_count': 0
            }