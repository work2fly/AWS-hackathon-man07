"""
REST API Lambda Handlers for Frontend Integration
🏆 Breaking Barriers UK 2026 compliant

Provides REST API endpoints for:
- User management
- Session management
- Red flags (therapist)
- Notifications
- Admin statistics
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

from ..middleware.auth_middleware import require_auth, require_role
from ..data.user_repository import UserRepository
from ..data.session_repository import SessionRepository
from ..data.red_flag_repository import RedFlagRepository
from ..data.notification_repository import NotificationRepository
from ..utils.logger import get_logger
from ..models.user import User, UserRole

logger = get_logger(__name__)

# Initialize repositories
user_repo = UserRepository()
session_repo = SessionRepository()
red_flag_repo = RedFlagRepository()
notification_repo = NotificationRepository()


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create API Gateway response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Configure for production
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }


# ============================================================================
# User Management Endpoints
# ============================================================================

@require_auth
def get_user_profile(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /auth/profile
    Get authenticated user's profile
    """
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        user = user_repo.get_by_id(user_id)
        if not user:
            return create_response(404, {'error': 'User not found'})
        
        return create_response(200, {
            'user': {
                'userId': user.user_id,
                'email': user.email,
                'role': user.role.value,
                'profile': user.profile.dict() if user.profile else {},
                'preferences': user.preferences.dict() if user.preferences else {},
                'createdAt': user.created_at.isoformat(),
                'isActive': user.is_active
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
def update_user_profile(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    PUT /auth/profile
    Update authenticated user's profile
    """
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        body = json.loads(event['body'])
        
        user = user_repo.get_by_id(user_id)
        if not user:
            return create_response(404, {'error': 'User not found'})
        
        # Update profile fields
        if 'profile' in body:
            for key, value in body['profile'].items():
                if hasattr(user.profile, key):
                    setattr(user.profile, key, value)
        
        # Update preferences
        if 'preferences' in body:
            for key, value in body['preferences'].items():
                if hasattr(user.preferences, key):
                    setattr(user.preferences, key, value)
        
        # Save updates
        updated_user = user_repo.update(user)
        
        return create_response(200, {
            'message': 'Profile updated successfully',
            'user': {
                'userId': updated_user.user_id,
                'email': updated_user.email,
                'profile': updated_user.profile.dict(),
                'preferences': updated_user.preferences.dict()
            }
        })
    
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
def get_user_sessions(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /users/{userId}/sessions
    Get user's therapy sessions
    """
    try:
        user_id = event['pathParameters']['userId']
        requesting_user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Users can only see their own sessions unless they're therapist/admin
        if user_id != requesting_user_id:
            user = user_repo.get_by_id(requesting_user_id)
            if user.role not in [UserRole.THERAPIST, UserRole.ADMIN]:
                return create_response(403, {'error': 'Forbidden'})
        
        sessions = session_repo.get_by_client_id(user_id)
        
        return create_response(200, {
            'sessions': [
                {
                    'sessionId': s.session_id,
                    'status': s.status.value,
                    'startTime': s.start_time.isoformat(),
                    'endTime': s.end_time.isoformat() if s.end_time else None,
                    'duration': s.duration,
                    'language': s.language,
                    'sentimentSummary': s.sentiment_summary.dict() if s.sentiment_summary else None
                }
                for s in sessions
            ]
        })
    
    except Exception as e:
        logger.error(f"Error getting user sessions: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


# ============================================================================
# Session Management Endpoints
# ============================================================================

@require_auth
def create_session(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    POST /sessions
    Create new therapy session
    """
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub']
        body = json.loads(event['body'])
        
        # Create session
        session = session_repo.create(
            client_id=user_id,
            language=body.get('language', 'en')
        )
        
        return create_response(201, {
            'message': 'Session created successfully',
            'session': {
                'sessionId': session.session_id,
                'clientId': session.client_id,
                'status': session.status.value,
                'startTime': session.start_time.isoformat(),
                'language': session.language
            }
        })
    
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
def get_session(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /sessions/{sessionId}
    Get session details
    """
    try:
        session_id = event['pathParameters']['sessionId']
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        session = session_repo.get_by_id(session_id)
        if not session:
            return create_response(404, {'error': 'Session not found'})
        
        # Check authorization
        user = user_repo.get_by_id(user_id)
        if session.client_id != user_id and user.role not in [UserRole.THERAPIST, UserRole.ADMIN]:
            return create_response(403, {'error': 'Forbidden'})
        
        return create_response(200, {
            'session': {
                'sessionId': session.session_id,
                'clientId': session.client_id,
                'status': session.status.value,
                'startTime': session.start_time.isoformat(),
                'endTime': session.end_time.isoformat() if session.end_time else None,
                'duration': session.duration,
                'language': session.language,
                'metadata': session.metadata.dict() if session.metadata else {},
                'sentimentSummary': session.sentiment_summary.dict() if session.sentiment_summary else None
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
def end_session(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    POST /sessions/{sessionId}/end
    End therapy session
    """
    try:
        session_id = event['pathParameters']['sessionId']
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        session = session_repo.get_by_id(session_id)
        if not session:
            return create_response(404, {'error': 'Session not found'})
        
        # Only session owner can end it
        if session.client_id != user_id:
            return create_response(403, {'error': 'Forbidden'})
        
        # End session
        session = session_repo.end_session(session_id)
        
        return create_response(200, {
            'message': 'Session ended successfully',
            'session': {
                'sessionId': session.session_id,
                'status': session.status.value,
                'endTime': session.end_time.isoformat(),
                'duration': session.duration
            }
        })
    
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


# ============================================================================
# Red Flags Endpoints (Therapist)
# ============================================================================

@require_auth
@require_role([UserRole.THERAPIST, UserRole.ADMIN])
def get_therapist_red_flags(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /therapists/{therapistId}/red-flags
    Get therapist's assigned red flags
    """
    try:
        therapist_id = event['pathParameters']['therapistId']
        requesting_user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Therapists can only see their own red flags
        if therapist_id != requesting_user_id:
            user = user_repo.get_by_id(requesting_user_id)
            if user.role != UserRole.ADMIN:
                return create_response(403, {'error': 'Forbidden'})
        
        # Get unresolved red flags
        red_flags = red_flag_repo.get_by_therapist(therapist_id, resolved=False)
        
        return create_response(200, {
            'redFlags': [
                {
                    'sessionId': rf.session_id,
                    'flagId': rf.flag_id,
                    'type': rf.type.value,
                    'severity': rf.severity.value,
                    'detectedAt': rf.detected_at.isoformat(),
                    'context': rf.context,
                    'notificationsSent': [
                        {
                            'recipientId': n.recipient_id,
                            'method': n.method.value,
                            'sentAt': n.sent_at.isoformat(),
                            'acknowledged': n.acknowledged
                        }
                        for n in rf.notifications_sent
                    ],
                    'resolved': rf.resolved
                }
                for rf in red_flags
            ]
        })
    
    except Exception as e:
        logger.error(f"Error getting therapist red flags: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
@require_role([UserRole.THERAPIST, UserRole.ADMIN])
def acknowledge_red_flag(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    POST /red-flags/{flagId}/acknowledge
    Acknowledge red flag
    """
    try:
        flag_id = event['pathParameters']['flagId']
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        red_flag = red_flag_repo.acknowledge(flag_id, user_id)
        
        return create_response(200, {
            'message': 'Red flag acknowledged',
            'redFlag': {
                'flagId': red_flag.flag_id,
                'acknowledged': True,
                'acknowledgedBy': user_id,
                'acknowledgedAt': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error acknowledging red flag: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
@require_role([UserRole.THERAPIST, UserRole.ADMIN])
def resolve_red_flag(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    POST /red-flags/{flagId}/resolve
    Resolve red flag
    """
    try:
        flag_id = event['pathParameters']['flagId']
        user_id = event['requestContext']['authorizer']['claims']['sub']
        body = json.loads(event['body'])
        
        red_flag = red_flag_repo.resolve(
            flag_id=flag_id,
            resolved_by=user_id,
            resolution_notes=body.get('notes', '')
        )
        
        return create_response(200, {
            'message': 'Red flag resolved',
            'redFlag': {
                'flagId': red_flag.flag_id,
                'resolved': True,
                'resolvedBy': user_id,
                'resolvedAt': red_flag.resolved_at.isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error resolving red flag: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


# ============================================================================
# Notifications Endpoints
# ============================================================================

@require_auth
def get_user_notifications(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /users/{userId}/notifications
    Get user's notifications
    """
    try:
        user_id = event['pathParameters']['userId']
        requesting_user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Users can only see their own notifications
        if user_id != requesting_user_id:
            return create_response(403, {'error': 'Forbidden'})
        
        notifications = notification_repo.get_by_recipient(user_id)
        
        return create_response(200, {
            'notifications': [
                {
                    'recipientId': n.recipient_id,
                    'timestamp': n.timestamp.isoformat(),
                    'type': n.type.value,
                    'priority': n.priority.value,
                    'title': n.title,
                    'message': n.message,
                    'relatedSessionId': n.related_session_id,
                    'relatedFlagId': n.related_flag_id,
                    'read': n.read,
                    'actionRequired': n.action_required
                }
                for n in notifications
            ]
        })
    
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
def mark_notification_read(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    POST /notifications/{notificationId}/read
    Mark notification as read
    """
    try:
        notification_id = event['pathParameters']['notificationId']
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        notification = notification_repo.mark_read(notification_id, user_id)
        
        return create_response(200, {
            'message': 'Notification marked as read',
            'notification': {
                'recipientId': notification.recipient_id,
                'timestamp': notification.timestamp.isoformat(),
                'read': True,
                'readAt': notification.read_at.isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


# ============================================================================
# Admin Endpoints
# ============================================================================

@require_auth
@require_role([UserRole.ADMIN])
def get_admin_stats(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /admin/stats
    Get system statistics
    """
    try:
        # Get counts from repositories
        total_users = user_repo.count()
        active_users = user_repo.count_active(hours=24)
        total_sessions = session_repo.count()
        active_sessions = session_repo.count_active()
        unresolved_red_flags = red_flag_repo.count_unresolved()
        unread_notifications = notification_repo.count_unread()
        
        return create_response(200, {
            'stats': {
                'totalUsers': total_users,
                'activeUsers': active_users,
                'totalSessions': total_sessions,
                'activeSessions': active_sessions,
                'redFlags': unresolved_red_flags,
                'notifications': unread_notifications,
                'timestamp': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
@require_role([UserRole.ADMIN])
def get_all_users(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /admin/users
    Get all users (admin only)
    """
    try:
        users = user_repo.get_all()
        
        return create_response(200, {
            'users': [
                {
                    'userId': u.user_id,
                    'email': u.email,
                    'role': u.role.value,
                    'isActive': u.is_active,
                    'createdAt': u.created_at.isoformat()
                }
                for u in users
            ]
        })
    
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
@require_role([UserRole.ADMIN])
def get_all_sessions(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /admin/sessions
    Get all sessions (admin only)
    """
    try:
        sessions = session_repo.get_all()
        
        return create_response(200, {
            'sessions': [
                {
                    'sessionId': s.session_id,
                    'clientId': s.client_id,
                    'status': s.status.value,
                    'startTime': s.start_time.isoformat(),
                    'duration': s.duration,
                    'language': s.language
                }
                for s in sessions
            ]
        })
    
    except Exception as e:
        logger.error(f"Error getting all sessions: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_auth
@require_role([UserRole.ADMIN])
def get_all_red_flags(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /admin/red-flags
    Get all red flags (admin only)
    """
    try:
        red_flags = red_flag_repo.get_all()
        
        return create_response(200, {
            'redFlags': [
                {
                    'sessionId': rf.session_id,
                    'flagId': rf.flag_id,
                    'type': rf.type.value,
                    'severity': rf.severity.value,
                    'detectedAt': rf.detected_at.isoformat(),
                    'resolved': rf.resolved
                }
                for rf in red_flags
            ]
        })
    
    except Exception as e:
        logger.error(f"Error getting all red flags: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})
