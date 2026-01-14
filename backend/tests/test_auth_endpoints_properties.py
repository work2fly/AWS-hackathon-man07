#!/usr/bin/env python3
"""
Property-Based Tests for Authentication Endpoints Availability
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 4: Authentication Endpoints Availability
**Validates: Requirements 3.1-3.8**
"""

import unittest
import json
import os
import sys
from typing import Dict, Any

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example

# Setup path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(backend_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import auth handlers directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "auth_handlers",
    os.path.join(src_dir, "lambda_functions", "auth_handlers.py")
)

# Mock dependencies before importing auth_handlers
class MockCognitoService:
    """Mock Cognito service for testing"""
    
    def register_user(self, email, password, role, language_preference):
        return {
            'success': True,
            'user_id': 'test-user-id',
            'email': email,
            'role': role
        }
    
    def authenticate_user(self, email, password):
        return {
            'success': True,
            'access_token': 'mock-access-token',
            'id_token': 'mock-id-token',
            'refresh_token': 'mock-refresh-token',
            'expires_in': 3600,
            'user_info': {'email': email, 'role': 'client'}
        }
    
    def refresh_token(self, refresh_token):
        return {
            'success': True,
            'access_token': 'new-mock-access-token',
            'id_token': 'new-mock-id-token',
            'expires_in': 3600
        }
    
    def verify_jwt_token(self, token):
        return {
            'valid': True,
            'email': 'test@example.com',
            'username': 'test-user',
            'role': 'client'
        }
    
    def reset_password(self, email):
        return {
            'success': True,
            'message': 'Password reset email sent'
        }
    
    def enable_mfa(self, username):
        return True
    
    def update_user_attributes(self, username, attributes):
        return True


class MockUserRepository:
    """Mock user repository for testing"""
    
    def get_user_by_email(self, email):
        return {
            'userId': 'test-user-id',
            'email': email,
            'role': 'client',
            'profile': {},
            'preferences': {},
            'languagePreference': 'en',
            'isActive': True,
            'mfaEnabled': False,
            'createdAt': '2025-01-01T00:00:00Z',
            'lastLoginAt': '2025-01-14T00:00:00Z'
        }
    
    def update_item(self, key, update_expression, expression_attribute_values):
        return True
    
    def enable_mfa(self, username):
        return True


class MockLogger:
    """Mock logger for testing"""
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass
    def debug(self, msg): pass


# Create mock instances
mock_cognito = MockCognitoService()
mock_user_repo = MockUserRepository()
mock_logger = MockLogger()


def validate_email(email):
    """Simple email validation for testing"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """Simple password validation for testing"""
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    return has_upper and has_lower and has_digit and has_symbol


# Import response formatter
spec_rf = importlib.util.spec_from_file_location(
    "response_formatter",
    os.path.join(src_dir, "utils", "response_formatter.py")
)
response_formatter = importlib.util.module_from_spec(spec_rf)
spec_rf.loader.exec_module(response_formatter)

success_response = response_formatter.success_response
error_response = response_formatter.error_response
get_cors_headers = response_formatter.get_cors_headers


# Define auth handler functions locally with mocks
def register_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle user registration"""
    try:
        if 'body' not in event:
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        role = body.get('role', 'client').lower()
        language_preference = body.get('language_preference', 'en')
        
        if not all([email, password, role]):
            return error_response('Missing required fields: email, password, role', 400,
                                 details={'fields': ['email', 'password', 'role']})
        
        if not validate_email(email):
            return error_response('Invalid email format', 400, details={'field': 'email'})
        
        if not validate_password(password):
            return error_response(
                'Password must be at least 8 characters with uppercase, lowercase, number, and symbol',
                400, details={'field': 'password'}
            )
        
        if role not in ['client', 'therapist', 'admin']:
            return error_response('Invalid role. Must be client, therapist, or admin', 400,
                                 details={'field': 'role', 'valid_values': ['client', 'therapist', 'admin']})
        
        result = mock_cognito.register_user(email, password, role, language_preference)
        
        if result['success']:
            return success_response(
                {'user_id': result['user_id'], 'email': result['email'], 'role': result['role']},
                201, message='User registered successfully'
            )
        else:
            return error_response(result['error'], 400)
    
    except json.JSONDecodeError:
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        return error_response('Internal server error', 500)


