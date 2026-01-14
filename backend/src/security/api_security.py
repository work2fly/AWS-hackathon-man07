"""
API Security Module - Comprehensive security controls
🏆 Breaking Barriers UK 2026 compliant
"""

import re
import json
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..utils.logger import get_logger

logger = get_logger(__name__)


class APIKeyManager:
    """Manages API key generation, validation, and rotation"""
    
    def __init__(self):
        self.key_prefix = "tp_"  # therapy platform prefix
        self.key_length = 32
    
    def generate_api_key(self, user_id: str, description: str = "") -> Dict[str, str]:
        """
        Generate a new API key
        
        Returns:
            {
                'api_key': 'tp_abc123...',
                'key_hash': 'hashed_value',
                'created_at': '2026-01-14T...',
                'description': 'Mobile app key'
            }
        """
        # Generate secure random key
        random_bytes = secrets.token_bytes(self.key_length)
        key_suffix = secrets.token_urlsafe(self.key_length)
        api_key = f"{self.key_prefix}{key_suffix}"
        
        # Hash the key for storage (never store plain text)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        return {
            'api_key': api_key,
            'key_hash': key_hash,
            'user_id': user_id,
            'description': description,
            'created_at': datetime.utcnow().isoformat(),
            'last_used': None,
            'is_active': True
        }
    
    def validate_api_key(self, api_key: str, stored_hash: str) -> bool:
        """Validate API key against stored hash"""
        if not api_key or not stored_hash:
            return False
        
        # Hash the provided key
        provided_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Constant-time comparison to prevent timing attacks
        return secrets.compare_digest(provided_hash, stored_hash)
    
    def rotate_api_key(self, old_key_hash: str, user_id: str) -> Dict[str, str]:
        """
        Rotate an API key (generate new, invalidate old)
        
        Returns new key info
        """
        # Generate new key
        new_key_info = self.generate_api_key(user_id, "Rotated key")
        
        # Old key should be marked as inactive in database
        # (handled by caller)
        
        logger.info(f"API key rotated for user: {user_id}")
        return new_key_info


