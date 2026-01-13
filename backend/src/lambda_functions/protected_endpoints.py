"""
Protected Endpoints Example for AI Therapy Platform
Demonstrates usage of authorization middleware
Breaking Barriers UK 2026 compliant
"""

import json
import logging
from typing import Dict, Any

from ..middleware.auth_middleware import (
    require_auth,
    require_role,
    require_permission,
    admin_only,
    therapist_or_admin,
    authenticated_user,
    get_user_from_event,
    RoleBasedAccessControl
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }

@authenticated_user
def get_user_dashboard(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get user dashboard - any authenticated user
    
    GET /dashboard
    """
    try:
        user_info = get_user_from_event(event)
        
        dashboard_data = {
            'user_id': user_info['user_id'],
            'email': user_info['email'],
            'role': user_info['role'],
            'permissions': RoleBasedAccessControl.get_user_permissions(user_info['role']),
            'message': f"Welcome to your {user_info['role']} dashboard!"
        }
        
        return create_response(200, dashboard_data)
    
    except Exception as e:
        logger.error(f"Dashboard handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

@require_role('client')
def create_session(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Create therapy session - clients only
    
    POST /sessions
    """
    try:
        user_info = get_user_from_event(event)
        
        # Only clients can create sessions
        session_data = {
            'session_id': 'session_123',
            'client_id': user_info['user_id'],
            'status': 'created',
            'message': 'Session created successfully'
        }
        
        return create_response(201, session_data)
    
    except Exception as e:
        logger.error(f"Create session handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

@therapist_or_admin
def view_session_summaries(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    View session summaries - therapists and admins only
    
    GET /sessions/summaries
    """
    try:
        user_info = get_user_from_event(event)
        
        summaries_data = {
            'summaries': [
                {
                    'session_id': 'session_123',
                    'client_id': 'client_456',
                    'sentiment': 'positive',
                    'duration': 45,
                    'date': '2026-01-13'
                }
            ],
            'viewer_role': user_info['role'],
            'message': 'Session summaries retrieved successfully'
        }
        
        return create_response(200, summaries_data)
    
    except Exception as e:
        logger.error(f"View summaries handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

@admin_only
def manage_users(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Manage users - admins only
    
    GET /admin/users
    """
    try:
        user_info = get_user_from_event(event)
        
        users_data = {
            'users': [
                {
                    'user_id': 'user_123',
                    'email': 'client@example.com',
                    'role': 'client',
                    'status': 'active'
                },
                {
                    'user_id': 'user_456',
                    'email': 'therapist@example.com',
                    'role': 'therapist',
                    'status': 'active'
                }
            ],
            'admin_id': user_info['user_id'],
            'message': 'Users retrieved successfully'
        }
        
        return create_response(200, users_data)
    
    except Exception as e:
        logger.error(f"Manage users handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

@require_permission('redflags:view')
def view_red_flags(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    View red flags - requires specific permission
    
    GET /redflags
    """
    try:
        user_info = get_user_from_event(event)
        
        red_flags_data = {
            'red_flags': [
                {
                    'flag_id': 'flag_123',
                    'session_id': 'session_456',
                    'type': 'self_harm',
                    'severity': 'high',
                    'timestamp': '2026-01-13T10:30:00Z'
                }
            ],
            'viewer_role': user_info['role'],
            'message': 'Red flags retrieved successfully'
        }
        
        return create_response(200, red_flags_data)
    
    except Exception as e:
        logger.error(f"View red flags handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

@require_permission('users:view')
def get_user_profile(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get user profile - requires user view permission
    
    GET /users/{user_id}
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get user_id from path parameters
        path_params = event.get('pathParameters', {})
        target_user_id = path_params.get('user_id')
        
        if not target_user_id:
            return create_response(400, {'error': 'Missing user_id parameter'})
        
        # Check if user can access this profile
        if user_info['role'] != 'admin' and user_info['user_id'] != target_user_id:
            return create_response(403, {'error': 'Cannot access other user profiles'})
        
        profile_data = {
            'user_id': target_user_id,
            'email': 'user@example.com',
            'role': 'client',
            'profile': {
                'first_name': 'John',
                'last_name': 'Doe'
            },
            'viewer_role': user_info['role'],
            'message': 'User profile retrieved successfully'
        }
        
        return create_response(200, profile_data)
    
    except Exception as e:
        logger.error(f"Get user profile handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler that routes to appropriate protected endpoint
    """
    try:
        # Get HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        logger.info(f"Protected endpoint: {http_method} {path}")
        
        # Route to appropriate handler
        if path == '/dashboard' and http_method == 'GET':
            return get_user_dashboard(event, context)
        elif path == '/sessions' and http_method == 'POST':
            return create_session(event, context)
        elif path == '/sessions/summaries' and http_method == 'GET':
            return view_session_summaries(event, context)
        elif path == '/admin/users' and http_method == 'GET':
            return manage_users(event, context)
        elif path == '/redflags' and http_method == 'GET':
            return view_red_flags(event, context)
        elif path.startswith('/users/') and http_method == 'GET':
            return get_user_profile(event, context)
        else:
            return create_response(404, {'error': 'Endpoint not found'})
    
    except Exception as e:
        logger.error(f"Protected endpoint routing error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})