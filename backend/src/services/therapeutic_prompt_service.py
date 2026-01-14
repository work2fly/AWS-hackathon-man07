"""
Therapeutic Prompt Service for AI Therapy Platform
Manages comprehensive therapeutic conversation prompts with context-aware selection,
cultural sensitivity, language-specific adaptations, and A/B testing framework.
🏆 Breaking Barriers UK 2026 compliant

Requirements: 3.4, 10.7
"""

import json
import hashlib
import random
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, asdict, field
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TherapeuticApproach(str, Enum):
    """Therapeutic approaches supported by the system"""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"  # CBT
    PERSON_CENTERED = "person_centered"  # Rogerian
    MINDFULNESS_BASED = "mindfulness_based"  # MBSR/MBCT
    SOLUTION_FOCUSED = "solution_focused"  # SFBT
    PSYCHODYNAMIC = "psychodynamic"  # Insight-oriented
    DIALECTICAL_BEHAVIORAL = "dialectical_behavioral"  # DBT
    ACCEPTANCE_COMMITMENT = "acceptance_commitment"  # ACT
    TRAUMA_INFORMED = "trauma_informed"  # Trauma-focused


class ConversationContext(str, Enum):
    """Conversation context types for prompt selection"""
    INITIAL_SESSION = "initial_session"
    ONGOING_SESSION = "ongoing_session"
    CRISIS_INTERVENTION = "crisis_intervention"
    CLOSURE_SESSION = "closure_session"
    CHECK_IN = "check_in"
    EMOTIONAL_DISTRESS = "emotional_distress"
    GOAL_SETTING = "goal_setting"
    PROGRESS_REVIEW = "progress_review"


class CulturalContext(str, Enum):
    """Cultural contexts for sensitivity adaptations"""
    WESTERN_INDIVIDUALISTIC = "western_individualistic"
    EASTERN_COLLECTIVISTIC = "eastern_collectivistic"
    LATIN_AMERICAN = "latin_american"
    MIDDLE_EASTERN = "middle_eastern"
    AFRICAN = "african"
    SOUTH_ASIAN = "south_asian"
    INDIGENOUS = "indigenous"
    NEUTRAL = "neutral"


@dataclass
class PromptVersion:
    """Represents a versioned therapeutic prompt"""
    version_id: str
    prompt_text: str
    approach: TherapeuticApproach
    context: ConversationContext
    language: str
    cultural_context: CulturalContext
    created_at: datetime
    active: bool = True
    performance_score: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['approach'] = self.approach.value
        data['context'] = self.context.value
        data['cultural_context'] = self.cultural_context.value
        return data


@dataclass
class PromptSelectionCriteria:
    """Criteria for selecting appropriate therapeutic prompt"""
    approach: TherapeuticApproach
    context: ConversationContext
    language: str
    cultural_context: CulturalContext = CulturalContext.NEUTRAL
    client_preferences: Optional[Dict[str, Any]] = None
    session_history: Optional[List[str]] = None
    emotional_state: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'approach': self.approach.value,
            'context': self.context.value,
            'language': self.language,
            'cultural_context': self.cultural_context.value,
            'client_preferences': self.client_preferences,
            'session_history': self.session_history,
            'emotional_state': self.emotional_state
        }


