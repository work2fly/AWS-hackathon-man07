"""
DynamoDB Query Optimizer Module
Provides efficient query operations for API endpoints
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base import BaseRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


class QueryOptimizer:
    """Optimized DynamoDB query operations for admin endpoints"""
    
    def __init__(self):
        """Initialize query optimizer with table references"""
        self.users_repo = BaseRepository.__new__(BaseRepository)
        self.users_repo.__init__ = lambda: None
        self.sessions_repo = BaseRepository.__new__(BaseRepository)
        self.sessions_repo.__init__ = lambda: None
        self.red_flags_repo = BaseRepository.__new__(BaseRepository)
        self.red_flags_repo.__init__ = lambda: None
        self.notifications_repo = BaseRepository.__new__(BaseRepository)
        self.notifications_repo.__init__ = lambda: None
        
        # Initialize repositories properly
        from .user_repository import UserRepository
        from .session_repository import SessionRepository
        from .red_flag_repository import RedFlagRepository
        from .notification_repository import NotificationRepository
        
        self._user_repo = UserRepository()
        self._session_repo = SessionRepository()
        self._red_flag_repo = RedFlagRepository()
        self._notification_repo = NotificationRepository()
    
    def get_user_count(self) -> int:
        """
        Get total user count efficiently using scan with Select='COUNT'
        
        Requirements: 9.1
        
        Returns:
            Total number of users
        """
        try:
            response = self._user_repo.table.scan(Select='COUNT')
            count = response.get('Count', 0)
            
            # Handle pagination for large tables
            while 'LastEvaluatedKey' in response:
                response = self._user_repo.table.scan(
                    Select='COUNT',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                count += response.get('Count', 0)
            
            logger.info(f"Total user count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get user count: {str(e)}")
            return 0
    
    def get_active_user_count(self, hours: int = 24) -> int:
        """
        Get count of users active within specified hours
        
        Requirements: 9.2
        
        Args:
            hours: Number of hours to look back (default: 24)
            
        Returns:
            Count of active users
        """
        try:
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
            
            response = self._user_repo.table.scan(
                Select='COUNT',
                FilterExpression='lastActiveAt >= :cutoff_time OR lastLoginAt >= :cutoff_time',
                ExpressionAttributeValues={':cutoff_time': cutoff_time}
            )
            count = response.get('Count', 0)
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self._user_repo.table.scan(
                    Select='COUNT',
                    FilterExpression='lastActiveAt >= :cutoff_time OR lastLoginAt >= :cutoff_time',
                    ExpressionAttributeValues={':cutoff_time': cutoff_time},
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                count += response.get('Count', 0)
            
            logger.info(f"Active user count (last {hours}h): {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get active user count: {str(e)}")
            return 0
    
    def get_active_session_count(self) -> int:
        """
        Get count of currently active sessions
        
        Requirements: 9.3
        
        Returns:
            Count of active sessions
        """
        try:
            response = self._session_repo.table.scan(
                Select='COUNT',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'active'}
            )
            count = response.get('Count', 0)
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self._session_repo.table.scan(
                    Select='COUNT',
                    FilterExpression='#status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':status': 'active'},
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                count += response.get('Count', 0)
            
            logger.info(f"Active session count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get active session count: {str(e)}")
            return 0
    
    def get_unresolved_red_flag_count(self) -> int:
        """
        Get count of unresolved red flags
        
        Requirements: 9.5
        
        Returns:
            Count of unresolved red flags
        """
        try:
            response = self._red_flag_repo.table.scan(
                Select='COUNT',
                FilterExpression='resolved = :resolved',
                ExpressionAttributeValues={':resolved': False}
            )
            count = response.get('Count', 0)
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self._red_flag_repo.table.scan(
                    Select='COUNT',
                    FilterExpression='resolved = :resolved',
                    ExpressionAttributeValues={':resolved': False},
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                count += response.get('Count', 0)
            
            logger.info(f"Unresolved red flag count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get unresolved red flag count: {str(e)}")
            return 0

    
    def get_therapist_red_flags(
        self,
        therapist_id: str,
        resolved: bool = False,
        limit: int = 100,
        exclusive_start_key: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get red flags for specific therapist with filtering
        
        Requirements: 9.4
        
        Args:
            therapist_id: ID of the therapist
            resolved: Filter by resolved status (default: False for unresolved)
            limit: Maximum number of items to return
            exclusive_start_key: Pagination key
            
        Returns:
            Dict with red_flags list, count, and last_evaluated_key
        """
        try:
            # Build filter expression
            filter_expression = 'resolved = :resolved'
            expression_values = {
                ':therapist_id': therapist_id,
                ':resolved': resolved
            }
            
            # Query using therapist GSI if available, otherwise scan with filter
            try:
                # Try to use therapist index
                query_kwargs = {
                    'IndexName': 'TherapistIndex',
                    'KeyConditionExpression': 'therapistId = :therapist_id',
                    'FilterExpression': filter_expression,
                    'ExpressionAttributeValues': expression_values,
                    'Limit': limit,
                    'ScanIndexForward': False  # Most recent first
                }
                
                if exclusive_start_key:
                    query_kwargs['ExclusiveStartKey'] = exclusive_start_key
                
                response = self._red_flag_repo.table.query(**query_kwargs)
                
            except Exception:
                # Fallback to scan if index doesn't exist
                logger.warning("TherapistIndex not available, falling back to scan")
                scan_kwargs = {
                    'FilterExpression': 'therapistId = :therapist_id AND resolved = :resolved',
                    'ExpressionAttributeValues': expression_values,
                    'Limit': limit
                }
                
                if exclusive_start_key:
                    scan_kwargs['ExclusiveStartKey'] = exclusive_start_key
                
                response = self._red_flag_repo.table.scan(**scan_kwargs)
            
            items = response.get('Items', [])
            
            # Format red flag items
            red_flags = []
            for item in items:
                red_flag_data = {
                    'sessionId': item.get('sessionId'),
                    'flagId': item.get('flagId'),
                    'type': item.get('type'),
                    'severity': item.get('severity'),
                    'detectedAt': item.get('detectedAt'),
                    'context': item.get('context'),
                    'notificationsSent': item.get('notificationsSent', []),
                    'resolved': item.get('resolved', False),
                    'resolvedAt': item.get('resolvedAt'),
                    'resolvedBy': item.get('resolvedBy'),
                    'acknowledgedAt': item.get('acknowledgedAt'),
                    'acknowledgedBy': item.get('acknowledgedBy')
                }
                red_flags.append(red_flag_data)
            
            result = {
                'red_flags': red_flags,
                'count': len(red_flags),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
            logger.info(f"Retrieved {len(red_flags)} red flags for therapist {therapist_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get therapist red flags: {str(e)}")
            return {'red_flags': [], 'count': 0, 'last_evaluated_key': None}
    
    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        exclusive_start_key: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get notifications for user with filtering
        
        Requirements: 9.6
        
        Args:
            user_id: ID of the user
            unread_only: Filter to only unread notifications
            limit: Maximum number of items to return
            exclusive_start_key: Pagination key
            
        Returns:
            Dict with notifications list, count, and last_evaluated_key
        """
        try:
            query_kwargs = {
                'KeyConditionExpression': 'recipientId = :user_id',
                'ExpressionAttributeValues': {':user_id': user_id},
                'Limit': limit,
                'ScanIndexForward': False  # Most recent first (descending by timestamp)
            }
            
            if unread_only:
                query_kwargs['FilterExpression'] = '#read = :read'
                query_kwargs['ExpressionAttributeNames'] = {'#read': 'read'}
                query_kwargs['ExpressionAttributeValues'][':read'] = False
            
            if exclusive_start_key:
                query_kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            response = self._notification_repo.table.query(**query_kwargs)
            
            items = response.get('Items', [])
            
            # Format notification items
            notifications = []
            for item in items:
                notification_data = {
                    'notificationId': item.get('notificationId'),
                    'recipientId': item.get('recipientId'),
                    'type': item.get('type'),
                    'message': item.get('message'),
                    'createdAt': item.get('timestamp'),
                    'read': item.get('read', False),
                    'readAt': item.get('readAt'),
                    'priority': item.get('priority'),
                    'actionRequired': item.get('actionRequired', False),
                    'metadata': item.get('metadata', {})
                }
                notifications.append(notification_data)
            
            result = {
                'notifications': notifications,
                'count': len(notifications),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
            logger.info(f"Retrieved {len(notifications)} notifications for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {str(e)}")
            return {'notifications': [], 'count': 0, 'last_evaluated_key': None}
    
    def get_all_users_paginated(
        self,
        limit: int = 50,
        exclusive_start_key: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all users with pagination
        
        Requirements: 9.6
        
        Args:
            limit: Maximum number of items to return
            exclusive_start_key: Pagination key
            
        Returns:
            Dict with users list, count, and last_evaluated_key
        """
        try:
            scan_kwargs = {'Limit': limit}
            
            if exclusive_start_key:
                scan_kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            response = self._user_repo.table.scan(**scan_kwargs)
            
            items = response.get('Items', [])
            
            # Format user items
            users = []
            for item in items:
                user_data = {
                    'userId': item.get('userId'),
                    'email': item.get('email'),
                    'role': item.get('role'),
                    'isActive': item.get('isActive', True),
                    'createdAt': item.get('createdAt'),
                    'lastLoginAt': item.get('lastLoginAt'),
                    'languagePreference': item.get('languagePreference', 'en')
                }
                users.append(user_data)
            
            result = {
                'users': users,
                'count': len(users),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
            logger.info(f"Retrieved {len(users)} users")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get all users: {str(e)}")
            return {'users': [], 'count': 0, 'last_evaluated_key': None}
    
    def get_all_sessions_paginated(
        self,
        limit: int = 50,
        status: Optional[str] = None,
        exclusive_start_key: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all sessions with pagination and optional status filter
        
        Args:
            limit: Maximum number of items to return
            status: Optional status filter
            exclusive_start_key: Pagination key
            
        Returns:
            Dict with sessions list, count, and last_evaluated_key
        """
        try:
            scan_kwargs = {'Limit': limit}
            
            if status:
                scan_kwargs['FilterExpression'] = '#status = :status'
                scan_kwargs['ExpressionAttributeNames'] = {'#status': 'status'}
                scan_kwargs['ExpressionAttributeValues'] = {':status': status}
            
            if exclusive_start_key:
                scan_kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            response = self._session_repo.table.scan(**scan_kwargs)
            
            items = response.get('Items', [])
            
            # Format session items
            sessions = []
            for item in items:
                session_data = {
                    'sessionId': item.get('sessionId'),
                    'userId': item.get('clientId') or item.get('userId'),
                    'therapistId': item.get('therapistId') or item.get('agentId'),
                    'status': item.get('status'),
                    'startTime': item.get('startTime'),
                    'endTime': item.get('endTime'),
                    'duration': item.get('duration'),
                    'timestamp': item.get('timestamp'),
                    'language': item.get('language', 'en')
                }
                sessions.append(session_data)
            
            result = {
                'sessions': sessions,
                'count': len(sessions),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
            logger.info(f"Retrieved {len(sessions)} sessions")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get all sessions: {str(e)}")
            return {'sessions': [], 'count': 0, 'last_evaluated_key': None}
    
    def get_all_red_flags_paginated(
        self,
        limit: int = 50,
        resolved: Optional[bool] = None,
        exclusive_start_key: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all red flags with pagination and optional resolved filter
        
        Args:
            limit: Maximum number of items to return
            resolved: Optional resolved status filter
            exclusive_start_key: Pagination key
            
        Returns:
            Dict with red_flags list, count, and last_evaluated_key
        """
        try:
            scan_kwargs = {'Limit': limit}
            
            if resolved is not None:
                scan_kwargs['FilterExpression'] = 'resolved = :resolved'
                scan_kwargs['ExpressionAttributeValues'] = {':resolved': resolved}
            
            if exclusive_start_key:
                scan_kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            response = self._red_flag_repo.table.scan(**scan_kwargs)
            
            items = response.get('Items', [])
            
            # Format red flag items
            red_flags = []
            for item in items:
                red_flag_data = {
                    'sessionId': item.get('sessionId'),
                    'flagId': item.get('flagId'),
                    'type': item.get('type'),
                    'severity': item.get('severity'),
                    'detectedAt': item.get('detectedAt'),
                    'context': item.get('context'),
                    'notificationsSent': item.get('notificationsSent', []),
                    'resolved': item.get('resolved', False),
                    'resolvedAt': item.get('resolvedAt'),
                    'resolvedBy': item.get('resolvedBy'),
                    'acknowledgedAt': item.get('acknowledgedAt'),
                    'acknowledgedBy': item.get('acknowledgedBy')
                }
                red_flags.append(red_flag_data)
            
            result = {
                'red_flags': red_flags,
                'count': len(red_flags),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
            logger.info(f"Retrieved {len(red_flags)} red flags")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get all red flags: {str(e)}")
            return {'red_flags': [], 'count': 0, 'last_evaluated_key': None}


# Global query optimizer instance
query_optimizer = QueryOptimizer()
