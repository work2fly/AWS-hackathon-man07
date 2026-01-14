"""
Personalization and Adaptation Engine for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

User preference learning, conversation style personalization,
therapeutic approach customization, and long-term relationship building.

Validates: Requirements 3.7, 10.6
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

from ..services.conversation_context_service import ConversationContextService
from ..services.agentcore_memory_service import AgentCoreMemoryService
from ..models.agent_memory import PersonalityAdaptation, TherapeuticProfile
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ConversationStyle(Enum):
    """Conversation style preferences"""
    DIRECT = "direct"
    GENTLE = "gentle"
    EXPLORATORY = "exploratory"
    STRUCTURED = "structured"
    SUPPORTIVE = "supportive"


class TherapeuticApproach(Enum):
    """Therapeutic approach types"""
    CBT = "cognitive_behavioral"  # Cognitive Behavioral Therapy
    PERSON_CENTERED = "person_centered"  # Person-Centered Therapy
    SOLUTION_FOCUSED = "solution_focused"  # Solution-Focused Brief Therapy
    MINDFULNESS = "mindfulness"  # Mindfulness-Based
    PSYCHODYNAMIC = "psychodynamic"  # Psychodynamic
    ECLECTIC = "eclectic"  # Eclectic/Integrative


class CommunicationPreference(Enum):
    """Communication preferences"""
    CONCISE = "concise"
    DETAILED = "detailed"
    BALANCED = "balanced"


@dataclass
class UserPreferences:
    """User preference profile"""
    client_id: str
    conversation_style: ConversationStyle
    therapeutic_approach: TherapeuticApproach
    communication_preference: CommunicationPreference
    language_preference: str
    pacing_preference: str  # "slow", "moderate", "fast"
    formality_level: str  # "casual", "professional", "formal"
    preferred_session_length: int  # minutes
    topics_of_interest: List[str] = field(default_factory=list)
    topics_to_avoid: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdaptationRecommendation:
    """Recommendation for conversation adaptation"""
    recommendation_type: str
    description: str
    confidence: float  # 0.0 to 1.0
    rationale: str
    priority: int  # 1-5, 5 being highest


class PersonalizationEngine:
    """
    Engine for personalizing therapeutic conversations
    
    Learns user preferences, adapts conversation style, customizes
    therapeutic approaches, and builds long-term relationships.
    """
    
    def __init__(
        self,
        context_service: Optional[ConversationContextService] = None,
        memory_service: Optional[AgentCoreMemoryService] = None
    ):
        """
        Initialize personalization engine
        
        Args:
            context_service: Conversation context service
            memory_service: AgentCore memory service
        """
        self.context_service = context_service or ConversationContextService()
        self.memory_service = memory_service or AgentCoreMemoryService()
        
        # Track user preferences
        self._user_preferences: Dict[str, UserPreferences] = {}
        
        # Track adaptation history
        self._adaptation_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        logger.info("Personalization Engine initialized")
    
    # ========== User Preference Learning ==========
    
    def learn_preferences_from_session(
        self,
        client_id: str,
        session_id: str,
        session_data: Dict[str, Any]
    ) -> UserPreferences:
        """
        Learn user preferences from session interactions
        
        Args:
            client_id: Client identifier
            session_id: Session identifier
            session_data: Session interaction data
            
        Returns:
            Updated UserPreferences
        """
        # Get or create preferences
        preferences = self._user_preferences.get(client_id)
        
        if not preferences:
            preferences = self._initialize_default_preferences(client_id)
        
        # Learn from session data
        if 'response_lengths' in session_data:
            preferences = self._learn_communication_preference(
                preferences,
                session_data['response_lengths']
            )
        
        if 'interaction_pace' in session_data:
            preferences = self._learn_pacing_preference(
                preferences,
                session_data['interaction_pace']
            )
        
        if 'topics_discussed' in session_data:
            preferences = self._learn_topic_preferences(
                preferences,
                session_data['topics_discussed'],
                session_data.get('topic_engagement', {})
            )
        
        if 'therapeutic_interventions' in session_data:
            preferences = self._learn_therapeutic_approach(
                preferences,
                session_data['therapeutic_interventions'],
                session_data.get('intervention_effectiveness', {})
            )
        
        # Update timestamp
        preferences.last_updated = datetime.utcnow()
        
        # Store preferences
        self._user_preferences[client_id] = preferences
        
        # Update in AgentCore memory
        self._update_therapeutic_profile(client_id, preferences)
        
        logger.info(f"Learned preferences from session {session_id} for client {client_id}")
        return preferences
    
    def _initialize_default_preferences(self, client_id: str) -> UserPreferences:
        """Initialize default preferences for new user"""
        return UserPreferences(
            client_id=client_id,
            conversation_style=ConversationStyle.SUPPORTIVE,
            therapeutic_approach=TherapeuticApproach.ECLECTIC,
            communication_preference=CommunicationPreference.BALANCED,
            language_preference="en",
            pacing_preference="moderate",
            formality_level="professional",
            preferred_session_length=45
        )
    
    def _learn_communication_preference(
        self,
        preferences: UserPreferences,
        response_lengths: List[int]
    ) -> UserPreferences:
        """Learn communication preference from response lengths"""
        if not response_lengths:
            return preferences
        
        avg_length = sum(response_lengths) / len(response_lengths)
        
        # Classify based on average word count
        if avg_length < 30:
            preferences.communication_preference = CommunicationPreference.CONCISE
        elif avg_length > 80:
            preferences.communication_preference = CommunicationPreference.DETAILED
        else:
            preferences.communication_preference = CommunicationPreference.BALANCED
        
        return preferences
    
    def _learn_pacing_preference(
        self,
        preferences: UserPreferences,
        interaction_pace: str
    ) -> UserPreferences:
        """Learn pacing preference from interaction patterns"""
        # Map interaction pace to preference
        pace_mapping = {
            'rapid': 'fast',
            'quick': 'fast',
            'normal': 'moderate',
            'measured': 'moderate',
            'slow': 'slow',
            'deliberate': 'slow'
        }
        
        preferences.pacing_preference = pace_mapping.get(interaction_pace, 'moderate')
        return preferences
    
    def _learn_topic_preferences(
        self,
        preferences: UserPreferences,
        topics_discussed: List[str],
        topic_engagement: Dict[str, float]
    ) -> UserPreferences:
        """Learn topic preferences from engagement"""
        # Identify highly engaging topics
        for topic, engagement in topic_engagement.items():
            if engagement > 0.7 and topic not in preferences.topics_of_interest:
                preferences.topics_of_interest.append(topic)
            elif engagement < 0.3 and topic not in preferences.topics_to_avoid:
                preferences.topics_to_avoid.append(topic)
        
        return preferences
    
    def _learn_therapeutic_approach(
        self,
        preferences: UserPreferences,
        interventions: List[str],
        effectiveness: Dict[str, float]
    ) -> UserPreferences:
        """Learn preferred therapeutic approach from intervention effectiveness"""
        # Map interventions to approaches
        approach_scores = defaultdict(float)
        
        for intervention, score in effectiveness.items():
            if 'cognitive' in intervention.lower() or 'thought' in intervention.lower():
                approach_scores[TherapeuticApproach.CBT] += score
            elif 'mindful' in intervention.lower() or 'present' in intervention.lower():
                approach_scores[TherapeuticApproach.MINDFULNESS] += score
            elif 'solution' in intervention.lower() or 'goal' in intervention.lower():
                approach_scores[TherapeuticApproach.SOLUTION_FOCUSED] += score
            elif 'empathy' in intervention.lower() or 'validation' in intervention.lower():
                approach_scores[TherapeuticApproach.PERSON_CENTERED] += score
        
        # Select approach with highest score
        if approach_scores:
            best_approach = max(approach_scores.items(), key=lambda x: x[1])[0]
            preferences.therapeutic_approach = best_approach
        
        return preferences
    
    def _update_therapeutic_profile(
        self,
        client_id: str,
        preferences: UserPreferences
    ) -> None:
        """Update therapeutic profile in AgentCore memory"""
        memory = self.memory_service.get_memory(client_id)
        
        if memory:
            # Update profile with preferences
            memory.therapeutic_profile.communication_style = preferences.conversation_style.value
            memory.therapeutic_profile.language_preference = preferences.language_preference
            memory.therapeutic_profile.preferred_approaches = [preferences.therapeutic_approach.value]
            
            # Update memory
            self.memory_service.update_memory(memory)
    
    # ========== Conversation Style Personalization ==========
    
    def personalize_conversation_style(
        self,
        client_id: str,
        base_response: str
    ) -> str:
        """
        Personalize conversation style based on user preferences
        
        Args:
            client_id: Client identifier
            base_response: Base AI response
            
        Returns:
            Personalized response
        """
        preferences = self._user_preferences.get(client_id)
        
        if not preferences:
            return base_response
        
        personalized = base_response
        
        # Apply communication preference
        if preferences.communication_preference == CommunicationPreference.CONCISE:
            personalized = self._make_concise(personalized)
        elif preferences.communication_preference == CommunicationPreference.DETAILED:
            personalized = self._make_detailed(personalized)
        
        # Apply formality level
        if preferences.formality_level == "casual":
            personalized = self._make_casual(personalized)
        elif preferences.formality_level == "formal":
            personalized = self._make_formal(personalized)
        
        # Apply conversation style
        if preferences.conversation_style == ConversationStyle.DIRECT:
            personalized = self._make_direct(personalized)
        elif preferences.conversation_style == ConversationStyle.GENTLE:
            personalized = self._make_gentle(personalized)
        
        logger.debug(f"Personalized response for client {client_id}")
        return personalized
    
    def _make_concise(self, text: str) -> str:
        """Make response more concise"""
        # Simple implementation: keep first 2 sentences
        sentences = text.split('. ')
        if len(sentences) > 2:
            return '. '.join(sentences[:2]) + '.'
        return text
    
    def _make_detailed(self, text: str) -> str:
        """Make response more detailed"""
        # In production, this would add elaboration
        # For now, just return as-is
        return text
    
    def _make_casual(self, text: str) -> str:
        """Make response more casual"""
        # Simple transformations
        text = text.replace("I understand", "I get")
        text = text.replace("Perhaps", "Maybe")
        return text
    
    def _make_formal(self, text: str) -> str:
        """Make response more formal"""
        # Simple transformations
        text = text.replace("I get", "I understand")
        text = text.replace("Maybe", "Perhaps")
        return text
    
    def _make_direct(self, text: str) -> str:
        """Make response more direct"""
        # Remove hedging language
        text = text.replace("I think ", "")
        text = text.replace("perhaps ", "")
        text = text.replace("maybe ", "")
        return text
    
    def _make_gentle(self, text: str) -> str:
        """Make response more gentle"""
        # Add softening language
        if not any(word in text.lower() for word in ['perhaps', 'maybe', 'might']):
            # Add gentle qualifier to first sentence
            sentences = text.split('. ')
            if sentences:
                sentences[0] = "Perhaps " + sentences[0].lower()
                text = '. '.join(sentences)
        return text
    
    # ========== Therapeutic Approach Customization ==========
    
    def customize_therapeutic_approach(
        self,
        client_id: str,
        intervention_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Customize therapeutic approach based on user preferences
        
        Args:
            client_id: Client identifier
            intervention_type: Type of intervention
            context: Conversation context
            
        Returns:
            Customized intervention guidance
        """
        preferences = self._user_preferences.get(client_id)
        
        if not preferences:
            return {
                'approach': TherapeuticApproach.ECLECTIC.value,
                'guidance': 'Use balanced therapeutic approach',
                'techniques': []
            }
        
        approach = preferences.therapeutic_approach
        
        # Customize based on approach
        if approach == TherapeuticApproach.CBT:
            return self._customize_cbt_approach(intervention_type, context)
        elif approach == TherapeuticApproach.PERSON_CENTERED:
            return self._customize_person_centered_approach(intervention_type, context)
        elif approach == TherapeuticApproach.SOLUTION_FOCUSED:
            return self._customize_solution_focused_approach(intervention_type, context)
        elif approach == TherapeuticApproach.MINDFULNESS:
            return self._customize_mindfulness_approach(intervention_type, context)
        else:
            return self._customize_eclectic_approach(intervention_type, context)
    
    def _customize_cbt_approach(
        self,
        intervention_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize for CBT approach"""
        return {
            'approach': TherapeuticApproach.CBT.value,
            'guidance': 'Focus on thoughts, feelings, and behaviors connection',
            'techniques': [
                'Identify automatic thoughts',
                'Challenge cognitive distortions',
                'Behavioral activation',
                'Thought records'
            ]
        }
    
    def _customize_person_centered_approach(
        self,
        intervention_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize for person-centered approach"""
        return {
            'approach': TherapeuticApproach.PERSON_CENTERED.value,
            'guidance': 'Emphasize empathy, unconditional positive regard, and genuineness',
            'techniques': [
                'Active listening',
                'Reflection of feelings',
                'Validation',
                'Non-directive exploration'
            ]
        }
    
    def _customize_solution_focused_approach(
        self,
        intervention_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize for solution-focused approach"""
        return {
            'approach': TherapeuticApproach.SOLUTION_FOCUSED.value,
            'guidance': 'Focus on solutions and future goals rather than problems',
            'techniques': [
                'Miracle question',
                'Scaling questions',
                'Exception finding',
                'Goal setting'
            ]
        }
    
    def _customize_mindfulness_approach(
        self,
        intervention_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize for mindfulness approach"""
        return {
            'approach': TherapeuticApproach.MINDFULNESS.value,
            'guidance': 'Emphasize present-moment awareness and acceptance',
            'techniques': [
                'Breathing exercises',
                'Body scan',
                'Mindful observation',
                'Acceptance practices'
            ]
        }
    
    def _customize_eclectic_approach(
        self,
        intervention_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize for eclectic/integrative approach"""
        return {
            'approach': TherapeuticApproach.ECLECTIC.value,
            'guidance': 'Use flexible, integrated approach based on client needs',
            'techniques': [
                'Empathetic listening',
                'Cognitive restructuring',
                'Goal setting',
                'Mindfulness practices'
            ]
        }
    
    # ========== Long-Term Relationship Building ==========
    
    def build_relationship_continuity(
        self,
        client_id: str,
        session_count: int
    ) -> Dict[str, Any]:
        """
        Build long-term therapeutic relationship continuity
        
        Args:
            client_id: Client identifier
            session_count: Number of sessions completed
            
        Returns:
            Relationship building guidance
        """
        # Get conversation history
        history = self.context_service.get_conversation_history(client_id, limit=10)
        
        # Get therapeutic progress
        progress = self.context_service.get_therapeutic_progress(client_id, days=90)
        
        # Determine relationship stage
        if session_count < 3:
            stage = "building_rapport"
        elif session_count < 10:
            stage = "establishing_trust"
        elif session_count < 20:
            stage = "deepening_work"
        else:
            stage = "maintenance"
        
        # Generate continuity guidance
        guidance = {
            'relationship_stage': stage,
            'session_count': session_count,
            'continuity_elements': self._generate_continuity_elements(
                client_id,
                history,
                progress
            ),
            'relationship_building_focus': self._get_stage_focus(stage)
        }
        
        logger.info(f"Built relationship continuity for client {client_id}: {stage}")
        return guidance
    
    def _generate_continuity_elements(
        self,
        client_id: str,
        history: List[Any],
        progress: Dict[str, Any]
    ) -> List[str]:
        """Generate elements for relationship continuity"""
        elements = []
        
        # Reference previous sessions
        if history:
            elements.append(f"Reference to previous session topics")
        
        # Acknowledge progress
        if progress.get('milestones'):
            elements.append("Acknowledge therapeutic milestones achieved")
        
        # Maintain consistency
        elements.append("Maintain consistent therapeutic approach")
        
        # Build on previous work
        if progress.get('ongoing_topics'):
            elements.append("Continue exploring ongoing topics")
        
        return elements
    
    def _get_stage_focus(self, stage: str) -> List[str]:
        """Get focus areas for relationship stage"""
        stage_focus = {
            'building_rapport': [
                'Establish safety and trust',
                'Understand client concerns',
                'Set initial therapeutic goals'
            ],
            'establishing_trust': [
                'Deepen therapeutic alliance',
                'Explore underlying patterns',
                'Build client confidence'
            ],
            'deepening_work': [
                'Address core issues',
                'Facilitate insight and change',
                'Strengthen coping strategies'
            ],
            'maintenance': [
                'Consolidate gains',
                'Prevent relapse',
                'Plan for future challenges'
            ]
        }
        
        return stage_focus.get(stage, [])
    
    # ========== Adaptation Recommendations ==========
    
    def get_adaptation_recommendations(
        self,
        client_id: str,
        current_session_data: Dict[str, Any]
    ) -> List[AdaptationRecommendation]:
        """
        Get recommendations for adapting conversation
        
        Args:
            client_id: Client identifier
            current_session_data: Current session data
            
        Returns:
            List of adaptation recommendations
        """
        recommendations = []
        
        preferences = self._user_preferences.get(client_id)
        
        if not preferences:
            return recommendations
        
        # Check if current approach matches preferences
        current_approach = current_session_data.get('therapeutic_approach')
        if current_approach and current_approach != preferences.therapeutic_approach.value:
            recommendations.append(AdaptationRecommendation(
                recommendation_type="therapeutic_approach",
                description=f"Consider shifting to {preferences.therapeutic_approach.value} approach",
                confidence=0.8,
                rationale="Client has shown better response to this approach in past sessions",
                priority=4
            ))
        
        # Check communication style
        current_style = current_session_data.get('communication_style')
        if current_style and current_style != preferences.conversation_style.value:
            recommendations.append(AdaptationRecommendation(
                recommendation_type="conversation_style",
                description=f"Adjust to {preferences.conversation_style.value} style",
                confidence=0.7,
                rationale="Client preference based on engagement patterns",
                priority=3
            ))
        
        # Check pacing
        current_pace = current_session_data.get('pacing')
        if current_pace and current_pace != preferences.pacing_preference:
            recommendations.append(AdaptationRecommendation(
                recommendation_type="pacing",
                description=f"Adjust pacing to {preferences.pacing_preference}",
                confidence=0.6,
                rationale="Client comfort level with conversation pace",
                priority=2
            ))
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        
        return recommendations
    
    def get_user_preferences(self, client_id: str) -> Optional[UserPreferences]:
        """Get user preferences"""
        return self._user_preferences.get(client_id)
