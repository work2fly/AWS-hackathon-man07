"""
Strands Agent Service for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Handles agent initialization, lifecycle management, tool integration,
and state management for therapeutic AI conversations.

Requirements: 3.2
"""

import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from ..config.strands_agent_config import (
    StrandsAgentConfig,
    AgentConfiguration,
    AgentState,
    AgentCapability,
    AgentTool,
    strands_agent_config
)
from ..config.nova_sonic_config import nova_sonic_client
from ..config.agentcore_config import get_memory_id
from ..services.agentcore_memory_service import AgentCoreMemoryService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AgentLifecycleError(Exception):
    """Exception raised for agent lifecycle errors"""
    pass


class StrandsAgent:
    """
    Strands Agent instance for therapeutic conversations
    
    Manages agent state, tools, and integration with Nova Sonic 2
    and AgentCore memory.
    """
    
    def __init__(self, config: AgentConfiguration):
        """
        Initialize Strands Agent
        
        Args:
            config: AgentConfiguration object
        """
        self.config = config
        self.state = AgentState.UNINITIALIZED
        self.created_at = datetime.utcnow()
        self.last_activity = self.created_at
        self.error_message: Optional[str] = None
        
        # Tool instances
        self._tools: Dict[str, Any] = {}
        
        # Integration clients
        self._nova_sonic_session: Optional[Dict[str, Any]] = None
        self._agentcore_memory: Optional[Any] = None
        
        logger.info(f"Created Strands Agent {config.agent_id} for session {config.session_id}")
    
    def initialize(self) -> bool:
        """
        Initialize the agent and all its tools
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.state = AgentState.INITIALIZING
            self.config.state = AgentState.INITIALIZING
            
            logger.info(f"Initializing agent {self.config.agent_id}")
            
            # Initialize Nova Sonic 2 if speech capability enabled
            if AgentCapability.SPEECH_TO_SPEECH in self.config.capabilities:
                self._initialize_nova_sonic()
            
            # Load AgentCore memory if memory capability enabled
            if AgentCapability.MEMORY_INTEGRATION in self.config.capabilities:
                self._initialize_agentcore_memory()
            
            # Initialize all tools
            for tool in self.config.tools:
                if tool.enabled:
                    self._initialize_tool(tool)
            
            # Mark as ready
            self.state = AgentState.READY
            self.config.state = AgentState.READY
            self.config.metadata["initialized_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Agent {self.config.agent_id} initialized successfully")
            return True
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.config.state = AgentState.ERROR
            self.error_message = str(e)
            logger.error(f"Failed to initialize agent {self.config.agent_id}: {e}")
            return False
    
    def _initialize_nova_sonic(self):
        """Initialize Nova Sonic 2 integration"""
        try:
            # Create Nova Sonic session
            self._nova_sonic_session = nova_sonic_client.create_session(
                session_id=self.config.session_id,
                client_id=self.config.client_id,
                language=self.config.language,
                custom_prompt=self.config.therapeutic_context.get("system_prompt") if self.config.therapeutic_context else None
            )
            
            logger.info(f"Nova Sonic session created for agent {self.config.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Nova Sonic for agent {self.config.agent_id}: {e}")
            raise
    
    def _initialize_agentcore_memory(self):
        """Initialize AgentCore memory integration"""
        try:
            memory_service = AgentCoreMemoryService()
            
            # Load existing memory or create new
            memory = memory_service.get_memory(self.config.client_id)
            if not memory:
                memory = memory_service.create_memory(
                    client_id=self.config.client_id,
                    language_preference=self.config.language
                )
            
            self._agentcore_memory = memory
            self.config.agentcore_memory_id = memory.memory_id
            
            # Load conversation context into therapeutic context
            if not self.config.therapeutic_context:
                self.config.therapeutic_context = {}
            
            self.config.therapeutic_context["conversation_history"] = (
                memory_service.serialize_context_for_prompt(self.config.client_id)
            )
            
            logger.info(f"AgentCore memory loaded for agent {self.config.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AgentCore memory for agent {self.config.agent_id}: {e}")
            raise
    
    def _initialize_tool(self, tool: AgentTool):
        """
        Initialize a specific tool
        
        Args:
            tool: AgentTool to initialize
        """
        try:
            # Store tool configuration
            self._tools[tool.name] = {
                "config": tool,
                "initialized": True,
                "last_used": None,
                "usage_count": 0
            }
            
            logger.debug(f"Initialized tool {tool.name} for agent {self.config.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize tool {tool.name}: {e}")
            raise
    
    def start(self) -> bool:
        """
        Start the agent (transition to ACTIVE state)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.state != AgentState.READY:
                raise AgentLifecycleError(
                    f"Cannot start agent in state {self.state.value}. "
                    "Agent must be in READY state."
                )
            
            self.state = AgentState.ACTIVE
            self.config.state = AgentState.ACTIVE
            self.config.metadata["started_at"] = datetime.utcnow().isoformat()
            self.last_activity = datetime.utcnow()
            
            logger.info(f"Agent {self.config.agent_id} started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {self.config.agent_id}: {e}")
            return False
    
    def pause(self) -> bool:
        """
        Pause the agent
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.state != AgentState.ACTIVE:
                raise AgentLifecycleError(
                    f"Cannot pause agent in state {self.state.value}"
                )
            
            self.state = AgentState.PAUSED
            self.config.state = AgentState.PAUSED
            self.config.metadata["paused_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Agent {self.config.agent_id} paused")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause agent {self.config.agent_id}: {e}")
            return False
    
    def resume(self) -> bool:
        """
        Resume the agent from paused state
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.state != AgentState.PAUSED:
                raise AgentLifecycleError(
                    f"Cannot resume agent in state {self.state.value}"
                )
            
            self.state = AgentState.ACTIVE
            self.config.state = AgentState.ACTIVE
            self.config.metadata["resumed_at"] = datetime.utcnow().isoformat()
            self.last_activity = datetime.utcnow()
            
            logger.info(f"Agent {self.config.agent_id} resumed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume agent {self.config.agent_id}: {e}")
            return False
    
    def terminate(self, save_memory: bool = True) -> bool:
        """
        Terminate the agent and cleanup resources
        
        Args:
            save_memory: Whether to save memory before terminating
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.state = AgentState.TERMINATING
            self.config.state = AgentState.TERMINATING
            
            logger.info(f"Terminating agent {self.config.agent_id}")
            
            # Save AgentCore memory if requested
            if save_memory and self._agentcore_memory:
                try:
                    memory_service = AgentCoreMemoryService()
                    memory_service.update_memory(self._agentcore_memory)
                    logger.info(f"Saved memory for agent {self.config.agent_id}")
                except Exception as e:
                    logger.error(f"Failed to save memory: {e}")
            
            # Terminate Nova Sonic session
            if self._nova_sonic_session:
                try:
                    nova_sonic_client.terminate_session(self.config.session_id)
                    logger.info(f"Terminated Nova Sonic session for agent {self.config.agent_id}")
                except Exception as e:
                    logger.error(f"Failed to terminate Nova Sonic session: {e}")
            
            # Cleanup tools
            self._tools.clear()
            
            # Mark as terminated
            self.state = AgentState.TERMINATED
            self.config.state = AgentState.TERMINATED
            self.config.metadata["terminated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Agent {self.config.agent_id} terminated successfully")
            return True
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.config.state = AgentState.ERROR
            self.error_message = str(e)
            logger.error(f"Failed to terminate agent {self.config.agent_id}: {e}")
            return False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def is_idle(self, idle_timeout_seconds: Optional[int] = None) -> bool:
        """
        Check if agent is idle
        
        Args:
            idle_timeout_seconds: Optional custom timeout (uses config default if None)
            
        Returns:
            True if idle, False otherwise
        """
        if idle_timeout_seconds is None:
            idle_timeout_seconds = self.config.metadata.get(
                "idle_timeout_seconds",
                300  # 5 minutes default
            )
        
        idle_duration = (datetime.utcnow() - self.last_activity).total_seconds()
        return idle_duration > idle_timeout_seconds
    
    def is_expired(self) -> bool:
        """
        Check if agent has exceeded maximum lifetime
        
        Returns:
            True if expired, False otherwise
        """
        timeout_seconds = self.config.metadata.get("timeout_seconds", 3600)
        lifetime = (datetime.utcnow() - self.created_at).total_seconds()
        return lifetime > timeout_seconds
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool dictionary or None if not found
        """
        return self._tools.get(tool_name)
    
    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use a tool
        
        Args:
            tool_name: Name of the tool to use
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        if not tool["initialized"]:
            raise ValueError(f"Tool {tool_name} not initialized")
        
        # Update tool usage
        tool["last_used"] = datetime.utcnow()
        tool["usage_count"] += 1
        
        # Update agent activity
        self.update_activity()
        
        logger.debug(f"Agent {self.config.agent_id} using tool {tool_name}")
        
        # Tool execution would happen here
        # For now, return success indicator
        return {"success": True, "tool": tool_name}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status
        
        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.config.agent_id,
            "session_id": self.config.session_id,
            "client_id": self.config.client_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "is_idle": self.is_idle(),
            "is_expired": self.is_expired(),
            "error_message": self.error_message,
            "capabilities": [cap.value for cap in self.config.capabilities],
            "tools": {
                name: {
                    "initialized": tool["initialized"],
                    "usage_count": tool["usage_count"],
                    "last_used": tool["last_used"].isoformat() if tool["last_used"] else None
                }
                for name, tool in self._tools.items()
            }
        }


