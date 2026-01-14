#!/usr/bin/env python3
"""
Simple validation script for Nova Sonic 2 configuration
Tests basic functionality without requiring AWS credentials
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import directly to avoid __init__.py boto3 dependency
import importlib.util
spec = importlib.util.spec_from_file_location(
    "nova_sonic_config",
    os.path.join(os.path.dirname(__file__), '..', 'src', 'config', 'nova_sonic_config.py')
)
nova_module = importlib.util.module_from_spec(spec)

# Mock boto3 before loading
class MockBoto3:
    @staticmethod
    def client(*args, **kwargs):
        return None
    @staticmethod
    def resource(*args, **kwargs):
        return None

sys.modules['boto3'] = MockBoto3()
sys.modules['botocore.config'] = type('obj', (object,), {'Config': lambda **kwargs: None})()
sys.modules['botocore.exceptions'] = type('obj', (object,), {
    'ClientError': Exception,
    'BotoCoreError': Exception
})()

spec.loader.exec_module(nova_module)

NovaSonicConfig = nova_module.NovaSonicConfig
NovaSonicClient = nova_module.NovaSonicClient
NovaSessionStatus = nova_module.NovaSessionStatus
NovaRetryStrategy = nova_module.NovaRetryStrategy


def test_retry_strategy():
    """Test retry strategy logic"""
    print("Testing NovaRetryStrategy...")
    
    # Test delay calculation
    delay_0 = NovaRetryStrategy.get_delay(0)
    delay_1 = NovaRetryStrategy.get_delay(1)
    delay_2 = NovaRetryStrategy.get_delay(2)
    
    assert delay_0 < delay_1 < delay_2, "Delays should increase exponentially"
    assert delay_2 <= NovaRetryStrategy.MAX_DELAY, "Should not exceed max delay"
    
    print("✓ Retry strategy tests passed")


def test_config_initialization():
    """Test config initialization"""
    print("\nTesting NovaSonicConfig initialization...")
    
    config = NovaSonicConfig()
    
    assert config.MODEL_ID == "amazon.nova-sonic-2"
    assert config.AUDIO_SAMPLE_RATE == 16000
    assert config.AUDIO_CHANNELS == 1
    assert config.MAX_LATENCY_MS == 200
    assert config.MAX_REQUESTS_PER_SECOND == 0.9
    
    print("✓ Config initialization tests passed")


def test_therapeutic_prompts():
    """Test therapeutic prompt generation"""
    print("\nTesting therapeutic prompts...")
    
    config = NovaSonicConfig()
    
    # Test English prompt
    prompt_en = config.get_therapeutic_system_prompt("en")
    assert "compassionate" in prompt_en.lower()
    assert "therapist" in prompt_en.lower()
    assert "self-harm" in prompt_en.lower()
    
    # Test Spanish prompt
    prompt_es = config.get_therapeutic_system_prompt("es")
    assert "Spanish" in prompt_es
    assert "compassionate" in prompt_es.lower()
    
    # Test French prompt
    prompt_fr = config.get_therapeutic_system_prompt("fr")
    assert "French" in prompt_fr
    
    print("✓ Therapeutic prompt tests passed")


def test_session_config():
    """Test session configuration creation"""
    print("\nTesting session configuration...")
    
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
    
    # Test custom prompt
    custom_prompt = "Custom therapeutic prompt"
    session_config_custom = config.create_session_config(
        session_id="test-session",
        client_id="client-123",
        custom_prompt=custom_prompt
    )
    assert session_config_custom["system_prompt"] == custom_prompt
    
    print("✓ Session configuration tests passed")


def test_client_basic_operations():
    """Test basic client operations (without AWS calls)"""
    print("\nTesting NovaSonicClient basic operations...")
    
    # Note: We can't test actual AWS operations without credentials
    # but we can test the client structure
    
    config = NovaSonicConfig()
    client = NovaSonicClient(config=config)
    
    assert client.config == config
    assert len(client._active_sessions) == 0
    
    # Test getting non-existent session
    session = client.get_session("non-existent")
    assert session is None
    
    # Test getting active sessions (empty)
    active = client.get_active_sessions()
    assert len(active) == 0
    
    print("✓ Client basic operation tests passed")


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("Nova Sonic 2 Configuration Validation")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("=" * 60)
    
    try:
        test_retry_strategy()
        test_config_initialization()
        test_therapeutic_prompts()
        test_session_config()
        test_client_basic_operations()
        
        print("\n" + "=" * 60)
        print("✅ All validation tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
