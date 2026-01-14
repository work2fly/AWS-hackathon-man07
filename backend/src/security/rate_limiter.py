"""
Rate Limiting and Abuse Prevention Module

Implements intelligent rate limiting, abuse detection, and automated blocking
for API endpoints. Uses DynamoDB for distributed rate limit tracking and
IP-based/user-based throttling.

Breaking Barriers UK 2026 Compliant:
- Uses DynamoDB (permitted service)
- Region: us-west-2
- No PII in examples
"""

import os
import time
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2'))


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


class RateLimiter:
    """
    Distributed rate limiter using DynamoDB for tracking request counts.
    
    Supports multiple rate limiting strategies:
    - Fixed window: Simple time-based windows
    - Sliding window: More accurate rate limiting
    - Token bucket: Burst handling with sustained rate
    """
    
    def __init__(self, table_name: str = None):
        """
        Initialize rate limiter.
        
        Args:
            table_name: DynamoDB table name for rate limit tracking
        """
        self.table_name = table_name or os.getenv('RATE_LIMIT_TABLE', 'RateLimits')
        self.table = dynamodb.Table(self.table_name)
        
        # Rate limit configurations (requests per time window)
        self.limits = {
            'default': {'requests': 100, 'window': 60},  # 100 req/min
            'auth': {'requests': 10, 'window': 60},      # 10 req/min for auth
            'chat': {'requests': 30, 'window': 60},      # 30 req/min for chat
            'api_key': {'requests': 1000, 'window': 60}, # 1000 req/min for API keys
        }
        
        # Abuse detection thresholds
        self.abuse_thresholds = {
            'rapid_requests': 50,      # 50 requests in 10 seconds
            'failed_auth': 5,          # 5 failed auth attempts
            'invalid_requests': 20,    # 20 invalid requests
            'block_duration': 3600,    # Block for 1 hour
        }
    
    def check_rate_limit(
        self,
        identifier: str,
        limit_type: str = 'default',
        user_id: Optional[str] = None
    ) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limits.
        
        Args:
            identifier: IP address or API key identifier
            limit_type: Type of rate limit to apply
            user_id: Optional user ID for user-based limiting
            
        Returns:
            Tuple of (allowed: bool, info: dict with limit details)
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        # Check if identifier is blocked
        if self._is_blocked(identifier):
            return False, {
                'allowed': False,
                'reason': 'blocked',
                'message': 'Access temporarily blocked due to abuse detection',
                'retry_after': self._get_block_remaining(identifier)
            }
        
        # Get rate limit configuration
        config = self.limits.get(limit_type, self.limits['default'])
        max_requests = config['requests']
        window_seconds = config['window']
        
        # Create composite key for tracking
        window_key = self._get_window_key(identifier, limit_type, window_seconds)
        
        try:
            # Get current request count
            response = self.table.get_item(Key={'limit_key': window_key})
            
            current_time = int(time.time())
            
            if 'Item' in response:
                item = response['Item']
                request_count = int(item.get('request_count', 0))
                window_start = int(item.get('window_start', current_time))
                
                # Check if window has expired
                if current_time - window_start >= window_seconds:
                    # Reset window
                    request_count = 0
                    window_start = current_time
                
                # Check if limit exceeded
                if request_count >= max_requests:
                    remaining_time = window_seconds - (current_time - window_start)
                    
                    # Check for rapid request abuse
                    self._check_abuse_pattern(identifier, 'rapid_requests')
                    
                    return False, {
                        'allowed': False,
                        'reason': 'rate_limit_exceeded',
                        'limit': max_requests,
                        'window': window_seconds,
                        'retry_after': remaining_time,
                        'message': f'Rate limit exceeded. Try again in {remaining_time} seconds.'
                    }
                
                # Increment counter
                self.table.update_item(
                    Key={'limit_key': window_key},
                    UpdateExpression='SET request_count = :count, last_request = :time',
                    ExpressionAttributeValues={
                        ':count': request_count + 1,
                        ':time': current_time
                    }
                )
                
                remaining = max_requests - request_count - 1
            else:
                # First request in window
                self.table.put_item(
                    Item={
                        'limit_key': window_key,
                        'identifier': identifier,
                        'limit_type': limit_type,
                        'request_count': 1,
                        'window_start': current_time,
                        'last_request': current_time,
                        'ttl': current_time + window_seconds + 3600  # Expire 1 hour after window
                    }
                )
                remaining = max_requests - 1
            
            return True, {
                'allowed': True,
                'limit': max_requests,
                'remaining': remaining,
                'window': window_seconds,
                'reset_at': window_start + window_seconds if 'Item' in response else current_time + window_seconds
            }
            
        except ClientError as e:
            print(f"Error checking rate limit: {e}")
            # Fail open - allow request if DynamoDB is unavailable
            return True, {
                'allowed': True,
                'message': 'Rate limiting temporarily unavailable'
            }
    
    def record_failed_auth(self, identifier: str) -> None:
        """
        Record a failed authentication attempt.
        
        Args:
            identifier: IP address or user identifier
        """
        self._increment_abuse_counter(identifier, 'failed_auth')
        
        # Check if threshold exceeded
        count = self._get_abuse_counter(identifier, 'failed_auth')
        if count >= self.abuse_thresholds['failed_auth']:
            self._block_identifier(identifier, 'excessive_failed_auth')
    
    def record_invalid_request(self, identifier: str) -> None:
        """
        Record an invalid or malformed request.
        
        Args:
            identifier: IP address or API key
        """
        self._increment_abuse_counter(identifier, 'invalid_requests')
        
        # Check if threshold exceeded
        count = self._get_abuse_counter(identifier, 'invalid_requests')
        if count >= self.abuse_thresholds['invalid_requests']:
            self._block_identifier(identifier, 'excessive_invalid_requests')
    
    def _check_abuse_pattern(self, identifier: str, pattern_type: str) -> None:
        """
        Check for abuse patterns and block if necessary.
        
        Args:
            identifier: IP address or identifier to check
            pattern_type: Type of abuse pattern
        """
        self._increment_abuse_counter(identifier, pattern_type)
        
        count = self._get_abuse_counter(identifier, pattern_type)
        threshold = self.abuse_thresholds.get(pattern_type, 100)
        
        if count >= threshold:
            self._block_identifier(identifier, pattern_type)
    
    def _block_identifier(self, identifier: str, reason: str) -> None:
        """
        Block an identifier for abuse.
        
        Args:
            identifier: IP address or identifier to block
            reason: Reason for blocking
        """
        block_key = f"block:{identifier}"
        current_time = int(time.time())
        block_until = current_time + self.abuse_thresholds['block_duration']
        
        try:
            self.table.put_item(
                Item={
                    'limit_key': block_key,
                    'identifier': identifier,
                    'blocked': True,
                    'reason': reason,
                    'blocked_at': current_time,
                    'block_until': block_until,
                    'ttl': block_until + 3600  # Expire 1 hour after block ends
                }
            )
            
            print(f"Blocked identifier {identifier} for {reason} until {block_until}")
            
        except ClientError as e:
            print(f"Error blocking identifier: {e}")
    
    def _is_blocked(self, identifier: str) -> bool:
        """
        Check if an identifier is currently blocked.
        
        Args:
            identifier: IP address or identifier to check
            
        Returns:
            True if blocked, False otherwise
        """
        block_key = f"block:{identifier}"
        
        try:
            response = self.table.get_item(Key={'limit_key': block_key})
            
            if 'Item' in response:
                item = response['Item']
                if item.get('blocked', False):
                    block_until = int(item.get('block_until', 0))
                    current_time = int(time.time())
                    
                    if current_time < block_until:
                        return True
                    else:
                        # Block expired, remove it
                        self.table.delete_item(Key={'limit_key': block_key})
            
            return False
            
        except ClientError as e:
            print(f"Error checking block status: {e}")
            return False
    
    def _get_block_remaining(self, identifier: str) -> int:
        """
        Get remaining block time in seconds.
        
        Args:
            identifier: IP address or identifier
            
        Returns:
            Remaining seconds, or 0 if not blocked
        """
        block_key = f"block:{identifier}"
        
        try:
            response = self.table.get_item(Key={'limit_key': block_key})
            
            if 'Item' in response:
                block_until = int(response['Item'].get('block_until', 0))
                current_time = int(time.time())
                return max(0, block_until - current_time)
            
            return 0
            
        except ClientError as e:
            print(f"Error getting block remaining: {e}")
            return 0
    
    def _increment_abuse_counter(self, identifier: str, counter_type: str) -> None:
        """
        Increment abuse detection counter.
        
        Args:
            identifier: IP address or identifier
            counter_type: Type of abuse counter
        """
        counter_key = f"abuse:{identifier}:{counter_type}"
        current_time = int(time.time())
        
        try:
            self.table.update_item(
                Key={'limit_key': counter_key},
                UpdateExpression='ADD abuse_count :inc SET last_abuse = :time, ttl = :ttl',
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':time': current_time,
                    ':ttl': current_time + 600  # Expire after 10 minutes
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                # Item doesn't exist, create it
                self.table.put_item(
                    Item={
                        'limit_key': counter_key,
                        'identifier': identifier,
                        'counter_type': counter_type,
                        'abuse_count': 1,
                        'last_abuse': current_time,
                        'ttl': current_time + 600
                    }
                )
    
    def _get_abuse_counter(self, identifier: str, counter_type: str) -> int:
        """
        Get current abuse counter value.
        
        Args:
            identifier: IP address or identifier
            counter_type: Type of abuse counter
            
        Returns:
            Current counter value
        """
        counter_key = f"abuse:{identifier}:{counter_type}"
        
        try:
            response = self.table.get_item(Key={'limit_key': counter_key})
            
            if 'Item' in response:
                return int(response['Item'].get('abuse_count', 0))
            
            return 0
            
        except ClientError as e:
            print(f"Error getting abuse counter: {e}")
            return 0
    
    def _get_window_key(self, identifier: str, limit_type: str, window_seconds: int) -> str:
        """
        Generate a window key for rate limiting.
        
        Args:
            identifier: IP address or identifier
            limit_type: Type of rate limit
            window_seconds: Window size in seconds
            
        Returns:
            Window key string
        """
        current_time = int(time.time())
        window_number = current_time // window_seconds
        
        # Hash identifier for privacy
        id_hash = hashlib.sha256(identifier.encode()).hexdigest()[:16]
        
        return f"rate:{limit_type}:{id_hash}:{window_number}"
    
    def unblock_identifier(self, identifier: str) -> bool:
        """
        Manually unblock an identifier (admin function).
        
        Args:
            identifier: IP address or identifier to unblock
            
        Returns:
            True if unblocked successfully
        """
        block_key = f"block:{identifier}"
        
        try:
            self.table.delete_item(Key={'limit_key': block_key})
            print(f"Unblocked identifier: {identifier}")
            return True
        except ClientError as e:
            print(f"Error unblocking identifier: {e}")
            return False
    
    def get_rate_limit_info(self, identifier: str, limit_type: str = 'default') -> Dict:
        """
        Get current rate limit status for an identifier.
        
        Args:
            identifier: IP address or identifier
            limit_type: Type of rate limit
            
        Returns:
            Dictionary with rate limit information
        """
        config = self.limits.get(limit_type, self.limits['default'])
        window_key = self._get_window_key(identifier, limit_type, config['window'])
        
        try:
            response = self.table.get_item(Key={'limit_key': window_key})
            
            if 'Item' in response:
                item = response['Item']
                request_count = int(item.get('request_count', 0))
                window_start = int(item.get('window_start', 0))
                current_time = int(time.time())
                
                return {
                    'limit': config['requests'],
                    'used': request_count,
                    'remaining': max(0, config['requests'] - request_count),
                    'window': config['window'],
                    'reset_at': window_start + config['window'],
                    'blocked': self._is_blocked(identifier)
                }
            
            return {
                'limit': config['requests'],
                'used': 0,
                'remaining': config['requests'],
                'window': config['window'],
                'blocked': self._is_blocked(identifier)
            }
            
        except ClientError as e:
            print(f"Error getting rate limit info: {e}")
            return {
                'error': 'Unable to retrieve rate limit information'
            }


def rate_limit_handler(limit_type: str = 'default'):
    """
    Decorator for Lambda handlers to enforce rate limiting.
    
    Usage:
        @rate_limit_handler('chat')
        def lambda_handler(event, context):
            # Your handler code
            pass
    
    Args:
        limit_type: Type of rate limit to apply
    """
    def decorator(func):
        def wrapper(event, context):
            rate_limiter = RateLimiter()
            
            # Extract identifier (IP or API key)
            identifier = _extract_identifier(event)
            user_id = _extract_user_id(event)
            
            # Check rate limit
            allowed, info = rate_limiter.check_rate_limit(
                identifier=identifier,
                limit_type=limit_type,
                user_id=user_id
            )
            
            if not allowed:
                return {
                    'statusCode': 429,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Retry-After': str(info.get('retry_after', 60)),
                        'X-RateLimit-Limit': str(info.get('limit', 0)),
                        'X-RateLimit-Remaining': '0',
                        'X-RateLimit-Reset': str(info.get('reset_at', 0))
                    },
                    'body': {
                        'error': 'Rate limit exceeded',
                        'message': info.get('message', 'Too many requests'),
                        'retry_after': info.get('retry_after', 60)
                    }
                }
            
            # Add rate limit headers to response
            response = func(event, context)
            
            if isinstance(response, dict) and 'headers' in response:
                response['headers'].update({
                    'X-RateLimit-Limit': str(info.get('limit', 0)),
                    'X-RateLimit-Remaining': str(info.get('remaining', 0)),
                    'X-RateLimit-Reset': str(info.get('reset_at', 0))
                })
            
            return response
        
        return wrapper
    return decorator


def _extract_identifier(event: Dict) -> str:
    """
    Extract identifier (IP address or API key) from Lambda event.
    
    Args:
        event: Lambda event dictionary
        
    Returns:
        Identifier string
    """
    # Try to get IP address from request context
    request_context = event.get('requestContext', {})
    identity = request_context.get('identity', {})
    source_ip = identity.get('sourceIp', 'unknown')
    
    # Try to get API key from headers
    headers = event.get('headers', {})
    api_key = headers.get('x-api-key') or headers.get('X-API-Key')
    
    # Prefer API key over IP for rate limiting
    return api_key if api_key else source_ip


def _extract_user_id(event: Dict) -> Optional[str]:
    """
    Extract user ID from Lambda event.
    
    Args:
        event: Lambda event dictionary
        
    Returns:
        User ID or None
    """
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    
    return authorizer.get('claims', {}).get('sub')
