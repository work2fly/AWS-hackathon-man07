"""
Unit tests for Multi-Language Conversation Service
🏆 Breaking Barriers UK 2026 compliant

Tests language detection, cultural adaptation, and multi-language support.
"""

import os
import pytest

# Set AWS region before importing services
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from src.services.multi_language_conversation_service import (
    MultiLanguageConversationService,
    SupportedLanguage,
    CulturalContext,
    TherapeuticApproach,
    LanguageDetectionResult
)


class TestMultiLanguageConversationService:
    """Test suite for Multi-Language Conversation Service"""
    
    @pytest.fixture
    def service(self):
        """Create multi-language service"""
        return MultiLanguageConversationService()
    
    def test_detect_english(self, service):
        """Test English language detection"""
        # Act
        result = service.detect_language("Hello, how are you today?")
        
        # Assert
        assert result.detected_language == SupportedLanguage.ENGLISH
        assert result.confidence > 0.0
    
    def test_detect_spanish(self, service):
        """Test Spanish language detection"""
        # Act
        result = service.detect_language("Hola, ¿cómo está usted hoy?")
        
        # Assert
        assert result.detected_language == SupportedLanguage.SPANISH
        assert result.confidence > 0.0
    
    def test_detect_french(self, service):
        """Test French language detection"""
        # Act
        result = service.detect_language("Bonjour, comment allez-vous?")
        
        # Assert
        assert result.detected_language == SupportedLanguage.FRENCH
        assert result.confidence > 0.0
    
    def test_set_and_get_session_language(self, service):
        """Test setting and getting session language"""
        # Act
        service.set_session_language("session123", SupportedLanguage.SPANISH)
        language = service.get_session_language("session123")
        
        # Assert
        assert language == SupportedLanguage.SPANISH
    
    def test_get_language_profile(self, service):
        """Test getting language profile"""
        # Act
        profile = service.get_language_profile(SupportedLanguage.SPANISH)
        
        # Assert
        assert profile is not None
        assert profile.language_code == "es"
        assert profile.cultural_context == CulturalContext.LATIN_AMERICAN
        assert len(profile.preferred_approaches) > 0
    
    def test_get_therapeutic_approach_for_culture(self, service):
        """Test getting therapeutic approach for culture"""
        # Act
        approach = service.get_therapeutic_approach_for_culture(
            SupportedLanguage.SPANISH
        )
        
        # Assert
        assert approach in [
            TherapeuticApproach.FAMILY_SYSTEMS,
            TherapeuticApproach.NARRATIVE,
            TherapeuticApproach.PERSON_CENTERED
        ]
    
    def test_get_culturally_appropriate_greeting(self, service):
        """Test getting culturally appropriate greeting"""
        # Act
        greeting_en = service.get_culturally_appropriate_greeting(SupportedLanguage.ENGLISH)
        greeting_es = service.get_culturally_appropriate_greeting(SupportedLanguage.SPANISH)
        
        # Assert
        assert "hello" in greeting_en.lower() or "how" in greeting_en.lower()
        assert "hola" in greeting_es.lower() or "cómo" in greeting_es.lower()
    
    def test_get_empathy_expression(self, service):
        """Test getting empathy expression"""
        # Act
        empathy_en = service.get_empathy_expression(SupportedLanguage.ENGLISH)
        empathy_es = service.get_empathy_expression(SupportedLanguage.SPANISH)
        
        # Assert
        assert len(empathy_en) > 0
        assert len(empathy_es) > 0
        assert empathy_en != empathy_es
    
    def test_get_cultural_considerations(self, service):
        """Test getting cultural considerations"""
        # Act
        considerations = service.get_cultural_considerations(SupportedLanguage.SPANISH)
        
        # Assert
        assert len(considerations) > 0
        assert any("family" in c.lower() for c in considerations)
    
    def test_switch_language(self, service):
        """Test switching language during session"""
        # Arrange
        service.set_session_language("session123", SupportedLanguage.ENGLISH)
        
        # Act
        success = service.switch_language("session123", SupportedLanguage.SPANISH)
        new_language = service.get_session_language("session123")
        
        # Assert
        assert success is True
        assert new_language == SupportedLanguage.SPANISH
    
    def test_get_supported_languages(self, service):
        """Test getting list of supported languages"""
        # Act
        languages = service.get_supported_languages()
        
        # Assert
        assert len(languages) > 0
        assert all("code" in lang for lang in languages)
        assert all("name" in lang for lang in languages)
        assert any(lang["code"] == "en" for lang in languages)
        assert any(lang["code"] == "es" for lang in languages)
    
    def test_adapt_response_for_culture(self, service):
        """Test adapting response for culture"""
        # Act
        response = "This is a test response"
        adapted = service.adapt_response_for_culture(
            response,
            SupportedLanguage.SPANISH
        )
        
        # Assert
        assert adapted is not None
        assert len(adapted) > 0
