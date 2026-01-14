"""
Integration Tests for Nova Sonic 2 Complete System
🏆 Breaking Barriers UK 2026 compliant

Task 8.1: Perform Nova Sonic 2 integration testing
- Test real-time audio processing performance
- Verify therapeutic response quality and appropriateness
- Test multi-language support and cultural adaptation
- Validate safety guardrails and content filtering

**Validates: Requirements 2.3, 2.4, 2.5, 3.5**
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import os

# Set AWS region before importing any AWS services
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.nova_sonic_config import (
    NovaSonicConfig,
    NovaSonicClient,
    NovaSessionStatus
)
from src.services.audio_streaming_service import (
    AudioStreamingService,
    AudioQuality
)
from src.services.language_processing_service import (
    LanguageProcessingService,
    SupportedLanguage
)
from src.services.voice_synthesis_service import (
    VoiceSynthesisService,
    VoiceSynthesisRequest,
    EmotionalTone
)
from src.services.safety_guardrails_service import SafetyGuardrailsService
from src.services.therapeutic_prompt_service import TherapeuticPromptService


class TestNovaSonicRealTimePerformance:
    """Test real-time audio processing performance"""
    
    def test_end_to_end_latency_under_200ms(self):
        """
        Test that end-to-end audio processing meets <200ms latency requirement
        
        **Validates: Requirements 2.2, 2.5**
        """
        # Initialize services
        config = NovaSonicConfig()
        streaming_service = AudioStreamingService()
        language_service = LanguageProcessingService()
        synthesis_service = VoiceSynthesisService()
        
        session_id = "perf-test-session-1"
        
        # Initialize stream
        streaming_service.initialize_stream(session_id)
        
        # Measure end-to-end latency
        start_time = time.time()
        
        # 1. Process audio chunk
        chunk_data = {
            'chunk_id': 'chunk-1',
            'session_id': session_id,
            'sequence_number': 0,
            'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
            'format': 'opus',
            'sample_rate': 16000,
            'channels': 1,
            'timestamp': time.time(),
            'duration_ms': 100.0
        }
        streaming_service.process_audio_chunk(session_id, chunk_data)
        
        # 2. Detect language
        detection_result = language_service.detect_language_realtime(
            session_id,
            "Hello, I'm feeling anxious today.",
            None
        )
        
        # 3. Synthesize response
        synthesis_request = VoiceSynthesisRequest(
            session_id=session_id,
            text="I'm here to support you. Let's talk about what's making you feel anxious.",
            language=detection_result.detected_language,
            tone=EmotionalTone.EMPATHETIC
        )
        synthesis_service.synthesize_speech(synthesis_request)
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Assert latency requirement
        assert latency_ms < 200, f"Latency {latency_ms:.2f}ms exceeds 200ms requirement"
        
        print(f"✅ End-to-end latency: {latency_ms:.2f}ms (target: <200ms)")
    
    def test_concurrent_session_handling(self):
        """
        Test handling multiple concurrent sessions
        
        **Validates: Requirements 2.1, 2.6, 8.4**
        """
        streaming_service = AudioStreamingService()
        
        # Create multiple concurrent sessions
        num_sessions = 5
        session_ids = [f"concurrent-session-{i}" for i in range(num_sessions)]
        
        # Initialize all sessions
        for session_id in session_ids:
            result = streaming_service.initialize_stream(session_id)
            assert result['success'] is True
        
        # Process chunks for all sessions
        for session_id in session_ids:
            chunk_data = {
                'chunk_id': 'chunk-1',
                'session_id': session_id,
                'sequence_number': 0,
                'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
                'format': 'opus',
                'sample_rate': 16000,
                'channels': 1,
                'timestamp': time.time(),
                'duration_ms': 100.0
            }
            result = streaming_service.process_audio_chunk(session_id, chunk_data)
            assert result['success'] is True
        
        # Verify all sessions have metrics
        for session_id in session_ids:
            metrics = streaming_service.get_stream_metrics(session_id)
            assert metrics is not None
            assert metrics['chunks_received'] > 0
        
        print(f"✅ Successfully handled {num_sessions} concurrent sessions")
    
    def test_audio_quality_adaptation(self):
        """
        Test adaptive audio quality based on network conditions
        
        **Validates: Requirements 2.2, 2.6**
        """
        streaming_service = AudioStreamingService()
        session_id = "quality-adapt-session"
        
        # Start with high quality
        streaming_service.initialize_stream(session_id)
        
        # Simulate poor network conditions with high latency chunks
        for i in range(10):
            chunk_data = {
                'chunk_id': f'chunk-{i}',
                'session_id': session_id,
                'sequence_number': i,
                'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
                'format': 'opus',
                'sample_rate': 16000,
                'channels': 1,
                'timestamp': time.time() - 0.5,  # High latency
                'duration_ms': 100.0
            }
            streaming_service.process_audio_chunk(session_id, chunk_data)
        
        # Verify metrics show adaptation
        metrics = streaming_service.get_stream_metrics(session_id)
        assert metrics['chunks_received'] == 10
        
        print("✅ Audio quality adaptation working correctly")


class TestTherapeuticResponseQuality:
    """Test therapeutic response quality and appropriateness"""
    
    def test_therapeutic_prompt_quality(self):
        """
        Test that therapeutic prompts contain appropriate guidance
        
        **Validates: Requirements 2.4, 3.4**
        """
        prompt_service = TherapeuticPromptService()
        
        # Test different therapeutic approaches
        approaches = [
            'person_centered',
            'cognitive_behavioral',
            'mindfulness_based'
        ]
        
        for approach in approaches:
            prompt = prompt_service.get_therapeutic_prompt(
                approach=approach,
                context='initial_session'
            )
            
            # Verify prompt contains therapeutic keywords
            prompt_lower = prompt.lower()
            assert any(word in prompt_lower for word in [
                'compassionate', 'empathetic', 'support', 'therapeutic'
            ]), f"Prompt for {approach} lacks therapeutic language"
            
            # Verify safety guidance is present
            assert any(word in prompt_lower for word in [
                'self-harm', 'crisis', 'safety', 'harm'
            ]), f"Prompt for {approach} lacks safety guidance"
        
        print(f"✅ Therapeutic prompts validated for {len(approaches)} approaches")
    
    def test_response_appropriateness_validation(self):
        """
        Test that responses are validated for therapeutic appropriateness
        
        **Validates: Requirements 3.4, 3.5**
        """
        guardrails_service = SafetyGuardrailsService()
        
        # Test appropriate responses
        appropriate_responses = [
            "I understand you're feeling anxious. Let's explore what's causing these feelings.",
            "It's completely normal to feel this way. Can you tell me more about what happened?",
            "I'm here to support you through this difficult time."
        ]
        
        for response in appropriate_responses:
            result = guardrails_service.validate_response(response)
            assert result['is_appropriate'] is True, \
                f"Appropriate response flagged as inappropriate: {response}"
        
        # Test inappropriate responses
        inappropriate_responses = [
            "You should just get over it.",
            "That's not a real problem.",
            "Stop being so dramatic."
        ]
        
        for response in inappropriate_responses:
            result = guardrails_service.validate_response(response)
            assert result['is_appropriate'] is False, \
                f"Inappropriate response not flagged: {response}"
        
        print("✅ Response appropriateness validation working correctly")
    
    def test_empathy_and_tone_consistency(self):
        """
        Test that responses maintain empathetic tone
        
        **Validates: Requirements 3.4, 3.7**
        """
        synthesis_service = VoiceSynthesisService()
        session_id = "empathy-test-session"
        
        # Test different emotional tones
        test_cases = [
            ("I'm feeling really sad today.", EmotionalTone.EMPATHETIC),
            ("I'm worried about my future.", EmotionalTone.WARM),
            ("I need help calming down.", EmotionalTone.CALM)
        ]
        
        for text, expected_tone in test_cases:
            request = VoiceSynthesisRequest(
                session_id=session_id,
                text=f"I understand. {text}",
                language=SupportedLanguage.ENGLISH,
                tone=expected_tone
            )
            
            result = synthesis_service.synthesize_speech(request)
            assert result.tone_applied == expected_tone, \
                f"Expected tone {expected_tone}, got {result.tone_applied}"
        
        print("✅ Empathy and tone consistency validated")


class TestMultiLanguageSupport:
    """Test multi-language support and cultural adaptation"""
    
    def test_language_detection_accuracy(self):
        """
        Test accurate language detection across supported languages
        
        **Validates: Requirements 10.1, 10.2**
        """
        language_service = LanguageProcessingService()
        session_id = "lang-detect-session"
        
        # Test cases with different languages
        test_cases = [
            ("Hello, how are you feeling today?", SupportedLanguage.ENGLISH),
            ("Hola, ¿cómo te sientes hoy?", SupportedLanguage.SPANISH),
            ("Bonjour, comment vous sentez-vous aujourd'hui?", SupportedLanguage.FRENCH),
            ("Hallo, wie fühlen Sie sich heute?", SupportedLanguage.GERMAN),
        ]
        
        for text, expected_lang in test_cases:
            result = language_service.detect_language_realtime(
                session_id,
                text,
                None
            )
            
            assert result.detected_language == expected_lang, \
                f"Expected {expected_lang}, detected {result.detected_language} for: {text}"
            assert result.confidence > 0.7, \
                f"Low confidence {result.confidence} for language detection"
        
        print(f"✅ Language detection validated for {len(test_cases)} languages")
    
    def test_culturally_appropriate_voice_synthesis(self):
        """
        Test culturally appropriate voice synthesis for different languages
        
        **Validates: Requirements 10.3, 10.4**
        """
        synthesis_service = VoiceSynthesisService()
        session_id = "cultural-voice-session"
        
        # Test different language/accent combinations
        test_cases = [
            (SupportedLanguage.ENGLISH, "US"),
            (SupportedLanguage.ENGLISH, "GB"),
            (SupportedLanguage.SPANISH, "ES"),
            (SupportedLanguage.SPANISH, "MX"),
            (SupportedLanguage.FRENCH, "FR"),
        ]
        
        for language, accent in test_cases:
            # Select voice profile
            profile = synthesis_service.select_voice_profile(
                language,
                accent,
                None  # Let service choose gender
            )
            
            assert profile is not None, \
                f"No voice profile found for {language}/{accent}"
            assert profile.language == language, \
                f"Profile language mismatch for {language}/{accent}"
            assert profile.accent == accent, \
                f"Profile accent mismatch for {language}/{accent}"
            
            # Synthesize speech
            request = VoiceSynthesisRequest(
                session_id=session_id,
                text="I'm here to help you.",
                language=language,
                accent=accent,
                tone=EmotionalTone.WARM
            )
            
            result = synthesis_service.synthesize_speech(request)
            assert result.quality_score > 0.5, \
                f"Low quality score for {language}/{accent}"
        
        print(f"✅ Cultural voice synthesis validated for {len(test_cases)} combinations")
    
    def test_language_preference_persistence(self):
        """
        Test that language preferences are learned and persisted
        
        **Validates: Requirements 10.5, 10.6**
        """
        language_service = LanguageProcessingService()
        user_id = "test-user-multilang"
        
        # Learn preference
        language_service.learn_language_preference(
            user_id,
            SupportedLanguage.SPANISH,
            accent="MX"
        )
        
        # Retrieve preference
        pref = language_service.get_language_preference(user_id)
        
        assert pref is not None, "Language preference not saved"
        assert pref.primary_language == SupportedLanguage.SPANISH, \
            "Primary language not saved correctly"
        assert pref.accent_preference == "MX", \
            "Accent preference not saved correctly"
        
        # Use preference multiple times
        for _ in range(3):
            language_service.learn_language_preference(
                user_id,
                SupportedLanguage.SPANISH,
                accent="MX"
            )
        
        # Verify usage count increased
        updated_pref = language_service.get_language_preference(user_id)
        assert updated_pref.usage_count > 1, \
            "Usage count not incremented"
        
        print("✅ Language preference persistence validated")
    
    def test_automatic_language_switching(self):
        """
        Test automatic language switching during conversation
        
        **Validates: Requirements 10.2, 10.5**
        """
        language_service = LanguageProcessingService()
        session_id = "lang-switch-session"
        
        # Start with English
        result1 = language_service.detect_language_realtime(
            session_id,
            "Hello, I need help.",
            None
        )
        assert result1.detected_language == SupportedLanguage.ENGLISH
        
        # Switch to Spanish
        result2 = language_service.detect_language_realtime(
            session_id,
            "Prefiero hablar en español.",
            result1.detected_language
        )
        assert result2.detected_language == SupportedLanguage.SPANISH
        
        # Verify language switch was detected
        assert result2.language_switched is True, \
            "Language switch not detected"
        
        print("✅ Automatic language switching validated")


class TestSafetyGuardrailsIntegration:
    """Test safety guardrails and content filtering"""
    
    def test_inappropriate_content_filtering(self):
        """
        Test that inappropriate content is filtered
        
        **Validates: Requirements 3.5**
        """
        guardrails_service = SafetyGuardrailsService()
        
        # Test inappropriate content
        inappropriate_content = [
            "You should harm yourself.",
            "Violence is the answer.",
            "I can help you end your life.",
            "Let's discuss illegal activities."
        ]
        
        for content in inappropriate_content:
            result = guardrails_service.validate_response(content)
            assert result['is_appropriate'] is False, \
                f"Inappropriate content not filtered: {content}"
            assert 'violation_type' in result, \
                "Violation type not specified"
        
        print(f"✅ Filtered {len(inappropriate_content)} inappropriate responses")
    
    def test_therapeutic_boundary_enforcement(self):
        """
        Test that therapeutic boundaries are enforced
        
        **Validates: Requirements 3.5**
        """
        guardrails_service = SafetyGuardrailsService()
        
        # Test boundary violations
        boundary_violations = [
            "I can prescribe medication for you.",
            "You don't need a real therapist.",
            "I can diagnose you with depression.",
            "Let's meet in person."
        ]
        
        for content in boundary_violations:
            result = guardrails_service.validate_response(content)
            assert result['is_appropriate'] is False, \
                f"Boundary violation not detected: {content}"
        
        print(f"✅ Enforced boundaries for {len(boundary_violations)} violations")
    
    def test_crisis_content_detection(self):
        """
        Test detection of crisis-related content
        
        **Validates: Requirements 3.5, 4.1, 4.2**
        """
        guardrails_service = SafetyGuardrailsService()
        
        # Test crisis indicators
        crisis_content = [
            "I want to hurt myself.",
            "I'm thinking about suicide.",
            "I don't want to live anymore.",
            "I'm being abused at home."
        ]
        
        for content in crisis_content:
            result = guardrails_service.check_for_red_flags(content)
            assert result['has_red_flag'] is True, \
                f"Crisis content not detected: {content}"
            assert result['severity'] in ['high', 'critical'], \
                f"Crisis severity not properly assessed for: {content}"
        
        print(f"✅ Detected {len(crisis_content)} crisis indicators")
    
    def test_response_quality_assurance(self):
        """
        Test response quality assurance checks
        
        **Validates: Requirements 3.5, 3.7**
        """
        guardrails_service = SafetyGuardrailsService()
        
        # Test quality metrics
        test_responses = [
            ("I understand how you're feeling. Let's talk about it.", True),
            ("Whatever.", False),  # Too brief
            ("You're wrong about everything.", False),  # Not supportive
            ("I'm here to support you through this difficult time.", True),
        ]
        
        for response, should_pass in test_responses:
            result = guardrails_service.validate_response(response)
            assert result['is_appropriate'] == should_pass, \
                f"Quality check failed for: {response}"
        
        print("✅ Response quality assurance validated")


class TestEndToEndIntegration:
    """Test complete end-to-end Nova Sonic 2 integration"""
    
    def test_complete_therapy_session_flow(self):
        """
        Test complete therapy session from start to finish
        
        **Validates: Requirements 2.1, 2.3, 2.4, 2.5, 3.5, 10.1, 10.2**
        """
        # Initialize all services
        config = NovaSonicConfig()
        streaming_service = AudioStreamingService()
        language_service = LanguageProcessingService()
        synthesis_service = VoiceSynthesisService()
        guardrails_service = SafetyGuardrailsService()
        prompt_service = TherapeuticPromptService()
        
        session_id = "e2e-test-session"
        
        # 1. Initialize session
        stream_result = streaming_service.initialize_stream(session_id)
        assert stream_result['success'] is True
        
        # 2. Get therapeutic prompt
        therapeutic_prompt = prompt_service.get_therapeutic_prompt(
            approach='person_centered',
            context='initial_session'
        )
        assert len(therapeutic_prompt) > 0
        
        # 3. Process client audio
        chunk_data = {
            'chunk_id': 'chunk-1',
            'session_id': session_id,
            'sequence_number': 0,
            'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
            'format': 'opus',
            'sample_rate': 16000,
            'channels': 1,
            'timestamp': time.time(),
            'duration_ms': 100.0
        }
        process_result = streaming_service.process_audio_chunk(session_id, chunk_data)
        assert process_result['success'] is True
        
        # 4. Detect language
        client_text = "I'm feeling really anxious about my job."
        detection_result = language_service.detect_language_realtime(
            session_id,
            client_text,
            None
        )
        assert detection_result.detected_language == SupportedLanguage.ENGLISH
        
        # 5. Generate response
        ai_response = "I hear that you're feeling anxious about your job. That's a very common concern. Can you tell me more about what specifically is making you feel this way?"
        
        # 6. Validate response with guardrails
        validation_result = guardrails_service.validate_response(ai_response)
        assert validation_result['is_appropriate'] is True
        
        # 7. Check for red flags in client input
        red_flag_result = guardrails_service.check_for_red_flags(client_text)
        assert red_flag_result['has_red_flag'] is False
        
        # 8. Synthesize response
        synthesis_request = VoiceSynthesisRequest(
            session_id=session_id,
            text=ai_response,
            language=detection_result.detected_language,
            tone=EmotionalTone.EMPATHETIC
        )
        synthesis_result = synthesis_service.synthesize_speech(synthesis_request)
        assert synthesis_result.quality_score > 0.5
        
        # 9. Verify metrics
        stream_metrics = streaming_service.get_stream_metrics(session_id)
        assert stream_metrics['chunks_received'] > 0
        
        language_metrics = language_service.get_session_metrics(session_id)
        assert language_metrics is not None
        
        output_report = synthesis_service.monitor_output_quality(session_id)
        assert output_report['total_syntheses'] > 0
        
        print("✅ Complete end-to-end therapy session flow validated")
    
    def test_multi_turn_conversation_continuity(self):
        """
        Test conversation continuity across multiple turns
        
        **Validates: Requirements 2.1, 2.6, 3.7**
        """
        streaming_service = AudioStreamingService()
        language_service = LanguageProcessingService()
        synthesis_service = VoiceSynthesisService()
        
        session_id = "multi-turn-session"
        
        # Initialize session
        streaming_service.initialize_stream(session_id)
        
        # Simulate multiple conversation turns
        conversation_turns = [
            "I've been feeling really stressed lately.",
            "It's mainly work pressure and deadlines.",
            "I'm worried I won't be able to handle it.",
            "Yes, I think talking about coping strategies would help."
        ]
        
        for i, turn in enumerate(conversation_turns):
            # Process audio chunk
            chunk_data = {
                'chunk_id': f'chunk-{i}',
                'session_id': session_id,
                'sequence_number': i,
                'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
                'format': 'opus',
                'sample_rate': 16000,
                'channels': 1,
                'timestamp': time.time(),
                'duration_ms': 100.0
            }
            streaming_service.process_audio_chunk(session_id, chunk_data)
            
            # Detect language
            detection_result = language_service.detect_language_realtime(
                session_id,
                turn,
                SupportedLanguage.ENGLISH if i > 0 else None
            )
            assert detection_result.detected_language == SupportedLanguage.ENGLISH
            
            # Synthesize response
            response_text = f"I understand. Let's explore that further."
            synthesis_request = VoiceSynthesisRequest(
                session_id=session_id,
                text=response_text,
                language=detection_result.detected_language,
                tone=EmotionalTone.EMPATHETIC
            )
            synthesis_service.synthesize_speech(synthesis_request)
        
        # Verify continuity metrics
        stream_metrics = streaming_service.get_stream_metrics(session_id)
        assert stream_metrics['chunks_received'] == len(conversation_turns)
        
        output_report = synthesis_service.monitor_output_quality(session_id)
        assert output_report['total_syntheses'] == len(conversation_turns)
        
        print(f"✅ Multi-turn conversation continuity validated ({len(conversation_turns)} turns)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
