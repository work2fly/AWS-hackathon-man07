"""
Unit tests for Conversation Context Management Service
Tests conversation history, therapeutic progress, personality adaptation, and context window management
🏆 Breaking Barriers UK 2026 compliant
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from src.services.conversation_context_service import ConversationContextService
from src.services.agentcore_memory_service import AgentCoreMemoryService
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


@pytest.fixture
def mock_memory_service():
    """Create mock AgentCore memory service"""
    service = Mock(spec=AgentCoreMemoryService)
    return service


@pytest.fixture
def conversation_service(mock_memory_service):
    """Create conversation context service with mock memory service"""
    return ConversationContextService(memory_service=mock_memory_service)


@pytest.fixture
def sample_memory():
    """Create sample AgentMemory for testing"""
    return AgentMemory(
        memory_id="test_memory_123",
        client_id="client_123",
        conversation_context=ConversationContext(
            session_history=[],
            ongoing_topics=["anxiety", "work_stress"],
            therapeutic_goals=["Manage anxiety", "Improve work-life balance"],
            progress_notes=[],
            personality_adaptations=[],
            total_sessions=0
        ),
        therapeutic_profile=TherapeuticProfile(
            communication_style="empathetic",
            language_preference="en",
            preferred_approaches=["CBT", "mindfulness"],
            triggers_to_avoid=["trauma"],
            successful_interventions=["breathing exercises"]
        ),
        retention_policy=RetentionPolicy(
            policy_type=RetentionPolicyType.STANDARD
        )
    )


class TestConversationHistoryTracking:
    """Test conversation history tracking functionality"""
    
    def test_add_conversation_turn(self, conversation_service, mock_memory_service, sample_memory):
        """Test adding a conversation turn"""
        mock_memory_service.get_memory.return_value = sample_memory
        
        result = conversation_service.add_conversation_turn(
            client_id="client_123",
            session_id="session_456",
            user_message="I'm feeling anxious about work",
            ai_response="I understand. Let's explore what's causing this anxiety."
        )
        
        assert result['client_id'] == "client_123"
        assert result['session_id'] == "session_456"
        assert 'timestamp' in result
        assert 'topics_extracted' in result
        assert isinstance(result['topics_extracted'], list)
    
    def test_add_conversation_turn_creates_memory_if_not_exists(
        self, conversation_service, mock_memory_service, sample_memory
    ):
        """Test that conversation turn creates memory if it doesn't exist"""
        mock_memory_service.get_memory.return_value = None
        mock_memory_service.create_memory.return_value = sample_memory
        
        result = conversation_service.add_conversation_turn(
            client_id="client_123",
            session_id="session_456",
            user_message="Hello",
            ai_response="Hi, how can I help you today?"
        )
        
        mock_memory_service.create_memory.assert_called_once_with("client_123")
        assert result['client_id'] == "client_123"
    
    def test_summarize_session(self, conversation_service, mock_memory_service):
        """Test session summarization"""
        conversation_turns = [
            {"user": "I'm feeling anxious", "ai": "Tell me more about that"},
            {"user": "It's about work", "ai": "What specifically at work?"},
            {"user": "My deadlines", "ai": "Let's work on coping strategies"}
        ]
        
        summary = conversation_service.summarize_session(
            client_id="client_123",
            session_id="session_456",
            duration_seconds=1800,
            conversation_turns=conversation_turns,
            emotional_states=["anxious", "stressed"]
        )
        
        assert isinstance(summary, SessionSummary)
        assert summary.session_id == "session_456"
        assert summary.duration_seconds == 1800
        assert len(summary.key_topics) > 0
        assert len(summary.emotional_state) == 2
        assert len(summary.therapeutic_progress) > 0
        mock_memory_service.add_session_summary.assert_called_once()
    
    def test_get_conversation_history(self, conversation_service, mock_memory_service):
        """Test retrieving conversation history"""
        # Create sample session history
        sessions = [
            SessionSummary(
                session_id=f"session_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i),
                duration_seconds=1800,
                key_topics=["anxiety"],
                emotional_state=["calm"],
                therapeutic_progress="Good progress",
                milestones_achieved=[]
            )
            for i in range(5)
        ]
        
        context = ConversationContext(session_history=sessions)
        mock_memory_service.get_conversation_context.return_value = context
        
        history = conversation_service.get_conversation_history("client_123", limit=3)
        
        assert len(history) == 3
        # Should be sorted by timestamp, most recent first
        assert history[0].session_id == "session_0"
        assert history[1].session_id == "session_1"
        assert history[2].session_id == "session_2"
    
    def test_get_conversation_history_no_memory(self, conversation_service, mock_memory_service):
        """Test retrieving history when no memory exists"""
        mock_memory_service.get_conversation_context.return_value = None
        
        history = conversation_service.get_conversation_history("client_123")
        
        assert history == []


