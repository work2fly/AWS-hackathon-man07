"""
Therapeutic Conversation Engine for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Handles conversation flow management, turn-taking, therapeutic intervention,
emotional intelligence, and conversation quality monitoring.

Requirements: 3.4, 3.7
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ConversationPhase(Enum):
    """Phases of a therapeutic conversation"""
    OPENING = "opening"
    RAPPORT_BUILDING = "rapport_building"
    EXPLORATION = "exploration"
    INTERVENTION = "intervention"
    CLOSURE = "closure"
    FOLLOW_UP = "follow_up"


class TurnType(Enum):
    """Types of conversation turns"""
    CLIENT_SPEAKING = "client_speaking"
    AGENT_SPEAKING = "agent_speaking"
    CLIENT_PAUSE = "client_pause"
    AGENT_LISTENING = "agent_listening"
    INTERRUPTION = "interruption"


class InterventionType(Enum):
    """Types of therapeutic interventions"""
    REFLECTION = "reflection"  # Reflecting back client's feelings
    CLARIFICATION = "clarification"  # Asking for clarification
    VALIDATION = "validation"  # Validating client's experience
    REFRAMING = "reframing"  # Offering alternative perspective
    PSYCHOEDUCATION = "psychoeducation"  # Teaching coping skills
    GOAL_SETTING = "goal_setting"  # Setting therapeutic goals
    HOMEWORK = "homework"  # Suggesting between-session activities
    CRISIS_RESPONSE = "crisis_response"  # Responding to crisis indicators


class EmotionalState(Enum):
    """Detected emotional states"""
    CALM = "calm"
    ANXIOUS = "anxious"
    SAD = "sad"
    ANGRY = "angry"
    HOPEFUL = "hopeful"
    CONFUSED = "confused"
    DISTRESSED = "distressed"
    NEUTRAL = "neutral"


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation"""
    turn_id: str
    turn_type: TurnType
    speaker: str  # "client" or "agent"
    content: str
    timestamp: datetime
    duration_seconds: float
    emotional_state: Optional[EmotionalState] = None
    intervention_type: Optional[InterventionType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationState:
    """Current state of the conversation"""
    session_id: str
    client_id: str
    phase: ConversationPhase
    turn_history: List[ConversationTurn] = field(default_factory=list)
    current_turn: Optional[ConversationTurn] = None
    emotional_trajectory: List[EmotionalState] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    interventions_used: List[InterventionType] = field(default_factory=list)
    rapport_score: float = 0.5  # 0.0 to 1.0
    engagement_score: float = 0.5  # 0.0 to 1.0
    therapeutic_alliance: float = 0.5  # 0.0 to 1.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)


class TherapeuticConversationEngine:
    """
    Engine for managing therapeutic conversations
    
    Handles conversation flow, turn-taking, therapeutic interventions,
    emotional intelligence, and quality monitoring.
    """
    
    def __init__(self):
        """Initialize conversation engine"""
        self._active_conversations: Dict[str, ConversationState] = {}
        logger.info("Therapeutic Conversation Engine initialized")
    
    def start_conversation(
        self,
        session_id: str,
        client_id: str,
        initial_phase: ConversationPhase = ConversationPhase.OPENING
    ) -> ConversationState:
        """
        Start a new therapeutic conversation
        
        Args:
            session_id: Unique session identifier
            client_id: Client user ID
            initial_phase: Starting phase of conversation
            
        Returns:
            ConversationState object
        """
        if session_id in self._active_conversations:
            logger.warning(f"Conversation {session_id} already exists, returning existing state")
            return self._active_conversations[session_id]
        
        state = ConversationState(
            session_id=session_id,
            client_id=client_id,
            phase=initial_phase
        )
        
        self._active_conversations[session_id] = state
        
        logger.info(f"Started conversation for session {session_id}, client {client_id}")
        return state
    
    def get_conversation_state(self, session_id: str) -> Optional[ConversationState]:
        """
        Get current conversation state
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationState or None if not found
        """
        return self._active_conversations.get(session_id)
    
    def add_turn(
        self,
        session_id: str,
        speaker: str,
        content: str,
        duration_seconds: float = 0.0,
        emotional_state: Optional[EmotionalState] = None,
        intervention_type: Optional[InterventionType] = None
    ) -> ConversationTurn:
        """
        Add a conversation turn
        
        Args:
            session_id: Session identifier
            speaker: "client" or "agent"
            content: Turn content
            duration_seconds: Duration of the turn
            emotional_state: Detected emotional state
            intervention_type: Type of intervention (if agent turn)
            
        Returns:
            ConversationTurn object
        """
        state = self._active_conversations.get(session_id)
        if not state:
            raise ValueError(f"Conversation {session_id} not found")
        
        # Determine turn type
        if speaker == "client":
            turn_type = TurnType.CLIENT_SPEAKING
        else:
            turn_type = TurnType.AGENT_SPEAKING
        
        # Create turn
        turn = ConversationTurn(
            turn_id=f"{session_id}_turn_{len(state.turn_history)}",
            turn_type=turn_type,
            speaker=speaker,
            content=content,
            timestamp=datetime.utcnow(),
            duration_seconds=duration_seconds,
            emotional_state=emotional_state,
            intervention_type=intervention_type
        )
        
        # Update state
        state.turn_history.append(turn)
        state.current_turn = turn
        state.last_activity = datetime.utcnow()
        
        # Track emotional trajectory
        if emotional_state:
            state.emotional_trajectory.append(emotional_state)
        
        # Track interventions
        if intervention_type:
            state.interventions_used.append(intervention_type)
        
        logger.debug(f"Added turn to conversation {session_id}: {speaker}")
        return turn
    
    def detect_turn_taking(
        self,
        session_id: str,
        audio_silence_duration: float
    ) -> bool:
        """
        Detect if it's time for turn-taking
        
        Args:
            session_id: Session identifier
            audio_silence_duration: Duration of silence in seconds
            
        Returns:
            True if turn should be taken, False otherwise
        """
        # Simple heuristic: if silence > 2 seconds, take turn
        SILENCE_THRESHOLD = 2.0
        
        state = self._active_conversations.get(session_id)
        if not state:
            return False
        
        # Check if current turn is client speaking
        if state.current_turn and state.current_turn.turn_type == TurnType.CLIENT_SPEAKING:
            if audio_silence_duration > SILENCE_THRESHOLD:
                logger.debug(f"Turn-taking detected for session {session_id}")
                return True
        
        return False
    
    def handle_interruption(
        self,
        session_id: str,
        interrupted_by: str
    ) -> bool:
        """
        Handle conversation interruption
        
        Args:
            session_id: Session identifier
            interrupted_by: "client" or "agent"
            
        Returns:
            True if interruption handled, False otherwise
        """
        state = self._active_conversations.get(session_id)
        if not state:
            return False
        
        # Create interruption turn
        turn = ConversationTurn(
            turn_id=f"{session_id}_interrupt_{len(state.turn_history)}",
            turn_type=TurnType.INTERRUPTION,
            speaker=interrupted_by,
            content="[Interruption]",
            timestamp=datetime.utcnow(),
            duration_seconds=0.0
        )
        
        state.turn_history.append(turn)
        state.current_turn = turn
        
        logger.info(f"Handled interruption in session {session_id} by {interrupted_by}")
        return True
    
    def select_intervention(
        self,
        session_id: str,
        client_emotional_state: EmotionalState,
        conversation_context: str
    ) -> Tuple[InterventionType, str]:
        """
        Select appropriate therapeutic intervention
        
        Args:
            session_id: Session identifier
            client_emotional_state: Current emotional state
            conversation_context: Recent conversation context
            
        Returns:
            Tuple of (intervention_type, intervention_guidance)
        """
        state = self._active_conversations.get(session_id)
        if not state:
            return InterventionType.REFLECTION, "Reflect on client's feelings"
        
        # Select intervention based on emotional state and phase
        if client_emotional_state == EmotionalState.DISTRESSED:
            return InterventionType.VALIDATION, "Validate client's distress and provide support"
        
        elif client_emotional_state == EmotionalState.ANXIOUS:
            return InterventionType.PSYCHOEDUCATION, "Teach grounding or breathing techniques"
        
        elif client_emotional_state == EmotionalState.CONFUSED:
            return InterventionType.CLARIFICATION, "Ask clarifying questions to understand better"
        
        elif client_emotional_state == EmotionalState.SAD:
            return InterventionType.REFLECTION, "Reflect back feelings and show empathy"
        
        elif client_emotional_state == EmotionalState.HOPEFUL:
            return InterventionType.GOAL_SETTING, "Explore goals and action steps"
        
        # Default to reflection
        return InterventionType.REFLECTION, "Reflect on what client shared"
    
    def advance_conversation_phase(
        self,
        session_id: str
    ) -> ConversationPhase:
        """
        Advance conversation to next appropriate phase
        
        Args:
            session_id: Session identifier
            
        Returns:
            New conversation phase
        """
        state = self._active_conversations.get(session_id)
        if not state:
            return ConversationPhase.OPENING
        
        # Phase progression logic
        phase_progression = {
            ConversationPhase.OPENING: ConversationPhase.RAPPORT_BUILDING,
            ConversationPhase.RAPPORT_BUILDING: ConversationPhase.EXPLORATION,
            ConversationPhase.EXPLORATION: ConversationPhase.INTERVENTION,
            ConversationPhase.INTERVENTION: ConversationPhase.CLOSURE,
            ConversationPhase.CLOSURE: ConversationPhase.FOLLOW_UP,
            ConversationPhase.FOLLOW_UP: ConversationPhase.FOLLOW_UP  # Stay in follow-up
        }
        
        # Check if ready to advance
        turn_count = len(state.turn_history)
        
        # Simple heuristic: advance every 10 turns
        if turn_count > 0 and turn_count % 10 == 0:
            new_phase = phase_progression.get(state.phase, state.phase)
            state.phase = new_phase
            logger.info(f"Advanced conversation {session_id} to phase {new_phase.value}")
            return new_phase
        
        return state.phase
    
    def assess_rapport(
        self,
        session_id: str
    ) -> float:
        """
        Assess rapport level (0.0 to 1.0)
        
        Args:
            session_id: Session identifier
            
        Returns:
            Rapport score
        """
        state = self._active_conversations.get(session_id)
        if not state:
            return 0.5
        
        # Simple heuristic based on turn count and emotional trajectory
        turn_count = len(state.turn_history)
        
        # More turns = better rapport (up to a point)
        turn_score = min(turn_count / 20.0, 0.5)
        
        # Positive emotional states increase rapport
        positive_emotions = [EmotionalState.CALM, EmotionalState.HOPEFUL]
        positive_count = sum(1 for e in state.emotional_trajectory if e in positive_emotions)
        emotion_score = min(positive_count / max(len(state.emotional_trajectory), 1), 0.5)
        
        rapport_score = turn_score + emotion_score
        state.rapport_score = rapport_score
        
        return rapport_score
    
    def assess_engagement(
        self,
        session_id: str
    ) -> float:
        """
        Assess client engagement level (0.0 to 1.0)
        
        Args:
            session_id: Session identifier
            
        Returns:
            Engagement score
        """
        state = self._active_conversations.get(session_id)
        if not state:
            return 0.5
        
        # Simple heuristic based on turn frequency and duration
        if not state.turn_history:
            return 0.5
        
        # Calculate average turn duration for client
        client_turns = [t for t in state.turn_history if t.speaker == "client"]
        if not client_turns:
            return 0.5
        
        avg_duration = sum(t.duration_seconds for t in client_turns) / len(client_turns)
        
        # Longer turns = higher engagement (up to a point)
        engagement_score = min(avg_duration / 30.0, 1.0)  # 30 seconds = max engagement
        state.engagement_score = engagement_score
        
        return engagement_score
    
    def monitor_conversation_quality(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Monitor overall conversation quality
        
        Args:
            session_id: Session identifier
            
        Returns:
            Quality metrics dictionary
        """
        state = self._active_conversations.get(session_id)
        if not state:
            return {"error": "Conversation not found"}
        
        rapport = self.assess_rapport(session_id)
        engagement = self.assess_engagement(session_id)
        
        # Calculate therapeutic alliance (combination of rapport and engagement)
        therapeutic_alliance = (rapport + engagement) / 2.0
        state.therapeutic_alliance = therapeutic_alliance
        
        # Assess intervention diversity
        unique_interventions = len(set(state.interventions_used))
        intervention_diversity = min(unique_interventions / 5.0, 1.0)  # 5 types = max diversity
        
        return {
            "session_id": session_id,
            "rapport_score": rapport,
            "engagement_score": engagement,
            "therapeutic_alliance": therapeutic_alliance,
            "intervention_diversity": intervention_diversity,
            "turn_count": len(state.turn_history),
            "phase": state.phase.value,
            "duration_minutes": (datetime.utcnow() - state.started_at).total_seconds() / 60.0,
            "topics_discussed": state.topics_discussed,
            "emotional_trajectory": [e.value for e in state.emotional_trajectory[-5:]]  # Last 5
        }
    
    def end_conversation(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        End conversation and return summary
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation summary
        """
        state = self._active_conversations.get(session_id)
        if not state:
            return {"error": "Conversation not found"}
        
        # Get final quality metrics
        quality_metrics = self.monitor_conversation_quality(session_id)
        
        # Create summary
        summary = {
            "session_id": session_id,
            "client_id": state.client_id,
            "started_at": state.started_at.isoformat(),
            "ended_at": datetime.utcnow().isoformat(),
            "duration_minutes": quality_metrics["duration_minutes"],
            "turn_count": len(state.turn_history),
            "final_phase": state.phase.value,
            "quality_metrics": quality_metrics,
            "interventions_used": [i.value for i in set(state.interventions_used)],
            "topics_discussed": state.topics_discussed
        }
        
        # Remove from active conversations
        del self._active_conversations[session_id]
        
        logger.info(f"Ended conversation for session {session_id}")
        return summary


# Global conversation engine instance
therapeutic_conversation_engine = TherapeuticConversationEngine()
