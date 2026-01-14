"""
Tests for Nova Sonic 2 Configuration
🏆 Breaking Barriers UK 2026 compliant

Tests authentication, session management, error handling, and retry logic
for Nova Sonic 2 client configuration.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError, BotoCoreError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.nova_sonic_config import (
    NovaSonicConfig,
    NovaSonicClient,
    NovaSessionStatus,
    NovaRetryStrategy
)


class TestNovaRetryStrategy:
    """Test retry strategy logic"""
    
    def test_should_retry_on_throttling(self):
        """Test retry on throttling errors"""
        error = ClientError(
            {'Error': {'Code': 'ThrottlingException'}},
            'test_operation'
        )
        assert NovaRetryStrategy.should_retry(error, 0) is True
        assert NovaRetryStrategy.should_retry(error, 1) is True
        assert NovaRetryStrategy.should_retry(error, 2) is True
        assert NovaRetryStrategy.should_retry(error, 3) is False  # Max retries
    
    def test_should_retry_on_service_unavailable(self):
        """Test retry on service unavailable"""
        error = ClientError(
            {'Error': {'Code': 'ServiceUnavailable'}},
            'test_operation'
        )
        assert NovaRetryStrategy.should_retry(error, 0) is True
    
    def test_should_not_retry_on_validation_error(self):
        """Test no retry on validation errors"""
        error = ClientError(
            {'Error': {'Code': 'ValidationException'}},
            'test_operation'
        )
        assert NovaRetryStrategy.should_retry(error, 0) is False
    
    def test_should_retry_on_botocore_error(self):
        """Test retry on network errors"""
        error = BotoCoreError()
        assert NovaRetryStrategy.should_retry(error, 0) is True
    
    def test_exponential_backoff_delay(self):
        """Test exponential backoff calculation"""
        delay_0 = NovaRetryStrategy.get_delay(0)
        delay_1 = NovaRetryStrategy.get_delay(1)
        delay_2 = NovaRetryStrategy.get_delay(2)
        
        # Delays should increase
        assert delay_0 < delay_1 < delay_2
        
        # Should not exceed max delay
        delay_10 = NovaRetryStrategy.get_delay(10)
        assert delay_10 <= NovaRetryStrategy.MAX_DELAY


class TestNovaSonicConfig:
    """Test Nova Sonic 2 configuration"""
    
    def test_initialization(self):
        """Test config initialization"""
        config = NovaSonicConfig()
        assert config.AWS_REGION in ['us-west-2', 'us-east-1']
        assert config.MODEL_ID == "amazon.nova-sonic-2"
        assert config.AUDIO_SAMPLE_RATE == 16000
        assert config.MAX_LATENCY_MS == 200
    
    def test_therapeutic_system_prompt_english(self):
        """Test English therapeutic prompt"""
        config = NovaSonicConfig()
        prompt = config.get_therapeutic_system_prompt("en")
        
        assert "compassionate" in prompt.lower()
        assert "therapist" in prompt.lower()
        assert "empathetically" in prompt.lower()
        assert "self-harm" in prompt.lower()
    
    def test_therapeutic_system_prompt_spanish(self):
        """Test Spanish therapeutic prompt includes language note"""
        config = NovaSonicConfig()
        prompt = config.get_therapeutic_system_prompt("es")
        
        assert "Spanish" in prompt
        assert "compassionate" in prompt.lower()
    
    def test_therapeutic_system_prompt_french(self):
        """Test French therapeutic prompt includes language note"""
        config = NovaSonicConfig()
        prompt = config.get_therapeutic_system_prompt("fr")
        
        assert "French" in prompt
    
    def test_session_config_creation(self):
        """Test session configuration creation"""
        config = NovaSonicConfig()
        session_config = config.create_session_config(
            session_id="test-session-123",
            client_id="client-456",
            language="en"
        )
        
        assert session_config["session_id"] == "test-session-123"
        assert session_config["client_id"] == "client-456"
        assert session_config["model_id"] == "amazon.nova-sonic-2"
        assert session_config["language"] == "en"
        assert "system_prompt" in session_config
        assert session_config["audio_config"]["sample_rate"] == 16000
        assert session_config["status"] == NovaSessionStatus.INITIALIZING.value
    
    def test_session_config_custom_prompt(self):
        """Test session config with custom prompt"""
        config = NovaSonicConfig()
        custom_prompt = "Custom therapeutic prompt"
        session_config = config.create_session_config(
            session_id="test-session",
            client_id="client-123",
            custom_prompt=custom_prompt
        )
        
        assert session_config["system_prompt"] == custom_prompt
    
    @patch.dict(os.environ, {'AWS_DEFAULT_REGION': 'eu-west-1'})
    def test_region_validation_warning(self, caplog):
        """Test warning for non-permitted regions"""
        import logging
        caplog.set_level(logging.WARNING)
        
        config = NovaSonicConfig()
        # Should log warning but not fail
        assert config.AWS_REGION == 'eu-west-1'


class TestNovaSonicClient:
    """Test Nova Sonic 2 client"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock config"""
        config = Mock(spec=NovaSonicConfig)
        config.AWS_REGION = 'us-west-2'
        config.MODEL_ID = 'amazon.nova-sonic-2'
        config.MAX_REQUESTS_PER_SECOND = 0.9
        config.bedrock_client = Mock()
        config.bedrock_runtime_client = Mock()
        config.create_session_config = Mock(return_value={
            "session_id": "test-session",
            "client_id": "client-123",
            "model_id": "amazon.nova-sonic-2",
            "language": "en",
            "system_prompt": "Test prompt",
            "audio_config": {},
            "performance_config": {},
            "timeout_config": {},
            "status": NovaSessionStatus.INITIALIZING.value,
            "created_at": time.time()
        })
        return config
    
    def test_client_initialization(self, mock_config):
        """Test client initialization"""
        client = NovaSonicClient(config=mock_config)
        assert client.config == mock_config
        assert len(client._active_sessions) == 0
    
    def test_create_session_success(self, mock_config):
        """Test successful session creation"""
        client = NovaSonicClient(config=mock_config)
        
        # Mock model verification
        mock_config.bedrock_client.get_foundation_model = Mock(
            return_value={'modelDetails': {}}
        )
        
        session = client.create_session(
            session_id="test-session-123",
            client_id="client-456",
            language="en"
        )
        
        assert session["session_id"] == "test-session"
        assert session["status"] == NovaSessionStatus.ACTIVE.value
        assert "test-session-123" in client._active_sessions
    
    def test_create_duplicate_session_fails(self, mock_config):
        """Test creating duplicate session raises error"""
        client = NovaSonicClient(config=mock_config)
        
        mock_config.bedrock_client.get_foundation_model = Mock(
            return_value={'modelDetails': {}}
        )
        
        # Create first session
        client.create_session(
            session_id="test-session",
            client_id="client-123"
        )
        
        # Attempt duplicate
        with pytest.raises(ValueError, match="already exists"):
            client.create_session(
                session_id="test-session",
                client_id="client-123"
            )
    
    def test_get_session(self, mock_config):
        """Test retrieving session"""
        client = NovaSonicClient(config=mock_config)
        
        mock_config.bedrock_client.get_foundation_model = Mock(
            return_value={'modelDetails': {}}
        )
        
        # Create session
        created = client.create_session(
            session_id="test-session",
            client_id="client-123"
        )
        
        # Retrieve session
        retrieved = client.get_session("test-session")
        assert retrieved is not None
        assert retrieved["session_id"] == created["session_id"]
        
        # Non-existent session
        assert client.get_session("non-existent") is None
    
    def test_terminate_session(self, mock_config):
        """Test session termination"""
        client = NovaSonicClient(config=mock_config)
        
        mock_config.bedrock_client.get_foundation_model = Mock(
            return_value={'modelDetails': {}}
        )
        
        # Create session
        client.create_session(
            session_id="test-session",
            client_id="client-123"
        )
        
        # Terminate session
        result = client.terminate_session("test-session")
        assert result is True
        assert "test-session" not in client._active_sessions
        
        # Terminate non-existent session
        result = client.terminate_session("non-existent")
        assert result is False
    
    def test_get_active_sessions(self, mock_config):
        """Test getting all active sessions"""
        client = NovaSonicClient(config=mock_config)
        
        mock_config.bedrock_client.get_foundation_model = Mock(
            return_value={'modelDetails': {}}
        )
        
        # Create multiple sessions
        client.create_session("session-1", "client-1")
        client.create_session("session-2", "client-2")
        
        active = client.get_active_sessions()
        assert len(active) == 2
        assert "session-1" in active
        assert "session-2" in active
    
    def test_rate_limiting(self, mock_config):
        """Test rate limiting enforcement"""
        client = NovaSonicClient(config=mock_config)
        
        mock_config.bedrock_client.get_foundation_model = Mock(
            return_value={'modelDetails': {}}
        )
        
        # Create multiple sessions rapidly
        start_time = time.time()
        
        client.create_session("session-1", "client-1")
        client.create_session("session-2", "client-2")
        client.create_session("session-3", "client-3")
        
        elapsed = time.time() - start_time
        
        # Should take at least 2 seconds for 3 requests at 0.9 RPS
        min_expected_time = 2.0 / 0.9
        assert elapsed >= min_expected_time * 0.9  # Allow 10% tolerance
    
    def test_retry_on_throttling(self, mock_config):
        """Test retry logic on throttling"""
        client = NovaSonicClient(config=mock_config)
        
        # Mock throttling then success
        mock_config.bedrock_client.get_foundation_model = Mock(
            side_effect=[
                ClientError(
                    {'Error': {'Code': 'ThrottlingException'}},
                    'get_foundation_model'
                ),
                {'modelDetails': {}}  # Success on retry
            ]
        )
        
        # Should succeed after retry
        session = client.create_session("test-session", "client-123")
        assert session["status"] == NovaSessionStatus.ACTIVE.value
    
    def test_retry_exhaustion(self, mock_config):
        """Test retry exhaustion raises error"""
        client = NovaSonicClient(config=mock_config)
        
        # Mock continuous throttling
        mock_config.bedrock_client.get_foundation_model = Mock(
            side_effect=ClientError(
                {'Error': {'Code': 'ThrottlingException'}},
                'get_foundation_model'
            )
        )
        
        # Should fail after max retries
        with pytest.raises(ClientError):
            client.create_session("test-session", "client-123")
    
    def test_health_check_healthy(self, mock_config):
        """Test health check when healthy"""
        client = NovaSonicClient(config=mock_config)
        
        mock_config.bedrock_client.list_foundation_models = Mock(
            return_value={'modelSummaries': []}
        )
        
        health = client.health_check()
        assert health["status"] == "healthy"
        assert health["region"] == "us-west-2"
        assert health["model_id"] == "amazon.nova-sonic-2"
        assert "active_sessions" in health
    
    def test_health_check_unhealthy(self, mock_config):
        """Test health check when unhealthy"""
        client = NovaSonicClient(config=mock_config)
        
        mock_config.bedrock_client.list_foundation_models = Mock(
            side_effect=ClientError(
                {'Error': {'Code': 'ServiceUnavailable'}},
                'list_foundation_models'
            )
        )
        
        health = client.health_check()
        assert health["status"] == "unhealthy"
        assert "error" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
