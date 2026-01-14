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
from ..utils.response_formatter import success_response, error_response, get_cors_headers

logger = get_logger(__name__)

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
        logger.info("Processing registration request")
        
        # Parse request body
        if 'body' not in event:
            logger.warning("Registration request missing body")
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract required fields
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        role = body.get('role', 'client').lower()
        language_preference = body.get('language_preference', 'en')
        
        # Validate required fields
        if not all([email, password, role]):
            logger.warning("Registration request missing required fields")
            return error_response('Missing required fields: email, password, role', 400, 
                                 details={'fields': ['email', 'password', 'role']})
        
        # Validate email format
        if not validate_email(email):
            logger.warning(f"Invalid email format: {email}")
            return error_response('Invalid email format', 400, 
                                 details={'field': 'email'})
        
        # Validate password strength
        if not validate_password(password):
            logger.warning("Password does not meet requirements")
            return error_response(
                'Password must be at least 8 characters with uppercase, lowercase, number, and symbol',
                400,
                details={'field': 'password'}
            )
        
        # Validate role
        if role not in ['client', 'therapist', 'admin']:
            logger.warning(f"Invalid role: {role}")
            return error_response('Invalid role. Must be client, therapist, or admin', 400,
                                 details={'field': 'role', 'valid_values': ['client', 'therapist', 'admin']})
        
        # Register user with Cognito
        result = cognito_service.register_user(email, password, role, language_preference)
        
        if result['success']:
            logger.info(f"User registered successfully: {email}")
            return success_response(
                {
                    'user_id': result['user_id'],
                    'email': result['email'],
                    'role': result['role']
                },
                201,
                message='User registered successfully'
            )
        else:
            logger.warning(f"Registration failed for {email}: {result['error']}")
            return error_response(result['error'], 400)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in registration request body")
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        logger.error(f"Registration handler error: {str(e)}")
        return error_response('Internal server error', 500)

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
        logger.info("Processing login request")
        
        # Parse request body
        if 'body' not in event:
            logger.warning("Login request missing body")
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract credentials
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        
        # Validate required fields
        if not all([email, password]):
            logger.warning("Login request missing email or password")
            return error_response('Missing email or password', 400,
                                 details={'fields': ['email', 'password']})
        
        # Authenticate with Cognito
        result = cognito_service.authenticate_user(email, password)
        
        if result['success']:
            logger.info(f"User authenticated successfully: {email}")
            return success_response(
                {
                    'access_token': result['access_token'],
                    'id_token': result['id_token'],
                    'refresh_token': result['refresh_token'],
                    'expires_in': result['expires_in'],
                    'user_info': result['user_info']
                },
                200,
                message='Authentication successful'
            )
        else:
            logger.warning(f"Authentication failed for {email}: {result['error']}")
            return error_response(result['error'], 401)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in login request body")
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        logger.error(f"Login handler error: {str(e)}")
        return error_response('Internal server error', 500)

def refresh_token_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle token refresh
    
    POST /auth/refresh
    Body: {
        "refresh_token": "eyJ..."
    }
    """
    try:
        logger.info("Processing token refresh request")
        
        # Parse request body
        if 'body' not in event:
            logger.warning("Token refresh request missing body")
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract refresh token
        refresh_token = body.get('refresh_token', '')
        
        if not refresh_token:
            logger.warning("Token refresh request missing refresh_token")
            return error_response('Missing refresh token', 400,
                                 details={'field': 'refresh_token'})
        
        # Refresh tokens with Cognito
        result = cognito_service.refresh_token(refresh_token)
        
        if result['success']:
            logger.info("Token refreshed successfully")
            return success_response(
                {
                    'access_token': result['access_token'],
                    'id_token': result['id_token'],
                    'expires_in': result['expires_in']
                },
                200,
                message='Token refreshed successfully'
            )
        else:
            logger.warning(f"Token refresh failed: {result['error']}")
            return error_response(result['error'], 401)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in token refresh request body")
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        logger.error(f"Token refresh handler error: {str(e)}")
        return error_response('Internal server error', 500)

def logout_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle user logout
    
    POST /auth/logout
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    """
    try:
        logger.info("Processing logout request")
        
        # Extract access token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            logger.warning("Logout request missing or invalid authorization header")
            return error_response('Missing or invalid authorization header', 401)
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Verify token to get user info
        token_info = cognito_service.verify_jwt_token(access_token)
        
        if token_info['valid']:
            logger.info(f"User logged out: {token_info['email']}")
            return success_response(
                {'logged_out': True},
                200,
                message='Logout successful'
            )
        else:
            logger.warning("Logout request with invalid token")
            return error_response('Invalid token', 401)
    
    except Exception as e:
        logger.error(f"Logout handler error: {str(e)}")
        return error_response('Internal server error', 500)

