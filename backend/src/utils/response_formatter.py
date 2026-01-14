"""
Response formatter utility for standardizing API responses.

This module provides functions to create consistent response formats
across all API endpoints with proper CORS headers.
"""

import json
import os
from typing import Any, Dict, Optional


def get_cors_headers(origin: str = '*') -> Dict[str, str]:
    """
    Get CORS headers for API responses.
    
    Args:
        origin: The allowed origin. Defaults to '*' for development.
                In production, should be set to specific domain.
    
    Returns:
        Dictionary of CORS headers
    """
    # In production, check environment for allowed origins
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        # Use configured origin or default to wildcard
        allowed_origin = os.getenv('ALLOWED_ORIGIN', origin)
    else:
        # Development: allow localhost and wildcard
        allowed_origin = origin
    
    return {
        'Access-Control-Allow-Origin': allowed_origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token',
        'Access-Control-Allow-Credentials': 'true',
        'Content-Type': 'application/json'
    }


def success_response(
    data: Any,
    status_code: int = 200,
    message: Optional[str] = None
) -> Dict:
    """
    Create standardized success response.
    
    Args:
        data: The response data to return
        status_code: HTTP status code (default: 200)
        message: Optional success message
    
    Returns:
        Lambda response dictionary with statusCode, headers, and body
    """
    body = {
        'success': True,
        'data': data
    }
    
    if message:
        body['message'] = message
    
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(body)
    }


def error_response(
    error: str,
    status_code: int = 400,
    details: Optional[Dict] = None
) -> Dict:
    """
    Create standardized error response.
    
    Args:
        error: Error message
        status_code: HTTP status code (default: 400)
        details: Optional additional error details
    
    Returns:
        Lambda response dictionary with statusCode, headers, and body
    """
    body = {
        'success': False,
        'error': error
    }
    
    if details:  # Only include details if not None and not empty
        body['details'] = details
    
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(body)
    }
