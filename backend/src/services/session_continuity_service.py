"""
Session Continuity Service for AI Therapy Platform
Handles cross-session memory persistence, conversation resumption, and therapeutic relationship continuity
🏆 Breaking Barriers UK 2026 compliant

Validates: Requirements 7.1, 7.2
"""

import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from ..models.agent_memory import (
    AgentMemory,
    SessionSummary,
    ConversationContext,
    TherapeuticProfile,
    PersonalityAdaptation,
    ProgressNote
)
from ..services.agentcore_memory_service import AgentCoreMemoryService
from ..services.conversation_context_service import ConversationContextService
from ..data.session_repository import SessionRepository
from ..models.session import TherapySession, SessionStatus
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionContinuityService:
    """
    Service for managing session continuity across multiple therapy sessions
    Implements cross-session memory persistence, conversation resumption, and therapeutic relationship continuity
    """
    
    def __init__(
        self,
        memory_service: Optional[AgentCoreMemoryService] = None,
        context_service: Optional[ConversationContextService] = None,
        session_repository: Optional[SessionRepository] = None
    ):
        """
        Initialize session continuity service
        
        Args:
            memory_service: AgentCore memory service instance
            context_service: Conversation context service instance
            session_repository: Session repository instance
        """
        self.memory_service = memory_service or AgentCoreMemoryService()
        self.context_service = context_service or ConversationContextService(self.memory_service)
        self.session_repository = session_repository or SessionRepository()
        logger.info("Session Continuity Service initialized")

    # ========== Cross-Session Memory Persistence ==========
    
    def persist_session_to_memory(
        self,
        client_id: str,
        session: TherapySession,
        conversation_turns: List[Dict[str, str]],
        emotional_states: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Persist session data to AgentCore memory for cross-session continuity
        
        Args:
            client_id: Unique client identifier
            session: TherapySession object
            conversation_turns: List of conversation turns with 'user' and 'ai' keys
            emotional_states: Detected emotional states during session
            
        Returns:
            Dictionary with persistence status and memory information
        """
        try:
            # Create session summary
            session_summary = self.context_service.summarize_session(
                client_id=client_id,
                session_id=session.session_id,
                duration_seconds=session.duration or 0,
                conversation_turns=conversation_turns,
                emotional_states=emotional_states
            )
            
            # Get or create memory
            memory = self.memory_service.get_memory(client_id)
            if not memory:
                memory = self.memory_service.create_memory(
                    client_id=client_id,
                    language_preference=session.language or "en"
                )
            
            # Update last session information
            memory.conversation_context.last_session_date = session.timestamp
            memory.conversation_context.total_sessions += 1
            
            # Update memory
            updated_memory = self.memory_service.update_memory(memory)
            
            logger.info(
                f"Persisted session {session.session_id} to memory for client {client_id}"
            )
            
            return {
                'success': True,
                'client_id': client_id,
                'session_id': session.session_id,
                'memory_id': updated_memory.memory_id,
                'total_sessions': updated_memory.conversation_context.total_sessions,
                'session_summary': {
                    'key_topics': session_summary.key_topics,
                    'milestones': session_summary.milestones_achieved,
                    'emotional_state': session_summary.emotional_state
                }
            }
            
        except Exception as e:
            logger.error(
                f"Failed to persist session {session.session_id} to memory: {str(e)}"
            )
            return {
                'success': False,
                'error': str(e),
                'client_id': client_id,
                'session_id': session.session_id
            }

    def load_session_context(
        self,
        client_id: str,
        include_recent_sessions: int = 3
    ) -> Dict[str, Any]:
        """
        Load conversation context from previous sessions for continuity
        
        Args:
            client_id: Unique client identifier
            include_recent_sessions: Number of recent sessions to include in context
            
        Returns:
            Dictionary with loaded context and session history
        """
        try:
            # Get memory from AgentCore
            memory = self.memory_service.get_memory(client_id)
            
            if not memory:
                logger.info(f"No previous memory found for client {client_id}")
                return {
                    'has_previous_sessions': False,
                    'total_sessions': 0,
                    'context': "This is your first session. Welcome!",
                    'therapeutic_profile': None,
                    'recent_sessions': []
                }
            
            # Get recent session history
            recent_sessions = sorted(
                memory.conversation_context.session_history,
                key=lambda s: s.timestamp,
                reverse=True
            )[:include_recent_sessions]
            
            # Generate context window for AI
            context_window = self.context_service.get_context_window(
                client_id=client_id,
                max_tokens=4000,
                include_recent_sessions=include_recent_sessions
            )
            
            # Get effective personality adaptations
            effective_adaptations = self.context_service.get_effective_adaptations(
                client_id=client_id,
                min_effectiveness=0.6
            )
            
            logger.info(
                f"Loaded session context for client {client_id}: "
                f"{memory.conversation_context.total_sessions} total sessions"
            )
            
            return {
                'has_previous_sessions': True,
                'total_sessions': memory.conversation_context.total_sessions,
                'last_session_date': memory.conversation_context.last_session_date.isoformat() if memory.conversation_context.last_session_date else None,
                'context': context_window,
                'therapeutic_profile': {
                    'communication_style': memory.therapeutic_profile.communication_style,
                    'language_preference': memory.therapeutic_profile.language_preference,
                    'preferred_approaches': memory.therapeutic_profile.preferred_approaches,
                    'triggers_to_avoid': memory.therapeutic_profile.triggers_to_avoid,
                    'successful_interventions': memory.therapeutic_profile.successful_interventions
                },
                'recent_sessions': [
                    {
                        'session_id': s.session_id,
                        'timestamp': s.timestamp.isoformat(),
                        'duration_seconds': s.duration_seconds,
                        'key_topics': s.key_topics,
                        'milestones': s.milestones_achieved
                    }
                    for s in recent_sessions
                ],
                'ongoing_topics': memory.conversation_context.ongoing_topics,
                'therapeutic_goals': memory.conversation_context.therapeutic_goals,
                'effective_adaptations': [
                    {
                        'type': a.adaptation_type,
                        'description': a.description,
                        'effectiveness': a.effectiveness_score
                    }
                    for a in effective_adaptations
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to load session context for client {client_id}: {str(e)}")
            return {
                'has_previous_sessions': False,
                'total_sessions': 0,
                'context': "Unable to load previous session context.",
                'error': str(e)
            }

    # ========== Conversation Resumption ==========
    
    def resume_conversation(
        self,
        client_id: str,
        new_session_id: str
    ) -> Dict[str, Any]:
        """
        Resume conversation from previous sessions with full context loading
        
        Args:
            client_id: Unique client identifier
            new_session_id: New session identifier
            
        Returns:
            Dictionary with resumption context and greeting
        """
        try:
            # Load session context
            context = self.load_session_context(client_id, include_recent_sessions=3)
            
            if not context['has_previous_sessions']:
                return {
                    'is_first_session': True,
                    'greeting': "Welcome to your first therapy session. I'm here to support you.",
                    'context': context['context'],
                    'session_id': new_session_id
                }
            
            # Generate personalized greeting based on history
            greeting = self._generate_resumption_greeting(
                total_sessions=context['total_sessions'],
                last_session_date=context.get('last_session_date'),
                ongoing_topics=context.get('ongoing_topics', []),
                therapeutic_goals=context.get('therapeutic_goals', [])
            )
            
            # Get time since last session
            time_since_last = None
            if context.get('last_session_date'):
                last_date = datetime.fromisoformat(context['last_session_date'])
                time_since_last = (datetime.utcnow() - last_date).days
            
            logger.info(
                f"Resumed conversation for client {client_id}: "
                f"session {new_session_id}, {context['total_sessions']} previous sessions"
            )
            
            return {
                'is_first_session': False,
                'greeting': greeting,
                'context': context['context'],
                'session_id': new_session_id,
                'total_previous_sessions': context['total_sessions'],
                'days_since_last_session': time_since_last,
                'ongoing_topics': context.get('ongoing_topics', []),
                'therapeutic_goals': context.get('therapeutic_goals', []),
                'therapeutic_profile': context.get('therapeutic_profile'),
                'recent_sessions_summary': context.get('recent_sessions', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to resume conversation for client {client_id}: {str(e)}")
            return {
                'is_first_session': True,
                'greeting': "Welcome. Let's begin our session.",
                'context': "Unable to load previous session context.",
                'error': str(e),
                'session_id': new_session_id
            }

    def check_session_gap(
        self,
        client_id: str,
        threshold_days: int = 7
    ) -> Dict[str, Any]:
        """
        Check if there's a significant gap since last session
        
        Args:
            client_id: Unique client identifier
            threshold_days: Number of days to consider as significant gap
            
        Returns:
            Dictionary with gap information and recommendations
        """
        try:
            memory = self.memory_service.get_memory(client_id)
            
            if not memory or not memory.conversation_context.last_session_date:
                return {
                    'has_gap': False,
                    'is_first_session': True,
                    'recommendation': 'first_session_protocol'
                }
            
            last_session = memory.conversation_context.last_session_date
            days_since_last = (datetime.utcnow() - last_session).days
            
            has_significant_gap = days_since_last >= threshold_days
            
            # Generate recommendations based on gap
            recommendation = 'continue_normally'
            if days_since_last >= 30:
                recommendation = 'reestablish_rapport'
            elif days_since_last >= 14:
                recommendation = 'check_in_thoroughly'
            elif days_since_last >= threshold_days:
                recommendation = 'brief_check_in'
            
            logger.info(
                f"Session gap check for client {client_id}: "
                f"{days_since_last} days, recommendation: {recommendation}"
            )
            
            return {
                'has_gap': has_significant_gap,
                'is_first_session': False,
                'days_since_last_session': days_since_last,
                'last_session_date': last_session.isoformat(),
                'recommendation': recommendation,
                'suggested_topics': self._get_check_in_topics(memory, days_since_last)
            }
            
        except Exception as e:
            logger.error(f"Failed to check session gap for client {client_id}: {str(e)}")
            return {
                'has_gap': False,
                'is_first_session': True,
                'error': str(e)
            }

    # ========== Therapeutic Relationship Continuity ==========
    
    def build_therapeutic_relationship(
        self,
        client_id: str,
        session_id: str,
        relationship_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build and strengthen therapeutic relationship across sessions
        
        Args:
            client_id: Unique client identifier
            session_id: Current session identifier
            relationship_indicators: Dictionary with rapport, trust, engagement metrics
            
        Returns:
            Dictionary with relationship status and recommendations
        """
        try:
            memory = self.memory_service.get_memory(client_id)
            
            if not memory:
                memory = self.memory_service.create_memory(client_id)
            
            # Extract relationship metrics
            rapport_score = relationship_indicators.get('rapport_score', 0.5)
            trust_level = relationship_indicators.get('trust_level', 0.5)
            engagement_level = relationship_indicators.get('engagement_level', 0.5)
            
            # Calculate overall relationship strength
            relationship_strength = (rapport_score + trust_level + engagement_level) / 3
            
            # Record as personality adaptation
            adaptation = self.context_service.record_personality_adaptation(
                client_id=client_id,
                adaptation_type='relationship_building',
                description=f"Session {session_id}: rapport={rapport_score:.2f}, trust={trust_level:.2f}, engagement={engagement_level:.2f}",
                effectiveness_score=relationship_strength
            )
            
            # Generate relationship-building recommendations
            recommendations = self._generate_relationship_recommendations(
                relationship_strength=relationship_strength,
                rapport_score=rapport_score,
                trust_level=trust_level,
                engagement_level=engagement_level,
                total_sessions=memory.conversation_context.total_sessions
            )
            
            logger.info(
                f"Built therapeutic relationship for client {client_id}: "
                f"strength={relationship_strength:.2f}"
            )
            
            return {
                'success': True,
                'client_id': client_id,
                'session_id': session_id,
                'relationship_strength': relationship_strength,
                'rapport_score': rapport_score,
                'trust_level': trust_level,
                'engagement_level': engagement_level,
                'total_sessions': memory.conversation_context.total_sessions,
                'recommendations': recommendations,
                'adaptation_id': adaptation.adaptation_id
            }
            
        except Exception as e:
            logger.error(
                f"Failed to build therapeutic relationship for client {client_id}: {str(e)}"
            )
            return {
                'success': False,
                'error': str(e),
                'client_id': client_id,
                'session_id': session_id
            }

    def track_therapeutic_alliance(
        self,
        client_id: str,
        alliance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Track therapeutic alliance development over time
        
        Args:
            client_id: Unique client identifier
            alliance_metrics: Dictionary with alliance strength metrics
            
        Returns:
            Dictionary with alliance tracking information
        """
        try:
            memory = self.memory_service.get_memory(client_id)
            
            if not memory:
                return {
                    'success': False,
                    'error': 'No memory found for client'
                }
            
            # Calculate alliance score
            alliance_score = sum(alliance_metrics.values()) / len(alliance_metrics)
            
            # Track as progress note
            note = self.context_service.track_therapeutic_milestone(
                client_id=client_id,
                milestone_type='alliance_development',
                description=f"Therapeutic alliance score: {alliance_score:.2f}. Metrics: {alliance_metrics}",
                importance=4 if alliance_score >= 0.7 else 3
            )
            
            # Get alliance trend over recent sessions
            alliance_trend = self._calculate_alliance_trend(memory)
            
            logger.info(
                f"Tracked therapeutic alliance for client {client_id}: "
                f"score={alliance_score:.2f}, trend={alliance_trend}"
            )
            
            return {
                'success': True,
                'client_id': client_id,
                'alliance_score': alliance_score,
                'alliance_metrics': alliance_metrics,
                'alliance_trend': alliance_trend,
                'note_id': note.note_id,
                'recommendations': self._get_alliance_recommendations(alliance_score, alliance_trend)
            }
            
        except Exception as e:
            logger.error(
                f"Failed to track therapeutic alliance for client {client_id}: {str(e)}"
            )
            return {
                'success': False,
                'error': str(e),
                'client_id': client_id
            }

    # ========== Memory-Based Personalization ==========
    
    def personalize_therapeutic_approach(
        self,
        client_id: str,
        session_feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Personalize therapeutic approach based on memory and feedback
        
        Args:
            client_id: Unique client identifier
            session_feedback: Optional feedback from recent session
            
        Returns:
            Dictionary with personalization recommendations
        """
        try:
            memory = self.memory_service.get_memory(client_id)
            
            if not memory:
                return {
                    'personalization_level': 'default',
                    'recommendations': ['Use standard therapeutic approach'],
                    'communication_style': 'empathetic',
                    'language_preference': 'en'
                }
            
            # Get effective adaptations
            effective_adaptations = self.context_service.get_effective_adaptations(
                client_id=client_id,
                min_effectiveness=0.6
            )
            
            # Analyze therapeutic profile
            profile = memory.therapeutic_profile
            
            # Generate personalization recommendations
            recommendations = []
            
            # Communication style recommendations
            if profile.communication_style:
                recommendations.append(
                    f"Use {profile.communication_style} communication style"
                )
            
            # Preferred approaches
            if profile.preferred_approaches:
                recommendations.append(
                    f"Focus on: {', '.join(profile.preferred_approaches[:3])}"
                )
            
            # Avoid triggers
            if profile.triggers_to_avoid:
                recommendations.append(
                    f"Avoid topics: {', '.join(profile.triggers_to_avoid[:3])}"
                )
            
            # Successful interventions
            if profile.successful_interventions:
                recommendations.append(
                    f"Leverage successful approaches: {', '.join(profile.successful_interventions[:3])}"
                )
            
            # Effective adaptations
            for adaptation in effective_adaptations[:3]:
                recommendations.append(
                    f"{adaptation.adaptation_type}: {adaptation.description}"
                )
            
            # Apply session feedback if provided
            if session_feedback:
                feedback_insights = self.context_service.learn_from_session_feedback(
                    client_id=client_id,
                    session_id=session_feedback.get('session_id', ''),
                    feedback_score=session_feedback.get('score', 0.5),
                    feedback_notes=session_feedback.get('notes')
                )
                recommendations.extend(feedback_insights.get('recommendations', []))
            
            personalization_level = self._calculate_personalization_level(
                memory.conversation_context.total_sessions,
                len(effective_adaptations),
                len(profile.preferred_approaches)
            )
            
            logger.info(
                f"Personalized therapeutic approach for client {client_id}: "
                f"level={personalization_level}, {len(recommendations)} recommendations"
            )
            
            return {
                'personalization_level': personalization_level,
                'recommendations': recommendations,
                'communication_style': profile.communication_style,
                'language_preference': profile.language_preference,
                'preferred_approaches': profile.preferred_approaches,
                'triggers_to_avoid': profile.triggers_to_avoid,
                'successful_interventions': profile.successful_interventions,
                'effective_adaptations': [
                    {
                        'type': a.adaptation_type,
                        'description': a.description,
                        'effectiveness': a.effectiveness_score
                    }
                    for a in effective_adaptations
                ],
                'total_sessions': memory.conversation_context.total_sessions
            }
            
        except Exception as e:
            logger.error(
                f"Failed to personalize therapeutic approach for client {client_id}: {str(e)}"
            )
            return {
                'personalization_level': 'default',
                'recommendations': ['Use standard therapeutic approach'],
                'error': str(e)
            }

    def adapt_to_client_preferences(
        self,
        client_id: str,
        observed_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt therapeutic approach based on observed client preferences
        
        Args:
            client_id: Unique client identifier
            observed_preferences: Dictionary with observed preferences (pacing, depth, topics, etc.)
            
        Returns:
            Dictionary with adaptation status
        """
        try:
            memory = self.memory_service.get_memory(client_id)
            
            if not memory:
                memory = self.memory_service.create_memory(client_id)
            
            # Update therapeutic profile based on preferences
            profile_updates = {}
            
            if 'communication_style' in observed_preferences:
                profile_updates['communication_style'] = observed_preferences['communication_style']
            
            if 'preferred_topics' in observed_preferences:
                # Add to preferred approaches
                new_approaches = observed_preferences['preferred_topics']
                existing = set(memory.therapeutic_profile.preferred_approaches)
                existing.update(new_approaches)
                profile_updates['preferred_approaches'] = list(existing)
            
            if 'avoided_topics' in observed_preferences:
                # Add to triggers to avoid
                new_triggers = observed_preferences['avoided_topics']
                existing = set(memory.therapeutic_profile.triggers_to_avoid)
                existing.update(new_triggers)
                profile_updates['triggers_to_avoid'] = list(existing)
            
            if 'cultural_preferences' in observed_preferences:
                # Add cultural considerations
                new_cultural = observed_preferences['cultural_preferences']
                existing = set(memory.therapeutic_profile.cultural_considerations)
                existing.update(new_cultural)
                profile_updates['cultural_considerations'] = list(existing)
            
            # Update profile
            if profile_updates:
                updated_memory = self.memory_service.update_therapeutic_profile(
                    client_id=client_id,
                    profile_updates=profile_updates
                )
            
            # Record adaptation
            adaptation_description = f"Adapted to preferences: {', '.join(observed_preferences.keys())}"
            adaptation = self.context_service.record_personality_adaptation(
                client_id=client_id,
                adaptation_type='preference_adaptation',
                description=adaptation_description,
                effectiveness_score=0.7  # Initial score, will be updated based on feedback
            )
            
            logger.info(
                f"Adapted to client preferences for {client_id}: "
                f"{len(observed_preferences)} preferences updated"
            )
            
            return {
                'success': True,
                'client_id': client_id,
                'preferences_updated': list(observed_preferences.keys()),
                'profile_updates': profile_updates,
                'adaptation_id': adaptation.adaptation_id
            }
            
        except Exception as e:
            logger.error(
                f"Failed to adapt to client preferences for {client_id}: {str(e)}"
            )
            return {
                'success': False,
                'error': str(e),
                'client_id': client_id
            }

    def get_continuity_metrics(
        self,
        client_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive continuity metrics for a client
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            Dictionary with continuity metrics and insights
        """
        try:
            memory = self.memory_service.get_memory(client_id)
            
            if not memory:
                return {
                    'has_history': False,
                    'total_sessions': 0,
                    'continuity_score': 0.0
                }
            
            context = memory.conversation_context
            
            # Calculate continuity score
            continuity_score = self._calculate_continuity_score(memory)
            
            # Get session frequency
            session_frequency = self._calculate_session_frequency(context.session_history)
            
            # Get topic consistency
            topic_consistency = self._calculate_topic_consistency(context)
            
            # Get relationship strength
            relationship_strength = self._calculate_relationship_strength(
                context.personality_adaptations
            )
            
            logger.info(
                f"Retrieved continuity metrics for client {client_id}: "
                f"score={continuity_score:.2f}"
            )
            
            return {
                'has_history': True,
                'total_sessions': context.total_sessions,
                'continuity_score': continuity_score,
                'session_frequency': session_frequency,
                'topic_consistency': topic_consistency,
                'relationship_strength': relationship_strength,
                'last_session_date': context.last_session_date.isoformat() if context.last_session_date else None,
                'ongoing_topics_count': len(context.ongoing_topics),
                'therapeutic_goals_count': len(context.therapeutic_goals),
                'progress_notes_count': len(context.progress_notes),
                'adaptations_count': len(context.personality_adaptations),
                'memory_version': memory.version
            }
            
        except Exception as e:
            logger.error(
                f"Failed to get continuity metrics for client {client_id}: {str(e)}"
            )
            return {
                'has_history': False,
                'total_sessions': 0,
                'continuity_score': 0.0,
                'error': str(e)
            }

    # ========== Helper Methods ==========
    
    def _generate_resumption_greeting(
        self,
        total_sessions: int,
        last_session_date: Optional[str],
        ongoing_topics: List[str],
        therapeutic_goals: List[str]
    ) -> str:
        """Generate personalized greeting for session resumption"""
        
        greeting_parts = []
        
        # Welcome back message
        if total_sessions == 1:
            greeting_parts.append("Welcome back! It's good to see you for your second session.")
        elif total_sessions < 5:
            greeting_parts.append(f"Welcome back! This is our session number {total_sessions + 1}.")
        else:
            greeting_parts.append("Welcome back! It's good to continue our work together.")
        
        # Time since last session
        if last_session_date:
            try:
                last_date = datetime.fromisoformat(last_session_date)
                days_since = (datetime.utcnow() - last_date).days
                
                if days_since == 0:
                    greeting_parts.append("I see we're meeting again today.")
                elif days_since == 1:
                    greeting_parts.append("It's been a day since we last spoke.")
                elif days_since < 7:
                    greeting_parts.append(f"It's been {days_since} days since our last session.")
                elif days_since < 14:
                    greeting_parts.append("It's been about a week since we last met.")
                elif days_since < 30:
                    greeting_parts.append(f"It's been {days_since} days. How have you been?")
                else:
                    greeting_parts.append("It's been a while since we last spoke. I'm glad you're back.")
            except:
                pass
        
        # Reference ongoing topics
        if ongoing_topics:
            if len(ongoing_topics) == 1:
                greeting_parts.append(f"Last time we were discussing {ongoing_topics[0]}.")
            elif len(ongoing_topics) <= 3:
                greeting_parts.append(f"We've been working on {', '.join(ongoing_topics[:2])}.")
        
        # Reference therapeutic goals
        if therapeutic_goals:
            greeting_parts.append("Let's continue working toward your goals.")
        
        return " ".join(greeting_parts)
    
    def _get_check_in_topics(
        self,
        memory: AgentMemory,
        days_since_last: int
    ) -> List[str]:
        """Get suggested check-in topics based on session gap"""
        
        topics = []
        
        if days_since_last >= 30:
            topics.extend([
                "How have you been since we last spoke?",
                "What's been happening in your life?",
                "Have there been any significant changes?"
            ])
        elif days_since_last >= 14:
            topics.extend([
                "How have things been going?",
                "Have you had a chance to work on what we discussed?"
            ])
        elif days_since_last >= 7:
            topics.extend([
                "How has your week been?",
                "Any updates since our last session?"
            ])
        
        # Add ongoing topics
        if memory.conversation_context.ongoing_topics:
            for topic in memory.conversation_context.ongoing_topics[:2]:
                topics.append(f"How are things with {topic}?")
        
        return topics
    
    def _generate_relationship_recommendations(
        self,
        relationship_strength: float,
        rapport_score: float,
        trust_level: float,
        engagement_level: float,
        total_sessions: int
    ) -> List[str]:
        """Generate recommendations for building therapeutic relationship"""
        
        recommendations = []
        
        # Overall relationship strength
        if relationship_strength < 0.5:
            recommendations.append("Focus on building rapport and trust")
            recommendations.append("Use more empathetic and validating language")
            recommendations.append("Allow client to set the pace")
        elif relationship_strength < 0.7:
            recommendations.append("Continue strengthening the therapeutic alliance")
            recommendations.append("Gradually introduce deeper therapeutic work")
        else:
            recommendations.append("Strong therapeutic relationship established")
            recommendations.append("Can engage in deeper therapeutic interventions")
        
        # Specific metrics
        if rapport_score < 0.5:
            recommendations.append("Work on building rapport through active listening")
        
        if trust_level < 0.5:
            recommendations.append("Build trust through consistency and reliability")
            recommendations.append("Maintain clear boundaries and expectations")
        
        if engagement_level < 0.5:
            recommendations.append("Increase engagement through relevant topics")
            recommendations.append("Use more interactive therapeutic techniques")
        
        # Session count considerations
        if total_sessions < 3:
            recommendations.append("Early sessions: focus on relationship building")
        elif total_sessions < 10:
            recommendations.append("Mid-phase: balance relationship and therapeutic work")
        else:
            recommendations.append("Established relationship: focus on therapeutic outcomes")
        
        return recommendations
    
    def _calculate_alliance_trend(
        self,
        memory: AgentMemory
    ) -> str:
        """Calculate therapeutic alliance trend from progress notes"""
        
        # Get alliance-related progress notes
        alliance_notes = [
            note for note in memory.conversation_context.progress_notes
            if note.category == 'alliance_development'
        ]
        
        if len(alliance_notes) < 2:
            return 'insufficient_data'
        
        # Sort by timestamp
        alliance_notes.sort(key=lambda n: n.timestamp)
        
        # Extract scores from descriptions (simplified)
        # In production, this would parse the actual scores
        recent_notes = alliance_notes[-3:]
        
        # Simple trend detection based on importance scores
        if len(recent_notes) >= 2:
            recent_avg = sum(n.importance for n in recent_notes[-2:]) / 2
            older_avg = sum(n.importance for n in recent_notes[:-2]) / max(len(recent_notes) - 2, 1)
            
            if recent_avg > older_avg + 0.5:
                return 'improving'
            elif recent_avg < older_avg - 0.5:
                return 'declining'
        
        return 'stable'
    
    def _get_alliance_recommendations(
        self,
        alliance_score: float,
        alliance_trend: str
    ) -> List[str]:
        """Get recommendations based on alliance score and trend"""
        
        recommendations = []
        
        if alliance_score < 0.5:
            recommendations.append("Alliance needs attention - focus on relationship repair")
            recommendations.append("Explore any ruptures or misunderstandings")
        elif alliance_score < 0.7:
            recommendations.append("Alliance is developing - continue building trust")
        else:
            recommendations.append("Strong alliance - leverage for therapeutic work")
        
        if alliance_trend == 'declining':
            recommendations.append("Alliance declining - address concerns proactively")
            recommendations.append("Check in about the therapeutic relationship")
        elif alliance_trend == 'improving':
            recommendations.append("Alliance improving - maintain current approach")
        
        return recommendations
    
    def _calculate_personalization_level(
        self,
        total_sessions: int,
        adaptations_count: int,
        approaches_count: int
    ) -> str:
        """Calculate personalization level"""
        
        if total_sessions == 0:
            return 'default'
        elif total_sessions < 3:
            return 'basic'
        elif total_sessions < 10:
            if adaptations_count >= 3 or approaches_count >= 2:
                return 'moderate'
            return 'basic'
        else:
            if adaptations_count >= 5 and approaches_count >= 3:
                return 'high'
            elif adaptations_count >= 3 or approaches_count >= 2:
                return 'moderate'
            return 'basic'
    
    def _calculate_continuity_score(
        self,
        memory: AgentMemory
    ) -> float:
        """Calculate overall continuity score"""
        
        context = memory.conversation_context
        
        # Factors contributing to continuity
        session_factor = min(context.total_sessions / 10, 1.0) * 0.3
        topic_factor = min(len(context.ongoing_topics) / 5, 1.0) * 0.2
        goal_factor = min(len(context.therapeutic_goals) / 3, 1.0) * 0.2
        adaptation_factor = min(len(context.personality_adaptations) / 5, 1.0) * 0.15
        note_factor = min(len(context.progress_notes) / 10, 1.0) * 0.15
        
        continuity_score = (
            session_factor +
            topic_factor +
            goal_factor +
            adaptation_factor +
            note_factor
        )
        
        return round(continuity_score, 2)
    
    def _calculate_session_frequency(
        self,
        session_history: List[SessionSummary]
    ) -> Dict[str, Any]:
        """Calculate session frequency metrics"""
        
        if len(session_history) < 2:
            return {
                'average_days_between_sessions': None,
                'frequency_category': 'insufficient_data'
            }
        
        # Sort by timestamp
        sorted_sessions = sorted(session_history, key=lambda s: s.timestamp)
        
        # Calculate gaps between sessions
        gaps = []
        for i in range(1, len(sorted_sessions)):
            gap = (sorted_sessions[i].timestamp - sorted_sessions[i-1].timestamp).days
            gaps.append(gap)
        
        avg_gap = sum(gaps) / len(gaps)
        
        # Categorize frequency
        if avg_gap <= 3:
            category = 'very_frequent'
        elif avg_gap <= 7:
            category = 'frequent'
        elif avg_gap <= 14:
            category = 'regular'
        elif avg_gap <= 30:
            category = 'occasional'
        else:
            category = 'infrequent'
        
        return {
            'average_days_between_sessions': round(avg_gap, 1),
            'frequency_category': category,
            'total_sessions': len(session_history)
        }
    
    def _calculate_topic_consistency(
        self,
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Calculate topic consistency across sessions"""
        
        if not context.session_history:
            return {
                'consistency_score': 0.0,
                'recurring_topics': []
            }
        
        # Count topic occurrences across sessions
        topic_counts = {}
        for session in context.session_history:
            for topic in session.key_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Find recurring topics (appear in multiple sessions)
        recurring_topics = [
            topic for topic, count in topic_counts.items()
            if count >= 2
        ]
        
        # Calculate consistency score
        if not topic_counts:
            consistency_score = 0.0
        else:
            consistency_score = len(recurring_topics) / len(topic_counts)
        
        return {
            'consistency_score': round(consistency_score, 2),
            'recurring_topics': recurring_topics[:5],  # Top 5
            'total_unique_topics': len(topic_counts)
        }
    
    def _calculate_relationship_strength(
        self,
        adaptations: List[PersonalityAdaptation]
    ) -> float:
        """Calculate relationship strength from adaptations"""
        
        if not adaptations:
            return 0.0
        
        # Filter relationship-building adaptations
        relationship_adaptations = [
            a for a in adaptations
            if a.adaptation_type in ['relationship_building', 'preference_adaptation']
        ]
        
        if not relationship_adaptations:
            return 0.0
        
        # Average effectiveness of relationship adaptations
        avg_effectiveness = sum(
            a.effectiveness_score for a in relationship_adaptations
        ) / len(relationship_adaptations)
        
        return round(avg_effectiveness, 2)
