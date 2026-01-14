"""
Service layer for AI Therapy Platform
"""

# Use lazy imports to avoid circular import issues during testing
try:
    from .user_service import UserService
except ImportError:
    UserService = None

try:
    from .session_service import SessionService
except ImportError:
    SessionService = None

try:
    from .notification_service import NotificationService
except ImportError:
    NotificationService = None

try:
    from .red_flag_detection_service import RedFlagDetectionService
except ImportError:
    RedFlagDetectionService = None

try:
    from .red_flag_management_service import RedFlagManagementService
except ImportError:
    RedFlagManagementService = None

try:
    from .sentiment_analysis_service import SentimentAnalysisService
except ImportError:
    SentimentAnalysisService = None

try:
    from .therapist_reporting_service import TherapistReportingService
except ImportError:
    TherapistReportingService = None

try:
    from .analytics_service import AnalyticsService
except ImportError:
    AnalyticsService = None

__all__ = [
    'UserService',
    'SessionService',
    'NotificationService',
    'RedFlagDetectionService',
    'RedFlagManagementService',
    'SentimentAnalysisService',
    'TherapistReportingService',
    'AnalyticsService'
]