def reset_password_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle password reset request
    
    POST /auth/reset-password
    Body: {
        "email": "user@example.com"
    }
    """
    try:
        logger.info("Processing password reset request")
        
        # Parse request body
        if 'body' not in event:
            logger.warning("Password reset request missing body")
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract email
        email = body.get('email', '').strip().lower()
        
        if not email:
            logger.warning("Password reset request missing email")
            return error_response('Missing email', 400,
                                 details={'field': 'email'})
        
        if not validate_email(email):
            logger.warning(f"Invalid email format for password reset: {email}")
            return error_response('Invalid email format', 400,
                                 details={'field': 'email'})
        
        # Initiate password reset with Cognito
        result = cognito_service.reset_password(email)
        
        if result['success']:
            logger.info(f"Password reset initiated for: {email}")
            return success_response(
                {'email': email},
                200,
                message=result['message']
            )
        else:
            logger.warning(f"Password reset failed for {email}: {result['error']}")
            return error_response(result['error'], 400)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in password reset request body")
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        logger.error(f"Password reset handler error: {str(e)}")
        return error_response('Internal server error', 500)

def get_profile_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get user profile
    
    GET /auth/profile
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    """
    try:
        logger.info("Processing get profile request")
        
        # Extract access token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            logger.warning("Get profile request missing or invalid authorization header")
            return error_response('Missing or invalid authorization header', 401)
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Verify token and get user info
        token_info = cognito_service.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            logger.warning("Get profile request with invalid token")
            return error_response('Invalid token', 401)
        
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
            
            logger.info(f"Profile retrieved for user: {token_info['email']}")
            return success_response(profile_data, 200)
        else:
            logger.warning(f"Profile not found for user: {token_info['email']}")
            return error_response('User profile not found', 404)
    
    except Exception as e:
        logger.error(f"Get profile handler error: {str(e)}")
        return error_response('Internal server error', 500)

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
        logger.info("Processing update profile request")
        
        # Extract access token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            logger.warning("Update profile request missing or invalid authorization header")
            return error_response('Missing or invalid authorization header', 401)
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Verify token and get user info
        token_info = cognito_service.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            logger.warning("Update profile request with invalid token")
            return error_response('Invalid token', 401)
        
        # Parse request body
        if 'body' not in event:
            logger.warning("Update profile request missing body")
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Get current user data
        user_data = user_repository.get_user_by_email(token_info['email'])
        
        if not user_data:
            logger.warning(f"User not found for profile update: {token_info['email']}")
            return error_response('User not found', 404)
        
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
            return success_response(
                {'updated': True},
                200,
                message='Profile updated successfully'
            )
        else:
            logger.error(f"Failed to update profile for user: {token_info['email']}")
            return error_response('Failed to update profile', 500)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in update profile request body")
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        logger.error(f"Update profile handler error: {str(e)}")
        return error_response('Internal server error', 500)

def enable_mfa_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Enable MFA for user
    
    POST /auth/enable-mfa
    Headers: {
        "Authorization": "Bearer <access_token>"
    }
    """
    try:
        logger.info("Processing enable MFA request")
        
        # Extract access token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            logger.warning("Enable MFA request missing or invalid authorization header")
            return error_response('Missing or invalid authorization header', 401)
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Verify token and get user info
        token_info = cognito_service.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            logger.warning("Enable MFA request with invalid token")
            return error_response('Invalid token', 401)
        
        # Enable MFA in Cognito
        success = cognito_service.enable_mfa(token_info['username'])
        
        if success:
            # Update MFA status in DynamoDB
            user_repository.enable_mfa(token_info['username'])
            
            logger.info(f"MFA enabled for user: {token_info['email']}")
            return success_response(
                {'mfa_enabled': True},
                200,
                message='MFA enabled successfully'
            )
        else:
            logger.error(f"Failed to enable MFA for user: {token_info['email']}")
            return error_response('Failed to enable MFA', 500)
    
    except Exception as e:
        logger.error(f"Enable MFA handler error: {str(e)}")
        return error_response('Internal server error', 500)

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
            logger.warning(f"Endpoint not found: {http_method} {path}")
            return error_response('Endpoint not found', 404)
    
    except Exception as e:
        logger.error(f"Auth handler routing error: {str(e)}")
        return error_response('Internal server error', 500)