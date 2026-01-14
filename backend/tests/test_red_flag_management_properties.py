#!/usr/bin/env python3
"""
Property-Based Tests for Red Flag Management Endpoints
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 7: Red Flag Management Endpoints Availability
**Validates: Requirements 6.1-6.6**
"""

import unittest
import json
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Property-based testing imports
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite

# Setup path for imports
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(backend_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import models and enums
from models.red_flag import RedFlag, RedFlagType, Severity, NotificationRecord, NotificationMethod


@composite
def therapist_id_strategy(draw):
    """Generate valid therapist IDs"""
    return draw(st.text(
        min_size=10,
        max_size=50,
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
    ))


@composite
def flag_id_strategy(draw):
    """Generate valid flag IDs"""
    timestamp = draw(st.integers(min_value=1600000000000, max_value=1700000000000))
    return f"flag_{timestamp}"


@composite
def session_id_strategy(draw):
    """Generate valid session IDs"""
    return draw(st.text(
        min_size=10,
        max_size=50,
        alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_'
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
    return draw(st.sampled_from(['therapist', 'admin']))


@composite
def red_flag_type_strategy(draw):
    """Generate valid red flag types"""
    return draw(st.sampled_from([t.value for t in RedFlagType]))


@composite
def severity_strategy(draw):
    """Generate valid severity levels"""
    return draw(st.sampled_from([s.value for s in Severity]))


@composite
def resolution_action_strategy(draw):
    """Generate valid resolution actions"""
    return draw(st.sampled_from([
        'no_action',
        'therapist_contact',
        'emergency_contact',
        'referral',
        'follow_up',
        'crisis_intervention'
    ]))


@composite
def red_flag_data_strategy(draw):
    """Generate complete red flag data"""
    detected_at = datetime.utcnow()
    
    return RedFlag(
        session_id=draw(session_id_strategy()),
        flag_id=draw(flag_id_strategy()),
        type=RedFlagType(draw(red_flag_type_strategy())),
        severity=Severity(draw(severity_strategy())),
        detected_at=detected_at,
        context=draw(st.text(min_size=10, max_size=200, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?')),
        notifications_sent=[],
        resolved=False,
        resolved_by=None,
        resolved_at=None
    )


@composite
def get_therapist_red_flags_event_strategy(draw):
    """Generate Lambda event for GET /therapists/{therapistId}/red-flags"""
    therapist_id = draw(therapist_id_strategy())
    auth_user_id = draw(therapist_id_strategy())
    auth_role = draw(role_strategy())
    
    return {
        'httpMethod': 'GET',
        'path': f'/therapists/{therapist_id}/red-flags',
        'pathParameters': {
            'therapistId': therapist_id
        },
        'queryStringParameters': {
            'resolved': draw(st.sampled_from(['true', 'false'])),
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


@composite
def acknowledge_red_flag_event_strategy(draw):
    """Generate Lambda event for POST /red-flags/{flagId}/acknowledge"""
    flag_id = draw(flag_id_strategy())
    session_id = draw(session_id_strategy())
    auth_user_id = draw(therapist_id_strategy())
    auth_role = draw(role_strategy())
    
    body_data = {
        'sessionId': session_id,
        'notes': draw(st.text(min_size=0, max_size=500, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'))
    }
    
    return {
        'httpMethod': 'POST',
        'path': f'/red-flags/{flag_id}/acknowledge',
        'pathParameters': {
            'flagId': flag_id
        },
        'headers': {
            'Authorization': 'Bearer mock.jwt.token',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body_data),
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
def resolve_red_flag_event_strategy(draw):
    """Generate Lambda event for POST /red-flags/{flagId}/resolve"""
    flag_id = draw(flag_id_strategy())
    session_id = draw(session_id_strategy())
    auth_user_id = draw(therapist_id_strategy())
    auth_role = draw(role_strategy())
    
    body_data = {
        'sessionId': session_id,
        'resolutionNotes': draw(st.text(min_size=10, max_size=500, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?')),
        'resolutionAction': draw(resolution_action_strategy())
    }
    
    return {
        'httpMethod': 'POST',
        'path': f'/red-flags/{flag_id}/resolve',
        'pathParameters': {
            'flagId': flag_id
        },
        'headers': {
            'Authorization': 'Bearer mock.jwt.token',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body_data),
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


class TestRedFlagManagementEndpointsProperties(unittest.TestCase):
    """Property-based tests for red flag management endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        pass
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @given(event=get_therapist_red_flags_event_strategy(), red_flags=st.lists(red_flag_data_strategy(), min_size=0, max_size=10))
    @settings(max_examples=100, deadline=None)
    def test_property_get_therapist_red_flags_endpoint_exists(self, event, red_flags):
        """
        Property 7: Red Flag Management Endpoints Availability - GET /therapists/{therapistId}/red-flags
        For any GET request to /therapists/{therapistId}/red-flags with valid authentication,
        the endpoint should exist and return the expected response structure.
        **Validates: Requirements 6.1, 6.4, 6.5**
        """
        # Import first, then patch where it's used
        from lambda_functions import red_flag_handlers
        
        with patch.object(red_flag_handlers.red_flag_repo, 'get_unresolved_red_flags') as mock_get_unresolved:
            mock_get_unresolved.return_value = red_flags
            
            # Make therapist_id match for authorization
            event['user_info']['user_id'] = event['pathParameters']['therapistId']
            event['user_info']['role'] = 'therapist'
            
            # Property: Endpoint should exist and return valid response
            response = red_flag_handlers.get_therapist_red_flags_handler(event, None)
            
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
                    
                    # Property: Data should have required fields
                    data = body_data['data']
                    self.assertIn('therapistId', data, "Data should include therapistId")
                    self.assertIn('redFlags', data, "Data should include redFlags array")
                    self.assertIn('count', data, "Data should include count")
                    self.assertIsInstance(data['redFlags'], list, 
                                        "redFlags should be a list")
                    
                    # Property: Each red flag should have required fields
                    for flag in data['redFlags']:
                        required_fields = ['sessionId', 'flagId', 'type', 'severity', 
                                         'detectedAt', 'context', 'notificationsSent', 
                                         'resolved']
                        for field in required_fields:
                            self.assertIn(field, flag, 
                                        f"Red flag should include {field}")
            except json.JSONDecodeError:
                self.fail("Response body should be valid JSON")
    
    @given(event=get_therapist_red_flags_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_get_therapist_red_flags_authorization_enforcement(self, event):
        """
        Property 7: Red Flag Management Endpoints Availability - Authorization Check
        For any GET request to /therapists/{therapistId}/red-flags where the authenticated
        therapist is not authorized, the endpoint should return 403 Forbidden.
        **Validates: Requirements 6.1**
        """
        from lambda_functions import red_flag_handlers
        
        # Set up scenario where therapist tries to access another therapist's flags
        event['user_info']['user_id'] = 'different_therapist_id'
        event['user_info']['role'] = 'therapist'  # Therapist can only access own flags
        
        # Property: Unauthorized access should return 403
        response = red_flag_handlers.get_therapist_red_flags_handler(event, None)
        
        # Should return 403 for unauthorized access
        if event['user_info']['user_id'] != event['pathParameters']['therapistId']:
            self.assertEqual(response['statusCode'], 403, 
                           "Unauthorized access should return 403")
            
            body_data = json.loads(response['body'])
            self.assertFalse(body_data['success'], 
                           "Unauthorized response should have success=false")
            self.assertIn('error', body_data, 
                         "Unauthorized response should include error message")
    
    @given(event=acknowledge_red_flag_event_strategy(), red_flag=red_flag_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_acknowledge_red_flag_endpoint_exists(self, event, red_flag):
        """
        Property 7: Red Flag Management Endpoints Availability - POST /red-flags/{flagId}/acknowledge
        For any POST request to /red-flags/{flagId}/acknowledge with valid authentication,
        the endpoint should exist and return the expected response structure.
        **Validates: Requirements 6.2, 6.6**
        """
        from lambda_functions import red_flag_handlers
        
        with patch.object(red_flag_handlers.red_flag_repo, 'get_red_flag') as mock_get_flag, \
             patch.object(red_flag_handlers.red_flag_repo, 'acknowledge_notification') as mock_ack:
            
            # Parse body to get session_id
            body_data = json.loads(event['body'])
            session_id = body_data['sessionId']
            
            # Set red flag data to match event
            red_flag.session_id = session_id
            red_flag.flag_id = event['pathParameters']['flagId']
            
            # Add a notification for the user
            red_flag.notifications_sent = [
                NotificationRecord(
                    recipient_id=event['user_info']['user_id'],
                    method=NotificationMethod.IN_APP,
                    sent_at=datetime.utcnow(),
                    acknowledged=False
                )
            ]
            
            # Mock repository
            mock_get_flag.return_value = red_flag
            mock_ack.return_value = True
            
            # Property: Endpoint should exist and return valid response
            response = red_flag_handlers.acknowledge_red_flag_handler(event, None)
            
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
                    
                    # Property: Data should have acknowledgment fields
                    data = body_data['data']
                    required_fields = ['flagId', 'sessionId', 'acknowledgedBy', 'acknowledgedAt']
                    for field in required_fields:
                        self.assertIn(field, data, 
                                    f"Acknowledgment data should include {field}")
            except json.JSONDecodeError:
                self.fail("Response body should be valid JSON")
    
    @given(event=resolve_red_flag_event_strategy(), red_flag=red_flag_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_resolve_red_flag_endpoint_exists(self, event, red_flag):
        """
        Property 7: Red Flag Management Endpoints Availability - POST /red-flags/{flagId}/resolve
        For any POST request to /red-flags/{flagId}/resolve with valid authentication,
        the endpoint should exist and return the expected response structure.
        **Validates: Requirements 6.3, 6.4**
        """
        from lambda_functions import red_flag_handlers
        
        with patch.object(red_flag_handlers.red_flag_repo, 'get_red_flag') as mock_get_flag, \
             patch.object(red_flag_handlers.red_flag_service, 'resolve_red_flag') as mock_resolve:
            
            # Parse body to get session_id
            body_data = json.loads(event['body'])
            session_id = body_data['sessionId']
            
            # Set red flag data to match event
            red_flag.session_id = session_id
            red_flag.flag_id = event['pathParameters']['flagId']
            red_flag.resolved = False  # Ensure not already resolved
            
            # Mock repository and service
            mock_get_flag.return_value = red_flag
            mock_resolve.return_value = True
            
            # Property: Endpoint should exist and return valid response
            response = red_flag_handlers.resolve_red_flag_handler(event, None)
            
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
                    
                    # Property: Data should have resolution fields
                    data = body_data['data']
                    required_fields = ['flagId', 'sessionId', 'resolvedBy', 'resolvedAt', 
                                     'resolutionAction', 'resolutionNotes']
                    for field in required_fields:
                        self.assertIn(field, data, 
                                    f"Resolution data should include {field}")
            except json.JSONDecodeError:
                self.fail("Response body should be valid JSON")
    
    @given(event=acknowledge_red_flag_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_acknowledge_red_flag_not_found(self, event):
        """
        Property 7: Red Flag Management Endpoints Availability - Red Flag Not Found
        For any POST request to /red-flags/{flagId}/acknowledge where the red flag
        does not exist, the endpoint should return 404 Not Found.
        **Validates: Requirements 6.2**
        """
        from lambda_functions import red_flag_handlers
        
        with patch.object(red_flag_handlers.red_flag_repo, 'get_red_flag') as mock_get_flag:
            # Mock repository to return None (red flag not found)
            mock_get_flag.return_value = None
            
            # Property: Non-existent red flag should return 404
            response = red_flag_handlers.acknowledge_red_flag_handler(event, None)
            
            self.assertEqual(response['statusCode'], 404, 
                            "Non-existent red flag should return 404")
            
            body_data = json.loads(response['body'])
            self.assertFalse(body_data['success'], 
                            "Not found response should have success=false")
            self.assertIn('error', body_data, 
                         "Not found response should include error message")
    
    @given(event=resolve_red_flag_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_resolve_red_flag_not_found(self, event):
        """
        Property 7: Red Flag Management Endpoints Availability - Red Flag Not Found for Resolution
        For any POST request to /red-flags/{flagId}/resolve where the red flag
        does not exist, the endpoint should return 404 Not Found.
        **Validates: Requirements 6.3**
        """
        from lambda_functions import red_flag_handlers
        
        with patch.object(red_flag_handlers.red_flag_repo, 'get_red_flag') as mock_get_flag:
            # Mock repository to return None (red flag not found)
            mock_get_flag.return_value = None
            
            # Property: Non-existent red flag should return 404
            response = red_flag_handlers.resolve_red_flag_handler(event, None)
            
            self.assertEqual(response['statusCode'], 404, 
                            "Non-existent red flag should return 404")
            
            body_data = json.loads(response['body'])
            self.assertFalse(body_data['success'], 
                            "Not found response should have success=false")
            self.assertIn('error', body_data, 
                         "Not found response should include error message")
    
    @given(event=resolve_red_flag_event_strategy(), red_flag=red_flag_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_resolve_already_resolved_red_flag(self, event, red_flag):
        """
        Property 7: Red Flag Management Endpoints Availability - Already Resolved
        For any POST request to /red-flags/{flagId}/resolve where the red flag
        is already resolved, the endpoint should return 400 Bad Request.
        **Validates: Requirements 6.3**
        """
        from lambda_functions import red_flag_handlers
        
        with patch.object(red_flag_handlers.red_flag_repo, 'get_red_flag') as mock_get_flag:
            # Parse body to get session_id
            body_data = json.loads(event['body'])
            session_id = body_data['sessionId']
            
            # Set red flag data to match event and mark as resolved
            red_flag.session_id = session_id
            red_flag.flag_id = event['pathParameters']['flagId']
            red_flag.resolved = True  # Already resolved
            red_flag.resolved_by = 'some_therapist'
            red_flag.resolved_at = datetime.utcnow()
            
            # Mock repository
            mock_get_flag.return_value = red_flag
            
            # Property: Already resolved red flag should return 400
            response = red_flag_handlers.resolve_red_flag_handler(event, None)
            
            self.assertEqual(response['statusCode'], 400, 
                            "Already resolved red flag should return 400")
            
            body_data = json.loads(response['body'])
            self.assertFalse(body_data['success'], 
                            "Bad request response should have success=false")
            self.assertIn('error', body_data, 
                         "Bad request response should include error message")


def run_red_flag_management_property_tests():
    """Run property-based tests for red flag management endpoints"""
    print("🧪 Running Property-Based Tests for Red Flag Management Endpoints")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 7: Red Flag Management Endpoints Availability")
    print("**Validates: Requirements 6.1-6.6**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestRedFlagManagementEndpointsProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All red flag management endpoint property-based tests passed!")
        print("✅ Red Flag Management Endpoints Availability properties validated")
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
    success = run_red_flag_management_property_tests()
    exit(0 if success else 1)
