"""
Tests for Session Continuity Service
🏆 Breaking Barriers UK 2026 compliant

Validates: Requirements 7.1, 7.2
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from src.services.session_continuity_service import SessionContinuityService
from src.models.agent_memory import (
    AgentMemory,
    ConversationContext,
    TherapeuticProfile,
    SessionSummary,
    ProgressNote,
    PersonalityAdaptation,
    RetentionPolicy,
    RetentionPolicyType
)
from src.models.session import TherapySession, SessionStatus


@pytest.fixture
def mock_memory_service():
    """Create mock AgentCore memory service"""
    return Mock()


@pytest.fixture
def mock_context_service():
    """Create mock conversation context service"""
    return Mock()


@pytest.fixture
def mock_session_repository():
    """Create mock session repository"""
    return Mock()


@pytest.fixture
def continuity_service(mock_memory_service, mock_context_service, mock_session_repository):
    """Create session continuity service with mocked dependencies"""
    return SessionContinuityService(
        memory_service=mock_memory_service,
        context_service=mock_context_service,
        session_repository=mock_session_repository
    )


@pytest.fixture
def sample_memory():
    """Create sample AgentMemory for testing"""
    return AgentMemory(
        memory_id="memory_client123",
        client_id="client123",
        conversation_context=ConversationContext(
            session_history=[
                SessionSummary(
                    session_id="session1",
                    timestamp=datetime.utcnow() - timedelta(days=7),
                    duration_seconds=1800,
                    key_topics=["anxiety", "work_stress"],
                    emotional_state=["anxious", "hopeful"],
                    therapeutic_progress="Client discussed work-related anxiety and coping strategies.",
                    milestones_achieved=["insight"]
                )
            ],
            ongoing_topics=["anxiety", "work_stress"],
            therapeutic_goals=["manage anxiety", "improve work-life balance"],
            progress_notes=[],
            personality_adaptations=[],
            last_session_date=datetime.utcnow() - timedelta(days=7),
            total_sessions=1
        ),
        therapeutic_profile=TherapeuticProfile(
            communication_style="empathetic",
            language_preference="en",
            preferred_approaches=["CBT", "mindfulness"],
            triggers_to_avoid=["criticism"],
            successful_interventions=["breathing exercises"]
        ),
        retention_policy=RetentionPolicy(
            policy_type=RetentionPolicyType.STANDARD
        )
    )


# ========== Cross-Session Memory Persistence Tests ==========

def test_persist_session_to_memory_success(continuity_service, mock_memory_service, mock_context_service):
    """Test successful session persistence to memory"""
    # Arrange
    client_id = "client123"
    session = TherapySession(
        session_id="session2",
        timestamp=datetime.utcnow(),
        client_id=client_id,
        agent_id="agent1",
        status=SessionStatus.COMPLETED,
        language="en"
    )
    conversation_turns = [
        {"user": "I've been feeling anxious", "ai": "Tell me more about that"},
        {"user": "Work has been stressful", "ai": "What specifically is causing stress?"}
    ]
    
    mock_session_summary = SessionSummary(
        session_id="session2",
        timestamp=datetime.utcnow(),
        duration_seconds=1800,
        key_topics=["anxiety", "work_stress"],
        emotional_state=["anxious"],
        therapeutic_progress="Discussed work anxiety",
        milestones_achieved=[]
    )
    
    mock_memory = AgentMemory(
        memory_id="memory_client123",
        client_id=client_id,
        conversation_context=ConversationContext(total_sessions=1)
    )
    
    mock_context_service.summarize_session.return_value = mock_session_summary
    mock_memory_service.get_memory.return_value = mock_memory
    mock_memory_service.update_memory.return_value = mock_memory
    
    # Act
    result = continuity_service.persist_session_to_memory(
        client_id=client_id,
        session=session,
        conversation_turns=conversation_turns,
        emotional_states=["anxious"]
    )
    
    # Assert
    assert result['success'] is True
    assert result['client_id'] == client_id
    assert result['session_id'] == "session2"
    assert 'memory_id' in result
    mock_context_service.summarize_session.assert_called_once()
    mock_memory_service.update_memory.assert_called_once()


def test_persist_session_creates_memory_if_not_exists(continuity_service, mock_memory_service, mock_context_service):
    """Test that persistence creates memory if it doesn't exist"""
    # Arrange
    client_id = "new_client"
    session = TherapySession(
        session_id="session1",
        timestamp=datetime.utcnow(),
        client_id=client_id,
        agent_id="agent1",
        status=SessionStatus.COMPLETED,
        language="en"
    )
    conversation_turns = [{"user": "Hello", "ai": "Hi there"}]
    
    mock_session_summary = SessionSummary(
        session_id="session1",
        timestamp=datetime.utcnow(),
        duration_seconds=600,
        key_topics=["introduction"],
        emotional_state=["neutral"],
        therapeutic_progress="First session",
        milestones_achieved=[]
    )
    
    new_memory = AgentMemory(
        memory_id="memory_new_client",
        client_id=client_id,
        conversation_context=ConversationContext()
    )
    
    mock_memory_service.get_memory.return_value = None
    mock_memory_service.create_memory.return_value = new_memory
    mock_context_service.summarize_session.return_value = mock_session_summary
    mock_memory_service.update_memory.return_value = new_memory
    
    # Act
    result = continuity_service.persist_session_to_memory(
        client_id=client_id,
        session=session,
        conversation_turns=conversation_turns
    )
    
    # Assert
    assert result['success'] is True
    mock_memory_service.create_memory.assert_called_once_with(
        client_id=client_id,
        language_preference="en"
    )


