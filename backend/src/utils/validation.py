"""
Data validation and sanitization utilities
🏆 Breaking Barriers UK 2026 compliant
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom validation error"""
    pass


class DataValidator:
    """Data validation and sanitization utilities"""
    
    # Regex patterns
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{10,20}$')
    USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]{1,50}$')
    SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]{1,100}$')
    LANGUAGE_CODE_PATTERN = re.compile(r'^[a-z]{2}(-[A-Z]{2})?$')
    
    # Dangerous patterns to sanitize
    SCRIPT_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    SQL_INJECTION_PATTERNS = [
        re.compile(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)', re.IGNORECASE),
        re.compile(r'(\b(OR|AND)\s+\d+\s*=\s*\d+)', re.IGNORECASE),
        re.compile(r'[\'";]', re.IGNORECASE)
    ]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        return bool(DataValidator.PHONE_PATTERN.match(phone.strip()))
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format"""
        if not user_id:
            return False
        return bool(DataValidator.USER_ID_PATTERN.match(user_id))
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format"""
        if not session_id:
            return False
        return bool(DataValidator.SESSION_ID_PATTERN.match(session_id))
    
    @staticmethod
    def validate_language_code(language: str) -> bool:
        """Validate language code (ISO 639-1 format)"""
        if not language:
            return False
        return bool(DataValidator.LANGUAGE_CODE_PATTERN.match(language))
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string length"""
        if not isinstance(value, str):
            return False
        return min_length <= len(value.strip()) <= max_length
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: Union[int, float], 
                              max_val: Union[int, float]) -> bool:
        """Validate numeric value is within range"""
        if not isinstance(value, (int, float)):
            return False
        return min_val <= value <= max_val
    
    @staticmethod
    def validate_datetime(value: Any) -> bool:
        """Validate datetime object or ISO string"""
        if isinstance(value, datetime):
            return True
        
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return True
            except ValueError:
                return False
        
        return False
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None, 
                       allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return ""
        
        # Remove null bytes
        sanitized = value.replace('\x00', '')
        
        # Remove or escape HTML
        if not allow_html:
            # Remove script tags
            sanitized = DataValidator.SCRIPT_PATTERN.sub('', sanitized)
            # Remove HTML tags
            sanitized = DataValidator.HTML_TAG_PATTERN.sub('', sanitized)
            # Escape remaining HTML entities
            sanitized = html.escape(sanitized)
        
        # Check for SQL injection patterns
        for pattern in DataValidator.SQL_INJECTION_PATTERNS:
            if pattern.search(sanitized):
                logger.warning(f"Potential SQL injection attempt detected: {sanitized[:100]}")
                # Replace suspicious patterns with safe alternatives
                sanitized = pattern.sub('', sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Truncate if max_length specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def sanitize_phone_number(phone: str) -> str:
        """Sanitize phone number"""
        if not phone:
            return ""
        
        # Remove all non-digit characters except + at the beginning
        sanitized = re.sub(r'[^\d+]', '', phone)
        
        # Ensure + is only at the beginning
        if '+' in sanitized:
            parts = sanitized.split('+')
            sanitized = '+' + ''.join(parts[1:])
        
        return sanitized
    
    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate user data and return errors"""
        errors = {}
        
        # Validate required fields
        required_fields = ['user_id', 'email', 'role']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Validate user_id
        if 'user_id' in user_data and user_data['user_id']:
            if not DataValidator.validate_user_id(user_data['user_id']):
                errors.setdefault('user_id', []).append("Invalid user ID format")
        
        # Validate email
        if 'email' in user_data and user_data['email']:
            if not DataValidator.validate_email(user_data['email']):
                errors.setdefault('email', []).append("Invalid email format")
        
        # Validate role
        if 'role' in user_data and user_data['role']:
            valid_roles = ['client', 'therapist', 'admin']
            if user_data['role'] not in valid_roles:
                errors.setdefault('role', []).append(f"Role must be one of: {', '.join(valid_roles)}")
        
        # Validate profile if present
        if 'profile' in user_data and isinstance(user_data['profile'], dict):
            profile = user_data['profile']
            
            # Validate names
            for name_field in ['first_name', 'last_name']:
                if name_field in profile and profile[name_field]:
                    if not DataValidator.validate_string_length(profile[name_field], 1, 50):
                        errors.setdefault(f'profile.{name_field}', []).append(f"{name_field} must be 1-50 characters")
            
            # Validate phone number
            if 'phone_number' in profile and profile['phone_number']:
                if not DataValidator.validate_phone_number(profile['phone_number']):
                    errors.setdefault('profile.phone_number', []).append("Invalid phone number format")
        
        # Validate language preference
        if 'language_preference' in user_data and user_data['language_preference']:
            if not DataValidator.validate_language_code(user_data['language_preference']):
                errors.setdefault('language_preference', []).append("Invalid language code format")
        
        return errors
    
    @staticmethod
    def validate_session_data(session_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate session data and return errors"""
        errors = {}
        
        # Validate required fields
        required_fields = ['session_id', 'client_id', 'agent_id', 'agent_memory_id']
        for field in required_fields:
            if field not in session_data or not session_data[field]:
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Validate session_id
        if 'session_id' in session_data and session_data['session_id']:
            if not DataValidator.validate_session_id(session_data['session_id']):
                errors.setdefault('session_id', []).append("Invalid session ID format")
        
        # Validate client_id
        if 'client_id' in session_data and session_data['client_id']:
            if not DataValidator.validate_user_id(session_data['client_id']):
                errors.setdefault('client_id', []).append("Invalid client ID format")
        
        # Validate agent_id
        if 'agent_id' in session_data and session_data['agent_id']:
            if not DataValidator.validate_string_length(session_data['agent_id'], 1, 100):
                errors.setdefault('agent_id', []).append("Agent ID must be 1-100 characters")
        
        # Validate status
        if 'status' in session_data and session_data['status']:
            valid_statuses = ['active', 'completed', 'terminated']
            if session_data['status'] not in valid_statuses:
                errors.setdefault('status', []).append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Validate language
        if 'language' in session_data and session_data['language']:
            if not DataValidator.validate_language_code(session_data['language']):
                errors.setdefault('language', []).append("Invalid language code format")
        
        # Validate timestamps
        for timestamp_field in ['start_time', 'end_time', 'timestamp']:
            if timestamp_field in session_data and session_data[timestamp_field]:
                if not DataValidator.validate_datetime(session_data[timestamp_field]):
                    errors.setdefault(timestamp_field, []).append(f"Invalid {timestamp_field} format")
        
        # Validate duration
        if 'duration' in session_data and session_data['duration'] is not None:
            if not isinstance(session_data['duration'], int) or session_data['duration'] < 0:
                errors.setdefault('duration', []).append("Duration must be a non-negative integer")
        
        return errors
    
    @staticmethod
    def validate_red_flag_data(red_flag_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate red flag data and return errors"""
        errors = {}
        
        # Validate required fields
        required_fields = ['session_id', 'flag_id', 'type', 'severity', 'context']
        for field in required_fields:
            if field not in red_flag_data or not red_flag_data[field]:
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Validate session_id
        if 'session_id' in red_flag_data and red_flag_data['session_id']:
            if not DataValidator.validate_session_id(red_flag_data['session_id']):
                errors.setdefault('session_id', []).append("Invalid session ID format")
        
        # Validate flag_id
        if 'flag_id' in red_flag_data and red_flag_data['flag_id']:
            if not DataValidator.validate_string_length(red_flag_data['flag_id'], 1, 100):
                errors.setdefault('flag_id', []).append("Flag ID must be 1-100 characters")
        
        # Validate type
        if 'type' in red_flag_data and red_flag_data['type']:
            valid_types = ['self_harm', 'suicidal_ideation', 'abuse', 'violence', 'crisis']
            if red_flag_data['type'] not in valid_types:
                errors.setdefault('type', []).append(f"Type must be one of: {', '.join(valid_types)}")
        
        # Validate severity
        if 'severity' in red_flag_data and red_flag_data['severity']:
            valid_severities = ['low', 'medium', 'high', 'critical']
            if red_flag_data['severity'] not in valid_severities:
                errors.setdefault('severity', []).append(f"Severity must be one of: {', '.join(valid_severities)}")
        
        # Validate context
        if 'context' in red_flag_data and red_flag_data['context']:
            if not DataValidator.validate_string_length(red_flag_data['context'], 1, 1000):
                errors.setdefault('context', []).append("Context must be 1-1000 characters")
        
        # Validate detected_at
        if 'detected_at' in red_flag_data and red_flag_data['detected_at']:
            if not DataValidator.validate_datetime(red_flag_data['detected_at']):
                errors.setdefault('detected_at', []).append("Invalid detected_at format")
        
        return errors
    
    @staticmethod
    def validate_notification_data(notification_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate notification data and return errors"""
        errors = {}
        
        # Validate required fields
        required_fields = ['recipient_id', 'type', 'priority', 'title', 'message']
        for field in required_fields:
            if field not in notification_data or not notification_data[field]:
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Validate recipient_id
        if 'recipient_id' in notification_data and notification_data['recipient_id']:
            if not DataValidator.validate_user_id(notification_data['recipient_id']):
                errors.setdefault('recipient_id', []).append("Invalid recipient ID format")
        
        # Validate type
        if 'type' in notification_data and notification_data['type']:
            valid_types = ['red_flag', 'session_complete', 'system_alert']
            if notification_data['type'] not in valid_types:
                errors.setdefault('type', []).append(f"Type must be one of: {', '.join(valid_types)}")
        
        # Validate priority
        if 'priority' in notification_data and notification_data['priority']:
            valid_priorities = ['low', 'medium', 'high', 'urgent']
            if notification_data['priority'] not in valid_priorities:
                errors.setdefault('priority', []).append(f"Priority must be one of: {', '.join(valid_priorities)}")
        
        # Validate title
        if 'title' in notification_data and notification_data['title']:
            if not DataValidator.validate_string_length(notification_data['title'], 1, 200):
                errors.setdefault('title', []).append("Title must be 1-200 characters")
        
        # Validate message
        if 'message' in notification_data and notification_data['message']:
            if not DataValidator.validate_string_length(notification_data['message'], 1, 1000):
                errors.setdefault('message', []).append("Message must be 1-1000 characters")
        
        # Validate optional session/flag IDs
        for id_field in ['related_session_id', 'related_flag_id']:
            if id_field in notification_data and notification_data[id_field]:
                if not DataValidator.validate_string_length(notification_data[id_field], 1, 100):
                    errors.setdefault(id_field, []).append(f"{id_field} must be 1-100 characters")
        
        return errors
    
    @staticmethod
    def sanitize_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize user input data"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Sanitize string values
                if key in ['email']:
                    # Don't sanitize email addresses (just validate them)
                    sanitized[key] = value.strip().lower()
                elif key in ['phone_number']:
                    sanitized[key] = DataValidator.sanitize_phone_number(value)
                else:
                    # General string sanitization
                    max_length = 1000
                    if key in ['first_name', 'last_name']:
                        max_length = 50
                    elif key in ['title']:
                        max_length = 200
                    elif key in ['context', 'message']:
                        max_length = 1000
                    
                    sanitized[key] = DataValidator.sanitize_string(value, max_length)
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = DataValidator.sanitize_user_input(value)
            elif isinstance(value, list):
                # Sanitize list items
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_list.append(DataValidator.sanitize_string(item, 100))
                    elif isinstance(item, dict):
                        sanitized_list.append(DataValidator.sanitize_user_input(item))
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
            else:
                # Keep other types as-is
                sanitized[key] = value
        
        return sanitized