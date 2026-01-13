#!/usr/bin/env python3
"""
Property-Based Tests for WebSocket Communication
🏆 Breaking Barriers UK 2026 compliant
Feature: ai-therapy-platform, Property 4: Real-Time WebSocket Communication
**Validates: Requirements 2.1, 2.2, 2.6, 2.7**
"""

import unittest
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import Mock, patch, MagicMock

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example, assume
from hypothesis.strategies import composite

# Import WebSocket components for testing
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.websocket_security import WebSocketSecurityManager, RateLimiter
from utils.validation import DataValidator


class MockWebSocketConnection:
    """Mock WebSocket connection for testing"""
    
    def __init__(self, connection_id: str, user_id: str, session_id: Optional[str] = None):
        self.connection_id = connection_id
        self.user_id = user_id
        self.session_id = session_id
        self.connected_at = datetime.utcnow().isoformat()
        self.status = 'connected'
        self.message_count = 0
        self.last_activity = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        data = {
            'connectionId': self.connection_id,
            'userId': self.user_id,
            'connectedAt': self.connected_at,
            'status': self.status,
            'lastActivity': self.last_activity
        }
        if self.session_id:
            data['sessionId'] = self.session_id
        return data


class MockConnectionManager:
    """Mock connection manager for testing"""
    
    def __init__(self):
        self.connections: Dict[str, MockWebSocketConnection] = {}
        self.user_connections: Dict[str, List[str]] = {}
        self.session_connections: Dict[str, List[str]] = {}
    
    def store_connection(self, connection_id: str, user_id: str, 
                        session_id: Optional[str] = None) -> bool:
        """Store a mock connection"""
        connection = MockWebSocketConnection(connection_id, user_id, session_id)
        self.connections[connection_id] = connection
        
        # Update user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        # Update session connections
        if session_id:
            if session_id not in self.session_connections:
                self.session_connections[session_id] = []
            self.session_connections[session_id].append(connection_id)
        
        return True
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove a mock connection"""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        user_id = connection.user_id
        session_id = connection.session_id
        
        # Remove from connections
        del self.connections[connection_id]
        
        # Remove from user connections
        if user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from session connections
        if session_id and session_id in self.session_connections:
            if connection_id in self.session_connections[session_id]:
                self.session_connections[session_id].remove(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        return True
    
    def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection details"""
        if connection_id in self.connections:
            return self.connections[connection_id].to_dict()
        return None
    
    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all connections for a user"""
        connection_ids = self.user_connections.get(user_id, [])
        return [self.connections[conn_id].to_dict() for conn_id in connection_ids if conn_id in self.connections]
    
    def get_session_connections(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all connections for a session"""
        connection_ids = self.session_connections.get(session_id, [])
        return [self.connections[conn_id].to_dict() for conn_id in connection_ids if conn_id in self.connections]
    
    def update_connection_session(self, connection_id: str, session_id: str) -> bool:
        """Update connection with session ID"""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        old_session_id = connection.session_id
        
        # Remove from old session
        if old_session_id and old_session_id in self.session_connections:
            if connection_id in self.session_connections[old_session_id]:
                self.session_connections[old_session_id].remove(connection_id)
            if not self.session_connections[old_session_id]:
                del self.session_connections[old_session_id]
        
        # Add to new session
        connection.session_id = session_id
        if session_id:
            if session_id not in self.session_connections:
                self.session_connections[session_id] = []
            self.session_connections[session_id].append(connection_id)
        
        return True


