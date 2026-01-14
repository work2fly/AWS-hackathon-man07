#!/usr/bin/env python3
"""
Property-Based Tests for Sentiment Analysis and Progress Tracking
🏆 Breaking Barriers UK 2026 compliant
Feature: ai-therapy-platform, Property 13: Session Sentiment Analysis
**Validates: Requirements 7.3, 7.5**
"""

import unittest
import sys
import os
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.sentiment_analysis_service import (
    SentimentAnalysisService,
    EmotionalState,
    MoodTrend
)
from src.services.progress_summarization_service import ProgressSummarizationService
from src.services.therapeutic_outcome_prediction_service import (
    TherapeuticOutcomePredictionService,
    OutcomePrediction,
    RiskCategory
)
from src.models.session import SentimentType, RiskLevel, ProgressIndicator
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Test data generators
@st.composite
def generate_message(draw, sentiment_bias=None):
    """Generate a conversation message with optional sentiment bias"""
    positive_words = ['happy', 'better', 'hopeful', 'grateful', 'progress', 'improved', 'calm', 'confident']
    negative_words = ['sad', 'anxious', 'worried', 'depressed', 'hopeless', 'stressed', 'overwhelmed', 'frustrated']
    neutral_words = ['okay', 'fine', 'normal', 'usual', 'same', 'alright', 'managing']
    
    base_phrases = [
        "I've been feeling",
        "Today I am",
        "I feel",
        "Things have been",
        "I'm experiencing"
    ]
    
    base = draw(st.sampled_from(base_phrases))
    
    if sentiment_bias == 'positive':
        word = draw(st.sampled_from(positive_words))
    elif sentiment_bias == 'negative':
        word = draw(st.sampled_from(negative_words))
    elif sentiment_bias == 'neutral':
        word = draw(st.sampled_from(neutral_words))
    else:
        # Random sentiment
        all_words = positive_words + negative_words + neutral_words
        word = draw(st.sampled_from(all_words))
    
    return f"{base} {word}."


@st.composite
def generate_conversation_messages(draw, min_messages=3, max_messages=20):
    """Generate a list of conversation messages"""
    message_count = draw(st.integers(min_value=min_messages, max_value=max_messages))
    
    messages = []
    for i in range(message_count):
        role = 'user' if i % 2 == 0 else 'assistant'
        content = draw(generate_message())
        messages.append({
            'role': role,
            'content': content,
            'timestamp': (datetime.utcnow() - timedelta(minutes=message_count - i)).isoformat()
        })
    
    return messages


@st.composite
def generate_session_data(draw):
    """Generate session data for testing"""
    sentiments = [SentimentType.POSITIVE.value, SentimentType.NEUTRAL.value, SentimentType.NEGATIVE.value]
    
    return {
        'session_id': f"session_{draw(st.integers(min_value=1000, max_value=9999))}",
        'sentiment': draw(st.sampled_from(sentiments)),
        'message_count': draw(st.integers(min_value=1, max_value=30)),
        'milestones': draw(st.lists(
            st.sampled_from(['insight', 'commitment', 'progress', 'breakthrough', 'coping_skill']),
            min_size=0,
            max_size=5
        )),
        'topics': draw(st.lists(
            st.sampled_from(['anxiety', 'depression', 'relationships', 'work_stress', 'self_esteem']),
            min_size=1,
            max_size=5,
            unique=True
        )),
        'emotional_states': draw(st.lists(
            st.sampled_from(['calm', 'anxious', 'hopeful', 'frustrated', 'content']),
            min_size=1,
            max_size=3,
            unique=True
        )),
        'risk_level': draw(st.sampled_from([RiskLevel.LOW.value, RiskLevel.MEDIUM.value, RiskLevel.HIGH.value])),
        'timestamp': datetime.utcnow().isoformat()
    }


@st.composite
def generate_session_history(draw, min_sessions=3, max_sessions=15):
    """Generate session history for testing"""
    session_count = draw(st.integers(min_value=min_sessions, max_value=max_sessions))
    
    sessions = []
    for i in range(session_count):
        session = draw(generate_session_data())
        session['timestamp'] = (datetime.utcnow() - timedelta(days=session_count - i)).isoformat()
        sessions.append(session)
    
    return sessions


