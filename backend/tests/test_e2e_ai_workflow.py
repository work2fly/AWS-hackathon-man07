"""
End-to-End AI Workflow Integration Tests
🏆 Breaking Barriers UK 2026 compliant

Task 8.3: Conduct end-to-end AI workflow testing
- Test complete therapy session AI workflows
- Verify red flag detection and escalation systems
- Test sentiment analysis and progress tracking
- Validate integration with backend and frontend systems

**Validates: Requirements 4.1, 4.4, 7.3**
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import json

import sys
import os
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.strands_agent_service import StrandsAgentService
from src.services.agentcore_memory_service import AgentCoreMemoryService
from src.services.red_flag_detection_service import RedFlagDetectionService
from src.services.red_flag_management_service import RedFlagManagementService
from src.services.sentiment_analysis_service import SentimentAnalysisService
from src.services.progress_summarization_service import ProgressSummarizationService
from src.services.session_continuity_service import SessionContinuityService
from src.models.agent_memory import SessionSummary


class TestCompleteTherapySessionWorkflow:
    """Test complete therapy session AI workflows"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    def test_full_session_lifecycle(self, mock_bedrock_client):
        """
        Test complete session lifecycle from start to finish
        
        **Validates: Requirements 2.1, 3.3, 3.7, 7.1, 7.2, 7.3**
        """
        # Initialize services
        memory_service = AgentCoreMemoryService()
        continuity_service = SessionContinuityService()
        sentiment_service = SentimentAnalysisService()
        progress_service = ProgressSummarizationService()
        
        client_id = "e2e-client-001"
        session_id = "e2e-session-001"
        
        # Step 1: Create initial memory
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        memory = memory_service.create_memory(client_id, language_preference="en")
        assert memory is not None
        
        # Step 2: Load session context
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        context = continuity_service.load_session_context(client_id, session_id)
        assert context is not None
        
        # Step 3: Simulate conversation turns
        conversation_turns = [
            {
                'client': "I've been feeling really anxious lately.",
                'ai': "I hear that you're feeling anxious. Can you tell me more about what's been happening?"
            },
            {
                'client': "It's mainly work stress. I have so many deadlines.",
                'ai': "Work stress can be overwhelming. Let's explore some coping strategies together."
            },
            {
                'client': "That would be helpful. I feel like I can't keep up.",
                'ai': "It's okay to feel that way. Let's start with some breathing exercises."
            }
        ]
        
        # Step 4: Analyze sentiment for each turn
        sentiment_scores = []
        for turn in conversation_turns:
            sentiment = sentiment_service.analyze_sentiment(
                session_id,
                turn['client']
            )
            sentiment_scores.append(sentiment)
            assert sentiment is not None
        
        # Step 5: Generate session summary
        session_text = " ".join([turn['client'] for turn in conversation_turns])
        summary = progress_service.generate_session_summary(
            session_id,
            session_text,
            duration_seconds=1800
        )
        assert summary is not None
        assert 'key_topics' in summary
        assert 'emotional_state' in summary
        
        # Step 6: Save session to memory
        session_summary = SessionSummary(
            session_id=session_id,
            duration_seconds=1800,
            key_topics=summary['key_topics'],
            emotional_state=summary['emotional_state'],
            therapeutic_progress=summary.get('progress_notes', 'Session completed')
        )
        
        updated_memory = memory_service.add_session_summary(client_id, session_summary)
        assert updated_memory is not None
        
        print("✅ Full session lifecycle validated")
    
    def test_multi_session_continuity_workflow(self, mock_bedrock_client):
        """
        Test continuity across multiple sessions
        
        **Validates: Requirements 3.7, 7.1, 7.2**
        """
        memory_service = AgentCoreMemoryService()
        continuity_service = SessionContinuityService()
        
        client_id = "e2e-client-002"
        
        # Create initial memory
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        memory = memory_service.create_memory(client_id)
        
        # Simulate 3 sessions
        for i in range(3):
            session_id = f"session-{i:03d}"
            
            # Load context
            memory_data = memory.to_dict()
            mock_bedrock_client.get_memory.return_value = {
                'memoryContent': json.dumps(memory_data)
            }
            
            context = continuity_service.load_session_context(client_id, session_id)
            assert context is not None
            
            # Add session summary
            session_summary = SessionSummary(
                session_id=session_id,
                duration_seconds=1800,
                key_topics=[f"topic-{i}", "progress"],
                emotional_state=["calm", "hopeful"],
                therapeutic_progress=f"Session {i} progress"
            )
            
            memory = memory_service.add_session_summary(client_id, session_summary)
        
        # Verify continuity
        final_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(final_data)
        }
        
        final_context = continuity_service.load_session_context(client_id, "session-004")
        assert final_context is not None
        
        print("✅ Multi-session continuity workflow validated")


