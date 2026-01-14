"""
Tests for Therapeutic Prompt Service
Validates prompt selection, A/B testing, and cultural sensitivity
🏆 Breaking Barriers UK 2026 compliant
"""

import pytest
from backend.src.services.therapeutic_prompt_service import (
    TherapeuticPromptService,
    PromptSelectionCriteria,
    TherapeuticApproach,
    ConversationContext,
    CulturalContext,
    PromptVersion
)


class TestTherapeuticPromptService:
    """Test suite for therapeutic prompt service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = TherapeuticPromptService()
    
    def test_service_initialization(self):
        """Test that service initializes with default prompts"""
        assert len(self.service.prompt_versions) > 0
        assert len(self.service.ab_test_config) == 0
        assert len(self.service.client_assignments) == 0
    
    def test_select_prompt_basic(self):
        """Test basic prompt selection"""
        criteria = PromptSelectionCriteria(
            approach=TherapeuticApproach.COGNITIVE_BEHAVIORAL,
            context=ConversationContext.INITIAL_SESSION,
            language="en",
            cultural_context=CulturalContext.NEUTRAL
        )
        
        prompt_version, metadata = self.service.select_prompt(criteria)
        
        assert prompt_version is not None
        assert isinstance(prompt_version, PromptVersion)
        assert prompt_version.approach == TherapeuticApproach.COGNITIVE_BEHAVIORAL
        assert prompt_version.context == ConversationContext.INITIAL_SESSION
        assert prompt_version.language == "en"
        assert "CBT" in prompt_version.prompt_text or "Cognitive Behavioral" in prompt_version.prompt_text
        
        # Check metadata
        assert metadata['version_id'] == prompt_version.version_id
        assert metadata['approach'] == TherapeuticApproach.COGNITIVE_BEHAVIORAL.value
        assert metadata['language'] == "en"
    
    def test_select_prompt_different_approaches(self):
        """Test prompt selection for different therapeutic approaches"""
        approaches = [
            TherapeuticApproach.COGNITIVE_BEHAVIORAL,
            TherapeuticApproach.PERSON_CENTERED,
            TherapeuticApproach.MINDFULNESS_BASED,
            TherapeuticApproach.TRAUMA_INFORMED
        ]
        
        for approach in approaches:
            criteria = PromptSelectionCriteria(
                approach=approach,
                context=ConversationContext.ONGOING_SESSION,
                language="en",
                cultural_context=CulturalContext.NEUTRAL
            )
            
            prompt_version, metadata = self.service.select_prompt(criteria)
            
            assert prompt_version.approach == approach
            assert len(prompt_version.prompt_text) > 100
    
    def test_select_prompt_different_languages(self):
        """Test prompt selection for different languages"""
        languages = ["en", "es", "fr", "de"]
        
        for language in languages:
            criteria = PromptSelectionCriteria(
                approach=TherapeuticApproach.PERSON_CENTERED,
                context=ConversationContext.ONGOING_SESSION,
                language=language,
                cultural_context=CulturalContext.NEUTRAL
            )
            
            prompt_version, metadata = self.service.select_prompt(criteria)
            
            assert prompt_version.language == language
            assert metadata['language'] == language
    
    def test_select_prompt_crisis_context(self):
        """Test prompt selection for crisis intervention"""
        criteria = PromptSelectionCriteria(
            approach=TherapeuticApproach.TRAUMA_INFORMED,
            context=ConversationContext.CRISIS_INTERVENTION,
            language="en",
            cultural_context=CulturalContext.NEUTRAL
        )
        
        prompt_version, metadata = self.service.select_prompt(criteria)
        
        assert prompt_version.context == ConversationContext.CRISIS_INTERVENTION
        assert "CRISIS" in prompt_version.prompt_text or "crisis" in prompt_version.prompt_text
        assert "safety" in prompt_version.prompt_text.lower()
    
    def test_select_prompt_cultural_sensitivity(self):
        """Test prompt selection with cultural context"""
        cultural_contexts = [
            CulturalContext.EASTERN_COLLECTIVISTIC,
            CulturalContext.LATIN_AMERICAN,
            CulturalContext.SOUTH_ASIAN
        ]
        
        for cultural_context in cultural_contexts:
            criteria = PromptSelectionCriteria(
                approach=TherapeuticApproach.PERSON_CENTERED,
                context=ConversationContext.ONGOING_SESSION,
                language="en",
                cultural_context=cultural_context
            )
            
            prompt_version, metadata = self.service.select_prompt(criteria)
            
            assert prompt_version.cultural_context == cultural_context
            # Should contain cultural sensitivity additions
            assert "Cultural Sensitivity" in prompt_version.prompt_text
    
    def test_ab_testing_assignment(self):
        """Test A/B testing client assignment"""
        # Add multiple versions for same criteria
        approach = TherapeuticApproach.COGNITIVE_BEHAVIORAL
        context = ConversationContext.ONGOING_SESSION
        language = "en"
        cultural_context = CulturalContext.NEUTRAL
        
        # Add a custom version
        version_id = self.service.add_prompt_version(
            approach=approach,
            context=context,
            language=language,
            cultural_context=cultural_context,
            custom_prompt="Custom CBT prompt for testing"
        )
        
        assert version_id is not None
        
        # Select with client ID (should use A/B testing)
        criteria = PromptSelectionCriteria(
            approach=approach,
            context=context,
            language=language,
            cultural_context=cultural_context
        )
        
        client_id = "test_client_123"
        prompt_version1, metadata1 = self.service.select_prompt(
            criteria, client_id=client_id, enable_ab_testing=True
        )
        
        # Same client should get same version
        prompt_version2, metadata2 = self.service.select_prompt(
            criteria, client_id=client_id, enable_ab_testing=True
        )
        
        assert prompt_version1.version_id == prompt_version2.version_id
        assert client_id in self.service.client_assignments
    
    def test_prompt_performance_update(self):
        """Test updating prompt performance metrics"""
        criteria = PromptSelectionCriteria(
            approach=TherapeuticApproach.PERSON_CENTERED,
            context=ConversationContext.ONGOING_SESSION,
            language="en",
            cultural_context=CulturalContext.NEUTRAL
        )
        
        prompt_version, metadata = self.service.select_prompt(criteria)
        version_id = prompt_version.version_id
        
        initial_score = prompt_version.performance_score
        
        # Update with successful session
        self.service.update_prompt_performance(
            version_id=version_id,
            success=True,
            feedback_score=0.9
        )
        
        # Performance should improve
        # Note: We need to get the version again to see updated score
        prompt_version2, _ = self.service.select_prompt(criteria)
        if prompt_version2.version_id == version_id:
            assert prompt_version2.performance_score >= initial_score
    
    def test_safety_guidelines_included(self):
        """Test that all prompts include safety guidelines"""
        criteria = PromptSelectionCriteria(
            approach=TherapeuticApproach.COGNITIVE_BEHAVIORAL,
            context=ConversationContext.ONGOING_SESSION,
            language="en",
            cultural_context=CulturalContext.NEUTRAL
        )
        
        prompt_version, metadata = self.service.select_prompt(criteria)
        
        # Check for safety-related keywords
        prompt_text = prompt_version.prompt_text.lower()
        assert "safety" in prompt_text or "red flag" in prompt_text
        assert "self-harm" in prompt_text or "suicide" in prompt_text
        assert "crisis" in prompt_text or "emergency" in prompt_text
    
    def test_get_language_phrases(self):
        """Test getting language-specific therapeutic phrases"""
        # English phrases
        en_phrases = self.service.get_language_phrases("en")
        assert "validation" in en_phrases
        assert "empathy" in en_phrases
        assert len(en_phrases["validation"]) > 0
        
        # Spanish phrases
        es_phrases = self.service.get_language_phrases("es")
        assert "validation" in es_phrases
        assert len(es_phrases["validation"]) > 0
        
        # Unknown language should fallback to English
        unknown_phrases = self.service.get_language_phrases("xx")
        assert unknown_phrases == en_phrases
    
    def test_prompt_analytics(self):
        """Test getting prompt analytics"""
        # Use some prompts
        for i in range(5):
            criteria = PromptSelectionCriteria(
                approach=TherapeuticApproach.PERSON_CENTERED,
                context=ConversationContext.ONGOING_SESSION,
                language="en",
                cultural_context=CulturalContext.NEUTRAL
            )
            self.service.select_prompt(criteria, client_id=f"client_{i}")
        
        analytics = self.service.get_prompt_analytics()
        
        assert "total_versions" in analytics
        assert "active_versions" in analytics
        assert "total_usage" in analytics
        assert "top_performing_versions" in analytics
        assert analytics["total_versions"] > 0
        assert analytics["total_usage"] >= 5
    
    def test_deactivate_prompt_version(self):
        """Test deactivating a prompt version"""
        # Add a custom version
        version_id = self.service.add_prompt_version(
            approach=TherapeuticApproach.COGNITIVE_BEHAVIORAL,
            context=ConversationContext.ONGOING_SESSION,
            language="en",
            cultural_context=CulturalContext.NEUTRAL,
            custom_prompt="Test prompt to deactivate"
        )
        
        # Deactivate it
        result = self.service.deactivate_prompt_version(version_id)
        assert result is True
        
        # Try to deactivate non-existent version
        result = self.service.deactivate_prompt_version("non_existent_id")
        assert result is False
    
    def test_fallback_prompt(self):
        """Test fallback prompt when selection fails"""
        # Create criteria with invalid combination
        criteria = PromptSelectionCriteria(
            approach=TherapeuticApproach.COGNITIVE_BEHAVIORAL,
            context=ConversationContext.ONGOING_SESSION,
            language="invalid_lang",
            cultural_context=CulturalContext.NEUTRAL
        )
        
        # Should still return a prompt (fallback)
        prompt_version, metadata = self.service.select_prompt(criteria)
        
        assert prompt_version is not None
        assert len(prompt_version.prompt_text) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
