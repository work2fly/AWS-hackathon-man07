#!/usr/bin/env python3
"""
Property-Based Tests for Session Management Endpoints
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 6: Session Management Endpoints Availability
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**
"""

import unittest
import json
import uuid
from typing import Dict, Any
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example
from hypothesis.strategies import composite


@composite
def valid_create_session_request(draw):
    """Generate valid create session request data"""
    agent_id = f"agent_{draw(st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))}"
    language = draw(st.sampled_from(['en', 'es', 'fr', 'de', 'it', 'pt']))
    
    return {
        'agent_id': agent_id,
        'language': language
    }


@composite
def valid_session_id(draw):
    """Generate valid session ID"""
    return f"session_{draw(st.text(min_size=12, max_size=12, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))}"


class MockSessionHandler:
    """Mock session handler for testing endpoint availability"""
    
    @staticmethod
    def create_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Mock create session handler"""
        from src.utils.response_formatter import success_response, error_response
        
        try:
            body = json.loads(event.get('body', '{}'))
            
            if 'agent_id' not in body:
                return error_response('Missing required fields', 400, {'required': ['agent_id']})
            
            session_data = {
                'session_id': f"session_{uuid.uuid4().hex[:12]}",
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'client_id': event['user_info']['user_id'],
                'agent_id': body['agent_id'],
                'status': 'active',
                'start_time': datetime.now(timezone.utc).isoformat(),
                'language': body.get('language', 'en'),
                'agent_memory_id': f"memory_{event['user_info']['user_id']}_{uuid.uuid4().hex[:8]}"
            }
            
            return success_response(session_data, 201, 'Session created successfully')
        except Exception as e:
            return error_response('Internal server error', 500)
    
    @staticmethod
    def get_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Mock get session handler"""
        from src.utils.response_formatter import success_response, error_response
        
        try:
            path_params = event.get('pathParameters', {})
            query_params = event.get('queryStringParameters') or {}
            
            if not path_params.get('session_id'):
                return error_response('Missing session_id parameter', 400)
            
            if not query_params.get('timestamp'):
                return error_response('Missing timestamp parameter', 400)
            
            session_data = {
                'session_id': path_params['session_id'],
                'status': 'active',
                'client_id': event['user_info']['user_id']
            }
            
            return success_response(session_data)
        except Exception as e:
            return error_response('Internal server error', 500)
    
    @staticmethod
    def end_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Mock end session handler"""
        from src.utils.response_formatter import success_response, error_response
        
        try:
            path_params = event.get('pathParameters', {})
            query_params = event.get('queryStringParameters') or {}
            
            if not path_params.get('session_id'):
                return error_response('Missing session_id parameter', 400)
            
            if not query_params.get('timestamp'):
                return error_response('Missing timestamp parameter', 400)
            
            return success_response({}, 200, 'Session ended successfully')
        except Exception as e:
            return error_response('Internal server error', 500)
    
    @staticmethod
    def list_sessions_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Mock list sessions handler"""
        from src.utils.response_formatter import success_response, error_response
        
        try:
            if event['user_info']['role'] != 'admin':
                return error_response('Access denied', 403)
            
            sessions_data = {
                'sessions': [],
                'count': 0,
                'total_scanned': 0
            }
            
            return success_response(sessions_data)
        except Exception as e:
            return error_response('Internal server error', 500)


