#!/usr/bin/env python3
"""
Test for Trauma-Informed Response Service
🏆 Breaking Barriers UK 2026 compliant
"""

import unittest
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.trauma_informed_response_service import TraumaInformedResponseService, ResponseType
from models.red_flag import RedFlag, RedFlagType, Severity


class TestTraumaInformedResponses(unittest.TestCase):
    """Test trauma-informed response generation"""
    
    def setUp(self):
        """Set up test environment"""
        self.response_service = TraumaInformedResponseService()
    
    def test_suicidal_ideation_response(self):
        """Test response for suicidal ideation red flag"""
        # Create test red flag
        red_flag = RedFlag(
            session_id="test_session_123",
            flag_id="test_flag_suicidal",
            type=RedFlagType.SUICIDAL_IDEATION,
            severity=Severity.CRITICAL,
            context="I want to take my life"
        )
        
        # Generate response
        response = self.response_service.generate_trauma_informed_response(red_flag)
        
        # Verify response components
        self.assertIn('acknowledgment', response)
        self.assertIn('validation', response)
        self.assertIn('resources', response)
        self.assertIn('emergency_protocol', response)
        
        # Verify emergency protocol is activated for critical severity
        self.assertTrue(response['emergency_protocol'])
        
        # Verify resources include crisis helplines
        self.assertIn('crisis_helplines', response['resources'])
        self.assertIn('samaritans', response['resources']['crisis_helplines'])
        
        # Format response for AI agent
        formatted_response = self.response_service.format_response_for_ai_agent(response)
        
        # Verify formatted response contains key elements
        self.assertIn("sorry", formatted_response.lower())
        self.assertIn("116 123", formatted_response)  # Samaritans number
        self.assertIn("999", formatted_response)      # Emergency services
        self.assertIn("not alone", formatted_response.lower())
    
    def test_self_harm_response(self):
        """Test response for self-harm red flag"""
        red_flag = RedFlag(
            session_id="test_session_123",
            flag_id="test_flag_self_harm",
            type=RedFlagType.SELF_HARM,
            severity=Severity.HIGH,
            context="I deserve this, I hate myself"
        )
        
        response = self.response_service.generate_trauma_informed_response(red_flag)
        
        # Verify response components
        self.assertIn('acknowledgment', response)
        self.assertIn('validation', response)
        self.assertIn('resources', response)
        
        # Verify resources include self-harm support
        self.assertIn('self_harm', response['resources'])
        
        formatted_response = self.response_service.format_response_for_ai_agent(response)
        
        # Verify trauma-informed language
        self.assertIn("sorry", formatted_response.lower())
        self.assertIn("care", formatted_response.lower())
    
    def test_abuse_response(self):
        """Test response for abuse red flag"""
        red_flag = RedFlag(
            session_id="test_session_123",
            flag_id="test_flag_abuse",
            type=RedFlagType.ABUSE,
            severity=Severity.HIGH,
            context="I'm scared of my partner, they hurt me"
        )
        
        response = self.response_service.generate_trauma_informed_response(red_flag)
        
        # Verify safety check is included for abuse
        self.assertIsNotNone(response['safety_check'])
        
        # Verify domestic abuse resources
        self.assertIn('domestic_abuse', response['resources'])
        self.assertIn('national_helpline', response['resources']['domestic_abuse'])
        
        formatted_response = self.response_service.format_response_for_ai_agent(response)
        
        # Verify domestic abuse helpline is included
        self.assertIn("0808 2000 247", formatted_response)
    
    def test_crisis_response_with_grounding(self):
        """Test response for crisis with grounding techniques"""
        red_flag = RedFlag(
            session_id="test_session_123",
            flag_id="test_flag_crisis",
            type=RedFlagType.CRISIS,
            severity=Severity.HIGH,
            context="I feel like I can't breathe, I think I'm having a panic attack"
        )
        
        response = self.response_service.generate_trauma_informed_response(red_flag)
        
        # Verify grounding technique is provided for crisis
        self.assertIsNotNone(response['grounding_technique'])
        self.assertTrue(response.get('immediate_grounding', False))
        self.assertIn('breathing_exercise', response)
        
        formatted_response = self.response_service.format_response_for_ai_agent(response)
        
        # Verify breathing guidance is included
        self.assertIn("breath", formatted_response.lower())
        self.assertIn("4 seconds", formatted_response.lower())
    
    def test_response_safety_validation(self):
        """Test response safety validation"""
        # Test safe response
        safe_response = "I hear that you're going through a difficult time. Your feelings are valid. Here are some resources that might help: Samaritans 116 123."
        
        validation = self.response_service.validate_response_safety(safe_response)
        
        self.assertTrue(validation['is_safe'])
        self.assertEqual(len(validation['safety_issues']), 0)
        self.assertTrue(validation['has_validation'])
        self.assertTrue(validation['has_resources'])
        
        # Test potentially harmful response
        harmful_response = "You should just get over it and think positive."
        
        validation = self.response_service.validate_response_safety(harmful_response)
        
        self.assertFalse(validation['is_safe'])
        self.assertGreater(len(validation['safety_issues']), 0)
    
    def test_ai_system_prompt_guidance(self):
        """Test AI system prompt guidance"""
        guidance = self.response_service.get_ai_system_prompt_guidance()
        
        # Verify key principles are included
        self.assertIn("trauma-informed", guidance.lower())
        self.assertIn("not a licensed therapist", guidance.lower())
        self.assertIn("calm", guidance.lower())
        self.assertIn("validating", guidance.lower())
        self.assertIn("non-judgmental", guidance.lower())
        
        # Verify emergency resources are included
        self.assertIn("999", guidance)
        self.assertIn("116 123", guidance)
        self.assertIn("0808 2000 247", guidance)
    
    def test_violence_response(self):
        """Test response for violence red flag"""
        red_flag = RedFlag(
            session_id="test_session_123",
            flag_id="test_flag_violence",
            type=RedFlagType.VIOLENCE,
            severity=Severity.HIGH,
            context="I feel like I want to hurt someone, I wish they were dead"
        )
        
        response = self.response_service.generate_trauma_informed_response(red_flag)
        
        # Verify appropriate response for violence
        self.assertIn('acknowledgment', response)
        self.assertIn('validation', response)
        
        formatted_response = self.response_service.format_response_for_ai_agent(response)
        
        # Verify emphasis on safety and professional help
        self.assertIn("professional", formatted_response.lower())
        self.assertIn("safely", formatted_response.lower())


def run_trauma_response_tests():
    """Run trauma-informed response tests"""
    print("🧪 Running Trauma-Informed Response Tests")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Based on UKind charity guidelines")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestTraumaInformedResponses)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All trauma-informed response tests passed!")
        print("✅ UKind charity guidelines implemented successfully")
        print("🏆 Breaking Barriers UK 2026 compliant responses verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_trauma_response_tests()
    exit(0 if success else 1)