def test_persist_session_handles_errors(continuity_service, mock_memory_service, mock_context_service):
    """Test error handling in session persistence"""
    # Arrange
    client_id = "client123"
    session = TherapySession(
        session_id="session2",
        timestamp=datetime.utcnow(),
        client_id=client_id,
        agent_id="agent1",
        status=SessionStatus.COMPLETED
    )
    conversation_turns = []
    
    mock_context_service.summarize_session.side_effect = Exception("Summarization failed")
    
    # Act
    result = continuity_service.persist_session_to_memory(
        client_id=client_id,
        session=session,
        conversation_turns=conversation_turns
    )
    
    # Assert
    assert result['success'] is False
    assert 'error' in result
    assert result['client_id'] == client_id


# ========== Conversation Resumption Tests ==========

def test_load_session_context_with_history(continuity_service, mock_memory_service, sample_memory):
    """Test loading session context with existing history"""
    # Arrange
    client_id = "client123"
    mock_memory_service.get_memory.return_value = sample_memory
    
    # Act
    result = continuity_service.load_session_context(client_id, include_recent_sessions=3)
    
    # Assert
    assert result['has_previous_sessions'] is True
    assert result['total_sessions'] == 1
    assert result['last_session_date'] is not None
    assert 'context' in result
    assert 'therapeutic_profile' in result
    assert len(result['recent_sessions']) == 1
    assert result['ongoing_topics'] == ["anxiety", "work_stress"]
    assert result['therapeutic_goals'] == ["manage anxiety", "improve work-life balance"]


def test_load_session_context_no_history(continuity_service, mock_memory_service):
    """Test loading session context for new client"""
    # Arrange
    client_id = "new_client"
    mock_memory_service.get_memory.return_value = None
    
    # Act
    result = continuity_service.load_session_context(client_id)
    
    # Assert
    assert result['has_previous_sessions'] is False
    assert result['total_sessions'] == 0
    assert "first session" in result['context'].lower()
    assert result['therapeutic_profile'] is None


def test_resume_conversation_first_session(continuity_service, mock_memory_service):
    """Test resuming conversation for first session"""
    # Arrange
    client_id = "new_client"
    session_id = "session1"
    mock_memory_service.get_memory.return_value = None
    
    # Act
    result = continuity_service.resume_conversation(client_id, session_id)
    
    # Assert
    assert result['is_first_session'] is True
    assert "first" in result['greeting'].lower()
    assert result['session_id'] == session_id


