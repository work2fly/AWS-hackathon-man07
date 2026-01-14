"""
WebSocket Authentication Utility Module for AI Therapy Platform
Handles JWT token extraction, validation, and user information extraction
Breaking Barriers UK 2026 compliant
"""

import os
from typing import Dict, Any, Optional, Tuple

from .logger import get_logger
from ..services.cognito_service import cognito_service
from ..data.user_repository import user_repository

logger = get_logger(__name__)


def extract_token_from_query_params(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract JWT token from WebSocket query parameters
    
    Args:
        event: Lambda event from API Gateway WebSocket
        
    Returns:
        JWT token string or None if not found
        
    Validates: Requirements 2.1
    """
    try:
        # Try query parameters first (most common for WebSocket)
        query_params = event.get('queryStringParameters') or {}
        token = query_params.get('token')
        
        if token:
            logger.debug("Token extracted from query parameters")
            return token
        
        # Try headers as fallback
        headers = event.get('headers') or {}
        auth_header = headers.get('Authorization') or headers.get('authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            logger.debug("Token extracted from Authorization header")
            return token
        
        logger.warning("No authentication token found in query parameters or headers")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting token from event: {str(e)}")
        return None


def validate_token_against_cognito(token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate JWT token against Cognito
    
    Args:
        token: JWT token to validate
        
    Returns:
        Tuple of (is_valid, token_info, error_message)
        - is_valid: Boolean indicating if token is valid
        - token_info: Dict containing token information if valid, None otherwise
        - error_message: Error message if invalid, None otherwise
        
    Validates: Requirements 2.3
    """
    try:
        if not token:
            return False, None, "Missing token"
        
        # Verify JWT token with Cognito
        token_info = cognito_service.verify_jwt_token(token)
        
        if not token_info.get('valid'):
            error = token_info.get('error', 'Invalid token')
            logger.warning(f"Token validation failed: {error}")
            return False, None, error
        
        logger.debug(f"Token validated successfully for user: {token_info.get('username')}")
        return True, token_info, None
        
    except Exception as e:
        error_msg = f"Token validation error: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg


def extract_user_information(token_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract user information from validated token
    
    Args:
        token_info: Validated token information from Cognito
        
    Returns:
        Dict containing user information:
        {
            'user_id': str,
            'email': str,
            'role': str,
            'username': str,
            'language_preference': str
        }
        Returns None if user not found or inactive
        
    Validates: Requirements 2.5
    """
    try:
        email = token_info.get('email')
        if not email:
            logger.error("No email found in token info")
            return None
        
        # Get user data from repository
        user_data = user_repository.get_user_by_email(email)
        
        if not user_data:
            logger.warning(f"User not found in database: {email}")
            return None
        
        # Check if user account is active
        if not user_data.get('isActive', True):
            logger.warning(f"Inactive user attempted connection: {user_data.get('userId')}")
            return None
        
        # Extract and return user information
        user_info = {
            'user_id': user_data['userId'],
            'email': user_data['email'],
            'role': user_data['role'],
            'username': token_info.get('username', email),
            'language_preference': user_data.get('languagePreference', 'en')
        }
        
        logger.debug(f"User information extracted for: {user_info['user_id']}")
        return user_info
        
    except Exception as e:
        logger.error(f"Error extracting user information: {str(e)}")
        return None


def authenticate_websocket_connection(event: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Complete WebSocket authentication flow
    
    Combines token extraction, validation, and user information extraction
    into a single authentication flow.
    
    Args:
        event: Lambda event from API Gateway WebSocket
        
    Returns:
        Tuple of (is_authenticated, user_info, error_message)
        - is_authenticated: Boolean indicating if authentication succeeded
        - user_info: Dict containing user information if authenticated, None otherwise
        - error_message: Error message if authentication failed, None otherwise
        
    Validates: Requirements 2.1, 2.3, 2.5
    """
    try:
        # Step 1: Extract token from query parameters
        token = extract_token_from_query_params(event)
        
        if not token:
            logger.warning("Authentication failed: No token provided")
            return False, None, "Authentication failed: No token provided"
        
        # Step 2: Validate token against Cognito
        is_valid, token_info, validation_error = validate_token_against_cognito(token)
        
        if not is_valid:
            logger.warning(f"Authentication failed: {validation_error}")
            return False, None, f"Authentication failed: {validation_error}"
        
        # Step 3: Extract user information
        user_info = extract_user_information(token_info)
        
        if not user_info:
            logger.warning("Authentication failed: User not found or inactive")
            return False, None, "Authentication failed: User not found or inactive"
        
        logger.info(f"WebSocket authentication successful for user: {user_info['user_id']}")
        return True, user_info, None
        
    except Exception as e:
        error_msg = f"Authentication error: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg
