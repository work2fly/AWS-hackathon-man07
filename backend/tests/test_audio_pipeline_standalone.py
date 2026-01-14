"""
Standalone Tests for Real-Time Audio Processing Pipeline
🏆 Breaking Barriers UK 2026 compliant

Tests the audio processing pipeline components without AWS dependencies.
"""

import pytest
import time


def test_audio_streaming_service_import():
    """Test that audio streaming service can be imported"""
    from src.services.audio_streaming_service import (
        AudioStreamingService,
        AudioStreamConfig,
        AudioQuality,
        AudioFormat,
        StreamingState
    )
    
    # Verify classes are available
    assert AudioStreamingService is not None
    assert AudioStreamConfig is not None
    assert AudioQuality is not None
    assert AudioFormat is not None
    assert StreamingState is not None


def test_language_processing_service_import():
    """Test that language processing service can be imported"""
    from src.services.language_processing_service import (
        LanguageProcessingService,
        ProcessingPipeline,
        LanguagePreference,
        RealTimeLanguageDetection
    )
    
    # Verify classes are available
    assert LanguageProcessingService is not None
    assert ProcessingPipeline is not None
    assert LanguagePreference is not None
    assert RealTimeLanguageDetection is not None


def test_voice_synthesis_service_import():
    """Test that voice synthesis service can be imported"""
    from src.services.voice_synthesis_service import (
        VoiceSynthesisService,
        VoiceProfile,
        VoiceSynthesisRequest,
        EmotionalTone,
        VoiceGender
    )
    
    # Verify classes are available
    assert VoiceSynthesisService is not None
    assert VoiceProfile is not None
    assert VoiceSynthesisRequest is not None
    assert EmotionalTone is not None
    assert VoiceGender is not None


def test_error_recovery_service_import():
    """Test that error recovery service can be imported"""
    from src.services.audio_error_recovery_service import (
        AudioErrorRecoveryService,
        ErrorType,
        ErrorSeverity,
        RecoveryStrategy,
        RecoveryConfig
    )
    
    # Verify classes are available
    assert AudioErrorRecoveryService is not None
    assert ErrorType is not None
    assert ErrorSeverity is not None
    assert RecoveryStrategy is not None
    assert RecoveryConfig is not None


def test_audio_streaming_config():
    """Test audio streaming configuration"""
    from src.services.audio_streaming_service import (
        AudioStreamConfig,
        AudioQuality,
        AudioFormat
    )
    
    # Test default config
    config = AudioStreamConfig()
    assert config.format == AudioFormat.OPUS
    assert config.sample_rate == 16000
    assert config.channels == 1
    
    # Test quality presets
    low_config = AudioStreamConfig.from_quality_preset(AudioQuality.LOW)
    assert low_config.sample_rate == 8000
    
    high_config = AudioStreamConfig.from_quality_preset(AudioQuality.HIGH)
    assert high_config.sample_rate == 24000


def test_language_processing_pipeline_mapping():
    """Test language to pipeline mapping"""
    from src.services.language_processing_service import (
        LanguageProcessingService,
        ProcessingPipeline
    )
    from src.services.multi_language_conversation_service import SupportedLanguage
    
    service = LanguageProcessingService()
    
    # Verify mappings exist
    assert SupportedLanguage.ENGLISH in service.LANGUAGE_TO_PIPELINE
    assert SupportedLanguage.SPANISH in service.LANGUAGE_TO_PIPELINE
    assert SupportedLanguage.CHINESE in service.LANGUAGE_TO_PIPELINE
    
    # Verify correct pipeline types
    assert service.LANGUAGE_TO_PIPELINE[SupportedLanguage.ENGLISH] == ProcessingPipeline.LATIN_SCRIPT
    assert service.LANGUAGE_TO_PIPELINE[SupportedLanguage.CHINESE] == ProcessingPipeline.CJK_SCRIPT
    assert service.LANGUAGE_TO_PIPELINE[SupportedLanguage.RUSSIAN] == ProcessingPipeline.CYRILLIC_SCRIPT


def test_voice_profile_selection():
    """Test voice profile selection"""
    from src.services.voice_synthesis_service import (
        VoiceSynthesisService,
        VoiceGender
    )
    from src.services.multi_language_conversation_service import SupportedLanguage
    
    service = VoiceSynthesisService()
    
    # Test profile selection
    profile = service.select_voice_profile(
        SupportedLanguage.ENGLISH,
        "US",
        VoiceGender.FEMALE
    )
    
    assert profile is not None
    assert profile.language == SupportedLanguage.ENGLISH
    assert profile.accent == "US"
    assert profile.gender == VoiceGender.FEMALE


def test_emotional_tone_prosody():
    """Test emotional tone to prosody mapping"""
    from src.services.voice_synthesis_service import (
        VoiceSynthesisService,
        EmotionalTone
    )
    
    service = VoiceSynthesisService()
    
    # Verify all tones have prosody mappings
    for tone in EmotionalTone:
        assert tone in service.TONE_PROSODY
        prosody = service.TONE_PROSODY[tone]
        assert 'pitch_modifier' in prosody
        assert 'speed_modifier' in prosody
        assert 'volume_modifier' in prosody


