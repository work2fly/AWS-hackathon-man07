"""
Multi-Language Conversation Service for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Handles automatic language detection, culturally appropriate responses,
language-specific therapeutic approaches, and accent/dialect adaptation.

Requirements: 10.1, 10.2, 10.3, 10.4
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from dataclasses import dataclass, field

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SupportedLanguage(Enum):
    """Supported languages for therapy sessions"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    POLISH = "pl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"


class CulturalContext(Enum):
    """Cultural contexts for therapeutic approaches"""
    WESTERN = "western"
    EASTERN = "eastern"
    LATIN_AMERICAN = "latin_american"
    MIDDLE_EASTERN = "middle_eastern"
    AFRICAN = "african"
    SOUTH_ASIAN = "south_asian"
    EAST_ASIAN = "east_asian"
    NEUTRAL = "neutral"


class TherapeuticApproach(Enum):
    """Therapeutic approaches adapted by culture"""
    PERSON_CENTERED = "person_centered"
    CBT = "cbt"
    DBT = "dbt"
    MINDFULNESS = "mindfulness"
    NARRATIVE = "narrative"
    SOLUTION_FOCUSED = "solution_focused"
    FAMILY_SYSTEMS = "family_systems"


@dataclass
class LanguageProfile:
    """Profile for a specific language"""
    language_code: str
    language_name: str
    cultural_context: CulturalContext
    preferred_approaches: List[TherapeuticApproach]
    communication_style: str
    formality_level: str  # "formal", "informal", "mixed"
    common_expressions: Dict[str, str] = field(default_factory=dict)
    cultural_considerations: List[str] = field(default_factory=list)
    accent_variations: List[str] = field(default_factory=list)


@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    detected_language: SupportedLanguage
    confidence: float  # 0.0 to 1.0
    alternative_languages: List[Tuple[SupportedLanguage, float]] = field(default_factory=list)
    dialect_detected: Optional[str] = None
    accent_detected: Optional[str] = None