def test_resume_conversation_with_history(continuity_service, mock_memory_service, sample_memory):
    """Test resuming conversation with existing history"""
    # Arrange
    client_id = "client123"
    session_id = "session2"
    mock_memory_service.get_memory.return_value = sample_memory
    
    # Act
    result = continuity_service.resume_conversation(client_id, session_id)
    
    # Assert
    assert result['is_first_session'] is False
    assert "welcome back" in result['greeting'].lower()
    assert result['session_id'] == session_id
    assert result['total_previous_sessions'] == 1
    assert result['days_since_last_session'] is not None
    assert result['ongoing_topics'] == ["anxiety", "work_stress"]


def test_check_session_gap_no_gap(continuity_service, mock_memory_service, sample_memory):
    """Test checking session gap when there's no significant gap"""
    # Arrange
    client_id = "client123"
    # Set last session to 3 days ago
    sample_memory.conversation_context.last_session_date = datetime.utcnow() - timedelta(days=3)
    mock_memory_service.get_memory.return_value = sample_memory
    
    # Act
    result = continuity_service.check_session_gap(client_id, threshold_days=7)
    
    # Assert
    assert result['has_gap'] is False
    assert result['is_first_session'] is False
    assert result['days_since_last_session'] == 3
    assert result['recommendation'] == 'continue_normally'


def test_check_session_gap_significant_gap(continuity_service, mock_memory_service, sample_memory):
    """Test checking session gap when there's a significant gap"""
    # Arrange
    client_id = "client123"
    # Set last session to 20 days ago
    sample_memory.conversation_context.last_session_date = datetime.utcnow() - timedelta(days=20)
    mock_memory_service.get_memory.return_value = sample_memory
    
    # Act
    result = continuity_service.check_session_gap(client_id, threshold_days=7)
    
    # Assert
    assert result['has_gap'] is True
    assert result['is_first_session'] is False
    assert result['days_since_last_session'] == 20
    assert result['recommendation'] == 'check_in_thoroughly'
    assert 'suggested_topics' in result


def test_check_session_gap_first_session(continuity_service, mock_memory_service):
    """Test checking session gap for first session"""
    # Arrange
    client_id = "new_client"
    mock_memory_service.get_memory.return_value = None
    
    # Act
    result = continuity_service.check_session_gap(client_id)
    
    # Assert
    assert result['has_gap'] is False
    assert result['is_first_session'] is True
    assert result['recommendation'] == 'first_session_protocol'


# ========== Therapeutic Relationship Continuity Tests ==========

def test_build_therapeutic_relationship(continuity_service, mock_memory_service, mock_context_service, sample_memory):
    """Test building therapeutic relationship"""
    # Arrange
    client_id = "client123"
    session_id = "session2"
    relationship_indicators = {
        'rapport_score': 0.8,
        'trust_level': 0.7,
        'engagement_level': 0.9
    }
    
    mock_adaptation = PersonalityAdaptation(
        adaptation_id="adapt1",
        timestamp=datetime.utcnow(),
        adaptation_type="relationship_building",
        description="Test adaptation",
        effectiveness_score=0.8
    )
    
    mock_memory_service.get_memory.return_value = sample_memory
    mock_context_service.record_personality_adaptation.return_value = mock_adaptation
    
    # Act
    result = continuity_service.build_therapeutic_relationship(
        client_id=client_id,
        session_id=session_id,
        relationship_indicators=relationship_indicators
    )
    
    # Assert
    assert result['success'] is True
    assert result['client_id'] == client_id
    assert result['session_id'] == session_id
    assert result['relationship_strength'] == 0.8
    assert result['rapport_score'] == 0.8
    assert result['trust_level'] == 0.7
    assert result['engagement_level'] == 0.9
    assert 'recommendations' in result
    assert len(result['recommendations']) > 0


def test_track_therapeutic_alliance(continuity_service, mock_memory_service, mock_context_service, sample_memory):
    """Test tracking therapeutic alliance"""
    # Arrange
    client_id = "client123"
    alliance_metrics = {
        'goal_agreement': 0.8,
        'task_agreement': 0.7,
        'bond': 0.9
    }
    
    mock_note = ProgressNote(
        note_id="note1",
        timestamp=datetime.utcnow(),
        content="Alliance tracking",
        category="alliance_development",
        importance=4
    )
    
    mock_memory_service.get_memory.return_value = sample_memory
    mock_context_service.track_therapeutic_milestone.return_value = mock_note
    
    # Act
    result = continuity_service.track_therapeutic_alliance(
        client_id=client_id,
        alliance_metrics=alliance_metrics
    )
    
    # Assert
    assert result['success'] is True
    assert result['client_id'] == client_id
    assert 'alliance_score' in result
    assert result['alliance_score'] == pytest.approx(0.8, abs=0.1)
    assert 'alliance_trend' in result
    assert 'recommendations' in result


