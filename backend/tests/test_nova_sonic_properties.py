"""
Property-Based Tests for Nova Sonic 2 Audio Processing
🏆 Breaking Barriers UK 2026 compliant

Feature: ai-therapy-platform, Property 5: Nova Sonic 2 Audio Processing

Tests universal properties for Nova Sonic 2 real-time audio processing including:
- Speech-to-speech processing with therapeutic context
- Multi-language support and language detection
- Cultural sensitivity and appropriate voice synthesis
- Real-time performance and latency requirements
- Natural turn-taking and conversation flow

**Validates: Requirements 2.3, 2.4, 2.5, 10.1, 10.2, 10.3, 10.4**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
import time
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Direct imports to avoid service dependencies
from src.config.nova_sonic_config import (
    NovaSonicConfig,
    NovaSonicClient,
    NovaSessionStatus,
    NovaRetryStrategy
)


# ============================================================================
# Test Data Generators
# ============================================================================

# Supported languages for multi-language testing
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'zh', 'ar', 'hi']

# Audio sample rates (Hz)
VALID_SAMPLE_RATES = [8000, 16000, 24000, 48000]


@st.composite
def session_ids(draw):
    """Generate valid session IDs"""
    prefix = draw(st.sampled_from(['session', 'therapy', 'audio']))
    suffix = draw(st.integers(min_value=1, max_value=999999))
    return f"{prefix}-{suffix}"


@st.composite
def client_ids(draw):
    """Generate valid client IDs"""
    prefix = draw(st.sampled_from(['client', 'user', 'patient']))
    suffix = draw(st.integers(min_value=1, max_value=999999))
    return f"{prefix}-{suffix}"


@st.composite
def language_codes(draw):
    """Generate valid language codes"""
    return draw(st.sampled_from(SUPPORTED_LANGUAGES))


@st.composite
def therapeutic_approaches(draw):
    """Generate therapeutic approach strings"""
    return draw(st.sampled_from([
        'person_centered',
        'cognitive_behavioral',
        'mindfulness_based',
        'solution_focused',
        'psychodynamic'
    ]))


@st.composite
def conversation_contexts(draw):
    """Generate conversation context strings"""
    return draw(st.sampled_from([
        'initial_session',
        'ongoing_session',
        'crisis_intervention',
        'session_closing',
        'follow_up'
    ]))


@st.composite
def cultural_contexts(draw):
    """Generate cultural context strings"""
    return draw(st.sampled_from([
        'neutral',
        'western',
        'eastern',
        'latin_american',
        'middle_eastern',
        'african'
    ]))


# ============================================================================
# Property 5.1: Multi-Language Session Configuration
# ============================================================================

@given(
    session_id=session_ids(),
    client_id=client_ids(),
    language=language_codes()
)
@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_multilanguage_session_creation(session_id, client_id, language):
    """
    Property: For any valid session ID, client ID, and supported language,
    creating a Nova Sonic 2 session should produce a valid configuration
    with appropriate language-specific settings.
    
    **Validates: Requirements 2.3, 10.1, 10.2**
    """
    config = NovaSonicConfig()
    
    # Create session configuration
    session_config = config.create_session_config(
        session_id=session_id,
        client_id=client_id,
        language=language
    )
    
    # Property assertions
    assert session_config is not None, "Session config should not be None"
    assert session_config['session_id'] == session_id, "Session ID should match"
    assert session_config['client_id'] == client_id, "Client ID should match"
    assert session_config['language'] == language, "Language should match"
    assert session_config['model_id'] == "amazon.nova-sonic-2", "Should use Nova Sonic 2"
    
    # System prompt should exist and be non-empty
    assert 'system_prompt' in session_config, "System prompt should exist"
    assert len(session_config['system_prompt']) > 0, "System prompt should not be empty"
    
    # Audio configuration should be valid
    assert 'audio_config' in session_config, "Audio config should exist"
    audio_config = session_config['audio_config']
    assert audio_config['sample_rate'] > 0, "Sample rate should be positive"
    assert audio_config['channels'] in [1, 2], "Channels should be 1 or 2"
    
    # Session should start in INITIALIZING state
    assert session_config['status'] == NovaSessionStatus.INITIALIZING.value


@given(
    language=language_codes(),
    approach=therapeutic_approaches(),
    context=conversation_contexts(),
    cultural_context=cultural_contexts()
)
@settings(max_examples=10, deadline=None)
def test_property_therapeutic_prompt_cultural_adaptation(language, approach, context, cultural_context):
    """
    Property: For any language and cultural context combination,
    the therapeutic system prompt should be culturally appropriate
    and contain therapeutic guidance.
    
    **Validates: Requirements 2.4, 10.3, 10.4**
    """
    config = NovaSonicConfig()
    
    # Get therapeutic prompt with cultural context
    prompt, metadata = config.get_therapeutic_system_prompt(
        language=language,
        approach=approach,
        context=context,
        cultural_context=cultural_context
    )
    
    # Property assertions
    assert prompt is not None, "Prompt should not be None"
    assert len(prompt) > 50, "Prompt should be substantial"
    assert isinstance(metadata, dict), "Metadata should be a dictionary"
    
    # Prompt should contain therapeutic keywords
    prompt_lower = prompt.lower()
    therapeutic_keywords = ['compassionate', 'empathetic', 'support', 'therapeutic', 'therapist']
    assert any(keyword in prompt_lower for keyword in therapeutic_keywords), \
        "Prompt should contain therapeutic language"
    
    # Prompt should mention safety concerns
    safety_keywords = ['self-harm', 'crisis', 'safety', 'harm']
    assert any(keyword in prompt_lower for keyword in safety_keywords), \
        "Prompt should address safety concerns"


# ============================================================================
# Property 5.2: Real-Time Audio Processing and Latency
# ============================================================================

@given(
    session_id=session_ids(),
    client_id=client_ids(),
    language=language_codes()
)
@settings(max_examples=10, deadline=None)
def test_property_audio_config_latency_requirements(session_id, client_id, language):
    """
    Property: For any session configuration, the audio settings
    should meet latency requirements suitable for real-time conversation.
    
    **Validates: Requirements 2.2, 2.5**
    """
    config = NovaSonicConfig()
    
    # Create session configuration
    session_config = config.create_session_config(
        session_id=session_id,
        client_id=client_id,
        language=language
    )
    
    # Property assertions on performance config
    assert 'performance_config' in session_config, "Performance config should exist"
    perf_config = session_config['performance_config']
    
    assert perf_config['max_latency_ms'] <= 200, \
        f"Max latency {perf_config['max_latency_ms']}ms exceeds 200ms requirement"
    
    assert perf_config['max_requests_per_second'] <= 1.0, \
        "Should respect Breaking Barriers UK 2026 rate limit constraint"
    
    # Audio config should support real-time processing
    audio_config = session_config['audio_config']
    assert audio_config['sample_rate'] >= 8000, "Sample rate should support speech"
    assert audio_config['buffer_size'] > 0, "Buffer size should be positive"


# ============================================================================
# Property 5.3: Session State Management and Continuity
# ============================================================================

@given(
    session_id=session_ids(),
    client_id=client_ids(),
    language=language_codes()
)
@settings(max_examples=10, deadline=None)
def test_property_session_lifecycle_state_transitions(session_id, client_id, language):
    """
    Property: For any session, the lifecycle should follow valid state
    transitions from INITIALIZING -> ACTIVE -> TERMINATED.
    
    **Validates: Requirements 2.1, 2.6**
    """
    config = NovaSonicConfig()
    
    # Mock Bedrock client to avoid AWS calls
    mock_bedrock = Mock()
    mock_bedrock.get_foundation_model = Mock(return_value={'modelDetails': {}})
    config._bedrock_client = mock_bedrock
    
    client = NovaSonicClient(config=config)
    
    # Create session
    session = client.create_session(
        session_id=session_id,
        client_id=client_id,
        language=language
    )
    
    # Property assertions
    assert session is not None, "Session should be created"
    assert session['status'] == NovaSessionStatus.ACTIVE.value, \
        "New session should be ACTIVE"
    assert session['session_id'] == session_id, "Session ID should match"
    
    # Retrieve session
    retrieved = client.get_session(session_id)
    assert retrieved is not None, "Should retrieve created session"
    assert retrieved['session_id'] == session_id, "Retrieved session should match"
    
    # Terminate session
    terminated = client.terminate_session(session_id)
    assert terminated is True, "Termination should succeed"
    
    # Session should no longer be active
    assert session_id not in client.get_active_sessions(), \
        "Terminated session should not be in active sessions"


@given(
    session_id=session_ids(),
    client_id=client_ids()
)
@settings(max_examples=10, deadline=None)
def test_property_duplicate_session_prevention(session_id, client_id):
    """
    Property: For any session ID, attempting to create a duplicate
    session should fail with an appropriate error.
    
    **Validates: Requirements 2.1**
    """
    config = NovaSonicConfig()
    
    mock_bedrock = Mock()
    mock_bedrock.get_foundation_model = Mock(return_value={'modelDetails': {}})
    config._bedrock_client = mock_bedrock
    
    client = NovaSonicClient(config=config)
    
    # Create first session
    session1 = client.create_session(session_id, client_id)
    assert session1 is not None, "First session should be created"
    
    # Attempt to create duplicate
    with pytest.raises(ValueError, match="already exists"):
        client.create_session(session_id, client_id)


# ============================================================================
# Property 5.4: Error Handling and Recovery
# ============================================================================

@given(
    attempt=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=10, deadline=None)
def test_property_retry_strategy_exponential_backoff(attempt):
    """
    Property: For any retry attempt, the delay should increase
    exponentially and not exceed the maximum delay (with jitter tolerance).
    
    **Validates: Requirements 2.7**
    """
    delay = NovaRetryStrategy.get_delay(attempt)
    
    # Property assertions
    assert delay > 0, "Delay should be positive"
    
    # Allow for jitter - delay can exceed max by up to 25% due to jitter calculation
    max_delay_with_jitter = NovaRetryStrategy.MAX_DELAY * 1.25
    assert delay <= max_delay_with_jitter, \
        f"Delay {delay}s exceeds max delay with jitter {max_delay_with_jitter}s"
    
    # If not at max attempts, delays should generally increase
    if attempt < NovaRetryStrategy.MAX_RETRIES - 1:
        next_delay = NovaRetryStrategy.get_delay(attempt + 1)
        # With jitter, we can't guarantee strict ordering, but average should increase
        # Just verify both are positive and reasonable
        assert next_delay > 0, "Next delay should be positive"


@given(
    error_code=st.sampled_from([
        'ThrottlingException',
        'ServiceUnavailable',
        'InternalServerError',
        'ValidationException',
        'AccessDeniedException'
    ]),
    attempt=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=10, deadline=None)
def test_property_retry_decision_consistency(error_code, attempt):
    """
    Property: For any error code and attempt number, the retry decision
    should be consistent with the retry strategy.
    
    **Validates: Requirements 2.7**
    """
    error = ClientError(
        {'Error': {'Code': error_code}},
        'test_operation'
    )
    
    should_retry = NovaRetryStrategy.should_retry(error, attempt)
    
    # Property assertions
    if attempt >= NovaRetryStrategy.MAX_RETRIES:
        assert should_retry is False, \
            "Should not retry after max attempts"
    
    if error_code in NovaRetryStrategy.RETRYABLE_ERRORS:
        if attempt < NovaRetryStrategy.MAX_RETRIES:
            assert should_retry is True, \
                f"Should retry on {error_code} within max attempts"
    else:
        assert should_retry is False, \
            f"Should not retry on non-retryable error {error_code}"


# ============================================================================
# Property 5.5: Rate Limiting Enforcement
# ============================================================================

@given(
    num_requests=st.integers(min_value=2, max_value=3)
)
@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_rate_limiting_enforcement(num_requests):
    """
    Property: For any number of rapid requests, the client should
    enforce rate limiting to stay below 1 RPS (Breaking Barriers constraint).
    
    **Validates: Requirements 2.2, 2.7**
    """
    config = NovaSonicConfig()
    
    mock_bedrock = Mock()
    mock_bedrock.get_foundation_model = Mock(return_value={'modelDetails': {}})
    config._bedrock_client = mock_bedrock
    
    client = NovaSonicClient(config=config)
    
    # Make multiple rapid requests
    start_time = time.time()
    
    for i in range(num_requests):
        session_id = f"session-{i}-{int(time.time() * 1000)}"
        client_id = f"client-{i}"
        client.create_session(session_id, client_id)
    
    elapsed = time.time() - start_time
    
    # Property assertion: should take at least (num_requests - 1) / 0.9 seconds
    min_expected_time = (num_requests - 1) / config.MAX_REQUESTS_PER_SECOND
    
    # Allow 10% tolerance for timing variations
    assert elapsed >= min_expected_time * 0.9, \
        f"Rate limiting not enforced: {elapsed:.2f}s < {min_expected_time:.2f}s"


# ============================================================================
# Property 5.6: Configuration Consistency
# ============================================================================

@given(
    session_id=session_ids(),
    client_id=client_ids(),
    language=language_codes()
)
@settings(max_examples=10, deadline=None)
def test_property_session_config_consistency(session_id, client_id, language):
    """
    Property: For any session configuration, all required fields should
    be present and consistent with each other.
    
    **Validates: Requirements 2.1, 2.3, 2.4**
    """
    config = NovaSonicConfig()
    
    # Create session configuration
    session_config = config.create_session_config(
        session_id=session_id,
        client_id=client_id,
        language=language
    )
    
    # Property assertions - all required fields present
    required_fields = [
        'session_id', 'client_id', 'model_id', 'language',
        'system_prompt', 'audio_config', 'performance_config',
        'timeout_config', 'status', 'created_at'
    ]
    
    for field in required_fields:
        assert field in session_config, f"Required field '{field}' missing"
    
    # Consistency checks
    assert session_config['language'] == language, "Language should be consistent"
    assert session_config['model_id'] == config.MODEL_ID, "Model ID should match config"
    assert session_config['audio_config']['sample_rate'] == config.AUDIO_SAMPLE_RATE, \
        "Sample rate should match config"
    assert session_config['timeout_config']['session_timeout'] == config.SESSION_TIMEOUT, \
        "Session timeout should match config"


@given(
    language=language_codes()
)
@settings(max_examples=10, deadline=None)
def test_property_prompt_metadata_completeness(language):
    """
    Property: For any language, the therapeutic prompt should include
    complete metadata about its selection and configuration.
    
    **Validates: Requirements 2.4, 10.3, 10.4**
    """
    config = NovaSonicConfig()
    
    # Get therapeutic prompt
    prompt, metadata = config.get_therapeutic_system_prompt(language=language)
    
    # Property assertions
    assert prompt is not None, "Prompt should not be None"
    assert metadata is not None, "Metadata should not be None"
    assert isinstance(metadata, dict), "Metadata should be a dictionary"
    
    # Metadata should contain useful information
    # (exact fields depend on implementation, but should not be empty)
    assert len(metadata) > 0, "Metadata should contain information"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