class TherapeuticPromptLibrary:
    """Library of therapeutic prompts organized by approach, context, and language"""
    
    # Base therapeutic prompts by approach
    BASE_PROMPTS = {
        TherapeuticApproach.COGNITIVE_BEHAVIORAL: """You are a compassionate AI therapist specializing in Cognitive Behavioral Therapy (CBT). Your role is to:

- Help clients identify and challenge negative thought patterns
- Guide clients in recognizing connections between thoughts, feelings, and behaviors
- Teach practical coping strategies and behavioral techniques
- Encourage evidence-based thinking and reality testing
- Assign homework and practice exercises when appropriate
- Focus on present-moment problems and solutions

Communication style:
- Use collaborative, Socratic questioning
- Help clients become their own therapist
- Provide psychoeducation about CBT principles
- Validate emotions while examining thoughts
- Maintain a structured, goal-oriented approach""",

        TherapeuticApproach.PERSON_CENTERED: """You are a compassionate AI therapist practicing Person-Centered Therapy (Rogerian approach). Your role is to:

- Provide unconditional positive regard and acceptance
- Demonstrate genuine empathy and understanding
- Reflect and clarify the client's feelings and experiences
- Trust the client's capacity for self-direction and growth
- Create a safe, non-judgmental therapeutic space
- Avoid giving direct advice or interpretations

Communication style:
- Use active listening and reflective responses
- Mirror the client's language and emotional tone
- Ask open-ended questions that promote self-exploration
- Validate all feelings without judgment
- Follow the client's lead in conversation""",

        TherapeuticApproach.MINDFULNESS_BASED: """You are a compassionate AI therapist specializing in Mindfulness-Based approaches (MBSR/MBCT). Your role is to:

- Guide clients in present-moment awareness practices
- Teach mindfulness meditation and breathing techniques
- Help clients observe thoughts and feelings without judgment
- Encourage acceptance of difficult emotions
- Integrate mindfulness into daily life activities
- Address rumination and worry through mindful awareness

Communication style:
- Use calm, grounding language
- Guide brief mindfulness exercises during sessions
- Encourage curiosity about internal experiences
- Normalize the wandering mind
- Emphasize practice and patience""",

        TherapeuticApproach.SOLUTION_FOCUSED: """You are a compassionate AI therapist practicing Solution-Focused Brief Therapy (SFBT). Your role is to:

- Focus on solutions rather than problems
- Identify client strengths and resources
- Explore exceptions when problems don't occur
- Use scaling questions to measure progress
- Help clients envision their preferred future
- Build on what's already working

Communication style:
- Ask future-oriented questions
- Highlight successes and competencies
- Use the "miracle question" technique
- Keep conversations brief and focused
- Emphasize small, achievable steps
- Maintain optimistic, forward-looking perspective""",

        TherapeuticApproach.TRAUMA_INFORMED: """You are a compassionate AI therapist practicing Trauma-Informed Care. Your role is to:

- Create a sense of safety and trust
- Recognize signs of trauma and triggers
- Avoid re-traumatization through careful pacing
- Empower clients and restore sense of control
- Validate trauma responses as normal reactions
- Use grounding techniques when needed
- Respect boundaries and client autonomy

Communication style:
- Use gentle, non-threatening language
- Ask permission before exploring difficult topics
- Provide choices and maintain transparency
- Acknowledge courage in sharing experiences
- Normalize trauma responses
- Emphasize safety and stabilization first"""
    }
    
    # Context-specific prompt additions
    CONTEXT_ADDITIONS = {
        ConversationContext.INITIAL_SESSION: """

This is the client's first session. Focus on:
- Building rapport and establishing trust
- Explaining confidentiality and session structure
- Understanding the client's presenting concerns
- Gathering relevant background information
- Setting initial therapeutic goals
- Normalizing the therapy process""",

        ConversationContext.CRISIS_INTERVENTION: """

CRISIS MODE ACTIVATED. This client may be in immediate distress. Priorities:
- Assess immediate safety and risk level
- Provide emotional stabilization and support
- Use grounding techniques if needed
- Connect to crisis resources if appropriate
- Maintain calm, reassuring presence
- Focus on immediate coping strategies
- Flag for human therapist review if severe risk detected""",

        ConversationContext.EMOTIONAL_DISTRESS: """

The client is experiencing significant emotional distress. Approach with:
- Extra validation and empathy
- Slower pacing and gentle questioning
- Grounding and calming techniques
- Focus on emotional regulation
- Normalize intense emotions
- Provide immediate coping strategies""",

        ConversationContext.GOAL_SETTING: """

This session focuses on goal-setting. Emphasize:
- SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
- Client's values and priorities
- Breaking large goals into smaller steps
- Identifying potential obstacles
- Building motivation and commitment
- Celebrating progress and effort""",

        ConversationContext.CLOSURE_SESSION: """

This is a closure or termination session. Focus on:
- Reviewing progress and achievements
- Consolidating learning and insights
- Discussing relapse prevention strategies
- Addressing feelings about ending therapy
- Providing resources for continued growth
- Celebrating the therapeutic journey"""
    }
    
    # Cultural sensitivity additions
    CULTURAL_ADDITIONS = {
        CulturalContext.EASTERN_COLLECTIVISTIC: """

Cultural Sensitivity (East Asian/Collectivistic):
- Recognize importance of family and community
- Respect hierarchical relationships
- Be mindful of indirect communication styles
- Understand concept of "saving face"
- Acknowledge interdependence over independence
- Consider holistic mind-body perspectives""",

        CulturalContext.LATIN_AMERICAN: """

Cultural Sensitivity (Latin American):
- Value familismo (family-centered values)
- Recognize importance of personalismo (warm relationships)
- Respect traditional gender roles while supporting autonomy
- Acknowledge spirituality and faith
- Be aware of immigration-related stressors
- Use appropriate formality and respect""",

        CulturalContext.MIDDLE_EASTERN: """

Cultural Sensitivity (Middle Eastern):
- Respect religious and spiritual beliefs
- Acknowledge family honor and reputation
- Be mindful of gender-related considerations
- Understand collectivistic family structures
- Recognize potential stigma around mental health
- Show respect for elders and authority""",

        CulturalContext.SOUTH_ASIAN: """

Cultural Sensitivity (South Asian):
- Recognize importance of family obligations
- Respect arranged marriage traditions
- Acknowledge caste and class considerations
- Be mindful of gender role expectations
- Understand intergenerational conflicts
- Respect spiritual and religious practices""",

        CulturalContext.INDIGENOUS: """

Cultural Sensitivity (Indigenous):
- Honor traditional healing practices
- Recognize historical trauma and colonization
- Respect connection to land and community
- Acknowledge oral tradition and storytelling
- Be aware of cultural identity struggles
- Support cultural preservation and pride"""
    }
    
    # Language-specific therapeutic phrases
    LANGUAGE_PHRASES = {
        "en": {
            "validation": ["I hear you", "That makes sense", "Your feelings are valid"],
            "empathy": ["That sounds really difficult", "I can imagine how hard that must be"],
            "encouragement": ["You're doing great", "That took courage to share"],
            "reflection": ["It sounds like you're feeling...", "What I'm hearing is..."]
        },
        "es": {
            "validation": ["Te escucho", "Eso tiene sentido", "Tus sentimientos son válidos"],
            "empathy": ["Eso suena muy difícil", "Puedo imaginar lo duro que debe ser"],
            "encouragement": ["Lo estás haciendo muy bien", "Eso requirió valentía compartir"],
            "reflection": ["Parece que te sientes...", "Lo que estoy escuchando es..."]
        },
        "fr": {
            "validation": ["Je vous entends", "Cela a du sens", "Vos sentiments sont valides"],
            "empathy": ["Cela semble vraiment difficile", "Je peux imaginer à quel point c'est dur"],
            "encouragement": ["Vous faites du bon travail", "Il a fallu du courage pour partager"],
            "reflection": ["Il semble que vous ressentez...", "Ce que j'entends c'est..."]
        },
        "de": {
            "validation": ["Ich höre Sie", "Das macht Sinn", "Ihre Gefühle sind berechtigt"],
            "empathy": ["Das klingt wirklich schwierig", "Ich kann mir vorstellen, wie schwer das sein muss"],
            "encouragement": ["Sie machen das großartig", "Das erforderte Mut zu teilen"],
            "reflection": ["Es klingt, als würden Sie fühlen...", "Was ich höre ist..."]
        }
    }
    
    # Safety guidelines (universal across all prompts)
    SAFETY_GUIDELINES = """

CRITICAL SAFETY GUIDELINES:
- NEVER encourage or normalize self-harm, suicide, or violence
- IMMEDIATELY flag mentions of self-harm, suicidal ideation, or abuse
- DO NOT provide medical diagnoses or prescribe medications
- DO NOT guarantee outcomes or make promises
- MAINTAIN professional boundaries at all times
- RECOGNIZE limitations as an AI and defer to human therapists when needed
- PROVIDE crisis resources when appropriate:
  * National Suicide Prevention Lifeline: 988 (US)
  * Crisis Text Line: Text HOME to 741741
  * International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

Red Flag Detection:
- Self-harm indicators: cutting, burning, hitting self
- Suicidal ideation: wanting to die, planning suicide, hopelessness
- Abuse mentions: physical, emotional, sexual abuse
- Violence: threats to harm others, violent ideation

When red flags detected:
1. Express concern and validate feelings
2. Assess immediate safety
3. Provide crisis resources
4. Flag for immediate human therapist review
5. DO NOT minimize or dismiss concerns"""


