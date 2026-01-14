"""
Conversation Context Management Service for AI Therapy Platform
Handles conversation history, therapeutic progress, personality adaptation, and context window management
🏆 Breaking Barriers UK 2026 compliant

Validates: Requirements 3.6, 3.7, 7.1, 7.2
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.agent_memory import (
    SessionSummary,
    ProgressNote,
    PersonalityAdaptation,
    ConversationContext,
    TherapeuticProfile
)
from ..services.agentcore_memory_service import AgentCoreMemoryService
from ..config.agentcore_config import (
    MAX_CONVERSATION_HISTORY_ITEMS,
    MAX_SESSION_SUMMARY_LENGTH
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ConversationContextService:
    """
    Service for managing conversation context, history, and therapeutic progress
    Implements conversation tracking, summarization, and context window management
    """
    
    def __init__(self, memory_service: Optional[AgentCoreMemoryService] = None):
        """
        Initialize conversation context service
        
        Args:
            memory_service: AgentCore memory service instance (creates new if None)
        """
        self.memory_service = memory_service or AgentCoreMemoryService()
        logger.info("Conversation Context Service initialized")
    
    # ========== Conversation History Tracking ==========
    
    def add_conversation_turn(
        self,
        client_id: str,
        session_id: str,
        user_message: str,
        ai_response: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Add a conversation turn to the current session context
        
        Args:
            client_id: Unique client identifier
            session_id: Current session identifier
            user_message: User's message content
            ai_response: AI's response content
            timestamp: Turn timestamp (defaults to now)
            
        Returns:
            Dictionary with turn information and context update status
        """
        timestamp = timestamp or datetime.utcnow()
        
        # Get current memory
        memory = self.memory_service.get_memory(client_id)
        if not memory:
            memory = self.memory_service.create_memory(client_id)
        
        # Extract topics from conversation turn
        topics = self._extract_topics(user_message, ai_response)
        
        # Update ongoing topics
        for topic in topics:
            if topic not in memory.conversation_context.ongoing_topics:
                memory.conversation_context.ongoing_topics.append(topic)
        
        logger.info(f"Added conversation turn for client {client_id}, session {session_id}")
        
        return {
            'client_id': client_id,
            'session_id': session_id,
            'timestamp': timestamp.isoformat(),
            'topics_extracted': topics,
            'ongoing_topics_count': len(memory.conversation_context.ongoing_topics)
        }
    
    def summarize_session(
        self,
        client_id: str,
        session_id: str,
        duration_seconds: int,
        conversation_turns: List[Dict[str, str]],
        emotional_states: Optional[List[str]] = None
    ) -> SessionSummary:
        """
        Create a comprehensive session summary
        
        Args:
            client_id: Unique client identifier
            session_id: Session identifier
            duration_seconds: Session duration in seconds
            conversation_turns: List of conversation turns with 'user' and 'ai' keys
            emotional_states: Detected emotional states during session
            
        Returns:
            SessionSummary object
        """
        # Extract key topics from all conversation turns
        all_text = " ".join([
            f"{turn.get('user', '')} {turn.get('ai', '')}"
            for turn in conversation_turns
        ])
        key_topics = self._extract_topics_from_text(all_text)
        
        # Generate therapeutic progress summary
        progress_summary = self._generate_progress_summary(
            conversation_turns,
            emotional_states or []
        )
        
        # Detect milestones achieved
        milestones = self._detect_milestones(conversation_turns)
        
        session_summary = SessionSummary(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            duration_seconds=duration_seconds,
            key_topics=key_topics[:10],  # Top 10 topics
            emotional_state=emotional_states or [],
            therapeutic_progress=progress_summary[:MAX_SESSION_SUMMARY_LENGTH],
            milestones_achieved=milestones
        )
        
        # Store in memory
        self.memory_service.add_session_summary(client_id, session_summary)
        
        logger.info(f"Created session summary for client {client_id}, session {session_id}")
        return session_summary
    
    def get_conversation_history(
        self,
        client_id: str,
        limit: Optional[int] = None
    ) -> List[SessionSummary]:
        """
        Retrieve conversation history for a client
        
        Args:
            client_id: Unique client identifier
            limit: Maximum number of sessions to return (None for all)
            
        Returns:
            List of SessionSummary objects, most recent first
        """
        context = self.memory_service.get_conversation_context(client_id)
        
        if not context:
            return []
        
        # Sort by timestamp, most recent first
        history = sorted(
            context.session_history,
            key=lambda s: s.timestamp,
            reverse=True
        )
        
        if limit:
            history = history[:limit]
        
        logger.info(f"Retrieved {len(history)} session summaries for client {client_id}")
        return history
    
    # ========== Therapeutic Progress Monitoring ==========
    
    def track_therapeutic_milestone(
        self,
        client_id: str,
        milestone_type: str,
        description: str,
        importance: int = 3
    ) -> ProgressNote:
        """
        Track a therapeutic milestone or progress point
        
        Args:
            client_id: Unique client identifier
            milestone_type: Type of milestone (e.g., 'breakthrough', 'goal_achieved', 'insight')
            description: Description of the milestone
            importance: Importance level (1-5, default 3)
            
        Returns:
            Created ProgressNote object
        """
        note_id = f"milestone_{client_id}_{datetime.utcnow().timestamp()}"
        
        progress_note = ProgressNote(
            note_id=note_id,
            timestamp=datetime.utcnow(),
            content=description,
            category=milestone_type,
            importance=min(max(importance, 1), 5)  # Clamp to 1-5
        )
        
        self.memory_service.add_progress_note(client_id, progress_note)
        
        logger.info(f"Tracked milestone for client {client_id}: {milestone_type}")
        return progress_note
    
    def get_therapeutic_progress(
        self,
        client_id: str,
        days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get therapeutic progress summary for a client
        
        Args:
            client_id: Unique client identifier
            days: Number of days to look back (None for all time)
            
        Returns:
            Dictionary with progress metrics and insights
        """
        context = self.memory_service.get_conversation_context(client_id)
        
        if not context:
            return {
                'total_sessions': 0,
                'progress_notes': [],
                'milestones': [],
                'ongoing_topics': [],
                'therapeutic_goals': []
            }
        
        # Filter by date if specified
        cutoff_date = None
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter progress notes
        progress_notes = context.progress_notes
        if cutoff_date:
            progress_notes = [
                note for note in progress_notes
                if note.timestamp > cutoff_date
            ]
        
        # Filter session history
        sessions = context.session_history
        if cutoff_date:
            sessions = [
                session for session in sessions
                if session.timestamp > cutoff_date
            ]
        
        # Extract milestones from sessions
        all_milestones = []
        for session in sessions:
            all_milestones.extend(session.milestones_achieved)
        
        # Calculate progress metrics
        progress_metrics = self._calculate_progress_metrics(
            sessions,
            progress_notes
        )
        
        logger.info(f"Retrieved therapeutic progress for client {client_id}")
        
        return {
            'total_sessions': len(sessions),
            'progress_notes': [
                {
                    'timestamp': note.timestamp.isoformat(),
                    'category': note.category,
                    'content': note.content,
                    'importance': note.importance
                }
                for note in sorted(progress_notes, key=lambda n: n.timestamp, reverse=True)
            ],
            'milestones': all_milestones,
            'ongoing_topics': context.ongoing_topics,
            'therapeutic_goals': context.therapeutic_goals,
            'metrics': progress_metrics
        }
    
    def set_therapeutic_goals(
        self,
        client_id: str,
        goals: List[str]
    ) -> ConversationContext:
        """
        Set or update therapeutic goals for a client
        
        Args:
            client_id: Unique client identifier
            goals: List of therapeutic goals
            
        Returns:
            Updated ConversationContext
        """
        memory = self.memory_service.get_memory(client_id)
        
        if not memory:
            memory = self.memory_service.create_memory(client_id)
        
        memory.conversation_context.therapeutic_goals = goals
        updated_memory = self.memory_service.update_memory(memory)
        
        logger.info(f"Set {len(goals)} therapeutic goals for client {client_id}")
        return updated_memory.conversation_context
    
    # ========== Personality Adaptation and Learning ==========
    
    def record_personality_adaptation(
        self,
        client_id: str,
        adaptation_type: str,
        description: str,
        effectiveness_score: float = 0.5
    ) -> PersonalityAdaptation:
        """
        Record an AI personality adaptation based on client interactions
        
        Args:
            client_id: Unique client identifier
            adaptation_type: Type of adaptation (e.g., 'tone', 'pacing', 'approach')
            description: Description of the adaptation
            effectiveness_score: Effectiveness score (0.0-1.0)
            
        Returns:
            Created PersonalityAdaptation object
        """
        adaptation_id = f"adapt_{client_id}_{datetime.utcnow().timestamp()}"
        
        adaptation = PersonalityAdaptation(
            adaptation_id=adaptation_id,
            timestamp=datetime.utcnow(),
            adaptation_type=adaptation_type,
            description=description,
            effectiveness_score=min(max(effectiveness_score, 0.0), 1.0)  # Clamp to 0-1
        )
        
        self.memory_service.add_personality_adaptation(client_id, adaptation)
        
        logger.info(f"Recorded personality adaptation for client {client_id}: {adaptation_type}")
        return adaptation
    
    def get_effective_adaptations(
        self,
        client_id: str,
        min_effectiveness: float = 0.6
    ) -> List[PersonalityAdaptation]:
        """
        Get effective personality adaptations for a client
        
        Args:
            client_id: Unique client identifier
            min_effectiveness: Minimum effectiveness score threshold
            
        Returns:
            List of effective PersonalityAdaptation objects
        """
        context = self.memory_service.get_conversation_context(client_id)
        
        if not context:
            return []
        
        effective_adaptations = [
            adapt for adapt in context.personality_adaptations
            if adapt.effectiveness_score >= min_effectiveness
        ]
        
        # Sort by effectiveness score, highest first
        effective_adaptations.sort(
            key=lambda a: a.effectiveness_score,
            reverse=True
        )
        
        logger.info(
            f"Retrieved {len(effective_adaptations)} effective adaptations "
            f"for client {client_id}"
        )
        return effective_adaptations
    
    def update_adaptation_effectiveness(
        self,
        client_id: str,
        adaptation_id: str,
        new_effectiveness: float
    ) -> bool:
        """
        Update the effectiveness score of a personality adaptation
        
        Args:
            client_id: Unique client identifier
            adaptation_id: Adaptation identifier
            new_effectiveness: New effectiveness score (0.0-1.0)
            
        Returns:
            True if update successful, False otherwise
        """
        memory = self.memory_service.get_memory(client_id)
        
        if not memory:
            return False
        
        # Find and update the adaptation
        updated = False
        for adaptation in memory.conversation_context.personality_adaptations:
            if adaptation.adaptation_id == adaptation_id:
                adaptation.effectiveness_score = min(max(new_effectiveness, 0.0), 1.0)
                updated = True
                break
        
        if updated:
            self.memory_service.update_memory(memory)
            logger.info(
                f"Updated adaptation {adaptation_id} effectiveness "
                f"to {new_effectiveness} for client {client_id}"
            )
        
        return updated
    
    def learn_from_session_feedback(
        self,
        client_id: str,
        session_id: str,
        feedback_score: float,
        feedback_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Learn from session feedback to improve personality adaptations
        
        Args:
            client_id: Unique client identifier
            session_id: Session identifier
            feedback_score: Feedback score (0.0-1.0)
            feedback_notes: Optional feedback notes
            
        Returns:
            Dictionary with learning insights
        """
        memory = self.memory_service.get_memory(client_id)
        
        if not memory:
            return {'error': 'No memory found for client'}
        
        # Find the session
        session = None
        for s in memory.conversation_context.session_history:
            if s.session_id == session_id:
                session = s
                break
        
        if not session:
            return {'error': 'Session not found'}
        
        # Analyze what worked well or poorly
        learning_insights = {
            'session_id': session_id,
            'feedback_score': feedback_score,
            'feedback_notes': feedback_notes,
            'recommendations': []
        }
        
        # If feedback is positive, reinforce successful approaches
        if feedback_score >= 0.7:
            # Identify successful topics and approaches
            for topic in session.key_topics:
                if topic not in memory.therapeutic_profile.successful_interventions:
                    memory.therapeutic_profile.successful_interventions.append(topic)
                    learning_insights['recommendations'].append(
                        f"Continue focusing on topic: {topic}"
                    )
        
        # If feedback is negative, identify areas for improvement
        elif feedback_score < 0.5:
            # Mark topics as potentially triggering
            for topic in session.key_topics:
                if topic not in memory.therapeutic_profile.triggers_to_avoid:
                    memory.therapeutic_profile.triggers_to_avoid.append(topic)
                    learning_insights['recommendations'].append(
                        f"Approach topic more carefully: {topic}"
                    )
        
        # Update memory
        self.memory_service.update_memory(memory)
        
        logger.info(f"Learned from session feedback for client {client_id}, session {session_id}")
        return learning_insights
    
    # ========== Context Window Management ==========
    
    def get_context_window(
        self,
        client_id: str,
        max_tokens: int = 4000,
        include_recent_sessions: int = 3
    ) -> str:
        """
        Get optimized context window for AI prompts
        Manages context size for long conversations
        
        Args:
            client_id: Unique client identifier
            max_tokens: Maximum token count for context (approximate)
            include_recent_sessions: Number of recent sessions to include
            
        Returns:
            Formatted context string optimized for token limits
        """
        memory = self.memory_service.get_memory(client_id)
        
        if not memory:
            return "No previous conversation history available."
        
        context_parts = []
        estimated_tokens = 0
        
        # Add therapeutic profile (always included, ~200 tokens)
        profile_context = self._format_therapeutic_profile(memory.therapeutic_profile)
        context_parts.append(profile_context)
        estimated_tokens += self._estimate_tokens(profile_context)
        
        # Add therapeutic goals (~100 tokens)
        if memory.conversation_context.therapeutic_goals:
            goals_context = "Therapeutic Goals:\n" + "\n".join(
                f"- {goal}" for goal in memory.conversation_context.therapeutic_goals
            )
            context_parts.append(goals_context)
            estimated_tokens += self._estimate_tokens(goals_context)
        
        # Add recent session summaries (prioritize most recent)
        recent_sessions = sorted(
            memory.conversation_context.session_history,
            key=lambda s: s.timestamp,
            reverse=True
        )[:include_recent_sessions]
        
        for session in recent_sessions:
            session_context = self._format_session_summary(session)
            session_tokens = self._estimate_tokens(session_context)
            
            if estimated_tokens + session_tokens > max_tokens:
                break
            
            context_parts.append(session_context)
            estimated_tokens += session_tokens
        
        # Add high-importance progress notes if space allows
        important_notes = [
            note for note in memory.conversation_context.progress_notes
            if note.importance >= 4
        ]
        important_notes.sort(key=lambda n: n.timestamp, reverse=True)
        
        for note in important_notes[:5]:  # Max 5 important notes
            note_context = f"Important Note ({note.category}): {note.content}"
            note_tokens = self._estimate_tokens(note_context)
            
            if estimated_tokens + note_tokens > max_tokens:
                break
            
            context_parts.append(note_context)
            estimated_tokens += note_tokens
        
        # Add effective personality adaptations if space allows
        effective_adaptations = self.get_effective_adaptations(client_id)
        
        if effective_adaptations and estimated_tokens < max_tokens * 0.9:
            adapt_context = "Effective Approaches:\n" + "\n".join(
                f"- {adapt.description} (effectiveness: {adapt.effectiveness_score:.2f})"
                for adapt in effective_adaptations[:3]
            )
            adapt_tokens = self._estimate_tokens(adapt_context)
            
            if estimated_tokens + adapt_tokens <= max_tokens:
                context_parts.append(adapt_context)
                estimated_tokens += adapt_tokens
        
        final_context = "\n\n".join(context_parts)
        
        logger.info(
            f"Generated context window for client {client_id}: "
            f"~{estimated_tokens} tokens, {len(context_parts)} sections"
        )
        
        return final_context
    
    def compress_conversation_history(
        self,
        client_id: str,
        keep_recent: int = 10
    ) -> Dict[str, Any]:
        """
        Compress conversation history to manage memory size
        Keeps most recent sessions and high-importance items
        
        Args:
            client_id: Unique client identifier
            keep_recent: Number of recent sessions to keep in full detail
            
        Returns:
            Dictionary with compression statistics
        """
        memory = self.memory_service.get_memory(client_id)
        
        if not memory:
            return {'error': 'No memory found for client'}
        
        original_session_count = len(memory.conversation_context.session_history)
        original_note_count = len(memory.conversation_context.progress_notes)
        
        # Keep most recent sessions
        memory.conversation_context.session_history = sorted(
            memory.conversation_context.session_history,
            key=lambda s: s.timestamp,
            reverse=True
        )[:keep_recent]
        
        # Keep high-importance progress notes and recent ones
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        memory.conversation_context.progress_notes = [
            note for note in memory.conversation_context.progress_notes
            if note.importance >= 4 or note.timestamp > cutoff_date
        ]
        
        # Update memory
        self.memory_service.update_memory(memory)
        
        compression_stats = {
            'client_id': client_id,
            'original_sessions': original_session_count,
            'compressed_sessions': len(memory.conversation_context.session_history),
            'original_notes': original_note_count,
            'compressed_notes': len(memory.conversation_context.progress_notes),
            'compression_ratio': (
                1 - (len(memory.conversation_context.session_history) + 
                     len(memory.conversation_context.progress_notes)) /
                (original_session_count + original_note_count)
            ) if (original_session_count + original_note_count) > 0 else 0
        }
        
        logger.info(
            f"Compressed conversation history for client {client_id}: "
            f"{compression_stats['compression_ratio']:.2%} reduction"
        )
        
        return compression_stats
    
    # ========== Helper Methods ==========
    
    def _extract_topics(self, user_message: str, ai_response: str) -> List[str]:
        """Extract topics from a conversation turn"""
        # Simple keyword extraction (in production, use NLP)
        text = f"{user_message} {ai_response}".lower()
        
        # Common therapeutic topics
        topic_keywords = {
            'anxiety': ['anxiety', 'anxious', 'worry', 'nervous'],
            'depression': ['depression', 'depressed', 'sad', 'hopeless'],
            'relationships': ['relationship', 'partner', 'family', 'friend'],
            'work_stress': ['work', 'job', 'career', 'stress'],
            'self_esteem': ['confidence', 'self-esteem', 'worth', 'value'],
            'trauma': ['trauma', 'traumatic', 'ptsd'],
            'coping': ['coping', 'manage', 'handle', 'deal with'],
            'goals': ['goal', 'objective', 'aim', 'target']
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text"""
        return self._extract_topics(text, "")
    
    def _generate_progress_summary(
        self,
        conversation_turns: List[Dict[str, str]],
        emotional_states: List[str]
    ) -> str:
        """Generate therapeutic progress summary"""
        # Simple summary generation (in production, use AI)
        turn_count = len(conversation_turns)
        
        summary_parts = [
            f"Session included {turn_count} conversation exchanges."
        ]
        
        if emotional_states:
            summary_parts.append(
                f"Emotional states observed: {', '.join(set(emotional_states))}."
            )
        
        # Analyze conversation depth
        avg_length = sum(
            len(turn.get('user', '')) + len(turn.get('ai', ''))
            for turn in conversation_turns
        ) / max(turn_count, 1)
        
        if avg_length > 200:
            summary_parts.append("Client engaged in deep, meaningful conversation.")
        elif avg_length > 100:
            summary_parts.append("Client showed moderate engagement.")
        else:
            summary_parts.append("Client provided brief responses.")
        
        return " ".join(summary_parts)
    
    def _detect_milestones(self, conversation_turns: List[Dict[str, str]]) -> List[str]:
        """Detect therapeutic milestones from conversation"""
        milestones = []
        
        # Simple milestone detection (in production, use AI)
        all_text = " ".join([
            f"{turn.get('user', '')} {turn.get('ai', '')}"
            for turn in conversation_turns
        ]).lower()
        
        milestone_indicators = {
            'insight': ['realize', 'understand', 'see now', 'makes sense'],
            'commitment': ['will try', 'going to', 'commit to', 'promise'],
            'progress': ['better', 'improved', 'progress', 'forward'],
            'breakthrough': ['breakthrough', 'aha', 'clarity', 'clear now']
        }
        
        for milestone_type, indicators in milestone_indicators.items():
            if any(indicator in all_text for indicator in indicators):
                milestones.append(milestone_type)
        
        return milestones
    
    def _calculate_progress_metrics(
        self,
        sessions: List[SessionSummary],
        progress_notes: List[ProgressNote]
    ) -> Dict[str, Any]:
        """Calculate therapeutic progress metrics"""
        if not sessions:
            return {
                'total_sessions': 0,
                'avg_session_duration': 0,
                'milestone_count': 0,
                'high_importance_notes': 0
            }
        
        total_duration = sum(s.duration_seconds for s in sessions)
        all_milestones = []
        for session in sessions:
            all_milestones.extend(session.milestones_achieved)
        
        high_importance_notes = len([n for n in progress_notes if n.importance >= 4])
        
        return {
            'total_sessions': len(sessions),
            'avg_session_duration': total_duration / len(sessions),
            'milestone_count': len(all_milestones),
            'unique_milestones': len(set(all_milestones)),
            'high_importance_notes': high_importance_notes,
            'topics_explored': len(set(
                topic for session in sessions for topic in session.key_topics
            ))
        }
    
    def _format_therapeutic_profile(self, profile: TherapeuticProfile) -> str:
        """Format therapeutic profile for context"""
        parts = [
            f"Communication Style: {profile.communication_style}",
            f"Language: {profile.language_preference}"
        ]
        
        if profile.preferred_approaches:
            parts.append(f"Preferred Approaches: {', '.join(profile.preferred_approaches[:3])}")
        
        if profile.triggers_to_avoid:
            parts.append(f"Triggers to Avoid: {', '.join(profile.triggers_to_avoid[:3])}")
        
        if profile.successful_interventions:
            parts.append(f"Successful Topics: {', '.join(profile.successful_interventions[:3])}")
        
        return "\n".join(parts)
    
    def _format_session_summary(self, session: SessionSummary) -> str:
        """Format session summary for context"""
        parts = [
            f"Session {session.session_id} ({session.timestamp.strftime('%Y-%m-%d')}):",
            f"Duration: {session.duration_seconds // 60} minutes",
            f"Topics: {', '.join(session.key_topics[:5])}"
        ]
        
        if session.milestones_achieved:
            parts.append(f"Milestones: {', '.join(session.milestones_achieved)}")
        
        parts.append(f"Progress: {session.therapeutic_progress[:200]}")
        
        return "\n".join(parts)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
