#!/usr/bin/env python3
"""
Property-Based Tests for Safety Guardrails System
🏆 Breaking Barriers UK 2026 compliant
Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering
**Validates: Requirements 3.5**
"""

import unittest
import sys
import os
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.safety_guardrails_service import (
    SafetyGuardrailsService,
    GuardrailViolationType,
    ResponseQuality
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Test data generators
@st.composite
def generate_safe_therapeutic_response(draw):
    """Generate safe therapeutic responses"""
    validation_phrases = [
        "I hear that you're going through a difficult time.",
        "Thank you for sharing that with me.",
        "Your feelings are valid and understandable.",
        "I can see how challenging this must be for you.",
        "It makes sense that you would feel this way."
    ]
    
    empathy_phrases = [
        "I understand this is difficult.",
        "You're not alone in feeling this way.",
        "It's okay to feel overwhelmed.",
        "You deserve support and care.",
        "I'm here to help you through this."
    ]
    
    resource_phrases = [
        "Would you like to explore some coping strategies?",
        "There are resources available to support you.",
        "Consider reaching out to a professional for additional support.",
        "Let's work together to find what helps you.",
        "You might find it helpful to talk to someone about this."
    ]
    
    # Build response with validation + empathy + resource
    validation = draw(st.sampled_from(validation_phrases))
    empathy = draw(st.sampled_from(empathy_phrases))
    resource = draw(st.sampled_from(resource_phrases))
    
    return f"{validation} {empathy} {resource}"


@st.composite
def generate_inappropriate_response(draw):
    """Generate responses with inappropriate content"""
    inappropriate_types = [
        "Let's be friends outside of therapy.",
        "I also have experienced this in my personal life.",
        "You should definitely leave your partner right now.",
        "You have depression and need medication.",
        "Just get over it and move on.",
        "Drinking might help you relax.",
        "You're overreacting to this situation.",
        "Tell me exactly what happened in graphic detail."
    ]
    
    return draw(st.sampled_from(inappropriate_types))


@st.composite
def generate_user_input_with_pii(draw):
    """Generate user input containing PII"""
    base_text = draw(st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))))
    
    pii_types = [
        ("email", "test.user@example.com"),
        ("phone", "07123 456789"),
        ("postcode", "SW1A 1AA")
    ]
    
    pii_type, pii_value = draw(st.sampled_from(pii_types))
    
    # Insert PII into text
    text_with_pii = f"{base_text} My {pii_type} is {pii_value}"
    
    return text_with_pii, pii_type