class TestTherapeuticProgressMonitoring:
    """Test therapeutic progress monitoring functionality"""
    
    def test_track_therapeutic_milestone(self, conversation_service, mock_memory_service):
        """Test tracking a therapeutic milestone"""
        note = conversation_service.track_therapeutic_milestone(
            client_id="client_123",
            milestone_type="breakthrough",
            description="Client had major insight about anxiety triggers",
            importance=5
        )
        
        assert isinstance(note, ProgressNote)
        assert note.category == "breakthrough"
        assert note.importance == 5
        assert "insight" in note.content.lower()
        mock_memory_service.add_progress_note.assert_called_once()
    
    def test_track_milestone_clamps_importance(self, conversation_service, mock_memory_service):
        """Test that importance is clamped to valid range"""
        note = conversation_service.track_therapeutic_milestone(
            client_id="client_123",
            milestone_type="insight",
            description="Small insight",
            importance=10  # Should be clamped to 5
        )
        
        assert note.importance == 5
    
    def test_get_therapeutic_progress(self, conversation_service, mock_memory_service):
        """Test getting therapeutic progress summary"""
        # Create sample data
        sessions = [
            SessionSummary(
                session_id=f"session_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i),
                duration_seconds=1800,
                key_topics=["anxiety", "work"],
                emotional_state=["calm"],
                therapeutic_progress="Progress made",
                milestones_achieved=["insight", "commitment"]
            )
            for i in range(3)
        ]
        
        notes = [
            ProgressNote(
                note_id=f"note_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i),
                content=f"Progress note {i}",
                category="general",
                importance=4
            )
            for i in range(2)
        ]
        
        context = ConversationContext(
            session_history=sessions,
            progress_notes=notes,
            ongoing_topics=["anxiety", "work_stress"],
            therapeutic_goals=["Manage anxiety"]
        )
        
        mock_memory_service.get_conversation_context.return_value = context
        
        progress = conversation_service.get_therapeutic_progress("client_123")
        
        assert progress['total_sessions'] == 3
        assert len(progress['progress_notes']) == 2
        assert len(progress['milestones']) == 6  # 2 milestones × 3 sessions
        assert len(progress['ongoing_topics']) == 2
        assert 'metrics' in progress
    
    def test_get_therapeutic_progress_with_date_filter(
        self, conversation_service, mock_memory_service
    ):
        """Test getting progress with date filter"""
        # Create sessions spanning 60 days
        sessions = [
            SessionSummary(
                session_id=f"session_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i * 10),
                duration_seconds=1800,
                key_topics=["anxiety"],
                emotional_state=["calm"],
                therapeutic_progress="Progress",
                milestones_achieved=[]
            )
            for i in range(6)
        ]
        
        context = ConversationContext(session_history=sessions)
        mock_memory_service.get_conversation_context.return_value = context
        
        # Get progress for last 30 days
        progress = conversation_service.get_therapeutic_progress("client_123", days=30)
        
        # Should only include sessions from last 30 days (sessions 0, 1, 2)
        assert progress['total_sessions'] == 3
    
    def test_set_therapeutic_goals(self, conversation_service, mock_memory_service, sample_memory):
        """Test setting therapeutic goals"""
        mock_memory_service.get_memory.return_value = sample_memory
        mock_memory_service.update_memory.return_value = sample_memory
        
        goals = ["Reduce anxiety", "Improve sleep", "Build confidence"]
        context = conversation_service.set_therapeutic_goals("client_123", goals)
        
        assert isinstance(context, ConversationContext)
        mock_memory_service.update_memory.assert_called_once()