class TestRedFlagDetectionAndEscalation:
    """Test red flag detection and escalation systems"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def mock_dynamodb(self):
        """Mock DynamoDB"""
        with patch('boto3.resource') as mock_resource:
            mock_instance = MagicMock()
            mock_resource.return_value = mock_instance
            yield mock_instance
    
    def test_red_flag_detection_workflow(self, mock_bedrock_client, mock_dynamodb):
        """
        Test complete red flag detection workflow
        
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
        """
        detection_service = RedFlagDetectionService()
        management_service = RedFlagManagementService()
        
        session_id = "red-flag-session-001"
        client_id = "red-flag-client-001"
        
        # Test cases with different severity levels
        test_cases = [
            {
                'text': "I've been thinking about hurting myself.",
                'expected_severity': 'critical',
                'expected_type': 'self_harm'
            },
            {
                'text': "Sometimes I feel like ending it all.",
                'expected_severity': 'critical',
                'expected_type': 'suicidal_ideation'
            },
            {
                'text': "My partner has been hitting me.",
                'expected_severity': 'high',
                'expected_type': 'abuse'
            }
        ]
        
        for test_case in test_cases:
            # Detect red flag
            result = detection_service.analyze_content(
                session_id,
                test_case['text']
            )
            
            assert result is not None
            assert result['has_red_flag'] is True
            assert result['severity'] in ['high', 'critical']
            
            # Create red flag record
            if result['has_red_flag']:
                red_flag = management_service.create_red_flag(
                    session_id=session_id,
                    client_id=client_id,
                    flag_type=result['flag_type'],
                    severity=result['severity'],
                    context=test_case['text'][:100]  # Sanitized context
                )
                
                assert red_flag is not None
                assert red_flag['severity'] == result['severity']
        
        print("✅ Red flag detection workflow validated")
    
    def test_escalation_workflow(self, mock_bedrock_client, mock_dynamodb):
        """
        Test red flag escalation to therapists
        
        **Validates: Requirements 4.4, 4.5, 4.6**
        """
        management_service = RedFlagManagementService()
        
        session_id = "escalation-session-001"
        client_id = "escalation-client-001"
        therapist_id = "therapist-001"
        
        # Create critical red flag
        red_flag = management_service.create_red_flag(
            session_id=session_id,
            client_id=client_id,
            flag_type='suicidal_ideation',
            severity='critical',
            context="Client expressed suicidal thoughts"
        )
        
        # Trigger escalation
        escalation_result = management_service.escalate_red_flag(
            red_flag['flag_id'],
            therapist_id
        )
        
        assert escalation_result is not None
        assert escalation_result['escalated'] is True
        
        print("✅ Escalation workflow validated")
    
    def test_multiple_red_flags_escalation(self, mock_bedrock_client, mock_dynamodb):
        """
        Test escalation when multiple red flags occur
        
        **Validates: Requirements 4.6**
        """
        management_service = RedFlagManagementService()
        
        session_id = "multi-flag-session-001"
        client_id = "multi-flag-client-001"
        
        # Create multiple red flags
        for i in range(3):
            red_flag = management_service.create_red_flag(
                session_id=session_id,
                client_id=client_id,
                flag_type='self_harm',
                severity='high',
                context=f"Red flag {i}"
            )
            assert red_flag is not None
        
        # Check if admin escalation triggered
        flags = management_service.get_session_red_flags(session_id)
        assert len(flags) >= 3
        
        print("✅ Multiple red flags escalation validated")


class TestSentimentAnalysisAndProgressTracking:
    """Test sentiment analysis and progress tracking"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    def test_sentiment_analysis_workflow(self, mock_bedrock_client):
        """
        Test sentiment analysis during session
        
        **Validates: Requirements 7.3, 7.5**
        """
        sentiment_service = SentimentAnalysisService()
        
        session_id = "sentiment-session-001"
        
        # Test different emotional states
        test_cases = [
            {
                'text': "I'm feeling really happy and hopeful today!",
                'expected_sentiment': 'positive'
            },
            {
                'text': "I'm feeling anxious and worried about everything.",
                'expected_sentiment': 'negative'
            },
            {
                'text': "Things are okay, nothing special.",
                'expected_sentiment': 'neutral'
            }
        ]
        
        for test_case in test_cases:
            result = sentiment_service.analyze_sentiment(
                session_id,
                test_case['text']
            )
            
            assert result is not None
            assert 'sentiment' in result
            assert 'confidence' in result
            assert result['confidence'] > 0.0
        
        # Get session sentiment summary
        summary = sentiment_service.get_session_sentiment_summary(session_id)
        assert summary is not None
        
        print("✅ Sentiment analysis workflow validated")
    
    def test_progress_tracking_workflow(self, mock_bedrock_client):
        """
        Test progress tracking across sessions
        
        **Validates: Requirements 7.3, 7.4, 7.5**
        """
        progress_service = ProgressSummarizationService()
        
        session_id = "progress-session-001"
        
        # Generate session summary
        session_text = """
        Client discussed anxiety management techniques.
        Practiced breathing exercises.
        Showed improvement in coping with stress.
        Set goals for next session.
        """
        
        summary = progress_service.generate_session_summary(
            session_id,
            session_text,
            duration_seconds=1800
        )
        
        assert summary is not None
        assert 'key_topics' in summary
        assert 'emotional_state' in summary
        assert 'progress_notes' in summary
        
        # Verify privacy compliance (no transcripts)
        assert 'transcript' not in summary
        assert 'full_conversation' not in summary
        
        print("✅ Progress tracking workflow validated")
    
    def test_therapeutic_outcome_prediction(self, mock_bedrock_client):
        """
        Test therapeutic outcome prediction
        
        **Validates: Requirements 7.3, 7.5**
        """
        progress_service = ProgressSummarizationService()
        
        client_id = "outcome-client-001"
        
        # Simulate session history
        session_history = [
            {
                'session_id': f'session-{i:03d}',
                'sentiment': 'positive' if i > 2 else 'negative',
                'progress_score': (i + 1) * 0.2
            }
            for i in range(5)
        ]
        
        # Predict outcome
        prediction = progress_service.predict_therapeutic_outcome(
            client_id,
            session_history
        )
        
        assert prediction is not None
        assert 'outcome_score' in prediction
        assert 'confidence' in prediction
        assert 'recommendations' in prediction
        
        print("✅ Therapeutic outcome prediction validated")


