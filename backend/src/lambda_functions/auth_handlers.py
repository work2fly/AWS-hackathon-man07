"""
Authentication Lambda Functions for AI Therapy Platform
Handles user registration, login, logout, token refresh, and profile management
Breaking Barriers UK 2026 compliant
"""

import json
import logging
from typing import Dict, Any, Optional

from ..services.cognito_service import cognito_service
from ..data.user_repository import user_repository
from ..utils.logger import get_logger
from ..utils.validation import validate_email, validate_password

logger = get_logger(__name__)

def create_response(status_code: int, body: Dict[str, Any], 
                   headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Create standardized API response"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body)
    }

def register_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle user registration
    
    POST /auth/register
    Body: {
        "email": "user@example.com",
        "password": "SecurePass123!",
        "role": "client",
        "language_preference": "en"
    }
    """
    try:
        # Parse request body
        if 'body' not in event:
            return create_response(400, {'error': 'Missing request body'})
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract required fields
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        role = body.get('role', 'client').lower()
        language_preference = body.get('language_preference', 'en')
        
        # Validate required fields
        if not all([email, password, role]):
            return create_response(400, {'error': 'Missing required fields: email, password, role'})
        
        # Validate email format
        if not validate_email(email):
            return create_response(400, {'error': 'Invalid email format'})
        
        # Validate password strength
        if not validate_password(password):
            return create_response(400, {
                'error': 'Password must be at least 8 characters with uppercase, lowercase, number, and symbol'
            })
        
        # Validate role
        if role not in ['client', 'therapist', 'admin']:
            return create_response(400, {'error': 'Invalid role. Must be client, therapist, or admin'})
        
        # Register user with Cognito
        result = cognito_service.register_user(email, password, role, language_preference)
        
        if result['success']:
            logger.info(f"User registered successfully: {email}")
            return create_response(201, {
                'message': 'User registered successfully',
                'user_id': result['user_id'],
                'email': result['email'],
                'role': result['role']
            })
        else:
            logger.warning(f"Registration failed for {email}: {result['error']}")
            return create_response(400, {'error': result['error']})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Registration handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def login_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle user login
    
    POST /auth/login
    Body: {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    """
    try:
        # Parse request body
        if 'body' not in event:
            return create_response(400, {'error': 'Missing request body'})
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract credentials
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        
        # Validate required fields
        if not all([email, password]):
            return create_response(400, {'error': 'Missing email or password'})
        
        # Authenticate with Cognito
        result = cognito_service.authenticate_user(email, password)
        
        if result['success']:
            logger.info(f"User authenticated successfully: {email}")
            return create_response(200, {
                'message': 'Authentication successful',
                'access_token': result['access_token'],
                'id_token': result['id_token'],
                'refresh_token': result['refresh_token'],
                'expires_in': result['expires_in'],
                'user_info': result['user_info']
            })
        else:
            logger.warning(f"Authentication failed for {email}: {result['error']}")
            return create_response(401, {'error': result['error']})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Login handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def refresh_token_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle token refresh
    
    POST /auth/refresh
    Body: {
        "refresh_token": "eyJ..."
    }
    """
    try:
        # Parse request body
        if 'body' not in event:
            return create_response(400, {'error': 'Missing request body'})
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract refresh token
        refresh_token = body.get('refresh_token', '')
        
        if not refresh_token:
            return create_response(400, {'error': 'Missing refresh token'})
        
        # Refresh tokens with Cognito
        result = cognito_service.refresh_token(refresh_token)
        
        if result['success']:
            logger.info("Token refreshed successfully")
            return create_response(200, {
                'message': 'Token refreshed successfully',
                'access_token': result['access_token'],
                'id_token': result['id_token'],
                'expires_in': result['expires_in']
            })
        else:
            logger.warning(f"Token refresh failed: {result['error']}")
            return create_response(401, {'error': result['error']})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Token refresh handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def logout_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle user logout
    
    POST /auth/logout
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    """
    try:
        # Extract access token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return create_response(401, {'error': 'Missing or invalid authorization header'})
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Verify token to get user info
        token_info = cognito_service.verify_jwt_token(access_token)
        
        if token_info['valid']:
            logger.info(f"User logged out: {token_info['email']}")
            return create_response(200, {'message': 'Logout successful'})
        else:
            return create_response(401, {'error': 'Invalid token'})
    
    except Exception as e:
        logger.error(f"Logout handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def reset_password_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle password reset request
    
    POST /auth/reset-password
    Body: {
        "email": "user@example.com"
    }
    """
    try:
        # Parse request body
        if 'body' not in event:
            return create_response(400, {'error': 'Missing request body'})
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract email
        email = body.get('email', '').strip().lower()
        
        if not email:
            return create_response(400, {'error': 'Missing email'})
        
        if not validate_email(email):
            return create_response(400, {'error': 'Invalid email format'})
        
        # Initiate password reset with Cognito
        result = cognito_service.reset_password(email)
        
        if result['success']:
            logger.info(f"Password reset initiated for: {email}")
            return create_response(200, {'message': result['message']})
        else:
            logger.warning(f"Password reset failed for {email}: {result['error']}")
            return create_response(400, {'error': result['error']})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Password reset handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def get_profile_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get user profile
    
    GET /auth/profile
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    """
    try:
        # Extract access token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return create_response(401, {'error': 'Missing or invalid authorization header'})
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Verify token and get user info
        token_info = cognito_service.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            return create_response(401, {'error': 'Invalid token'})
        
        # Get detailed user info from DynamoDB
        user_data = user_repository.get_user_by_email(token_info['email'])
        
        if user_data:
            # Remove sensitive information
            profile_data = {
                'user_id': user_data.get('userId'),
                'email': user_data.get('email'),
                'role': user_data.get('role'),
                'profile': user_data.get('profile', {}),
                'preferences': user_data.get('preferences', {}),
                'language_preference': user_data.get('languagePreference', 'en'),
                'is_active': user_data.get('isActive', True),
                'mfa_enabled': user_data.get('mfaEnabled', False),
                'created_at': user_data.get('createdAt'),
                'last_login_at': user_data.get('lastLoginAt')
            }
            
            return create_response(200, profile_data)
        else:
            return create_response(404, {'error': 'User profile not found'})
    
    except Exception as e:
        logger.error(f"Get profile handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def update_profile_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Update user profile
    
    PUT /auth/profile
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    Body: {
        "profile": {
            "first_name": "John",
            "last_name": "Doe",
            "timezone": "UTC"
        },
        "preferences": {
            "language": "en",
            "voice_settings": {...}
        }
    }
    """
    try:
        # Extract access token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return create_response(401, {'error': 'Missing or invalid authorization header'})
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Verify token and get user info
        token_info = cognito_service.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            return create_response(401, {'error': 'Invalid token'})
        
        # Parse request body
        if 'body' not in event:
            return create_response(400, {'error': 'Missing request body'})
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Get current user data
        user_data = user_repository.get_user_by_email(token_info['email'])
        
        if not user_data:
            return create_response(404, {'error': 'User not found'})
        
        # Update profile fields if provided
        if 'profile' in body:
            current_profile = user_data.get('profile', {})
            current_profile.update(body['profile'])
            user_data['profile'] = current_profile
        
        # Update preferences if provided
        if 'preferences' in body:
            current_preferences = user_data.get('preferences', {})
            current_preferences.update(body['preferences'])
            user_data['preferences'] = current_preferences
        
        # Update language preference if provided
        if 'language_preference' in body:
            user_data['languagePreference'] = body['language_preference']
            # Also update in Cognito
            cognito_service.update_user_attributes(
                token_info['username'], 
                {'language_preference': body['language_preference']}
            )
        
        # Update user in DynamoDB
        success = user_repository.update_item(
            key={'userId': user_data['userId']},
            update_expression="SET profile = :profile, preferences = :preferences, languagePreference = :lang, updatedAt = :updated",
            expression_attribute_values={
                ':profile': user_data['profile'],
                ':preferences': user_data['preferences'],
                ':lang': user_data.get('languagePreference', 'en'),
                ':updated': user_data.get('updatedAt')
            }
        )
        
        if success:
            logger.info(f"Profile updated for user: {token_info['email']}")
            return create_response(200, {'message': 'Profile updated successfully'})
        else:
            return create_response(500, {'error': 'Failed to update profile'})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Update profile handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def enable_mfa_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Enable MFA for user
    
    POST /auth/enable-mfa
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    """
    try:
        # Extract access token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return create_response(401, {'error': 'Missing or invalid authorization header'})
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Verify token and get user info
        token_info = cognito_service.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            return create_response(401, {'error': 'Invalid token'})
        
        # Enable MFA in Cognito
        success = cognito_service.enable_mfa(token_info['username'])
        
        if success:
            # Update MFA status in DynamoDB
            user_repository.enable_mfa(token_info['username'])
            
            logger.info(f"MFA enabled for user: {token_info['email']}")
            return create_response(200, {'message': 'MFA enabled successfully'})
        else:
            return create_response(500, {'error': 'Failed to enable MFA'})
    
    except Exception as e:
        logger.error(f"Enable MFA handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

# Lambda handler routing
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler that routes to appropriate auth handler
    """
    try:
        # Get HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        logger.info(f"Auth handler: {http_method} {path}")
        
        # Route to appropriate handler
        if path == '/auth/register' and http_method == 'POST':
            return register_handler(event, context)
        elif path == '/auth/login' and http_method == 'POST':
            return login_handler(event, context)
        elif path == '/auth/logout' and http_method == 'POST':
            return logout_handler(event, context)
        elif path == '/auth/refresh' and http_method == 'POST':
            return refresh_token_handler(event, context)
        elif path == '/auth/reset-password' and http_method == 'POST':
            return reset_password_handler(event, context)
        elif path == '/auth/profile' and http_method == 'GET':
            return get_profile_handler(event, context)
        elif path == '/auth/profile' and http_method == 'PUT':
            return update_profile_handler(event, context)
        elif path == '/auth/enable-mfa' and http_method == 'POST':
            return enable_mfa_handler(event, context)
        else:
            return create_response(404, {'error': 'Endpoint not found'})
    
    except Exception as e:
        logger.error(f"Auth handler routing error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})