"""
Strands Agent SDK Configuration for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Handles Strands Agent SDK setup, configuration, and integration with Nova Sonic 2
for therapeutic AI conversation capabilities.

Requirements: 3.2
"""

import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Strands Agent lifecycle states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    ERROR = "error"


class AgentCapability(Enum):
    """Agent capabilities for therapeutic conversations"""
    SPEECH_TO_SPEECH = "speech_to_speech"
    CONVERSATION_MANAGEMENT = "conversation_management"
    MEMORY_INTEGRATION = "memory_integration"
    SAFETY_GUARDRAILS = "safety_guardrails"
    RED_FLAG_DETECTION = "red_flag_detection"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    MULTI_LANGUAGE = "multi_language"
    THERAPEUTIC_GUIDANCE = "therapeutic_guidance"


@dataclass
class AgentTool:
    """Configuration for an agent tool"""
    name: str
    description: str
    capability: AgentCapability
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "capability": self.capability.value,
            "enabled": self.enabled,
            "parameters": self.parameters
        }


@dataclass
class AgentConfiguration:
    """Complete agent configuration"""
    agent_id: str
    session_id: str
    client_id: str
    language: str = "en"
    capabilities: List[AgentCapability] = field(default_factory=list)
    tools: List[AgentTool] = field(default_factory=list)
    nova_sonic_config: Optional[Dict[str, Any]] = None
    agentcore_memory_id: Optional[str] = None
    therapeutic_context: Optional[Dict[str, Any]] = None
    state: AgentState = AgentState.UNINITIALIZED
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "client_id": self.client_id,
            "language": self.language,
            "capabilities": [cap.value for cap in self.capabilities],
            "tools": [tool.to_dict() for tool in self.tools],
            "nova_sonic_config": self.nova_sonic_config,
            "agentcore_memory_id": self.agentcore_memory_id,
            "therapeutic_context": self.therapeutic_context,
            "state": self.state.value,
            "metadata": self.metadata
        }


