"""
API Security Middleware for AI Therapy Platform
Implements comprehensive security headers, request validation, and protection
🏆 Breaking Barriers UK 2026 compliant
"""

import json
import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime, timedelta

from ..utils.logger import get_logger
from ..utils.validation import DataValidator
from ..utils.metrics import metrics

logger = get_logger(__name__)


class SecurityHeaders:
    """Security headers for API responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get comprehensive security headers for API responses
        
        Returns:
            Dictionary of security headers
        """
        return {
            # CORS headers
            'Access-Control-Allow-Origin': '*',  # Configure based on environment
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key, X-Request-ID',
            'Access-Control-Max-Age': '86400',
            
            # Security headers
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            
            # Additional headers
            'Cache-Control': 'no-store, no-cache, must-revalidate, private',
            'Pragma': 'no-cache',
            'X-Powered-By': 'AWS Lambda'
        }
    
    @staticmethod
    def add_security_headers(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add security headers to Lambda response
        
        Args:
            response: Lambda response dictionary
            
        Returns:
            Response with security headers added
        """
        if 'headers' not in response:
            response['headers'] = {}
        
        response['headers'].update(SecurityHeaders.get_security_headers())
        return response


class RequestValidator:
    """Request validation and sanitization"""
    
    @staticmethod
    def validate_request_size(event: Dict[str, Any], max_size_bytes: int = 1048576) -> bool:
        """
        Validate request body size (default 1MB)
        
        Args:
            event: Lambda event
            max_size_bytes: Maximum allowed size in bytes
            
        Returns:
            Boolean indicating if size is valid
        """
        body = event.get('body', '')
        if body:
            body_size = len(body.encode('utf-8'))
            if body_size > max_size_bytes:
                logger.warning(
                    f"Request body too large: {body_size} bytes",
                    body_size=body_size,
                    max_size=max_size_bytes
                )
                return False
        return True
    
    @staticmethod
    def validate_content_type(event: Dict[str, Any], allowed_types: List[str] = None) -> bool:
        """
        Validate request content type
        
        Args:
            event: Lambda event
            allowed_types: List of allowed content types
            
        Returns:
            Boolean indicating if content type is valid
        """
        if allowed_types is None:
            allowed_types = ['application/json', 'application/x-www-form-urlencoded']
        
        headers = event.get('headers', {})
        content_type = None
        
        # Find content-type header (case-insensitive)
        for key, value in headers.items():
            if key.lower() == 'content-type':
                content_type = value.split(';')[0].strip().lower()
                break
        
        if not content_type:
            # Allow requests without content-type for GET requests
            method = event.get('httpMethod', '').upper()
            if method in ['GET', 'DELETE', 'OPTIONS']:
                return True
            return False
        
        return content_type in allowed_types
    
    @staticmethod
    def sanitize_request_body(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize request body to prevent injection attacks
        
        Args:
            event: Lambda event
            
        Returns:
            Event with sanitized body
        """
        try:
            body = event.get('body')
            if not body:
                return event
            
            # Parse JSON body
            if isinstance(body, str):
                try:
                    body_data = json.loads(body)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in request body")
                    return event
            else:
                body_data = body
            
            # Sanitize the data
            sanitized_data = DataValidator.sanitize_user_input(body_data)
            
            # Update event with sanitized body
            event['body'] = json.dumps(sanitized_data)
            event['sanitized_body'] = sanitized_data
            
            return event
            
        except Exception as e:
            logger.error(f"Error sanitizing request body: {str(e)}", error=e)
            return event
    
    @staticmethod
    def validate_request_id(event: Dict[str, Any]) -> str:
        """
        Validate or generate request ID for tracking
        
        Args:
            event: Lambda event
            
        Returns:
            Request ID
        """
        headers = event.get('headers', {})
        
        # Check for existing request ID
        for key, value in headers.items():
            if key.lower() == 'x-request-id':
                return value
        
        # Generate new request ID
        request_context = event.get('requestContext', {})
        request_id = request_context.get('requestId', secrets.token_urlsafe(16))
        
        return request_id


class APIKeyManager:
    """API key management and validation"""
    
    # In production, these would be stored in AWS Secrets Manager
    # For hackathon, using environment-based configuration
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a new API key
        
        Returns:
            API key string
        """
        # Generate 32-byte random key
        key_bytes = secrets.token_bytes(32)
        api_key = hashlib.sha256(key_bytes).hexdigest()
        
        return f"ak_{api_key[:48]}"
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate API key
        
        Args:
            api_key: API key to validate
            
        Returns:
            Boolean indicating if key is valid
        """
        # In production, this would check against Secrets Manager or DynamoDB
        # For hackathon, we'll use JWT tokens primarily
        
        if not api_key or not api_key.startswith('ak_'):
            return False
        
        # Basic format validation
        if len(api_key) != 51:  # ak_ + 48 chars
            return False
        
        return True
    
    @staticmethod
    def extract_api_key(event: Dict[str, Any]) -> Optional[str]:
        """
        Extract API key from request
        
        Args:
            event: Lambda event
            
        Returns:
            API key or None
        """
        headers = event.get('headers', {})
        
        # Check X-API-Key header
        for key, value in headers.items():
            if key.lower() == 'x-api-key':
                return value
        
        # Check query parameters
        query_params = event.get('queryStringParameters') or {}
        if 'api_key' in query_params:
            return query_params['api_key']
        
        return None


class RateLimitTracker:
    """
    Rate limit tracking (in-memory for Lambda)
    In production, use Redis/ElastiCache for distributed rate limiting
    """
    
    def __init__(self):
        self.requests = {}  # {identifier: [(timestamp, count)]}
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = time.time()
    
    def check_rate_limit(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Boolean indicating if request is allowed
        """
        current_time = time.time()
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time, window_seconds)
        
        # Get request history for identifier
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove requests outside the time window
        cutoff_time = current_time - window_seconds
        self.requests[identifier] = [
            (ts, count) for ts, count in self.requests[identifier]
            if ts > cutoff_time
        ]
        
        # Count requests in window
        total_requests = sum(count for _, count in self.requests[identifier])
        
        # Check if limit exceeded
        if total_requests >= limit:
            logger.warning(
                f"Rate limit exceeded for {identifier}",
                identifier=identifier,
                requests=total_requests,
                limit=limit,
                window_seconds=window_seconds
            )
            return False
        
        # Add current request
        self.requests[identifier].append((current_time, 1))
        
        return True
    
    def _cleanup_old_entries(self, current_time: float, window_seconds: int):
        """Clean up old rate limit entries"""
        cutoff_time = current_time - (window_seconds * 2)
        
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                (ts, count) for ts, count in self.requests[identifier]
                if ts > cutoff_time
            ]
            
            # Remove empty entries
            if not self.requests[identifier]:
                del self.requests[identifier]
        
        self.last_cleanup = current_time


# Global rate limit tracker
rate_limiter = RateLimitTracker()


def with_security_headers(func: Callable) -> Callable:
    """
    Decorator to add security headers to Lambda response
    
    Args:
        func: Lambda handler function
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        try:
            response = func(event, context)
            return SecurityHeaders.add_security_headers(response)
        except Exception as e:
            logger.error(f"Error in security headers decorator: {str(e)}", error=e)
            # Return error response with security headers
            error_response = {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal server error'})
            }
            return SecurityHeaders.add_security_headers(error_response)
    
    return wrapper


def validate_request(max_size_bytes: int = 1048576, 
                    allowed_content_types: List[str] = None):
    """
    Decorator to validate and sanitize requests
    
    Args:
        max_size_bytes: Maximum request body size
        allowed_content_types: List of allowed content types
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                # Generate/validate request ID
                request_id = RequestValidator.validate_request_id(event)
                event['request_id'] = request_id
                
                # Validate request size
                if not RequestValidator.validate_request_size(event, max_size_bytes):
                    return SecurityHeaders.add_security_headers({
                        'statusCode': 413,
                        'body': json.dumps({'error': 'Request body too large'})
                    })
                
                # Validate content type
                if not RequestValidator.validate_content_type(event, allowed_content_types):
                    return SecurityHeaders.add_security_headers({
                        'statusCode': 415,
                        'body': json.dumps({'error': 'Unsupported content type'})
                    })
                
                # Sanitize request body
                event = RequestValidator.sanitize_request_body(event)
                
                # Call original function
                return func(event, context)
                
            except Exception as e:
                logger.error(f"Error in request validation: {str(e)}", error=e)
                return SecurityHeaders.add_security_headers({
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Request validation error'})
                })
        
        return wrapper
    return decorator


def require_api_key(func: Callable) -> Callable:
    """
    Decorator to require API key for endpoint access
    
    Args:
        func: Lambda handler function
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        try:
            # Extract API key
            api_key = APIKeyManager.extract_api_key(event)
            
            if not api_key:
                logger.warning("Missing API key in request")
                return SecurityHeaders.add_security_headers({
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Missing API key'})
                })
            
            # Validate API key
            if not APIKeyManager.validate_api_key(api_key):
                logger.warning(f"Invalid API key: {api_key[:10]}...")
                metrics.put_metric('InvalidAPIKey', 1)
                return SecurityHeaders.add_security_headers({
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Invalid API key'})
                })
            
            # Add API key info to event
            event['api_key'] = api_key
            
            # Call original function
            return func(event, context)
            
        except Exception as e:
            logger.error(f"Error in API key validation: {str(e)}", error=e)
            return SecurityHeaders.add_security_headers({
                'statusCode': 500,
                'body': json.dumps({'error': 'API key validation error'})
            })
    
    return wrapper


def rate_limit(requests_per_minute: int = 60, 
              identifier_key: str = 'user_id'):
    """
    Decorator to apply rate limiting to endpoints
    
    Args:
        requests_per_minute: Maximum requests per minute
        identifier_key: Key to use for rate limit tracking (user_id, ip, etc.)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                # Get identifier for rate limiting
                if identifier_key == 'user_id':
                    user_info = event.get('user_info', {})
                    identifier = user_info.get('user_id', 'anonymous')
                elif identifier_key == 'ip':
                    request_context = event.get('requestContext', {})
                    identity = request_context.get('identity', {})
                    identifier = identity.get('sourceIp', 'unknown')
                else:
                    identifier = event.get(identifier_key, 'unknown')
                
                # Check rate limit
                if not rate_limiter.check_rate_limit(identifier, requests_per_minute, 60):
                    metrics.put_metric('RateLimitExceeded', 1, dimensions={
                        'Identifier': identifier
                    })
                    
                    return SecurityHeaders.add_security_headers({
                        'statusCode': 429,
                        'headers': {
                            'Retry-After': '60'
                        },
                        'body': json.dumps({
                            'error': 'Rate limit exceeded',
                            'retry_after': 60
                        })
                    })
                
                # Call original function
                return func(event, context)
                
            except Exception as e:
                logger.error(f"Error in rate limiting: {str(e)}", error=e)
                return SecurityHeaders.add_security_headers({
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Rate limiting error'})
                })
        
        return wrapper
    return decorator


def log_security_event(event_type: str, severity: str = 'medium'):
    """
    Decorator to log security events
    
    Args:
        event_type: Type of security event
        severity: Event severity (low, medium, high, critical)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                # Log security event
                user_info = event.get('user_info', {})
                request_context = event.get('requestContext', {})
                
                logger.warning(
                    f"Security event: {event_type}",
                    event_type=event_type,
                    severity=severity,
                    user_id=user_info.get('user_id'),
                    source_ip=request_context.get('identity', {}).get('sourceIp'),
                    request_id=event.get('request_id'),
                    security_event=True
                )
                
                metrics.put_metric('SecurityEvents', 1, dimensions={
                    'EventType': event_type,
                    'Severity': severity
                })
                
                # Call original function
                return func(event, context)
                
            except Exception as e:
                logger.error(f"Error logging security event: {str(e)}", error=e)
                return func(event, context)
        
        return wrapper
    return decorator
