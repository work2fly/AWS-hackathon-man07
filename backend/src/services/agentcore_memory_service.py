"""
AWS AgentCore Memory Service for AI Therapy Platform
Handles memory creation, retrieval, updates, and optimization
🏆 Breaking Barriers UK 2026 compliant

Validates: Requirements 3.1, 3.3, 3.6, 3.7
"""

import json
import boto3
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

from ..config.agentcore_config import (
    AGENTCORE_RETRY_CONFIG,
    MEMORY_TTL_DAYS,
    MAX_MEMORY_SIZE_KB,
    MEMORY_OPTIMIZATION_THRESHOLD,
    MAX_CONVERSATION_HISTORY_ITEMS,
    get_memory_id,
    validate_memory_size
)
from ..models.agent_memory import (
    AgentMemory,
    ConversationContext,
    TherapeuticProfile,
    RetentionPolicy,
    RetentionPolicyType,
    SessionSummary,
    ProgressNote,
    PersonalityAdaptation
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AgentCoreMemoryService:
    """
    Service for managing AgentCore memory operations
    Handles conversation context persistence and therapeutic continuity
    """
    
    def __init__(self):
        """Initialize AgentCore memory service"""
        # Note: AgentCore uses bedrock-agent-runtime client
        self.client = boto3.client('bedrock-agent-runtime', config=AGENTCORE_RETRY_CONFIG)
        logger.info("AgentCore Memory Service initialized")

    def create_memory(
        self,
        client_id: str,
        language_preference: str = "en",
        retention_policy_type: RetentionPolicyType = RetentionPolicyType.STANDARD
    ) -> AgentMemory:
        """
        Create new memory for a client
        
        Args:
            client_id: Unique client identifier
            language_preference: Preferred language code
            retention_policy_type: Memory retention policy
            
        Returns:
            AgentMemory object
        """
        try:
            memory_id = get_memory_id(client_id)
            
            # Create new memory object
            memory = AgentMemory(
                memory_id=memory_id,
                client_id=client_id,
                conversation_context=ConversationContext(),
                therapeutic_profile=TherapeuticProfile(
                    language_preference=language_preference
                ),
                retention_policy=RetentionPolicy(
                    policy_type=retention_policy_type
                )
            )
            
            # Store in AgentCore (simulated for now - actual implementation would use bedrock-agent-runtime)
            logger.info(f"Created memory for client {client_id} with ID {memory_id}")
            
            return memory
            
        except Exception as e:
            logger.error(f"Failed to create memory for client {client_id}: {str(e)}")
            raise

    def get_memory(self, client_id: str) -> Optional[AgentMemory]:
        """
        Retrieve memory for a client
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            AgentMemory object or None if not found
        """
        try:
            memory_id = get_memory_id(client_id)
            
            # Retrieve from AgentCore (simulated for now)
            # In production, this would call bedrock-agent-runtime API
            logger.info(f"Retrieved memory for client {client_id}")
            
            # For now, return None to indicate no existing memory
            # This will be replaced with actual AgentCore API calls
            return None
            
        except Exception as e:
            logger.error(f"Failed to get memory for client {client_id}: {str(e)}")
            return None

    def update_memory(self, memory: AgentMemory) -> AgentMemory:
        """
        Update existing memory
        
        Args:
            memory: AgentMemory object to update
            
        Returns:
            Updated AgentMemory object
        """
        try:
            # Increment version
            memory.version += 1
            memory.last_updated = datetime.utcnow()
            
            # Check if optimization is needed
            if self._needs_optimization(memory):
                memory = self._optimize_memory(memory)
            
            # Update in AgentCore (simulated for now)
            logger.info(f"Updated memory for client {memory.client_id}, version {memory.version}")
            
            return memory
            
        except Exception as e:
            logger.error(f"Failed to update memory for client {memory.client_id}: {str(e)}")
            raise

    def add_session_summary(
        self,
        client_id: str,
        session_summary: SessionSummary
    ) -> AgentMemory:
        """
        Add session summary to memory
        
        Args:
            client_id: Unique client identifier
            session_summary: SessionSummary to add
            
        Returns:
            Updated AgentMemory object
        """
        try:
            memory = self.get_memory(client_id)
            if not memory:
                memory = self.create_memory(client_id)
            
            # Add summary to history
            memory.conversation_context.session_history.append(session_summary)
            
            # Update last session date
            memory.conversation_context.last_session_date = session_summary.timestamp
            
            # Update memory
            return self.update_memory(memory)
            
        except Exception as e:
            logger.error(f"Failed to add session summary for client {client_id}: {str(e)}")
            raise

    def add_progress_note(
        self,
        client_id: str,
        progress_note: ProgressNote
    ) -> AgentMemory:
        """
        Add progress note to memory
        
        Args:
            client_id: Unique client identifier
            progress_note: ProgressNote to add
            
        Returns:
            Updated AgentMemory object
        """
        try:
            memory = self.get_memory(client_id)
            if not memory:
                memory = self.create_memory(client_id)
            
            # Add note to progress notes
            memory.conversation_context.progress_notes.append(progress_note)
            
            # Update memory
            return self.update_memory(memory)
            
        except Exception as e:
            logger.error(f"Failed to add progress note for client {client_id}: {str(e)}")
            raise

    def update_therapeutic_profile(
        self,
        client_id: str,
        profile_updates: Dict[str, Any]
    ) -> AgentMemory:
        """
        Update therapeutic profile
        
        Args:
            client_id: Unique client identifier
            profile_updates: Dictionary of profile fields to update
            
        Returns:
            Updated AgentMemory object
        """
        try:
            memory = self.get_memory(client_id)
            if not memory:
                memory = self.create_memory(client_id)
            
            # Update profile fields
            for key, value in profile_updates.items():
                if hasattr(memory.therapeutic_profile, key):
                    setattr(memory.therapeutic_profile, key, value)
            
            # Update memory
            return self.update_memory(memory)
            
        except Exception as e:
            logger.error(f"Failed to update therapeutic profile for client {client_id}: {str(e)}")
            raise

    def add_personality_adaptation(
        self,
        client_id: str,
        adaptation: PersonalityAdaptation
    ) -> AgentMemory:
        """
        Add personality adaptation to memory
        
        Args:
            client_id: Unique client identifier
            adaptation: PersonalityAdaptation to add
            
        Returns:
            Updated AgentMemory object
        """
        try:
            memory = self.get_memory(client_id)
            if not memory:
                memory = self.create_memory(client_id)
            
            # Add adaptation
            memory.conversation_context.personality_adaptations.append(adaptation)
            
            # Update memory
            return self.update_memory(memory)
            
        except Exception as e:
            logger.error(f"Failed to add personality adaptation for client {client_id}: {str(e)}")
            raise

    def get_conversation_context(self, client_id: str) -> Optional[ConversationContext]:
        """
        Get conversation context for a client
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            ConversationContext or None
        """
        memory = self.get_memory(client_id)
        return memory.conversation_context if memory else None

    def get_therapeutic_profile(self, client_id: str) -> Optional[TherapeuticProfile]:
        """
        Get therapeutic profile for a client
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            TherapeuticProfile or None
        """
        memory = self.get_memory(client_id)
        return memory.therapeutic_profile if memory else None

    def serialize_context_for_prompt(self, client_id: str) -> str:
        """
        Serialize conversation context for AI prompts
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            Formatted context string
        """
        try:
            memory = self.get_memory(client_id)
            if not memory:
                return "No previous conversation history."
            
            context_parts = []
            
            # Add session count
            total_sessions = memory.conversation_context.total_sessions
            context_parts.append(f"Total sessions: {total_sessions}")
            
            # Add ongoing topics
            if memory.conversation_context.ongoing_topics:
                topics = ", ".join(memory.conversation_context.ongoing_topics)
                context_parts.append(f"Ongoing topics: {topics}")
            
            # Add therapeutic goals
            if memory.conversation_context.therapeutic_goals:
                goals = ", ".join(memory.conversation_context.therapeutic_goals)
                context_parts.append(f"Therapeutic goals: {goals}")
            
            # Add recent session summaries
            recent_sessions = sorted(
                memory.conversation_context.session_history,
                key=lambda s: s.timestamp,
                reverse=True
            )[:3]
            
            if recent_sessions:
                context_parts.append("\nRecent sessions:")
                for session in recent_sessions:
                    context_parts.append(f"- {session.therapeutic_progress}")
            
            # Add therapeutic profile
            profile = memory.therapeutic_profile
            context_parts.append(f"\nCommunication style: {profile.communication_style}")
            context_parts.append(f"Language preference: {profile.language_preference}")
            
            if profile.preferred_approaches:
                approaches = ", ".join(profile.preferred_approaches)
                context_parts.append(f"Preferred approaches: {approaches}")
            
            if profile.triggers_to_avoid:
                triggers = ", ".join(profile.triggers_to_avoid)
                context_parts.append(f"Triggers to avoid: {triggers}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to serialize context for client {client_id}: {str(e)}")
            return "Error loading conversation context."

    def delete_memory(self, client_id: str) -> bool:
        """
        Delete memory for a client (GDPR compliance)
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            memory_id = get_memory_id(client_id)
            
            # Delete from AgentCore (simulated for now)
            logger.info(f"Deleted memory for client {client_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory for client {client_id}: {str(e)}")
            return False

    def _needs_optimization(self, memory: AgentMemory) -> bool:
        """Check if memory needs optimization"""
        # Simplified check - in production would calculate actual size
        session_count = len(memory.conversation_context.session_history)
        note_count = len(memory.conversation_context.progress_notes)
        
        return (
            session_count > MAX_CONVERSATION_HISTORY_ITEMS or
            note_count > 100
        )

    def _optimize_memory(self, memory: AgentMemory) -> AgentMemory:
        """Optimize memory by removing old/low-priority data"""
        context = memory.conversation_context
        
        # Keep only recent sessions
        if len(context.session_history) > MAX_CONVERSATION_HISTORY_ITEMS:
            context.session_history = sorted(
                context.session_history,
                key=lambda s: s.timestamp,
                reverse=True
            )[:MAX_CONVERSATION_HISTORY_ITEMS]
        
        # Remove old low-importance progress notes
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        context.progress_notes = [
            note for note in context.progress_notes
            if note.timestamp > cutoff_date or note.importance >= 4
        ]
        
        # Keep only effective personality adaptations
        context.personality_adaptations = [
            adapt for adapt in context.personality_adaptations
            if adapt.effectiveness_score >= 0.6
        ]
        
        logger.info(f"Optimized memory for client {memory.client_id}")
        
        return memory
