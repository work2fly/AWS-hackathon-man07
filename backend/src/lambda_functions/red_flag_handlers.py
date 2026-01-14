"""
Red Flag Management Lambda Handlers for AI Therapy Platform
Provides REST API endpoints for red flag management operations
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from typing import Dict, Any
from datetime import datetime

from ..data.red_flag_repository import RedFlagRepository
from ..services.red_flag_management_service import RedFlagManagementService, ResolutionAction
from ..utils.response_formatter import success_response, error_response
from ..utils.logger import get_logger
from ..middleware.auth_middleware import require_role, get_user_from_event

logger = get_logger(__name__)


# Initialize services
red_flag_repo = RedFlagRepository()
red_flag_service = RedFlagManagementService()


@require_role('therapist', 'admin')
def get_therapist_red_flags_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /therapists/{therapistId}/red-flags
    
    Get all red flags assigned to a therapist.
    
    Args:
        event: Lambda event with path parameters
        context: Lambda context
        
    Returns:
        Response with red flags list
    """
    try:
        # Extract therapist ID from path
        path_params = event.get('pathParameters', {})
        therapist_id = path_params.get('therapistId')
        
        if not therapist_id:
            return error_response('Missing therapistId in path', 400)
        
        # Get user info from auth middleware
        user_info = get_user_from_event(event)
        if not user_info:
            return error_response('Unauthorized', 401)
        
        # Check authorization: therapists can only view their own flags, admins can view all
        user_role = user_info.get('role')
        user_id = user_info.get('user_id')
        
        if user_role == 'therapist' and user_id != therapist_id:
            return error_response('Access denied: can only view your own red flags', 403)
        
        # Get query parameters for filtering
        query_params = event.get('queryStringParameters') or {}
        resolved_filter = query_params.get('resolved', 'false').lower() == 'true'
        limit = int(query_params.get('limit', '100'))
        
        # Get unresolved red flags (in production, would filter by therapist assignment)
        # For hackathon, we'll get all unresolved flags
        if not resolved_filter:
            red_flags = red_flag_repo.get_unresolved_red_flags(limit=limit)
        else:
            # Get all red flags and filter resolved ones
            # In production, this would use a proper query
            all_flags = red_flag_repo.get_unresolved_red_flags(limit=limit * 2)
            red_flags = [flag for flag in all_flags if flag.resolved][:limit]
        
        # Convert to response format
        red_flags_data = []
        for flag in red_flags:
            flag_data = {
                'sessionId': flag.session_id,
                'flagId': flag.flag_id,
                'type': flag.type.value,
                'severity': flag.severity.value,
                'detectedAt': flag.detected_at.isoformat(),
                'context': flag.context,
                'notificationsSent': [
                    {
                        'recipientId': notif.recipient_id,
                        'method': notif.method.value,
                        'sentAt': notif.sent_at.isoformat(),
                        'acknowledged': notif.acknowledged,
                        'acknowledgedAt': notif.acknowledged_at.isoformat() if notif.acknowledged_at else None
                    }
                    for notif in flag.notifications_sent
                ],
                'resolved': flag.resolved,
                'resolvedBy': flag.resolved_by,
                'resolvedAt': flag.resolved_at.isoformat() if flag.resolved_at else None
            }
            red_flags_data.append(flag_data)
        
        logger.info(f"Retrieved {len(red_flags_data)} red flags for therapist {therapist_id}")
        
        return success_response({
            'therapistId': therapist_id,
            'redFlags': red_flags_data,
            'count': len(red_flags_data),
            'resolved': resolved_filter
        })
    
    except ValueError as e:
        logger.error(f"Validation error in get_therapist_red_flags: {str(e)}")
        return error_response(f'Validation error: {str(e)}', 400)
    
    except Exception as e:
        logger.error(f"Error getting therapist red flags: {str(e)}")
        return error_response('Failed to retrieve red flags', 500)


