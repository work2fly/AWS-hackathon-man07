"""
Unit tests for Conversation Orchestration Service
🏆 Breaking Barriers UK 2026 compliant

Tests session state management, conversation flow control, turn-taking,
and interruption handling.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from src.services.conversation_orchestration_service import (
    ConversationOrchestrationService,
    SessionLifecycleState,
    ConversationFlowState,
    SessionStateSnapshot
)
from src.services.therapeutic_conversation_engine import (
    ConversationPhase,
    EmotionalState,
    InterventionType
)
from src.models.session import TherapySession, SessionStatus


class TestConversationOrchestrationService:
    """Test suite for conversation orchestration service"""
    
    @pytest.fixture
    def mock_session_service(self):
        """Create mock session service"""
        service = Mock()
        
        # Create a side effect that generates unique session IDs
        def create_session_side_effect(client_id, agent_id, language="en"):
            import uuid
            return TherapySession(
                session_id=f"test_session_{uuid.uuid4().hex[:8]}",
                timestamp=datetime.utcnow(),
                client_id=client_id,
                agent_id=agent_id,
                status=SessionStatus.ACTIVE,
                start_time=datetime.utcnow(),
                language=language,
                agent_memory_id=f"memory_{client_id}"
            )
        
        service.create_session.side_effect = create_session_side_effect
        return service
    
    @pytest.fixture
    def mock_conversation_engine(self):
        """Create mock conversation engine"""
        engine = Mock()
        
        # Create side effect for start_conversation
        def start_conversation_side_effect(session_id, client_id, initial_phase=ConversationPhase.OPENING):
            return Mock(
                session_id=session_id,
                client_id=client_id,
                phase=initial_phase
            )
        
        engine.start_conversation.side_effect = start_conversation_side_effect
        engine.add_turn.return_value = Mock(turn_id="turn_1")
        engine.select_intervention.return_value = (
            InterventionType.REFLECTION,
            "Reflect on client's feelings"
        )
        engine.advance_conversation_phase.return_value = ConversationPhase.OPENING
        engine.detect_turn_taking.return_value = True
        engine.handle_interruption.return_value = True
        engine.end_conversation.return_value = {'session_id': 'test_session_123'}
        engine.monitor_conversation_quality.return_value = {
            'therapeutic_alliance': 0.7,
            'rapport_score': 0.6,
            'engagement_score': 0.8
        }
        return engine
    
    @pytest.fixture
    def mock_context_service(self):
        """Create mock context service"""
        service = Mock()
        service.add_conversation_turn.return_value = {}
        service.summarize_session.return_value = Mock(
            session_id="test_session_123",
            duration_seconds=1800
        )
        return service
    
    @pytest.fixture
    def mock_memory_service(self):
        """Create mock memory service"""
        service = Mock()
        service.get_memory.return_value = Mock(
            client_id="client_123",
            conversation_context=Mock()
        )
        service.create_memory.return_value = Mock(
            client_id="client_123"
        )
        return service
    
    @pytest.fixture
    def orchestration_service(
        self,
        mock_session_service,
        mock_conversation_engine,
        mock_context_service,
        mock_memory_service
    ):
        """Create orchestration service with mocked dependencies"""
        return ConversationOrchestrationService(
            session_service=mock_session_service,
            conversation_engine=mock_conversation_engine,
            context_service=mock_context_service,
            memory_service=mock_memory_service
        )
    
    # ========== Session Lifecycle Tests ==========
    
    def test_initialize_session_success(self, orchestration_service):
        """Test successful session initialization"""
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456",
            language="en"
        )
        
        assert state is not None
        assert state.session_id.startswith("test_session_")
        assert state.client_id == "client_123"
        assert state.agent_id == "agent_456"
        assert state.lifecycle_state == SessionLifecycleState.ACTIVE
        assert state.conversation_flow_state == ConversationFlowState.WAITING_FOR_CLIENT
        assert state.conversation_phase == ConversationPhase.OPENING
        assert state.turn_count == 0
    
    def test_get_session_state(self, orchestration_service):
        """Test retrieving session state"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Retrieve state
        retrieved_state = orchestration_service.get_session_state(state.session_id)
        
        assert retrieved_state is not None
        assert retrieved_state.session_id == state.session_id
        assert retrieved_state.client_id == state.client_id
    
    def test_pause_session(self, orchestration_service):
        """Test pausing an active session"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Pause session
        success = orchestration_service.pause_session(
            state.session_id,
            reason="user_requested"
        )
        
        assert success is True
        
        # Verify state
        updated_state = orchestration_service.get_session_state(state.session_id)
        assert updated_state.lifecycle_state == SessionLifecycleState.PAUSED
        assert updated_state.pause_count == 1
        assert 'pause_reason' in updated_state.metadata
    
    def test_resume_session(self, orchestration_service):
        """Test resuming a paused session"""
        # Initialize and pause session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        orchestration_service.pause_session(state.session_id)
        
        # Resume session
        success = orchestration_service.resume_session(state.session_id)
        
        assert success is True
        
        # Verify state
        updated_state = orchestration_service.get_session_state(state.session_id)
        assert updated_state.lifecycle_state == SessionLifecycleState.ACTIVE
        assert 'resumed_at' in updated_state.metadata
    
    def test_complete_session(self, orchestration_service, mock_session_service):
        """Test completing a session"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Mock get_session
        mock_session_service.get_session.return_value = Mock(
            session_id=state.session_id
        )
        
        # Complete session
        result = orchestration_service.complete_session(state.session_id)
        
        assert result['success'] is True
        assert result['session_id'] == state.session_id
        assert 'duration_seconds' in result
        assert 'turn_count' in result
        
        # Verify session removed from active states
        assert orchestration_service.get_session_state(state.session_id) is None
    
    def test_terminate_session(self, orchestration_service, mock_session_service):
        """Test terminating a session"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Mock get_session
        mock_session_service.get_session.return_value = Mock(
            session_id=state.session_id
        )
        
        # Terminate session
        result = orchestration_service.terminate_session(
            state.session_id,
            reason="emergency"
        )
        
        assert result['success'] is True
        assert result['reason'] == "emergency"
        
        # Verify session removed
        assert orchestration_service.get_session_state(state.session_id) is None
    
    # ========== Conversation Flow Tests ==========
    
    def test_process_client_input(self, orchestration_service):
        """Test processing client input"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Process client input
        result = orchestration_service.process_client_input(
            session_id=state.session_id,
            input_text="I'm feeling anxious today",
            audio_duration=3.5,
            emotional_state=EmotionalState.ANXIOUS
        )
        
        assert result['success'] is True
        assert result['should_respond'] is True
        assert 'intervention_type' in result
        assert 'intervention_guidance' in result
        
        # Verify state updated
        updated_state = orchestration_service.get_session_state(state.session_id)
        assert updated_state.turn_count == 1
        assert updated_state.conversation_flow_state == ConversationFlowState.AGENT_RESPONDING
    
    def test_process_agent_response(self, orchestration_service):
        """Test processing agent response"""
        # Initialize session and process client input
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        orchestration_service.process_client_input(
            session_id=state.session_id,
            input_text="I'm feeling anxious",
            emotional_state=EmotionalState.ANXIOUS
        )
        
        # Process agent response
        result = orchestration_service.process_agent_response(
            session_id=state.session_id,
            response_text="I hear that you're feeling anxious. Can you tell me more?",
            audio_duration=4.0,
            intervention_type=InterventionType.REFLECTION
        )
        
        assert result['success'] is True
        assert result['waiting_for_client'] is True
        
        # Verify state updated
        updated_state = orchestration_service.get_session_state(state.session_id)
        assert updated_state.turn_count == 2
        assert updated_state.conversation_flow_state == ConversationFlowState.WAITING_FOR_CLIENT
        assert updated_state.current_speaker is None
    
    # ========== Turn-Taking Tests ==========
    
    def test_detect_turn_opportunity(self, orchestration_service):
        """Test detecting turn-taking opportunity"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Detect turn opportunity
        result = orchestration_service.detect_turn_opportunity(
            session_id=state.session_id,
            silence_duration=2.5
        )
        
        assert 'should_take_turn' in result
        assert 'silence_duration' in result
        assert result['silence_duration'] == 2.5
    
    def test_handle_interruption(self, orchestration_service):
        """Test handling conversation interruption"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Handle interruption
        result = orchestration_service.handle_interruption(
            session_id=state.session_id,
            interrupted_by="client"
        )
        
        assert result['success'] is True
        assert result['interrupted_by'] == "client"
        
        # Verify state updated
        updated_state = orchestration_service.get_session_state(state.session_id)
        assert updated_state.interruption_count == 1
    
    # ========== State Monitoring Tests ==========
    
    def test_get_active_sessions(self, orchestration_service):
        """Test retrieving active sessions"""
        # Initialize multiple sessions
        state1 = orchestration_service.initialize_session(
            client_id="client_1",
            agent_id="agent_1"
        )
        state2 = orchestration_service.initialize_session(
            client_id="client_2",
            agent_id="agent_2"
        )
        
        # Get active sessions
        active_sessions = orchestration_service.get_active_sessions()
        
        assert len(active_sessions) == 2
        assert all(s.lifecycle_state == SessionLifecycleState.ACTIVE for s in active_sessions)
    
    def test_get_session_health(self, orchestration_service):
        """Test getting session health metrics"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Get health metrics
        health = orchestration_service.get_session_health(state.session_id)
        
        assert 'healthy' in health
        assert 'lifecycle_state' in health
        assert 'flow_state' in health
        assert 'turn_count' in health
        assert 'quality_metrics' in health
    
    def test_cleanup_stale_sessions(self, orchestration_service, mock_session_service):
        """Test cleaning up stale sessions"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Mock get_session for termination
        mock_session_service.get_session.return_value = Mock(
            session_id=state.session_id
        )
        
        # Manually set last_activity to old time
        session_state = orchestration_service.get_session_state(state.session_id)
        session_state.last_activity = datetime.utcnow() - timedelta(minutes=35)
        
        # Cleanup stale sessions
        result = orchestration_service.cleanup_stale_sessions(max_idle_minutes=30)
        
        assert result['success'] is True
        assert result['sessions_cleaned'] == 1
        assert state.session_id in result['session_ids']
    
    # ========== Edge Cases ==========
    
    def test_pause_non_active_session(self, orchestration_service):
        """Test pausing a non-active session fails gracefully"""
        # Initialize and complete session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Manually set to completed
        session_state = orchestration_service.get_session_state(state.session_id)
        session_state.lifecycle_state = SessionLifecycleState.COMPLETED
        
        # Try to pause
        success = orchestration_service.pause_session(state.session_id)
        
        assert success is False
    
    def test_process_input_for_nonexistent_session(self, orchestration_service):
        """Test processing input for non-existent session"""
        result = orchestration_service.process_client_input(
            session_id="nonexistent_session",
            input_text="Hello"
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_multiple_interruptions_tracked(self, orchestration_service):
        """Test multiple interruptions are tracked correctly"""
        # Initialize session
        state = orchestration_service.initialize_session(
            client_id="client_123",
            agent_id="agent_456"
        )
        
        # Handle multiple interruptions
        orchestration_service.handle_interruption(state.session_id, "client")
        orchestration_service.handle_interruption(state.session_id, "agent")
        orchestration_service.handle_interruption(state.session_id, "client")
        
        # Verify count
        updated_state = orchestration_service.get_session_state(state.session_id)
        assert updated_state.interruption_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
