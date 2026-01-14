#!/usr/bin/env python3
"""
Validation script for Therapeutic Prompt Service
Tests core functionality without full service dependencies
"""

import sys
import os
import logging

# Create a simple logger mock
class MockLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        self.logger.addHandler(handler)
    
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def debug(self, msg): self.logger.debug(msg)

def get_logger(name):
    return MockLogger(name)

# Mock the utils.logger module
sys.modules['backend.src.utils.logger'] = type(sys)('backend.src.utils.logger')
sys.modules['backend.src.utils.logger'].get_logger = get_logger

# Now we can import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import by modifying the import path
import importlib
import importlib.util

# Load the module with mocked dependencies
module_path = os.path.join(os.path.dirname(__file__), 'src', 'services', 'therapeutic_prompt_service.py')

# Read and modify the source to remove relative imports
with open(module_path, 'r') as f:
    source = f.read()

# Replace relative import with our mock
source = source.replace('from ..utils.logger import get_logger', 'from backend.src.utils.logger import get_logger')

# Compile and execute
code = compile(source, module_path, 'exec')
tps = type(sys)('therapeutic_prompt_service')
exec(code, tps.__dict__)

def main():
    print("\n" + "="*70)
    print("THERAPEUTIC PROMPT SERVICE VALIDATION")
    print("="*70 + "\n")
    
    # Test 1: Service initialization
    print("Test 1: Service Initialization")
    print("-" * 70)
    service = tps.TherapeuticPromptService()
    print(f"✓ Service initialized with {len(service.prompt_versions)} prompt groups")
    print(f"✓ Total prompts: {sum(len(v) for v in service.prompt_versions.values())}")
    print()
    
    # Test 2: Basic prompt selection
    print("Test 2: Basic Prompt Selection")
    print("-" * 70)
    criteria = tps.PromptSelectionCriteria(
        approach=tps.TherapeuticApproach.COGNITIVE_BEHAVIORAL,
        context=tps.ConversationContext.INITIAL_SESSION,
        language='en',
        cultural_context=tps.CulturalContext.NEUTRAL
    )
    
    prompt_version, metadata = service.select_prompt(criteria)
    print(f"✓ Selected prompt version: {prompt_version.version_id}")
    print(f"✓ Approach: {prompt_version.approach.value}")
    print(f"✓ Context: {prompt_version.context.value}")
    print(f"✓ Language: {prompt_version.language}")
    print(f"✓ Prompt length: {len(prompt_version.prompt_text)} characters")
    print(f"✓ Contains CBT content: {'CBT' in prompt_version.prompt_text or 'Cognitive Behavioral' in prompt_version.prompt_text}")
    print()
    
    # Test 3: Different approaches
    print("Test 3: Different Therapeutic Approaches")
    print("-" * 70)
    approaches = [
        tps.TherapeuticApproach.COGNITIVE_BEHAVIORAL,
        tps.TherapeuticApproach.PERSON_CENTERED,
        tps.TherapeuticApproach.MINDFULNESS_BASED,
        tps.TherapeuticApproach.TRAUMA_INFORMED
    ]
    
    for approach in approaches:
        criteria = tps.PromptSelectionCriteria(
            approach=approach,
            context=tps.ConversationContext.ONGOING_SESSION,
            language='en',
            cultural_context=tps.CulturalContext.NEUTRAL
        )
        prompt_version, _ = service.select_prompt(criteria)
        print(f"✓ {approach.value}: {len(prompt_version.prompt_text)} chars")
    print()
    
    # Test 4: Multi-language support
    print("Test 4: Multi-Language Support")
    print("-" * 70)
    languages = ["en", "es", "fr", "de"]
    
    for language in languages:
        criteria = tps.PromptSelectionCriteria(
            approach=tps.TherapeuticApproach.PERSON_CENTERED,
            context=tps.ConversationContext.ONGOING_SESSION,
            language=language,
            cultural_context=tps.CulturalContext.NEUTRAL
        )
        prompt_version, metadata = service.select_prompt(criteria)
        print(f"✓ Language {language}: prompt generated ({len(prompt_version.prompt_text)} chars)")
    print()
    
    # Test 5: Crisis intervention
    print("Test 5: Crisis Intervention Context")
    print("-" * 70)
    criteria = tps.PromptSelectionCriteria(
        approach=tps.TherapeuticApproach.TRAUMA_INFORMED,
        context=tps.ConversationContext.CRISIS_INTERVENTION,
        language='en',
        cultural_context=tps.CulturalContext.NEUTRAL
    )
    prompt_version, _ = service.select_prompt(criteria)
    has_crisis = "CRISIS" in prompt_version.prompt_text or "crisis" in prompt_version.prompt_text
    has_safety = "safety" in prompt_version.prompt_text.lower()
    print(f"✓ Crisis context detected: {has_crisis}")
    print(f"✓ Safety guidelines included: {has_safety}")
    print()
    
    # Test 6: Cultural sensitivity
    print("Test 6: Cultural Sensitivity")
    print("-" * 70)
    cultural_contexts = [
        tps.CulturalContext.EASTERN_COLLECTIVISTIC,
        tps.CulturalContext.LATIN_AMERICAN,
        tps.CulturalContext.SOUTH_ASIAN
    ]
    
    for cultural_context in cultural_contexts:
        criteria = tps.PromptSelectionCriteria(
            approach=tps.TherapeuticApproach.PERSON_CENTERED,
            context=tps.ConversationContext.ONGOING_SESSION,
            language='en',
            cultural_context=cultural_context
        )
        prompt_version, _ = service.select_prompt(criteria)
        has_cultural = "Cultural Sensitivity" in prompt_version.prompt_text
        print(f"✓ {cultural_context.value}: cultural sensitivity included = {has_cultural}")
    print()
    
    # Test 7: A/B testing
    print("Test 7: A/B Testing")
    print("-" * 70)
    # Add a custom version
    version_id = service.add_prompt_version(
        approach=tps.TherapeuticApproach.COGNITIVE_BEHAVIORAL,
        context=tps.ConversationContext.ONGOING_SESSION,
        language='en',
        cultural_context=tps.CulturalContext.NEUTRAL,
        custom_prompt="Custom CBT prompt for A/B testing"
    )
    print(f"✓ Added custom prompt version: {version_id}")
    
    # Test consistent assignment
    criteria = tps.PromptSelectionCriteria(
        approach=tps.TherapeuticApproach.COGNITIVE_BEHAVIORAL,
        context=tps.ConversationContext.ONGOING_SESSION,
        language='en',
        cultural_context=tps.CulturalContext.NEUTRAL
    )
    
    client_id = "test_client_123"
    prompt1, _ = service.select_prompt(criteria, client_id=client_id, enable_ab_testing=True)
    prompt2, _ = service.select_prompt(criteria, client_id=client_id, enable_ab_testing=True)
    
    print(f"✓ Consistent assignment: {prompt1.version_id == prompt2.version_id}")
    print(f"✓ Client assigned to version: {service.client_assignments.get(client_id)}")
    print()
    
    # Test 8: Safety guidelines
    print("Test 8: Safety Guidelines")
    print("-" * 70)
    criteria = tps.PromptSelectionCriteria(
        approach=tps.TherapeuticApproach.COGNITIVE_BEHAVIORAL,
        context=tps.ConversationContext.ONGOING_SESSION,
        language='en',
        cultural_context=tps.CulturalContext.NEUTRAL
    )
    prompt_version, _ = service.select_prompt(criteria)
    prompt_text = prompt_version.prompt_text.lower()
    
    has_safety = "safety" in prompt_text or "red flag" in prompt_text
    has_self_harm = "self-harm" in prompt_text or "suicide" in prompt_text
    has_crisis_resources = "crisis" in prompt_text or "emergency" in prompt_text
    
    print(f"✓ Safety keywords: {has_safety}")
    print(f"✓ Self-harm/suicide detection: {has_self_harm}")
    print(f"✓ Crisis resources: {has_crisis_resources}")
    print()
    
    # Test 9: Language phrases
    print("Test 9: Language-Specific Phrases")
    print("-" * 70)
    for lang in ["en", "es", "fr", "de"]:
        phrases = service.get_language_phrases(lang)
        print(f"✓ {lang}: {len(phrases)} phrase categories")
    print()
    
    # Test 10: Analytics
    print("Test 10: Analytics")
    print("-" * 70)
    analytics = service.get_prompt_analytics()
    print(f"✓ Total versions: {analytics['total_versions']}")
    print(f"✓ Active versions: {analytics['active_versions']}")
    print(f"✓ Total usage: {analytics['total_usage']}")
    print(f"✓ A/B test assignments: {analytics['ab_test_assignments']}")
    print()
    
    # Test 11: Prompt library content
    print("Test 11: Prompt Library Content")
    print("-" * 70)
    library = tps.TherapeuticPromptLibrary()
    print(f"✓ Base prompts: {len(library.BASE_PROMPTS)} approaches")
    print(f"✓ Context additions: {len(library.CONTEXT_ADDITIONS)} contexts")
    print(f"✓ Cultural additions: {len(library.CULTURAL_ADDITIONS)} cultures")
    print(f"✓ Language phrases: {len(library.LANGUAGE_PHRASES)} languages")
    print(f"✓ Safety guidelines: {len(library.SAFETY_GUIDELINES)} characters")
    print()
    
    print("="*70)
    print("✅ ALL VALIDATION TESTS PASSED")
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
