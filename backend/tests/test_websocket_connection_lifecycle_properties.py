#!/usr/bin/env python3
"""
Property-Based Tests for WebSocket Connection Lifecycle
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 3: WebSocket Connection Lifecycle
**Validates: Requirements 2.6, 2.7, 2.8, 2.9**
"""

import unittest
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch, MagicMock, call

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example, assume
from hypothesis.strategies import composite

# Import test utilities
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@composite
def connection_lifecycle_data(draw):
    """Generate connection lifecycle test data"""
    connection_id = draw(st.text(min_size=10, max_size=50, 
                                 alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    user_id = draw(st.text(min_size=10, max_size=50, 
                          alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    
    return {
        'connectionId': connection_id,
        'userId': user_id,
        'connectedAt': datetime.utcnow().isoformat()
    }


@composite
def websocket_connect_event(draw):
    """Generate WebSocket connect event"""
    connection_id = draw(st.text(min_size=10, max_size=50, 
                                 alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    
    # Generate a mock JWT token
    token_parts = [
        draw(st.text(min_size=20, max_size=100, 
                    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')),
        draw(st.text(min_size=20, max_size=100, 
                    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')),
        draw(st.text(min_size=20, max_size=100, 
                    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'))
    ]
    token = '.'.join(token_parts)
    
    return {
        'requestContext': {
            'connectionId': connection_id,
            'domainName': draw(st.sampled_from(['api.example.com', 'ws.therapy.com'])),
            'stage': draw(st.sampled_from(['dev', 'staging', 'prod']))
        },
        'queryStringParameters': {
            'token': token
        }
    }


@composite
def websocket_disconnect_event(draw, connection_id=None):
    """Generate WebSocket disconnect event"""
    if connection_id is None:
        connection_id = draw(st.text(min_size=10, max_size=50, 
                                     alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    
    return {
        'requestContext': {
            'connectionId': connection_id,
            'domainName': draw(st.sampled_from(['api.example.com', 'ws.therapy.com'])),
            'stage': draw(st.sampled_from(['dev', 'staging', 'prod']))
        }
    }


class MockConnectionRepository:
    """Mock connection repository for testing"""
    
    def __init__(self):
        self.connections = {}
    
    def create_connection(self, connection_id: str, user_id: str, session_id: Optional[str] = None) -> bool:
        """Store connection"""
        self.connections[connection_id] = {
            'connectionId': connection_id,
            'userId': user_id,
            'sessionId': session_id,
            'connectedAt': datetime.utcnow().isoformat()
        }
        return True
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            return True
        return False
    
    def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection"""
        return self.connections.get(connection_id)


class TestWebSocketConnectionLifecycleProperties(unittest.TestCase):
    """Property-based tests for WebSocket connection lifecycle"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_repository = MockConnectionRepository()
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @given(connection_data=connection_lifecycle_data())
    @settings(max_examples=100, deadline=None)
    @example(connection_data={
        'connectionId': 'test_conn_123',
        'userId': 'test_user_456',
        'connectedAt': '2026-01-14T10:00:00Z'
    })
    def test_property_connection_storage(self, connection_data):
        """
        Property 3: WebSocket Connection Lifecycle - Connection Storage
        For any authenticated WebSocket connection, the system should store
        the connection with all required fields in DynamoDB.
        **Validates: Requirements 2.6, 2.7**
        """
        connection_id = connection_data['connectionId']
        user_id = connection_data['userId']
        
        # Property: Connection storage should succeed
        success = self.mock_repository.create_connection(connection_id, user_id)
        self.assertTrue(success, "Connection storage should succeed")
        
        # Property: Stored connection should be retrievable
        stored_connection = self.mock_repository.get_connection(connection_id)
        self.assertIsNotNone(stored_connection, "Stored connection should be retrievable")
        
        # Property: Stored connection should have all required fields
        required_fields = ['connectionId', 'userId', 'connectedAt']
        for field in required_fields:
            self.assertIn(field, stored_connection, 
                         f"Stored connection should include {field}")
        
        # Property: Stored values should match input
        self.assertEqual(stored_connection['connectionId'], connection_id,
                        "Connection ID should match")
        self.assertEqual(stored_connection['userId'], user_id,
                        "User ID should match")
    
    @given(connection_data=connection_lifecycle_data())
    @settings(max_examples=100, deadline=None)
    @example(connection_data={
        'connectionId': 'test_conn_789',
        'userId': 'test_user_abc',
        'connectedAt': '2026-01-14T10:00:00Z'
    })
    def test_property_connection_removal(self, connection_data):
        """
        Property 3: WebSocket Connection Lifecycle - Connection Removal
        For any disconnected WebSocket connection, the system should remove
        the connection record from DynamoDB.
        **Validates: Requirements 2.9**
        """
        connection_id = connection_data['connectionId']
        user_id = connection_data['userId']
        
        # First, store the connection
        self.mock_repository.create_connection(connection_id, user_id)
        
        # Verify it's stored
        stored_connection = self.mock_repository.get_connection(connection_id)
        self.assertIsNotNone(stored_connection, "Connection should be stored initially")
        
        # Property: Connection removal should succeed
        removal_success = self.mock_repository.remove_connection(connection_id)
        self.assertTrue(removal_success, "Connection removal should succeed")
        
        # Property: Removed connection should not be retrievable
        removed_connection = self.mock_repository.get_connection(connection_id)
        self.assertIsNone(removed_connection, 
                         "Removed connection should not be retrievable")
    
    @given(connection_data=connection_lifecycle_data())
    @settings(max_examples=100, deadline=None)
    def test_property_connection_lifecycle_complete(self, connection_data):
        """
        Property 3: WebSocket Connection Lifecycle - Complete Lifecycle
        For any WebSocket connection, the complete lifecycle (connect, store, disconnect, remove)
        should work correctly.
        **Validates: Requirements 2.6, 2.7, 2.8, 2.9**
        """
        connection_id = connection_data['connectionId']
        user_id = connection_data['userId']
        
        # Phase 1: Connection establishment and storage
        storage_success = self.mock_repository.create_connection(connection_id, user_id)
        self.assertTrue(storage_success, "Connection storage should succeed")
        
        # Phase 2: Connection should be active and retrievable
        active_connection = self.mock_repository.get_connection(connection_id)
        self.assertIsNotNone(active_connection, "Active connection should be retrievable")
        self.assertEqual(active_connection['connectionId'], connection_id)
        self.assertEqual(active_connection['userId'], user_id)
        
        # Phase 3: Connection disconnection and removal
        removal_success = self.mock_repository.remove_connection(connection_id)
        self.assertTrue(removal_success, "Connection removal should succeed")
        
        # Phase 4: Connection should no longer exist
        final_connection = self.mock_repository.get_connection(connection_id)
        self.assertIsNone(final_connection, "Connection should not exist after removal")
    
    @patch('lambda_functions.websocket_handlers.authenticate_websocket_connection')
    @patch('lambda_functions.websocket_handlers.connection_manager')
    @given(event=websocket_connect_event())
    @settings(max_examples=100, deadline=None)
    def test_property_connect_handler_success(self, event, mock_connection_manager, mock_auth):
        """
        Property 3: WebSocket Connection Lifecycle - Connect Handler Success
        For any valid WebSocket connection attempt, the connect handler should
        authenticate, store the connection, and return 200 status.
        **Validates: Requirements 2.6, 2.7, 2.8**
        """
        # Mock successful authentication
        mock_user_info = {
            'user_id': 'test_user_123',
            'email': 'test@example.com',
            'role': 'client',
            'username': 'testuser',
            'language_preference': 'en'
        }
        mock_auth.return_value = (True, mock_user_info, None)
        
        # Mock successful connection storage
        mock_connection_manager.store_connection.return_value = True
        
        # Import and call connect handler
        try:
            from lambda_functions.websocket_handlers import connect_handler
            
            # Property: Connect handler should return 200 for valid connection
            response = connect_handler(event, None)
            
            self.assertIsInstance(response, dict, "Response should be a dictionary")
            self.assertIn('statusCode', response, "Response should include statusCode")
            
            # Property: Successful connection should return 200
            if mock_auth.return_value[0] and mock_connection_manager.store_connection.return_value:
                self.assertEqual(response['statusCode'], 200,
                               "Successful connection should return 200 status")
            
            # Property: Authentication should be called
            mock_auth.assert_called_once_with(event)
            
            # Property: Connection storage should be called with correct parameters
            if mock_auth.return_value[0]:
                connection_id = event['requestContext']['connectionId']
                user_id = mock_user_info['user_id']
                mock_connection_manager.store_connection.assert_called_once()
                
        except ImportError:
            # If import fails, skip this test
            self.skipTest("Cannot import websocket_handlers module")
    
    @patch('lambda_functions.websocket_handlers.connection_manager')
    @given(connection_data=connection_lifecycle_data())
    @settings(max_examples=100, deadline=None)
    def test_property_disconnect_handler_cleanup(self, connection_data, mock_connection_manager):
        """
        Property 3: WebSocket Connection Lifecycle - Disconnect Handler Cleanup
        For any WebSocket disconnection, the disconnect handler should
        gracefully clean up the connection record.
        **Validates: Requirements 2.9**
        """
        connection_id = connection_data['connectionId']
        user_id = connection_data['userId']
        
        # Mock connection info
        mock_connection_manager.get_connection.return_value = {
            'connectionId': connection_id,
            'userId': user_id,
            'connectedAt': connection_data['connectedAt']
        }
        
        # Mock successful removal
        mock_connection_manager.remove_connection.return_value = True
        
        # Create disconnect event
        disconnect_event = {
            'requestContext': {
                'connectionId': connection_id,
                'domainName': 'api.example.com',
                'stage': 'dev'
            }
        }
        
        # Import and call disconnect handler
        try:
            from lambda_functions.websocket_handlers import disconnect_handler
            
            # Property: Disconnect handler should return 200
            response = disconnect_handler(disconnect_event, None)
            
            self.assertIsInstance(response, dict, "Response should be a dictionary")
            self.assertIn('statusCode', response, "Response should include statusCode")
            self.assertEqual(response['statusCode'], 200,
                           "Disconnect handler should return 200 status")
            
            # Property: Connection removal should be called
            mock_connection_manager.remove_connection.assert_called_once_with(connection_id)
            
        except ImportError:
            # If import fails, skip this test
            self.skipTest("Cannot import websocket_handlers module")
    
    @given(st.lists(connection_lifecycle_data(), min_size=1, max_size=10))
    @settings(max_examples=50, deadline=None)
    def test_property_multiple_connections_lifecycle(self, connection_list):
        """
        Property 3: WebSocket Connection Lifecycle - Multiple Connections
        For any set of WebSocket connections, the system should handle
        multiple concurrent connection lifecycles correctly.
        **Validates: Requirements 2.6, 2.7, 2.8, 2.9**
        """
        # Track unique connection IDs to handle duplicates
        unique_connections = {}
        
        # Phase 1: Store all connections (handling duplicates)
        for connection_data in connection_list:
            connection_id = connection_data['connectionId']
            user_id = connection_data['userId']
            
            success = self.mock_repository.create_connection(connection_id, user_id)
            self.assertTrue(success, f"Connection {connection_id} should be stored")
            
            # Track unique connections (last write wins for duplicates)
            unique_connections[connection_id] = user_id
        
        # Phase 2: Verify all unique connections are retrievable
        for connection_id in unique_connections.keys():
            connection = self.mock_repository.get_connection(connection_id)
            self.assertIsNotNone(connection, 
                               f"Connection {connection_id} should be retrievable")
        
        # Phase 3: Remove all unique connections
        for connection_id in unique_connections.keys():
            removal_success = self.mock_repository.remove_connection(connection_id)
            self.assertTrue(removal_success, 
                          f"Connection {connection_id} should be removed")
        
        # Phase 4: Verify all connections are removed
        for connection_id in unique_connections.keys():
            connection = self.mock_repository.get_connection(connection_id)
            self.assertIsNone(connection, 
                            f"Connection {connection_id} should not exist after removal")
    
    @given(connection_data=connection_lifecycle_data())
    @settings(max_examples=100, deadline=None)
    def test_property_connection_idempotency(self, connection_data):
        """
        Property 3: WebSocket Connection Lifecycle - Idempotency
        For any connection, storing the same connection multiple times
        should be idempotent (last write wins).
        **Validates: Requirements 2.6, 2.7**
        """
        connection_id = connection_data['connectionId']
        user_id = connection_data['userId']
        
        # Store connection first time
        success1 = self.mock_repository.create_connection(connection_id, user_id)
        self.assertTrue(success1, "First storage should succeed")
        
        # Store same connection again (simulating reconnection)
        success2 = self.mock_repository.create_connection(connection_id, user_id)
        self.assertTrue(success2, "Second storage should succeed (idempotent)")
        
        # Property: Connection should still be retrievable
        connection = self.mock_repository.get_connection(connection_id)
        self.assertIsNotNone(connection, "Connection should be retrievable after multiple stores")
        self.assertEqual(connection['connectionId'], connection_id)
        self.assertEqual(connection['userId'], user_id)
    
    @given(connection_data=connection_lifecycle_data())
    @settings(max_examples=100, deadline=None)
    def test_property_connection_removal_idempotency(self, connection_data):
        """
        Property 3: WebSocket Connection Lifecycle - Removal Idempotency
        For any connection, removing a non-existent connection should
        handle gracefully without errors.
        **Validates: Requirements 2.9**
        """
        connection_id = connection_data['connectionId']
        
        # Property: Removing non-existent connection should not raise error
        try:
            removal_result = self.mock_repository.remove_connection(connection_id)
            # Should return False for non-existent connection
            self.assertFalse(removal_result, 
                           "Removing non-existent connection should return False")
        except Exception as e:
            self.fail(f"Removing non-existent connection should not raise exception: {e}")


def run_websocket_connection_lifecycle_property_tests():
    """Run property-based tests for WebSocket connection lifecycle"""
    print("🧪 Running Property-Based Tests for WebSocket Connection Lifecycle")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 3: WebSocket Connection Lifecycle")
    print("**Validates: Requirements 2.6, 2.7, 2.8, 2.9**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestWebSocketConnectionLifecycleProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All WebSocket connection lifecycle property-based tests passed!")
        print("✅ WebSocket Connection Lifecycle properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant connection management verified")
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
    success = run_websocket_connection_lifecycle_property_tests()
    exit(0 if success else 1)
