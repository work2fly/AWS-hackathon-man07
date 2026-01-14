"""
Audio Error Recovery Service for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Handles graceful degradation, fallback mechanisms, automatic recovery,
and comprehensive error logging for audio processing pipeline.

Requirements: 2.7
"""

import time
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Types of audio processing errors"""
    CONNECTION_LOST = "connection_lost"
    AUDIO_PROCESSING_FAILED = "audio_processing_failed"
    SYNTHESIS_FAILED = "synthesis_failed"
    LANGUAGE_DETECTION_FAILED = "language_detection_failed"
    BUFFER_OVERFLOW = "buffer_overflow"
    BUFFER_UNDERFLOW = "buffer_underflow"
    QUALITY_DEGRADATION = "quality_degradation"
    TIMEOUT = "timeout"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_AUDIO_FORMAT = "invalid_audio_format"
    NETWORK_ERROR = "network_error"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    DEGRADE = "degrade"
    RECONNECT = "reconnect"
    SKIP = "skip"
    TERMINATE = "terminate"


@dataclass
class ErrorEvent:
    """Represents an error event"""
    session_id: str
    error_type: ErrorType
    severity: ErrorSeverity
    timestamp: float
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_strategy: Optional[RecoveryStrategy] = None


@dataclass
class RecoveryConfig:
    """Configuration for error recovery"""
    max_retries: int = 3
    retry_delay_ms: int = 1000
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    max_retry_delay_ms: int = 10000
    enable_fallback: bool = True
    enable_degradation: bool = True
    auto_reconnect: bool = True
    reconnect_timeout_ms: int = 30000
    error_threshold: int = 10  # Max errors before circuit breaker
    circuit_breaker_timeout_ms: int = 60000


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for service protection"""
    session_id: str
    is_open: bool = False
    error_count: int = 0
    last_error_time: float = 0.0
    opened_at: float = 0.0
    half_open_attempts: int = 0
    
    def record_error(self):
        """Record an error"""
        self.error_count += 1
        self.last_error_time = time.time()
    
    def record_success(self):
        """Record a success"""
        self.error_count = max(0, self.error_count - 1)
    
    def open_circuit(self):
        """Open the circuit breaker"""
        self.is_open = True
        self.opened_at = time.time()
        logger.warning(f"Circuit breaker opened for session {self.session_id}")
    
    def close_circuit(self):
        """Close the circuit breaker"""
        self.is_open = False
        self.error_count = 0
        self.half_open_attempts = 0
        logger.info(f"Circuit breaker closed for session {self.session_id}")
    
    def should_attempt_recovery(self, timeout_ms: int) -> bool:
        """Check if recovery should be attempted"""
        if not self.is_open:
            return True
        
        # Check if timeout has passed
        elapsed_ms = (time.time() - self.opened_at) * 1000
        return elapsed_ms >= timeout_ms


@dataclass
class ErrorStatistics:
    """Statistics for error tracking"""
    session_id: str
    total_errors: int = 0
    errors_by_type: Dict[ErrorType, int] = field(default_factory=dict)
    errors_by_severity: Dict[ErrorSeverity, int] = field(default_factory=dict)
    successful_recoveries: int = 0
    failed_recoveries: int = 0
    average_recovery_time_ms: float = 0.0
    last_error_time: float = 0.0
    
    def record_error(self, error: ErrorEvent):
        """Record an error"""
        self.total_errors += 1
        
        # Update type distribution
        if error.error_type not in self.errors_by_type:
            self.errors_by_type[error.error_type] = 0
        self.errors_by_type[error.error_type] += 1
        
        # Update severity distribution
        if error.severity not in self.errors_by_severity:
            self.errors_by_severity[error.severity] = 0
        self.errors_by_severity[error.severity] += 1
        
        self.last_error_time = error.timestamp
    
    def record_recovery(self, success: bool, recovery_time_ms: float):
        """Record a recovery attempt"""
        if success:
            self.successful_recoveries += 1
        else:
            self.failed_recoveries += 1
        
        # Update average recovery time
        total_recoveries = self.successful_recoveries + self.failed_recoveries
        if total_recoveries > 0:
            alpha = 0.1
            self.average_recovery_time_ms = (
                alpha * recovery_time_ms +
                (1 - alpha) * self.average_recovery_time_ms
            )


