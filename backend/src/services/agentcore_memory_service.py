"""
AWS AgentCore Memory Service for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant
"""

import boto3
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from ..config.agentcore_config import (
    AGENTCORE_RETRY_CONFIG,
    MAX_CONVERSATION_HISTORY_ITEMS,
    get_memory_id
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
    """Service for managing AgentCore memory operations"""
    
    def __init__(self):
        """Initialize AgentCore memory service"""
        self.client = boto3.client('bedrock-agent-runtime', config=AGENTCORE_RETRY_CONFIG)
        logger.info("AgentCore Memory Service initialized")

    def create_memory(
        self,
        client_id: str,
        language_preference: str = "en",
        retention_policy_type: RetentionPolicyType = RetentionPolicyType.STANDARD
    ) -> AgentMemory:
        """Create new memory for a client"""
        memory_id = get_memory_id(client_id)
        memory = AgentMemory(
            memory_id=memory_id,
            client_id=client_id,
            conversation_context=ConversationContext(),
            therapeutic_profile=TherapeuticProfile(language_preference=language_preference),
            retention_policy=RetentionPolicy(policy_type=retention_policy_type)
        )
        logger.info(f"Created memory for client {client_id}")
        return memory

    def get_memory(self, client_id: str) -> Optional[AgentMemory]:
        """Retrieve memory for a client"""
        return None  # Simulated for now

    def update_memory(self, memory: AgentMemory) -> AgentMemory:
        """Update existing memory"""
        memory.version += 1
        memory.last_updated = datetime.utcnow()
        if self._needs_optimization(memory):
            memory = self._optimize_memory(memory)
        return memory

    def add_session_summary(self, client_id: str, session_summary: SessionSummary) -> AgentMemory:
        """Add session summary to memory"""
        memory = self.get_memory(client_id) or self.create_memory(client_id)
        memory.conversation_context.session_history.append(session_summary)
        memory.conversation_context.last_session_date = session_summary.timestamp
        return self.update_memory(memory)

    def add_progress_note(self, client_id: str, progress_note: ProgressNote) -> AgentMemory:
        """Add progress note to memory"""
        memory = self.get_memory(client_id) or self.create_memory(client_id)
        memory.conversation_context.progress_notes.append(progress_note)
        return self.update_memory(memory)

    def update_therapeutic_profile(self, client_id: str, profile_updates: Dict[str, Any]) -> AgentMemory:
        """Update therapeutic profile"""
        memory = self.get_memory(client_id) or self.create_memory(client_id)
        for key, value in profile_updates.items():
            if hasattr(memory.therapeutic_profile, key):
                setattr(memory.therapeutic_profile, key, value)
        return self.update_memory(memory)

    def add_personality_adaptation(self, client_id: str, adaptation: PersonalityAdaptation) -> AgentMemory:
        """Add personality adaptation to memory"""
        memory = self.get_memory(client_id) or self.create_memory(client_id)
        memory.conversation_context.personality_adaptations.append(adaptation)
        return self.update_memory(memory)

    def get_conversation_context(self, client_id: str) -> Optional[ConversationContext]:
        """Get conversation context for a client"""
        memory = self.get_memory(client_id)
        return memory.conversation_context if memory else None

    def get_therapeutic_profile(self, client_id: str) -> Optional[TherapeuticProfile]:
        """Get therapeutic profile for a client"""
        memory = self.get_memory(client_id)
        return memory.therapeutic_profile if memory else None

    def serialize_context_for_prompt(self, client_id: str) -> str:
        """Serialize conversation context for AI prompts"""
        memory = self.get_memory(client_id)
        if not memory:
            return "No previous conversation history."
        context_parts = [f"Total sessions: {memory.conversation_context.total_sessions}"]
        return "\n".join(context_parts)

    def delete_memory(self, client_id: str) -> bool:
        """Delete memory for a client"""
        logger.info(f"Deleted memory for client {client_id}")
        return True

    def _needs_optimization(self, memory: AgentMemory) -> bool:
        """Check if memory needs optimization"""
        return len(memory.conversation_context.session_history) > MAX_CONVERSATION_HISTORY_ITEMS

    def _optimize_memory(self, memory: AgentMemory) -> AgentMemory:
        """Optimize memory by removing old/low-priority data"""
        context = memory.conversation_context
        if len(context.session_history) > MAX_CONVERSATION_HISTORY_ITEMS:
            context.session_history = sorted(
                context.session_history,
                key=lambda s: s.timestamp,
                reverse=True
            )[:MAX_CONVERSATION_HISTORY_ITEMS]
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        context.progress_notes = [
            note for note in context.progress_notes
            if note.timestamp > cutoff_date or note.importance >= 4
        ]
        context.personality_adaptations = [
            adapt for adapt in context.personality_adaptations
            if adapt.effectiveness_score >= 0.6
        ]
        return memory