class RequestValidator:
    """Validates and sanitizes API requests"""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"('.*OR.*'.*=.*')",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"\.\.\\",
    ]
    
    def __init__(self):
        self.sql_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.SQL_INJECTION_PATTERNS]
        self.xss_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS]
        self.path_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.PATH_TRAVERSAL_PATTERNS]
    
    def validate_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate incoming API request
        
        Returns:
            {
                'valid': True/False,
                'errors': ['error1', 'error2'],
                'sanitized_body': {...}
            }
        """
        errors = []
        
        # Validate HTTP method
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method'))
        if http_method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']:
            errors.append(f"Invalid HTTP method: {http_method}")
        
        # Validate content type for POST/PUT
        if http_method in ['POST', 'PUT', 'PATCH']:
            headers = event.get('headers', {})
            content_type = headers.get('Content-Type', headers.get('content-type', ''))
            if 'application/json' not in content_type.lower():
                errors.append("Invalid Content-Type. Expected application/json")
        
        # Parse and validate body
        body = event.get('body', '{}')
        if isinstance(body, str):
            try:
                body = json.loads(body) if body else {}
            except json.JSONDecodeError:
                errors.append("Invalid JSON in request body")
                body = {}
        
        # Sanitize body
        sanitized_body = self.sanitize_input(body)
        
        # Check for injection attacks
        body_str = json.dumps(sanitized_body)
        
        if self._contains_sql_injection(body_str):
            errors.append("Potential SQL injection detected")
            logger.warning(f"SQL injection attempt detected: {body_str[:100]}")
        
        if self._contains_xss(body_str):
            errors.append("Potential XSS attack detected")
            logger.warning(f"XSS attempt detected: {body_str[:100]}")
        
        if self._contains_path_traversal(body_str):
            errors.append("Potential path traversal detected")
            logger.warning(f"Path traversal attempt detected: {body_str[:100]}")
        
        # Validate path parameters
        path_params = event.get('pathParameters', {})
        if path_params:
            for key, value in path_params.items():
                if self._contains_path_traversal(str(value)):
                    errors.append(f"Invalid path parameter: {key}")
        
        # Validate query parameters
        query_params = event.get('queryStringParameters', {})
        if query_params:
            for key, value in query_params.items():
                if self._contains_sql_injection(str(value)) or self._contains_xss(str(value)):
                    errors.append(f"Invalid query parameter: {key}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'sanitized_body': sanitized_body
        }
    
    def sanitize_input(self, data: Any) -> Any:
        """Recursively sanitize input data"""
        if isinstance(data, dict):
            return {key: self.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        elif isinstance(data, str):
            # Remove null bytes
            data = data.replace('\x00', '')
            # Limit string length
            if len(data) > 10000:
                data = data[:10000]
            return data
        else:
            return data
    
    def _contains_sql_injection(self, text: str) -> bool:
        """Check if text contains SQL injection patterns"""
        return any(regex.search(text) for regex in self.sql_regex)
    
    def _contains_xss(self, text: str) -> bool:
        """Check if text contains XSS patterns"""
        return any(regex.search(text) for regex in self.xss_regex)
    
    def _contains_path_traversal(self, text: str) -> bool:
        """Check if text contains path traversal patterns"""
        return any(regex.search(text) for regex in self.path_regex)


class SecurityHeaders:
    """Manages security headers for API responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get comprehensive security headers
        
        Returns headers that protect against:
        - XSS attacks
        - Clickjacking
        - MIME sniffing
        - Information leakage
        """
        return {
            # Prevent XSS attacks
            'X-Content-Type-Options': 'nosniff',
            
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            
            # Enable XSS protection
            'X-XSS-Protection': '1; mode=block',
            
            # Content Security Policy
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://bedrock-runtime.us-west-2.amazonaws.com",
            
            # Strict Transport Security (HTTPS only)
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Permissions policy
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            
            # CORS headers (configure as needed)
            'Access-Control-Allow-Origin': '*',  # Configure for your domain
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
            'Access-Control-Max-Age': '86400',
            
            # Cache control
            'Cache-Control': 'no-store, no-cache, must-revalidate, private',
            'Pragma': 'no-cache',
            
            # Content type
            'Content-Type': 'application/json'
        }
    
    @staticmethod
    def add_security_headers(response: Dict[str, Any]) -> Dict[str, Any]:
        """Add security headers to Lambda response"""
        if 'headers' not in response:
            response['headers'] = {}
        
        response['headers'].update(SecurityHeaders.get_security_headers())
        return response


class SecurityMiddleware:
    """Middleware for API security checks"""
    
    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.request_validator = RequestValidator()
    
    def validate_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate request security
        
        Returns:
            {
                'authorized': True/False,
                'error': 'error message',
                'sanitized_event': {...}
            }
        """
        # Validate request format and content
        validation_result = self.request_validator.validate_request(event)
        
        if not validation_result['valid']:
            return {
                'authorized': False,
                'error': f"Request validation failed: {', '.join(validation_result['errors'])}",
                'sanitized_event': None
            }
        
        # Update event with sanitized body
        sanitized_event = event.copy()
        sanitized_event['body'] = validation_result['sanitized_body']
        
        return {
            'authorized': True,
            'error': None,
            'sanitized_event': sanitized_event
        }
    
    def create_error_response(self, status_code: int, error_message: str) -> Dict[str, Any]:
        """Create secure error response"""
        response = {
            'statusCode': status_code,
            'body': json.dumps({
                'error': error_message,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
        return SecurityHeaders.add_security_headers(response)


# Global security middleware instance
security_middleware = SecurityMiddleware()


def secure_handler(handler_func):
    """
    Decorator to add security checks to Lambda handlers
    
    Usage:
        @secure_handler
        def my_handler(event, context):
            # Your handler code
            pass
    """
    def wrapper(event, context):
        # Validate request
        validation_result = security_middleware.validate_request(event)
        
        if not validation_result['authorized']:
            logger.warning(f"Unauthorized request: {validation_result['error']}")
            return security_middleware.create_error_response(
                400,
                validation_result['error']
            )
        
        # Call original handler with sanitized event
        try:
            response = handler_func(validation_result['sanitized_event'], context)
            
            # Add security headers to response
            return SecurityHeaders.add_security_headers(response)
            
        except Exception as e:
            logger.error(f"Handler error: {str(e)}", exc_info=True)
            return security_middleware.create_error_response(
                500,
                "Internal server error"
            )
    
    return wrapper
