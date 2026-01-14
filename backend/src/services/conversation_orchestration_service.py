"""
Conversation Orchestration Service for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Comprehensive session state management, conversation flow control, turn-taking,
interruption handling, and session lifecycle management.

Validates: Requirements 7.1, 7.2
"""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from ..services.session_service import SessionService
from ..services.therapeutic_conversation_engine import (
    TherapeuticConversationEngine,
    ConversationPhase,
    TurnType,
    EmotionalState,
    InterventionType
)
from ..services.conversation_context_service import ConversationContextService
from ..services.agentcore_memory_service import AgentCoreMemoryService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionLifecycleState(Enum):
    """Session lifecycle states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    RESUMING = "resuming"
    COMPLETING = "completing"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    ERROR = "error"


class ConversationFlowState(Enum):
    """Conversation flow states"""
    WAITING_FOR_CLIENT = "waiting_for_client"
    CLIENT_SPEAKING = "client_speaking"
    PROCESSING_INPUT = "processing_input"
    AGENT_RESPONDING = "agent_responding"
    WAITING_FOR_TURN = "waiting_for_turn"
    HANDLING_INTERRUPTION = "handling_interruption"


@dataclass
class SessionStateSnapshot:
    """Comprehensive session state snapshot"""
    session_id: str
    client_id: str
    agent_id: str
    lifecycle_state: SessionLifecycleState
    conversation_flow_state: ConversationFlowState
    conversation_phase: ConversationPhase
    current_speaker: Optional[str]
    turn_count: int
    started_at: datetime
    last_activity: datetime
    pause_count: int = 0
    interruption_count: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationOrchestrationService:
    """
    Service for orchestrating conversation state and flow
    
    Manages session lifecycle, conversation flow control, turn-taking,
    interruption handling, and state transitions.
    """
    
    def __init__(
        self,
        session_service: Optional[SessionService] = None,
        conversation_engine: Optional[TherapeuticConversationEngine] = None,
        context_service: Optional[ConversationContextService] = None,
        memory_service: Optional[AgentCoreMemoryService] = None
    ):
        """
        Initialize conversation orchestration service
        
        Args:
            session_service: Session management service
            conversation_engine: Therapeutic conversation engine
            context_service: Conversation context service
            memory_service: AgentCore memory service
        """
        self.session_service = session_service or SessionService()
        self.conversation_engine = conversation_engine or TherapeuticConversationEngine()
        self.context_service = context_service or ConversationContextService()
        self.memory_service = memory_service or AgentCoreMemoryService()
        
        # Track active session states
        self._session_states: Dict[str, SessionStateSnapshot] = {}
        
        logger.info("Conversation Orchestration Service initialized")
    
    # ========== Session Lifecycle Management ==========
    
    def initialize_session(
        self,
        client_id: str,
        agent_id: str,
        language: str = "en",
        initial_context: Optional[Dict[str, Any]] = None
    ) -> SessionStateSnapshot:
        """
        Initialize a new therapy session with complete state setup
        
        Args:
            client_id: Client user ID
            agent_id: AI agent ID
            language: Session language
            initial_context: Optional initial context data
            
        Returns:
            SessionStateSnapshot with initialized state
        """
        try:
            # Create session in database
            session = self.session_service.create_session(
                client_id=client_id,
                agent_id=agent_id,
                language=language
            )
            
            if not session:
                raise ValueError("Failed to create session")
            
            session_id = session.session_id
            
            # Initialize conversation engine
            conversation_state = self.conversation_engine.start_conversation(
                session_id=session_id,
                client_id=client_id,
                initial_phase=ConversationPhase.OPENING
            )
            
            # Load previous conversation context from AgentCore
            memory = self.memory_service.get_memory(client_id)
            if not memory:
                memory = self.memory_service.create_memory(client_id)
            
            # Create session state snapshot
            state_snapshot = SessionStateSnapshot(
                session_id=session_id,
                client_id=client_id,
                agent_id=agent_id,
                lifecycle_state=SessionLifecycleState.INITIALIZING,
                conversation_flow_state=ConversationFlowState.WAITING_FOR_CLIENT,
                conversation_phase=ConversationPhase.OPENING,
                current_speaker=None,
                turn_count=0,
                started_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                metadata={
                    'language': language,
                    'agent_memory_id': session.agent_memory_id,
                    'initial_context': initial_context or {}
                }
            )
            
            # Store state
            self._session_states[session_id] = state_snapshot
            
            # Transition to active
            self._transition_lifecycle_state(
                session_id,
                SessionLifecycleState.ACTIVE
            )
            
            logger.info(f"Initialized session {session_id} for client {client_id}")
            return state_snapshot
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {str(e)}")
            raise
    
    def get_session_state(self, session_id: str) -> Optional[SessionStateSnapshot]:
        """
        Get current session state snapshot
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionStateSnapshot or None if not found
        """
        return self._session_states.get(session_id)
    
    def pause_session(
        self,
        session_id: str,
        reason: str = "user_requested"
    ) -> bool:
        """
        Pause an active session
        
        Args:
            session_id: Session identifier
            reason: Reason for pausing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                logger.error(f"Session {session_id} not found for pause")
                return False
            
            if state.lifecycle_state != SessionLifecycleState.ACTIVE:
                logger.warning(f"Cannot pause session {session_id} in state {state.lifecycle_state}")
                return False
            
            # Transition to paused
            self._transition_lifecycle_state(session_id, SessionLifecycleState.PAUSED)
            state.pause_count += 1
            state.metadata['pause_reason'] = reason
            state.metadata['paused_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Paused session {session_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause session {session_id}: {str(e)}")
            return False
    
    def resume_session(self, session_id: str) -> bool:
        """
        Resume a paused session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                logger.error(f"Session {session_id} not found for resume")
                return False
            
            if state.lifecycle_state != SessionLifecycleState.PAUSED:
                logger.warning(f"Cannot resume session {session_id} in state {state.lifecycle_state}")
                return False
            
            # Transition through resuming to active
            self._transition_lifecycle_state(session_id, SessionLifecycleState.RESUMING)
            
            # Reload context from AgentCore
            memory = self.memory_service.get_memory(state.client_id)
            if memory:
                state.metadata['context_reloaded'] = True
            
            # Transition to active
            self._transition_lifecycle_state(session_id, SessionLifecycleState.ACTIVE)
            state.metadata['resumed_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Resumed session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {str(e)}")
            return False
    
    def complete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Complete a session and perform cleanup
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session completion summary
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                return {'success': False, 'error': 'Session not found'}
            
            # Transition to completing
            self._transition_lifecycle_state(session_id, SessionLifecycleState.COMPLETING)
            
            # End conversation in engine
            conversation_summary = self.conversation_engine.end_conversation(session_id)
            
            # Complete session in database
            session = self.session_service.get_session(
                session_id,
                state.started_at.isoformat()
            )
            
            if session:
                self.session_service.complete_session(
                    session_id,
                    state.started_at.isoformat()
                )
            
            # Create session summary for AgentCore
            # This would typically include conversation turns
            session_summary = self.context_service.summarize_session(
                client_id=state.client_id,
                session_id=session_id,
                duration_seconds=int((datetime.utcnow() - state.started_at).total_seconds()),
                conversation_turns=[],  # Would be populated from actual turns
                emotional_states=[]
            )
            
            # Transition to completed
            self._transition_lifecycle_state(session_id, SessionLifecycleState.COMPLETED)
            
            # Create completion summary
            completion_summary = {
                'success': True,
                'session_id': session_id,
                'client_id': state.client_id,
                'duration_seconds': int((datetime.utcnow() - state.started_at).total_seconds()),
                'turn_count': state.turn_count,
                'pause_count': state.pause_count,
                'interruption_count': state.interruption_count,
                'final_phase': state.conversation_phase.value,
                'conversation_summary': conversation_summary,
                'completed_at': datetime.utcnow().isoformat()
            }
            
            # Remove from active states
            del self._session_states[session_id]
            
            logger.info(f"Completed session {session_id}")
            return completion_summary
            
        except Exception as e:
            logger.error(f"Failed to complete session {session_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def terminate_session(
        self,
        session_id: str,
        reason: str = "user_terminated"
    ) -> Dict[str, Any]:
        """
        Terminate a session (emergency or user-initiated)
        
        Args:
            session_id: Session identifier
            reason: Termination reason
            
        Returns:
            Termination summary
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                return {'success': False, 'error': 'Session not found'}
            
            # Transition to terminated
            self._transition_lifecycle_state(session_id, SessionLifecycleState.TERMINATED)
            
            # End conversation
            self.conversation_engine.end_conversation(session_id)
            
            # Terminate in database
            session = self.session_service.get_session(
                session_id,
                state.started_at.isoformat()
            )
            
            if session:
                self.session_service.terminate_session(
                    session_id,
                    state.started_at.isoformat(),
                    reason=reason
                )
            
            termination_summary = {
                'success': True,
                'session_id': session_id,
                'reason': reason,
                'duration_seconds': int((datetime.utcnow() - state.started_at).total_seconds()),
                'turn_count': state.turn_count,
                'terminated_at': datetime.utcnow().isoformat()
            }
            
            # Remove from active states
            del self._session_states[session_id]
            
            logger.info(f"Terminated session {session_id}: {reason}")
            return termination_summary
            
        except Exception as e:
            logger.error(f"Failed to terminate session {session_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Conversation Flow Control ==========
    
    def process_client_input(
        self,
        session_id: str,
        input_text: str,
        audio_duration: float = 0.0,
        emotional_state: Optional[EmotionalState] = None
    ) -> Dict[str, Any]:
        """
        Process client input and manage conversation flow
        
        Args:
            session_id: Session identifier
            input_text: Client's input text
            audio_duration: Duration of audio input
            emotional_state: Detected emotional state
            
        Returns:
            Processing result with next action
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                return {'success': False, 'error': 'Session not found'}
            
            # Update flow state
            self._transition_flow_state(session_id, ConversationFlowState.CLIENT_SPEAKING)
            state.current_speaker = "client"
            state.last_activity = datetime.utcnow()
            
            # Add turn to conversation engine
            turn = self.conversation_engine.add_turn(
                session_id=session_id,
                speaker="client",
                content=input_text,
                duration_seconds=audio_duration,
                emotional_state=emotional_state
            )
            
            state.turn_count += 1
            
            # Add to conversation context
            self.context_service.add_conversation_turn(
                client_id=state.client_id,
                session_id=session_id,
                user_message=input_text,
                ai_response="",  # Will be filled when agent responds
                timestamp=datetime.utcnow()
            )
            
            # Transition to processing
            self._transition_flow_state(session_id, ConversationFlowState.PROCESSING_INPUT)
            
            # Select appropriate intervention
            intervention_type, intervention_guidance = self.conversation_engine.select_intervention(
                session_id=session_id,
                client_emotional_state=emotional_state or EmotionalState.NEUTRAL,
                conversation_context=input_text
            )
            
            # Check if phase should advance
            new_phase = self.conversation_engine.advance_conversation_phase(session_id)
            state.conversation_phase = new_phase
            
            # Transition to agent responding
            self._transition_flow_state(session_id, ConversationFlowState.AGENT_RESPONDING)
            
            return {
                'success': True,
                'session_id': session_id,
                'turn_id': turn.turn_id,
                'intervention_type': intervention_type.value,
                'intervention_guidance': intervention_guidance,
                'conversation_phase': new_phase.value,
                'should_respond': True
            }
            
        except Exception as e:
            logger.error(f"Failed to process client input for session {session_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_agent_response(
        self,
        session_id: str,
        response_text: str,
        audio_duration: float = 0.0,
        intervention_type: Optional[InterventionType] = None
    ) -> Dict[str, Any]:
        """
        Process agent response and update conversation state
        
        Args:
            session_id: Session identifier
            response_text: Agent's response text
            audio_duration: Duration of audio response
            intervention_type: Type of intervention used
            
        Returns:
            Processing result
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                return {'success': False, 'error': 'Session not found'}
            
            state.current_speaker = "agent"
            state.last_activity = datetime.utcnow()
            
            # Add turn to conversation engine
            turn = self.conversation_engine.add_turn(
                session_id=session_id,
                speaker="agent",
                content=response_text,
                duration_seconds=audio_duration,
                intervention_type=intervention_type
            )
            
            state.turn_count += 1
            
            # Transition to waiting for client
            self._transition_flow_state(session_id, ConversationFlowState.WAITING_FOR_CLIENT)
            state.current_speaker = None
            
            return {
                'success': True,
                'session_id': session_id,
                'turn_id': turn.turn_id,
                'waiting_for_client': True
            }
            
        except Exception as e:
            logger.error(f"Failed to process agent response for session {session_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Turn-Taking Management ==========
    
    def detect_turn_opportunity(
        self,
        session_id: str,
        silence_duration: float
    ) -> Dict[str, Any]:
        """
        Detect if it's an appropriate time for turn-taking
        
        Args:
            session_id: Session identifier
            silence_duration: Duration of silence in seconds
            
        Returns:
            Turn-taking decision
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                return {'should_take_turn': False, 'error': 'Session not found'}
            
            # Check conversation engine for turn-taking
            should_take_turn = self.conversation_engine.detect_turn_taking(
                session_id=session_id,
                audio_silence_duration=silence_duration
            )
            
            if should_take_turn:
                self._transition_flow_state(session_id, ConversationFlowState.WAITING_FOR_TURN)
            
            return {
                'should_take_turn': should_take_turn,
                'silence_duration': silence_duration,
                'current_flow_state': state.conversation_flow_state.value
            }
            
        except Exception as e:
            logger.error(f"Failed to detect turn opportunity for session {session_id}: {str(e)}")
            return {'should_take_turn': False, 'error': str(e)}
    
    def handle_interruption(
        self,
        session_id: str,
        interrupted_by: str
    ) -> Dict[str, Any]:
        """
        Handle conversation interruption
        
        Args:
            session_id: Session identifier
            interrupted_by: "client" or "agent"
            
        Returns:
            Interruption handling result
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                return {'success': False, 'error': 'Session not found'}
            
            # Transition to handling interruption
            self._transition_flow_state(session_id, ConversationFlowState.HANDLING_INTERRUPTION)
            state.interruption_count += 1
            state.last_activity = datetime.utcnow()
            
            # Handle in conversation engine
            handled = self.conversation_engine.handle_interruption(
                session_id=session_id,
                interrupted_by=interrupted_by
            )
            
            if handled:
                # Transition back to appropriate state
                if interrupted_by == "client":
                    self._transition_flow_state(session_id, ConversationFlowState.CLIENT_SPEAKING)
                else:
                    self._transition_flow_state(session_id, ConversationFlowState.AGENT_RESPONDING)
            
            return {
                'success': handled,
                'session_id': session_id,
                'interrupted_by': interrupted_by,
                'interruption_count': state.interruption_count
            }
            
        except Exception as e:
            logger.error(f"Failed to handle interruption for session {session_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== State Transition Management ==========
    
    def _transition_lifecycle_state(
        self,
        session_id: str,
        new_state: SessionLifecycleState
    ) -> bool:
        """
        Transition session lifecycle state
        
        Args:
            session_id: Session identifier
            new_state: New lifecycle state
            
        Returns:
            True if transition successful
        """
        state = self._session_states.get(session_id)
        if not state:
            return False
        
        old_state = state.lifecycle_state
        state.lifecycle_state = new_state
        state.last_activity = datetime.utcnow()
        
        logger.debug(f"Session {session_id} lifecycle: {old_state.value} -> {new_state.value}")
        return True
    
    def _transition_flow_state(
        self,
        session_id: str,
        new_state: ConversationFlowState
    ) -> bool:
        """
        Transition conversation flow state
        
        Args:
            session_id: Session identifier
            new_state: New flow state
            
        Returns:
            True if transition successful
        """
        state = self._session_states.get(session_id)
        if not state:
            return False
        
        old_state = state.conversation_flow_state
        state.conversation_flow_state = new_state
        state.last_activity = datetime.utcnow()
        
        logger.debug(f"Session {session_id} flow: {old_state.value} -> {new_state.value}")
        return True
    
    # ========== State Monitoring and Reporting ==========
    
    def get_active_sessions(self) -> List[SessionStateSnapshot]:
        """
        Get all active session states
        
        Returns:
            List of active SessionStateSnapshot objects
        """
        return [
            state for state in self._session_states.values()
            if state.lifecycle_state == SessionLifecycleState.ACTIVE
        ]
    
    def get_session_health(self, session_id: str) -> Dict[str, Any]:
        """
        Get session health metrics
        
        Args:
            session_id: Session identifier
            
        Returns:
            Health metrics dictionary
        """
        try:
            state = self._session_states.get(session_id)
            if not state:
                return {'healthy': False, 'error': 'Session not found'}
            
            # Calculate health metrics
            duration_minutes = (datetime.utcnow() - state.started_at).total_seconds() / 60.0
            time_since_activity = (datetime.utcnow() - state.last_activity).total_seconds()
            
            # Get conversation quality metrics
            quality_metrics = self.conversation_engine.monitor_conversation_quality(session_id)
            
            # Determine health status
            is_healthy = (
                state.lifecycle_state == SessionLifecycleState.ACTIVE and
                time_since_activity < 300 and  # Less than 5 minutes idle
                state.error_count == 0 and
                quality_metrics.get('therapeutic_alliance', 0) > 0.3
            )
            
            return {
                'healthy': is_healthy,
                'session_id': session_id,
                'lifecycle_state': state.lifecycle_state.value,
                'flow_state': state.conversation_flow_state.value,
                'duration_minutes': duration_minutes,
                'time_since_activity_seconds': time_since_activity,
                'turn_count': state.turn_count,
                'pause_count': state.pause_count,
                'interruption_count': state.interruption_count,
                'error_count': state.error_count,
                'quality_metrics': quality_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get session health for {session_id}: {str(e)}")
            return {'healthy': False, 'error': str(e)}
    
    def cleanup_stale_sessions(self, max_idle_minutes: int = 30) -> Dict[str, Any]:
        """
        Cleanup sessions that have been idle too long
        
        Args:
            max_idle_minutes: Maximum idle time before cleanup
            
        Returns:
            Cleanup summary
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=max_idle_minutes)
            stale_sessions = []
            
            for session_id, state in list(self._session_states.items()):
                if state.last_activity < cutoff_time:
                    stale_sessions.append(session_id)
                    
                    # Terminate stale session
                    self.terminate_session(session_id, reason="idle_timeout")
            
            logger.info(f"Cleaned up {len(stale_sessions)} stale sessions")
            
            return {
                'success': True,
                'sessions_cleaned': len(stale_sessions),
                'session_ids': stale_sessions,
                'max_idle_minutes': max_idle_minutes
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup stale sessions: {str(e)}")
            return {'success': False, 'error': str(e)}