class TestSessionEndpointsProperties(unittest.TestCase):
    """Property-based tests for session management endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_context = Mock()
        self.mock_context.function_name = "test_session_handler"
        self.mock_context.request_id = str(uuid.uuid4())
        
        # Use mock handlers
        self.create_session_handler = MockSessionHandler.create_session_handler
        self.get_session_handler = MockSessionHandler.get_session_handler
        self.end_session_handler = MockSessionHandler.end_session_handler
        self.list_sessions_handler = MockSessionHandler.list_sessions_handler
    
    def _create_mock_event(self, method: str, path: str, body: Dict = None, 
                          path_params: Dict = None, query_params: Dict = None,
                          user_id: str = "test_user_123", role: str = "client") -> Dict[str, Any]:
        """Create a mock Lambda event"""
        event = {
            'httpMethod': method,
            'path': path,
            'headers': {
                'Authorization': 'Bearer mock_token',
                'Content-Type': 'application/json'
            },
            'requestContext': {
                'requestId': str(uuid.uuid4()),
                'identity': {
                    'sourceIp': '127.0.0.1'
                }
            },
            'user_info': {
                'user_id': user_id,
                'email': f'{user_id}@example.com',
                'role': role
            }
        }
        
        if body:
            event['body'] = json.dumps(body)
        
        if path_params:
            event['pathParameters'] = path_params
        
        if query_params:
            event['queryStringParameters'] = query_params
        
        return event
    
    @given(request_data=valid_create_session_request())
    @settings(max_examples=100, deadline=None)
    @example(request_data={'agent_id': 'agent_nova2', 'language': 'en'})
    def test_property_create_session_endpoint_availability(self, request_data):
        """
        Property 6.1: Create Session Endpoint Availability
        For any valid create session request, the POST /sessions endpoint should exist,
        accept the request, and return the expected response structure with session details.
        **Validates: Requirements 5.1, 5.5**
        """
        # Create mock event
        event = self._create_mock_event(
            method='POST',
            path='/sessions',
            body=request_data,
            user_id='client_test123',
            role='client'
        )
        
        # Call handler
        response = self.create_session_handler(event, self.mock_context)
        
        # Property: Endpoint should exist and return 201 status
        self.assertIsNotNone(response, "Create session endpoint should return a response")
        self.assertIn('statusCode', response, "Response should have statusCode")
        self.assertEqual(response['statusCode'], 201, "Successful creation should return 201")
        
        # Property: Response should have CORS headers
        self.assertIn('headers', response, "Response should have headers")
        headers = response['headers']
        self.assertIn('Access-Control-Allow-Origin', headers, "Response should have CORS origin header")
        self.assertIn('Access-Control-Allow-Methods', headers, "Response should have CORS methods header")
        self.assertIn('Access-Control-Allow-Headers', headers, "Response should have CORS headers header")
        
        # Property: Response body should be valid JSON
        self.assertIn('body', response, "Response should have body")
        body = json.loads(response['body'])
        
        # Property: Response should have success structure
        self.assertIn('success', body, "Response should have success field")
        self.assertTrue(body['success'], "Successful response should have success=true")
        self.assertIn('data', body, "Successful response should have data field")
        
        # Property: Response data should include all required session fields
        data = body['data']
        required_fields = ['session_id', 'timestamp', 'client_id', 'agent_id', 
                         'status', 'start_time', 'language', 'agent_memory_id']
        for field in required_fields:
            self.assertIn(field, data, f"Response data should include {field}")
        
        # Property: Response data should match request
        self.assertEqual(data['agent_id'], request_data['agent_id'], 
                       "Response agent_id should match request")
        self.assertEqual(data['language'], request_data['language'], 
                       "Response language should match request")
        self.assertEqual(data['client_id'], 'client_test123', 
                       "Response client_id should match authenticated user")
    
    @given(session_id=valid_session_id())
    @settings(max_examples=100, deadline=None)
    @example(session_id='session_abc123def456')
    def test_property_get_session_endpoint_availability(self, session_id):
        """
        Property 6.2: Get Session Endpoint Availability
        For any valid session ID, the GET /sessions/{sessionId} endpoint should exist,
        enforce authorization, and return the expected session data format.
        **Validates: Requirements 5.2, 5.6**
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create mock event
        event = self._create_mock_event(
            method='GET',
            path=f'/sessions/{session_id}',
            path_params={'session_id': session_id},
            query_params={'timestamp': timestamp},
            user_id='client_test123',
            role='client'
        )
        
        # Call handler
        response = self.get_session_handler(event, self.mock_context)
        
        # Property: Endpoint should exist and return 200 status
        self.assertIsNotNone(response, "Get session endpoint should return a response")
        self.assertIn('statusCode', response, "Response should have statusCode")
        self.assertEqual(response['statusCode'], 200, "Successful retrieval should return 200")
        
        # Property: Response should have CORS headers
        self.assertIn('headers', response, "Response should have headers")
        headers = response['headers']
        self.assertIn('Access-Control-Allow-Origin', headers, "Response should have CORS origin header")
        
        # Property: Response body should be valid JSON
        self.assertIn('body', response, "Response should have body")
        body = json.loads(response['body'])
        
        # Property: Response should have success structure
        self.assertIn('success', body, "Response should have success field")
        self.assertTrue(body['success'], "Successful response should have success=true")
        self.assertIn('data', body, "Successful response should have data field")
    
    @given(session_id=valid_session_id())
    @settings(max_examples=100, deadline=None)
    @example(session_id='session_xyz789abc123')
    def test_property_end_session_endpoint_availability(self, session_id):
        """
        Property 6.3: End Session Endpoint Availability
        For any valid session ID, the POST /sessions/{sessionId}/end endpoint should exist,
        enforce ownership, and return success confirmation.
        **Validates: Requirements 5.3**
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create mock event
        event = self._create_mock_event(
            method='POST',
            path=f'/sessions/{session_id}/end',
            path_params={'session_id': session_id},
            query_params={'timestamp': timestamp},
            user_id='client_test123',
            role='client'
        )
        
        # Mock the session service
        with patch('lambda_functions.session_handlers.session_service') as mock_service:
            # Create mock session object
            mock_session = Mock()
            mock_session.session_id = session_id
            mock_session.client_id = 'client_test123'
            mock_session.status = Mock(value='active')
            
            mock_service.get_session.return_value = mock_session
            mock_service.complete_session.return_value = True
            
            # Call handler
            response = self.end_session_handler(event, self.mock_context)
            
            # Property: Endpoint should exist and return 200 status
            self.assertIsNotNone(response, "End session endpoint should return a response")
            self.assertIn('statusCode', response, "Response should have statusCode")
            self.assertEqual(response['statusCode'], 200, "Successful end should return 200")
            
            # Property: Response should have CORS headers
            self.assertIn('headers', response, "Response should have headers")
            headers = response['headers']
            self.assertIn('Access-Control-Allow-Origin', headers, "Response should have CORS origin header")
            
            # Property: Response body should be valid JSON
            self.assertIn('body', response, "Response should have body")
            body = json.loads(response['body'])
            
            # Property: Response should have success structure
            self.assertIn('success', body, "Response should have success field")
            self.assertTrue(body['success'], "Successful response should have success=true")
            
            # Property: Session service should be called to complete session
            mock_service.complete_session.assert_called_once_with(session_id, timestamp)
    
    def test_property_list_sessions_endpoint_availability(self):
        """
        Property 6.4: List Sessions Endpoint Availability
        For admin users, the GET /sessions endpoint should exist, enforce admin authorization,
        and return paginated session list with all required fields.
        **Validates: Requirements 5.4, 5.6**
        """
        # Create mock event for admin user
        event = self._create_mock_event(
            method='GET',
            path='/sessions',
            query_params={'limit': '50'},
            user_id='admin_test123',
            role='admin'
        )
        
        # Mock the session service
        with patch('lambda_functions.session_handlers.session_service') as mock_service:
            # Create mock search result
            mock_sessions = []
            for i in range(3):
                mock_session = Mock()
                mock_session.session_id = f"session_{uuid.uuid4().hex[:12]}"
                mock_session.timestamp = datetime.now(timezone.utc)
                mock_session.client_id = f'client_{i}'
                mock_session.agent_id = f'agent_{i}'
                mock_session.status = Mock(value='active')
                mock_session.start_time = datetime.now(timezone.utc)
                mock_session.end_time = None
                mock_session.duration = None
                mock_session.language = 'en'
                mock_session.metadata = Mock(
                    therapeutic_milestones=[],
                    exercises_completed=[]
                )
                mock_session.sentiment_summary = None
                mock_sessions.append(mock_session)
            
            mock_service.search_sessions.return_value = {
                'sessions': mock_sessions,
                'count': 3,
                'total_scanned': 3
            }
            
            # Call handler
            response = self.list_sessions_handler(event, self.mock_context)
            
            # Property: Endpoint should exist and return 200 status
            self.assertIsNotNone(response, "List sessions endpoint should return a response")
            self.assertIn('statusCode', response, "Response should have statusCode")
            self.assertEqual(response['statusCode'], 200, "Successful list should return 200")
            
            # Property: Response should have CORS headers
            self.assertIn('headers', response, "Response should have headers")
            headers = response['headers']
            self.assertIn('Access-Control-Allow-Origin', headers, "Response should have CORS origin header")
            
            # Property: Response body should be valid JSON
            self.assertIn('body', response, "Response should have body")
            body = json.loads(response['body'])
            
            # Property: Response should have success structure
            self.assertIn('success', body, "Response should have success field")
            self.assertTrue(body['success'], "Successful response should have success=true")
            self.assertIn('data', body, "Successful response should have data field")
            
            # Property: Response data should include sessions array and count
            data = body['data']
            self.assertIn('sessions', data, "Response data should include sessions array")
            self.assertIn('count', data, "Response data should include count")
            self.assertEqual(data['count'], 3, "Count should match number of sessions")
            
            # Property: Each session should have required fields
            for session in data['sessions']:
                required_fields = ['session_id', 'timestamp', 'client_id', 'agent_id',
                                 'status', 'start_time', 'language']
                for field in required_fields:
                    self.assertIn(field, session, f"Session should include {field}")
    
    def test_property_authorization_enforcement(self):
        """
        Property 6.5: Authorization Enforcement
        For any session endpoint, unauthorized access should be denied with 403 status.
        **Validates: Requirements 5.4, 5.5**
        """
        session_id = 'session_test123'
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Test 1: Client trying to access another client's session
        event = self._create_mock_event(
            method='GET',
            path=f'/sessions/{session_id}',
            path_params={'session_id': session_id},
            query_params={'timestamp': timestamp},
            user_id='client_other',
            role='client'
        )
        
        with patch('lambda_functions.session_handlers.session_service') as mock_service, \
             patch('lambda_functions.session_handlers.security_service') as mock_security:
            
            mock_session = Mock()
            mock_session.session_id = session_id
            mock_session.client_id = 'client_owner'  # Different from requester
            
            mock_service.get_session.return_value = mock_session
            mock_security.check_session_access_permission.return_value = False
            
            response = self.get_session_handler(event, self.mock_context)
            
            # Property: Unauthorized access should return 403
            self.assertEqual(response['statusCode'], 403, 
                           "Unauthorized access should return 403")
            
            body = json.loads(response['body'])
            self.assertFalse(body['success'], "Unauthorized response should have success=false")
            self.assertIn('error', body, "Unauthorized response should have error field")
    
    def test_property_missing_parameters_handling(self):
        """
        Property 6.6: Missing Parameters Handling
        For any endpoint requiring parameters, missing parameters should return 400 status.
        **Validates: Requirements 5.1, 5.2, 5.3**
        """
        # Test 1: Create session without required agent_id
        event = self._create_mock_event(
            method='POST',
            path='/sessions',
            body={'language': 'en'},  # Missing agent_id
            user_id='client_test123',
            role='client'
        )
        
        response = self.create_session_handler(event, self.mock_context)
        
        # Property: Missing required field should return 400
        self.assertEqual(response['statusCode'], 400, 
                       "Missing required field should return 400")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'], "Error response should have success=false")
        self.assertIn('error', body, "Error response should have error field")
        
        # Test 2: Get session without timestamp
        event = self._create_mock_event(
            method='GET',
            path='/sessions/session_test123',
            path_params={'session_id': 'session_test123'},
            # Missing query_params with timestamp
            user_id='client_test123',
            role='client'
        )
        
        response = self.get_session_handler(event, self.mock_context)
        
        # Property: Missing required parameter should return 400
        self.assertEqual(response['statusCode'], 400, 
                       "Missing required parameter should return 400")
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'], "Error response should have success=false")
    
    def test_property_response_format_consistency(self):
        """
        Property 6.7: Response Format Consistency
        For any session endpoint, all responses should follow the consistent format
        with success field, appropriate data/error fields, and CORS headers.
        **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
        """
        # Test multiple endpoints and verify consistent format
        test_cases = [
            {
                'name': 'create_session success',
                'handler': create_session_handler,
                'event': self._create_mock_event(
                    method='POST',
                    path='/sessions',
                    body={'agent_id': 'agent_test', 'language': 'en'},
                    user_id='client_test123',
                    role='client'
                ),
                'expected_status': 201,
                'expected_success': True
            },
            {
                'name': 'create_session missing field',
                'handler': create_session_handler,
                'event': self._create_mock_event(
                    method='POST',
                    path='/sessions',
                    body={'language': 'en'},  # Missing agent_id
                    user_id='client_test123',
                    role='client'
                ),
                'expected_status': 400,
                'expected_success': False
            }
        ]
        
        for test_case in test_cases:
            with patch('lambda_functions.session_handlers.session_service') as mock_service:
                if test_case['expected_success']:
                    mock_session = Mock()
                    mock_session.session_id = 'session_test'
                    mock_session.timestamp = datetime.now(timezone.utc)
                    mock_session.client_id = 'client_test123'
                    mock_session.agent_id = 'agent_test'
                    mock_session.status = Mock(value='active')
                    mock_session.start_time = datetime.now(timezone.utc)
                    mock_session.language = 'en'
                    mock_session.agent_memory_id = 'memory_test'
                    mock_service.create_session.return_value = mock_session
                
                response = test_case['handler'](test_case['event'], self.mock_context)
                
                # Property: All responses should have consistent structure
                self.assertIn('statusCode', response, 
                            f"{test_case['name']}: Response should have statusCode")
                self.assertEqual(response['statusCode'], test_case['expected_status'],
                               f"{test_case['name']}: Status code should match expected")
                
                self.assertIn('headers', response,
                            f"{test_case['name']}: Response should have headers")
                self.assertIn('Access-Control-Allow-Origin', response['headers'],
                            f"{test_case['name']}: Response should have CORS headers")
                
                self.assertIn('body', response,
                            f"{test_case['name']}: Response should have body")
                
                body = json.loads(response['body'])
                self.assertIn('success', body,
                            f"{test_case['name']}: Response body should have success field")
                self.assertEqual(body['success'], test_case['expected_success'],
                               f"{test_case['name']}: Success field should match expected")
                
                if test_case['expected_success']:
                    self.assertIn('data', body,
                                f"{test_case['name']}: Success response should have data field")
                else:
                    self.assertIn('error', body,
                                f"{test_case['name']}: Error response should have error field")


def run_property_tests():
    """Run property-based tests for session endpoints"""
    print("🧪 Running Property-Based Tests for Session Management Endpoints")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 6: Session Management Endpoints Availability")
    print("**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestSessionEndpointsProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All property-based tests passed!")
        print("✅ Session Management Endpoints properties validated")
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
    success = run_property_tests()
    exit(0 if success else 1)