class TestSentimentAnalysisProperties(unittest.TestCase):
    """Property-based tests for sentiment analysis service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sentiment_service = SentimentAnalysisService()
        self.summarization_service = ProgressSummarizationService(self.sentiment_service)
        self.prediction_service = TherapeuticOutcomePredictionService(
            self.sentiment_service,
            self.summarization_service
        )
    
    # ========== Property 13.1: Sentiment Analysis Consistency ==========
    
    @given(message=generate_message())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sentiment_analysis_returns_valid_sentiment(self, message):
        """
        Property: For any message, sentiment analysis should return a valid sentiment type
        **Validates: Requirements 7.3**
        """
        result = self.sentiment_service.analyze_message_sentiment(message)
        
        # Property: Result must contain valid sentiment
        self.assertIn('sentiment', result)
        self.assertIn(result['sentiment'], [
            SentimentType.POSITIVE.value,
            SentimentType.NEUTRAL.value,
            SentimentType.NEGATIVE.value
        ])
        
        # Property: Confidence must be between 0 and 1
        self.assertIn('confidence', result)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
        
        # Property: Intensity must be between 0 and 1
        self.assertIn('intensity', result)
        self.assertGreaterEqual(result['intensity'], 0.0)
        self.assertLessEqual(result['intensity'], 1.0)
    
    @given(messages=generate_conversation_messages())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_conversation_sentiment_aggregation_is_consistent(self, messages):
        """
        Property: For any conversation, aggregated sentiment should be consistent with individual messages
        **Validates: Requirements 7.3**
        """
        assume(len(messages) >= 3)
        
        result = self.sentiment_service.analyze_conversation_sentiment(messages)
        
        # Property: Overall sentiment must be valid
        self.assertIn(result['overall_sentiment'], [
            SentimentType.POSITIVE.value,
            SentimentType.NEUTRAL.value,
            SentimentType.NEGATIVE.value
        ])
        
        # Property: Message count must match input
        self.assertEqual(result['message_count'], len(messages))
        
        # Property: Sentiment distribution must sum to approximately 1.0
        distribution = result['sentiment_distribution']
        total_distribution = sum(distribution.values())
        self.assertAlmostEqual(total_distribution, 1.0, places=1)

    
    # ========== Property 13.2: Emotional State Detection ==========
    
    @given(text=st.text(min_size=10, max_size=200))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_emotional_state_detection_returns_valid_states(self, text):
        """
        Property: For any text, emotional state detection should return valid emotional states
        **Validates: Requirements 7.3**
        """
        states = self.sentiment_service.detect_emotional_states(text)
        
        # Property: Must return at least one state
        self.assertGreater(len(states), 0)
        
        # Property: All states must be valid EmotionalState enums
        valid_states = set(EmotionalState)
        for state in states:
            self.assertIn(state, valid_states)
    
    @given(messages=generate_conversation_messages())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_emotional_state_summary_is_comprehensive(self, messages):
        """
        Property: For any session messages, emotional state summary should be comprehensive
        **Validates: Requirements 7.3**
        """
        assume(len(messages) >= 3)
        
        summary = self.sentiment_service.get_emotional_state_summary(messages)
        
        # Property: Summary must contain required fields
        self.assertIn('dominant_states', summary)
        self.assertIn('state_distribution', summary)
        self.assertIn('state_count', summary)
        self.assertIn('unique_states', summary)
        
        # Property: State count must be non-negative
        self.assertGreaterEqual(summary['state_count'], 0)
        
        # Property: Unique states must be <= total states
        self.assertLessEqual(summary['unique_states'], summary['state_count'])
    
    # ========== Property 13.3: Mood Pattern Recognition ==========
    
    @given(session_history=generate_session_history())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_mood_pattern_analysis_returns_valid_trend(self, session_history):
        """
        Property: For any session history, mood pattern analysis should return a valid trend
        **Validates: Requirements 7.3**
        """
        assume(len(session_history) >= 3)
        
        result = self.sentiment_service.analyze_mood_patterns(session_history)
        
        # Property: Trend must be valid
        self.assertIn(result['trend'], [
            MoodTrend.IMPROVING.value,
            MoodTrend.STABLE.value,
            MoodTrend.DECLINING.value,
            MoodTrend.FLUCTUATING.value
        ])
        
        # Property: Sessions analyzed must be <= input (due to lookback_sessions default of 10)
        self.assertLessEqual(result['sessions_analyzed'], len(session_history))
        self.assertGreater(result['sessions_analyzed'], 0)
        # If input is <= 10, all sessions should be analyzed
        if len(session_history) <= 10:
            self.assertEqual(result['sessions_analyzed'], len(session_history))
        
        # Property: Average mood score must be between -1 and 1
        if 'average_mood_score' in result:
            self.assertGreaterEqual(result['average_mood_score'], -1.0)
            self.assertLessEqual(result['average_mood_score'], 1.0)
    
    @given(session_history=generate_session_history(min_sessions=6, max_sessions=15))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_mood_cycles_detection_is_consistent(self, session_history):
        """
        Property: For any session history, detected mood cycles should be consistent
        **Validates: Requirements 7.3**
        """
        cycles = self.sentiment_service.detect_mood_cycles(session_history)
        
        # Property: All cycles must have valid types
        for cycle in cycles:
            self.assertIn('type', cycle)
            self.assertIn(cycle['type'], ['peak', 'trough'])
            
            # Property: Session index must be within bounds
            self.assertIn('session_index', cycle)
            self.assertGreaterEqual(cycle['session_index'], 0)
            self.assertLess(cycle['session_index'], len(session_history))
    
    # ========== Property 13.4: Progress Measurement ==========
    
    @given(session_history=generate_session_history(min_sessions=5, max_sessions=15))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_therapeutic_progress_indicators_are_valid(self, session_history):
        """
        Property: For any session history, progress indicators should be valid
        **Validates: Requirements 7.3, 7.5**
        """
        indicators = self.sentiment_service.measure_therapeutic_progress(session_history)
        
        # Property: All indicators must have valid values between 0 and 1
        for indicator in indicators:
            self.assertIsInstance(indicator, ProgressIndicator)
            self.assertGreaterEqual(indicator.value, 0.0)
            self.assertLessEqual(indicator.value, 1.0)
            
            # Property: Must have required fields
            self.assertIsNotNone(indicator.metric_name)
            self.assertIsNotNone(indicator.description)
            self.assertIsInstance(indicator.timestamp, datetime)
    
    @given(session_history=generate_session_history())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_progress_score_is_normalized(self, session_history):
        """
        Property: For any session history, progress score should be normalized between 0 and 1
        **Validates: Requirements 7.3, 7.5**
        """
        assume(len(session_history) >= 3)
        
        result = self.sentiment_service.calculate_progress_score(session_history)
        
        # Property: Overall score must be between 0 and 1
        self.assertGreaterEqual(result['overall_score'], 0.0)
        self.assertLessEqual(result['overall_score'], 1.0)
        
        # Property: Confidence must be between 0 and 1
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
        
        # Property: All breakdown scores must be between 0 and 1
        for metric, score in result['breakdown'].items():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    
    # ========== Property 13.5: Progress Summarization ==========
    
    @given(messages=generate_conversation_messages(min_messages=5, max_messages=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_session_summary_generation_is_complete(self, messages):
        """
        Property: For any session messages, generated summary should be complete
        **Validates: Requirements 7.3, 7.4**
        """
        session_id = "test_session_123"
        client_id = "test_client_456"
        duration = 1800  # 30 minutes
        
        summary = self.summarization_service.generate_session_summary(
            session_id,
            client_id,
            messages,
            duration
        )
        
        # Property: Summary must have all required fields
        self.assertIsNotNone(summary.overall_sentiment)
        self.assertIsInstance(summary.emotional_state, list)
        self.assertIsInstance(summary.key_topics, list)
        self.assertIsInstance(summary.progress_indicators, list)
        self.assertIsNotNone(summary.risk_level)
        self.assertIsInstance(summary.generated_at, datetime)
        
        # Property: Risk level must be valid
        self.assertIn(summary.risk_level, [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH])
    
    @given(messages=generate_conversation_messages())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_key_topic_extraction_returns_valid_topics(self, messages):
        """
        Property: For any messages, extracted topics should be valid therapeutic topics
        **Validates: Requirements 7.3**
        """
        topics = self.summarization_service.extract_key_topics(messages)
        
        # Property: Topics must be a list
        self.assertIsInstance(topics, list)
        
        # Property: All topics must be strings
        for topic in topics:
            self.assertIsInstance(topic, str)
            self.assertGreater(len(topic), 0)
    
    @given(messages=generate_conversation_messages())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_milestone_detection_returns_valid_milestones(self, messages):
        """
        Property: For any messages, detected milestones should be valid
        **Validates: Requirements 7.3**
        """
        milestones = self.summarization_service.detect_therapeutic_milestones(messages)
        
        # Property: Milestones must be a list
        self.assertIsInstance(milestones, list)
        
        # Property: All milestones must be valid types
        valid_milestone_types = {
            'insight', 'commitment', 'progress', 'breakthrough', 'coping_skill', 'goal_setting'
        }
        for milestone in milestones:
            self.assertIn(milestone, valid_milestone_types)
    
    # ========== Property 13.6: Outcome Prediction ==========
    
    @given(session_history=generate_session_history(min_sessions=5, max_sessions=15))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_outcome_prediction_returns_valid_prediction(self, session_history):
        """
        Property: For any session history, outcome prediction should be valid
        **Validates: Requirements 7.5**
        """
        client_id = "test_client_789"
        
        result = self.prediction_service.predict_therapeutic_outcome(
            client_id,
            session_history
        )
        
        # Property: Prediction must be valid
        self.assertIn(result['prediction'], [
            OutcomePrediction.EXCELLENT.value,
            OutcomePrediction.GOOD.value,
            OutcomePrediction.MODERATE.value,
            OutcomePrediction.POOR.value,
            OutcomePrediction.UNCERTAIN.value
        ])
        
        # Property: Confidence must be between 0 and 1
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
        
        # Property: Prediction score must be between 0 and 1
        self.assertGreaterEqual(result['prediction_score'], 0.0)
        self.assertLessEqual(result['prediction_score'], 1.0)
    
    @given(
        session_history=generate_session_history(min_sessions=3, max_sessions=10),
        current_topics=st.lists(
            st.sampled_from(['anxiety', 'depression', 'relationships', 'work_stress']),
            min_size=1,
            max_size=3,
            unique=True
        ),
        emotional_states=st.lists(
            st.sampled_from(['anxious', 'calm', 'hopeful', 'frustrated']),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_intervention_recommendations_are_valid(self, session_history, current_topics, emotional_states):
        """
        Property: For any client data, intervention recommendations should be valid
        **Validates: Requirements 7.5**
        """
        client_id = "test_client_101"
        
        recommendations = self.prediction_service.recommend_interventions(
            client_id,
            session_history,
            current_topics,
            emotional_states
        )
        
        # Property: Recommendations must be a list
        self.assertIsInstance(recommendations, list)
        
        # Property: Each recommendation must have required fields
        for rec in recommendations:
            self.assertIn('intervention', rec)
            self.assertIn('reason', rec)
            self.assertIn('priority', rec)
            self.assertIn(rec['priority'], ['high', 'medium', 'low'])
    
    @given(
        session_history=generate_session_history(min_sessions=3, max_sessions=10),
        current_session=generate_session_data()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_risk_assessment_returns_valid_category(self, session_history, current_session):
        """
        Property: For any session data, risk assessment should return valid category
        **Validates: Requirements 7.5**
        """
        client_id = "test_client_202"
        
        assessment = self.prediction_service.assess_comprehensive_risk(
            client_id,
            current_session,
            session_history
        )
        
        # Property: Risk category must be valid
        self.assertIn(assessment['risk_category'], [
            RiskCategory.IMMEDIATE_CRISIS.value,
            RiskCategory.HIGH_RISK.value,
            RiskCategory.MODERATE_RISK.value,
            RiskCategory.LOW_RISK.value,
            RiskCategory.MINIMAL_RISK.value
        ])
        
        # Property: Risk score must be between 0 and 1
        self.assertGreaterEqual(assessment['risk_score'], 0.0)
        self.assertLessEqual(assessment['risk_score'], 1.0)
        
        # Property: Risk factors must be a list
        self.assertIsInstance(assessment['risk_factors'], list)
        
        # Property: Recommendations must be a list
        self.assertIsInstance(assessment['recommendations'], list)
    
    # ========== Property 13.7: Privacy Compliance ==========
    
    @given(messages=generate_conversation_messages())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_therapist_summary_contains_no_transcripts(self, messages):
        """
        Property: For any session, therapist summary should contain no conversation transcripts
        **Validates: Requirements 5.2, 5.5**
        """
        session_id = "test_session_999"
        client_id = "test_client_888"
        duration = 1800
        
        # Generate sentiment summary
        sentiment_summary = self.summarization_service.generate_session_summary(
            session_id,
            client_id,
            messages,
            duration
        )
        
        # Generate therapist summary
        therapist_summary = self.summarization_service.generate_therapist_summary(
            session_id,
            client_id,
            sentiment_summary,
            duration,
            len(sentiment_summary.progress_indicators)
        )
        
        # Property: Summary must contain privacy note
        self.assertIn('privacy_note', therapist_summary)
        self.assertIn('no conversation transcripts', therapist_summary['privacy_note'].lower())
        
        # Property: Summary should not contain actual message content
        summary_text = therapist_summary.get('summary_text', '')
        for message in messages:
            content = message.get('content', '')
            # Check that exact message content is not in summary
            self.assertNotIn(content, summary_text)


if __name__ == '__main__':
    unittest.main()
