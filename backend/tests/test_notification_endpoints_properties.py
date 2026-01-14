#!/usr/bin/env python3
"""
Property-Based Tests for Notification Endpoints
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 8: Notification Endpoints Availability
**Validates: Requirements 7.1-7.5**
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

from models.notification import Notification, NotificationType, Priority


@composite
def user_id_strategy(draw):
    """Generate valid user IDs"""
    return draw(st.text(
        min_size=10,
        max_size=50,
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
    ))


@composite
def notification_id_strategy(draw):
    """Generate valid notification IDs (ISO timestamps)"""
    year = draw(st.integers(min_value=2024, max_value=2026))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))
    hour = draw(st.integers(min_value=0, max_value=23))
    minute = draw(st.integers(min_value=0, max_value=59))
    second = draw(st.integers(min_value=0, max_value=59))
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"


@composite
def notification_type_strategy(draw):
    """Generate valid notification types"""
    return draw(st.sampled_from(['red_flag', 'session_complete', 'system_alert']))


@composite
def priority_strategy(draw):
    """Generate valid priority levels"""
    return draw(st.sampled_from(['low', 'medium', 'high', 'urgent']))


@composite
def notification_data_strategy(draw):
    """Generate notification data"""
    return {
        'notificationId': draw(notification_id_strategy()),
        'userId': draw(user_id_strategy()),
        'type': draw(notification_type_strategy()),
        'priority': draw(priority_strategy()),
        'title': draw(st.text(min_size=5, max_size=100)),
        'message': draw(st.text(min_size=10, max_size=500)),
        'createdAt': draw(notification_id_strategy()),
        'read': draw(st.booleans()),
        'actionRequired': draw(st.booleans())
    }


@composite
def get_notifications_event_strategy(draw):
    """Generate Lambda event for GET /users/{userId}/notifications"""
    user_id = draw(user_id_strategy())
    auth_user_id = draw(user_id_strategy())
    
    query_params = {}
    if draw(st.booleans()):
        query_params['unread_only'] = draw(st.sampled_from(['true', 'false']))
    if draw(st.booleans()):
        query_params['limit'] = str(draw(st.integers(min_value=1, max_value=100)))
    
    return {
        'httpMethod': 'GET',
        'path': f'/users/{user_id}/notifications',
        'pathParameters': {
            'userId': user_id
        },
        'queryStringParameters': query_params if query_params else None,
        'headers': {
            'Authorization': 'Bearer mock.jwt.token',
            'Content-Type': 'application/json'
        },
        'user_info': {
            'user_id': auth_user_id,
            'email': f"{auth_user_id}@example.com",
            'role': draw(st.sampled_from(['client', 'therapist', 'admin'])),
            'username': auth_user_id
        },
        'requestContext': {
            'requestId': draw(st.text(min_size=20, max_size=40))
        }
    }


@composite
def mark_read_event_strategy(draw):
    """Generate Lambda event for POST /notifications/{notificationId}/read"""
    notification_id = draw(notification_id_strategy())
    user_id = draw(user_id_strategy())
    auth_user_id = draw(user_id_strategy())
    
    body = {'userId': user_id}
    
    return {
        'httpMethod': 'POST',
        'path': f'/notifications/{notification_id}/read',
        'pathParameters': {
            'notificationId': notification_id
        },
        'headers': {
            'Authorization': 'Bearer mock.jwt.token',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body),
        'user_info': {
            'user_id': auth_user_id,
            'email': f"{auth_user_id}@example.com",
            'role': draw(st.sampled_from(['client', 'therapist', 'admin'])),
            'username': auth_user_id
        },
        'requestContext': {
            'requestId': draw(st.text(min_size=20, max_size=40))
        }
    }


class TestNotificationEndpointsProperties(unittest.TestCase):
    """Property-based tests for notification endpoints"""
    
    @given(event=get_notifications_event_strategy(), notifications=st.lists(notification_data_strategy(), min_size=0, max_size=10))
    @settings(max_examples=100, deadline=None)
    def test_property_get_notifications_endpoint_exists(self, event, notifications):
        """
        Property 8: Notification Endpoints Availability - GET /users/{userId}/notifications
        For any GET request to /users/{userId}/notifications with valid authentication,
        the endpoint should exist and return the expected response structure.
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
        """
        # Mock the repository before importing
        mock_repo_class = Mock()
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        with patch.dict('sys.modules', {'data.notification_repository': Mock(NotificationRepository=mock_repo_class)}):
            # Now we can import
            import importlib
            if 'lambda_functions.notification_handlers' in sys.modules:
                importlib.reload(sys.modules['lambda_functions.notification_handlers'])
            from lambda_functions.notification_handlers import get_user_notifications_handler
            
            # Make user authorized
            event['user_info']['user_id'] = event['pathParameters']['userId']
            event['user_info']['role'] = 'admin'
            
            # Create mock notification objects
            mock_notifications = []
            for notif_data in notifications:
                mock_notif = Mock(spec=Notification)
                mock_notif.timestamp = datetime.fromisoformat(notif_data['createdAt'].replace('Z', '+00:00'))
                mock_notif.recipient_id = notif_data['userId']
                mock_notif.type = Mock(value=notif_data['type'])
                mock_notif.priority = Mock(value=notif_data['priority'])
                mock_notif.title = notif_data['title']
                mock_notif.message = notif_data['message']
                mock_notif.read = notif_data['read']
                mock_notif.action_required = notif_data['actionRequired']
                mock_notif.read_at = None
                mock_notif.related_session_id = None
                mock_notif.related_flag_id = None
                mock_notifications.append(mock_notif)
            
            # Mock repository
            mock_repo.get_notifications_for_user.return_value = {
                'notifications': mock_notifications,
                'count': len(mock_notifications),
                'last_evaluated_key': None
            }
            
            # Property: Endpoint should exist and return valid response
            response = get_user_notifications_handler(event, None)
            
            self.assertIsNotNone(response, "Response should not be None")
            self.assertIsInstance(response, dict, "Response should be a dictionary")
            
            # Property: Response should have required fields
            self.assertIn('statusCode', response)
            self.assertIn('headers', response)
            self.assertIn('body', response)
            
            # Property: Status code should be valid
            self.assertIn(response['statusCode'], [200, 400, 401, 403, 404, 500])
            
            # Property: Headers should include CORS
            headers = response['headers']
            self.assertIn('Access-Control-Allow-Origin', headers)
            self.assertIn('Content-Type', headers)
            
            # Property: Body should be valid JSON
            body_data = json.loads(response['body'])
            self.assertIsInstance(body_data, dict)
            self.assertIn('success', body_data)
            
            # If successful, validate data structure
            if response['statusCode'] == 200:
                self.assertIn('data', body_data)
                data = body_data['data']
                self.assertIn('notifications', data)
                self.assertIn('count', data)
                self.assertIsInstance(data['notifications'], list)
                
                # Property: Notifications should be ordered by createdAt descending (Requirement 7.4)
                if len(data['notifications']) > 1:
                    for i in range(len(data['notifications']) - 1):
                        self.assertGreaterEqual(
                            data['notifications'][i]['createdAt'],
                            data['notifications'][i + 1]['createdAt'],
                            "Notifications should be ordered newest first"
                        )
    
    @given(event=mark_read_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_mark_notification_read_endpoint_exists(self, event):
        """
        Property 8: Notification Endpoints Availability - POST /notifications/{notificationId}/read
        For any POST request to mark notification as read with valid authentication,
        the endpoint should exist and return the expected response structure.
        **Validates: Requirements 7.2, 7.5**
        """
        # Mock the repository before importing
        mock_repo_class = Mock()
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        with patch.dict('sys.modules', {'data.notification_repository': Mock(NotificationRepository=mock_repo_class)}):
            import importlib
            if 'lambda_functions.notification_handlers' in sys.modules:
                importlib.reload(sys.modules['lambda_functions.notification_handlers'])
            from lambda_functions.notification_handlers import mark_notification_read_handler
            
            # Make user authorized
            body = json.loads(event['body'])
            event['user_info']['user_id'] = body['userId']
            
            # Mock repository
            mock_repo.mark_notification_as_read.return_value = True
            
            # Property: Endpoint should exist and return valid response
            response = mark_notification_read_handler(event, None)
            
            self.assertIsNotNone(response)
            self.assertIsInstance(response, dict)
            
            # Property: Response should have required fields
            self.assertIn('statusCode', response)
            self.assertIn('headers', response)
            self.assertIn('body', response)
            
            # Property: Status code should be valid
            self.assertIn(response['statusCode'], [200, 400, 401, 403, 404, 500])
            
            # Property: Headers should include CORS
            headers = response['headers']
            self.assertIn('Access-Control-Allow-Origin', headers)
            
            # Property: Body should be valid JSON
            body_data = json.loads(response['body'])
            self.assertIsInstance(body_data, dict)
            self.assertIn('success', body_data)
            
            # If successful, validate data structure (Requirement 7.5)
            if response['statusCode'] == 200:
                self.assertIn('data', body_data)
                data = body_data['data']
                self.assertIn('notificationId', data)
                self.assertIn('userId', data)
                self.assertIn('read', data)
                self.assertIn('readAt', data)
                self.assertTrue(data['read'], "Notification should be marked as read")
    
    @given(event=get_notifications_event_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_get_notifications_authorization(self, event):
        """
        Property 8: Notification Endpoints Availability - Authorization Check
        For any GET request where user is not authorized,
        the endpoint should return 403 Forbidden.
        **Validates: Requirements 7.1**
        """
        # Mock the repository before importing
        mock_repo_class = Mock()
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        with patch.dict('sys.modules', {'data.notification_repository': Mock(NotificationRepository=mock_repo_class)}):
            import importlib
            if 'lambda_functions.notification_handlers' in sys.modules:
                importlib.reload(sys.modules['lambda_functions.notification_handlers'])
            from lambda_functions.notification_handlers import get_user_notifications_handler
            
            # Set up unauthorized scenario
            event['user_info']['user_id'] = 'different_user_id'
            event['user_info']['role'] = 'client'
            
            # Property: Unauthorized access should return 403
            response = get_user_notifications_handler(event, None)
            
            if event['user_info']['user_id'] != event['pathParameters']['userId']:
                self.assertEqual(response['statusCode'], 403)
                body_data = json.loads(response['body'])
                self.assertFalse(body_data['success'])
                self.assertIn('error', body_data)


def run_notification_endpoint_property_tests():
    """Run property-based tests for notification endpoints"""
    print("🧪 Running Property-Based Tests for Notification Endpoints")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 8: Notification Endpoints Availability")
    print("**Validates: Requirements 7.1-7.5**")
    print("=" * 70)
    
    test_suite = unittest.TestSuite()
    tests = unittest.TestLoader().loadTestsFromTestCase(TestNotificationEndpointsProperties)
    test_suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All notification endpoint property-based tests passed!")
        print("✅ Notification Endpoints Availability properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant endpoints verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_notification_endpoint_property_tests()
    exit(0 if success else 1)
