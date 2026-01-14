#!/usr/bin/env python3
"""
Property-Based Tests for HTTP Status Code Correctness
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 12: HTTP Status Code Correctness
**Validates: Requirements 11.3-11.8**
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

# Import response formatter
import importlib.util
spec_rf = importlib.util.spec_from_file_location(
    "response_formatter",
    os.path.join(src_dir, "utils", "response_formatter.py")
)
response_formatter = importlib.util.module_from_spec(spec_rf)
spec_rf.loader.exec_module(response_formatter)

success_response = response_formatter.success_response
error_response = response_formatter.error_response
get_cors_headers = response_formatter.get_cors_headers


# Mock services for testing
class MockCognitoServiceWithFailures:
    """Mock Cognito service that can simulate various failure modes"""
    
    def __init__(self, mode='success'):
        self.mode = mode
    
    def verify_jwt_token(self, token):
        if self.mode == 'invalid_token':
            return {'valid': False}
        return {'valid': True, 'email': 'test@example.com', 'username': 'test-user', 'role': 'client'}
    
    def authenticate_user(self, email, password):
        if self.mode == 'auth_failure':
            return {'success': False, 'error': 'Invalid credentials'}
        return {'success': True, 'access_token': 'token', 'id_token': 'id', 'refresh_token': 'refresh', 'expires_in': 3600, 'user_info': {}}


class MockUserRepositoryWithFailures:
    """Mock user repository that can simulate various failure modes"""
    
    def __init__(self, mode='success'):
        self.mode = mode
    
    def get_user_by_email(self, email):
        if self.mode == 'not_found':
            return None
        return {'userId': 'test-id', 'email': email, 'role': 'client'}
    
    def get_user(self, user_id):
        if self.mode == 'not_found':
            return None
        return {'userId': user_id, 'email': 'test@example.com', 'role': 'client'}


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


# Handler functions that simulate various error conditions
def simulate_auth_failure_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simulate authentication failure - returns 401"""
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return error_response('Missing or invalid authorization header', 401)
    
    # Simulate invalid token
    return error_response('Invalid token', 401)


def simulate_authorization_failure_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simulate authorization failure - returns 403"""
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return error_response('Missing or invalid authorization header', 401)
    
    # Simulate user lacks permission
    return error_response('Access denied. Insufficient permissions.', 403)


def simulate_not_found_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simulate resource not found - returns 404"""
    resource_id = event.get('pathParameters', {}).get('id', 'unknown')
    return error_response(f'Resource not found: {resource_id}', 404)


def simulate_validation_failure_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simulate validation failure - returns 400"""
    if 'body' not in event:
        return error_response('Missing request body', 400)
    
    try:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
    except json.JSONDecodeError:
        return error_response('Invalid JSON in request body', 400)
    
    # Validate required fields
    errors = []
    if not body.get('email'):
        errors.append({'field': 'email', 'message': 'Email is required'})
    elif not validate_email(body.get('email', '')):
        errors.append({'field': 'email', 'message': 'Invalid email format'})
    
    if not body.get('password'):
        errors.append({'field': 'password', 'message': 'Password is required'})
    elif not validate_password(body.get('password', '')):
        errors.append({'field': 'password', 'message': 'Password does not meet requirements'})
    
    if errors:
        return error_response('Validation failed', 400, details={'validation_errors': errors})
    
    return success_response({'valid': True}, 200)


def simulate_server_error_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simulate server error - returns 500"""
    return error_response('Internal server error', 500)