class AudioErrorRecoveryService:
    """
    Service for audio error handling and recovery
    
    Provides graceful degradation, fallback mechanisms, automatic recovery,
    and comprehensive error logging.
    """
    
    # Error type to recovery strategy mapping
    ERROR_RECOVERY_STRATEGIES = {
        ErrorType.CONNECTION_LOST: RecoveryStrategy.RECONNECT,
        ErrorType.AUDIO_PROCESSING_FAILED: RecoveryStrategy.RETRY,
        ErrorType.SYNTHESIS_FAILED: RecoveryStrategy.FALLBACK,
        ErrorType.LANGUAGE_DETECTION_FAILED: RecoveryStrategy.FALLBACK,
        ErrorType.BUFFER_OVERFLOW: RecoveryStrategy.DEGRADE,
        ErrorType.BUFFER_UNDERFLOW: RecoveryStrategy.SKIP,
        ErrorType.QUALITY_DEGRADATION: RecoveryStrategy.DEGRADE,
        ErrorType.TIMEOUT: RecoveryStrategy.RETRY,
        ErrorType.SERVICE_UNAVAILABLE: RecoveryStrategy.FALLBACK,
        ErrorType.RATE_LIMIT_EXCEEDED: RecoveryStrategy.DEGRADE,
        ErrorType.INVALID_AUDIO_FORMAT: RecoveryStrategy.FALLBACK,
        ErrorType.NETWORK_ERROR: RecoveryStrategy.RECONNECT,
    }
    
    # Error type to severity mapping
    ERROR_SEVERITIES = {
        ErrorType.CONNECTION_LOST: ErrorSeverity.HIGH,
        ErrorType.AUDIO_PROCESSING_FAILED: ErrorSeverity.MEDIUM,
        ErrorType.SYNTHESIS_FAILED: ErrorSeverity.MEDIUM,
        ErrorType.LANGUAGE_DETECTION_FAILED: ErrorSeverity.LOW,
        ErrorType.BUFFER_OVERFLOW: ErrorSeverity.MEDIUM,
        ErrorType.BUFFER_UNDERFLOW: ErrorSeverity.LOW,
        ErrorType.QUALITY_DEGRADATION: ErrorSeverity.LOW,
        ErrorType.TIMEOUT: ErrorSeverity.MEDIUM,
        ErrorType.SERVICE_UNAVAILABLE: ErrorSeverity.CRITICAL,
        ErrorType.RATE_LIMIT_EXCEEDED: ErrorSeverity.MEDIUM,
        ErrorType.INVALID_AUDIO_FORMAT: ErrorSeverity.MEDIUM,
        ErrorType.NETWORK_ERROR: ErrorSeverity.HIGH,
    }
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        """Initialize error recovery service"""
        self.config = config or RecoveryConfig()
        self._error_history: Dict[str, deque] = {}
        self._circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self._statistics: Dict[str, ErrorStatistics] = {}
        self._recovery_handlers: Dict[RecoveryStrategy, Callable] = {}
        self._register_default_handlers()
        logger.info("Audio Error Recovery Service initialized")
    
    def handle_error(
        self,
        session_id: str,
        error_type: ErrorType,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> bool:
        """
        Handle an error and attempt recovery
        
        Args:
            session_id: Session identifier
            error_type: Type of error
            message: Error message
            context: Optional error context
            stack_trace: Optional stack trace
            
        Returns:
            True if recovery successful, False otherwise
        """
        # Create error event
        severity = self.ERROR_SEVERITIES.get(error_type, ErrorSeverity.MEDIUM)
        error = ErrorEvent(
            session_id=session_id,
            error_type=error_type,
            severity=severity,
            timestamp=time.time(),
            message=message,
            context=context or {},
            stack_trace=stack_trace
        )
        
        # Log error
        self._log_error(error)
        
        # Record in history
        self._record_error(error)
        
        # Check circuit breaker
        if not self._check_circuit_breaker(session_id):
            logger.warning(
                f"Circuit breaker open for session {session_id}, "
                "skipping recovery attempt"
            )
            return False
        
        # Attempt recovery
        recovery_strategy = self.ERROR_RECOVERY_STRATEGIES.get(
            error_type,
            RecoveryStrategy.RETRY
        )
        
        success = self._attempt_recovery(error, recovery_strategy)
        
        # Update error event
        error.recovery_attempted = True
        error.recovery_successful = success
        error.recovery_strategy = recovery_strategy
        
        # Update circuit breaker
        if success:
            self._record_success(session_id)
        else:
            self._record_failure(session_id)
        
        return success
    
    def retry_with_backoff(
        self,
        session_id: str,
        operation: Callable,
        *args,
        **kwargs
    ) -> Tuple[bool, Any]:
        """
        Retry an operation with exponential backoff
        
        Args:
            session_id: Session identifier
            operation: Operation to retry
            *args: Operation arguments
            **kwargs: Operation keyword arguments
            
        Returns:
            Tuple of (success, result)
        """
        delay_ms = self.config.retry_delay_ms
        
        for attempt in range(self.config.max_retries):
            try:
                result = operation(*args, **kwargs)
                logger.info(
                    f"Operation succeeded for session {session_id} "
                    f"on attempt {attempt + 1}"
                )
                return True, result
            except Exception as e:
                logger.warning(
                    f"Operation failed for session {session_id} "
                    f"on attempt {attempt + 1}/{self.config.max_retries}: {e}"
                )
                
                if attempt < self.config.max_retries - 1:
                    # Wait before retry
                    time.sleep(delay_ms / 1000.0)
                    
                    # Apply exponential backoff
                    if self.config.exponential_backoff:
                        delay_ms = min(
                            delay_ms * self.config.backoff_multiplier,
                            self.config.max_retry_delay_ms
                        )
        
        return False, None
    
    def degrade_gracefully(
        self,
        session_id: str,
        degradation_level: int = 1
    ) -> Dict[str, Any]:
        """
        Apply graceful degradation
        
        Args:
            session_id: Session identifier
            degradation_level: Level of degradation (1-3)
            
        Returns:
            Degradation configuration
        """
        degradation_configs = {
            1: {
                'audio_quality': 'medium',
                'sample_rate': 16000,
                'buffer_size': 3,
                'enable_features': ['basic_processing']
            },
            2: {
                'audio_quality': 'low',
                'sample_rate': 8000,
                'buffer_size': 2,
                'enable_features': ['basic_processing']
            },
            3: {
                'audio_quality': 'minimal',
                'sample_rate': 8000,
                'buffer_size': 1,
                'enable_features': []
            }
        }
        
        config = degradation_configs.get(degradation_level, degradation_configs[1])
        
        logger.info(
            f"Applied graceful degradation level {degradation_level} "
            f"for session {session_id}"
        )
        
        return config
    
    def attempt_reconnection(
        self,
        session_id: str,
        reconnect_callback: Callable
    ) -> bool:
        """
        Attempt to reconnect
        
        Args:
            session_id: Session identifier
            reconnect_callback: Callback function for reconnection
            
        Returns:
            True if reconnection successful
        """
        if not self.config.auto_reconnect:
            return False
        
        logger.info(f"Attempting reconnection for session {session_id}")
        
        start_time = time.time()
        timeout_s = self.config.reconnect_timeout_ms / 1000.0
        
        while (time.time() - start_time) < timeout_s:
            try:
                reconnect_callback()
                logger.info(f"Reconnection successful for session {session_id}")
                return True
            except Exception as e:
                logger.debug(f"Reconnection attempt failed: {e}")
                time.sleep(1.0)  # Wait 1 second between attempts
        
        logger.error(
            f"Reconnection failed for session {session_id} "
            f"after {timeout_s}s timeout"
        )
        return False
    
    def get_error_statistics(
        self,
        session_id: str
    ) -> Optional[ErrorStatistics]:
        """
        Get error statistics for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            ErrorStatistics or None
        """
        return self._statistics.get(session_id)
    
    def get_error_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ErrorEvent]:
        """
        Get error history for session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of errors to return
            
        Returns:
            List of ErrorEvent objects
        """
        if session_id not in self._error_history:
            return []
        
        history = list(self._error_history[session_id])
        return history[-limit:]
    
    def reset_circuit_breaker(self, session_id: str):
        """
        Manually reset circuit breaker
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._circuit_breakers:
            self._circuit_breakers[session_id].close_circuit()
            logger.info(f"Circuit breaker manually reset for session {session_id}")
    
    def _register_default_handlers(self):
        """Register default recovery handlers"""
        self._recovery_handlers[RecoveryStrategy.RETRY] = self._handle_retry
        self._recovery_handlers[RecoveryStrategy.FALLBACK] = self._handle_fallback
        self._recovery_handlers[RecoveryStrategy.DEGRADE] = self._handle_degrade
        self._recovery_handlers[RecoveryStrategy.RECONNECT] = self._handle_reconnect
        self._recovery_handlers[RecoveryStrategy.SKIP] = self._handle_skip
        self._recovery_handlers[RecoveryStrategy.TERMINATE] = self._handle_terminate
    
    def _attempt_recovery(
        self,
        error: ErrorEvent,
        strategy: RecoveryStrategy
    ) -> bool:
        """Attempt recovery using specified strategy"""
        start_time = time.time()
        
        handler = self._recovery_handlers.get(strategy)
        if not handler:
            logger.error(f"No handler for recovery strategy: {strategy.value}")
            return False
        
        try:
            success = handler(error)
            recovery_time_ms = (time.time() - start_time) * 1000
            
            # Record recovery attempt
            if error.session_id in self._statistics:
                self._statistics[error.session_id].record_recovery(
                    success, recovery_time_ms
                )
            
            return success
        except Exception as e:
            logger.error(f"Recovery handler failed: {e}")
            return False
    
    def _handle_retry(self, error: ErrorEvent) -> bool:
        """Handle retry recovery strategy"""
        logger.info(f"Applying retry strategy for {error.error_type.value}")
        # Placeholder - actual retry logic would be implemented here
        return True
    
    def _handle_fallback(self, error: ErrorEvent) -> bool:
        """Handle fallback recovery strategy"""
        logger.info(f"Applying fallback strategy for {error.error_type.value}")
        # Placeholder - actual fallback logic would be implemented here
        return True
    
    def _handle_degrade(self, error: ErrorEvent) -> bool:
        """Handle degradation recovery strategy"""
        logger.info(f"Applying degradation strategy for {error.error_type.value}")
        self.degrade_gracefully(error.session_id)
        return True
    
    def _handle_reconnect(self, error: ErrorEvent) -> bool:
        """Handle reconnection recovery strategy"""
        logger.info(f"Applying reconnection strategy for {error.error_type.value}")
        # Placeholder - actual reconnection logic would be implemented here
        return True
    
    def _handle_skip(self, error: ErrorEvent) -> bool:
        """Handle skip recovery strategy"""
        logger.info(f"Applying skip strategy for {error.error_type.value}")
        return True
    
    def _handle_terminate(self, error: ErrorEvent) -> bool:
        """Handle termination recovery strategy"""
        logger.error(f"Terminating session {error.session_id} due to {error.error_type.value}")
        return False
    
    def _log_error(self, error: ErrorEvent):
        """Log error with appropriate level"""
        log_message = (
            f"Error in session {error.session_id}: "
            f"{error.error_type.value} - {error.message}"
        )
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _record_error(self, error: ErrorEvent):
        """Record error in history and statistics"""
        # Initialize history if needed
        if error.session_id not in self._error_history:
            self._error_history[error.session_id] = deque(maxlen=100)
        
        # Add to history
        self._error_history[error.session_id].append(error)
        
        # Initialize statistics if needed
        if error.session_id not in self._statistics:
            self._statistics[error.session_id] = ErrorStatistics(
                session_id=error.session_id
            )
        
        # Update statistics
        self._statistics[error.session_id].record_error(error)
    
    def _check_circuit_breaker(self, session_id: str) -> bool:
        """Check if circuit breaker allows operation"""
        if session_id not in self._circuit_breakers:
            self._circuit_breakers[session_id] = CircuitBreakerState(
                session_id=session_id
            )
        
        breaker = self._circuit_breakers[session_id]
        
        # Check if circuit is open
        if breaker.is_open:
            # Check if timeout has passed
            if breaker.should_attempt_recovery(self.config.circuit_breaker_timeout_ms):
                logger.info(f"Circuit breaker timeout passed for session {session_id}, attempting recovery")
                return True
            return False
        
        # Check if error threshold exceeded
        if breaker.error_count >= self.config.error_threshold:
            breaker.open_circuit()
            return False
        
        return True
    
    def _record_success(self, session_id: str):
        """Record successful operation"""
        if session_id in self._circuit_breakers:
            breaker = self._circuit_breakers[session_id]
            breaker.record_success()
            
            # Close circuit if it was open
            if breaker.is_open and breaker.error_count == 0:
                breaker.close_circuit()
    
    def _record_failure(self, session_id: str):
        """Record failed operation"""
        if session_id in self._circuit_breakers:
            self._circuit_breakers[session_id].record_error()
    
    def cleanup_session(self, session_id: str):
        """
        Cleanup session data
        
        Args:
            session_id: Session identifier
        """
        self._error_history.pop(session_id, None)
        self._circuit_breakers.pop(session_id, None)
        self._statistics.pop(session_id, None)
        logger.info(f"Cleaned up error recovery data for session {session_id}")


# Global service instance
audio_error_recovery_service = AudioErrorRecoveryService()
