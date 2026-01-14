"""
Language Processing Service for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Handles real-time language identification, language-specific processing pipelines,
accent and dialect recognition, and language preference learning.

Requirements: 10.1, 10.2, 10.5, 10.6
"""

import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from .multi_language_conversation_service import (
    SupportedLanguage,
    LanguageProfile,
    multi_language_conversation_service
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ProcessingPipeline(Enum):
    """Language-specific processing pipelines"""
    LATIN_SCRIPT = "latin_script"
    CYRILLIC_SCRIPT = "cyrillic_script"
    CJK_SCRIPT = "cjk_script"
    ARABIC_SCRIPT = "arabic_script"
    DEVANAGARI_SCRIPT = "devanagari_script"


@dataclass
class LanguagePreference:
    """User language preference profile"""
    user_id: str
    primary_language: SupportedLanguage
    secondary_languages: List[SupportedLanguage] = field(default_factory=list)
    accent_preference: Optional[str] = None
    dialect_preference: Optional[str] = None
    formality_preference: str = "mixed"  # "formal", "informal", "mixed"
    usage_count: int = 0
    last_used: float = 0.0
    confidence_score: float = 0.5  # 0.0 to 1.0
    
    def update_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used = time.time()
        # Increase confidence with usage
        self.confidence_score = min(1.0, self.confidence_score + 0.05)


@dataclass
class RealTimeLanguageDetection:
    """Real-time language detection result"""
    session_id: str
    detected_language: SupportedLanguage
    confidence: float
    detection_time_ms: float
    audio_features: Dict[str, Any] = field(default_factory=dict)
    text_features: Dict[str, Any] = field(default_factory=dict)
    accent_detected: Optional[str] = None
    dialect_detected: Optional[str] = None
    processing_pipeline: ProcessingPipeline = ProcessingPipeline.LATIN_SCRIPT


@dataclass
class LanguageProcessingMetrics:
    """Metrics for language processing"""
    session_id: str
    total_detections: int = 0
    successful_detections: int = 0
    language_switches: int = 0
    average_confidence: float = 0.0
    average_detection_time_ms: float = 0.0
    pipeline_switches: int = 0
    accent_adaptations: int = 0
    
    def update_detection(self, confidence: float, detection_time_ms: float):
        """Update detection metrics"""
        self.total_detections += 1
        if confidence > 0.7:
            self.successful_detections += 1
        
        # Running average
        alpha = 0.1
        self.average_confidence = (
            alpha * confidence + (1 - alpha) * self.average_confidence
        )
        self.average_detection_time_ms = (
            alpha * detection_time_ms + (1 - alpha) * self.average_detection_time_ms
        )


class LanguageProcessingService:
    """
    Service for real-time language processing
    
    Handles language identification, processing pipeline selection,
    accent/dialect recognition, and preference learning.
    """
    
    # Pipeline mappings
    LANGUAGE_TO_PIPELINE = {
        SupportedLanguage.ENGLISH: ProcessingPipeline.LATIN_SCRIPT,
        SupportedLanguage.SPANISH: ProcessingPipeline.LATIN_SCRIPT,
        SupportedLanguage.FRENCH: ProcessingPipeline.LATIN_SCRIPT,
        SupportedLanguage.GERMAN: ProcessingPipeline.LATIN_SCRIPT,
        SupportedLanguage.ITALIAN: ProcessingPipeline.LATIN_SCRIPT,
        SupportedLanguage.PORTUGUESE: ProcessingPipeline.LATIN_SCRIPT,
        SupportedLanguage.DUTCH: ProcessingPipeline.LATIN_SCRIPT,
        SupportedLanguage.POLISH: ProcessingPipeline.LATIN_SCRIPT,
        SupportedLanguage.RUSSIAN: ProcessingPipeline.CYRILLIC_SCRIPT,
        SupportedLanguage.CHINESE: ProcessingPipeline.CJK_SCRIPT,
        SupportedLanguage.JAPANESE: ProcessingPipeline.CJK_SCRIPT,
        SupportedLanguage.KOREAN: ProcessingPipeline.CJK_SCRIPT,
        SupportedLanguage.ARABIC: ProcessingPipeline.ARABIC_SCRIPT,
        SupportedLanguage.HINDI: ProcessingPipeline.DEVANAGARI_SCRIPT,
    }
    
    def __init__(self):
        """Initialize language processing service"""
        self._user_preferences: Dict[str, LanguagePreference] = {}
        self._session_metrics: Dict[str, LanguageProcessingMetrics] = {}
        self._session_languages: Dict[str, SupportedLanguage] = {}
        self._session_pipelines: Dict[str, ProcessingPipeline] = {}
        self._language_history: Dict[str, List[Tuple[float, SupportedLanguage]]] = defaultdict(list)
        logger.info("Language Processing Service initialized")
    
    def detect_language_realtime(
        self,
        session_id: str,
        text: str,
        audio_features: Optional[Dict[str, Any]] = None
    ) -> RealTimeLanguageDetection:
        """
        Perform real-time language detection
        
        Args:
            session_id: Session identifier
            text: Text to analyze
            audio_features: Optional audio features
            
        Returns:
            RealTimeLanguageDetection result
        """
        start_time = time.time()
        
        # Get user preference if available
        user_id = self._get_user_id_from_session(session_id)
        user_pref = self._user_preferences.get(user_id) if user_id else None
        
        # Use multi-language service for detection
        detection_result = multi_language_conversation_service.detect_language(
            text, audio_features
        )
        
        # If user has strong preference and detection is uncertain, use preference
        if user_pref and detection_result.confidence < 0.7:
            if user_pref.confidence_score > 0.8:
                detected_language = user_pref.primary_language
                confidence = user_pref.confidence_score
                logger.info(
                    f"Using user preference for session {session_id}: "
                    f"{detected_language.value}"
                )
            else:
                detected_language = detection_result.detected_language
                confidence = detection_result.confidence
        else:
            detected_language = detection_result.detected_language
            confidence = detection_result.confidence
        
        # Detect accent/dialect if audio features provided
        accent = None
        dialect = None
        if audio_features:
            accent = multi_language_conversation_service.detect_accent_or_dialect(
                audio_features, detected_language
            )
            dialect = self._detect_dialect(text, detected_language)
        
        # Determine processing pipeline
        pipeline = self.LANGUAGE_TO_PIPELINE.get(
            detected_language,
            ProcessingPipeline.LATIN_SCRIPT
        )
        
        # Calculate detection time
        detection_time_ms = (time.time() - start_time) * 1000
        
        # Create result
        result = RealTimeLanguageDetection(
            session_id=session_id,
            detected_language=detected_language,
            confidence=confidence,
            detection_time_ms=detection_time_ms,
            audio_features=audio_features or {},
            text_features=self._extract_text_features(text),
            accent_detected=accent,
            dialect_detected=dialect,
            processing_pipeline=pipeline
        )
        
        # Update metrics
        self._update_metrics(session_id, confidence, detection_time_ms)
        
        # Update language history
        self._language_history[session_id].append((time.time(), detected_language))
        
        # Check for language switch
        if session_id in self._session_languages:
            if self._session_languages[session_id] != detected_language:
                self._handle_language_switch(session_id, detected_language)
        
        # Update session state
        self._session_languages[session_id] = detected_language
        self._session_pipelines[session_id] = pipeline
        
        logger.info(
            f"Real-time detection for session {session_id}: "
            f"{detected_language.value} (confidence: {confidence:.2f}, "
            f"time: {detection_time_ms:.2f}ms)"
        )
        
        return result
    
    def get_processing_pipeline(
        self,
        session_id: str
    ) -> Optional[ProcessingPipeline]:
        """
        Get current processing pipeline for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            ProcessingPipeline or None
        """
        return self._session_pipelines.get(session_id)
    
    def switch_processing_pipeline(
        self,
        session_id: str,
        new_pipeline: ProcessingPipeline
    ) -> bool:
        """
        Switch processing pipeline for session
        
        Args:
            session_id: Session identifier
            new_pipeline: New pipeline to use
            
        Returns:
            True if successful
        """
        try:
            old_pipeline = self._session_pipelines.get(session_id)
            self._session_pipelines[session_id] = new_pipeline
            
            # Update metrics
            if session_id in self._session_metrics:
                self._session_metrics[session_id].pipeline_switches += 1
            
            logger.info(
                f"Switched pipeline for session {session_id}: "
                f"{old_pipeline.value if old_pipeline else 'None'} -> {new_pipeline.value}"
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to switch pipeline for session {session_id}: {e}")
            return False
    
    def learn_language_preference(
        self,
        user_id: str,
        language: SupportedLanguage,
        accent: Optional[str] = None,
        dialect: Optional[str] = None
    ):
        """
        Learn and update user language preference
        
        Args:
            user_id: User identifier
            language: Preferred language
            accent: Optional accent preference
            dialect: Optional dialect preference
        """
        if user_id not in self._user_preferences:
            # Create new preference
            self._user_preferences[user_id] = LanguagePreference(
                user_id=user_id,
                primary_language=language,
                accent_preference=accent,
                dialect_preference=dialect
            )
        else:
            # Update existing preference
            pref = self._user_preferences[user_id]
            
            # If language changed, move old primary to secondary
            if pref.primary_language != language:
                if pref.primary_language not in pref.secondary_languages:
                    pref.secondary_languages.append(pref.primary_language)
                pref.primary_language = language
            
            # Update accent/dialect if provided
            if accent:
                pref.accent_preference = accent
            if dialect:
                pref.dialect_preference = dialect
        
        # Update usage
        self._user_preferences[user_id].update_usage()
        
        logger.info(
            f"Updated language preference for user {user_id}: {language.value}"
        )
    
    def get_language_preference(
        self,
        user_id: str
    ) -> Optional[LanguagePreference]:
        """
        Get user language preference
        
        Args:
            user_id: User identifier
            
        Returns:
            LanguagePreference or None
        """
        return self._user_preferences.get(user_id)
    
    def adapt_for_accent(
        self,
        text: str,
        accent: str,
        language: SupportedLanguage
    ) -> str:
        """
        Adapt text for specific accent
        
        Args:
            text: Original text
            accent: Target accent
            language: Language
            
        Returns:
            Adapted text
        """
        # Placeholder implementation
        # In production, this would use accent-specific adaptations
        logger.debug(f"Adapting text for accent: {accent} ({language.value})")
        return text
    
    def adapt_for_dialect(
        self,
        text: str,
        dialect: str,
        language: SupportedLanguage
    ) -> str:
        """
        Adapt text for specific dialect
        
        Args:
            text: Original text
            dialect: Target dialect
            language: Language
            
        Returns:
            Adapted text
        """
        # Placeholder implementation
        # In production, this would use dialect-specific adaptations
        logger.debug(f"Adapting text for dialect: {dialect} ({language.value})")
        return text
    
    def get_session_metrics(
        self,
        session_id: str
    ) -> Optional[LanguageProcessingMetrics]:
        """
        Get language processing metrics for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            LanguageProcessingMetrics or None
        """
        return self._session_metrics.get(session_id)
    
    def get_language_history(
        self,
        session_id: str
    ) -> List[Tuple[float, SupportedLanguage]]:
        """
        Get language detection history for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of (timestamp, language) tuples
        """
        return self._language_history.get(session_id, [])
    
    def _get_user_id_from_session(self, session_id: str) -> Optional[str]:
        """Extract user ID from session ID"""
        # Placeholder - in production, this would query session data
        return None
    
    def _detect_dialect(
        self,
        text: str,
        language: SupportedLanguage
    ) -> Optional[str]:
        """
        Detect dialect from text
        
        Args:
            text: Text to analyze
            language: Detected language
            
        Returns:
            Dialect identifier or None
        """
        # Placeholder implementation
        # In production, this would use dialect detection models
        return None
    
    def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """
        Extract features from text for language detection
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of text features
        """
        return {
            'length': len(text),
            'word_count': len(text.split()),
            'has_special_chars': any(ord(c) > 127 for c in text),
            'avg_word_length': sum(len(word) for word in text.split()) / max(len(text.split()), 1)
        }
    
    def _update_metrics(
        self,
        session_id: str,
        confidence: float,
        detection_time_ms: float
    ):
        """Update session metrics"""
        if session_id not in self._session_metrics:
            self._session_metrics[session_id] = LanguageProcessingMetrics(
                session_id=session_id
            )
        
        self._session_metrics[session_id].update_detection(
            confidence, detection_time_ms
        )
    
    def _handle_language_switch(
        self,
        session_id: str,
        new_language: SupportedLanguage
    ):
        """
        Handle language switch during session
        
        Args:
            session_id: Session identifier
            new_language: New detected language
        """
        old_language = self._session_languages.get(session_id)
        
        # Update metrics
        if session_id in self._session_metrics:
            self._session_metrics[session_id].language_switches += 1
        
        # Update multi-language service
        multi_language_conversation_service.switch_language(session_id, new_language)
        
        # Switch pipeline if needed
        new_pipeline = self.LANGUAGE_TO_PIPELINE.get(
            new_language,
            ProcessingPipeline.LATIN_SCRIPT
        )
        old_pipeline = self._session_pipelines.get(session_id)
        
        if old_pipeline != new_pipeline:
            self.switch_processing_pipeline(session_id, new_pipeline)
        
        logger.info(
            f"Language switch detected for session {session_id}: "
            f"{old_language.value if old_language else 'None'} -> {new_language.value}"
        )
    
    def cleanup_session(self, session_id: str):
        """
        Cleanup session data
        
        Args:
            session_id: Session identifier
        """
        self._session_languages.pop(session_id, None)
        self._session_pipelines.pop(session_id, None)
        self._session_metrics.pop(session_id, None)
        self._language_history.pop(session_id, None)
        
        logger.info(f"Cleaned up language processing data for session {session_id}")


# Global service instance
language_processing_service = LanguageProcessingService()