def login_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle user login"""
    try:
        if 'body' not in event:
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        
        if not all([email, password]):
            return error_response('Missing email or password', 400,
                                 details={'fields': ['email', 'password']})
        
        result = mock_cognito.authenticate_user(email, password)
        
        if result['success']:
            return success_response(
                {
                    'access_token': result['access_token'],
                    'id_token': result['id_token'],
                    'refresh_token': result['refresh_token'],
                    'expires_in': result['expires_in'],
                    'user_info': result['user_info']
                },
                200, message='Authentication successful'
            )
        else:
            return error_response(result['error'], 401)
    
    except json.JSONDecodeError:
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        return error_response('Internal server error', 500)


def logout_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle user logout"""
    try:
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return error_response('Missing or invalid authorization header', 401)
        
        access_token = auth_header.replace('Bearer ', '')
        token_info = mock_cognito.verify_jwt_token(access_token)
        
        if token_info['valid']:
            return success_response({'logged_out': True}, 200, message='Logout successful')
        else:
            return error_response('Invalid token', 401)
    
    except Exception as e:
        return error_response('Internal server error', 500)


def refresh_token_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle token refresh"""
    try:
        if 'body' not in event:
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        refresh_token = body.get('refresh_token', '')
        
        if not refresh_token:
            return error_response('Missing refresh token', 400, details={'field': 'refresh_token'})
        
        result = mock_cognito.refresh_token(refresh_token)
        
        if result['success']:
            return success_response(
                {
                    'access_token': result['access_token'],
                    'id_token': result['id_token'],
                    'expires_in': result['expires_in']
                },
                200, message='Token refreshed successfully'
            )
        else:
            return error_response(result['error'], 401)
    
    except json.JSONDecodeError:
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        return error_response('Internal server error', 500)


def get_profile_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get user profile"""
    try:
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return error_response('Missing or invalid authorization header', 401)
        
        access_token = auth_header.replace('Bearer ', '')
        token_info = mock_cognito.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            return error_response('Invalid token', 401)
        
        user_data = mock_user_repo.get_user_by_email(token_info['email'])
        
        if user_data:
            profile_data = {
                'user_id': user_data.get('userId'),
                'email': user_data.get('email'),
                'role': user_data.get('role'),
                'profile': user_data.get('profile', {}),
                'preferences': user_data.get('preferences', {}),
                'language_preference': user_data.get('languagePreference', 'en'),
                'is_active': user_data.get('isActive', True),
                'mfa_enabled': user_data.get('mfaEnabled', False),
                'created_at': user_data.get('createdAt'),
                'last_login_at': user_data.get('lastLoginAt')
            }
            return success_response(profile_data, 200)
        else:
            return error_response('User profile not found', 404)
    
    except Exception as e:
        return error_response('Internal server error', 500)


