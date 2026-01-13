"""
AI Therapy Platform - Centralized Logging Utility
Breaking Barriers UK 2026 compliant logging configuration
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import traceback

# Configure logging level from environment
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'ai-therapy-platform')

class StructuredLogger:
    """
    Structured logger for AWS CloudWatch compatibility
    Outputs JSON formatted logs for better parsing and monitoring
    """
    
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # Custom JSON formatter
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.propagate = False
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method with structured data"""
        extra_data = {
            'service': SERVICE_NAME,
            'environment': ENVIRONMENT,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # Add request context if available (for Lambda)
        if hasattr(self, '_request_context'):
            extra_data.update(self._request_context)
        
        getattr(self.logger, level.lower())(message, extra=extra_data)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception details"""
        if error:
            kwargs.update({
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc()
            })
        self._log('ERROR', message, **kwargs)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception details"""
        if error:
            kwargs.update({
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc()
            })
        self._log('CRITICAL', message, **kwargs)
    
    def set_request_context(self, context: Dict[str, Any]):
        """Set request context for all subsequent logs"""
        self._request_context = context
    
    def clear_request_context(self):
        """Clear request context"""
        if hasattr(self, '_request_context'):
            delattr(self, '_request_context')

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields from the record
        if hasattr(record, 'service'):
            log_entry['service'] = record.service
        if hasattr(record, 'environment'):
            log_entry['environment'] = record.environment
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
        if hasattr(record, 'error_message'):
            log_entry['error_message'] = record.error_message
        if hasattr(record, 'traceback'):
            log_entry['traceback'] = record.traceback
        
        # Add any additional fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'message', 'exc_info', 'exc_text', 
                          'stack_info', 'service', 'environment', 'timestamp',
                          'request_id', 'user_id', 'session_id', 'error_type', 
                          'error_message', 'traceback']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

# Global logger instance
logger = StructuredLogger(__name__)

# Convenience functions for common logging patterns
def log_api_request(method: str, path: str, user_id: Optional[str] = None, **kwargs):
    """Log API request with standard fields"""
    logger.info(
        f"API Request: {method} {path}",
        method=method,
        path=path,
        user_id=user_id,
        **kwargs
    )

def log_api_response(method: str, path: str, status_code: int, 
                    duration_ms: float, user_id: Optional[str] = None, **kwargs):
    """Log API response with standard fields"""
    logger.info(
        f"API Response: {method} {path} - {status_code}",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        user_id=user_id,
        **kwargs
    )

def log_database_operation(operation: str, table: str, success: bool, 
                          duration_ms: float, **kwargs):
    """Log database operation with standard fields"""
    level = 'info' if success else 'error'
    getattr(logger, level)(
        f"Database {operation}: {table} - {'Success' if success else 'Failed'}",
        operation=operation,
        table=table,
        success=success,
        duration_ms=duration_ms,
        **kwargs
    )

def log_security_event(event_type: str, user_id: Optional[str] = None, 
                      severity: str = 'medium', **kwargs):
    """Log security event with standard fields"""
    logger.warning(
        f"Security Event: {event_type}",
        event_type=event_type,
        user_id=user_id,
        severity=severity,
        security_event=True,
        **kwargs
    )

def log_red_flag_detection(session_id: str, flag_type: str, severity: str, 
                          user_id: Optional[str] = None, **kwargs):
    """Log red flag detection with standard fields"""
    logger.critical(
        f"Red Flag Detected: {flag_type} - {severity}",
        session_id=session_id,
        flag_type=flag_type,
        severity=severity,
        user_id=user_id,
        red_flag_event=True,
        **kwargs
    )

def log_bedrock_request(model_id: str, success: bool, duration_ms: float, 
                       tokens_used: Optional[int] = None, **kwargs):
    """Log Bedrock API request with standard fields"""
    level = 'info' if success else 'error'
    getattr(logger, level)(
        f"Bedrock Request: {model_id} - {'Success' if success else 'Failed'}",
        model_id=model_id,
        success=success,
        duration_ms=duration_ms,
        tokens_used=tokens_used,
        bedrock_request=True,
        **kwargs
    )

# Lambda context decorator
def with_lambda_context(func):
    """Decorator to add Lambda context to all logs within a function"""
    def wrapper(event, context):
        # Set Lambda context
        logger.set_request_context({
            'request_id': context.aws_request_id,
            'function_name': context.function_name,
            'function_version': context.function_version,
            'remaining_time_ms': context.get_remaining_time_in_millis()
        })
        
        try:
            result = func(event, context)
            return result
        finally:
            # Clear context after function execution
            logger.clear_request_context()
    
    return wrapper