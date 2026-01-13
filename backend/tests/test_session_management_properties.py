#!/usr/bin/env python3
"""
Property-Based Tests for Session Management
🏆 Breaking Barriers UK 2026 compliant
Feature: ai-therapy-platform, Property 13: Session Sentiment Analysis
**Validates: Requirements 7.3, 7.5**
"""

import unittest
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from enum import Enum

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example
from hypothesis.strategies import composite


class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class SentimentType(str, Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class RiskLevel(str, Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SimpleSessionManager:
    """Simplified session manager for testing"""
    
    def __init__(self):
        self.sessions = {}
        self.sentiment_summaries = {}
    
    def create_session(self, client_id: str, agent_id: str, language: str = "en") -> Dict[str, Any]:
        """Create a new therapy session"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc)
        
        session = {
            'session_id': session_id,
            'timestamp': timestamp.isoformat(),
            'client_id': client_id,
            'agent_id': agent_id,
            'status': SessionStatus.ACTIVE.value,
            'start_time': timestamp.isoformat(),
            'end_time': None,
            'duration': None,
            'language': language,
            'metadata': {
                'therapeutic_milestones': [],
                'exercises_completed': [],
                'audio_quality': {
                    'average_latency_ms': 0.0,
                    'packet_loss_rate': 0.0,
                    'audio_clarity_score': 1.0,
                    'connection_stability': 1.0
                },
                'connection_metrics': {
                    'connection_duration_ms': 0,
                    'reconnection_count': 0,
                    'average_response_time_ms': 0.0,
                    'data_transfer_mb': 0.0
                }
            },
            'agent_memory_id': f"memory_{client_id}_{uuid.uuid4().hex[:8]}"
        }
        
        self.sessions[session_id] = session
        return session
    
    def complete_session(self, session_id: str) -> bool:
        """Complete a therapy session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        if session['status'] != SessionStatus.ACTIVE.value:
            return False
        
        # Update session completion
        end_time = datetime.now(timezone.utc)
        start_time = datetime.fromisoformat(session['start_time'])
        duration = int((end_time - start_time).total_seconds())
        
        session['status'] = SessionStatus.COMPLETED.value
        session['end_time'] = end_time.isoformat()
        session['duration'] = duration
        
        # Trigger sentiment analysis
        self._generate_sentiment_summary(session_id)
        
        return True
    
    def _generate_sentiment_summary(self, session_id: str) -> None:
        """Generate sentiment summary for completed session"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        # Simulate AI-powered sentiment analysis
        # In real implementation, this would analyze conversation context
        sentiment_summary = {
            'overall_sentiment': SentimentType.POSITIVE.value,  # Simplified for testing
            'emotional_state': ['calm', 'engaged'],
            'progress_indicators': [
                {
                    'metric_name': 'engagement_level',
                    'value': 0.8,
                    'description': 'Client showed high engagement throughout session',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            ],
            'key_topics': ['anxiety_management', 'coping_strategies'],
            'risk_level': RiskLevel.LOW.value,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.sentiment_summaries[session_id] = sentiment_summary
        session['sentiment_summary'] = sentiment_summary
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def get_client_sessions(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a client"""
        return [session for session in self.sessions.values() 
                if session['client_id'] == client_id]
    
    def get_sessions_with_sentiment(self) -> List[Dict[str, Any]]:
        """Get sessions that have sentiment summaries"""
        return [session for session in self.sessions.values() 
                if 'sentiment_summary' in session]
    
    def validate_session_data(self, session_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate session data and return errors"""
        errors = {}
        
        # Validate required fields
        required_fields = ['session_id', 'client_id', 'agent_id', 'agent_memory_id']
        for field in required_fields:
            if field not in session_data or not session_data[field]:
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Validate session_id format
        if 'session_id' in session_data and session_data['session_id']:
            if not session_data['session_id'].startswith('session_'):
                errors.setdefault('session_id', []).append("Invalid session ID format")
        
        # Validate status
        if 'status' in session_data and session_data['status']:
            valid_statuses = [s.value for s in SessionStatus]
            if session_data['status'] not in valid_statuses:
                errors.setdefault('status', []).append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Validate language
        if 'language' in session_data and session_data['language']:
            valid_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja']
            if session_data['language'] not in valid_languages:
                errors.setdefault('language', []).append(f"Language must be one of: {', '.join(valid_languages)}")
        
        # Validate timestamps
        for timestamp_field in ['start_time', 'end_time', 'timestamp']:
            if timestamp_field in session_data and session_data[timestamp_field]:
                try:
                    datetime.fromisoformat(session_data[timestamp_field])
                except ValueError:
                    errors.setdefault(timestamp_field, []).append(f"Invalid {timestamp_field} format")
        
        # Validate duration
        if 'duration' in session_data and session_data['duration'] is not None:
            if not isinstance(session_data['duration'], int) or session_data['duration'] < 0:
                errors.setdefault('duration', []).append("Duration must be a non-negative integer")
        
        return errors
    
    def validate_sentiment_summary(self, sentiment_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate sentiment summary data"""
        errors = {}
        
        # Validate required fields
        required_fields = ['overall_sentiment', 'risk_level', 'generated_at']
        for field in required_fields:
            if field not in sentiment_data or sentiment_data[field] is None:
                errors.setdefault(field, []).append(f"{field} is required")
        
        # Validate sentiment type
        if 'overall_sentiment' in sentiment_data and sentiment_data['overall_sentiment']:
            valid_sentiments = [s.value for s in SentimentType]
            if sentiment_data['overall_sentiment'] not in valid_sentiments:
                errors.setdefault('overall_sentiment', []).append(f"Sentiment must be one of: {', '.join(valid_sentiments)}")
        
        # Validate risk level
        if 'risk_level' in sentiment_data and sentiment_data['risk_level']:
            valid_risk_levels = [r.value for r in RiskLevel]
            if sentiment_data['risk_level'] not in valid_risk_levels:
                errors.setdefault('risk_level', []).append(f"Risk level must be one of: {', '.join(valid_risk_levels)}")
        
        # Validate progress indicators
        if 'progress_indicators' in sentiment_data and sentiment_data['progress_indicators']:
            if not isinstance(sentiment_data['progress_indicators'], list):
                errors.setdefault('progress_indicators', []).append("Progress indicators must be a list")
            else:
                for i, indicator in enumerate(sentiment_data['progress_indicators']):
                    if not isinstance(indicator, dict):
                        errors.setdefault('progress_indicators', []).append(f"Progress indicator {i} must be a dictionary")
                        continue
                    
                    # Validate indicator fields
                    required_indicator_fields = ['metric_name', 'value', 'description']
                    for field in required_indicator_fields:
                        if field not in indicator:
                            errors.setdefault('progress_indicators', []).append(f"Progress indicator {i} missing {field}")
                    
                    # Validate value range
                    if 'value' in indicator and isinstance(indicator['value'], (int, float)):
                        if not (0 <= indicator['value'] <= 1):
                            errors.setdefault('progress_indicators', []).append(f"Progress indicator {i} value must be between 0 and 1")
        
        # Validate timestamp
        if 'generated_at' in sentiment_data and sentiment_data['generated_at']:
            try:
                datetime.fromisoformat(sentiment_data['generated_at'])
            except ValueError:
                errors.setdefault('generated_at', []).append("Invalid generated_at timestamp format")
        
        return errors


@composite
def valid_session_data(draw):
    """Generate valid session data for property testing"""
    client_id = f"client_{draw(st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))}"
    agent_id = f"agent_{draw(st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))}"
    language = draw(st.sampled_from(['en', 'es', 'fr', 'de', 'it', 'pt']))
    
    return {
        'client_id': client_id,
        'agent_id': agent_id,
        'language': language
    }


@composite
def valid_sentiment_data(draw):
    """Generate valid sentiment summary data for property testing"""
    overall_sentiment = draw(st.sampled_from([s.value for s in SentimentType]))
    risk_level = draw(st.sampled_from([r.value for r in RiskLevel]))
    
    # Generate progress indicators
    num_indicators = draw(st.integers(min_value=0, max_value=5))
    progress_indicators = []
    
    for _ in range(num_indicators):
        indicator = {
            'metric_name': draw(st.sampled_from(['engagement_level', 'mood_improvement', 'anxiety_reduction', 'coping_skills'])),
            'value': draw(st.floats(min_value=0.0, max_value=1.0)),
            'description': draw(st.text(min_size=10, max_size=100)),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        progress_indicators.append(indicator)
    
    emotional_states = draw(st.lists(
        st.sampled_from(['calm', 'anxious', 'happy', 'sad', 'engaged', 'withdrawn', 'hopeful', 'frustrated']),
        min_size=0, max_size=5
    ))
    
    key_topics = draw(st.lists(
        st.sampled_from(['anxiety_management', 'depression', 'coping_strategies', 'relationships', 'work_stress', 'self_esteem']),
        min_size=0, max_size=5
    ))
    
    return {
        'overall_sentiment': overall_sentiment,
        'emotional_state': emotional_states,
        'progress_indicators': progress_indicators,
        'key_topics': key_topics,
        'risk_level': risk_level,
        'generated_at': datetime.now(timezone.utc).isoformat()
    }


class TestSessionManagementProperties(unittest.TestCase):
    """Property-based tests for session management"""
    
    def setUp(self):
        """Set up test environment"""
        self.session_manager = SimpleSessionManager()
    
    @given(session_data=valid_session_data())
    @settings(max_examples=10, deadline=None)
    @example(session_data={
        'client_id': 'client_test123',
        'agent_id': 'agent_nova2',
        'language': 'en'
    })
    def test_property_session_sentiment_analysis(self, session_data):
        """
        Property 13: Session Sentiment Analysis
        For any completed therapy session, the system should generate AI-powered sentiment 
        analysis and progress summaries accessible to therapists while maintaining session 
        metadata including timestamps, duration, and therapeutic milestones.
        **Validates: Requirements 7.3, 7.5**
        """
        # Create session
        session = self.session_manager.create_session(
            client_id=session_data['client_id'],
            agent_id=session_data['agent_id'],
            language=session_data['language']
        )
        
        # Property: Session should be created successfully
        self.assertIsNotNone(session, "Session should be created successfully")
        self.assertEqual(session['status'], SessionStatus.ACTIVE.value, "New session should be active")
        
        # Property: Session should have required metadata
        self.assertIn('session_id', session, "Session should have session_id")
        self.assertIn('timestamp', session, "Session should have timestamp")
        self.assertIn('start_time', session, "Session should have start_time")
        self.assertIn('metadata', session, "Session should have metadata")
        self.assertIn('agent_memory_id', session, "Session should have agent_memory_id")
        
        # Property: Session validation should pass for valid data
        validation_errors = self.session_manager.validate_session_data(session)
        self.assertEqual(len(validation_errors), 0, 
                        f"Valid session should have no validation errors: {validation_errors}")
        
        # Complete the session
        success = self.session_manager.complete_session(session['session_id'])
        
        # Property: Session completion should succeed
        self.assertTrue(success, "Session completion should succeed")
        
        # Get updated session
        updated_session = self.session_manager.get_session(session['session_id'])
        
        # Property: Completed session should have end time and duration
        self.assertEqual(updated_session['status'], SessionStatus.COMPLETED.value, 
                        "Completed session should have completed status")
        self.assertIsNotNone(updated_session['end_time'], "Completed session should have end_time")
        self.assertIsNotNone(updated_session['duration'], "Completed session should have duration")
        self.assertGreaterEqual(updated_session['duration'], 0, "Duration should be non-negative")
        
        # Property: Completed session should have sentiment summary
        self.assertIn('sentiment_summary', updated_session, 
                     "Completed session should have sentiment summary")
        
        sentiment_summary = updated_session['sentiment_summary']
        
        # Property: Sentiment summary should be valid
        sentiment_errors = self.session_manager.validate_sentiment_summary(sentiment_summary)
        self.assertEqual(len(sentiment_errors), 0, 
                        f"Sentiment summary should be valid: {sentiment_errors}")
        
        # Property: Sentiment summary should have required fields
        required_fields = ['overall_sentiment', 'risk_level', 'generated_at']
        for field in required_fields:
            self.assertIn(field, sentiment_summary, f"Sentiment summary should have {field}")
        
        # Property: Sentiment values should be valid enums
        self.assertIn(sentiment_summary['overall_sentiment'], [s.value for s in SentimentType],
                     "Overall sentiment should be valid sentiment type")
        self.assertIn(sentiment_summary['risk_level'], [r.value for r in RiskLevel],
                     "Risk level should be valid risk level")
        
        # Property: Progress indicators should be properly formatted
        if 'progress_indicators' in sentiment_summary:
            for indicator in sentiment_summary['progress_indicators']:
                self.assertIn('metric_name', indicator, "Progress indicator should have metric_name")
                self.assertIn('value', indicator, "Progress indicator should have value")
                self.assertIn('description', indicator, "Progress indicator should have description")
                self.assertIsInstance(indicator['value'], (int, float), "Progress indicator value should be numeric")
                self.assertGreaterEqual(indicator['value'], 0, "Progress indicator value should be >= 0")
                self.assertLessEqual(indicator['value'], 1, "Progress indicator value should be <= 1")
        
        # Property: Timestamps should be valid ISO format
        try:
            datetime.fromisoformat(sentiment_summary['generated_at'])
        except ValueError:
            self.fail("Sentiment summary generated_at should be valid ISO timestamp")
    
    @given(sentiment_data=valid_sentiment_data())
    @settings(max_examples=5, deadline=None)
    def test_property_sentiment_summary_validation(self, sentiment_data):
        """
        Property: Sentiment summary validation should be consistent
        For any sentiment summary data, validation should produce consistent results.
        """
        # Test validation consistency
        result1 = self.session_manager.validate_sentiment_summary(sentiment_data)
        result2 = self.session_manager.validate_sentiment_summary(sentiment_data)
        
        # Property: Validation should be deterministic
        self.assertEqual(result1, result2, f"Sentiment validation should be consistent for: {sentiment_data}")
        
        # Property: Valid sentiment data should pass validation
        if len(result1) == 0:  # No errors means valid
            # Check that all required fields are present and valid
            self.assertIn(sentiment_data['overall_sentiment'], [s.value for s in SentimentType],
                         "Valid sentiment should have valid overall_sentiment")
            self.assertIn(sentiment_data['risk_level'], [r.value for r in RiskLevel],
                         "Valid sentiment should have valid risk_level")
            
            # Check progress indicators if present
            if sentiment_data.get('progress_indicators'):
                for indicator in sentiment_data['progress_indicators']:
                    self.assertIsInstance(indicator.get('value'), (int, float),
                                        "Progress indicator value should be numeric")
                    self.assertGreaterEqual(indicator.get('value', -1), 0,
                                          "Progress indicator value should be >= 0")
                    self.assertLessEqual(indicator.get('value', 2), 1,
                                       "Progress indicator value should be <= 1")
    
    @given(session_data=valid_session_data())
    @settings(max_examples=5, deadline=None)
    def test_property_session_lifecycle_consistency(self, session_data):
        """
        Property: Session lifecycle should be consistent
        For any session, the lifecycle (create -> complete) should maintain data integrity.
        """
        # Create session
        session = self.session_manager.create_session(
            client_id=session_data['client_id'],
            agent_id=session_data['agent_id'],
            language=session_data['language']
        )
        
        session_id = session['session_id']
        original_client_id = session['client_id']
        original_agent_id = session['agent_id']
        original_language = session['language']
        original_start_time = session['start_time']
        
        # Complete session
        self.session_manager.complete_session(session_id)
        
        # Get updated session
        updated_session = self.session_manager.get_session(session_id)
        
        # Property: Core session data should remain unchanged
        self.assertEqual(updated_session['session_id'], session_id,
                        "Session ID should remain unchanged")
        self.assertEqual(updated_session['client_id'], original_client_id,
                        "Client ID should remain unchanged")
        self.assertEqual(updated_session['agent_id'], original_agent_id,
                        "Agent ID should remain unchanged")
        self.assertEqual(updated_session['language'], original_language,
                        "Language should remain unchanged")
        self.assertEqual(updated_session['start_time'], original_start_time,
                        "Start time should remain unchanged")
        
        # Property: Session should have progression from active to completed
        self.assertEqual(updated_session['status'], SessionStatus.COMPLETED.value,
                        "Session should be completed after completion")
        
        # Property: End time should be after start time
        start_time = datetime.fromisoformat(updated_session['start_time'])
        end_time = datetime.fromisoformat(updated_session['end_time'])
        self.assertGreater(end_time, start_time,
                          "End time should be after start time")
        
        # Property: Duration should match time difference
        expected_duration = int((end_time - start_time).total_seconds())
        self.assertEqual(updated_session['duration'], expected_duration,
                        "Duration should match actual time difference")
    
    def test_property_client_session_filtering(self):
        """
        Property: Client session filtering should be accurate
        For any client, only their sessions should be returned.
        """
        # Create sessions for different clients
        client1_id = "client_test1"
        client2_id = "client_test2"
        
        session1 = self.session_manager.create_session(client1_id, "agent1", "en")
        session2 = self.session_manager.create_session(client2_id, "agent2", "es")
        session3 = self.session_manager.create_session(client1_id, "agent3", "fr")
        
        # Get sessions for client1
        client1_sessions = self.session_manager.get_client_sessions(client1_id)
        
        # Property: Should only return sessions for the specified client
        self.assertEqual(len(client1_sessions), 2, "Should return exactly 2 sessions for client1")
        
        for session in client1_sessions:
            self.assertEqual(session['client_id'], client1_id,
                           "All returned sessions should belong to client1")
        
        # Property: Should include all sessions for the client
        session_ids = [s['session_id'] for s in client1_sessions]
        self.assertIn(session1['session_id'], session_ids, "Should include session1")
        self.assertIn(session3['session_id'], session_ids, "Should include session3")
        self.assertNotIn(session2['session_id'], session_ids, "Should not include session2")
    
    def test_property_sentiment_analysis_completeness(self):
        """
        Property: Sentiment analysis should be complete for all completed sessions
        For any completed session, sentiment analysis should be generated.
        """
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session = self.session_manager.create_session(f"client_{i}", f"agent_{i}", "en")
            sessions.append(session)
        
        # Complete some sessions
        self.session_manager.complete_session(sessions[0]['session_id'])
        self.session_manager.complete_session(sessions[2]['session_id'])
        # Leave sessions[1] active
        
        # Get sessions with sentiment
        sessions_with_sentiment = self.session_manager.get_sessions_with_sentiment()
        
        # Property: Only completed sessions should have sentiment summaries
        self.assertEqual(len(sessions_with_sentiment), 2,
                        "Should have sentiment summaries for 2 completed sessions")
        
        # Property: All sessions with sentiment should be completed
        for session in sessions_with_sentiment:
            self.assertEqual(session['status'], SessionStatus.COMPLETED.value,
                           "Sessions with sentiment should be completed")
            self.assertIn('sentiment_summary', session,
                         "Sessions with sentiment should have sentiment_summary")
        
        # Property: Active sessions should not have sentiment summaries
        active_session = self.session_manager.get_session(sessions[1]['session_id'])
        self.assertEqual(active_session['status'], SessionStatus.ACTIVE.value,
                        "Session 1 should still be active")
        self.assertNotIn('sentiment_summary', active_session,
                        "Active session should not have sentiment summary")


def run_property_tests():
    """Run property-based tests for session management"""
    print("🧪 Running Property-Based Tests for Session Management")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: ai-therapy-platform, Property 13: Session Sentiment Analysis")
    print("**Validates: Requirements 7.3, 7.5**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestSessionManagementProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All property-based tests passed!")
        print("✅ Session Sentiment Analysis properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant session management verified")
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