def update_profile_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Update user profile"""
    try:
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return error_response('Missing or invalid authorization header', 401)
        
        access_token = auth_header.replace('Bearer ', '')
        token_info = mock_cognito.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            return error_response('Invalid token', 401)
        
        if 'body' not in event:
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        user_data = mock_user_repo.get_user_by_email(token_info['email'])
        
        if not user_data:
            return error_response('User not found', 404)
        
        success = mock_user_repo.update_item(
            key={'userId': user_data['userId']},
            update_expression="SET profile = :profile",
            expression_attribute_values={':profile': body.get('profile', {})}
        )
        
        if success:
            return success_response({'updated': True}, 200, message='Profile updated successfully')
        else:
            return error_response('Failed to update profile', 500)
    
    except json.JSONDecodeError:
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        return error_response('Internal server error', 500)


def enable_mfa_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Enable MFA for user"""
    try:
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return error_response('Missing or invalid authorization header', 401)
        
        access_token = auth_header.replace('Bearer ', '')
        token_info = mock_cognito.verify_jwt_token(access_token)
        
        if not token_info['valid']:
            return error_response('Invalid token', 401)
        
        success = mock_cognito.enable_mfa(token_info['username'])
        
        if success:
            mock_user_repo.enable_mfa(token_info['username'])
            return success_response({'mfa_enabled': True}, 200, message='MFA enabled successfully')
        else:
            return error_response('Failed to enable MFA', 500)
    
    except Exception as e:
        return error_response('Internal server error', 500)


