"""
Tests for Real-Time Audio Processing Pipeline
🏆 Breaking Barriers UK 2026 compliant

Tests the integration of audio streaming, language processing,
voice synthesis, and error recovery services.
"""

import pytest
from unittest.mock import Mock, patch
import time

from src.services.audio_streaming_service import (
    AudioStreamingService,
    AudioStreamConfig,
    AudioQuality,
    AudioChunk,
    AudioFormat
)
from src.services.language_processing_service import (
    LanguageProcessingService,
    SupportedLanguage
)
from src.services.voice_synthesis_service import (
    VoiceSynthesisService,
    VoiceSynthesisRequest,
    EmotionalTone,
    VoiceGender
)
from src.services.audio_error_recovery_service import (
    AudioErrorRecoveryService,
    ErrorType,
    RecoveryConfig
)


class TestAudioStreamingIntegration:
    """Test audio streaming service integration"""
    
    def test_initialize_stream(self):
        """Test stream initialization"""
        service = AudioStreamingService()
        session_id = "test-session-1"
        
        result = service.initialize_stream(session_id)
        
        assert result['success'] is True
        assert result['session_id'] == session_id
        assert 'config' in result
    
    def test_process_audio_chunk(self):
        """Test audio chunk processing"""
        service = AudioStreamingService()
        session_id = "test-session-2"
        
        # Initialize stream
        service.initialize_stream(session_id)
        
        # Create test chunk
        chunk_data = {
            'chunk_id': 'chunk-1',
            'session_id': session_id,
            'sequence_number': 0,
            'audio_data': 'dGVzdCBhdWRpbyBkYXRh',  # base64 encoded
            'format': 'opus',
            'sample_rate': 16000,
            'channels': 1,
            'timestamp': time.time(),
            'duration_ms': 100.0
        }
        
        result = service.process_audio_chunk(session_id, chunk_data)
        
        assert result['success'] is True
        assert result['session_id'] == session_id
        assert 'metrics' in result
    
    def test_adaptive_buffering(self):
        """Test adaptive buffering based on network conditions"""
        service = AudioStreamingService()
        session_id = "test-session-3"
        
        # Initialize with medium quality
        config = AudioStreamConfig.from_quality_preset(AudioQuality.MEDIUM)
        service.initialize_stream(session_id, config)
        
        # Simulate poor network by processing chunks with high latency
        for i in range(10):
            chunk_data = {
                'chunk_id': f'chunk-{i}',
                'session_id': session_id,
                'sequence_number': i,
                'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
                'format': 'opus',
                'sample_rate': 16000,
                'channels': 1,
                'timestamp': time.time() - 0.5,  # Simulate high latency
                'duration_ms': 100.0
            }
            service.process_audio_chunk(session_id, chunk_data)
        
        # Check metrics
        metrics = service.get_stream_metrics(session_id)
        assert metrics is not None
        assert metrics['chunks_received'] == 10


class TestLanguageProcessingIntegration:
    """Test language processing service integration"""
    
    def test_realtime_language_detection(self):
        """Test real-time language detection"""
        service = LanguageProcessingService()
        session_id = "test-session-4"
        
        # Test English detection
        result = service.detect_language_realtime(
            session_id,
            "Hello, how are you feeling today?",
            None
        )
        
        assert result.detected_language == SupportedLanguage.ENGLISH
        assert result.confidence > 0.0
        assert result.detection_time_ms > 0.0
    
    def test_language_preference_learning(self):
        """Test language preference learning"""
        service = LanguageProcessingService()
        user_id = "test-user-1"
        
        # Learn preference
        service.learn_language_preference(
            user_id,
            SupportedLanguage.SPANISH,
            accent="ES"
        )
        
        # Get preference
        pref = service.get_language_preference(user_id)
        
        assert pref is not None
        assert pref.primary_language == SupportedLanguage.SPANISH
        assert pref.accent_preference == "ES"
        assert pref.usage_count == 1
    
    def test_processing_pipeline_selection(self):
        """Test processing pipeline selection"""
        service = LanguageProcessingService()
        session_id = "test-session-5"
        
        # Detect language
        service.detect_language_realtime(
            session_id,
            "Bonjour, comment allez-vous?",
            None
        )
        
        # Get pipeline
        pipeline = service.get_processing_pipeline(session_id)
        
        assert pipeline is not None


class TestVoiceSynthesisIntegration:
    """Test voice synthesis service integration"""
    
    def test_voice_profile_selection(self):
        """Test voice profile selection"""
        service = VoiceSynthesisService()
        
        # Select English US Female profile
        profile = service.select_voice_profile(
            SupportedLanguage.ENGLISH,
            "US",
            VoiceGender.FEMALE
        )
        
        assert profile is not None
        assert profile.language == SupportedLanguage.ENGLISH
        assert profile.accent == "US"
        assert profile.gender == VoiceGender.FEMALE
    
    def test_speech_synthesis(self):
        """Test speech synthesis"""
        service = VoiceSynthesisService()
        session_id = "test-session-6"
        
        # Create synthesis request
        request = VoiceSynthesisRequest(
            session_id=session_id,
            text="Hello, how can I help you today?",
            language=SupportedLanguage.ENGLISH,
            tone=EmotionalTone.WARM
        )
        
        # Synthesize
        result = service.synthesize_speech(request)
        
        assert result.session_id == session_id
        assert result.synthesis_time_ms > 0.0
        assert result.quality_score > 0.0
        assert result.tone_applied == EmotionalTone.WARM
    
    def test_emotional_tone_application(self):
        """Test emotional tone application"""
        service = VoiceSynthesisService()
        session_id = "test-session-7"
        
        # Test different tones
        tones = [
            EmotionalTone.WARM,
            EmotionalTone.EMPATHETIC,
            EmotionalTone.CALM
        ]
        
        for tone in tones:
            request = VoiceSynthesisRequest(
                session_id=session_id,
                text="I understand how you feel.",
                language=SupportedLanguage.ENGLISH,
                tone=tone
            )
            
            result = service.synthesize_speech(request)
            assert result.tone_applied == tone
    
    def test_output_quality_monitoring(self):
        """Test output quality monitoring"""
        service = VoiceSynthesisService()
        session_id = "test-session-8"
        
        # Synthesize multiple times
        for i in range(5):
            request = VoiceSynthesisRequest(
                session_id=session_id,
                text=f"Test message {i}",
                language=SupportedLanguage.ENGLISH
            )
            service.synthesize_speech(request)
        
        # Get quality report
        report = service.monitor_output_quality(session_id)
        
        assert report['session_id'] == session_id
        assert report['total_syntheses'] == 5
        assert 'quality_status' in report
        assert 'performance_status' in report


class TestErrorRecoveryIntegration:
    """Test error recovery service integration"""
    
    def test_error_handling(self):
        """Test error handling"""
        service = AudioErrorRecoveryService()
        session_id = "test-session-9"
        
        # Handle error
        success = service.handle_error(
            session_id,
            ErrorType.CONNECTION_LOST,
            "Connection lost to audio service"
        )
        
        # Check statistics
        stats = service.get_error_statistics(session_id)
        assert stats is not None
        assert stats.total_errors == 1
    
    def test_retry_with_backoff(self):
        """Test retry with exponential backoff"""
        service = AudioErrorRecoveryService()
        session_id = "test-session-10"
        
        # Create a mock operation that fails twice then succeeds
        call_count = [0]
        
        def mock_operation():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Operation failed")
            return "success"
        
        # Retry operation
        success, result = service.retry_with_backoff(
            session_id,
            mock_operation
        )
        
        assert success is True
        assert result == "success"
        assert call_count[0] == 3
    
    def test_graceful_degradation(self):
        """Test graceful degradation"""
        service = AudioErrorRecoveryService()
        session_id = "test-session-11"
        
        # Apply degradation
        config = service.degrade_gracefully(session_id, degradation_level=2)
        
        assert config['audio_quality'] == 'low'
        assert config['sample_rate'] == 8000
    
    def test_circuit_breaker(self):
        """Test circuit breaker functionality"""
        config = RecoveryConfig(error_threshold=3)
        service = AudioErrorRecoveryService(config)
        session_id = "test-session-12"
        
        # Trigger multiple errors
        for i in range(5):
            service.handle_error(
                session_id,
                ErrorType.AUDIO_PROCESSING_FAILED,
                f"Processing failed {i}"
            )
        
        # Check statistics
        stats = service.get_error_statistics(session_id)
        assert stats.total_errors >= 3


class TestEndToEndPipeline:
    """Test end-to-end audio processing pipeline"""
    
    def test_complete_audio_flow(self):
        """Test complete audio processing flow"""
        # Initialize services
        streaming_service = AudioStreamingService()
        language_service = LanguageProcessingService()
        synthesis_service = VoiceSynthesisService()
        error_service = AudioErrorRecoveryService()
        
        session_id = "test-session-13"
        
        # 1. Initialize audio stream
        stream_result = streaming_service.initialize_stream(session_id)
        assert stream_result['success'] is True
        
        # 2. Process incoming audio chunk
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
        
        # 3. Detect language from transcribed text
        detection_result = language_service.detect_language_realtime(
            session_id,
            "Hello, I need help with my anxiety.",
            None
        )
        assert detection_result.detected_language == SupportedLanguage.ENGLISH
        
        # 4. Synthesize response
        synthesis_request = VoiceSynthesisRequest(
            session_id=session_id,
            text="I'm here to help you. Let's talk about what you're experiencing.",
            language=detection_result.detected_language,
            tone=EmotionalTone.EMPATHETIC
        )
        
        synthesis_result = synthesis_service.synthesize_speech(synthesis_request)
        assert synthesis_result.quality_score > 0.0
        
        # 5. Verify metrics are tracked
        stream_metrics = streaming_service.get_stream_metrics(session_id)
        assert stream_metrics is not None
        
        language_metrics = language_service.get_session_metrics(session_id)
        assert language_metrics is not None
        
        output_report = synthesis_service.monitor_output_quality(session_id)
        assert output_report['total_syntheses'] > 0
    
    def test_error_recovery_in_pipeline(self):
        """Test error recovery during pipeline execution"""
        streaming_service = AudioStreamingService()
        error_service = AudioErrorRecoveryService()
        
        session_id = "test-session-14"
        
        # Initialize stream
        streaming_service.initialize_stream(session_id)
        
        # Simulate error
        success = error_service.handle_error(
            session_id,
            ErrorType.BUFFER_OVERFLOW,
            "Buffer overflow detected"
        )
        
        # Verify recovery was attempted
        stats = error_service.get_error_statistics(session_id)
        assert stats.total_errors > 0
        
        # Apply degradation
        degraded_config = error_service.degrade_gracefully(session_id)
        assert degraded_config['audio_quality'] in ['low', 'medium', 'minimal']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