class TestSafetyGuardrailsProperties(unittest.TestCase):
    """Property-based tests for safety guardrails system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.guardrails_service = SafetyGuardrailsService()
    
    @given(generate_safe_therapeutic_response())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_safe_responses_pass_validation(self, safe_response):
        """
        Property: Safe therapeutic responses should pass validation
        
        For any safe therapeutic response with validation, empathy, and resources,
        the guardrails should approve it without violations.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        # Validate the safe response
        validation_result = self.guardrails_service.validate_ai_response(safe_response)
        
        # Property: Safe responses should have no violations
        self.assertTrue(validation_result['is_safe'], 
                       f"Safe response flagged as unsafe: {validation_result.get('violations', [])}")
        
        # Property: Safe responses should not need revision
        self.assertFalse(validation_result['needs_revision'],
                        f"Safe response marked for revision: {validation_result.get('recommendation', '')}")
        
        # Property: Violations list should be empty
        self.assertEqual(len(validation_result['violations']), 0,
                        f"Safe response has violations: {validation_result['violations']}")
    
    @given(generate_inappropriate_response())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_inappropriate_responses_detected(self, inappropriate_response):
        """
        Property: Inappropriate responses should be detected and blocked
        
        For any response containing inappropriate content, therapeutic boundary violations,
        harmful advice, or medical diagnosis, the guardrails should detect violations.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        # Validate the inappropriate response
        validation_result = self.guardrails_service.validate_ai_response(inappropriate_response)
        
        # Property: Inappropriate responses should be flagged as unsafe
        self.assertFalse(validation_result['is_safe'],
                        f"Inappropriate response passed validation: {inappropriate_response}")
        
        # Property: Inappropriate responses should need revision
        self.assertTrue(validation_result['needs_revision'],
                       f"Inappropriate response not marked for revision: {inappropriate_response}")
        
        # Property: At least one violation should be detected
        self.assertGreater(len(validation_result['violations']), 0,
                          f"No violations detected for inappropriate response: {inappropriate_response}")
    
    @given(st.text(min_size=20, max_size=500, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_validation_always_returns_structure(self, response_text):
        """
        Property: Validation should always return complete structure
        
        For any text input, validation should return a complete result structure
        with all required fields, never raising exceptions.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        # Validate any text
        validation_result = self.guardrails_service.validate_ai_response(response_text)
        
        # Property: Result should always have required fields
        required_fields = ['is_safe', 'needs_revision', 'violations', 'warnings', 
                          'quality_assessment', 'validated_at', 'recommendation']
        
        for field in required_fields:
            self.assertIn(field, validation_result,
                         f"Validation result missing required field: {field}")
        
        # Property: is_safe should be boolean
        self.assertIsInstance(validation_result['is_safe'], bool,
                             "is_safe should be boolean")
        
        # Property: violations should be a list
        self.assertIsInstance(validation_result['violations'], list,
                             "violations should be a list")
        
        # Property: quality_assessment should be a dict
        self.assertIsInstance(validation_result['quality_assessment'], dict,
                             "quality_assessment should be a dict")
    
    @given(generate_user_input_with_pii())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_pii_filtering_removes_sensitive_data(self, input_data):
        """
        Property: PII filtering should remove sensitive information
        
        For any user input containing PII (email, phone, postcode),
        the filtering should detect and remove it.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        text_with_pii, pii_type = input_data
        
        # Filter the input
        filter_result = self.guardrails_service.filter_user_input(text_with_pii)
        
        # Property: PII should be detected
        self.assertGreater(len(filter_result['pii_removed']), 0,
                          f"PII not detected in text: {text_with_pii}")
        
        # Property: Filtered text should not contain original PII
        # (it should be replaced with placeholder)
        self.assertNotEqual(filter_result['filtered_text'], filter_result['original_text'],
                           f"Text not filtered despite PII detection: {pii_type}")
        
        # Property: Result should indicate what was removed
        self.assertIn(pii_type, filter_result['pii_removed'],
                     f"PII type {pii_type} not recorded in pii_removed list")
    
    @given(st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_quality_assessment_consistent(self, response_text):
        """
        Property: Quality assessment should be consistent and deterministic
        
        For any response text, running quality assessment multiple times
        should produce the same results.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        # Run quality assessment twice
        result1 = self.guardrails_service._assess_response_quality(response_text)
        result2 = self.guardrails_service._assess_response_quality(response_text)
        
        # Property: Results should be identical
        self.assertEqual(result1['quality'], result2['quality'],
                        "Quality assessment not deterministic")
        
        self.assertEqual(result1['quality_score'], result2['quality_score'],
                        "Quality score not deterministic")
        
        self.assertEqual(result1['validation_count'], result2['validation_count'],
                        "Validation count not deterministic")
    
    @given(st.lists(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))), 
                   min_size=1, max_size=10))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_validation_scales_with_input(self, text_list):
        """
        Property: Validation should handle varying input sizes efficiently
        
        For any list of text inputs of varying sizes, validation should
        complete successfully for all inputs.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        # Validate all texts
        results = []
        for text in text_list:
            result = self.guardrails_service.validate_ai_response(text)
            results.append(result)
        
        # Property: All validations should complete
        self.assertEqual(len(results), len(text_list),
                        "Not all validations completed")
        
        # Property: All results should have required structure
        for result in results:
            self.assertIn('is_safe', result)
            self.assertIn('violations', result)
            self.assertIn('quality_assessment', result)
    
    def test_property_fallback_response_always_safe(self):
        """
        Property: Fallback responses should always be safe
        
        For any context, the fallback response should pass all safety checks.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        # Get fallback response
        fallback = self.guardrails_service.get_fallback_response()
        
        # Validate fallback
        validation_result = self.guardrails_service.validate_ai_response(fallback)
        
        # Property: Fallback should always be safe
        self.assertTrue(validation_result['is_safe'],
                       f"Fallback response is not safe: {validation_result.get('violations', [])}")
        
        # Property: Fallback should have no violations
        self.assertEqual(len(validation_result['violations']), 0,
                        f"Fallback response has violations: {validation_result['violations']}")
        
        # Property: Fallback should not need revision
        self.assertFalse(validation_result['needs_revision'],
                        "Fallback response needs revision")
    
    @given(st.text(min_size=1, max_size=1000, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_no_false_positives_on_benign_text(self, benign_text):
        """
        Property: Benign text should not trigger false positive violations
        
        For any text that doesn't contain obvious violation patterns,
        the system should not flag critical violations.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        # Skip texts that actually contain violation keywords
        violation_keywords = ['you should', 'you have depression', 'let\'s be friends', 
                             'drink alcohol', 'just get over it']
        
        assume(not any(keyword in benign_text.lower() for keyword in violation_keywords))
        
        # Validate the benign text
        validation_result = self.guardrails_service.validate_ai_response(benign_text)
        
        # Property: Should not have critical violations
        critical_violations = [v for v in validation_result['violations'] 
                              if v.get('severity') == 'critical']
        
        self.assertEqual(len(critical_violations), 0,
                        f"Benign text triggered critical violations: {critical_violations}")
    
    @given(st.text(min_size=20, max_size=200, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_recommendation_matches_safety_status(self, response_text):
        """
        Property: Recommendation should match safety status
        
        For any response, if it's marked as unsafe, the recommendation
        should indicate blocking or revision.
        
        **Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering**
        **Validates: Requirements 3.5**
        """
        # Validate response
        validation_result = self.guardrails_service.validate_ai_response(response_text)
        
        is_safe = validation_result['is_safe']
        recommendation = validation_result['recommendation']
        
        # Property: Unsafe responses should have BLOCK or REVISE recommendation
        if not is_safe:
            self.assertTrue(
                'BLOCK' in recommendation or 'REVISE' in recommendation,
                f"Unsafe response has inappropriate recommendation: {recommendation}"
            )
        
        # Property: Safe responses should have APPROVE or CAUTION recommendation
        if is_safe and len(validation_result['violations']) == 0:
            self.assertTrue(
                'APPROVE' in recommendation or 'CAUTION' in recommendation or 'WARN' in recommendation,
                f"Safe response has inappropriate recommendation: {recommendation}"
            )


def run_property_tests():
    """Run property-based tests for safety guardrails"""
    print("🧪 Running Property-Based Tests for Safety Guardrails System")
    print("=" * 70)
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: ai-therapy-platform, Property 7: Safety Guardrails and Filtering")
    print("**Validates: Requirements 3.5**")
    print("=" * 70)
    print()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestSafetyGuardrailsProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_property_tests()
    sys.exit(0 if success else 1)
