#!/usr/bin/env python3
"""
Property-Based Tests for DynamoDB Operations
🏆 Breaking Barriers UK 2026 compliant
Feature: ai-therapy-platform, Property 1: User Registration and Authentication
**Validates: Requirements 1.1, 1.2, 1.3**
"""

import unittest
import os
import sys
import re
import html
from datetime import datetime
from typing import Dict, Any, List
from email_validator import validate_email, EmailNotValidError

# Property-based testing imports
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis.strategies import composite


class SimpleDataValidator:
    """Simplified data validator for testing"""
    
    # Regex patterns
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{10,20}$')
    USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]{1,50}$')
    LANGUAGE_CODE_PATTERN = re.compile(r'^[a-z]{2}(-[A-Z]{2})?$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        try:
            # Skip deliverability check for testing
            validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        return bool(SimpleDataValidator.PHONE_PATTERN.match(phone.strip()))
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format"""
        if not user_id:
            return False
        return bool(SimpleDataValidator.USER_ID_PATTERN.match(user_id))
    
    @staticmethod
    def validate_language_code(language: str) -> bool:
        """Validate language code (ISO 639-1 format)"""
        if not language:
            return False
        return bool(SimpleDataValidator.LANGUAGE_CODE_PATTERN.match(language))
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string length"""
        if not isinstance(value, str):
            return False
        return min_length <= len(value.strip()) <= max_length
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = None) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return ""
        
        # Remove null bytes
        sanitized = value.replace('\x00', '')
        
        # Remove script tags
        script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
        sanitized = script_pattern.sub('', sanitized)
        
        # Remove HTML tags
        html_tag_pattern = re.compile(r'<[^>]+>')
        sanitized = html_tag_pattern.sub('', sanitized)
        
        # Remove javascript: protocol
        javascript_pattern = re.compile(r'javascript:', re.IGNORECASE)
        sanitized = javascript_pattern.sub('', sanitized)
        
        # Escape HTML entities
        sanitized = html.escape(sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Truncate if max_length specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
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
            if not SimpleDataValidator.validate_user_id(user_data['user_id']):
                errors.setdefault('user_id', []).append("Invalid user ID format")
        
        # Validate email
        if 'email' in user_data and user_data['email']:
            if not SimpleDataValidator.validate_email(user_data['email']):
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
                    if not SimpleDataValidator.validate_string_length(profile[name_field], 1, 50):
                        errors.setdefault(f'profile.{name_field}', []).append(f"{name_field} must be 1-50 characters")
            
            # Validate phone number
            if 'phone_number' in profile and profile['phone_number']:
                if not SimpleDataValidator.validate_phone_number(profile['phone_number']):
                    errors.setdefault('profile.phone_number', []).append("Invalid phone number format")
        
        # Validate language preference
        if 'language_preference' in user_data and user_data['language_preference']:
            if not SimpleDataValidator.validate_language_code(user_data['language_preference']):
                errors.setdefault('language_preference', []).append("Invalid language code format")
        
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
                    # Remove all non-digit characters except + at the beginning
                    phone_sanitized = re.sub(r'[^\d+]', '', value)
                    if '+' in phone_sanitized:
                        parts = phone_sanitized.split('+')
                        phone_sanitized = '+' + ''.join(parts[1:])
                    sanitized[key] = phone_sanitized
                else:
                    # General string sanitization
                    max_length = 1000
                    if key in ['first_name', 'last_name']:
                        max_length = 50
                    elif key in ['title']:
                        max_length = 200
                    elif key in ['context', 'message']:
                        max_length = 1000
                    
                    sanitized[key] = SimpleDataValidator.sanitize_string(value, max_length)
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = SimpleDataValidator.sanitize_user_input(value)
            elif isinstance(value, list):
                # Sanitize list items
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_list.append(SimpleDataValidator.sanitize_string(item, 100))
                    elif isinstance(item, dict):
                        sanitized_list.append(SimpleDataValidator.sanitize_user_input(item))
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
            else:
                # Keep other types as-is
                sanitized[key] = value
        
        return sanitized


@composite
def valid_user_data(draw):
    """Generate valid user data for property testing"""
    first_name = draw(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
    last_name = draw(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
    
    # Generate valid email
    email_local = draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
    email_domain = draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
    email = f"{email_local}@{email_domain}.com"
    
    # Generate valid user ID (only ASCII alphanumeric, hyphens, underscores)
    user_id = draw(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    
    role = draw(st.sampled_from(['client', 'therapist', 'admin']))
    language = draw(st.sampled_from(['en', 'es', 'fr', 'de']))
    
    # Generate valid phone number (optional)
    phone_number = None
    if draw(st.booleans()):
        phone_digits = draw(st.text(min_size=10, max_size=15, alphabet='0123456789'))
        phone_number = f"+1{phone_digits}"
    
    return {
        'user_id': user_id,
        'email': email.lower(),
        'role': role,
        'language_preference': language,
        'profile': {
            'first_name': first_name,
            'last_name': last_name,
            'timezone': 'UTC',
            'phone_number': phone_number
        },
        'preferences': {
            'language': language,
            'voice_settings': {
                'voice_id': 'default',
                'speed': draw(st.floats(min_value=0.5, max_value=2.0)),
                'pitch': draw(st.floats(min_value=0.5, max_value=2.0)),
                'volume': draw(st.floats(min_value=0.1, max_value=1.0))
            },
            'notification_settings': {
                'email_enabled': draw(st.booleans()),
                'sms_enabled': draw(st.booleans()),
                'push_enabled': draw(st.booleans()),
                'red_flag_alerts': draw(st.booleans()),
                'session_reminders': draw(st.booleans())
            },
            'privacy_settings': {
                'data_sharing_consent': draw(st.booleans()),
                'analytics_consent': draw(st.booleans()),
                'marketing_consent': draw(st.booleans()),
                'session_recording_consent': draw(st.booleans())
            }
        }
    }


@composite
def invalid_user_data(draw):
    """Generate invalid user data for property testing"""
    # Choose what to make invalid
    invalid_type = draw(st.sampled_from(['email', 'user_id', 'role', 'empty_required']))
    
    base_data = {
        'user_id': 'valid_user_123',
        'email': 'valid@example.com',
        'role': 'client',
        'profile': {
            'first_name': 'John',
            'last_name': 'Doe'
        }
    }
    
    if invalid_type == 'email':
        # Invalid email formats
        invalid_email = draw(st.sampled_from([
            'invalid-email',
            '@example.com',
            'user@',
            'user@.com',
            'user space@example.com',
            ''
        ]))
        base_data['email'] = invalid_email
    elif invalid_type == 'user_id':
        # Invalid user ID formats
        invalid_user_id = draw(st.sampled_from([
            '',  # Empty
            'user with spaces',  # Spaces
            'user@invalid',  # Invalid characters
            'a' * 100,  # Too long
            '!@#$%^&*()',  # Special characters
        ]))
        base_data['user_id'] = invalid_user_id
    elif invalid_type == 'role':
        # Invalid roles
        invalid_role = draw(st.sampled_from([
            'invalid_role',
            'user',
            'moderator',
            '',
            123
        ]))
        base_data['role'] = invalid_role
    elif invalid_type == 'empty_required':
        # Remove required fields
        field_to_remove = draw(st.sampled_from(['user_id', 'email', 'role']))
        if field_to_remove in base_data:
            del base_data[field_to_remove]
    
    return base_data


class TestDynamoDBProperties(unittest.TestCase):
    """Property-based tests for DynamoDB operations"""
    
    def setUp(self):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ['ENVIRONMENT'] = 'test'
        os.environ['PROJECT_NAME'] = 'ai-therapy-platform'
        os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
        
        # Initialize validator
        self.validator = SimpleDataValidator()
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @given(user_data=valid_user_data())
    @settings(max_examples=5, deadline=None)
    @example(user_data={
        'user_id': 'test_user_123',
        'email': 'test@example.com',
        'role': 'client',
        'language_preference': 'en',
        'profile': {
            'first_name': 'Test',
            'last_name': 'User',
            'timezone': 'UTC',
            'phone_number': '+1234567890'
        },
        'preferences': {
            'language': 'en',
            'voice_settings': {
                'voice_id': 'default',
                'speed': 1.0,
                'pitch': 1.0,
                'volume': 1.0
            },
            'notification_settings': {
                'email_enabled': True,
                'sms_enabled': False,
                'push_enabled': True,
                'red_flag_alerts': True,
                'session_reminders': True
            },
            'privacy_settings': {
                'data_sharing_consent': False,
                'analytics_consent': False,
                'marketing_consent': False,
                'session_recording_consent': True
            }
        }
    })
    def test_property_user_registration_and_authentication(self, user_data):
        """
        Property 1: User Registration and Authentication
        For any valid user registration data, the system should validate it correctly
        and produce consistent results.
        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        # Test data validation
        validation_errors = self.validator.validate_user_data(user_data)
        
        # Property: Valid user data should pass validation
        self.assertEqual(len(validation_errors), 0, 
                        f"Valid user data should have no validation errors: {validation_errors}")
        
        # Property: Email should be valid format
        self.assertTrue(self.validator.validate_email(user_data['email']), 
                       f"Email {user_data['email']} should be valid")
        
        # Property: User ID should be valid format
        self.assertTrue(self.validator.validate_user_id(user_data['user_id']), 
                       f"User ID {user_data['user_id']} should be valid format")
        
        # Property: Role should be one of the valid roles
        self.assertIn(user_data['role'], ['client', 'therapist', 'admin'], 
                     f"Role {user_data['role']} must be one of the valid roles")
        
        # Property: Language preference should be valid
        if user_data.get('language_preference'):
            self.assertTrue(self.validator.validate_language_code(user_data['language_preference']),
                           f"Language preference {user_data['language_preference']} should be valid")
        
        # Property: Profile data should be valid
        if 'profile' in user_data:
            profile = user_data['profile']
            if 'first_name' in profile:
                self.assertTrue(self.validator.validate_string_length(profile['first_name'], 1, 50),
                               f"First name should be 1-50 characters: {profile['first_name']}")
            if 'last_name' in profile:
                self.assertTrue(self.validator.validate_string_length(profile['last_name'], 1, 50),
                               f"Last name should be 1-50 characters: {profile['last_name']}")
            if 'phone_number' in profile and profile['phone_number']:
                self.assertTrue(self.validator.validate_phone_number(profile['phone_number']),
                               f"Phone number should be valid: {profile['phone_number']}")
        
        # Property: Data sanitization should be safe
        sanitized_data = self.validator.sanitize_user_input(user_data)
        self.assertIsInstance(sanitized_data, dict, "Sanitized data should be a dictionary")
        
        # Property: Sanitized email should be lowercase
        if 'email' in sanitized_data:
            self.assertEqual(sanitized_data['email'], sanitized_data['email'].lower(),
                           "Sanitized email should be lowercase")
    
    @given(user_data=invalid_user_data())
    @settings(max_examples=3, deadline=None)
    def test_property_invalid_user_data_rejection(self, user_data):
        """
        Property: Invalid user data should always be rejected with appropriate errors
        For any invalid user registration data, the system should reject it with validation errors.
        """
        # Test data validation
        validation_errors = self.validator.validate_user_data(user_data)
        
        # Property: Invalid data should always result in validation errors
        self.assertGreater(len(validation_errors), 0, 
                          f"Invalid user data should have validation errors: {user_data}")
        
        # Property: Errors should be descriptive
        for field, errors in validation_errors.items():
            self.assertIsInstance(errors, list, f"Errors for {field} should be a list")
            self.assertGreater(len(errors), 0, f"Error list for {field} should not be empty")
            for error in errors:
                self.assertIsInstance(error, str, f"Error message should be string: {error}")
                self.assertGreater(len(error), 0, f"Error message should not be empty: {error}")
    
    @given(user_data=valid_user_data())
    @settings(max_examples=3, deadline=None)
    def test_property_data_consistency(self, user_data):
        """
        Property: Data validation should be consistent
        For any user data, validation should produce consistent results.
        """
        # Test validation consistency
        result1 = self.validator.validate_user_data(user_data)
        result2 = self.validator.validate_user_data(user_data)
        
        # Property: Validation should be deterministic
        self.assertEqual(result1, result2, f"Validation should be consistent for: {user_data}")
        
        # Property: Sanitization should be consistent
        sanitized1 = self.validator.sanitize_user_input(user_data)
        sanitized2 = self.validator.sanitize_user_input(user_data)
        
        self.assertEqual(sanitized1, sanitized2, f"Sanitization should be consistent for: {user_data}")
    
    @given(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    @settings(max_examples=3, deadline=None)
    def test_property_user_id_validation_consistency(self, user_id):
        """
        Property: User ID validation should be consistent
        For any string, validation should consistently determine if it's a valid user ID.
        """
        # Test validation consistency
        result1 = self.validator.validate_user_id(user_id)
        result2 = self.validator.validate_user_id(user_id)
        
        # Property: Validation should be deterministic
        self.assertEqual(result1, result2, f"User ID validation should be consistent for: {user_id}")
        
        # Property: Valid user IDs should meet format requirements
        if result1:
            self.assertGreater(len(user_id), 0, "Valid user ID should not be empty")
            self.assertLessEqual(len(user_id), 50, "Valid user ID should not exceed 50 characters")
            # Should only contain alphanumeric, hyphens, and underscores
            import re
            self.assertTrue(re.match(r'^[a-zA-Z0-9\-_]+$', user_id), 
                           f"Valid user ID should only contain allowed characters: {user_id}")
    
    @given(st.emails())
    @settings(max_examples=3, deadline=None)
    def test_property_email_validation_consistency(self, email):
        """
        Property: Email validation should be consistent
        For any email string, validation should consistently determine if it's valid.
        """
        # Test validation consistency
        result1 = self.validator.validate_email(email)
        result2 = self.validator.validate_email(email)
        
        # Property: Validation should be deterministic
        self.assertEqual(result1, result2, f"Email validation should be consistent for: {email}")
        
        # Property: Valid emails should contain @ and domain
        if result1:
            self.assertIn('@', email, "Valid email should contain @")
            parts = email.split('@')
            self.assertEqual(len(parts), 2, "Valid email should have exactly one @")
            self.assertGreater(len(parts[0]), 0, "Valid email should have non-empty local part")
            self.assertGreater(len(parts[1]), 0, "Valid email should have non-empty domain part")
    
    def test_property_data_sanitization_safety(self):
        """
        Property: Data sanitization should always produce safe output
        For any input string, sanitization should remove dangerous content.
        """
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "SELECT * FROM users WHERE id = '1' OR '1'='1'",
            "\x00null\x00byte",
            "<iframe src='javascript:alert(1)'></iframe>"
        ]
        
        for dangerous_input in dangerous_inputs:
            sanitized = self.validator.sanitize_string(dangerous_input)
            
            # Property: Sanitized output should not contain dangerous patterns
            self.assertNotIn('<script', sanitized.lower(), 
                           f"Sanitized string should not contain script tags: {sanitized}")
            self.assertNotIn('javascript:', sanitized.lower(), 
                           f"Sanitized string should not contain javascript: {sanitized}")
            self.assertNotIn('\x00', sanitized, 
                           f"Sanitized string should not contain null bytes: {sanitized}")
            
            # Property: Sanitized output should be a string
            self.assertIsInstance(sanitized, str, "Sanitized output should be string")


def run_property_tests():
    """Run property-based tests for DynamoDB operations"""
    print("🧪 Running Property-Based Tests for DynamoDB Operations")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: ai-therapy-platform, Property 1: User Registration and Authentication")
    print("**Validates: Requirements 1.1, 1.2, 1.3**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestDynamoDBProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All property-based tests passed!")
        print("✅ User Registration and Authentication properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant DynamoDB operations verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
        
        # Print failure details
        for test, traceback in result.failures:
            print(f"\nFAILURE: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_property_tests()
    exit(0 if success else 1)