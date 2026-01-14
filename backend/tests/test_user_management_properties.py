#!/usr/bin/env python3
"""
Property-Based Tests for User Management Endpoints
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 5: User Management Endpoints Availability
**Validates: Requirements 4.1-4.5**
"""

import unittest
import json
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock, create_autospec
from datetime import datetime

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example
from hypothesis.strategies import composite

# Setup path for imports
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the actual response formatter and auth utilities we need
from src.utils.response_formatter import success_response, error_response
from src.middleware.auth_middleware import get_user_from_event, is_user_authorized_for_resource


@composite
def user_id_strategy(draw):
    """Generate valid user IDs"""
    return draw(st.text(
        min_size=10,
        max_size=50,
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
    ))


@composite
def email_strategy(draw):
    """Generate valid email addresses"""
    username = draw(st.text(min_size=3, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
    domain = draw(st.sampled_from(['example.com', 'test.com', 'therapy.com']))
    return f"{username}@{domain}"


@composite
def role_strategy(draw):
    """Generate valid user roles"""
    return draw(st.sampled_from(['client', 'therapist', 'admin']))


@composite
def language_strategy(draw):
    """Generate valid language preferences"""
    return draw(st.sampled_from(['en', 'es', 'fr', 'de', 'it', 'pt']))


@composite
def user_data_strategy(draw):
    """Generate complete user data"""
    return {
        'userId': draw(user_id_strategy()),
        'email': draw(email_strategy()),
        'role': draw(role_strategy()),
        'profile': {
            'firstName': draw(st.text(min_size=2, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')),
            'lastName': draw(st.text(min_size=2, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        },
        'preferences': {
            'notifications': draw(st.booleans()),
            'theme': draw(st.sampled_from(['light', 'dark', 'auto']))
        },
        'isActive': draw(st.booleans()),
        'mfaEnabled': draw(st.booleans()),
        'languagePreference': draw(language_strategy()),
        'createdAt': '2024-01-01T00:00:00Z',
        'updatedAt': '2024-01-01T00:00:00Z'
    }


@composite
def session_data_strategy(draw):
    """Generate session data"""
    return {
        'sessionId': draw(st.text(min_size=10, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_')),
        'userId': draw(user_id_strategy()),
        'therapistId': draw(user_id_strategy()),
        'status': draw(st.sampled_from(['active', 'completed', 'cancelled'])),
        'startTime': '2024-01-01T10:00:00Z',
        'endTime': '2024-01-01T11:00:00Z',
        'duration': draw(st.integers(min_value=300, max_value=7200)),
        'timestamp': '2024-01-01T10:00:00Z',
        'metadata': {}
    }


@composite
def get_user_event_strategy(draw):
    """Generate Lambda event for GET /users/{userId}"""
    user_id = draw(user_id_strategy())
    auth_user_id = draw(user_id_strategy())
    auth_role = draw(role_strategy())
    
    return {
        'httpMethod': 'GET',
        'path': f'/users/{user_id}',
        'pathParameters': {
            'userId': user_id
        },
        'headers': {
            'Authorization': 'Bearer mock.jwt.token',
            'Content-Type': 'application/json'
        },
        'user_info': {
            'user_id': auth_user_id,
            'email': draw(email_strategy()),
            'role': auth_role,
            'username': draw(st.text(min_size=5, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'))
        },
        'requestContext': {
            'requestId': draw(st.text(min_size=20, max_size=40, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
        }
    }


@composite
def update_user_event_strategy(draw):
    """Generate Lambda event for PUT /users/{userId}"""
    user_id = draw(user_id_strategy())
    auth_user_id = draw(user_id_strategy())
    auth_role = draw(role_strategy())
    
    update_data = {}
    
    # Randomly include fields to update
    if draw(st.booleans()):
        update_data['profile'] = {
            'firstName': draw(st.text(min_size=2, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')),
            'lastName': draw(st.text(min_size=2, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        }
    
    if draw(st.booleans()):
        update_data['preferences'] = {
            'notifications': draw(st.booleans()),
            'theme': draw(st.sampled_from(['light', 'dark', 'auto']))
        }
    
    if draw(st.booleans()):
        update_data['languagePreference'] = draw(language_strategy())
    
    return {
        'httpMethod': 'PUT',
        'path': f'/users/{user_id}',
        'pathParameters': {
            'userId': user_id
        },
        'headers': {
            'Authorization': 'Bearer mock.jwt.token',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(update_data),
        'user_info': {
            'user_id': auth_user_id,
            'email': draw(email_strategy()),
            'role': auth_role,
            'username': draw(st.text(min_size=5, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'))
        },
        'requestContext': {
            'requestId': draw(st.text(min_size=20, max_size=40, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
        }
    }


@composite
def get_user_sessions_event_strategy(draw):
    """Generate Lambda event for GET /users/{userId}/sessions"""
    user_id = draw(user_id_strategy())
    auth_user_id = draw(user_id_strategy())
    auth_role = draw(role_strategy())
    
    return {
        'httpMethod': 'GET',
        'path': f'/users/{user_id}/sessions',
        'pathParameters': {
            'userId': user_id
        },
        'queryStringParameters': {
            'limit': str(draw(st.integers(min_value=10, max_value=100)))
        },
        'headers': {
            'Authorization': 'Bearer mock.jwt.token',
            'Content-Type': 'application/json'
        },
        'user_info': {
            'user_id': auth_user_id,
            'email': draw(email_strategy()),
            'role': auth_role,
            'username': draw(st.text(min_size=5, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'))
        },
        'requestContext': {
            'requestId': draw(st.text(min_size=20, max_size=40, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
        }
    }


class TestUserManagementEndpointsProperties(unittest.TestCase):
    """Property-based tests for user management endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        # Import handlers with mocked dependencies
        with patch('lambda_functions.user_handlers.user_repository') as mock_user_repo, \
             patch('lambda_functions.user_handlers.session_repository') as mock_session_repo:
            from lambda_functions import user_handlers
            self.user_handlers = user_handlers
            self.mock_user_repo = mock_user_repo
            self.mock_session_repo = mock_session_repo
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @patch('lambda_functions.user_handlers.user_repository')
    @given(event=get_user_event_strategy(), user_data=user_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_get_user_endpoint_exists(self, event, user_data, mock_user_repo):
        """
        Property 5: User Management Endpoints Availability - GET /users/{userId}
        For any GET request to /users/{userId} with valid authentication,
        the endpoint should exist and return the expected response structure.
        **Validates: Requirements 4.1, 4.4**
        """
        from lambda_functions.user_handlers import get_user_handler
        
        # Make user_id match for authorization
        user_data['userId'] = event['pathParameters']['userId']
        event['user_info']['user_id'] = event['pathParameters']['userId']
        event['user_info']['role'] = 'admin'  # Admin can access any user
        
        # Mock repository to return user data
        mock_user_repo.get_item.return_value = user_data
        
        # Property: Endpoint should exist and return valid response
        response = get_user_handler(event, None)
        
        self.assertIsNotNone(response, "Response should not be None")
        self.assertIsInstance(response, dict, "Response should be a dictionary")
        
        # Property: Response should have required fields
        self.assertIn('statusCode', response, "Response should include statusCode")
        self.assertIn('headers', response, "Response should include headers")
        self.assertIn('body', response, "Response should include body")
        
        # Property: Status code should be valid HTTP status
        self.assertIn(response['statusCode'], [200, 401, 403, 404, 500], 
                     "Status code should be a valid HTTP status")
        
        # Property: Headers should include CORS headers
        headers = response['headers']
        self.assertIn('Access-Control-Allow-Origin', headers, 
                     "Headers should include CORS origin")
        self.assertIn('Content-Type', headers, 
                     "Headers should include Content-Type")
        
        # Property: Body should be valid JSON
        try:
            body_data = json.loads(response['body'])
            self.assertIsInstance(body_data, dict, "Body should be a JSON object")
            
            # Property: Body should have success field
            self.assertIn('success', body_data, "Body should include success field")
            
            # If successful, should have data field
            if response['statusCode'] == 200:
                self.assertIn('data', body_data, "Successful response should include data")
                
                # Property: User data should have required fields
                user_response = body_data['data']
                required_fields = ['userId', 'email', 'role', 'profile', 'preferences']
                for field in required_fields:
                    self.assertIn(field, user_response, 
                                f"User data should include {field}")
        except json.JSONDecodeError:
            self.fail("Response body should be valid JSON")
    
    @patch('lambda_functions.user_handlers.user_repository')
    @given(event=get_user_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_get_user_authorization_enforcement(self, event, mock_user_repo):
        """
        Property 5: User Management Endpoints Availability - Authorization Check
        For any GET request to /users/{userId} where the authenticated user
        is not authorized, the endpoint should return 403 Forbidden.
        **Validates: Requirements 4.4**
        """
        from lambda_functions.user_handlers import get_user_handler
        
        # Set up scenario where user tries to access another user's data
        event['user_info']['user_id'] = 'different_user_id'
        event['user_info']['role'] = 'client'  # Client can only access own data
        
        # Mock repository (shouldn't be called due to auth failure)
        mock_user_repo.get_item.return_value = None
        
        # Property: Unauthorized access should return 403
        response = get_user_handler(event, None)
        
        # Should return 403 for unauthorized access
        if event['user_info']['user_id'] != event['pathParameters']['userId']:
            self.assertEqual(response['statusCode'], 403, 
                           "Unauthorized access should return 403")
            
            body_data = json.loads(response['body'])
            self.assertFalse(body_data['success'], 
                           "Unauthorized response should have success=false")
            self.assertIn('error', body_data, 
                         "Unauthorized response should include error message")
    
    @patch('lambda_functions.user_handlers.user_repository')
    @given(event=update_user_event_strategy(), user_data=user_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_update_user_endpoint_exists(self, event, user_data, mock_user_repo):
        """
        Property 5: User Management Endpoints Availability - PUT /users/{userId}
        For any PUT request to /users/{userId} with valid authentication,
        the endpoint should exist and return the expected response structure.
        **Validates: Requirements 4.2, 4.5**
        """
        from lambda_functions.user_handlers import update_user_handler
        
        # Make user_id match for authorization
        user_data['userId'] = event['pathParameters']['userId']
        event['user_info']['user_id'] = event['pathParameters']['userId']
        
        # Mock repository
        mock_user_repo.get_item.return_value = user_data
        mock_user_repo.update_item.return_value = True
        
        # Property: Endpoint should exist and return valid response
        response = update_user_handler(event, None)
        
        self.assertIsNotNone(response, "Response should not be None")
        self.assertIsInstance(response, dict, "Response should be a dictionary")
        
        # Property: Response should have required fields
        self.assertIn('statusCode', response, "Response should include statusCode")
        self.assertIn('headers', response, "Response should include headers")
        self.assertIn('body', response, "Response should include body")
        
        # Property: Status code should be valid HTTP status
        self.assertIn(response['statusCode'], [200, 400, 401, 403, 404, 500], 
                     "Status code should be a valid HTTP status")
        
        # Property: Headers should include CORS headers
        headers = response['headers']
        self.assertIn('Access-Control-Allow-Origin', headers, 
                     "Headers should include CORS origin")
        
        # Property: Body should be valid JSON
        try:
            body_data = json.loads(response['body'])
            self.assertIsInstance(body_data, dict, "Body should be a JSON object")
            self.assertIn('success', body_data, "Body should include success field")
            
            # If successful, should have data field
            if response['statusCode'] == 200:
                self.assertIn('data', body_data, "Successful response should include data")
        except json.JSONDecodeError:
            self.fail("Response body should be valid JSON")
    
    @patch('lambda_functions.user_handlers.user_repository')
    @given(event=update_user_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_update_user_authorization_enforcement(self, event, mock_user_repo):
        """
        Property 5: User Management Endpoints Availability - Update Authorization
        For any PUT request to /users/{userId} where the authenticated user
        is not authorized, the endpoint should return 403 Forbidden.
        **Validates: Requirements 4.5**
        """
        from lambda_functions.user_handlers import update_user_handler
        
        # Set up scenario where user tries to update another user's data
        event['user_info']['user_id'] = 'different_user_id'
        event['user_info']['role'] = 'client'  # Client can only update own data
        
        # Property: Unauthorized update should return 403
        response = update_user_handler(event, None)
        
        # Should return 403 for unauthorized access
        if event['user_info']['user_id'] != event['pathParameters']['userId']:
            self.assertEqual(response['statusCode'], 403, 
                           "Unauthorized update should return 403")
            
            body_data = json.loads(response['body'])
            self.assertFalse(body_data['success'], 
                           "Unauthorized response should have success=false")
    
    @patch('lambda_functions.user_handlers.session_repository')
    @given(event=get_user_sessions_event_strategy(), sessions=st.lists(session_data_strategy(), min_size=0, max_size=10))
    @settings(max_examples=100, deadline=None)
    def test_property_get_user_sessions_endpoint_exists(self, event, sessions, mock_session_repo):
        """
        Property 5: User Management Endpoints Availability - GET /users/{userId}/sessions
        For any GET request to /users/{userId}/sessions with valid authentication,
        the endpoint should exist and return the expected response structure.
        **Validates: Requirements 4.3, 4.4**
        """
        from lambda_functions.user_handlers import get_user_sessions_handler
        
        # Make user_id match for authorization
        event['user_info']['user_id'] = event['pathParameters']['userId']
        
        # Ensure all sessions belong to the user
        for session in sessions:
            session['userId'] = event['pathParameters']['userId']
        
        # Mock repository to return sessions
        mock_session_repo.query.return_value = {
            'Items': sessions,
            'LastEvaluatedKey': None
        }
        
        # Property: Endpoint should exist and return valid response
        response = get_user_sessions_handler(event, None)
        
        self.assertIsNotNone(response, "Response should not be None")
        self.assertIsInstance(response, dict, "Response should be a dictionary")
        
        # Property: Response should have required fields
        self.assertIn('statusCode', response, "Response should include statusCode")
        self.assertIn('headers', response, "Response should include headers")
        self.assertIn('body', response, "Response should include body")
        
        # Property: Status code should be valid HTTP status
        self.assertIn(response['statusCode'], [200, 401, 403, 404, 500], 
                     "Status code should be a valid HTTP status")
        
        # Property: Headers should include CORS headers
        headers = response['headers']
        self.assertIn('Access-Control-Allow-Origin', headers, 
                     "Headers should include CORS origin")
        
        # Property: Body should be valid JSON
        try:
            body_data = json.loads(response['body'])
            self.assertIsInstance(body_data, dict, "Body should be a JSON object")
            self.assertIn('success', body_data, "Body should include success field")
            
            # If successful, should have data field with sessions
            if response['statusCode'] == 200:
                self.assertIn('data', body_data, "Successful response should include data")
                
                # Property: Data should have sessions array
                data = body_data['data']
                self.assertIn('sessions', data, "Data should include sessions array")
                self.assertIn('count', data, "Data should include count")
                self.assertIsInstance(data['sessions'], list, 
                                    "Sessions should be a list")
                
                # Property: Each session should have required fields
                for session in data['sessions']:
                    required_fields = ['sessionId', 'userId', 'status', 'startTime']
                    for field in required_fields:
                        self.assertIn(field, session, 
                                    f"Session should include {field}")
        except json.JSONDecodeError:
            self.fail("Response body should be valid JSON")
    
    @patch('lambda_functions.user_handlers.session_repository')
    @given(event=get_user_sessions_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_get_user_sessions_authorization_enforcement(self, event, mock_session_repo):
        """
        Property 5: User Management Endpoints Availability - Sessions Authorization
        For any GET request to /users/{userId}/sessions where the authenticated user
        is not authorized, the endpoint should return 403 Forbidden.
        **Validates: Requirements 4.4**
        """
        from lambda_functions.user_handlers import get_user_sessions_handler
        
        # Set up scenario where user tries to access another user's sessions
        event['user_info']['user_id'] = 'different_user_id'
        event['user_info']['role'] = 'client'  # Client can only access own sessions
        
        # Property: Unauthorized access should return 403
        response = get_user_sessions_handler(event, None)
        
        # Should return 403 for unauthorized access
        if event['user_info']['user_id'] != event['pathParameters']['userId']:
            self.assertEqual(response['statusCode'], 403, 
                           "Unauthorized access should return 403")
            
            body_data = json.loads(response['body'])
            self.assertFalse(body_data['success'], 
                           "Unauthorized response should have success=false")
    
    @patch('lambda_functions.user_handlers.user_repository')
    @given(event=get_user_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_get_user_not_found(self, event, mock_user_repo):
        """
        Property 5: User Management Endpoints Availability - User Not Found
        For any GET request to /users/{userId} where the user does not exist,
        the endpoint should return 404 Not Found.
        **Validates: Requirements 4.1**
        """
        from lambda_functions.user_handlers import get_user_handler
        
        # Make user authorized
        event['user_info']['user_id'] = event['pathParameters']['userId']
        
        # Mock repository to return None (user not found)
        mock_user_repo.get_item.return_value = None
        
        # Property: Non-existent user should return 404
        response = get_user_handler(event, None)
        
        self.assertEqual(response['statusCode'], 404, 
                        "Non-existent user should return 404")
        
        body_data = json.loads(response['body'])
        self.assertFalse(body_data['success'], 
                        "Not found response should have success=false")
        self.assertIn('error', body_data, 
                     "Not found response should include error message")


def run_user_management_property_tests():
    """Run property-based tests for user management endpoints"""
    print("🧪 Running Property-Based Tests for User Management Endpoints")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 5: User Management Endpoints Availability")
    print("**Validates: Requirements 4.1-4.5**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestUserManagementEndpointsProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All user management endpoint property-based tests passed!")
        print("✅ User Management Endpoints Availability properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant endpoints verified")
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
    success = run_user_management_property_tests()
    exit(0 if success else 1)