class TestPersonalityAdaptation:
    """Test personality adaptation and learning functionality"""
    
    def test_record_personality_adaptation(self, conversation_service, mock_memory_service):
        """Test recording a personality adaptation"""
        adaptation = conversation_service.record_personality_adaptation(
            client_id="client_123",
            adaptation_type="tone",
            description="Use more gentle, slower pacing",
            effectiveness_score=0.8
        )
        
        assert isinstance(adaptation, PersonalityAdaptation)
        assert adaptation.adaptation_type == "tone"
        assert adaptation.effectiveness_score == 0.8
        mock_memory_service.add_personality_adaptation.assert_called_once()
    
    def test_record_adaptation_clamps_effectiveness(self, conversation_service, mock_memory_service):
        """Test that effectiveness score is clamped to valid range"""
        adaptation = conversation_service.record_personality_adaptation(
            client_id="client_123",
            adaptation_type="approach",
            description="Test adaptation",
            effectiveness_score=1.5  # Should be clamped to 1.0
        )
        
        assert adaptation.effectiveness_score == 1.0
    
    def test_get_effective_adaptations(self, conversation_service, mock_memory_service):
        """Test getting effective adaptations"""
        adaptations = [
            PersonalityAdaptation(
                adaptation_id=f"adapt_{i}",
                timestamp=datetime.utcnow(),
                adaptation_type="tone",
                description=f"Adaptation {i}",
                effectiveness_score=0.5 + (i * 0.1)
            )
            for i in range(5)
        ]
        
        context = ConversationContext(personality_adaptations=adaptations)
        mock_memory_service.get_conversation_context.return_value = context
        
        effective = conversation_service.get_effective_adaptations(
            "client_123",
            min_effectiveness=0.7
        )
        
        # Should return adaptations with score >= 0.7 (adapt_2, adapt_3, adapt_4)
        assert len(effective) == 3
        # Should be sorted by effectiveness, highest first
        assert effective[0].effectiveness_score >= effective[1].effectiveness_score
    
    def test_update_adaptation_effectiveness(
        self, conversation_service, mock_memory_service, sample_memory
    ):
        """Test updating adaptation effectiveness"""
        adaptation = PersonalityAdaptation(
            adaptation_id="adapt_123",
            timestamp=datetime.utcnow(),
            adaptation_type="tone",
            description="Test",
            effectiveness_score=0.5
        )
        sample_memory.conversation_context.personality_adaptations.append(adaptation)
        
        mock_memory_service.get_memory.return_value = sample_memory
        
        success = conversation_service.update_adaptation_effectiveness(
            "client_123",
            "adapt_123",
            0.9
        )
        
        assert success is True
        assert adaptation.effectiveness_score == 0.9
        mock_memory_service.update_memory.assert_called_once()
    
    def test_learn_from_session_feedback_positive(
        self, conversation_service, mock_memory_service, sample_memory
    ):
        """Test learning from positive session feedback"""
        session = SessionSummary(
            session_id="session_123",
            timestamp=datetime.utcnow(),
            duration_seconds=1800,
            key_topics=["mindfulness", "breathing"],
            emotional_state=["calm"],
            therapeutic_progress="Great progress",
            milestones_achieved=["insight"]
        )
        sample_memory.conversation_context.session_history.append(session)
        
        mock_memory_service.get_memory.return_value = sample_memory
        mock_memory_service.update_memory.return_value = sample_memory
        
        insights = conversation_service.learn_from_session_feedback(
            client_id="client_123",
            session_id="session_123",
            feedback_score=0.9,
            feedback_notes="Very helpful session"
        )
        
        assert insights['feedback_score'] == 0.9
        assert len(insights['recommendations']) > 0
        # Topics should be added to successful interventions
        assert "mindfulness" in sample_memory.therapeutic_profile.successful_interventions
    
    def test_learn_from_session_feedback_negative(
        self, conversation_service, mock_memory_service, sample_memory
    ):
        """Test learning from negative session feedback"""
        session = SessionSummary(
            session_id="session_123",
            timestamp=datetime.utcnow(),
            duration_seconds=1800,
            key_topics=["trauma", "past_events"],
            emotional_state=["distressed"],
            therapeutic_progress="Difficult session",
            milestones_achieved=[]
        )
        sample_memory.conversation_context.session_history.append(session)
        
        mock_memory_service.get_memory.return_value = sample_memory
        mock_memory_service.update_memory.return_value = sample_memory
        
        insights = conversation_service.learn_from_session_feedback(
            client_id="client_123",
            session_id="session_123",
            feedback_score=0.3,
            feedback_notes="Too intense"
        )
        
        assert insights['feedback_score'] == 0.3
        # Topics should be added to triggers to avoid
        assert "trauma" in sample_memory.therapeutic_profile.triggers_to_avoid


