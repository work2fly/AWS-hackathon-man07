"""
WebSocket Security and Rate Limiting for AI Therapy Platform
Implements connection authentication, rate limiting, and abuse prevention
Breaking Barriers UK 2026 compliant
"""

import time
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque

import boto3
from botocore.exceptions import ClientError

from .logger import get_logger
from ..services.cognito_service import cognito_service

logger = get_logger(__name__)

# AWS clients
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

class RateLimiter:
    """Rate limiting for WebSocket connections"""
    
    def __init__(self):
        # In-memory rate limiting (for Lambda, this resets per cold start)
        # For production, consider using Redis or DynamoDB for persistent rate limiting
        self.connection_requests = defaultdict(deque)  # connection_id -> deque of timestamps
        self.ip_requests = defaultdict(deque)  # ip_address -> deque of timestamps
        self.user_requests = defaultdict(deque)  # user_id -> deque of timestamps
        
        # Rate limiting configuration
        self.limits = {
            'connection_messages_per_minute': 60,  # 60 messages per minute per connection
            'connection_messages_per_hour': 1000,  # 1000 messages per hour per connection
            'ip_connections_per_minute': 10,  # 10 new connections per minute per IP
            'ip_connections_per_hour': 100,  # 100 new connections per hour per IP
            'user_connections_per_minute': 5,  # 5 new connections per minute per user
            'user_messages_per_minute': 100,  # 100 messages per minute per user
            'audio_data_per_minute': 30,  # 30 audio messages per minute per connection
            'audio_data_size_mb': 10  # 10MB max audio data per message
        }
    
    def _cleanup_old_requests(self, request_deque: deque, window_seconds: int):
        """Remove old requests outside the time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        while request_deque and request_deque[0] < cutoff_time:
            request_deque.popleft()
    
    def check_connection_rate_limit(self, connection_id: str, message_type: str = 'message') -> Tuple[bool, str]:
        """Check if connection is within rate limits"""
        current_time = time.time()
        
        # Get request history for this connection
        requests = self.connection_requests[connection_id]
        
        # Clean up old requests
        self._cleanup_old_requests(requests, 3600)  # 1 hour window
        
        # Check per-minute limit
        minute_requests = sum(1 for req_time in requests if req_time > current_time - 60)
        if minute_requests >= self.limits['connection_messages_per_minute']:
            return False, f"Rate limit exceeded: {minute_requests} messages in last minute"
        
        # Check per-hour limit
        hour_requests = len(requests)
        if hour_requests >= self.limits['connection_messages_per_hour']:
            return False, f"Rate limit exceeded: {hour_requests} messages in last hour"
        
        # Special limits for audio data
        if message_type == 'audio_data':
            audio_requests = sum(1 for req_time in requests if req_time > current_time - 60)
            if audio_requests >= self.limits['audio_data_per_minute']:
                return False, f"Audio rate limit exceeded: {audio_requests} audio messages in last minute"
        
        # Add current request
        requests.append(current_time)
        
        return True, "OK"
    
    def check_ip_rate_limit(self, ip_address: str, action: str = 'connection') -> Tuple[bool, str]:
        """Check if IP address is within rate limits"""
        current_time = time.time()
        
        # Get request history for this IP
        requests = self.ip_requests[ip_address]
        
        # Clean up old requests
        self._cleanup_old_requests(requests, 3600)  # 1 hour window
        
        if action == 'connection':
            # Check per-minute connection limit
            minute_requests = sum(1 for req_time in requests if req_time > current_time - 60)
            if minute_requests >= self.limits['ip_connections_per_minute']:
                return False, f"IP rate limit exceeded: {minute_requests} connections in last minute"
            
            # Check per-hour connection limit
            hour_requests = len(requests)
            if hour_requests >= self.limits['ip_connections_per_hour']:
                return False, f"IP rate limit exceeded: {hour_requests} connections in last hour"
        
        # Add current request
        requests.append(current_time)
        
        return True, "OK"
    
    def check_user_rate_limit(self, user_id: str, action: str = 'message') -> Tuple[bool, str]:
        """Check if user is within rate limits"""
        current_time = time.time()
        
        # Get request history for this user
        requests = self.user_requests[user_id]
        
        # Clean up old requests
        self._cleanup_old_requests(requests, 3600)  # 1 hour window
        
        if action == 'connection':
            # Check per-minute connection limit
            minute_requests = sum(1 for req_time in requests if req_time > current_time - 60)
            if minute_requests >= self.limits['user_connections_per_minute']:
                return False, f"User rate limit exceeded: {minute_requests} connections in last minute"
        
        elif action == 'message':
            # Check per-minute message limit
            minute_requests = sum(1 for req_time in requests if req_time > current_time - 60)
            if minute_requests >= self.limits['user_messages_per_minute']:
                return False, f"User rate limit exceeded: {minute_requests} messages in last minute"
        
        # Add current request
        requests.append(current_time)
        
        return True, "OK"
    
    def check_audio_data_size(self, data_size_bytes: int) -> Tuple[bool, str]:
        """Check if audio data size is within limits"""
        max_size_bytes = self.limits['audio_data_size_mb'] * 1024 * 1024
        
        if data_size_bytes > max_size_bytes:
            return False, f"Audio data too large: {data_size_bytes} bytes (max: {max_size_bytes})"
        
        return True, "OK"
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get current rate limiting statistics"""
        current_time = time.time()
        
        stats = {
            'active_connections': len(self.connection_requests),
            'active_ips': len(self.ip_requests),
            'active_users': len(self.user_requests),
            'total_requests_last_minute': 0,
            'total_requests_last_hour': 0
        }
        
        # Count recent requests
        for requests in self.connection_requests.values():
            stats['total_requests_last_minute'] += sum(1 for req_time in requests if req_time > current_time - 60)
            stats['total_requests_last_hour'] += len(requests)
        
        return stats