@require_role('therapist', 'admin')
def acknowledge_red_flag_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    POST /red-flags/{flagId}/acknowledge
    
    Mark a red flag as acknowledged by the therapist.
    
    Args:
        event: Lambda event with path parameters and body
        context: Lambda context
        
    Returns:
        Response with acknowledgment status
    """
    try:
        # Extract flag ID from path
        path_params = event.get('pathParameters', {})
        flag_id = path_params.get('flagId')
        
        if not flag_id:
            return error_response('Missing flagId in path', 400)
        
        # Get user info from auth middleware
        user_info = get_user_from_event(event)
        if not user_info:
            return error_response('Unauthorized', 401)
        
        user_id = user_info.get('user_id')
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return error_response('Invalid JSON in request body', 400)
        
        session_id = body.get('sessionId')
        notes = body.get('notes', '')
        
        if not session_id:
            return error_response('Missing sessionId in request body', 400)
        
        # Get the red flag
        red_flag = red_flag_repo.get_red_flag(session_id, flag_id)
        
        if not red_flag:
            return error_response('Red flag not found', 404)
        
        # Acknowledge the notification for this user
        acknowledged_at = datetime.utcnow()
        success = red_flag_repo.acknowledge_notification(
            session_id=session_id,
            flag_id=flag_id,
            recipient_id=user_id,
            acknowledged_at=acknowledged_at
        )
        
        if not success:
            logger.warning(f"Failed to acknowledge red flag {flag_id} for user {user_id}")
            return error_response('Failed to acknowledge red flag', 500)
        
        # Log the acknowledgment
        logger.info(f"Red flag {flag_id} acknowledged by {user_id}")
        
        return success_response({
            'flagId': flag_id,
            'sessionId': session_id,
            'acknowledgedBy': user_id,
            'acknowledgedAt': acknowledged_at.isoformat(),
            'notes': notes
        }, message='Red flag acknowledged successfully')
    
    except Exception as e:
        logger.error(f"Error acknowledging red flag: {str(e)}")
        return error_response('Failed to acknowledge red flag', 500)


@require_role('therapist', 'admin')
def resolve_red_flag_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    POST /red-flags/{flagId}/resolve
    
    Mark a red flag as resolved with resolution details.
    
    Args:
        event: Lambda event with path parameters and body
        context: Lambda context
        
    Returns:
        Response with resolution status
    """
    try:
        # Extract flag ID from path
        path_params = event.get('pathParameters', {})
        flag_id = path_params.get('flagId')
        
        if not flag_id:
            return error_response('Missing flagId in path', 400)
        
        # Get user info from auth middleware
        user_info = get_user_from_event(event)
        if not user_info:
            return error_response('Unauthorized', 401)
        
        user_id = user_info.get('user_id')
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return error_response('Invalid JSON in request body', 400)
        
        session_id = body.get('sessionId')
        resolution_notes = body.get('resolutionNotes', '')
        resolution_action = body.get('resolutionAction', 'no_action')
        
        if not session_id:
            return error_response('Missing sessionId in request body', 400)
        
        if not resolution_notes:
            return error_response('Missing resolutionNotes in request body', 400)
        
        # Validate resolution action
        try:
            action = ResolutionAction(resolution_action)
        except ValueError:
            valid_actions = [a.value for a in ResolutionAction]
            return error_response(
                f'Invalid resolutionAction. Must be one of: {", ".join(valid_actions)}',
                400
            )
        
        # Get the red flag
        red_flag = red_flag_repo.get_red_flag(session_id, flag_id)
        
        if not red_flag:
            return error_response('Red flag not found', 404)
        
        # Check if already resolved
        if red_flag.resolved:
            return error_response('Red flag is already resolved', 400)
        
        # Resolve the red flag
        success = red_flag_service.resolve_red_flag(
            red_flag_id=flag_id,
            session_id=session_id,
            resolved_by=user_id,
            resolution_action=action,
            resolution_notes=resolution_notes
        )
        
        if not success:
            logger.error(f"Failed to resolve red flag {flag_id}")
            return error_response('Failed to resolve red flag', 500)
        
        resolved_at = datetime.utcnow()
        
        logger.info(f"Red flag {flag_id} resolved by {user_id} with action {resolution_action}")
        
        return success_response({
            'flagId': flag_id,
            'sessionId': session_id,
            'resolvedBy': user_id,
            'resolvedAt': resolved_at.isoformat(),
            'resolutionAction': resolution_action,
            'resolutionNotes': resolution_notes
        }, message='Red flag resolved successfully')
    
    except Exception as e:
        logger.error(f"Error resolving red flag: {str(e)}")
        return error_response('Failed to resolve red flag', 500)