class StrandsAgentConfig:
    """
    Configuration manager for Strands Agent SDK
    
    Handles agent initialization, tool registration, and capability management
    for therapeutic AI conversations.
    """
    
    # Agent Configuration
    AGENT_VERSION = "1.0.0"
    AGENT_TYPE = "therapeutic_assistant"
    
    # Default capabilities for therapeutic agents
    DEFAULT_CAPABILITIES = [
        AgentCapability.SPEECH_TO_SPEECH,
        AgentCapability.CONVERSATION_MANAGEMENT,
        AgentCapability.MEMORY_INTEGRATION,
        AgentCapability.SAFETY_GUARDRAILS,
        AgentCapability.THERAPEUTIC_GUIDANCE
    ]
    
    # Tool definitions
    DEFAULT_TOOLS = [
        AgentTool(
            name="nova_sonic_speech",
            description="Real-time speech-to-speech processing with Nova Sonic 2",
            capability=AgentCapability.SPEECH_TO_SPEECH,
            parameters={
                "model_id": "amazon.nova-sonic-2",
                "streaming": True,
                "low_latency": True
            }
        ),
        AgentTool(
            name="conversation_manager",
            description="Manage conversation flow and turn-taking",
            capability=AgentCapability.CONVERSATION_MANAGEMENT,
            parameters={
                "turn_detection": True,
                "interruption_handling": True
            }
        ),
        AgentTool(
            name="memory_loader",
            description="Load and save conversation context from AgentCore",
            capability=AgentCapability.MEMORY_INTEGRATION,
            parameters={
                "auto_save": True,
                "save_interval": 60  # seconds
            }
        ),
        AgentTool(
            name="safety_filter",
            description="Apply therapeutic guardrails and content filtering",
            capability=AgentCapability.SAFETY_GUARDRAILS,
            parameters={
                "strict_mode": True,
                "therapeutic_boundaries": True
            }
        ),
        AgentTool(
            name="red_flag_detector",
            description="Detect concerning content requiring therapist notification",
            capability=AgentCapability.RED_FLAG_DETECTION,
            parameters={
                "real_time": True,
                "severity_classification": True
            }
        ),
        AgentTool(
            name="sentiment_analyzer",
            description="Analyze emotional state and conversation sentiment",
            capability=AgentCapability.SENTIMENT_ANALYSIS,
            parameters={
                "continuous_monitoring": True,
                "mood_tracking": True
            }
        ),
        AgentTool(
            name="language_detector",
            description="Detect and adapt to client's language",
            capability=AgentCapability.MULTI_LANGUAGE,
            parameters={
                "auto_detect": True,
                "supported_languages": ["en", "es", "fr", "de"]
            }
        ),
        AgentTool(
            name="therapeutic_guide",
            description="Provide evidence-based therapeutic guidance",
            capability=AgentCapability.THERAPEUTIC_GUIDANCE,
            parameters={
                "approaches": ["person_centered", "cbt", "dbt"],
                "cultural_sensitivity": True
            }
        )
    ]
    
    # Performance Configuration
    MAX_CONCURRENT_AGENTS = int(os.getenv('MAX_CONCURRENT_AGENTS', '100'))
    AGENT_TIMEOUT_SECONDS = int(os.getenv('AGENT_TIMEOUT_SECONDS', '3600'))  # 1 hour
    IDLE_TIMEOUT_SECONDS = int(os.getenv('AGENT_IDLE_TIMEOUT', '300'))  # 5 minutes
    
    # Integration Configuration
    NOVA_SONIC_INTEGRATION = True
    AGENTCORE_INTEGRATION = True
    
    def __init__(self):
        """Initialize Strands Agent configuration"""
        self._validate_environment()
        logger.info("Strands Agent SDK configuration initialized")
    
    def _validate_environment(self):
        """Validate environment configuration"""
        if self.MAX_CONCURRENT_AGENTS < 1:
            raise ValueError("MAX_CONCURRENT_AGENTS must be at least 1")
        
        if self.AGENT_TIMEOUT_SECONDS < 60:
            raise ValueError("AGENT_TIMEOUT_SECONDS must be at least 60")
        
        logger.info(
            f"Agent configuration validated: "
            f"max_concurrent={self.MAX_CONCURRENT_AGENTS}, "
            f"timeout={self.AGENT_TIMEOUT_SECONDS}s"
        )
    
    def create_agent_configuration(
        self,
        session_id: str,
        client_id: str,
        language: str = "en",
        capabilities: Optional[List[AgentCapability]] = None,
        custom_tools: Optional[List[AgentTool]] = None,
        nova_sonic_config: Optional[Dict[str, Any]] = None,
        agentcore_memory_id: Optional[str] = None,
        therapeutic_context: Optional[Dict[str, Any]] = None
    ) -> AgentConfiguration:
        """
        Create agent configuration for a therapy session
        
        Args:
            session_id: Unique session identifier
            client_id: Client user ID
            language: Preferred language code
            capabilities: Optional list of capabilities (uses defaults if None)
            custom_tools: Optional custom tools to add
            nova_sonic_config: Optional Nova Sonic 2 configuration
            agentcore_memory_id: Optional AgentCore memory ID
            therapeutic_context: Optional therapeutic context data
            
        Returns:
            AgentConfiguration object
        """
        agent_id = f"agent_{session_id}"
        
        # Use default capabilities if none provided
        if capabilities is None:
            capabilities = self.DEFAULT_CAPABILITIES.copy()
        
        # Start with default tools
        tools = [tool for tool in self.DEFAULT_TOOLS if tool.capability in capabilities]
        
        # Add custom tools if provided
        if custom_tools:
            tools.extend(custom_tools)
        
        # Create configuration
        config = AgentConfiguration(
            agent_id=agent_id,
            session_id=session_id,
            client_id=client_id,
            language=language,
            capabilities=capabilities,
            tools=tools,
            nova_sonic_config=nova_sonic_config,
            agentcore_memory_id=agentcore_memory_id,
            therapeutic_context=therapeutic_context,
            state=AgentState.UNINITIALIZED,
            metadata={
                "agent_version": self.AGENT_VERSION,
                "agent_type": self.AGENT_TYPE,
                "created_at": None,  # Will be set on initialization
                "timeout_seconds": self.AGENT_TIMEOUT_SECONDS,
                "idle_timeout_seconds": self.IDLE_TIMEOUT_SECONDS
            }
        )
        
        logger.info(
            f"Created agent configuration for session {session_id}, "
            f"client {client_id}, language {language}"
        )
        
        return config
    
    def get_tool_by_name(self, tool_name: str) -> Optional[AgentTool]:
        """
        Get tool definition by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            AgentTool or None if not found
        """
        for tool in self.DEFAULT_TOOLS:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_tools_by_capability(
        self,
        capability: AgentCapability
    ) -> List[AgentTool]:
        """
        Get all tools for a specific capability
        
        Args:
            capability: AgentCapability to filter by
            
        Returns:
            List of AgentTool objects
        """
        return [
            tool for tool in self.DEFAULT_TOOLS
            if tool.capability == capability
        ]
    
    def validate_configuration(
        self,
        config: AgentConfiguration
    ) -> tuple[bool, Optional[str]]:
        """
        Validate agent configuration
        
        Args:
            config: AgentConfiguration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if not config.agent_id:
            return False, "agent_id is required"
        
        if not config.session_id:
            return False, "session_id is required"
        
        if not config.client_id:
            return False, "client_id is required"
        
        # Check capabilities
        if not config.capabilities:
            return False, "At least one capability is required"
        
        # Check tools
        if not config.tools:
            return False, "At least one tool is required"
        
        # Validate tool-capability alignment
        tool_capabilities = {tool.capability for tool in config.tools}
        for capability in config.capabilities:
            if capability not in tool_capabilities:
                return False, f"No tool found for capability {capability.value}"
        
        # Check Nova Sonic integration
        if AgentCapability.SPEECH_TO_SPEECH in config.capabilities:
            if not config.nova_sonic_config:
                return False, "Nova Sonic config required for speech capability"
        
        # Check AgentCore integration
        if AgentCapability.MEMORY_INTEGRATION in config.capabilities:
            if not config.agentcore_memory_id:
                return False, "AgentCore memory ID required for memory capability"
        
        return True, None


# Global configuration instance
strands_agent_config = StrandsAgentConfig()