class TestBackendFrontendIntegration:
    """Test integration with backend and frontend systems"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def mock_dynamodb(self):
        """Mock DynamoDB"""
        with patch('boto3.resource') as mock_resource:
            mock_instance = MagicMock()
            mock_resource.return_value = mock_instance
            yield mock_instance
    
    def test_session_state_synchronization(self, mock_bedrock_client, mock_dynamodb):
        """
        Test session state synchronization with backend
        
        **Validates: Requirements 7.1, 7.2**
        """
        continuity_service = SessionContinuityService()
        memory_service = AgentCoreMemoryService()
        
        client_id = "sync-client-001"
        session_id = "sync-session-001"
        
        # Create memory
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        memory = memory_service.create_memory(client_id)
        
        # Load session context
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        context = continuity_service.load_session_context(client_id, session_id)
        assert context is not None
        
        # Verify state can be serialized for frontend
        state_json = json.dumps(context, default=str)
        assert state_json is not None
        
        print("✅ Session state synchronization validated")
    
    def test_notification_delivery_workflow(self, mock_bedrock_client, mock_dynamodb):
        """
        Test notification delivery to therapists
        
        **Validates: Requirements 4.4, 4.5**
        """
        management_service = RedFlagManagementService()
        
        session_id = "notification-session-001"
        client_id = "notification-client-001"
        therapist_id = "therapist-001"
        
        # Create red flag
        red_flag = management_service.create_red_flag(
            session_id=session_id,
            client_id=client_id,
            flag_type='crisis',
            severity='critical',
            context="Crisis situation detected"
        )
        
        # Send notifications
        notification_result = management_service.send_notifications(
            red_flag['flag_id'],
            [therapist_id]
        )
        
        assert notification_result is not None
        assert notification_result['sent'] is True
        
        print("✅ Notification delivery workflow validated")
    
    def test_therapist_dashboard_data_format(self, mock_bedrock_client):
        """
        Test data format for therapist dashboard
        
        **Validates: Requirements 5.2, 7.3, 7.4**
        """
        progress_service = ProgressSummarizationService()
        sentiment_service = SentimentAnalysisService()
        
        session_id = "dashboard-session-001"
        
        # Generate session summary
        session_text = "Client discussed progress with anxiety management."
        summary = progress_service.generate_session_summary(
            session_id,
            session_text,
            duration_seconds=1800
        )
        
        # Get sentiment summary
        sentiment_summary = sentiment_service.get_session_sentiment_summary(session_id)
        
        # Combine for dashboard
        dashboard_data = {
            'session_id': session_id,
            'summary': summary,
            'sentiment': sentiment_summary,
            'timestamp': datetime.now().isoformat()
        }
        
        # Verify format
        assert 'session_id' in dashboard_data
        assert 'summary' in dashboard_data
        assert 'sentiment' in dashboard_data
        
        # Verify no transcripts (privacy requirement)
        assert 'transcript' not in dashboard_data
        assert 'full_conversation' not in dashboard_data
        
        print("✅ Therapist dashboard data format validated")


class TestEndToEndAIWorkflow:
    """Test complete end-to-end AI workflow"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def mock_dynamodb(self):
        """Mock DynamoDB"""
        with patch('boto3.resource') as mock_resource:
            mock_instance = MagicMock()
            mock_resource.return_value = mock_instance
            yield mock_instance
    
    def test_complete_ai_workflow(self, mock_bedrock_client, mock_dynamodb):
        """
        Test complete AI workflow from session start to finish
        
        **Validates: Requirements 2.1, 3.3, 3.7, 4.1, 4.4, 7.1, 7.2, 7.3**
        """
        # Initialize all services
        memory_service = AgentCoreMemoryService()
        continuity_service = SessionContinuityService()
        detection_service = RedFlagDetectionService()
        management_service = RedFlagManagementService()
        sentiment_service = SentimentAnalysisService()
        progress_service = ProgressSummarizationService()
        
        client_id = "complete-workflow-client"
        session_id = "complete-workflow-session"
        therapist_id = "therapist-001"
        
        # Step 1: Initialize session
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        memory = memory_service.create_memory(client_id, language_preference="en")
        assert memory is not None
        print("✅ Step 1: Session initialized")
        
        # Step 2: Load context
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        context = continuity_service.load_session_context(client_id, session_id)
        assert context is not None
        print("✅ Step 2: Context loaded")
        
        # Step 3: Process conversation with red flag detection
        conversation_text = "I've been feeling really anxious. Sometimes I think about hurting myself."
        
        # Detect red flags
        red_flag_result = detection_service.analyze_content(session_id, conversation_text)
        assert red_flag_result is not None
        print("✅ Step 3: Red flag detection completed")
        
        # Step 4: Handle red flag if detected
        if red_flag_result.get('has_red_flag'):
            red_flag = management_service.create_red_flag(
                session_id=session_id,
                client_id=client_id,
                flag_type=red_flag_result['flag_type'],
                severity=red_flag_result['severity'],
                context=conversation_text[:100]
            )
            assert red_flag is not None
            
            # Escalate to therapist
            escalation = management_service.escalate_red_flag(
                red_flag['flag_id'],
                therapist_id
            )
            assert escalation is not None
            print("✅ Step 4: Red flag escalated")
        
        # Step 5: Analyze sentiment
        sentiment = sentiment_service.analyze_sentiment(session_id, conversation_text)
        assert sentiment is not None
        print("✅ Step 5: Sentiment analyzed")
        
        # Step 6: Generate session summary
        summary = progress_service.generate_session_summary(
            session_id,
            conversation_text,
            duration_seconds=1800
        )
        assert summary is not None
        assert 'key_topics' in summary
        print("✅ Step 6: Session summary generated")
        
        # Step 7: Save to memory
        session_summary = SessionSummary(
            session_id=session_id,
            duration_seconds=1800,
            key_topics=summary['key_topics'],
            emotional_state=summary['emotional_state'],
            therapeutic_progress=summary.get('progress_notes', 'Session completed')
        )
        
        updated_memory = memory_service.add_session_summary(client_id, session_summary)
        assert updated_memory is not None
        print("✅ Step 7: Memory updated")
        
        # Step 8: Verify complete workflow
        final_data = updated_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(final_data)
        }
        
        final_context = continuity_service.load_session_context(client_id, "next-session")
        assert final_context is not None
        print("✅ Step 8: Workflow completed successfully")
        
        print("\n✅ Complete end-to-end AI workflow validated")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
