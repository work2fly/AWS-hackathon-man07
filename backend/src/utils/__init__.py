"""
Utility functions for AI Therapy Platform
"""

# Use lazy imports to avoid circular import issues during testing
try:
    from .logger import get_logger
except ImportError:
    get_logger = None

try:
    from .validation import validate_email, validate_password
except ImportError:
    validate_email = None
    validate_password = None

try:
    from .metrics import MetricsCollector
except ImportError:
    MetricsCollector = None

try:
    from .alerts import AlertManager
except ImportError:
    AlertManager = None

try:
    from .response_formatter import get_cors_headers, success_response, error_response
except ImportError:
    get_cors_headers = None
    success_response = None
    error_response = None

__all__ = [
    'get_logger',
    'validate_email',
    'validate_password',
    'MetricsCollector',
    'AlertManager',
    'get_cors_headers',
    'success_response',
    'error_response'
]