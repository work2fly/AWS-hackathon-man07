"""
Authorization Middleware for AI Therapy Platform
Handles JWT token validation, role-based access control, and audit logging
Breaking Barriers UK 2026 compliant
"""

import json
import logging
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from datetime import datetime

from ..services.cognito_service import cognito_service
from ..utils.logger import get_logger

logger = get_logger(__name__)

class AuthorizationError(Exception):
    """Custom exception for authorization errors"""
    pass

class AuthMiddleware:
    """Authorization middleware for Lambda functions"""
    
    @staticmethod
    def extract_token_from_event(event: Dict[str, Any]) -> Optional[str]:
        """
        Extract JWT token from Lambda event
        
        Args:
            event: Lambda event
            
        Returns:
            JWT token or None if not found
        """
        # Check headers
        headers = event.get('headers', {})
        
        # Handle case-insensitive headers
        auth_header = None
        for key, value in headers.items():
            if key.lower() == 'authorization':
                auth_header = value
                break
        
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.replace('Bearer ', '')
        
        # Check query parameters as fallback
        query_params = event.get('queryStringParameters') or {}
        if 'token' in query_params:
            return query_params['token']
        
        return None
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify JWT token and extract user information
        
        Args:
            token: JWT access token
            
        Returns:
            Dict containing token verification result
        """
        try:
            result = cognito_service.verify_jwt_token(token)
            
            if result['valid']:
                return {
                    'valid': True,
                    'user_id': result['username'],
                    'email': result['email'],
                    'role': result['role'],
                    'language_preference': result.get('language_preference', 'en')
                }
            else:
                return {'valid': False, 'error': result.get('error', 'Invalid token')}
        
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return {'valid': False, 'error': 'Token verification failed'}
    
    @staticmethod
    def check_role_permission(user_role: str, required_roles: List[str]) -> bool:
        """
        Check if user role has required permissions
        
        Args:
            user_role: User's role
            required_roles: List of roles that have access
            
        Returns:
            Boolean indicating if user has permission
        """
        if not user_role or not required_roles:
            return False
        
        # Role hierarchy: admin > therapist > client
        role_hierarchy = {
            'admin': 3,
            'therapist': 2,
            'client': 1
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_levels = [role_hierarchy.get(role, 0) for role in required_roles]
        
        # User must have at least one of the required role levels
        return user_level >= min(required_levels) if required_levels else False
    
    @staticmethod
    def log_auth_event(event_type: str, user_info: Dict[str, Any], 
                      event: Dict[str, Any], success: bool = True, 
                      error: Optional[str] = None) -> None:
        """
        Log authentication and authorization events for audit
        
        Args:
            event_type: Type of auth event (login, access, etc.)
            user_info: User information
            event: Lambda event
            success: Whether the event was successful
            error: Error message if failed
        """
        try:
            # Extract request information
            request_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'success': success,
                'user_id': user_info.get('user_id'),
                'email': user_info.get('email'),
                'role': user_info.get('role'),
                'http_method': event.get('httpMethod'),
                'path': event.get('path'),
                'source_ip': event.get('requestContext', {}).get('identity', {}).get('sourceIp'),
                'user_agent': event.get('headers', {}).get('User-Agent'),
                'request_id': event.get('requestContext', {}).get('requestId')
            }
            
            if error:
                request_info['error'] = error
            
            # Log the audit event
            if success:
                logger.info(f"Auth audit: {json.dumps(request_info)}")
            else:
                logger.warning(f"Auth audit (failed): {json.dumps(request_info)}")
        
        except Exception as e:
            logger.error(f"Failed to log auth event: {str(e)}")

def require_auth(required_roles: Optional[List[str]] = None):
    """
    Decorator for Lambda functions that require authentication
    
    Args:
        required_roles: List of roles that have access (None = any authenticated user)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                # Extract token from event
                token = AuthMiddleware.extract_token_from_event(event)
                
                if not token:
                    AuthMiddleware.log_auth_event(
                        'access_denied', {}, event, False, 'Missing token'
                    )
                    return {
                        'statusCode': 401,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Missing authorization token'})
                    }
                
                # Verify token
                token_info = AuthMiddleware.verify_token(token)
                
                if not token_info['valid']:
                    AuthMiddleware.log_auth_event(
                        'access_denied', {}, event, False, token_info.get('error')
                    )
                    return {
                        'statusCode': 401,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': token_info.get('error', 'Invalid token')})
                    }
                
                # Check role permissions if required
                if required_roles:
                    user_role = token_info.get('role')
                    
                    if not AuthMiddleware.check_role_permission(user_role, required_roles):
                        AuthMiddleware.log_auth_event(
                            'access_denied', token_info, event, False, 
                            f'Insufficient permissions. Required: {required_roles}, User: {user_role}'
                        )
                        return {
                            'statusCode': 403,
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*'
                            },
                            'body': json.dumps({'error': 'Insufficient permissions'})
                        }
                
                # Add user info to event for use in handler
                event['user_info'] = token_info
                
                # Log successful authentication
                AuthMiddleware.log_auth_event('access_granted', token_info, event, True)
                
                # Call the original function
                return func(event, context)
            
            except Exception as e:
                logger.error(f"Auth middleware error: {str(e)}")
                AuthMiddleware.log_auth_event(
                    'auth_error', {}, event, False, str(e)
                )
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Authentication error'})
                }
        
        return wrapper
    return decorator