class TestContextWindowManagement:
    """Test context window management functionality"""
    
    def test_get_context_window(self, conversation_service, mock_memory_service, sample_memory):
        """Test getting optimized context window"""
        # Add session history
        sessions = [
            SessionSummary(
                session_id=f"session_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i),
                duration_seconds=1800,
                key_topics=["anxiety", "work"],
                emotional_state=["calm"],
                therapeutic_progress="Making progress with anxiety management",
                milestones_achieved=["insight"]
            )
            for i in range(5)
        ]
        sample_memory.conversation_context.session_history = sessions
        
        # Add progress notes
        notes = [
            ProgressNote(
                note_id=f"note_{i}",
                timestamp=datetime.utcnow(),
                content=f"Important progress note {i}",
                category="breakthrough",
                importance=5
            )
            for i in range(3)
        ]
        sample_memory.conversation_context.progress_notes = notes
        
        mock_memory_service.get_memory.return_value = sample_memory
        
        context = conversation_service.get_context_window(
            "client_123",
            max_tokens=2000,
            include_recent_sessions=3
        )
        
        assert isinstance(context, str)
        assert len(context) > 0
        # Should include therapeutic profile
        assert "Communication Style" in context
        # Should include therapeutic goals
        assert "Therapeutic Goals" in context or "Manage anxiety" in context
    
    def test_get_context_window_respects_token_limit(
        self, conversation_service, mock_memory_service, sample_memory
    ):
        """Test that context window respects token limits"""
        # Add many sessions
        sessions = [
            SessionSummary(
                session_id=f"session_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i),
                duration_seconds=1800,
                key_topics=["anxiety"] * 10,  # Many topics
                emotional_state=["calm"],
                therapeutic_progress="Long progress description " * 50,  # Long text
                milestones_achieved=["insight"]
            )
            for i in range(20)
        ]
        sample_memory.conversation_context.session_history = sessions
        
        mock_memory_service.get_memory.return_value = sample_memory
        
        context = conversation_service.get_context_window(
            "client_123",
            max_tokens=1000,  # Small limit
            include_recent_sessions=10
        )
        
        # Rough check: context should be approximately within token limit
        estimated_tokens = len(context) // 4
        assert estimated_tokens <= 1200  # Allow some overhead
    
    def test_compress_conversation_history(
        self, conversation_service, mock_memory_service, sample_memory
    ):
        """Test compressing conversation history"""
        # Add many sessions
        sessions = [
            SessionSummary(
                session_id=f"session_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i * 5),
                duration_seconds=1800,
                key_topics=["anxiety"],
                emotional_state=["calm"],
                therapeutic_progress="Progress",
                milestones_achieved=[]
            )
            for i in range(20)
        ]
        sample_memory.conversation_context.session_history = sessions
        
        # Add many progress notes
        notes = [
            ProgressNote(
                note_id=f"note_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i * 10),
                content=f"Note {i}",
                category="general",
                importance=2
            )
            for i in range(30)
        ]
        sample_memory.conversation_context.progress_notes = notes
        
        mock_memory_service.get_memory.return_value = sample_memory
        mock_memory_service.update_memory.return_value = sample_memory
        
        stats = conversation_service.compress_conversation_history(
            "client_123",
            keep_recent=10
        )
        
        assert stats['original_sessions'] == 20
        assert stats['compressed_sessions'] == 10
        assert stats['compression_ratio'] > 0
        mock_memory_service.update_memory.assert_called_once()
    
    def test_compress_keeps_high_importance_notes(
        self, conversation_service, mock_memory_service, sample_memory
    ):
        """Test that compression keeps high-importance notes"""
        # Add old but important note
        important_note = ProgressNote(
            note_id="important",
            timestamp=datetime.utcnow() - timedelta(days=60),
            content="Critical insight",
            category="breakthrough",
            importance=5
        )
        
        # Add recent low-importance note
        recent_note = ProgressNote(
            note_id="recent",
            timestamp=datetime.utcnow() - timedelta(days=5),
            content="Minor note",
            category="general",
            importance=2
        )
        
        sample_memory.conversation_context.progress_notes = [important_note, recent_note]
        
        mock_memory_service.get_memory.return_value = sample_memory
        mock_memory_service.update_memory.return_value = sample_memory
        
        conversation_service.compress_conversation_history("client_123", keep_recent=5)
        
        # Both notes should be kept (important + recent)
        assert len(sample_memory.conversation_context.progress_notes) == 2


class TestHelperMethods:
    """Test helper methods"""
    
    def test_extract_topics(self, conversation_service):
        """Test topic extraction from conversation"""
        topics = conversation_service._extract_topics(
            "I'm feeling very anxious about my relationship with my partner",
            "Let's explore what's causing this anxiety in your relationship"
        )
        
        assert "anxiety" in topics
        assert "relationships" in topics
    
    def test_generate_progress_summary(self, conversation_service):
        """Test progress summary generation"""
        turns = [
            {"user": "I'm feeling better", "ai": "That's great to hear"},
            {"user": "I've been practicing mindfulness", "ai": "Excellent progress"}
        ]
        
        summary = conversation_service._generate_progress_summary(
            turns,
            ["calm", "hopeful"]
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "calm" in summary or "hopeful" in summary
    
    def test_detect_milestones(self, conversation_service):
        """Test milestone detection"""
        turns = [
            {"user": "I realize now what was causing my anxiety", "ai": "That's a breakthrough"},
            {"user": "I'm going to try the breathing exercises", "ai": "Great commitment"}
        ]
        
        milestones = conversation_service._detect_milestones(turns)
        
        assert "insight" in milestones or "breakthrough" in milestones
        assert "commitment" in milestones
    
    def test_estimate_tokens(self, conversation_service):
        """Test token estimation"""
        text = "This is a test sentence with approximately twenty tokens in it for testing purposes."
        tokens = conversation_service._estimate_tokens(text)
        
        # Should be roughly 20 tokens (text length / 4)
        assert 15 <= tokens <= 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