def test_track_therapeutic_alliance_no_memory(continuity_service, mock_memory_service):
    """Test tracking alliance when no memory exists"""
    # Arrange
    client_id = "new_client"
    alliance_metrics = {'goal_agreement': 0.7}
    
    mock_memory_service.get_memory.return_value = None
    
    # Act
    result = continuity_service.track_therapeutic_alliance(
        client_id=client_id,
        alliance_metrics=alliance_metrics
    )
    
    # Assert
    assert result['success'] is False
    assert 'error' in result


# ========== Memory-Based Personalization Tests ==========

def test_personalize_therapeutic_approach_with_history(continuity_service, mock_memory_service, mock_context_service, sample_memory):
    """Test personalizing therapeutic approach with existing history"""
    # Arrange
    client_id = "client123"
    
    mock_adaptations = [
        PersonalityAdaptation(
            adaptation_id="adapt1",
            timestamp=datetime.utcnow(),
            adaptation_type="tone",
            description="Use calm, reassuring tone",
            effectiveness_score=0.8
        )
    ]
    
    mock_memory_service.get_memory.return_value = sample_memory
    mock_context_service.get_effective_adaptations.return_value = mock_adaptations
    
    # Act
    result = continuity_service.personalize_therapeutic_approach(client_id)
    
    # Assert
    assert result['personalization_level'] in ['default', 'basic', 'moderate', 'high']
    assert 'recommendations' in result
    assert len(result['recommendations']) > 0
    assert result['communication_style'] == "empathetic"
    assert result['language_preference'] == "en"
    assert 'preferred_approaches' in result
    assert 'triggers_to_avoid' in result


def test_personalize_therapeutic_approach_no_history(continuity_service, mock_memory_service):
    """Test personalizing approach for new client"""
    # Arrange
    client_id = "new_client"
    mock_memory_service.get_memory.return_value = None
    
    # Act
    result = continuity_service.personalize_therapeutic_approach(client_id)
    
    # Assert
    assert result['personalization_level'] == 'default'
    assert 'recommendations' in result
    assert result['communication_style'] == 'empathetic'
    assert result['language_preference'] == 'en'


def test_personalize_with_session_feedback(continuity_service, mock_memory_service, mock_context_service, sample_memory):
    """Test personalization with session feedback"""
    # Arrange
    client_id = "client123"
    session_feedback = {
        'session_id': 'session1',
        'score': 0.9,
        'notes': 'Very helpful session'
    }
    
    mock_adaptations = []
    feedback_insights = {
        'recommendations': ['Continue current approach']
    }
    
    mock_memory_service.get_memory.return_value = sample_memory
    mock_context_service.get_effective_adaptations.return_value = mock_adaptations
    mock_context_service.learn_from_session_feedback.return_value = feedback_insights
    
    # Act
    result = continuity_service.personalize_therapeutic_approach(
        client_id=client_id,
        session_feedback=session_feedback
    )
    
    # Assert
    assert 'recommendations' in result
    assert 'Continue current approach' in result['recommendations']
    mock_context_service.learn_from_session_feedback.assert_called_once()


