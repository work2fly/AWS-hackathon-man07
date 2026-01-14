#!/usr/bin/env python3
"""
Property-Based Tests for WebSocket Authentication
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 2: WebSocket Token Validation
**Validates: Requirements 2.1, 2.3, 2.5**
"""

import unittest
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from unittest.mock import Mock, patch, MagicMock

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example, assume
from hypothesis.strategies import composite

# Import WebSocket authentication components for testing
import sys
import os

# Setup path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Now import the websocket_auth module
from src.utils.websocket_auth import (
    extract_token_from_query_params,
    validate_token_against_cognito,
    extract_user_information,
    authenticate_websocket_connection
)


@composite
def websocket_event_with_token(draw):
    """Generate WebSocket event with JWT token in query parameters"""
    # Generate a mock JWT token (not a real one, just for structure testing)
    token_parts = [
        draw(st.text(min_size=20, max_size=100, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')),
        draw(st.text(min_size=20, max_size=100, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')),
        draw(st.text(min_size=20, max_size=100, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'))
    ]
    token = '.'.join(token_parts)
    
    # Create event structure
    event = {
        'requestContext': {
            'connectionId': draw(st.text(min_size=10, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')),
            'domainName': draw(st.sampled_from(['api.example.com', 'ws.therapy.com', 'localhost'])),
            'stage': draw(st.sampled_from(['dev', 'staging', 'prod']))
        },
        'queryStringParameters': {
            'token': token
        }
    }
    
    return event


@composite
def websocket_event_without_token(draw):
    """Generate WebSocket event without JWT token"""
    event = {
        'requestContext': {
            'connectionId': draw(st.text(min_size=10, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')),
            'domainName': draw(st.sampled_from(['api.example.com', 'ws.therapy.com', 'localhost'])),
            'stage': draw(st.sampled_from(['dev', 'staging', 'prod']))
        },
        'queryStringParameters': None
    }
    
    return event


@composite
def websocket_event_with_header_token(draw):
    """Generate WebSocket event with JWT token in Authorization header"""
    token_parts = [
        draw(st.text(min_size=20, max_size=100, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')),
        draw(st.text(min_size=20, max_size=100, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')),
        draw(st.text(min_size=20, max_size=100, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'))
    ]
    token = '.'.join(token_parts)
    
    event = {
        'requestContext': {
            'connectionId': draw(st.text(min_size=10, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')),
            'domainName': draw(st.sampled_from(['api.example.com', 'ws.therapy.com', 'localhost'])),
            'stage': draw(st.sampled_from(['dev', 'staging', 'prod']))
        },
        'headers': {
            'Authorization': f'Bearer {token}'
        }
    }
    
    return event


@composite
def mock_token_info(draw):
    """Generate mock token information from Cognito"""
    return {
        'valid': True,
        'username': draw(st.text(min_size=5, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_')),
        'email': f"{draw(st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz'))}@example.com",
        'role': draw(st.sampled_from(['client', 'therapist', 'admin'])),
        'language_preference': draw(st.sampled_from(['en', 'es', 'fr', 'de']))
    }


@composite
def mock_user_data(draw):
    """Generate mock user data from repository"""
    return {
        'userId': draw(st.text(min_size=10, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')),
        'email': f"{draw(st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz'))}@example.com",
        'role': draw(st.sampled_from(['client', 'therapist', 'admin'])),
        'isActive': True,
        'languagePreference': draw(st.sampled_from(['en', 'es', 'fr', 'de']))
    }


class TestWebSocketAuthenticationProperties(unittest.TestCase):
    """Property-based tests for WebSocket authentication"""
    
    def setUp(self):
        """Set up test environment"""
        pass
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @given(event=websocket_event_with_token())
    @settings(max_examples=100, deadline=None)
    @example(event={
        'requestContext': {
            'connectionId': 'test_conn_123',
            'domainName': 'api.example.com',
            'stage': 'dev'
        },
        'queryStringParameters': {
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        }
    })
    def test_property_token_extraction_from_query_params(self, event):
        """
        Property 2: WebSocket Token Validation - Token Extraction
        For any WebSocket connection attempt with a JWT token in query parameters,
        the system should correctly extract the token.
        **Validates: Requirements 2.1**
        """
        # Property: Token extraction should return a string or None
        token = extract_token_from_query_params(event)
        
        if event.get('queryStringParameters') and event['queryStringParameters'].get('token'):
            # If token is in query params, it should be extracted
            self.assertIsNotNone(token, "Token should be extracted from query parameters")
            self.assertIsInstance(token, str, "Extracted token should be a string")
            self.assertEqual(token, event['queryStringParameters']['token'], 
                           "Extracted token should match the token in query parameters")
        else:
            # If no token in query params, check headers
            if event.get('headers') and event['headers'].get('Authorization'):
                auth_header = event['headers']['Authorization']
                if auth_header.startswith('Bearer '):
                    expected_token = auth_header.replace('Bearer ', '')
                    self.assertEqual(token, expected_token, 
                                   "Token should be extracted from Authorization header")
    
    @given(event=websocket_event_without_token())
    @settings(max_examples=100, deadline=None)
    @example(event={
        'requestContext': {
            'connectionId': 'test_conn_456',
            'domainName': 'api.example.com',
            'stage': 'dev'
        },
        'queryStringParameters': None
    })
    def test_property_token_extraction_missing_token(self, event):
        """
        Property 2: WebSocket Token Validation - Missing Token Handling
        For any WebSocket connection attempt without a JWT token,
        the system should return None.
        **Validates: Requirements 2.1**
        """
        # Property: Missing token should return None
        token = extract_token_from_query_params(event)
        
        # If no token in query params or headers, should return None
        has_query_token = (event.get('queryStringParameters') and 
                          event['queryStringParameters'].get('token'))
        has_header_token = (event.get('headers') and 
                           event['headers'].get('Authorization', '').startswith('Bearer '))
        
        if not has_query_token and not has_header_token:
            self.assertIsNone(token, "Missing token should return None")
    
    @given(event=websocket_event_with_header_token())
    @settings(max_examples=100, deadline=None)
    @example(event={
        'requestContext': {
            'connectionId': 'test_conn_789',
            'domainName': 'api.example.com',
            'stage': 'dev'
        },
        'headers': {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        }
    })
    def test_property_token_extraction_from_header(self, event):
        """
        Property 2: WebSocket Token Validation - Header Token Extraction
        For any WebSocket connection attempt with a JWT token in Authorization header,
        the system should correctly extract the token.
        **Validates: Requirements 2.1**
        """
        # Property: Token extraction from header should work
        token = extract_token_from_query_params(event)
        
        if event.get('headers') and event['headers'].get('Authorization'):
            auth_header = event['headers']['Authorization']
            if auth_header.startswith('Bearer '):
                expected_token = auth_header.replace('Bearer ', '')
                self.assertIsNotNone(token, "Token should be extracted from Authorization header")
                self.assertEqual(token, expected_token, 
                               "Extracted token should match the token in Authorization header")
    
    @patch('utils.websocket_auth.cognito_service')
    @given(token_info=mock_token_info())
    @settings(max_examples=100, deadline=None)
    def test_property_token_validation_success(self, token_info, mock_cognito):
        """
        Property 2: WebSocket Token Validation - Valid Token
        For any valid JWT token, the system should validate it against Cognito
        and return success with token information.
        **Validates: Requirements 2.3**
        """
        # Mock Cognito service to return valid token info
        mock_cognito.verify_jwt_token.return_value = token_info
        
        # Property: Valid token should return success
        test_token = 'valid.jwt.token'
        is_valid, returned_token_info, error_message = validate_token_against_cognito(test_token)
        
        self.assertTrue(is_valid, "Valid token should return True")
        self.assertIsNotNone(returned_token_info, "Valid token should return token info")
        self.assertIsNone(error_message, "Valid token should not return error message")
        
        # Property: Returned token info should match expected structure
        if returned_token_info:
            self.assertIn('username', returned_token_info, "Token info should include username")
            self.assertIn('email', returned_token_info, "Token info should include email")
            self.assertIn('role', returned_token_info, "Token info should include role")
    
    @patch('utils.websocket_auth.cognito_service')
    @settings(max_examples=100, deadline=None)
    def test_property_token_validation_invalid(self, mock_cognito):
        """
        Property 2: WebSocket Token Validation - Invalid Token
        For any invalid JWT token, the system should reject it and return
        an appropriate error message.
        **Validates: Requirements 2.3**
        """
        # Mock Cognito service to return invalid token
        mock_cognito.verify_jwt_token.return_value = {
            'valid': False,
            'error': 'Invalid token'
        }
        
        # Property: Invalid token should return failure
        test_token = 'invalid.jwt.token'
        is_valid, token_info, error_message = validate_token_against_cognito(test_token)
        
        self.assertFalse(is_valid, "Invalid token should return False")
        self.assertIsNone(token_info, "Invalid token should not return token info")
        self.assertIsNotNone(error_message, "Invalid token should return error message")
        self.assertIsInstance(error_message, str, "Error message should be a string")
    
    @patch('utils.websocket_auth.user_repository')
    @given(token_info=mock_token_info(), user_data=mock_user_data())
    @settings(max_examples=100, deadline=None)
    def test_property_user_information_extraction(self, token_info, user_data, mock_user_repo):
        """
        Property 2: WebSocket Token Validation - User Information Extraction
        For any validated token, the system should extract user information
        from the database and return it in the correct format.
        **Validates: Requirements 2.5**
        """
        # Ensure email matches between token and user data
        user_data['email'] = token_info['email']
        
        # Mock user repository to return user data
        mock_user_repo.get_user_by_email.return_value = user_data
        
        # Property: User information should be extracted successfully
        user_info = extract_user_information(token_info)
        
        self.assertIsNotNone(user_info, "User information should be extracted")
        self.assertIsInstance(user_info, dict, "User information should be a dictionary")
        
        # Property: User information should contain required fields
        required_fields = ['user_id', 'email', 'role', 'username', 'language_preference']
        for field in required_fields:
            self.assertIn(field, user_info, f"User information should include {field}")
        
        # Property: User information should match user data
        self.assertEqual(user_info['user_id'], user_data['userId'], 
                        "User ID should match")
        self.assertEqual(user_info['email'], user_data['email'], 
                        "Email should match")
        self.assertEqual(user_info['role'], user_data['role'], 
                        "Role should match")
    
    @patch('utils.websocket_auth.user_repository')
    @given(token_info=mock_token_info())
    @settings(max_examples=100, deadline=None)
    def test_property_user_information_inactive_user(self, token_info, mock_user_repo):
        """
        Property 2: WebSocket Token Validation - Inactive User Handling
        For any validated token belonging to an inactive user,
        the system should reject the connection.
        **Validates: Requirements 2.5**
        """
        # Mock user repository to return inactive user
        inactive_user_data = {
            'userId': 'inactive_user_123',
            'email': token_info['email'],
            'role': token_info['role'],
            'isActive': False,
            'languagePreference': 'en'
        }
        mock_user_repo.get_user_by_email.return_value = inactive_user_data
        
        # Property: Inactive user should return None
        user_info = extract_user_information(token_info)
        
        self.assertIsNone(user_info, "Inactive user should return None")
    
    @patch('utils.websocket_auth.user_repository')
    @given(token_info=mock_token_info())
    @settings(max_examples=100, deadline=None)
    def test_property_user_information_user_not_found(self, token_info, mock_user_repo):
        """
        Property 2: WebSocket Token Validation - User Not Found Handling
        For any validated token where the user is not found in the database,
        the system should reject the connection.
        **Validates: Requirements 2.5**
        """
        # Mock user repository to return None (user not found)
        mock_user_repo.get_user_by_email.return_value = None
        
        # Property: User not found should return None
        user_info = extract_user_information(token_info)
        
        self.assertIsNone(user_info, "User not found should return None")
    
    @patch('utils.websocket_auth.cognito_service')
    @patch('utils.websocket_auth.user_repository')
    @given(event=websocket_event_with_token(), token_info=mock_token_info(), user_data=mock_user_data())
    @settings(max_examples=100, deadline=None)
    def test_property_complete_authentication_flow_success(self, event, token_info, user_data, 
                                                          mock_user_repo, mock_cognito):
        """
        Property 2: WebSocket Token Validation - Complete Authentication Flow
        For any WebSocket connection with a valid token and active user,
        the complete authentication flow should succeed.
        **Validates: Requirements 2.1, 2.3, 2.5**
        """
        # Ensure email matches
        user_data['email'] = token_info['email']
        
        # Mock services
        mock_cognito.verify_jwt_token.return_value = token_info
        mock_user_repo.get_user_by_email.return_value = user_data
        
        # Property: Complete authentication should succeed
        is_authenticated, user_info, error_message = authenticate_websocket_connection(event)
        
        self.assertTrue(is_authenticated, "Authentication should succeed for valid token and active user")
        self.assertIsNotNone(user_info, "User information should be returned")
        self.assertIsNone(error_message, "No error message should be returned on success")
        
        # Property: User information should be complete
        if user_info:
            required_fields = ['user_id', 'email', 'role', 'username', 'language_preference']
            for field in required_fields:
                self.assertIn(field, user_info, f"User information should include {field}")
    
    @patch('utils.websocket_auth.cognito_service')
    @given(event=websocket_event_without_token())
    @settings(max_examples=100, deadline=None)
    def test_property_complete_authentication_flow_missing_token(self, event, mock_cognito):
        """
        Property 2: WebSocket Token Validation - Missing Token Flow
        For any WebSocket connection without a token,
        the authentication flow should fail with appropriate error.
        **Validates: Requirements 2.1**
        """
        # Property: Authentication should fail for missing token
        is_authenticated, user_info, error_message = authenticate_websocket_connection(event)
        
        self.assertFalse(is_authenticated, "Authentication should fail for missing token")
        self.assertIsNone(user_info, "No user information should be returned")
        self.assertIsNotNone(error_message, "Error message should be returned")
        self.assertIn('No token', error_message, "Error message should mention missing token")
    
    @patch('utils.websocket_auth.cognito_service')
    @given(event=websocket_event_with_token())
    @settings(max_examples=100, deadline=None)
    def test_property_complete_authentication_flow_invalid_token(self, event, mock_cognito):
        """
        Property 2: WebSocket Token Validation - Invalid Token Flow
        For any WebSocket connection with an invalid token,
        the authentication flow should fail with appropriate error.
        **Validates: Requirements 2.3**
        """
        # Mock Cognito to return invalid token
        mock_cognito.verify_jwt_token.return_value = {
            'valid': False,
            'error': 'Token expired'
        }
        
        # Property: Authentication should fail for invalid token
        is_authenticated, user_info, error_message = authenticate_websocket_connection(event)
        
        self.assertFalse(is_authenticated, "Authentication should fail for invalid token")
        self.assertIsNone(user_info, "No user information should be returned")
        self.assertIsNotNone(error_message, "Error message should be returned")
        self.assertIn('Authentication failed', error_message, 
                     "Error message should indicate authentication failure")


def run_websocket_auth_property_tests():
    """Run property-based tests for WebSocket authentication"""
    print("🧪 Running Property-Based Tests for WebSocket Authentication")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 2: WebSocket Token Validation")
    print("**Validates: Requirements 2.1, 2.3, 2.5**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestWebSocketAuthenticationProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All WebSocket authentication property-based tests passed!")
        print("✅ WebSocket Token Validation properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant authentication verified")
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
    success = run_websocket_auth_property_tests()
    exit(0 if success else 1)