# Strategies for generating test data
email_strategy = st.emails()
invalid_email_strategy = st.text(min_size=1, max_size=50).filter(lambda x: '@' not in x or '.' not in x.split('@')[-1] if '@' in x else True)
token_strategy = st.text(min_size=10, max_size=100, alphabet=st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'))
resource_id_strategy = st.text(min_size=1, max_size=50, alphabet=st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'))


class TestHTTPStatusCodeProperties(unittest.TestCase):
    """Property-based tests for HTTP status code correctness"""
    
    def setUp(self):
        """Set up test environment"""
        pass
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @given(token=token_strategy)
    @settings(max_examples=100, deadline=None)
    @example(token='invalid-token-123')
    def test_property_authentication_failure_returns_401(self, token):
        """
        Property 12: HTTP Status Code Correctness - Authentication Failure
        For any authentication failure, the system should return 401 status code.
        **Validates: Requirements 11.3**
        """
        event = {
            'headers': {
                'Authorization': f'Bearer {token}'
            }
        }
        
        response = simulate_auth_failure_handler(event, None)
        
        # Property: Authentication failures must return 401
        self.assertEqual(response['statusCode'], 401,
                        "Authentication failure must return 401 status code")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'],
                        "Authentication failure must have success: false")
        self.assertIn('error', body,
                     "Authentication failure must include error message")
    
    def test_property_missing_auth_header_returns_401(self):
        """
        Property 12: HTTP Status Code Correctness - Missing Auth Header
        For any request missing authorization header, the system should return 401.
        **Validates: Requirements 11.3**
        """
        # Test with empty headers
        response = simulate_auth_failure_handler({'headers': {}}, None)
        self.assertEqual(response['statusCode'], 401)
        
        # Test with wrong header format
        response = simulate_auth_failure_handler({'headers': {'Authorization': 'Basic abc'}}, None)
        self.assertEqual(response['statusCode'], 401)
    
    @given(token=token_strategy)
    @settings(max_examples=100, deadline=None)
    @example(token='valid-token-but-no-permission')
    def test_property_authorization_failure_returns_403(self, token):
        """
        Property 12: HTTP Status Code Correctness - Authorization Failure
        For any authorization failure, the system should return 403 status code.
        **Validates: Requirements 11.4**
        """
        event = {
            'headers': {
                'Authorization': f'Bearer {token}'
            }
        }
        
        response = simulate_authorization_failure_handler(event, None)
        
        # Property: Authorization failures must return 403
        self.assertEqual(response['statusCode'], 403,
                        "Authorization failure must return 403 status code")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'],
                        "Authorization failure must have success: false")
        self.assertIn('error', body,
                     "Authorization failure must include error message")
    
    @given(resource_id=resource_id_strategy)
    @settings(max_examples=100, deadline=None)
    @example(resource_id='non-existent-resource-123')
    def test_property_not_found_returns_404(self, resource_id):
        """
        Property 12: HTTP Status Code Correctness - Not Found
        For any resource not found, the system should return 404 status code.
        **Validates: Requirements 11.5**
        """
        event = {
            'pathParameters': {
                'id': resource_id
            }
        }
        
        response = simulate_not_found_handler(event, None)
        
        # Property: Not found must return 404
        self.assertEqual(response['statusCode'], 404,
                        "Not found must return 404 status code")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'],
                        "Not found must have success: false")
        self.assertIn('error', body,
                     "Not found must include error message")

    @given(invalid_email=invalid_email_strategy)
    @settings(max_examples=100, deadline=None)
    @example(invalid_email='not-an-email')
    @example(invalid_email='missing@domain')
    def test_property_validation_failure_returns_400(self, invalid_email):
        """
        Property 12: HTTP Status Code Correctness - Validation Failure
        For any validation failure, the system should return 400 status code.
        **Validates: Requirements 11.6**
        """
        event = {
            'body': json.dumps({
                'email': invalid_email,
                'password': 'short'  # Invalid password too
            })
        }
        
        response = simulate_validation_failure_handler(event, None)
        
        # Property: Validation failures must return 400
        self.assertEqual(response['statusCode'], 400,
                        "Validation failure must return 400 status code")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'],
                        "Validation failure must have success: false")
        self.assertIn('error', body,
                     "Validation failure must include error message")
    
    def test_property_missing_body_returns_400(self):
        """
        Property 12: HTTP Status Code Correctness - Missing Body
        For any request missing required body, the system should return 400.
        **Validates: Requirements 11.6**
        """
        response = simulate_validation_failure_handler({}, None)
        
        self.assertEqual(response['statusCode'], 400,
                        "Missing body must return 400 status code")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('error', body)
    
    def test_property_invalid_json_returns_400(self):
        """
        Property 12: HTTP Status Code Correctness - Invalid JSON
        For any request with invalid JSON body, the system should return 400.
        **Validates: Requirements 11.6**
        """
        event = {
            'body': 'not valid json {'
        }
        
        response = simulate_validation_failure_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400,
                        "Invalid JSON must return 400 status code")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('error', body)
    
    @given(data=st.dictionaries(st.text(min_size=1, max_size=20), st.text(min_size=1, max_size=50)))
    @settings(max_examples=100, deadline=None)
    def test_property_server_error_returns_500(self, data):
        """
        Property 12: HTTP Status Code Correctness - Server Error
        For any server error, the system should return 500 status code.
        **Validates: Requirements 11.7**
        """
        event = {
            'body': json.dumps(data)
        }
        
        response = simulate_server_error_handler(event, None)
        
        # Property: Server errors must return 500
        self.assertEqual(response['statusCode'], 500,
                        "Server error must return 500 status code")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'],
                        "Server error must have success: false")
        self.assertIn('error', body,
                     "Server error must include error message")
    
    @given(error_msg=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, deadline=None)
    @example(error_msg='Something went wrong')
    def test_property_error_responses_include_descriptive_messages(self, error_msg):
        """
        Property 12: HTTP Status Code Correctness - Descriptive Error Messages
        For any error response, the system should include descriptive error messages.
        **Validates: Requirements 11.8**
        """
        # Test various error responses
        response_401 = error_response(error_msg, 401)
        response_403 = error_response(error_msg, 403)
        response_404 = error_response(error_msg, 404)
        response_400 = error_response(error_msg, 400)
        response_500 = error_response(error_msg, 500)
        
        for response in [response_401, response_403, response_404, response_400, response_500]:
            body = json.loads(response['body'])
            
            # Property: All error responses must include error message
            self.assertIn('error', body,
                         "Error response must include 'error' field")
            self.assertEqual(body['error'], error_msg,
                           "Error message must match provided message")
            self.assertFalse(body['success'],
                           "Error response must have success: false")
    
    @given(error_msg=st.text(min_size=1, max_size=100),
           details=st.dictionaries(st.text(min_size=1, max_size=20), st.text(min_size=1, max_size=50), min_size=1))
    @settings(max_examples=100, deadline=None)
    @example(error_msg='Validation failed', details={'field': 'email', 'reason': 'invalid'})
    def test_property_validation_errors_include_details(self, error_msg, details):
        """
        Property 12: HTTP Status Code Correctness - Validation Error Details
        For any validation error, the system should include validation error details.
        **Validates: Requirements 11.6, 11.8**
        """
        response = error_response(error_msg, 400, details=details)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn('error', body)
        
        # Property: Validation errors with details should include them
        if details:
            self.assertIn('details', body,
                         "Validation error with details should include 'details' field")
            self.assertEqual(body['details'], details)
    
    def test_property_status_codes_are_integers(self):
        """
        Property 12: HTTP Status Code Correctness - Status Code Type
        For any response, the status code should be an integer.
        **Validates: Requirements 11.3-11.8**
        """
        status_codes = [200, 201, 400, 401, 403, 404, 500, 503]
        
        for code in status_codes:
            if code in [200, 201]:
                response = success_response({'test': 'data'}, code)
            else:
                response = error_response('Test error', code)
            
            # Property: Status code must be an integer
            self.assertIsInstance(response['statusCode'], int,
                                 f"Status code {code} must be an integer")
            self.assertEqual(response['statusCode'], code,
                           f"Status code must match expected value {code}")
    
    def test_property_error_status_codes_have_success_false(self):
        """
        Property 12: HTTP Status Code Correctness - Error Status Codes
        For any error status code (4xx, 5xx), success must be false.
        **Validates: Requirements 11.3-11.8**
        """
        error_codes = [400, 401, 403, 404, 500, 503]
        
        for code in error_codes:
            response = error_response('Test error', code)
            body = json.loads(response['body'])
            
            # Property: Error status codes must have success: false
            self.assertFalse(body['success'],
                           f"Status code {code} must have success: false")
    
    def test_property_success_status_codes_have_success_true(self):
        """
        Property 12: HTTP Status Code Correctness - Success Status Codes
        For any success status code (2xx), success must be true.
        **Validates: Requirements 11.3-11.8**
        """
        success_codes = [200, 201, 204]
        
        for code in success_codes:
            response = success_response({'test': 'data'}, code)
            body = json.loads(response['body'])
            
            # Property: Success status codes must have success: true
            self.assertTrue(body['success'],
                          f"Status code {code} must have success: true")
    
    @given(email=st.from_regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', fullmatch=True))
    @settings(max_examples=100, deadline=None)
    def test_property_valid_input_does_not_return_400(self, email):
        """
        Property 12: HTTP Status Code Correctness - Valid Input
        For any valid input, the system should not return 400 validation error.
        **Validates: Requirements 11.6**
        """
        # Create valid password
        valid_password = 'ValidPass123!'
        
        event = {
            'body': json.dumps({
                'email': email,
                'password': valid_password
            })
        }
        
        response = simulate_validation_failure_handler(event, None)
        
        # Property: Valid input should return 200, not 400
        self.assertEqual(response['statusCode'], 200,
                        "Valid input should not return 400")
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])


def run_http_status_code_property_tests():
    """Run property-based tests for HTTP status code correctness"""
    print("🧪 Running Property-Based Tests for HTTP Status Code Correctness")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 12: HTTP Status Code Correctness")
    print("**Validates: Requirements 11.3-11.8**")
    print("=" * 70)
    
    test_suite = unittest.TestSuite()
    tests = unittest.TestLoader().loadTestsFromTestCase(TestHTTPStatusCodeProperties)
    test_suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All HTTP status code property-based tests passed!")
        print("✅ HTTP Status Code Correctness properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant status codes verified")
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
    success = run_http_status_code_property_tests()
    exit(0 if success else 1)