def test_adapt_to_client_preferences(continuity_service, mock_memory_service, mock_context_service, sample_memory):
    """Test adapting to client preferences"""
    # Arrange
    client_id = "client123"
    observed_preferences = {
        'communication_style': 'direct',
        'preferred_topics': ['mindfulness', 'exercise'],
        'avoided_topics': ['family'],
        'cultural_preferences': ['respect for elders']
    }
    
    mock_adaptation = PersonalityAdaptation(
        adaptation_id="adapt2",
        timestamp=datetime.utcnow(),
        adaptation_type="preference_adaptation",
        description="Adapted to preferences",
        effectiveness_score=0.7
    )
    
    mock_memory_service.get_memory.return_value = sample_memory
    mock_memory_service.update_therapeutic_profile.return_value = sample_memory
    mock_context_service.record_personality_adaptation.return_value = mock_adaptation
    
    # Act
    result = continuity_service.adapt_to_client_preferences(
        client_id=client_id,
        observed_preferences=observed_preferences
    )
    
    # Assert
    assert result['success'] is True
    assert result['client_id'] == client_id
    assert 'preferences_updated' in result
    assert len(result['preferences_updated']) == 4
    assert 'profile_updates' in result
    assert 'adaptation_id' in result


def test_adapt_to_preferences_creates_memory(continuity_service, mock_memory_service, mock_context_service):
    """Test that adaptation creates memory if it doesn't exist"""
    # Arrange
    client_id = "new_client"
    observed_preferences = {'communication_style': 'supportive'}
    
    new_memory = AgentMemory(
        memory_id="memory_new_client",
        client_id=client_id,
        conversation_context=ConversationContext()
    )
    
    mock_adaptation = PersonalityAdaptation(
        adaptation_id="adapt1",
        timestamp=datetime.utcnow(),
        adaptation_type="preference_adaptation",
        description="Initial adaptation",
        effectiveness_score=0.7
    )
    
    mock_memory_service.get_memory.return_value = None
    mock_memory_service.create_memory.return_value = new_memory
    mock_memory_service.update_therapeutic_profile.return_value = new_memory
    mock_context_service.record_personality_adaptation.return_value = mock_adaptation
    
    # Act
    result = continuity_service.adapt_to_client_preferences(
        client_id=client_id,
        observed_preferences=observed_preferences
    )
    
    # Assert
    assert result['success'] is True
    mock_memory_service.create_memory.assert_called_once_with(client_id)


# ========== Continuity Metrics Tests ==========

def test_get_continuity_metrics_with_history(continuity_service, mock_memory_service, sample_memory):
    """Test getting continuity metrics with existing history"""
    # Arrange
    client_id = "client123"
    mock_memory_service.get_memory.return_value = sample_memory
    
    # Act
    result = continuity_service.get_continuity_metrics(client_id)
    
    # Assert
    assert result['has_history'] is True
    assert result['total_sessions'] == 1
    assert 'continuity_score' in result
    assert result['continuity_score'] >= 0.0
    assert result['continuity_score'] <= 1.0
    assert 'session_frequency' in result
    assert 'topic_consistency' in result
    assert 'relationship_strength' in result
    assert result['ongoing_topics_count'] == 2
    assert result['therapeutic_goals_count'] == 2


def test_get_continuity_metrics_no_history(continuity_service, mock_memory_service):
    """Test getting continuity metrics for new client"""
    # Arrange
    client_id = "new_client"
    mock_memory_service.get_memory.return_value = None
    
    # Act
    result = continuity_service.get_continuity_metrics(client_id)
    
    # Assert
    assert result['has_history'] is False
    assert result['total_sessions'] == 0
    assert result['continuity_score'] == 0.0


def test_continuity_score_calculation(continuity_service, mock_memory_service):
    """Test continuity score calculation with various factors"""
    # Arrange
    client_id = "client123"
    
    # Create memory with high continuity factors
    memory = AgentMemory(
        memory_id="memory_client123",
        client_id=client_id,
        conversation_context=ConversationContext(
            session_history=[
                SessionSummary(
                    session_id=f"session{i}",
                    timestamp=datetime.utcnow() - timedelta(days=i*7),
                    duration_seconds=1800,
                    key_topics=["anxiety"],
                    emotional_state=["calm"],
                    therapeutic_progress="Progress",
                    milestones_achieved=[]
                )
                for i in range(10)
            ],
            ongoing_topics=["anxiety", "work", "relationships", "self-esteem", "goals"],
            therapeutic_goals=["manage anxiety", "improve relationships", "build confidence"],
            progress_notes=[
                ProgressNote(
                    note_id=f"note{i}",
                    timestamp=datetime.utcnow(),
                    content="Progress note",
                    category="milestone",
                    importance=4
                )
                for i in range(10)
            ],
            personality_adaptations=[
                PersonalityAdaptation(
                    adaptation_id=f"adapt{i}",
                    timestamp=datetime.utcnow(),
                    adaptation_type="tone",
                    description="Adaptation",
                    effectiveness_score=0.8
                )
                for i in range(5)
            ],
            total_sessions=10
        )
    )
    
    mock_memory_service.get_memory.return_value = memory
    
    # Act
    result = continuity_service.get_continuity_metrics(client_id)
    
    # Assert
    assert result['continuity_score'] > 0.5  # Should be high with all factors present
    assert result['total_sessions'] == 10


