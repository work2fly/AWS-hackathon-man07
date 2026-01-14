"""
Voice Synthesis and Output Management Service for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Handles culturally appropriate voice synthesis, emotional tone control,
voice personalization, and output quality monitoring.

Requirements: 10.3, 10.4
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .multi_language_conversation_service import SupportedLanguage, CulturalContext
from ..utils.logger import get_logger

logger = get_logger(__name__)


class VoiceGender(Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class EmotionalTone(Enum):
    """Emotional tone for voice synthesis"""
    NEUTRAL = "neutral"
    WARM = "warm"
    EMPATHETIC = "empathetic"
    ENCOURAGING = "encouraging"
    CALM = "calm"
    PROFESSIONAL = "professional"
    GENTLE = "gentle"
    REASSURING = "reassuring"


class VoiceQuality(Enum):
    """Voice synthesis quality levels"""
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"


@dataclass
class VoiceProfile:
    """Voice synthesis profile"""
    voice_id: str
    language: SupportedLanguage
    gender: VoiceGender
    accent: str
    cultural_context: CulturalContext
    default_tone: EmotionalTone
    pitch_range: tuple = (0.8, 1.2)  # Relative pitch multiplier
    speed_range: tuple = (0.9, 1.1)  # Relative speed multiplier
    warmth_level: float = 0.7  # 0.0 to 1.0
    formality_level: float = 0.5  # 0.0 (informal) to 1.0 (formal)
    supported_tones: List[EmotionalTone] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.supported_tones:
            self.supported_tones = list(EmotionalTone)


@dataclass
class VoiceSynthesisRequest:
    """Request for voice synthesis"""
    session_id: str
    text: str
    language: SupportedLanguage
    tone: EmotionalTone = EmotionalTone.NEUTRAL
    pitch: float = 1.0  # 0.5 to 2.0
    speed: float = 1.0  # 0.5 to 2.0
    volume: float = 1.0  # 0.0 to 1.0
    emphasis_words: List[str] = field(default_factory=list)
    pause_after_ms: int = 0
    quality: VoiceQuality = VoiceQuality.HIGH


@dataclass
class VoiceSynthesisResult:
    """Result of voice synthesis"""
    session_id: str
    audio_data: bytes
    duration_ms: float
    sample_rate: int
    channels: int
    format: str
    synthesis_time_ms: float
    quality_score: float  # 0.0 to 1.0
    tone_applied: EmotionalTone
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutputQualityMetrics:
    """Metrics for output quality monitoring"""
    session_id: str
    total_syntheses: int = 0
    average_quality_score: float = 0.0
    average_synthesis_time_ms: float = 0.0
    tone_distribution: Dict[EmotionalTone, int] = field(default_factory=dict)
    error_count: int = 0
    last_updated: float = 0.0
    
    def update_synthesis(
        self,
        quality_score: float,
        synthesis_time_ms: float,
        tone: EmotionalTone
    ):
        """Update metrics after synthesis"""
        self.total_syntheses += 1
        
        # Running average for quality
        alpha = 0.1
        self.average_quality_score = (
            alpha * quality_score + (1 - alpha) * self.average_quality_score
        )
        
        # Running average for synthesis time
        self.average_synthesis_time_ms = (
            alpha * synthesis_time_ms + (1 - alpha) * self.average_synthesis_time_ms
        )
        
        # Update tone distribution
        if tone not in self.tone_distribution:
            self.tone_distribution[tone] = 0
        self.tone_distribution[tone] += 1
        
        self.last_updated = time.time()


class VoiceSynthesisService:
    """
    Service for voice synthesis and output management
    
    Handles culturally appropriate voice synthesis, emotional tone control,
    voice personalization, and output quality monitoring.
    """
    
    # Predefined voice profiles for different languages and cultures
    VOICE_PROFILES = {
        (SupportedLanguage.ENGLISH, "US", VoiceGender.FEMALE): VoiceProfile(
            voice_id="en-US-female-1",
            language=SupportedLanguage.ENGLISH,
            gender=VoiceGender.FEMALE,
            accent="US",
            cultural_context=CulturalContext.WESTERN,
            default_tone=EmotionalTone.WARM,
            pitch_range=(0.9, 1.1),
            speed_range=(0.95, 1.05),
            warmth_level=0.8,
            formality_level=0.4
        ),
        (SupportedLanguage.ENGLISH, "US", VoiceGender.MALE): VoiceProfile(
            voice_id="en-US-male-1",
            language=SupportedLanguage.ENGLISH,
            gender=VoiceGender.MALE,
            accent="US",
            cultural_context=CulturalContext.WESTERN,
            default_tone=EmotionalTone.CALM,
            pitch_range=(0.8, 1.0),
            speed_range=(0.95, 1.05),
            warmth_level=0.7,
            formality_level=0.5
        ),
        (SupportedLanguage.SPANISH, "ES", VoiceGender.FEMALE): VoiceProfile(
            voice_id="es-ES-female-1",
            language=SupportedLanguage.SPANISH,
            gender=VoiceGender.FEMALE,
            accent="ES",
            cultural_context=CulturalContext.LATIN_AMERICAN,
            default_tone=EmotionalTone.WARM,
            pitch_range=(0.95, 1.15),
            speed_range=(0.9, 1.0),
            warmth_level=0.9,
            formality_level=0.6
        ),
        (SupportedLanguage.FRENCH, "FR", VoiceGender.FEMALE): VoiceProfile(
            voice_id="fr-FR-female-1",
            language=SupportedLanguage.FRENCH,
            gender=VoiceGender.FEMALE,
            accent="FR",
            cultural_context=CulturalContext.WESTERN,
            default_tone=EmotionalTone.PROFESSIONAL,
            pitch_range=(0.9, 1.1),
            speed_range=(0.95, 1.05),
            warmth_level=0.6,
            formality_level=0.7
        ),
        (SupportedLanguage.GERMAN, "DE", VoiceGender.MALE): VoiceProfile(
            voice_id="de-DE-male-1",
            language=SupportedLanguage.GERMAN,
            gender=VoiceGender.MALE,
            accent="DE",
            cultural_context=CulturalContext.WESTERN,
            default_tone=EmotionalTone.PROFESSIONAL,
            pitch_range=(0.85, 1.0),
            speed_range=(0.95, 1.05),
            warmth_level=0.6,
            formality_level=0.7
        ),
    }
    
    # Emotional tone to prosody mappings
    TONE_PROSODY = {
        EmotionalTone.NEUTRAL: {
            'pitch_modifier': 1.0,
            'speed_modifier': 1.0,
            'volume_modifier': 1.0,
            'pause_multiplier': 1.0
        },
        EmotionalTone.WARM: {
            'pitch_modifier': 1.05,
            'speed_modifier': 0.95,
            'volume_modifier': 1.0,
            'pause_multiplier': 1.1
        },
        EmotionalTone.EMPATHETIC: {
            'pitch_modifier': 0.98,
            'speed_modifier': 0.9,
            'volume_modifier': 0.95,
            'pause_multiplier': 1.2
        },
        EmotionalTone.ENCOURAGING: {
            'pitch_modifier': 1.1,
            'speed_modifier': 1.05,
            'volume_modifier': 1.05,
            'pause_multiplier': 0.9
        },
        EmotionalTone.CALM: {
            'pitch_modifier': 0.95,
            'speed_modifier': 0.9,
            'volume_modifier': 0.9,
            'pause_multiplier': 1.3
        },
        EmotionalTone.PROFESSIONAL: {
            'pitch_modifier': 1.0,
            'speed_modifier': 1.0,
            'volume_modifier': 1.0,
            'pause_multiplier': 1.0
        },
        EmotionalTone.GENTLE: {
            'pitch_modifier': 1.02,
            'speed_modifier': 0.92,
            'volume_modifier': 0.9,
            'pause_multiplier': 1.15
        },
        EmotionalTone.REASSURING: {
            'pitch_modifier': 0.97,
            'speed_modifier': 0.93,
            'volume_modifier': 0.95,
            'pause_multiplier': 1.2
        },
    }
    
    def __init__(self):
        """Initialize voice synthesis service"""
        self._session_profiles: Dict[str, VoiceProfile] = {}
        self._session_metrics: Dict[str, OutputQualityMetrics] = {}
        self._user_voice_preferences: Dict[str, Dict[str, Any]] = {}
        logger.info("Voice Synthesis Service initialized")
    
    def select_voice_profile(
        self,
        language: SupportedLanguage,
        accent: str = "US",
        gender: VoiceGender = VoiceGender.FEMALE,
        cultural_context: Optional[CulturalContext] = None
    ) -> VoiceProfile:
        """
        Select appropriate voice profile
        
        Args:
            language: Target language
            accent: Accent preference
            gender: Voice gender
            cultural_context: Optional cultural context
            
        Returns:
            VoiceProfile
        """
        # Try to find exact match
        key = (language, accent, gender)
        if key in self.VOICE_PROFILES:
            return self.VOICE_PROFILES[key]
        
        # Try to find language match with different accent/gender
        for (lang, acc, gen), profile in self.VOICE_PROFILES.items():
            if lang == language:
                return profile
        
        # Default to English US Female
        default_key = (SupportedLanguage.ENGLISH, "US", VoiceGender.FEMALE)
        return self.VOICE_PROFILES.get(
            default_key,
            self.VOICE_PROFILES[list(self.VOICE_PROFILES.keys())[0]]
        )
    
    def set_session_voice(
        self,
        session_id: str,
        profile: VoiceProfile
    ):
        """
        Set voice profile for session
        
        Args:
            session_id: Session identifier
            profile: Voice profile to use
        """
        self._session_profiles[session_id] = profile
        logger.info(
            f"Set voice profile for session {session_id}: "
            f"{profile.voice_id} ({profile.language.value})"
        )
    
    def synthesize_speech(
        self,
        request: VoiceSynthesisRequest
    ) -> VoiceSynthesisResult:
        """
        Synthesize speech from text
        
        Args:
            request: Voice synthesis request
            
        Returns:
            VoiceSynthesisResult
        """
        start_time = time.time()
        
        try:
            # Get voice profile for session
            profile = self._session_profiles.get(request.session_id)
            if not profile:
                # Select default profile
                profile = self.select_voice_profile(request.language)
                self.set_session_voice(request.session_id, profile)
            
            # Apply emotional tone prosody
            prosody = self.TONE_PROSODY.get(request.tone, self.TONE_PROSODY[EmotionalTone.NEUTRAL])
            
            # Calculate final prosody parameters
            final_pitch = request.pitch * prosody['pitch_modifier']
            final_speed = request.speed * prosody['speed_modifier']
            final_volume = request.volume * prosody['volume_modifier']
            
            # Clamp values to valid ranges
            final_pitch = max(0.5, min(2.0, final_pitch))
            final_speed = max(0.5, min(2.0, final_speed))
            final_volume = max(0.0, min(1.0, final_volume))
            
            # In production, this would call AWS Polly or similar TTS service
            # For now, create placeholder result
            audio_data = self._synthesize_audio_placeholder(
                request.text,
                profile,
                final_pitch,
                final_speed,
                final_volume
            )
            
            # Calculate metrics
            synthesis_time_ms = (time.time() - start_time) * 1000
            duration_ms = len(request.text) * 50  # Rough estimate: 50ms per character
            quality_score = self._calculate_quality_score(
                request, profile, synthesis_time_ms
            )
            
            # Create result
            result = VoiceSynthesisResult(
                session_id=request.session_id,
                audio_data=audio_data,
                duration_ms=duration_ms,
                sample_rate=24000,
                channels=1,
                format="opus",
                synthesis_time_ms=synthesis_time_ms,
                quality_score=quality_score,
                tone_applied=request.tone,
                metadata={
                    'voice_id': profile.voice_id,
                    'language': profile.language.value,
                    'accent': profile.accent,
                    'pitch': final_pitch,
                    'speed': final_speed,
                    'volume': final_volume
                }
            )
            
            # Update metrics
            self._update_metrics(request.session_id, result)
            
            logger.info(
                f"Synthesized speech for session {request.session_id}: "
                f"{len(request.text)} chars, {duration_ms:.0f}ms, "
                f"quality: {quality_score:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to synthesize speech for session {request.session_id}: {e}")
            # Update error count
            if request.session_id in self._session_metrics:
                self._session_metrics[request.session_id].error_count += 1
            raise
    
    def apply_emotional_inflection(
        self,
        text: str,
        tone: EmotionalTone,
        emphasis_words: Optional[List[str]] = None
    ) -> str:
        """
        Apply emotional inflection markers to text
        
        Args:
            text: Original text
            tone: Emotional tone to apply
            emphasis_words: Words to emphasize
            
        Returns:
            Text with inflection markers (SSML-like)
        """
        # In production, this would generate proper SSML
        inflected_text = text
        
        # Add emphasis to specified words
        if emphasis_words:
            for word in emphasis_words:
                inflected_text = inflected_text.replace(
                    word,
                    f"<emphasis>{word}</emphasis>"
                )
        
        # Add tone-specific markers
        prosody = self.TONE_PROSODY.get(tone, {})
        if prosody:
            inflected_text = f"<prosody tone='{tone.value}'>{inflected_text}</prosody>"
        
        return inflected_text
    
    def personalize_voice(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ):
        """
        Store user voice preferences
        
        Args:
            user_id: User identifier
            preferences: Voice preferences
        """
        self._user_voice_preferences[user_id] = preferences
        logger.info(f"Updated voice preferences for user {user_id}")
    
    def get_voice_preferences(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user voice preferences
        
        Args:
            user_id: User identifier
            
        Returns:
            Preferences dictionary or None
        """
        return self._user_voice_preferences.get(user_id)
    
    def get_output_metrics(
        self,
        session_id: str
    ) -> Optional[OutputQualityMetrics]:
        """
        Get output quality metrics for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            OutputQualityMetrics or None
        """
        return self._session_metrics.get(session_id)
    
    def monitor_output_quality(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Monitor and report output quality
        
        Args:
            session_id: Session identifier
            
        Returns:
            Quality report dictionary
        """
        metrics = self._session_metrics.get(session_id)
        if not metrics:
            return {
                'session_id': session_id,
                'status': 'no_data',
                'message': 'No metrics available'
            }
        
        # Calculate quality indicators
        quality_status = "excellent" if metrics.average_quality_score > 0.9 else \
                        "good" if metrics.average_quality_score > 0.7 else \
                        "fair" if metrics.average_quality_score > 0.5 else "poor"
        
        performance_status = "excellent" if metrics.average_synthesis_time_ms < 100 else \
                           "good" if metrics.average_synthesis_time_ms < 200 else \
                           "fair" if metrics.average_synthesis_time_ms < 500 else "poor"
        
        return {
            'session_id': session_id,
            'quality_status': quality_status,
            'performance_status': performance_status,
            'average_quality_score': round(metrics.average_quality_score, 2),
            'average_synthesis_time_ms': round(metrics.average_synthesis_time_ms, 2),
            'total_syntheses': metrics.total_syntheses,
            'error_count': metrics.error_count,
            'error_rate': round(metrics.error_count / max(metrics.total_syntheses, 1), 3),
            'tone_distribution': {
                tone.value: count
                for tone, count in metrics.tone_distribution.items()
            }
        }
    
    def optimize_for_network(
        self,
        session_id: str,
        network_quality: float
    ) -> VoiceQuality:
        """
        Optimize voice quality based on network conditions
        
        Args:
            session_id: Session identifier
            network_quality: Network quality score (0.0 to 1.0)
            
        Returns:
            Recommended VoiceQuality
        """
        if network_quality > 0.8:
            quality = VoiceQuality.PREMIUM
        elif network_quality > 0.5:
            quality = VoiceQuality.HIGH
        else:
            quality = VoiceQuality.STANDARD
        
        logger.info(
            f"Optimized voice quality for session {session_id}: "
            f"{quality.value} (network: {network_quality:.2f})"
        )
        
        return quality
    
    def _synthesize_audio_placeholder(
        self,
        text: str,
        profile: VoiceProfile,
        pitch: float,
        speed: float,
        volume: float
    ) -> bytes:
        """
        Placeholder for actual audio synthesis
        
        In production, this would call AWS Polly or similar service
        """
        # Return empty bytes as placeholder
        return b""
    
    def _calculate_quality_score(
        self,
        request: VoiceSynthesisRequest,
        profile: VoiceProfile,
        synthesis_time_ms: float
    ) -> float:
        """
        Calculate quality score for synthesis
        
        Args:
            request: Synthesis request
            profile: Voice profile used
            synthesis_time_ms: Time taken for synthesis
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        # Factors: synthesis time, text length, quality setting
        time_score = max(0.0, 1.0 - (synthesis_time_ms / 1000.0))
        
        # Text length score (prefer reasonable lengths)
        text_length = len(request.text)
        length_score = 1.0 if 10 <= text_length <= 500 else 0.8
        
        # Quality setting score
        quality_scores = {
            VoiceQuality.STANDARD: 0.7,
            VoiceQuality.HIGH: 0.9,
            VoiceQuality.PREMIUM: 1.0
        }
        quality_score = quality_scores.get(request.quality, 0.8)
        
        # Weighted average
        final_score = (
            0.3 * time_score +
            0.2 * length_score +
            0.5 * quality_score
        )
        
        return final_score
    
    def _update_metrics(
        self,
        session_id: str,
        result: VoiceSynthesisResult
    ):
        """Update session metrics"""
        if session_id not in self._session_metrics:
            self._session_metrics[session_id] = OutputQualityMetrics(
                session_id=session_id
            )
        
        self._session_metrics[session_id].update_synthesis(
            result.quality_score,
            result.synthesis_time_ms,
            result.tone_applied
        )
    
    def cleanup_session(self, session_id: str):
        """
        Cleanup session data
        
        Args:
            session_id: Session identifier
        """
        self._session_profiles.pop(session_id, None)
        self._session_metrics.pop(session_id, None)
        logger.info(f"Cleaned up voice synthesis data for session {session_id}")


# Global service instance
voice_synthesis_service = VoiceSynthesisService()