def require_role(*roles: str):
    """
    Decorator for Lambda functions that require specific roles
    
    Args:
        roles: Required roles (admin, therapist, client)
        
    Returns:
        Decorated function
    """
    return require_auth(list(roles))

def admin_only(func: Callable) -> Callable:
    """Decorator for admin-only endpoints"""
    return require_role('admin')(func)

def therapist_or_admin(func: Callable) -> Callable:
    """Decorator for therapist and admin endpoints"""
    return require_role('therapist', 'admin')(func)

def authenticated_user(func: Callable) -> Callable:
    """Decorator for any authenticated user"""
    return require_auth()(func)

class RoleBasedAccessControl:
    """Role-based access control utilities"""
    
    # Define permissions for each role
    ROLE_PERMISSIONS = {
        'client': [
            'session:create',
            'session:join',
            'session:view_own',
            'profile:view_own',
            'profile:update_own'
        ],
        'therapist': [
            'session:view_summaries',
            'session:view_all',
            'redflags:view',
            'redflags:acknowledge',
            'notifications:view',
            'profile:view_own',
            'profile:update_own',
            'clients:view_summaries'
        ],
        'admin': [
            'users:create',
            'users:view',
            'users:update',
            'users:delete',
            'system:configure',
            'system:monitor',
            'analytics:view',
            'redflags:manage',
            'notifications:manage',
            'profile:view_all',
            'profile:update_all'
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: str, permission: str) -> bool:
        """
        Check if user role has specific permission
        
        Args:
            user_role: User's role
            permission: Permission to check
            
        Returns:
            Boolean indicating if user has permission
        """
        if not user_role:
            return False
        
        # Admin has all permissions
        if user_role == 'admin':
            return True
        
        # Check role-specific permissions
        role_perms = cls.ROLE_PERMISSIONS.get(user_role, [])
        return permission in role_perms
    
    @classmethod
    def get_user_permissions(cls, user_role: str) -> List[str]:
        """
        Get all permissions for a user role
        
        Args:
            user_role: User's role
            
        Returns:
            List of permissions
        """
        if user_role == 'admin':
            # Admin gets all permissions
            all_perms = set()
            for perms in cls.ROLE_PERMISSIONS.values():
                all_perms.update(perms)
            return list(all_perms)
        
        return cls.ROLE_PERMISSIONS.get(user_role, [])

def require_permission(permission: str):
    """
    Decorator for Lambda functions that require specific permission
    
    Args:
        permission: Required permission
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                # First check authentication
                token = AuthMiddleware.extract_token_from_event(event)
                
                if not token:
                    return {
                        'statusCode': 401,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Missing authorization token'})
                    }
                
                # Verify token
                token_info = AuthMiddleware.verify_token(token)
                
                if not token_info['valid']:
                    return {
                        'statusCode': 401,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': token_info.get('error', 'Invalid token')})
                    }
                
                # Check permission
                user_role = token_info.get('role')
                
                if not RoleBasedAccessControl.has_permission(user_role, permission):
                    AuthMiddleware.log_auth_event(
                        'permission_denied', token_info, event, False,
                        f'Missing permission: {permission}'
                    )
                    return {
                        'statusCode': 403,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': f'Missing permission: {permission}'})
                    }
                
                # Add user info to event
                event['user_info'] = token_info
                
                # Log successful authorization
                AuthMiddleware.log_auth_event('permission_granted', token_info, event, True)
                
                # Call the original function
                return func(event, context)
            
            except Exception as e:
                logger.error(f"Permission middleware error: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Authorization error'})
                }
        
        return wrapper
    return decorator

# Utility functions for common authorization patterns
def get_user_from_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get user information from Lambda event (after auth middleware)
    
    Args:
        event: Lambda event with user_info added by middleware
        
    Returns:
        User information or None
    """
    return event.get('user_info')

def is_user_authorized_for_resource(user_info: Dict[str, Any], 
                                  resource_owner_id: str) -> bool:
    """
    Check if user is authorized to access a resource
    
    Args:
        user_info: User information from token
        resource_owner_id: ID of the resource owner
        
    Returns:
        Boolean indicating authorization
    """
    if not user_info:
        return False
    
    user_role = user_info.get('role')
    user_id = user_info.get('user_id')
    
    # Admin can access everything
    if user_role == 'admin':
        return True
    
    # Therapists can access client resources
    if user_role == 'therapist':
        return True  # Therapists can view client summaries
    
    # Users can access their own resources
    return user_id == resource_owner_id