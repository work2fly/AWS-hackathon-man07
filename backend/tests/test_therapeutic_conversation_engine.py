"""
Unit tests for Therapeutic Conversation Engine
🏆 Breaking Barriers UK 2026 compliant

Tests conversation flow, turn-taking, interventions, and quality monitoring.
"""

import os
import pytest
from datetime import datetime, timedelta

# Set AWS region before importing services
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from src.services.therapeutic_conversation_engine import (
    TherapeuticConversationEngine,
    ConversationPhase,
    TurnType,
    InterventionType,
    EmotionalState,
    ConversationTurn,
    ConversationState
)


class TestTherapeuticConversationEngine:
    """Test suite for Therapeutic Conversation Engine"""
    
    @pytest.fixture
    def engine(self):
        """Create conversation engine"""
        return TherapeuticConversationEngine()
    
    def test_start_conversation(self, engine):
        """Test starting a new conversation"""
        # Act
        state = engine.start_conversation(
            session_id="session123",
            client_id="client123"
        )
        
        # Assert
        assert state is not None
        assert state.session_id == "session123"
        assert state.client_id == "client123"
        assert state.phase == ConversationPhase.OPENING
        assert len(state.turn_history) == 0
    
    def test_add_client_turn(self, engine):
        """Test adding a client turn"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        
        # Act
        turn = engine.add_turn(
            session_id="session123",
            speaker="client",
            content="I've been feeling anxious lately",
            duration_seconds=5.0,
            emotional_state=EmotionalState.ANXIOUS
        )
        
        # Assert
        assert turn is not None
        assert turn.speaker == "client"
        assert turn.turn_type == TurnType.CLIENT_SPEAKING
        assert turn.emotional_state == EmotionalState.ANXIOUS
        assert len(state.turn_history) == 1
        assert EmotionalState.ANXIOUS in state.emotional_trajectory
    
    def test_add_agent_turn_with_intervention(self, engine):
        """Test adding an agent turn with intervention"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        
        # Act
        turn = engine.add_turn(
            session_id="session123",
            speaker="agent",
            content="I hear that you're feeling anxious. Can you tell me more?",
            duration_seconds=3.0,
            intervention_type=InterventionType.REFLECTION
        )
        
        # Assert
        assert turn is not None
        assert turn.speaker == "agent"
        assert turn.turn_type == TurnType.AGENT_SPEAKING
        assert turn.intervention_type == InterventionType.REFLECTION
        assert InterventionType.REFLECTION in state.interventions_used
    
    def test_turn_taking_detection(self, engine):
        """Test turn-taking detection"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        engine.add_turn("session123", "client", "Hello", 2.0)
        
        # Act - Short silence
        should_take_turn_short = engine.detect_turn_taking("session123", 1.0)
        
        # Assert - Should not take turn
        assert should_take_turn_short is False
        
        # Act - Long silence
        should_take_turn_long = engine.detect_turn_taking("session123", 3.0)
        
        # Assert - Should take turn
        assert should_take_turn_long is True
    
    def test_handle_interruption(self, engine):
        """Test handling interruptions"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        engine.add_turn("session123", "agent", "Let me explain...", 2.0)
        
        # Act
        success = engine.handle_interruption("session123", "client")
        
        # Assert
        assert success is True
        assert state.current_turn.turn_type == TurnType.INTERRUPTION
        assert state.current_turn.speaker == "client"
    
    def test_select_intervention_for_distressed_client(self, engine):
        """Test intervention selection for distressed client"""
        # Arrange
        engine.start_conversation("session123", "client123")
        
        # Act
        intervention_type, guidance = engine.select_intervention(
            session_id="session123",
            client_emotional_state=EmotionalState.DISTRESSED,
            conversation_context="Client expressing distress"
        )
        
        # Assert
        assert intervention_type == InterventionType.VALIDATION
        assert "validate" in guidance.lower()
    
    def test_select_intervention_for_anxious_client(self, engine):
        """Test intervention selection for anxious client"""
        # Arrange
        engine.start_conversation("session123", "client123")
        
        # Act
        intervention_type, guidance = engine.select_intervention(
            session_id="session123",
            client_emotional_state=EmotionalState.ANXIOUS,
            conversation_context="Client expressing anxiety"
        )
        
        # Assert
        assert intervention_type == InterventionType.PSYCHOEDUCATION
        assert "grounding" in guidance.lower() or "breathing" in guidance.lower()
    
    def test_advance_conversation_phase(self, engine):
        """Test conversation phase advancement"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        
        # Add 10 turns to trigger phase advancement
        for i in range(10):
            engine.add_turn("session123", "client" if i % 2 == 0 else "agent", f"Turn {i}", 1.0)
        
        # Act
        new_phase = engine.advance_conversation_phase("session123")
        
        # Assert
        assert new_phase == ConversationPhase.RAPPORT_BUILDING
        assert state.phase == ConversationPhase.RAPPORT_BUILDING
    
    def test_assess_rapport(self, engine):
        """Test rapport assessment"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        
        # Add turns with positive emotions
        for i in range(5):
            engine.add_turn(
                "session123",
                "client",
                f"Turn {i}",
                2.0,
                emotional_state=EmotionalState.HOPEFUL
            )
        
        # Act
        rapport_score = engine.assess_rapport("session123")
        
        # Assert
        assert 0.0 <= rapport_score <= 1.0
        assert rapport_score > 0.5  # Should be higher due to positive emotions
    
    def test_assess_engagement(self, engine):
        """Test engagement assessment"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        
        # Add client turns with varying durations
        engine.add_turn("session123", "client", "Turn 1", 10.0)
        engine.add_turn("session123", "client", "Turn 2", 15.0)
        engine.add_turn("session123", "client", "Turn 3", 20.0)
        
        # Act
        engagement_score = engine.assess_engagement("session123")
        
        # Assert
        assert 0.0 <= engagement_score <= 1.0
        assert engagement_score > 0.3  # Should be moderate due to decent turn durations
    
    def test_monitor_conversation_quality(self, engine):
        """Test conversation quality monitoring"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        
        # Add some turns
        engine.add_turn("session123", "client", "Hello", 2.0, EmotionalState.CALM)
        engine.add_turn("session123", "agent", "Hi there", 1.0, intervention_type=InterventionType.REFLECTION)
        engine.add_turn("session123", "client", "I'm anxious", 3.0, EmotionalState.ANXIOUS)
        
        # Act
        quality_metrics = engine.monitor_conversation_quality("session123")
        
        # Assert
        assert "rapport_score" in quality_metrics
        assert "engagement_score" in quality_metrics
        assert "therapeutic_alliance" in quality_metrics
        assert "turn_count" in quality_metrics
        assert quality_metrics["turn_count"] == 3
        assert quality_metrics["phase"] == ConversationPhase.OPENING.value
    
    def test_end_conversation(self, engine):
        """Test ending a conversation"""
        # Arrange
        state = engine.start_conversation("session123", "client123")
        engine.add_turn("session123", "client", "Thank you", 2.0)
        engine.add_turn("session123", "agent", "You're welcome", 1.0)
        
        # Act
        summary = engine.end_conversation("session123")
        
        # Assert
        assert "session_id" in summary
        assert summary["session_id"] == "session123"
        assert "turn_count" in summary
        assert summary["turn_count"] == 2
        assert "quality_metrics" in summary
        
        # Verify conversation is removed
        assert engine.get_conversation_state("session123") is None
    
    def test_multiple_conversations(self, engine):
        """Test managing multiple conversations"""
        # Act
        state1 = engine.start_conversation("session1", "client1")
        state2 = engine.start_conversation("session2", "client2")
        
        engine.add_turn("session1", "client", "Hello from session 1", 2.0)
        engine.add_turn("session2", "client", "Hello from session 2", 2.0)
        
        # Assert
        assert engine.get_conversation_state("session1") is not None
        assert engine.get_conversation_state("session2") is not None
        assert len(state1.turn_history) == 1
        assert len(state2.turn_history) == 1
