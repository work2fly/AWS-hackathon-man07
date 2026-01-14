"""
Notification Lambda Handlers for AI Therapy Platform
Handles notification retrieval and management endpoints
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from typing import Dict, Any
from datetime import datetime

from ..data.notification_repository import NotificationRepository
from ..utils.response_formatter import success_response, error_response
from ..utils.logger import get_logger
from ..middleware.auth_middleware import (
    require_auth,
    get_user_from_event,
    is_user_authorized_for_resource
)

logger = get_logger(__name__)


@require_auth()
def get_user_notifications_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /users/{userId}/notifications
    Get notifications for a specific user
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    try:
        # Extract user ID from path parameters
        path_params = event.get('pathParameters', {})
        user_id = path_params.get('userId')
        
        if not user_id:
            logger.warning("Missing userId in path parameters")
            return error_response(
                error="Missing userId parameter",
                status_code=400
            )
        
        # Get authenticated user info
        user_info = get_user_from_event(event)
        
        if not user_info:
            logger.warning("No user info found in event")
            return error_response(
                error="Authentication required",
                status_code=401
            )
        
        # Authorization check: users can only access their own notifications
        # unless they are admin
        if not is_user_authorized_for_resource(user_info, user_id):
            logger.warning(
                f"User {user_info.get('user_id')} attempted to access "
                f"notifications for user {user_id}"
            )
            return error_response(
                error="Access denied",
                status_code=403
            )
        
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        unread_only = query_params.get('unread_only', 'false').lower() == 'true'
        limit = int(query_params.get('limit', '50'))
        
        # Validate limit
        if limit < 1 or limit > 100:
            return error_response(
                error="Limit must be between 1 and 100",
                status_code=400
            )
        
        # Get notifications from repository
        notification_repo = NotificationRepository()
        result = notification_repo.get_notifications_for_user(
            recipient_id=user_id,
            limit=limit,
            unread_only=unread_only
        )
        
        # Convert notifications to dict format
        notifications_data = []
        for notification in result['notifications']:
            notif_dict = {
                'notificationId': notification.timestamp.isoformat(),
                'userId': notification.recipient_id,
                'type': notification.type.value,
                'priority': notification.priority.value,
                'title': notification.title,
                'message': notification.message,
                'createdAt': notification.timestamp.isoformat(),
                'read': notification.read,
                'actionRequired': notification.action_required
            }
            
            # Add optional fields
            if notification.read_at:
                notif_dict['readAt'] = notification.read_at.isoformat()
            if notification.related_session_id:
                notif_dict['relatedSessionId'] = notification.related_session_id
            if notification.related_flag_id:
                notif_dict['relatedFlagId'] = notification.related_flag_id
            
            notifications_data.append(notif_dict)
        
        # Sort by createdAt descending (newest first) - Requirement 7.4
        notifications_data.sort(key=lambda x: x['createdAt'], reverse=True)
        
        response_data = {
            'notifications': notifications_data,
            'count': result['count'],
            'unreadOnly': unread_only
        }
        
        # Add pagination info if available
        if result.get('last_evaluated_key'):
            response_data['lastEvaluatedKey'] = result['last_evaluated_key']
        
        logger.info(
            f"Retrieved {result['count']} notifications for user {user_id} "
            f"(unread_only={unread_only})"
        )
        
        return success_response(
            data=response_data,
            status_code=200
        )
        
    except ValueError as e:
        logger.error(f"Validation error in get_user_notifications: {str(e)}")
        return error_response(
            error="Invalid parameter value",
            status_code=400,
            details={'message': str(e)}
        )
    except Exception as e:
        logger.error(f"Error getting user notifications: {str(e)}")
        return error_response(
            error="Failed to retrieve notifications",
            status_code=500
        )


@require_auth()
def mark_notification_read_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    POST /notifications/{notificationId}/read
    Mark a notification as read
    
    Requirements: 7.2, 7.5
    """
    try:
        # Extract notification ID from path parameters
        path_params = event.get('pathParameters', {})
        notification_id = path_params.get('notificationId')
        
        if not notification_id:
            logger.warning("Missing notificationId in path parameters")
            return error_response(
                error="Missing notificationId parameter",
                status_code=400
            )
        
        # Get authenticated user info
        user_info = get_user_from_event(event)
        
        if not user_info:
            logger.warning("No user info found in event")
            return error_response(
                error="Authentication required",
                status_code=401
            )
        
        # Parse request body to get recipient_id
        # (notification_id is timestamp, we need recipient_id for DynamoDB key)
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                return error_response(
                    error="Invalid JSON in request body",
                    status_code=400
                )
        
        # Get recipient_id from body or use authenticated user's ID
        recipient_id = body.get('userId', user_info.get('user_id'))
        
        # Authorization check: users can only mark their own notifications as read
        # unless they are admin
        if not is_user_authorized_for_resource(user_info, recipient_id):
            logger.warning(
                f"User {user_info.get('user_id')} attempted to mark "
                f"notification for user {recipient_id} as read"
            )
            return error_response(
                error="Access denied",
                status_code=403
            )
        
        # Mark notification as read - Requirement 7.5
        notification_repo = NotificationRepository()
        read_at = datetime.utcnow()
        
        success = notification_repo.mark_notification_as_read(
            recipient_id=recipient_id,
            timestamp=notification_id,
            read_at=read_at
        )
        
        if not success:
            logger.warning(
                f"Failed to mark notification {notification_id} as read "
                f"for user {recipient_id}"
            )
            return error_response(
                error="Notification not found or already read",
                status_code=404
            )
        
        logger.info(
            f"Marked notification {notification_id} as read for user {recipient_id}"
        )
        
        return success_response(
            data={
                'notificationId': notification_id,
                'userId': recipient_id,
                'read': True,
                'readAt': read_at.isoformat()
            },
            status_code=200,
            message="Notification marked as read"
        )
        
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return error_response(
            error="Failed to mark notification as read",
            status_code=500
        )
