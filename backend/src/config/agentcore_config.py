"""
AWS AgentCore Configuration for AI Therapy Platform
Handles AgentCore client setup and configuration
🏆 Breaking Barriers UK 2026 compliant
"""

import os
from typing import Optional
from botocore.config import Config

# AgentCore Configuration
AGENTCORE_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')

# Memory configuration
MEMORY_TTL_DAYS = int(os.getenv('AGENTCORE_MEMORY_TTL_DAYS', '90'))  # 90 days default retention
MAX_MEMORY_SIZE_KB = int(os.getenv('AGENTCORE_MAX_MEMORY_SIZE_KB', '512'))  # 512KB max memory size
MEMORY_OPTIMIZATION_THRESHOLD = 0.8  # Trigger optimization at 80% capacity

# Conversation context configuration
MAX_CONVERSATION_HISTORY_ITEMS = int(os.getenv('MAX_CONVERSATION_HISTORY', '50'))
MAX_SESSION_SUMMARY_LENGTH = int(os.getenv('MAX_SESSION_SUMMARY_LENGTH', '1000'))

# AgentCore API configuration
AGENTCORE_RETRY_CONFIG = Config(
    region_name=AGENTCORE_REGION,
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    },
    connect_timeout=5,
    read_timeout=30
)

# Memory storage keys
MEMORY_KEY_PREFIX = "therapy_session"
CONVERSATION_CONTEXT_KEY = "conversation_context"
THERAPEUTIC_PROFILE_KEY = "therapeutic_profile"
SESSION_HISTORY_KEY = "session_history"

def get_memory_id(client_id: str) -> str:
    """
    Generate AgentCore memory ID for a client
    
    Args:
        client_id: Unique client identifier
        
    Returns:
        Formatted memory ID for AgentCore
    """
    return f"{MEMORY_KEY_PREFIX}_{client_id}"

def validate_memory_size(memory_data: dict) -> bool:
    """
    Validate that memory data is within size limits
    
    Args:
        memory_data: Memory data dictionary
        
    Returns:
        True if within limits, False otherwise
    """
    import json
    memory_json = json.dumps(memory_data)
    size_kb = len(memory_json.encode('utf-8')) / 1024
    return size_kb <= MAX_MEMORY_SIZE_KB