def test_error_recovery_strategies():
    """Test error recovery strategy mappings"""
    from src.services.audio_error_recovery_service import (
        AudioErrorRecoveryService,
        ErrorType,
        RecoveryStrategy
    )
    
    service = AudioErrorRecoveryService()
    
    # Verify all error types have strategies
    for error_type in ErrorType:
        assert error_type in service.ERROR_RECOVERY_STRATEGIES
        strategy = service.ERROR_RECOVERY_STRATEGIES[error_type]
        assert isinstance(strategy, RecoveryStrategy)


def test_circuit_breaker_initialization():
    """Test circuit breaker initialization"""
    from src.services.audio_error_recovery_service import (
        CircuitBreakerState
    )
    
    breaker = CircuitBreakerState(session_id="test-session")
    
    assert breaker.is_open is False
    assert breaker.error_count == 0
    
    # Test error recording
    breaker.record_error()
    assert breaker.error_count == 1
    
    # Test success recording
    breaker.record_success()
    assert breaker.error_count == 0


def test_recovery_config():
    """Test recovery configuration"""
    from src.services.audio_error_recovery_service import RecoveryConfig
    
    # Test default config
    config = RecoveryConfig()
    assert config.max_retries == 3
    assert config.retry_delay_ms == 1000
    assert config.exponential_backoff is True
    
    # Test custom config
    custom_config = RecoveryConfig(
        max_retries=5,
        retry_delay_ms=500,
        exponential_backoff=False
    )
    assert custom_config.max_retries == 5
    assert custom_config.retry_delay_ms == 500
    assert custom_config.exponential_backoff is False


def test_audio_buffer_operations():
    """Test audio buffer operations"""
    from src.services.audio_streaming_service import AudioBuffer
    
    buffer = AudioBuffer(max_size=5, session_id="test-session")
    
    # Test initial state
    assert buffer.is_empty() is True
    assert buffer.is_full() is False
    assert buffer.get_fill_level() == 0.0
    
    # Test resize
    buffer.resize(10)
    assert buffer.max_size == 10


def test_streaming_metrics():
    """Test streaming metrics"""
    from src.services.audio_streaming_service import StreamingMetrics
    
    metrics = StreamingMetrics(session_id="test-session")
    
    # Test latency update
    metrics.update_latency(150.0)
    assert metrics.current_latency_ms == 150.0
    assert metrics.average_latency_ms == 150.0
    
    # Test packet loss update
    metrics.update_packet_loss(0, 0)
    assert metrics.chunks_received == 1
    
    # Test connection quality calculation
    quality = metrics.calculate_connection_quality()
    assert 0.0 <= quality <= 1.0


def test_language_preference():
    """Test language preference"""
    from src.services.language_processing_service import LanguagePreference
    from src.services.multi_language_conversation_service import SupportedLanguage
    
    pref = LanguagePreference(
        user_id="test-user",
        primary_language=SupportedLanguage.ENGLISH
    )
    
    assert pref.usage_count == 0
    assert pref.confidence_score == 0.5
    
    # Test usage update
    pref.update_usage()
    assert pref.usage_count == 1
    assert pref.confidence_score > 0.5


def test_error_statistics():
    """Test error statistics"""
    from src.services.audio_error_recovery_service import (
        ErrorStatistics,
        ErrorEvent,
        ErrorType,
        ErrorSeverity
    )
    
    stats = ErrorStatistics(session_id="test-session")
    
    # Create test error
    error = ErrorEvent(
        session_id="test-session",
        error_type=ErrorType.CONNECTION_LOST,
        severity=ErrorSeverity.HIGH,
        timestamp=time.time(),
        message="Test error"
    )
    
    # Record error
    stats.record_error(error)
    assert stats.total_errors == 1
    assert ErrorType.CONNECTION_LOST in stats.errors_by_type
    
    # Record recovery
    stats.record_recovery(True, 100.0)
    assert stats.successful_recoveries == 1


def test_pipeline_integration_structure():
    """Test that all pipeline components can work together"""
    from src.services.audio_streaming_service import AudioStreamingService
    from src.services.language_processing_service import LanguageProcessingService
    from src.services.voice_synthesis_service import VoiceSynthesisService
    from src.services.audio_error_recovery_service import AudioErrorRecoveryService
    
    # Initialize all services
    streaming = AudioStreamingService()
    language = LanguageProcessingService()
    synthesis = VoiceSynthesisService()
    recovery = AudioErrorRecoveryService()
    
    # Verify all services initialized
    assert streaming is not None
    assert language is not None
    assert synthesis is not None
    assert recovery is not None
    
    # Verify services have expected methods
    assert hasattr(streaming, 'initialize_stream')
    assert hasattr(language, 'detect_language_realtime')
    assert hasattr(synthesis, 'synthesize_speech')
    assert hasattr(recovery, 'handle_error')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
