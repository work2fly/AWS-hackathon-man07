"""
Admin Lambda Handlers for AI Therapy Platform
Provides REST API endpoints for admin operations
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from typing import Dict, Any

from ..data.query_optimizer import query_optimizer
from ..utils.response_formatter import success_response, error_response
from ..middleware.auth_middleware import admin_only, get_user_from_event
from ..utils.logger import get_logger

logger = get_logger(__name__)


@admin_only
def get_admin_stats_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /admin/stats
    Get system statistics including user counts, session counts, and red flag counts
    
    Requirements: 8.1, 8.5, 8.6, 8.7, 8.8
    """
    try:
        user_info = get_user_from_event(event)
        logger.info(f"Admin {user_info.get('user_id')} requesting system stats")
        
        # Get all statistics using optimized queries
        total_users = query_optimizer.get_user_count()
        active_users = query_optimizer.get_active_user_count(hours=24)
        active_sessions = query_optimizer.get_active_session_count()
        unresolved_red_flags = query_optimizer.get_unresolved_red_flag_count()
        
        stats = {
            'totalUsers': total_users,
            'activeUsers': active_users,
            'activeSessions': active_sessions,
            'unresolvedRedFlags': unresolved_red_flags,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        }
        
        logger.info(f"Admin stats retrieved successfully: {stats}")
        return success_response(stats)
        
    except Exception as e:
        logger.error(f"Error in get_admin_stats_handler: {str(e)}")
        return error_response("Internal server error", 500)


@admin_only
def list_all_users_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /admin/users
    List all users with pagination
    
    Requirements: 8.2
    """
    try:
        user_info = get_user_from_event(event)
        logger.info(f"Admin {user_info.get('user_id')} requesting user list")
        
        # Get query parameters for pagination
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        
        # Parse exclusive_start_key if provided
        exclusive_start_key = None
        if query_params.get('lastEvaluatedKey'):
            try:
                exclusive_start_key = json.loads(query_params['lastEvaluatedKey'])
            except json.JSONDecodeError:
                return error_response("Invalid lastEvaluatedKey format", 400)
        
        # Get users with pagination
        result = query_optimizer.get_all_users_paginated(
            limit=limit,
            exclusive_start_key=exclusive_start_key
        )
        
        response_data = {
            'users': result['users'],
            'count': result['count']
        }
        
        if result['last_evaluated_key']:
            response_data['lastEvaluatedKey'] = result['last_evaluated_key']
        
        logger.info(f"Retrieved {result['count']} users for admin")
        return success_response(response_data)
        
    except ValueError as e:
        logger.warning(f"Invalid parameter in list_all_users_handler: {str(e)}")
        return error_response("Invalid parameter format", 400)
    except Exception as e:
        logger.error(f"Error in list_all_users_handler: {str(e)}")
        return error_response("Internal server error", 500)


@admin_only
def list_all_sessions_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /admin/sessions
    List all sessions with pagination
    
    Requirements: 8.3
    """
    try:
        user_info = get_user_from_event(event)
        logger.info(f"Admin {user_info.get('user_id')} requesting session list")
        
        # Get query parameters for pagination and filtering
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        status = query_params.get('status')  # Optional status filter
        
        # Parse exclusive_start_key if provided
        exclusive_start_key = None
        if query_params.get('lastEvaluatedKey'):
            try:
                exclusive_start_key = json.loads(query_params['lastEvaluatedKey'])
            except json.JSONDecodeError:
                return error_response("Invalid lastEvaluatedKey format", 400)
        
        # Get sessions with pagination
        result = query_optimizer.get_all_sessions_paginated(
            limit=limit,
            status=status,
            exclusive_start_key=exclusive_start_key
        )
        
        response_data = {
            'sessions': result['sessions'],
            'count': result['count']
        }
        
        if result['last_evaluated_key']:
            response_data['lastEvaluatedKey'] = result['last_evaluated_key']
        
        logger.info(f"Retrieved {result['count']} sessions for admin")
        return success_response(response_data)
        
    except ValueError as e:
        logger.warning(f"Invalid parameter in list_all_sessions_handler: {str(e)}")
        return error_response("Invalid parameter format", 400)
    except Exception as e:
        logger.error(f"Error in list_all_sessions_handler: {str(e)}")
        return error_response("Internal server error", 500)


@admin_only
def list_all_red_flags_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /admin/red-flags
    List all red flags with pagination
    
    Requirements: 8.4
    """
    try:
        user_info = get_user_from_event(event)
        logger.info(f"Admin {user_info.get('user_id')} requesting red flags list")
        
        # Get query parameters for pagination and filtering
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        
        # Parse resolved filter (default: show unresolved)
        resolved_param = query_params.get('resolved')
        resolved = None
        if resolved_param is not None:
            resolved = resolved_param.lower() == 'true'
        
        # Parse exclusive_start_key if provided
        exclusive_start_key = None
        if query_params.get('lastEvaluatedKey'):
            try:
                exclusive_start_key = json.loads(query_params['lastEvaluatedKey'])
            except json.JSONDecodeError:
                return error_response("Invalid lastEvaluatedKey format", 400)
        
        # Get red flags with pagination
        result = query_optimizer.get_all_red_flags_paginated(
            limit=limit,
            resolved=resolved,
            exclusive_start_key=exclusive_start_key
        )
        
        response_data = {
            'redFlags': result['red_flags'],
            'count': result['count']
        }
        
        if result['last_evaluated_key']:
            response_data['lastEvaluatedKey'] = result['last_evaluated_key']
        
        logger.info(f"Retrieved {result['count']} red flags for admin")
        return success_response(response_data)
        
    except ValueError as e:
        logger.warning(f"Invalid parameter in list_all_red_flags_handler: {str(e)}")
        return error_response("Invalid parameter format", 400)
    except Exception as e:
        logger.error(f"Error in list_all_red_flags_handler: {str(e)}")
        return error_response("Internal server error", 500)