# ========== Helper Method Tests ==========

def test_generate_resumption_greeting_second_session(continuity_service):
    """Test greeting generation for second session"""
    # Act
    greeting = continuity_service._generate_resumption_greeting(
        total_sessions=1,
        last_session_date=(datetime.utcnow() - timedelta(days=7)).isoformat(),
        ongoing_topics=["anxiety"],
        therapeutic_goals=["manage stress"]
    )
    
    # Assert
    assert "welcome back" in greeting.lower()
    assert "second session" in greeting.lower()


def test_generate_resumption_greeting_long_gap(continuity_service):
    """Test greeting generation after long gap"""
    # Act
    greeting = continuity_service._generate_resumption_greeting(
        total_sessions=5,
        last_session_date=(datetime.utcnow() - timedelta(days=45)).isoformat(),
        ongoing_topics=[],
        therapeutic_goals=[]
    )
    
    # Assert
    assert "welcome back" in greeting.lower()
    assert "while" in greeting.lower()


def test_calculate_personalization_level(continuity_service):
    """Test personalization level calculation"""
    # Test default level
    level = continuity_service._calculate_personalization_level(0, 0, 0)
    assert level == 'default'
    
    # Test basic level
    level = continuity_service._calculate_personalization_level(2, 1, 1)
    assert level == 'basic'
    
    # Test moderate level
    level = continuity_service._calculate_personalization_level(5, 3, 2)
    assert level == 'moderate'
    
    # Test high level
    level = continuity_service._calculate_personalization_level(15, 6, 4)
    assert level == 'high'


def test_calculate_session_frequency(continuity_service):
    """Test session frequency calculation"""
    # Create sessions with 7-day gaps
    sessions = [
        SessionSummary(
            session_id=f"session{i}",
            timestamp=datetime.utcnow() - timedelta(days=i*7),
            duration_seconds=1800,
            key_topics=[],
            emotional_state=[],
            therapeutic_progress="Progress",
            milestones_achieved=[]
        )
        for i in range(5)
    ]
    
    # Act
    result = continuity_service._calculate_session_frequency(sessions)
    
    # Assert
    assert result['average_days_between_sessions'] == pytest.approx(7.0, abs=0.1)
    assert result['frequency_category'] == 'frequent'
    assert result['total_sessions'] == 5


def test_calculate_topic_consistency(continuity_service):
    """Test topic consistency calculation"""
    # Create context with recurring topics
    context = ConversationContext(
        session_history=[
            SessionSummary(
                session_id="session1",
                timestamp=datetime.utcnow(),
                duration_seconds=1800,
                key_topics=["anxiety", "work"],
                emotional_state=[],
                therapeutic_progress="Progress",
                milestones_achieved=[]
            ),
            SessionSummary(
                session_id="session2",
                timestamp=datetime.utcnow(),
                duration_seconds=1800,
                key_topics=["anxiety", "relationships"],
                emotional_state=[],
                therapeutic_progress="Progress",
                milestones_achieved=[]
            ),
            SessionSummary(
                session_id="session3",
                timestamp=datetime.utcnow(),
                duration_seconds=1800,
                key_topics=["anxiety", "work"],
                emotional_state=[],
                therapeutic_progress="Progress",
                milestones_achieved=[]
            )
        ]
    )
    
    # Act
    result = continuity_service._calculate_topic_consistency(context)
    
    # Assert
    assert 'consistency_score' in result
    assert result['consistency_score'] > 0.0
    assert 'anxiety' in result['recurring_topics']
    assert 'work' in result['recurring_topics']
    assert result['total_unique_topics'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