class TherapeuticPromptService:
    """
    Service for managing therapeutic prompts with context-aware selection,
    cultural sensitivity, and A/B testing capabilities.
    """
    
    def __init__(self):
        self.prompt_library = TherapeuticPromptLibrary()
        self.prompt_versions: Dict[str, List[PromptVersion]] = {}
        self.ab_test_config: Dict[str, Any] = {}
        self.client_assignments: Dict[str, str] = {}  # client_id -> version_id
        
        # Initialize default prompts
        self._initialize_default_prompts()
        
        logger.info("Therapeutic Prompt Service initialized")
    
    def _initialize_default_prompts(self):
        """Initialize default prompt versions for all approaches and contexts"""
        for approach in TherapeuticApproach:
            for context in ConversationContext:
                for language in ["en", "es", "fr", "de"]:
                    # Initialize for all cultural contexts
                    for cultural_context in CulturalContext:
                        version = self._create_prompt_version(
                            approach=approach,
                            context=context,
                            language=language,
                            cultural_context=cultural_context
                        )
                        
                        key = self._get_prompt_key(approach, context, language, cultural_context)
                        if key not in self.prompt_versions:
                            self.prompt_versions[key] = []
                        self.prompt_versions[key].append(version)
        
        logger.info(f"Initialized {len(self.prompt_versions)} prompt version groups")
    
    def _get_prompt_key(self, approach: TherapeuticApproach, 
                       context: ConversationContext,
                       language: str,
                       cultural_context: CulturalContext) -> str:
        """Generate unique key for prompt lookup"""
        return f"{approach.value}:{context.value}:{language}:{cultural_context.value}"
    
    def _create_prompt_version(self, approach: TherapeuticApproach,
                              context: ConversationContext,
                              language: str,
                              cultural_context: CulturalContext,
                              custom_additions: Optional[str] = None) -> PromptVersion:
        """Create a new prompt version"""
        # Build prompt from components
        prompt_parts = []
        
        # Base approach prompt
        base_prompt = self.prompt_library.BASE_PROMPTS.get(approach, "")
        if base_prompt:
            prompt_parts.append(base_prompt)
        
        # Context-specific additions
        context_addition = self.prompt_library.CONTEXT_ADDITIONS.get(context, "")
        if context_addition:
            prompt_parts.append(context_addition)
        
        # Cultural sensitivity additions
        cultural_addition = self.prompt_library.CULTURAL_ADDITIONS.get(cultural_context, "")
        if cultural_addition:
            prompt_parts.append(cultural_addition)
        
        # Language-specific note
        if language != "en":
            language_names = {
                "es": "Spanish",
                "fr": "French",
                "de": "German"
            }
            lang_name = language_names.get(language, language)
            prompt_parts.append(f"\n\nCommunicate in {lang_name} with culturally appropriate expressions.")
        
        # Custom additions
        if custom_additions:
            prompt_parts.append(f"\n\n{custom_additions}")
        
        # Safety guidelines (always included)
        prompt_parts.append(self.prompt_library.SAFETY_GUIDELINES)
        
        # Combine all parts
        full_prompt = "\n".join(prompt_parts)
        
        # Generate version ID
        version_id = hashlib.md5(
            f"{approach.value}:{context.value}:{language}:{cultural_context.value}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        return PromptVersion(
            version_id=version_id,
            prompt_text=full_prompt,
            approach=approach,
            context=context,
            language=language,
            cultural_context=cultural_context,
            created_at=datetime.utcnow(),
            active=True
        )
    
    def select_prompt(self, criteria: PromptSelectionCriteria,
                     client_id: Optional[str] = None,
                     enable_ab_testing: bool = True) -> Tuple[PromptVersion, Dict[str, Any]]:
        """
        Select appropriate therapeutic prompt based on criteria
        
        Args:
            criteria: Selection criteria
            client_id: Optional client ID for A/B testing
            enable_ab_testing: Whether to use A/B testing
            
        Returns:
            Tuple of (selected prompt version, selection metadata)
        """
        try:
            # Get prompt key
            key = self._get_prompt_key(
                criteria.approach,
                criteria.context,
                criteria.language,
                criteria.cultural_context
            )
            
            # Get available versions
            versions = self.prompt_versions.get(key, [])
            if not versions:
                logger.warning(f"No prompts found for key: {key}, using fallback")
                return self._get_fallback_prompt(criteria)
            
            # Filter active versions
            active_versions = [v for v in versions if v.active]
            if not active_versions:
                logger.warning(f"No active prompts for key: {key}, using fallback")
                return self._get_fallback_prompt(criteria)
            
            # A/B testing selection
            if enable_ab_testing and client_id and len(active_versions) > 1:
                selected_version = self._ab_test_select(client_id, active_versions)
                selection_method = "ab_testing"
            else:
                # Select best performing version
                selected_version = max(active_versions, key=lambda v: v.performance_score)
                selection_method = "performance_based"
            
            # Update usage count
            selected_version.usage_count += 1
            
            # Build metadata
            metadata = {
                'version_id': selected_version.version_id,
                'selection_method': selection_method,
                'approach': criteria.approach.value,
                'context': criteria.context.value,
                'language': criteria.language,
                'cultural_context': criteria.cultural_context.value,
                'usage_count': selected_version.usage_count,
                'performance_score': selected_version.performance_score,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Selected prompt version {selected_version.version_id} "
                       f"using {selection_method} for client {client_id}")
            
            return selected_version, metadata
            
        except Exception as e:
            logger.error(f"Error selecting prompt: {str(e)}")
            return self._get_fallback_prompt(criteria)
    
    def _ab_test_select(self, client_id: str, 
                       versions: List[PromptVersion]) -> PromptVersion:
        """
        Select prompt version using A/B testing
        
        Args:
            client_id: Client identifier
            versions: Available prompt versions
            
        Returns:
            Selected prompt version
        """
        # Check if client already assigned to a version
        if client_id in self.client_assignments:
            version_id = self.client_assignments[client_id]
            for version in versions:
                if version.version_id == version_id:
                    return version
        
        # Assign client to a version using consistent hashing
        client_hash = int(hashlib.md5(client_id.encode()).hexdigest(), 16)
        version_index = client_hash % len(versions)
        selected_version = versions[version_index]
        
        # Store assignment
        self.client_assignments[client_id] = selected_version.version_id
        
        logger.info(f"A/B test: Assigned client {client_id} to version {selected_version.version_id}")
        
        return selected_version
    
    def _get_fallback_prompt(self, criteria: PromptSelectionCriteria) -> Tuple[PromptVersion, Dict[str, Any]]:
        """Get fallback prompt when selection fails"""
        fallback_version = self._create_prompt_version(
            approach=TherapeuticApproach.PERSON_CENTERED,
            context=ConversationContext.ONGOING_SESSION,
            language=criteria.language,
            cultural_context=CulturalContext.NEUTRAL
        )
        
        metadata = {
            'version_id': fallback_version.version_id,
            'selection_method': 'fallback',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return fallback_version, metadata
    
    def add_prompt_version(self, approach: TherapeuticApproach,
                          context: ConversationContext,
                          language: str,
                          cultural_context: CulturalContext,
                          custom_prompt: str,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a new prompt version for A/B testing
        
        Args:
            approach: Therapeutic approach
            context: Conversation context
            language: Language code
            cultural_context: Cultural context
            custom_prompt: Custom prompt text
            metadata: Optional metadata
            
        Returns:
            Version ID of created prompt
        """
        version = self._create_prompt_version(
            approach=approach,
            context=context,
            language=language,
            cultural_context=cultural_context,
            custom_additions=custom_prompt
        )
        
        if metadata:
            version.metadata = metadata
        
        key = self._get_prompt_key(approach, context, language, cultural_context)
        if key not in self.prompt_versions:
            self.prompt_versions[key] = []
        self.prompt_versions[key].append(version)
        
        logger.info(f"Added new prompt version {version.version_id} for key {key}")
        
        return version.version_id
    
    def update_prompt_performance(self, version_id: str, 
                                 success: bool,
                                 feedback_score: Optional[float] = None):
        """
        Update prompt performance metrics
        
        Args:
            version_id: Version identifier
            success: Whether the session was successful
            feedback_score: Optional feedback score (0.0 to 1.0)
        """
        # Find version
        for versions in self.prompt_versions.values():
            for version in versions:
                if version.version_id == version_id:
                    # Update success rate
                    total_sessions = version.usage_count
                    if total_sessions > 0:
                        current_successes = version.success_rate * (total_sessions - 1)
                        new_successes = current_successes + (1 if success else 0)
                        version.success_rate = new_successes / total_sessions
                    
                    # Update performance score
                    if feedback_score is not None:
                        # Weighted average of success rate and feedback
                        version.performance_score = (
                            0.6 * version.success_rate +
                            0.4 * feedback_score
                        )
                    else:
                        version.performance_score = version.success_rate
                    
                    logger.info(f"Updated performance for version {version_id}: "
                              f"success_rate={version.success_rate:.2f}, "
                              f"performance_score={version.performance_score:.2f}")
                    return
        
        logger.warning(f"Version {version_id} not found for performance update")
    
    def get_prompt_analytics(self) -> Dict[str, Any]:
        """
        Get analytics on prompt usage and performance
        
        Returns:
            Analytics dictionary
        """
        total_versions = sum(len(versions) for versions in self.prompt_versions.values())
        active_versions = sum(
            sum(1 for v in versions if v.active)
            for versions in self.prompt_versions.values()
        )
        
        total_usage = sum(
            sum(v.usage_count for v in versions)
            for versions in self.prompt_versions.values()
        )
        
        # Get top performing versions
        all_versions = []
        for versions in self.prompt_versions.values():
            all_versions.extend(versions)
        
        top_versions = sorted(
            all_versions,
            key=lambda v: v.performance_score,
            reverse=True
        )[:10]
        
        return {
            'total_versions': total_versions,
            'active_versions': active_versions,
            'total_usage': total_usage,
            'ab_test_assignments': len(self.client_assignments),
            'top_performing_versions': [
                {
                    'version_id': v.version_id,
                    'approach': v.approach.value,
                    'context': v.context.value,
                    'language': v.language,
                    'performance_score': v.performance_score,
                    'usage_count': v.usage_count,
                    'success_rate': v.success_rate
                }
                for v in top_versions
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def deactivate_prompt_version(self, version_id: str) -> bool:
        """
        Deactivate a prompt version
        
        Args:
            version_id: Version identifier
            
        Returns:
            True if successful
        """
        for versions in self.prompt_versions.values():
            for version in versions:
                if version.version_id == version_id:
                    version.active = False
                    logger.info(f"Deactivated prompt version {version_id}")
                    return True
        
        logger.warning(f"Version {version_id} not found for deactivation")
        return False
    
    def get_language_phrases(self, language: str) -> Dict[str, List[str]]:
        """
        Get therapeutic phrases for a specific language
        
        Args:
            language: Language code
            
        Returns:
            Dictionary of phrase categories
        """
        return self.prompt_library.LANGUAGE_PHRASES.get(
            language,
            self.prompt_library.LANGUAGE_PHRASES["en"]
        )


# Global service instance
therapeutic_prompt_service = TherapeuticPromptService()