class MultiLanguageConversationService:
    """
    Service for multi-language conversation support
    
    Handles language detection, cultural adaptation, and language-specific
    therapeutic approaches.
    """
    
    # Language profiles with cultural contexts
    LANGUAGE_PROFILES = {
        SupportedLanguage.ENGLISH: LanguageProfile(
            language_code="en",
            language_name="English",
            cultural_context=CulturalContext.WESTERN,
            preferred_approaches=[
                TherapeuticApproach.PERSON_CENTERED,
                TherapeuticApproach.CBT,
                TherapeuticApproach.MINDFULNESS
            ],
            communication_style="direct",
            formality_level="mixed",
            common_expressions={
                "greeting": "Hello, how are you feeling today?",
                "empathy": "I understand that must be difficult for you.",
                "validation": "Your feelings are completely valid.",
                "closure": "Thank you for sharing with me today."
            },
            cultural_considerations=[
                "Individualism valued",
                "Direct communication preferred",
                "Personal autonomy emphasized"
            ],
            accent_variations=["US", "UK", "Australian", "Canadian"]
        ),
        SupportedLanguage.SPANISH: LanguageProfile(
            language_code="es",
            language_name="Spanish",
            cultural_context=CulturalContext.LATIN_AMERICAN,
            preferred_approaches=[
                TherapeuticApproach.FAMILY_SYSTEMS,
                TherapeuticApproach.NARRATIVE,
                TherapeuticApproach.PERSON_CENTERED
            ],
            communication_style="warm",
            formality_level="formal",
            common_expressions={
                "greeting": "Hola, ¿cómo se siente hoy?",
                "empathy": "Entiendo que esto debe ser difícil para usted.",
                "validation": "Sus sentimientos son completamente válidos.",
                "closure": "Gracias por compartir conmigo hoy."
            },
            cultural_considerations=[
                "Family-oriented culture",
                "Respect for authority",
                "Collectivist values",
                "Importance of personalismo (personal relationships)"
            ],
            accent_variations=["Mexican", "Spanish", "Argentine", "Colombian"]
        ),
        SupportedLanguage.FRENCH: LanguageProfile(
            language_code="fr",
            language_name="French",
            cultural_context=CulturalContext.WESTERN,
            preferred_approaches=[
                TherapeuticApproach.PERSON_CENTERED,
                TherapeuticApproach.NARRATIVE,
                TherapeuticApproach.CBT
            ],
            communication_style="formal",
            formality_level="formal",
            common_expressions={
                "greeting": "Bonjour, comment vous sentez-vous aujourd'hui?",
                "empathy": "Je comprends que cela doit être difficile pour vous.",
                "validation": "Vos sentiments sont tout à fait valides.",
                "closure": "Merci d'avoir partagé avec moi aujourd'hui."
            },
            cultural_considerations=[
                "Intellectual approach valued",
                "Formal communication preferred",
                "Privacy highly valued"
            ],
            accent_variations=["Parisian", "Canadian", "Belgian", "Swiss"]
        ),
        SupportedLanguage.GERMAN: LanguageProfile(
            language_code="de",
            language_name="German",
            cultural_context=CulturalContext.WESTERN,
            preferred_approaches=[
                TherapeuticApproach.CBT,
                TherapeuticApproach.SOLUTION_FOCUSED,
                TherapeuticApproach.PERSON_CENTERED
            ],
            communication_style="direct",
            formality_level="formal",
            common_expressions={
                "greeting": "Guten Tag, wie fühlen Sie sich heute?",
                "empathy": "Ich verstehe, dass das schwierig für Sie sein muss.",
                "validation": "Ihre Gefühle sind völlig berechtigt.",
                "closure": "Vielen Dank, dass Sie heute mit mir gesprochen haben."
            },
            cultural_considerations=[
                "Direct communication valued",
                "Structured approach preferred",
                "Privacy and boundaries important"
            ],
            accent_variations=["Standard", "Austrian", "Swiss"]
        )
    }
    
    def __init__(self):
        """Initialize multi-language conversation service"""
        self._session_languages: Dict[str, SupportedLanguage] = {}
        self._session_profiles: Dict[str, LanguageProfile] = {}
        logger.info("Multi-Language Conversation Service initialized")
    
    def detect_language(
        self,
        text: str,
        audio_features: Optional[Dict[str, Any]] = None
    ) -> LanguageDetectionResult:
        """
        Detect language from text and optional audio features
        
        Args:
            text: Text to analyze
            audio_features: Optional audio features for accent detection
            
        Returns:
            LanguageDetectionResult object
        """
        # Simple heuristic-based detection (in production, use AWS Comprehend or similar)
        # This is a placeholder implementation
        
        # Check for common words in different languages
        language_indicators = {
            SupportedLanguage.SPANISH: ["hola", "gracias", "por favor", "cómo", "está"],
            SupportedLanguage.FRENCH: ["bonjour", "merci", "s'il vous plaît", "comment", "êtes"],
            SupportedLanguage.GERMAN: ["guten", "danke", "bitte", "wie", "sind"],
            SupportedLanguage.ENGLISH: ["hello", "thank", "please", "how", "are"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for language, indicators in language_indicators.items():
            score = sum(1 for word in indicators if word in text_lower)
            if score > 0:
                scores[language] = score / len(indicators)
        
        # Default to English if no match
        if not scores:
            detected_language = SupportedLanguage.ENGLISH
            confidence = 0.5
        else:
            detected_language = max(scores, key=scores.get)
            confidence = scores[detected_language]
        
        # Get alternatives
        alternatives = [
            (lang, score) for lang, score in scores.items()
            if lang != detected_language
        ]
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        result = LanguageDetectionResult(
            detected_language=detected_language,
            confidence=confidence,
            alternative_languages=alternatives[:3]
        )
        
        logger.info(
            f"Detected language: {detected_language.value} "
            f"(confidence: {confidence:.2f})"
        )
        
        return result
    
    def set_session_language(
        self,
        session_id: str,
        language: SupportedLanguage
    ):
        """
        Set language for a session
        
        Args:
            session_id: Session identifier
            language: Language to use
        """
        self._session_languages[session_id] = language
        
        # Load language profile
        if language in self.LANGUAGE_PROFILES:
            self._session_profiles[session_id] = self.LANGUAGE_PROFILES[language]
        
        logger.info(f"Set language for session {session_id}: {language.value}")
    
    def get_session_language(
        self,
        session_id: str
    ) -> Optional[SupportedLanguage]:
        """
        Get language for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            SupportedLanguage or None
        """
        return self._session_languages.get(session_id)
    
    def get_language_profile(
        self,
        language: SupportedLanguage
    ) -> Optional[LanguageProfile]:
        """
        Get language profile
        
        Args:
            language: Language to get profile for
            
        Returns:
            LanguageProfile or None
        """
        return self.LANGUAGE_PROFILES.get(language)
    
    def adapt_response_for_culture(
        self,
        response: str,
        language: SupportedLanguage,
        cultural_context: Optional[CulturalContext] = None
    ) -> str:
        """
        Adapt response for cultural appropriateness
        
        Args:
            response: Original response
            language: Target language
            cultural_context: Optional specific cultural context
            
        Returns:
            Culturally adapted response
        """
        profile = self.LANGUAGE_PROFILES.get(language)
        if not profile:
            return response
        
        # Use provided cultural context or profile default
        context = cultural_context or profile.cultural_context
        
        # Apply cultural adaptations based on context
        adapted_response = response
        
        # Add formality if needed
        if profile.formality_level == "formal":
            # In production, this would use proper translation/adaptation
            adapted_response = response  # Placeholder
        
        logger.debug(
            f"Adapted response for {language.value} "
            f"(cultural context: {context.value})"
        )
        
        return adapted_response
    
    def get_therapeutic_approach_for_culture(
        self,
        language: SupportedLanguage,
        client_preferences: Optional[List[TherapeuticApproach]] = None
    ) -> TherapeuticApproach:
        """
        Get appropriate therapeutic approach for culture
        
        Args:
            language: Client's language
            client_preferences: Optional client preferences
            
        Returns:
            Recommended TherapeuticApproach
        """
        profile = self.LANGUAGE_PROFILES.get(language)
        if not profile:
            return TherapeuticApproach.PERSON_CENTERED
        
        # If client has preferences, try to match with culturally appropriate ones
        if client_preferences:
            for pref in client_preferences:
                if pref in profile.preferred_approaches:
                    return pref
        
        # Return most preferred approach for culture
        return profile.preferred_approaches[0]
    
    def get_culturally_appropriate_greeting(
        self,
        language: SupportedLanguage
    ) -> str:
        """
        Get culturally appropriate greeting
        
        Args:
            language: Target language
            
        Returns:
            Greeting text
        """
        profile = self.LANGUAGE_PROFILES.get(language)
        if not profile:
            return "Hello, how are you feeling today?"
        
        return profile.common_expressions.get(
            "greeting",
            "Hello, how are you feeling today?"
        )
    
    def get_empathy_expression(
        self,
        language: SupportedLanguage
    ) -> str:
        """
        Get culturally appropriate empathy expression
        
        Args:
            language: Target language
            
        Returns:
            Empathy expression
        """
        profile = self.LANGUAGE_PROFILES.get(language)
        if not profile:
            return "I understand that must be difficult for you."
        
        return profile.common_expressions.get(
            "empathy",
            "I understand that must be difficult for you."
        )
    
    def detect_accent_or_dialect(
        self,
        audio_features: Dict[str, Any],
        language: SupportedLanguage
    ) -> Optional[str]:
        """
        Detect accent or dialect from audio features
        
        Args:
            audio_features: Audio analysis features
            language: Detected language
            
        Returns:
            Accent/dialect identifier or None
        """
        # Placeholder implementation
        # In production, this would use audio analysis
        profile = self.LANGUAGE_PROFILES.get(language)
        if not profile or not profile.accent_variations:
            return None
        
        # Return first accent as placeholder
        return profile.accent_variations[0]
    
    def get_cultural_considerations(
        self,
        language: SupportedLanguage
    ) -> List[str]:
        """
        Get cultural considerations for therapeutic approach
        
        Args:
            language: Target language
            
        Returns:
            List of cultural considerations
        """
        profile = self.LANGUAGE_PROFILES.get(language)
        if not profile:
            return []
        
        return profile.cultural_considerations
    
    def switch_language(
        self,
        session_id: str,
        new_language: SupportedLanguage
    ) -> bool:
        """
        Switch language during a session
        
        Args:
            session_id: Session identifier
            new_language: New language to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            old_language = self._session_languages.get(session_id)
            self.set_session_language(session_id, new_language)
            
            logger.info(
                f"Switched language for session {session_id}: "
                f"{old_language.value if old_language else 'None'} -> {new_language.value}"
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to switch language for session {session_id}: {e}")
            return False
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages
        
        Returns:
            List of language dictionaries
        """
        return [
            {
                "code": lang.value,
                "name": profile.language_name,
                "cultural_context": profile.cultural_context.value
            }
            for lang, profile in self.LANGUAGE_PROFILES.items()
        ]


# Global service instance
multi_language_conversation_service = MultiLanguageConversationService()