class StrandsAgentService:
    """
    Service for managing Strands Agent instances
    
    Handles agent creation, lifecycle management, and cleanup.
    """
    
    def __init__(self, config: Optional[StrandsAgentConfig] = None):
        """
        Initialize Strands Agent Service
        
        Args:
            config: Optional StrandsAgentConfig instance
        """
        self.config = config or strands_agent_config
        self._agents: Dict[str, StrandsAgent] = {}
        logger.info("Strands Agent Service initialized")
    
    def create_agent(
        self,
        session_id: str,
        client_id: str,
        language: str = "en",
        capabilities: Optional[List[AgentCapability]] = None,
        custom_tools: Optional[List[AgentTool]] = None,
        nova_sonic_config: Optional[Dict[str, Any]] = None,
        therapeutic_context: Optional[Dict[str, Any]] = None
    ) -> StrandsAgent:
        """
        Create and initialize a new agent
        
        Args:
            session_id: Unique session identifier
            client_id: Client user ID
            language: Preferred language code
            capabilities: Optional list of capabilities
            custom_tools: Optional custom tools
            nova_sonic_config: Optional Nova Sonic configuration
            therapeutic_context: Optional therapeutic context
            
        Returns:
            Initialized StrandsAgent instance
        """
        try:
            # Check concurrent agent limit
            if len(self._agents) >= self.config.MAX_CONCURRENT_AGENTS:
                raise AgentLifecycleError(
                    f"Maximum concurrent agents ({self.config.MAX_CONCURRENT_AGENTS}) reached"
                )
            
            # Get AgentCore memory ID
            agentcore_memory_id = get_memory_id(client_id)
            
            # Create agent configuration
            agent_config = self.config.create_agent_configuration(
                session_id=session_id,
                client_id=client_id,
                language=language,
                capabilities=capabilities,
                custom_tools=custom_tools,
                nova_sonic_config=nova_sonic_config,
                agentcore_memory_id=agentcore_memory_id,
                therapeutic_context=therapeutic_context
            )
            
            # Validate configuration
            is_valid, error_msg = self.config.validate_configuration(agent_config)
            if not is_valid:
                raise ValueError(f"Invalid agent configuration: {error_msg}")
            
            # Create agent instance
            agent = StrandsAgent(agent_config)
            
            # Initialize agent
            if not agent.initialize():
                raise AgentLifecycleError(f"Failed to initialize agent: {agent.error_message}")
            
            # Store agent
            self._agents[agent_config.agent_id] = agent
            
            logger.info(f"Created agent {agent_config.agent_id} for session {session_id}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent for session {session_id}: {e}")
            raise
    
    def get_agent(self, agent_id: str) -> Optional[StrandsAgent]:
        """
        Get agent by ID
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            StrandsAgent or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_agent_by_session(self, session_id: str) -> Optional[StrandsAgent]:
        """
        Get agent by session ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            StrandsAgent or None if not found
        """
        agent_id = f"agent_{session_id}"
        return self.get_agent(agent_id)
    
    def terminate_agent(self, agent_id: str, save_memory: bool = True) -> bool:
        """
        Terminate an agent
        
        Args:
            agent_id: Agent identifier
            save_memory: Whether to save memory before terminating
            
        Returns:
            True if successful, False otherwise
        """
        agent = self._agents.get(agent_id)
        if not agent:
            logger.warning(f"Agent {agent_id} not found for termination")
            return False
        
        # Terminate agent
        success = agent.terminate(save_memory=save_memory)
        
        # Remove from active agents
        if success:
            del self._agents[agent_id]
        
        return success
    
    def cleanup_idle_agents(self) -> int:
        """
        Cleanup idle agents
        
        Returns:
            Number of agents cleaned up
        """
        cleanup_count = 0
        agents_to_remove = []
        
        for agent_id, agent in self._agents.items():
            if agent.is_idle() or agent.is_expired():
                logger.info(f"Cleaning up idle/expired agent {agent_id}")
                if agent.terminate(save_memory=True):
                    agents_to_remove.append(agent_id)
                    cleanup_count += 1
        
        # Remove cleaned up agents
        for agent_id in agents_to_remove:
            del self._agents[agent_id]
        
        if cleanup_count > 0:
            logger.info(f"Cleaned up {cleanup_count} idle/expired agents")
        
        return cleanup_count
    
    def get_active_agents(self) -> List[StrandsAgent]:
        """
        Get all active agents
        
        Returns:
            List of active StrandsAgent instances
        """
        return [
            agent for agent in self._agents.values()
            if agent.state == AgentState.ACTIVE
        ]
    
    def get_agent_count(self) -> int:
        """
        Get total number of agents
        
        Returns:
            Agent count
        """
        return len(self._agents)
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status
        
        Returns:
            Status dictionary
        """
        agents_by_state = {}
        for agent in self._agents.values():
            state = agent.state.value
            agents_by_state[state] = agents_by_state.get(state, 0) + 1
        
        return {
            "total_agents": len(self._agents),
            "max_concurrent_agents": self.config.MAX_CONCURRENT_AGENTS,
            "agents_by_state": agents_by_state,
            "active_agents": len(self.get_active_agents())
        }


# Global service instance
strands_agent_service = StrandsAgentService()