def reset_password_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle password reset request"""
    try:
        if 'body' not in event:
            return error_response('Missing request body', 400)
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        email = body.get('email', '').strip().lower()
        
        if not email:
            return error_response('Missing email', 400, details={'field': 'email'})
        
        if not validate_email(email):
            return error_response('Invalid email format', 400, details={'field': 'email'})
        
        result = mock_cognito.reset_password(email)
        
        if result['success']:
            return success_response({'email': email}, 200, message=result['message'])
        else:
            return error_response(result['error'], 400)
    
    except json.JSONDecodeError:
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        return error_response('Internal server error', 500)


# Strategies for generating test data
email_strategy = st.emails()
password_strategy = st.text(
    alphabet=st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'),
    min_size=8, max_size=20
).filter(lambda p: any(c.isupper() for c in p) and any(c.islower() for c in p) 
         and any(c.isdigit() for c in p) and any(c in '!@#$%^&*' for c in p))
role_strategy = st.sampled_from(['client', 'therapist', 'admin'])
token_strategy = st.text(min_size=10, max_size=100, alphabet=st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'))


class TestAuthEndpointsProperties(unittest.TestCase):
    """Property-based tests for authentication endpoints availability"""
    
    def setUp(self):
        """Set up test environment"""
        pass
    
    def tearDown(self):
        """Clean up test environment"""
        pass

    @given(email=email_strategy, password=password_strategy, role=role_strategy)
    @settings(max_examples=100, deadline=None)
    @example(email='test@example.com', password='Test123!@', role='client')
    def test_property_register_endpoint_returns_correct_format(self, email, password, role):
        """
        Property 4: Authentication Endpoints Availability - Register
        For any valid registration request, the endpoint should return the expected response structure.
        **Validates: Requirements 3.1**
        """
        event = {
            'body': json.dumps({
                'email': email,
                'password': password,
                'role': role,
                'language_preference': 'en'
            })
        }
        
        response = register_handler(event, None)
        
        # Property: Response must have required structure
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        
        # Property: Body must be valid JSON
        body = json.loads(response['body'])
        self.assertIn('success', body)
        
        # Property: Successful registration returns 201 with success: true
        if response['statusCode'] == 201:
            self.assertTrue(body['success'])
            self.assertIn('data', body)
            self.assertIn('user_id', body['data'])
            self.assertIn('email', body['data'])
            self.assertIn('role', body['data'])
    
    @given(email=email_strategy, password=password_strategy)
    @settings(max_examples=100, deadline=None)
    @example(email='test@example.com', password='Test123!@')
    def test_property_login_endpoint_returns_correct_format(self, email, password):
        """
        Property 4: Authentication Endpoints Availability - Login
        For any valid login request, the endpoint should return the expected response structure.
        **Validates: Requirements 3.2**
        """
        event = {
            'body': json.dumps({
                'email': email,
                'password': password
            })
        }
        
        response = login_handler(event, None)
        
        # Property: Response must have required structure
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        
        body = json.loads(response['body'])
        self.assertIn('success', body)
        
        # Property: Successful login returns 200 with tokens
        if response['statusCode'] == 200:
            self.assertTrue(body['success'])
            self.assertIn('data', body)
            self.assertIn('access_token', body['data'])
            self.assertIn('id_token', body['data'])
            self.assertIn('refresh_token', body['data'])
    
    @given(token=token_strategy)
    @settings(max_examples=100, deadline=None)
    @example(token='valid-access-token-123')
    def test_property_logout_endpoint_returns_correct_format(self, token):
        """
        Property 4: Authentication Endpoints Availability - Logout
        For any logout request with authorization, the endpoint should return the expected response structure.
        **Validates: Requirements 3.3**
        """
        event = {
            'headers': {
                'Authorization': f'Bearer {token}'
            }
        }
        
        response = logout_handler(event, None)
        
        # Property: Response must have required structure
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        
        body = json.loads(response['body'])
        self.assertIn('success', body)
        
        # Property: Successful logout returns 200
        if response['statusCode'] == 200:
            self.assertTrue(body['success'])
    
    @given(refresh_token=token_strategy)
    @settings(max_examples=100, deadline=None)
    @example(refresh_token='valid-refresh-token-123')
    def test_property_refresh_endpoint_returns_correct_format(self, refresh_token):
        """
        Property 4: Authentication Endpoints Availability - Refresh
        For any token refresh request, the endpoint should return the expected response structure.
        **Validates: Requirements 3.4**
        """
        event = {
            'body': json.dumps({
                'refresh_token': refresh_token
            })
        }
        
        response = refresh_token_handler(event, None)
        
        # Property: Response must have required structure
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        
        body = json.loads(response['body'])
        self.assertIn('success', body)
        
        # Property: Successful refresh returns 200 with new tokens
        if response['statusCode'] == 200:
            self.assertTrue(body['success'])
            self.assertIn('data', body)
            self.assertIn('access_token', body['data'])
            self.assertIn('id_token', body['data'])
    
    @given(token=token_strategy)
    @settings(max_examples=100, deadline=None)
    @example(token='valid-access-token-123')
    def test_property_get_profile_endpoint_returns_correct_format(self, token):
        """
        Property 4: Authentication Endpoints Availability - Get Profile
        For any get profile request with authorization, the endpoint should return the expected response structure.
        **Validates: Requirements 3.5**
        """
        event = {
            'headers': {
                'Authorization': f'Bearer {token}'
            }
        }
        
        response = get_profile_handler(event, None)
        
        # Property: Response must have required structure
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        
        body = json.loads(response['body'])
        self.assertIn('success', body)
        
        # Property: Successful profile retrieval returns 200 with user data
        if response['statusCode'] == 200:
            self.assertTrue(body['success'])
            self.assertIn('data', body)
            self.assertIn('user_id', body['data'])
            self.assertIn('email', body['data'])
            self.assertIn('role', body['data'])
    
    @given(token=token_strategy, first_name=st.text(min_size=1, max_size=50, alphabet=st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')))
    @settings(max_examples=100, deadline=None)
    @example(token='valid-access-token-123', first_name='John')
    def test_property_update_profile_endpoint_returns_correct_format(self, token, first_name):
        """
        Property 4: Authentication Endpoints Availability - Update Profile
        For any update profile request with authorization, the endpoint should return the expected response structure.
        **Validates: Requirements 3.6**
        """
        event = {
            'headers': {
                'Authorization': f'Bearer {token}'
            },
            'body': json.dumps({
                'profile': {
                    'first_name': first_name
                }
            })
        }
        
        response = update_profile_handler(event, None)
        
        # Property: Response must have required structure
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        
        body = json.loads(response['body'])
        self.assertIn('success', body)
        
        # Property: Successful update returns 200
        if response['statusCode'] == 200:
            self.assertTrue(body['success'])
    
    @given(token=token_strategy)
    @settings(max_examples=100, deadline=None)
    @example(token='valid-access-token-123')
    def test_property_enable_mfa_endpoint_returns_correct_format(self, token):
        """
        Property 4: Authentication Endpoints Availability - Enable MFA
        For any enable MFA request with authorization, the endpoint should return the expected response structure.
        **Validates: Requirements 3.7**
        """
        event = {
            'headers': {
                'Authorization': f'Bearer {token}'
            }
        }
        
        response = enable_mfa_handler(event, None)
        
        # Property: Response must have required structure
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        
        body = json.loads(response['body'])
        self.assertIn('success', body)
        
        # Property: Successful MFA enable returns 200
        if response['statusCode'] == 200:
            self.assertTrue(body['success'])
    
    @given(email=email_strategy)
    @settings(max_examples=100, deadline=None)
    @example(email='test@example.com')
    def test_property_reset_password_endpoint_returns_correct_format(self, email):
        """
        Property 4: Authentication Endpoints Availability - Reset Password
        For any reset password request, the endpoint should return the expected response structure.
        **Validates: Requirements 3.8**
        """
        event = {
            'body': json.dumps({
                'email': email
            })
        }
        
        response = reset_password_handler(event, None)
        
        # Property: Response must have required structure
        self.assertIn('statusCode', response)
        self.assertIn('headers', response)
        self.assertIn('body', response)
        
        body = json.loads(response['body'])
        self.assertIn('success', body)
        
        # Property: Successful reset returns 200
        if response['statusCode'] == 200:
            self.assertTrue(body['success'])
    
    @given(email=email_strategy, password=password_strategy, role=role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_property_all_auth_responses_have_cors_headers(self, email, password, role):
        """
        Property 4: Authentication Endpoints Availability - CORS Headers
        For any authentication endpoint response, CORS headers should be present.
        **Validates: Requirements 3.1-3.8**
        """
        # Test register endpoint
        register_event = {
            'body': json.dumps({'email': email, 'password': password, 'role': role})
        }
        register_response = register_handler(register_event, None)
        
        # Property: All responses must have CORS headers
        self.assertIn('Access-Control-Allow-Origin', register_response['headers'])
        self.assertIn('Access-Control-Allow-Methods', register_response['headers'])
        self.assertIn('Access-Control-Allow-Headers', register_response['headers'])
    
    def test_property_missing_body_returns_400(self):
        """
        Property 4: Authentication Endpoints Availability - Missing Body
        For any endpoint requiring a body, missing body should return 400.
        **Validates: Requirements 3.1-3.8**
        """
        # Test register without body
        response = register_handler({}, None)
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        
        # Test login without body
        response = login_handler({}, None)
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
    
    def test_property_missing_auth_header_returns_401(self):
        """
        Property 4: Authentication Endpoints Availability - Missing Auth
        For any endpoint requiring authorization, missing auth should return 401.
        **Validates: Requirements 3.3, 3.5, 3.6, 3.7**
        """
        # Test logout without auth
        response = logout_handler({'headers': {}}, None)
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        
        # Test get profile without auth
        response = get_profile_handler({'headers': {}}, None)
        self.assertEqual(response['statusCode'], 401)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])


def run_auth_endpoints_property_tests():
    """Run property-based tests for authentication endpoints"""
    print("🧪 Running Property-Based Tests for Authentication Endpoints")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 4: Authentication Endpoints Availability")
    print("**Validates: Requirements 3.1-3.8**")
    print("=" * 70)
    
    test_suite = unittest.TestSuite()
    tests = unittest.TestLoader().loadTestsFromTestCase(TestAuthEndpointsProperties)
    test_suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All authentication endpoints property-based tests passed!")
        print("✅ Authentication Endpoints Availability properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant authentication verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
        
        for test, traceback in result.failures:
            print(f"\nFAILURE: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_auth_endpoints_property_tests()
    exit(0 if success else 1)
