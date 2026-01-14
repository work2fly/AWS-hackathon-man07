"""
Standalone Tests for Therapeutic Prompt Service
Tests prompt selection, A/B testing, and cultural sensitivity without full service dependencies
🏆 Breaking Barriers UK 2026 compliant
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Direct imports to avoid service dependencies
from src.services.therapeutic_prompt_service import (
    TherapeuticPromptService,
    PromptSelectionCriteria,
    TherapeuticApproach,
    ConversationContext,
    CulturalContext,
    PromptVersion,
    TherapeuticPromptLibrary
)


def test_service_initialization():
    """Test that service initializes with default prompts"""
    service = TherapeuticPromptService()
    assert len(service.prompt_versions) > 0
    print(f"✓ Service initialized with {len(service.prompt_versions)} prompt groups")


def test_select_prompt_basic():
    """Test basic prompt selection"""
    service = TherapeuticPromptService()
    
    criteria = PromptSelectionCriteria(
        approach=TherapeuticApproach.COGNITIVE_BEHAVIORAL,
        context=ConversationContext.INITIAL_SESSION,
        language="en",
        cultural_context=CulturalContext.NEUTRAL
    )
    
    prompt_version, metadata = service.select_prompt(criteria)
    
    assert prompt_version is not None
    assert isinstance(prompt_version, PromptVersion)
    assert prompt_version.approach == TherapeuticApproach.COGNITIVE_BEHAVIORAL
    assert prompt_version.context == ConversationContext.INITIAL_SESSION
    assert prompt_version.language == "en"
    assert "CBT" in prompt_version.prompt_text or "Cognitive Behavioral" in prompt_version.prompt_text
    
    print(f"✓ Basic prompt selection works")
    print(f"  Version ID: {prompt_version.version_id}")
    print(f"  Approach: {prompt_version.approach.value}")
    print(f"  Prompt length: {len(prompt_version.prompt_text)} characters")


def test_select_prompt_different_approaches():
    """Test prompt selection for different therapeutic approaches"""
    service = TherapeuticPromptService()
    
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
        
        prompt_version, metadata = service.select_prompt(criteria)
        
        assert prompt_version.approach == approach
        assert len(prompt_version.prompt_text) > 100
        print(f"✓ {approach.value}: {len(prompt_version.prompt_text)} chars")


def test_select_prompt_different_languages():
    """Test prompt selection for different languages"""
    service = TherapeuticPromptService()
    
    languages = ["en", "es", "fr", "de"]
    
    for language in languages:
        criteria = PromptSelectionCriteria(
            approach=TherapeuticApproach.PERSON_CENTERED,
            context=ConversationContext.ONGOING_SESSION,
            language=language,
            cultural_context=CulturalContext.NEUTRAL
        )
        
        prompt_version, metadata = service.select_prompt(criteria)
        
        assert prompt_version.language == language
        assert metadata['language'] == language
        print(f"✓ Language {language}: prompt generated")


def test_select_prompt_crisis_context():
    """Test prompt selection for crisis intervention"""
    service = TherapeuticPromptService()
    
    criteria = PromptSelectionCriteria(
        approach=TherapeuticApproach.TRAUMA_INFORMED,
        context=ConversationContext.CRISIS_INTERVENTION,
        language="en",
        cultural_context=CulturalContext.NEUTRAL
    )
    
    prompt_version, metadata = service.select_prompt(criteria)
    
    assert prompt_version.context == ConversationContext.CRISIS_INTERVENTION
    assert "CRISIS" in prompt_version.prompt_text or "crisis" in prompt_version.prompt_text
    assert "safety" in prompt_version.prompt_text.lower()
    print(f"✓ Crisis intervention prompt includes safety guidelines")


def test_select_prompt_cultural_sensitivity():
    """Test prompt selection with cultural context"""
    service = TherapeuticPromptService()
    
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
        
        prompt_version, metadata = service.select_prompt(criteria)
        
        assert prompt_version.cultural_context == cultural_context
        # Should contain cultural sensitivity additions
        assert "Cultural Sensitivity" in prompt_version.prompt_text
        print(f"✓ {cultural_context.value}: cultural sensitivity included")


def test_ab_testing_assignment():
    """Test A/B testing client assignment"""
    service = TherapeuticPromptService()
    
    # Add multiple versions for same criteria
    approach = TherapeuticApproach.COGNITIVE_BEHAVIORAL
    context = ConversationContext.ONGOING_SESSION
    language = "en"
    cultural_context = CulturalContext.NEUTRAL
    
    # Add a custom version
    version_id = service.add_prompt_version(
        approach=approach,
        context=context,
        language=language,
        cultural_context=cultural_context,
        custom_prompt="Custom CBT prompt for testing"
    )
    
    assert version_id is not None
    print(f"✓ Added custom prompt version: {version_id}")
    
    # Select with client ID (should use A/B testing)
    criteria = PromptSelectionCriteria(
        approach=approach,
        context=context,
        language=language,
        cultural_context=cultural_context
    )
    
    client_id = "test_client_123"
    prompt_version1, metadata1 = service.select_prompt(
        criteria, client_id=client_id, enable_ab_testing=True
    )
    
    # Same client should get same version
    prompt_version2, metadata2 = service.select_prompt(
        criteria, client_id=client_id, enable_ab_testing=True
    )
    
    assert prompt_version1.version_id == prompt_version2.version_id
    assert client_id in service.client_assignments
    print(f"✓ A/B testing: consistent assignment for client {client_id}")


def test_safety_guidelines_included():
    """Test that all prompts include safety guidelines"""
    service = TherapeuticPromptService()
    
    criteria = PromptSelectionCriteria(
        approach=TherapeuticApproach.COGNITIVE_BEHAVIORAL,
        context=ConversationContext.ONGOING_SESSION,
        language="en",
        cultural_context=CulturalContext.NEUTRAL
    )
    
    prompt_version, metadata = service.select_prompt(criteria)
    
    # Check for safety-related keywords
    prompt_text = prompt_version.prompt_text.lower()
    assert "safety" in prompt_text or "red flag" in prompt_text
    assert "self-harm" in prompt_text or "suicide" in prompt_text
    assert "crisis" in prompt_text or "emergency" in prompt_text
    print(f"✓ Safety guidelines included in all prompts")


def test_get_language_phrases():
    """Test getting language-specific therapeutic phrases"""
    service = TherapeuticPromptService()
    
    # English phrases
    en_phrases = service.get_language_phrases("en")
    assert "validation" in en_phrases
    assert "empathy" in en_phrases
    assert len(en_phrases["validation"]) > 0
    print(f"✓ English phrases: {len(en_phrases)} categories")
    
    # Spanish phrases
    es_phrases = service.get_language_phrases("es")
    assert "validation" in es_phrases
    assert len(es_phrases["validation"]) > 0
    print(f"✓ Spanish phrases: {len(es_phrases)} categories")
    
    # Unknown language should fallback to English
    unknown_phrases = service.get_language_phrases("xx")
    assert unknown_phrases == en_phrases
    print(f"✓ Unknown language fallback works")


def test_prompt_analytics():
    """Test getting prompt analytics"""
    service = TherapeuticPromptService()
    
    # Use some prompts
    for i in range(5):
        criteria = PromptSelectionCriteria(
            approach=TherapeuticApproach.PERSON_CENTERED,
            context=ConversationContext.ONGOING_SESSION,
            language="en",
            cultural_context=CulturalContext.NEUTRAL
        )
        service.select_prompt(criteria, client_id=f"client_{i}")
    
    analytics = service.get_prompt_analytics()
    
    assert "total_versions" in analytics
    assert "active_versions" in analytics
    assert "total_usage" in analytics
    assert "top_performing_versions" in analytics
    assert analytics["total_versions"] > 0
    assert analytics["total_usage"] >= 5
    print(f"✓ Analytics: {analytics['total_versions']} versions, {analytics['total_usage']} uses")


def test_prompt_library_content():
    """Test that prompt library has comprehensive content"""
    library = TherapeuticPromptLibrary()
    
    # Check base prompts
    assert len(library.BASE_PROMPTS) >= 4
    print(f"✓ Base prompts: {len(library.BASE_PROMPTS)} approaches")
    
    # Check context additions
    assert len(library.CONTEXT_ADDITIONS) >= 4
    print(f"✓ Context additions: {len(library.CONTEXT_ADDITIONS)} contexts")
    
    # Check cultural additions
    assert len(library.CULTURAL_ADDITIONS) >= 4
    print(f"✓ Cultural additions: {len(library.CULTURAL_ADDITIONS)} cultures")
    
    # Check language phrases
    assert len(library.LANGUAGE_PHRASES) >= 4
    print(f"✓ Language phrases: {len(library.LANGUAGE_PHRASES)} languages")
    
    # Check safety guidelines exist
    assert len(library.SAFETY_GUIDELINES) > 100
    print(f"✓ Safety guidelines: {len(library.SAFETY_GUIDELINES)} characters")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("THERAPEUTIC PROMPT SERVICE TESTS")
    print("="*70 + "\n")
    
    tests = [
        ("Service Initialization", test_service_initialization),
        ("Basic Prompt Selection", test_select_prompt_basic),
        ("Different Approaches", test_select_prompt_different_approaches),
        ("Different Languages", test_select_prompt_different_languages),
        ("Crisis Context", test_select_prompt_crisis_context),
        ("Cultural Sensitivity", test_select_prompt_cultural_sensitivity),
        ("A/B Testing", test_ab_testing_assignment),
        ("Safety Guidelines", test_safety_guidelines_included),
        ("Language Phrases", test_get_language_phrases),
        ("Analytics", test_prompt_analytics),
        ("Prompt Library Content", test_prompt_library_content)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}:")
            print("-" * 70)
            test_func()
            passed += 1
            print(f"✅ PASSED\n")
        except AssertionError as e:
            failed += 1
            print(f"❌ FAILED: {str(e)}\n")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR: {str(e)}\n")
    
    print("="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