class WebSocketSecurityManager:
    """Manages WebSocket security, authentication, and monitoring"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.blocked_ips = set()  # In-memory blocked IPs (consider using DynamoDB for persistence)
        self.suspicious_patterns = {
            'rapid_connections': 20,  # More than 20 connections in 1 minute
            'excessive_messages': 200,  # More than 200 messages in 1 minute
            'invalid_message_ratio': 0.5,  # More than 50% invalid messages
            'failed_auth_attempts': 10  # More than 10 failed auth attempts
        }
    
    def authenticate_connection(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate WebSocket connection"""
        try:
            # Extract IP address for rate limiting
            ip_address = self._get_client_ip(event)
            
            # Check if IP is blocked
            if ip_address in self.blocked_ips:
                logger.warning(f"Blocked IP attempted connection: {ip_address}")
                self._log_security_event('blocked_ip_connection', {'ip_address': ip_address})
                return None
            
            # Check IP rate limits
            ip_allowed, ip_message = self.rate_limiter.check_ip_rate_limit(ip_address, 'connection')
            if not ip_allowed:
                logger.warning(f"IP rate limit exceeded for {ip_address}: {ip_message}")
                self._log_security_event('ip_rate_limit_exceeded', {
                    'ip_address': ip_address,
                    'message': ip_message
                })
                return None
            
            # Get authentication token
            token = self._extract_auth_token(event)
            if not token:
                logger.warning(f"No authentication token provided from IP: {ip_address}")
                self._log_security_event('missing_auth_token', {'ip_address': ip_address})
                return None
            
            # Verify JWT token
            token_info = cognito_service.verify_jwt_token(token)
            if not token_info['valid']:
                logger.warning(f"Invalid token from IP {ip_address}: {token_info.get('error')}")
                self._log_security_event('invalid_auth_token', {
                    'ip_address': ip_address,
                    'error': token_info.get('error')
                })
                return None
            
            # Get user information
            from ..data.user_repository import user_repository
            user_data = user_repository.get_user_by_email(token_info['email'])
            
            if not user_data:
                logger.warning(f"User not found for token from IP {ip_address}: {token_info['email']}")
                self._log_security_event('user_not_found', {
                    'ip_address': ip_address,
                    'email': token_info['email']
                })
                return None
            
            # Check if user account is active
            if not user_data.get('isActive', True):
                logger.warning(f"Inactive user attempted connection: {user_data['userId']}")
                self._log_security_event('inactive_user_connection', {
                    'user_id': user_data['userId'],
                    'ip_address': ip_address
                })
                return None
            
            # Check user rate limits
            user_allowed, user_message = self.rate_limiter.check_user_rate_limit(user_data['userId'], 'connection')
            if not user_allowed:
                logger.warning(f"User rate limit exceeded for {user_data['userId']}: {user_message}")
                self._log_security_event('user_rate_limit_exceeded', {
                    'user_id': user_data['userId'],
                    'message': user_message
                })
                return None
            
            # Log successful authentication
            self._log_security_event('successful_auth', {
                'user_id': user_data['userId'],
                'ip_address': ip_address,
                'role': user_data['role']
            })
            
            return {
                'user_id': user_data['userId'],
                'email': user_data['email'],
                'role': user_data['role'],
                'username': token_info['username'],
                'ip_address': ip_address
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self._log_security_event('auth_error', {'error': str(e)})
            return None
    
    def validate_message_security(self, connection_id: str, user_id: str, 
                                 message: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate message security and rate limits"""
        try:
            message_type = message.get('type', 'unknown')
            
            # Check connection rate limits
            allowed, rate_message = self.rate_limiter.check_connection_rate_limit(connection_id, message_type)
            if not allowed:
                self._log_security_event('connection_rate_limit_exceeded', {
                    'connection_id': connection_id,
                    'user_id': user_id,
                    'message': rate_message
                })
                return False, rate_message
            
            # Check user rate limits
            user_allowed, user_message = self.rate_limiter.check_user_rate_limit(user_id, 'message')
            if not user_allowed:
                self._log_security_event('user_message_rate_limit_exceeded', {
                    'user_id': user_id,
                    'connection_id': connection_id,
                    'message': user_message
                })
                return False, user_message
            
            # Special validation for audio data
            if message_type == 'audio_data':
                return self._validate_audio_message(connection_id, user_id, message)
            
            # Validate message content for suspicious patterns
            if not self._validate_message_content(message):
                self._log_security_event('suspicious_message_content', {
                    'connection_id': connection_id,
                    'user_id': user_id,
                    'message_type': message_type
                })
                return False, "Message content validation failed"
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Message security validation error: {str(e)}")
            return False, "Security validation error"
    
    def _validate_audio_message(self, connection_id: str, user_id: str, 
                               message: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate audio message security"""
        # Check audio data size
        audio_data = message.get('data', '')
        if isinstance(audio_data, str):
            # Estimate size for base64 encoded data
            estimated_size = len(audio_data) * 3 // 4  # Base64 overhead
        else:
            estimated_size = len(str(audio_data))
        
        size_allowed, size_message = self.rate_limiter.check_audio_data_size(estimated_size)
        if not size_allowed:
            self._log_security_event('audio_size_limit_exceeded', {
                'connection_id': connection_id,
                'user_id': user_id,
                'size_bytes': estimated_size
            })
            return False, size_message
        
        # Validate audio format if specified
        audio_format = message.get('format', '').lower()
        if audio_format and audio_format not in ['wav', 'mp3', 'webm', 'ogg']:
            self._log_security_event('invalid_audio_format', {
                'connection_id': connection_id,
                'user_id': user_id,
                'format': audio_format
            })
            return False, f"Invalid audio format: {audio_format}"
        
        return True, "OK"
    
    def _validate_message_content(self, message: Dict[str, Any]) -> bool:
        """Validate message content for suspicious patterns"""
        try:
            # Check for excessively large messages
            message_str = json.dumps(message)
            if len(message_str) > 100000:  # 100KB limit
                return False
            
            # Check for suspicious content patterns
            content = message.get('content', '')
            if isinstance(content, str):
                # Check for script injection attempts
                suspicious_patterns = [
                    '<script', 'javascript:', 'data:text/html',
                    'eval(', 'setTimeout(', 'setInterval(',
                    'document.cookie', 'localStorage', 'sessionStorage'
                ]
                
                content_lower = content.lower()
                for pattern in suspicious_patterns:
                    if pattern in content_lower:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Content validation error: {str(e)}")
            return False
    
    def _get_client_ip(self, event: Dict[str, Any]) -> str:
        """Extract client IP address from event"""
        # Try multiple sources for IP address
        request_context = event.get('requestContext', {})
        
        # API Gateway WebSocket
        if 'identity' in request_context:
            identity = request_context['identity']
            return identity.get('sourceIp', 'unknown')
        
        # Fallback to headers
        headers = event.get('headers', {})
        for header in ['X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP']:
            if header in headers:
                # Take first IP if comma-separated
                return headers[header].split(',')[0].strip()
        
        return 'unknown'
    
    def _extract_auth_token(self, event: Dict[str, Any]) -> Optional[str]:
        """Extract authentication token from event"""
        # Try query parameters first
        query_params = event.get('queryStringParameters') or {}
        token = query_params.get('token')
        
        if token:
            return token
        
        # Try headers
        headers = event.get('headers') or {}
        auth_header = headers.get('Authorization') or headers.get('authorization', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header.replace('Bearer ', '')
        
        return None
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event to CloudWatch"""
        try:
            # Log to application logs
            logger.info(f"Security event: {event_type}", extra=details)
            
            # Send custom metric to CloudWatch
            cloudwatch.put_metric_data(
                Namespace='AITherapyPlatform/WebSocket/Security',
                MetricData=[
                    {
                        'MetricName': event_type,
                        'Value': 1,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {
                                'Name': 'EventType',
                                'Value': event_type
                            }
                        ]
                    }
                ]
            )
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    def block_ip(self, ip_address: str, reason: str):
        """Block an IP address"""
        self.blocked_ips.add(ip_address)
        self._log_security_event('ip_blocked', {
            'ip_address': ip_address,
            'reason': reason
        })
        logger.warning(f"Blocked IP address {ip_address}: {reason}")
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip_address)
        self._log_security_event('ip_unblocked', {'ip_address': ip_address})
        logger.info(f"Unblocked IP address: {ip_address}")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        rate_stats = self.rate_limiter.get_rate_limit_stats()
        
        return {
            'blocked_ips': len(self.blocked_ips),
            'rate_limiting': rate_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def cleanup_old_data(self):
        """Clean up old rate limiting data"""
        # This is automatically handled by the deque cleanup in rate limiting methods
        # For production, consider implementing periodic cleanup
        pass

# Global security manager instance
websocket_security_manager = WebSocketSecurityManager()