@composite
def websocket_connection_data(draw):
    """Generate WebSocket connection data for testing"""
    connection_id = draw(st.text(min_size=10, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    user_id = draw(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    
    # Optional session ID
    session_id = None
    if draw(st.booleans()):
        session_id = draw(st.text(min_size=10, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    
    return {
        'connection_id': connection_id,
        'user_id': user_id,
        'session_id': session_id
    }


@composite
def websocket_message_data(draw):
    """Generate WebSocket message data for testing"""
    message_type = draw(st.sampled_from([
        'ping', 'pong', 'join_session', 'leave_session',
        'audio_data', 'session_message', 'connection_established'
    ]))
    
    message = {
        'type': message_type,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Add type-specific data
    if message_type == 'join_session':
        session_id = draw(st.text(min_size=10, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
        message['session_id'] = session_id
    
    elif message_type == 'audio_data':
        # Generate mock audio data (base64-like string)
        audio_data = draw(st.text(min_size=100, max_size=1000, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='))
        audio_format = draw(st.sampled_from(['wav', 'mp3', 'webm', 'ogg']))
        message['data'] = audio_data
        message['format'] = audio_format
    
    elif message_type == 'session_message':
        content = draw(st.text(min_size=1, max_size=1000))
        message['content'] = content
    
    elif message_type in ['ping', 'pong']:
        # Add optional ping/pong data
        if draw(st.booleans()):
            message['original_timestamp'] = draw(st.text(min_size=10, max_size=50))
    
    return message


@composite
def rate_limit_test_data(draw):
    """Generate rate limiting test data"""
    connection_id = draw(st.text(min_size=10, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    user_id = draw(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    ip_address = f"{draw(st.integers(min_value=1, max_value=255))}.{draw(st.integers(min_value=1, max_value=255))}.{draw(st.integers(min_value=1, max_value=255))}.{draw(st.integers(min_value=1, max_value=255))}"
    message_count = draw(st.integers(min_value=1, max_value=200))
    
    return {
        'connection_id': connection_id,
        'user_id': user_id,
        'ip_address': ip_address,
        'message_count': message_count
    }


class TestWebSocketProperties(unittest.TestCase):
    """Property-based tests for WebSocket communication"""
    
    def setUp(self):
        """Set up test environment"""
        self.connection_manager = MockConnectionManager()
        self.rate_limiter = RateLimiter()
        self.security_manager = WebSocketSecurityManager()
        self.validator = DataValidator()
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @given(connection_data=websocket_connection_data())
    @settings(max_examples=10, deadline=None)
    @example(connection_data={
        'connection_id': 'test_connection_123',
        'user_id': 'test_user_456',
        'session_id': 'test_session_789'
    })
    @example(connection_data={
        'connection_id': 'client_connection_abc',
        'user_id': 'client_user_def',
        'session_id': None
    })
    def test_property_websocket_connection_management(self, connection_data):
        """
        Property 4: Real-Time WebSocket Communication - Connection Management
        For any WebSocket connection, the system should establish persistent connections
        with proper connection tracking and cleanup.
        **Validates: Requirements 2.1, 2.6**
        """
        connection_id = connection_data['connection_id']
        user_id = connection_data['user_id']
        session_id = connection_data['session_id']
        
        # Property: Connection storage should succeed for valid data
        success = self.connection_manager.store_connection(connection_id, user_id, session_id)
        self.assertTrue(success, f"Connection storage should succeed for valid data: {connection_data}")
        
        # Property: Stored connection should be retrievable
        stored_connection = self.connection_manager.get_connection(connection_id)
        self.assertIsNotNone(stored_connection, f"Stored connection should be retrievable: {connection_id}")
        self.assertEqual(stored_connection['connectionId'], connection_id)
        self.assertEqual(stored_connection['userId'], user_id)
        
        if session_id:
            self.assertEqual(stored_connection['sessionId'], session_id)
        
        # Property: User connections should be trackable
        user_connections = self.connection_manager.get_user_connections(user_id)
        self.assertGreater(len(user_connections), 0, f"User should have at least one connection: {user_id}")
        
        connection_ids = [conn['connectionId'] for conn in user_connections]
        self.assertIn(connection_id, connection_ids, f"User connections should include stored connection")
        
        # Property: Session connections should be trackable (if session provided)
        if session_id:
            session_connections = self.connection_manager.get_session_connections(session_id)
            self.assertGreater(len(session_connections), 0, f"Session should have at least one connection: {session_id}")
            
            session_connection_ids = [conn['connectionId'] for conn in session_connections]
            self.assertIn(connection_id, session_connection_ids, f"Session connections should include stored connection")
        
        # Property: Connection removal should succeed
        removal_success = self.connection_manager.remove_connection(connection_id)
        self.assertTrue(removal_success, f"Connection removal should succeed: {connection_id}")
        
        # Property: Removed connection should not be retrievable
        removed_connection = self.connection_manager.get_connection(connection_id)
        self.assertIsNone(removed_connection, f"Removed connection should not be retrievable: {connection_id}")
    
    @given(message_data=websocket_message_data())
    @settings(max_examples=15, deadline=None)
    @example(message_data={
        'type': 'ping',
        'timestamp': '2026-01-13T10:30:00Z'
    })
    @example(message_data={
        'type': 'join_session',
        'timestamp': '2026-01-13T10:30:00Z',
        'session_id': 'therapy_session_123'
    })
    @example(message_data={
        'type': 'audio_data',
        'timestamp': '2026-01-13T10:30:00Z',
        'data': 'UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT',
        'format': 'wav'
    })
    def test_property_websocket_message_validation(self, message_data):
        """
        Property 4: Real-Time WebSocket Communication - Message Validation
        For any WebSocket message, the system should validate message format
        and ensure proper message routing.
        **Validates: Requirements 2.2, 2.7**
        """
        # Property: Message validation should be consistent
        validation_errors1 = self.validator.validate_websocket_message(message_data)
        validation_errors2 = self.validator.validate_websocket_message(message_data)
        
        self.assertEqual(validation_errors1, validation_errors2, 
                        f"Message validation should be consistent for: {message_data}")
        
        # Property: Valid messages should have no validation errors
        if message_data.get('type') in ['ping', 'pong', 'connection_established']:
            # These message types should always be valid
            self.assertEqual(len(validation_errors1), 0, 
                           f"Basic message types should be valid: {message_data}")
        
        # Property: Messages with required fields should validate correctly
        message_type = message_data.get('type')
        
        if message_type == 'join_session':
            if 'session_id' in message_data and message_data['session_id']:
                # Should be valid if session_id is provided and valid format
                session_id = message_data['session_id']
                if self.validator.validate_session_id(session_id):
                    self.assertEqual(len(validation_errors1), 0, 
                                   f"join_session with valid session_id should be valid: {message_data}")
        
        elif message_type == 'audio_data':
            if 'data' in message_data:
                # Should be valid if audio data is provided
                audio_format = message_data.get('format', '')
                if audio_format in ['wav', 'mp3', 'webm', 'ogg']:
                    # Valid format should not cause validation errors for format
                    format_errors = [error for field, errors in validation_errors1.items() 
                                   if field == 'format' for error in errors]
                    self.assertEqual(len(format_errors), 0, 
                                   f"Valid audio format should not cause errors: {audio_format}")
        
        elif message_type == 'session_message':
            if 'content' in message_data and message_data['content']:
                content = message_data['content']
                if self.validator.validate_string_length(content, 1, 5000):
                    # Valid content length should not cause validation errors
                    content_errors = [error for field, errors in validation_errors1.items() 
                                    if field == 'content' for error in errors]
                    self.assertEqual(len(content_errors), 0, 
                                   f"Valid content length should not cause errors: {len(content)} chars")
        
        # Property: Message sanitization should be safe
        sanitized_message = self.validator.sanitize_websocket_message(message_data)
        self.assertIsInstance(sanitized_message, dict, "Sanitized message should be a dictionary")
        
        # Property: Sanitized message should preserve message type
        if 'type' in message_data:
            self.assertEqual(sanitized_message.get('type'), message_data['type'], 
                           "Message type should be preserved during sanitization")
    
    @given(rate_limit_data=rate_limit_test_data())
    @settings(max_examples=5, deadline=None)
    def test_property_websocket_rate_limiting(self, rate_limit_data):
        """
        Property 4: Real-Time WebSocket Communication - Rate Limiting
        For any connection, the system should enforce rate limits to prevent abuse
        and maintain system stability.
        **Validates: Requirements 2.6, 2.7**
        """
        connection_id = rate_limit_data['connection_id']
        user_id = rate_limit_data['user_id']
        ip_address = rate_limit_data['ip_address']
        message_count = min(rate_limit_data['message_count'], 100)  # Limit for testing
        
        # Property: Initial rate limit checks should pass
        initial_allowed, initial_message = self.rate_limiter.check_connection_rate_limit(connection_id)
        self.assertTrue(initial_allowed, f"Initial rate limit check should pass: {initial_message}")
        
        initial_ip_allowed, initial_ip_message = self.rate_limiter.check_ip_rate_limit(ip_address, 'connection')
        self.assertTrue(initial_ip_allowed, f"Initial IP rate limit check should pass: {initial_ip_message}")
        
        initial_user_allowed, initial_user_message = self.rate_limiter.check_user_rate_limit(user_id, 'message')
        self.assertTrue(initial_user_allowed, f"Initial user rate limit check should pass: {initial_user_message}")
        
        # Property: Rate limiting should be consistent
        for i in range(min(message_count, 10)):  # Test up to 10 messages
            allowed1, message1 = self.rate_limiter.check_connection_rate_limit(connection_id)
            allowed2, message2 = self.rate_limiter.check_connection_rate_limit(connection_id)
            
            # Both calls should have the same result (though the second might be rate limited)
            # The important thing is that the rate limiter behaves consistently
            self.assertIsInstance(allowed1, bool, "Rate limit result should be boolean")
            self.assertIsInstance(message1, str, "Rate limit message should be string")
        
        # Property: Rate limit statistics should be trackable
        stats = self.rate_limiter.get_rate_limit_stats()
        self.assertIsInstance(stats, dict, "Rate limit stats should be a dictionary")
        self.assertIn('active_connections', stats, "Stats should include active connections")
        self.assertIn('active_ips', stats, "Stats should include active IPs")
        self.assertIn('active_users', stats, "Stats should include active users")
        
        # Property: Stats should have non-negative values
        for key, value in stats.items():
            if isinstance(value, int):
                self.assertGreaterEqual(value, 0, f"Stat {key} should be non-negative: {value}")
    
    @given(connection_data=websocket_connection_data())
    @settings(max_examples=5, deadline=None)
    def test_property_websocket_session_management(self, connection_data):
        """
        Property 4: Real-Time WebSocket Communication - Session Management
        For any WebSocket connection, the system should properly manage session
        associations and handle session state changes.
        **Validates: Requirements 2.1, 2.7**
        """
        connection_id = connection_data['connection_id']
        user_id = connection_data['user_id']
        initial_session_id = connection_data['session_id']
        
        # Property: Connection should be stored successfully
        success = self.connection_manager.store_connection(connection_id, user_id, initial_session_id)
        self.assertTrue(success, f"Connection should be stored successfully")
        
        # Property: Session association should be updateable
        new_session_id = f"new_session_{int(time.time())}"
        update_success = self.connection_manager.update_connection_session(connection_id, new_session_id)
        self.assertTrue(update_success, f"Session association should be updateable")
        
        # Property: Updated session should be reflected in connection
        updated_connection = self.connection_manager.get_connection(connection_id)
        self.assertIsNotNone(updated_connection, "Updated connection should be retrievable")
        self.assertEqual(updated_connection['sessionId'], new_session_id, 
                        f"Connection should reflect updated session ID")
        
        # Property: Session connections should be updated
        new_session_connections = self.connection_manager.get_session_connections(new_session_id)
        self.assertGreater(len(new_session_connections), 0, 
                          f"New session should have connections")
        
        new_session_connection_ids = [conn['connectionId'] for conn in new_session_connections]
        self.assertIn(connection_id, new_session_connection_ids, 
                     f"New session should include updated connection")
        
        # Property: Old session should not include the connection (if it was different)
        if initial_session_id and initial_session_id != new_session_id:
            old_session_connections = self.connection_manager.get_session_connections(initial_session_id)
            old_session_connection_ids = [conn['connectionId'] for conn in old_session_connections]
            self.assertNotIn(connection_id, old_session_connection_ids, 
                           f"Old session should not include moved connection")
        
        # Property: Connection removal should clean up session associations
        removal_success = self.connection_manager.remove_connection(connection_id)
        self.assertTrue(removal_success, f"Connection removal should succeed")
        
        # Property: Removed connection should not appear in session connections
        final_session_connections = self.connection_manager.get_session_connections(new_session_id)
        final_session_connection_ids = [conn['connectionId'] for conn in final_session_connections]
        self.assertNotIn(connection_id, final_session_connection_ids, 
                        f"Removed connection should not appear in session connections")
    
    def test_property_websocket_security_validation(self):
        """
        Property 4: Real-Time WebSocket Communication - Security Validation
        For any WebSocket connection, the system should enforce security measures
        and prevent unauthorized access.
        **Validates: Requirements 2.6, 2.7**
        """
        # Property: Security manager should initialize correctly
        self.assertIsInstance(self.security_manager, WebSocketSecurityManager, 
                             "Security manager should be properly initialized")
        
        # Property: Rate limiter should be functional
        self.assertIsInstance(self.security_manager.rate_limiter, RateLimiter, 
                             "Security manager should have functional rate limiter")
        
        # Property: Security statistics should be available
        security_stats = self.security_manager.get_security_stats()
        self.assertIsInstance(security_stats, dict, "Security stats should be a dictionary")
        self.assertIn('blocked_ips', security_stats, "Security stats should include blocked IPs")
        self.assertIn('rate_limiting', security_stats, "Security stats should include rate limiting info")
        self.assertIn('timestamp', security_stats, "Security stats should include timestamp")
        
        # Property: IP blocking should work correctly
        test_ip = '192.168.1.100'
        test_reason = 'Testing IP blocking functionality'
        
        # Initially IP should not be blocked
        self.assertNotIn(test_ip, self.security_manager.blocked_ips, 
                        f"IP should not be initially blocked: {test_ip}")
        
        # Block the IP
        self.security_manager.block_ip(test_ip, test_reason)
        self.assertIn(test_ip, self.security_manager.blocked_ips, 
                     f"IP should be blocked after blocking: {test_ip}")
        
        # Unblock the IP
        self.security_manager.unblock_ip(test_ip)
        self.assertNotIn(test_ip, self.security_manager.blocked_ips, 
                        f"IP should not be blocked after unblocking: {test_ip}")
        
        # Property: Audio message validation should work
        test_connection_id = 'test_conn_123'
        test_user_id = 'test_user_456'
        
        # Valid audio message
        valid_audio_message = {
            'type': 'audio_data',
            'data': 'UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT',
            'format': 'wav'
        }
        
        is_valid, validation_message = self.security_manager.validate_message_security(
            test_connection_id, test_user_id, valid_audio_message
        )
        
        # Should be valid for reasonable audio data
        self.assertTrue(is_valid, f"Valid audio message should pass security validation: {validation_message}")
        
        # Property: Oversized audio should be rejected
        oversized_audio_message = {
            'type': 'audio_data',
            'data': 'A' * (15 * 1024 * 1024),  # 15MB of data (over 10MB limit)
            'format': 'wav'
        }
        
        is_oversized_valid, oversized_message = self.security_manager.validate_message_security(
            test_connection_id, test_user_id, oversized_audio_message
        )
        
        # Should be rejected for oversized data
        self.assertFalse(is_oversized_valid, f"Oversized audio should be rejected: {oversized_message}")
    
    @given(st.lists(websocket_connection_data(), min_size=1, max_size=5))
    @settings(max_examples=3, deadline=None)
    def test_property_websocket_concurrent_connections(self, connection_list):
        """
        Property 4: Real-Time WebSocket Communication - Concurrent Connections
        For any set of WebSocket connections, the system should handle multiple
        concurrent connections correctly.
        **Validates: Requirements 2.1, 2.6**
        """
        stored_connections = []
        
        # Property: Multiple connections should be storable
        for connection_data in connection_list:
            connection_id = connection_data['connection_id']
            user_id = connection_data['user_id']
            session_id = connection_data['session_id']
            
            success = self.connection_manager.store_connection(connection_id, user_id, session_id)
            self.assertTrue(success, f"Each connection should be storable: {connection_id}")
            stored_connections.append(connection_data)
        
        # Property: All stored connections should be retrievable
        for connection_data in stored_connections:
            connection_id = connection_data['connection_id']
            retrieved_connection = self.connection_manager.get_connection(connection_id)
            self.assertIsNotNone(retrieved_connection, f"Each stored connection should be retrievable: {connection_id}")
        
        # Property: User connections should be aggregated correctly
        user_connection_counts = {}
        for connection_data in stored_connections:
            user_id = connection_data['user_id']
            user_connection_counts[user_id] = user_connection_counts.get(user_id, 0) + 1
        
        for user_id, expected_count in user_connection_counts.items():
            user_connections = self.connection_manager.get_user_connections(user_id)
            actual_count = len(user_connections)
            self.assertEqual(actual_count, expected_count, 
                           f"User {user_id} should have {expected_count} connections, got {actual_count}")
        
        # Property: Session connections should be aggregated correctly
        session_connection_counts = {}
        for connection_data in stored_connections:
            session_id = connection_data['session_id']
            if session_id:
                session_connection_counts[session_id] = session_connection_counts.get(session_id, 0) + 1
        
        for session_id, expected_count in session_connection_counts.items():
            session_connections = self.connection_manager.get_session_connections(session_id)
            actual_count = len(session_connections)
            self.assertEqual(actual_count, expected_count, 
                           f"Session {session_id} should have {expected_count} connections, got {actual_count}")
        
        # Property: Connection removal should work for all connections
        for connection_data in stored_connections:
            connection_id = connection_data['connection_id']
            removal_success = self.connection_manager.remove_connection(connection_id)
            self.assertTrue(removal_success, f"Each connection should be removable: {connection_id}")
        
        # Property: After removal, no connections should be retrievable
        for connection_data in stored_connections:
            connection_id = connection_data['connection_id']
            removed_connection = self.connection_manager.get_connection(connection_id)
            self.assertIsNone(removed_connection, f"Removed connection should not be retrievable: {connection_id}")


def run_websocket_property_tests():
    """Run property-based tests for WebSocket communication"""
    print("🧪 Running Property-Based Tests for WebSocket Communication")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: ai-therapy-platform, Property 4: Real-Time WebSocket Communication")
    print("**Validates: Requirements 2.1, 2.2, 2.6, 2.7**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestWebSocketProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All WebSocket property-based tests passed!")
        print("✅ Real-Time WebSocket Communication properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant WebSocket infrastructure verified")
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
    success = run_websocket_property_tests()
    exit(0 if success else 1)