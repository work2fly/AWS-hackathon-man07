"""
Rate Limiting and Abuse Prevention Service
Implements intelligent rate limiting, abuse detection, and automated blocking
🏆 Breaking Barriers UK 2026 compliant
"""

import time
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass

from ..utils.logger import get_logger
from ..utils.metrics import metrics
from ..data.base import DynamoDBRepository

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int  # Maximum burst requests
    burst_window_seconds: int  # Burst window


@dataclass
class AbusePattern:
    """Abuse pattern detection"""
    pattern_type: str
    severity: str
    threshold: int
    window_seconds: int
    action: str  # warn, throttle, block


class RateLimitingService:
    """
    Comprehensive rate limiting and abuse prevention service
    Uses DynamoDB for distributed rate limiting across Lambda instances
    """
    
    # Default rate limit configurations by user role
    DEFAULT_LIMITS = {
        'client': RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_limit=10,
            burst_window_seconds=5
        ),
        'therapist': RateLimitConfig(
            requests_per_minute=120,
            requests_per_hour=2000,
            requests_per_day=20000,
            burst_limit=20,
            burst_window_seconds=5
        ),
        'admin': RateLimitConfig(
            requests_per_minute=200,
            requests_per_hour=5000,
            requests_per_day=50000,
            burst_limit=30,
            burst_window_seconds=5
        ),
        'anonymous': RateLimitConfig(
            requests_per_minute=10,
            requests_per_hour=100,
            requests_per_day=500,
            burst_limit=5,
            burst_window_seconds=5
        )
    }
    
    # Abuse detection patterns
    ABUSE_PATTERNS = [
        AbusePattern(
            pattern_type='rapid_requests',
            severity='high',
            threshold=100,
            window_seconds=10,
            action='block'
        ),
        AbusePattern(
            pattern_type='failed_auth_attempts',
            severity='high',
            threshold=5,
            window_seconds=300,
            action='block'
        ),
        AbusePattern(
            pattern_type='invalid_requests',
            severity='medium',
            threshold=20,
            window_seconds=60,
            action='throttle'
        ),
        AbusePattern(
            pattern_type='suspicious_patterns',
            severity='medium',
            threshold=10,
            window_seconds=300,
            action='warn'
        )
    ]
    
    def __init__(self):
        self.repository = DynamoDBRepository('RateLimits')
        self.blocked_identifiers = {}  # {identifier: (blocked_until, reason)}
        self.request_history = defaultdict(list)  # In-memory cache
        self.abuse_scores = defaultdict(int)  # Abuse scoring
    
    def check_rate_limit(self, identifier: str, user_role: str = 'anonymous',
                        endpoint: str = None) -> Tuple[bool, Optional[str]]:
        """
        Check if request is within rate limits
        
        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            user_role: User role for role-based limits
            endpoint: API endpoint for endpoint-specific limits
            
        Returns:
            Tuple of (allowed: bool, reason: Optional[str])
        """
        try:
            # Check if identifier is blocked
            if self._is_blocked(identifier):
                reason = self.blocked_identifiers[identifier][1]
                logger.warning(
                    f"Blocked identifier attempted request: {identifier}",
                    identifier=identifier,
                    reason=reason
                )
                metrics.put_metric('BlockedRequests', 1, dimensions={
                    'Identifier': identifier
                })
                return False, f"Access blocked: {reason}"
            
            # Get rate limit configuration
            config = self.DEFAULT_LIMITS.get(user_role, self.DEFAULT_LIMITS['anonymous'])
            
            # Check burst limit
            if not self._check_burst_limit(identifier, config):
                logger.warning(
                    f"Burst limit exceeded: {identifier}",
                    identifier=identifier,
                    user_role=user_role
                )
                metrics.put_metric('BurstLimitExceeded', 1, dimensions={
                    'UserRole': user_role
                })
                return False, "Burst limit exceeded. Please slow down."
            
            # Check minute limit
            if not self._check_time_window_limit(identifier, config.requests_per_minute, 60):
                logger.warning(
                    f"Per-minute rate limit exceeded: {identifier}",
                    identifier=identifier,
                    user_role=user_role
                )
                metrics.put_metric('RateLimitExceeded', 1, dimensions={
                    'Window': 'minute',
                    'UserRole': user_role
                })
                return False, "Rate limit exceeded. Maximum 60 requests per minute."
            
            # Check hour limit
            if not self._check_time_window_limit(identifier, config.requests_per_hour, 3600):
                logger.warning(
                    f"Per-hour rate limit exceeded: {identifier}",
                    identifier=identifier,
                    user_role=user_role
                )
                metrics.put_metric('RateLimitExceeded', 1, dimensions={
                    'Window': 'hour',
                    'UserRole': user_role
                })
                return False, "Rate limit exceeded. Maximum requests per hour reached."
            
            # Check day limit
            if not self._check_time_window_limit(identifier, config.requests_per_day, 86400):
                logger.warning(
                    f"Per-day rate limit exceeded: {identifier}",
                    identifier=identifier,
                    user_role=user_role
                )
                metrics.put_metric('RateLimitExceeded', 1, dimensions={
                    'Window': 'day',
                    'UserRole': user_role
                })
                return False, "Daily rate limit exceeded. Please try again tomorrow."
            
            # Record request
            self._record_request(identifier)
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}", error=e)
            # Fail open for availability, but log the error
            return True, None
    
    def detect_abuse(self, identifier: str, event_type: str, 
                    metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Detect abuse patterns and take action
        
        Args:
            identifier: Unique identifier
            event_type: Type of event (request, auth_failure, invalid_request, etc.)
            metadata: Additional event metadata
            
        Returns:
            Action taken (None, 'warn', 'throttle', 'block')
        """
        try:
            current_time = time.time()
            
            # Check each abuse pattern
            for pattern in self.ABUSE_PATTERNS:
                if self._matches_abuse_pattern(identifier, event_type, pattern, current_time):
                    action = pattern.action
                    
                    logger.warning(
                        f"Abuse pattern detected: {pattern.pattern_type}",
                        identifier=identifier,
                        pattern_type=pattern.pattern_type,
                        severity=pattern.severity,
                        action=action
                    )
                    
                    metrics.put_metric('AbuseDetected', 1, dimensions={
                        'PatternType': pattern.pattern_type,
                        'Severity': pattern.severity,
                        'Action': action
                    })
                    
                    # Take action based on pattern
                    if action == 'block':
                        self._block_identifier(identifier, pattern.pattern_type, 
                                             duration_seconds=3600)  # 1 hour block
                        return 'block'
                    elif action == 'throttle':
                        self._increase_abuse_score(identifier, 10)
                        return 'throttle'
                    elif action == 'warn':
                        self._increase_abuse_score(identifier, 5)
                        return 'warn'
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting abuse: {str(e)}", error=e)
            return None
    
    def block_identifier(self, identifier: str, reason: str, 
                        duration_seconds: int = 3600) -> bool:
        """
        Manually block an identifier
        
        Args:
            identifier: Identifier to block
            reason: Reason for blocking
            duration_seconds: Block duration in seconds
            
        Returns:
            Boolean indicating success
        """
        try:
            self._block_identifier(identifier, reason, duration_seconds)
            
            logger.warning(
                f"Identifier manually blocked: {identifier}",
                identifier=identifier,
                reason=reason,
                duration_seconds=duration_seconds
            )
            
            metrics.put_metric('ManualBlocks', 1)
            
            return True
            
        except Exception as e:
            logger.error(f"Error blocking identifier: {str(e)}", error=e)
            return False
    
    def unblock_identifier(self, identifier: str) -> bool:
        """
        Unblock an identifier
        
        Args:
            identifier: Identifier to unblock
            
        Returns:
            Boolean indicating success
        """
        try:
            if identifier in self.blocked_identifiers:
                del self.blocked_identifiers[identifier]
                
                logger.info(
                    f"Identifier unblocked: {identifier}",
                    identifier=identifier
                )
                
                metrics.put_metric('ManualUnblocks', 1)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error unblocking identifier: {str(e)}", error=e)
            return False
    
    def get_rate_limit_status(self, identifier: str, user_role: str = 'anonymous') -> Dict[str, Any]:
        """
        Get current rate limit status for an identifier
        
        Args:
            identifier: Unique identifier
            user_role: User role
            
        Returns:
            Dictionary with rate limit status
        """
        try:
            config = self.DEFAULT_LIMITS.get(user_role, self.DEFAULT_LIMITS['anonymous'])
            current_time = time.time()
            
            # Count requests in different windows
            requests_last_minute = self._count_requests_in_window(identifier, 60, current_time)
            requests_last_hour = self._count_requests_in_window(identifier, 3600, current_time)
            requests_last_day = self._count_requests_in_window(identifier, 86400, current_time)
            
            # Check if blocked
            is_blocked = self._is_blocked(identifier)
            blocked_until = None
            block_reason = None
            
            if is_blocked:
                blocked_until = self.blocked_identifiers[identifier][0]
                block_reason = self.blocked_identifiers[identifier][1]
            
            return {
                'identifier': identifier,
                'user_role': user_role,
                'is_blocked': is_blocked,
                'blocked_until': blocked_until,
                'block_reason': block_reason,
                'abuse_score': self.abuse_scores.get(identifier, 0),
                'limits': {
                    'per_minute': {
                        'limit': config.requests_per_minute,
                        'used': requests_last_minute,
                        'remaining': max(0, config.requests_per_minute - requests_last_minute)
                    },
                    'per_hour': {
                        'limit': config.requests_per_hour,
                        'used': requests_last_hour,
                        'remaining': max(0, config.requests_per_hour - requests_last_hour)
                    },
                    'per_day': {
                        'limit': config.requests_per_day,
                        'used': requests_last_day,
                        'remaining': max(0, config.requests_per_day - requests_last_day)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {str(e)}", error=e)
            return {'error': 'Failed to get rate limit status'}
    
    # Private helper methods
    
    def _is_blocked(self, identifier: str) -> bool:
        """Check if identifier is currently blocked"""
        if identifier not in self.blocked_identifiers:
            return False
        
        blocked_until, _ = self.blocked_identifiers[identifier]
        current_time = time.time()
        
        if current_time >= blocked_until:
            # Block expired, remove it
            del self.blocked_identifiers[identifier]
            return False
        
        return True
    
    def _block_identifier(self, identifier: str, reason: str, duration_seconds: int):
        """Block an identifier for a specified duration"""
        blocked_until = time.time() + duration_seconds
        self.blocked_identifiers[identifier] = (blocked_until, reason)
        
        # Also store in DynamoDB for persistence across Lambda instances
        try:
            self.repository.put_item({
                'identifier': identifier,
                'blocked_until': blocked_until,
                'reason': reason,
                'blocked_at': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to persist block to DynamoDB: {str(e)}", error=e)
    
    def _check_burst_limit(self, identifier: str, config: RateLimitConfig) -> bool:
        """Check burst limit"""
        current_time = time.time()
        cutoff_time = current_time - config.burst_window_seconds
        
        # Count requests in burst window
        if identifier not in self.request_history:
            return True
        
        burst_requests = sum(
            1 for ts in self.request_history[identifier]
            if ts > cutoff_time
        )
        
        return burst_requests < config.burst_limit
    
    def _check_time_window_limit(self, identifier: str, limit: int, 
                                 window_seconds: int) -> bool:
        """Check time window limit"""
        current_time = time.time()
        count = self._count_requests_in_window(identifier, window_seconds, current_time)
        return count < limit
    
    def _count_requests_in_window(self, identifier: str, window_seconds: int, 
                                  current_time: float) -> int:
        """Count requests in time window"""
        if identifier not in self.request_history:
            return 0
        
        cutoff_time = current_time - window_seconds
        return sum(
            1 for ts in self.request_history[identifier]
            if ts > cutoff_time
        )
    
    def _record_request(self, identifier: str):
        """Record a request timestamp"""
        current_time = time.time()
        self.request_history[identifier].append(current_time)
        
        # Clean up old entries (keep last 24 hours)
        cutoff_time = current_time - 86400
        self.request_history[identifier] = [
            ts for ts in self.request_history[identifier]
            if ts > cutoff_time
        ]
    
    def _matches_abuse_pattern(self, identifier: str, event_type: str, 
                              pattern: AbusePattern, current_time: float) -> bool:
        """Check if event matches abuse pattern"""
        # Map event types to pattern types
        event_pattern_map = {
            'request': 'rapid_requests',
            'auth_failure': 'failed_auth_attempts',
            'invalid_request': 'invalid_requests',
            'suspicious': 'suspicious_patterns'
        }
        
        if event_pattern_map.get(event_type) != pattern.pattern_type:
            return False
        
        # Count matching events in window
        cutoff_time = current_time - pattern.window_seconds
        event_count = self._count_requests_in_window(identifier, pattern.window_seconds, current_time)
        
        return event_count >= pattern.threshold
    
    def _increase_abuse_score(self, identifier: str, points: int):
        """Increase abuse score for identifier"""
        self.abuse_scores[identifier] += points
        
        # Auto-block if abuse score too high
        if self.abuse_scores[identifier] >= 100:
            self._block_identifier(identifier, 'High abuse score', 7200)  # 2 hour block


# Global rate limiting service instance
rate_limiting_service = RateLimitingService()


# Convenience functions
def check_rate_limit(identifier: str, user_role: str = 'anonymous') -> Tuple[bool, Optional[str]]:
    """Check rate limit for identifier"""
    return rate_limiting_service.check_rate_limit(identifier, user_role)


def detect_abuse(identifier: str, event_type: str, metadata: Dict[str, Any] = None) -> Optional[str]:
    """Detect abuse patterns"""
    return rate_limiting_service.detect_abuse(identifier, event_type, metadata)


def block_identifier(identifier: str, reason: str, duration_seconds: int = 3600) -> bool:
    """Block an identifier"""
    return rate_limiting_service.block_identifier(identifier, reason, duration_seconds)


def unblock_identifier(identifier: str) -> bool:
    """Unblock an identifier"""
    return rate_limiting_service.unblock_identifier(identifier)


def get_rate_limit_status(identifier: str, user_role: str = 'anonymous') -> Dict[str, Any]:
    """Get rate limit status"""
    return rate_limiting_service.get_rate_limit_status(identifier, user_role)
