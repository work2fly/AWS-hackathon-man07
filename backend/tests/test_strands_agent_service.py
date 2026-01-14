"""
Unit tests for Strands Agent Service
🏆 Breaking Barriers UK 2026 compliant

Tests agent initialization, lifecycle management, and tool integration.
"""

import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Set AWS region before importing services
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from src.services.strands_agent_service import (
    StrandsAgent,
    StrandsAgentService,
    AgentLifecycleError
)
from src.config.strands_agent_config import (
    AgentConfiguration,
    AgentState,
    AgentCapability,
    AgentTool,
    StrandsAgentConfig
)


class TestStrandsAgent:
    """Test suite for StrandsAgent"""
    
    @pytest.fixture
    def basic_config(self):
        """Create basic agent configuration"""
        config = StrandsAgentConfig()
        return config.create_agent_configuration(
            session_id="session123",
            client_id="client123",
            language="en"
        )
    
    @pytest.fixture
    def mock_nova_client(self):
        """Mock Nova Sonic client"""
        with patch('src.services.strands_agent_service.nova_sonic_client') as mock:
            mock.create_session.return_value = {
                "session_id": "session123",
                "status": "active"
            }
            yield mock
    
    @pytest.fixture
    def mock_memory_service(self):
        """Mock AgentCore memory service"""
        with patch('src.services.strands_agent_service.AgentCoreMemoryService') as mock:
            mock_instance = MagicMock()
            mock_instance.get_memory.return_value = None
            mock_instance.create_memory.return_value = MagicMock(memory_id="mem123")
            mock.return_value = mock_instance
            yield mock_instance

    def test_agent_initialization(self, basic_config, mock_nova_client, mock_memory_service):
        """Test agent initialization"""
        # Arrange
        agent = StrandsAgent(basic_config)
        
        # Act
        success = agent.initialize()
        
        # Assert
        assert success is True
        assert agent.state == AgentState.READY
        assert agent.config.state == AgentState.READY
        assert agent.created_at is not None
    
    def test_agent_start(self, basic_config, mock_nova_client, mock_memory_service):
        """Test agent start"""
        # Arrange
        agent = StrandsAgent(basic_config)
        agent.initialize()
        
        # Act
        success = agent.start()
        
        # Assert
        assert success is True
        assert agent.state == AgentState.ACTIVE
        assert agent.config.state == AgentState.ACTIVE
    
    def test_agent_pause_resume(self, basic_config, mock_nova_client, mock_memory_service):
        """Test agent pause and resume"""
        # Arrange
        agent = StrandsAgent(basic_config)
        agent.initialize()
        agent.start()
        
        # Act - Pause
        pause_success = agent.pause()
        
        # Assert - Paused
        assert pause_success is True
        assert agent.state == AgentState.PAUSED
        
        # Act - Resume
        resume_success = agent.resume()
        
        # Assert - Resumed
        assert resume_success is True
        assert agent.state == AgentState.ACTIVE
    
    def test_agent_terminate(self, basic_config, mock_nova_client, mock_memory_service):
        """Test agent termination"""
        # Arrange
        agent = StrandsAgent(basic_config)
        agent.initialize()
        agent.start()
        
        # Act
        success = agent.terminate(save_memory=True)
        
        # Assert
        assert success is True
        assert agent.state == AgentState.TERMINATED
        mock_nova_client.terminate_session.assert_called_once()
    
    def test_agent_idle_detection(self, basic_config, mock_nova_client, mock_memory_service):
        """Test idle detection"""
        # Arrange
        agent = StrandsAgent(basic_config)
        agent.initialize()
        agent.last_activity = datetime.utcnow() - timedelta(seconds=400)
        
        # Act
        is_idle = agent.is_idle(idle_timeout_seconds=300)
        
        # Assert
        assert is_idle is True
    
    def test_agent_expiration_detection(self, basic_config, mock_nova_client, mock_memory_service):
        """Test expiration detection"""
        # Arrange
        agent = StrandsAgent(basic_config)
        agent.initialize()
        agent.created_at = datetime.utcnow() - timedelta(seconds=4000)
        agent.config.metadata["timeout_seconds"] = 3600
        
        # Act
        is_expired = agent.is_expired()
        
        # Assert
        assert is_expired is True


class TestStrandsAgentService:
    """Test suite for StrandsAgentService"""
    
    @pytest.fixture
    def agent_service(self):
        """Create agent service"""
        return StrandsAgentService()
    
    @pytest.fixture
    def mock_nova_client(self):
        """Mock Nova Sonic client"""
        with patch('src.services.strands_agent_service.nova_sonic_client') as mock:
            mock.create_session.return_value = {
                "session_id": "session123",
                "status": "active"
            }
            yield mock
    
    @pytest.fixture
    def mock_memory_service(self):
        """Mock AgentCore memory service"""
        with patch('src.services.strands_agent_service.AgentCoreMemoryService') as mock:
            mock_instance = MagicMock()
            mock_instance.get_memory.return_value = None
            mock_instance.create_memory.return_value = MagicMock(memory_id="mem123")
            mock.return_value = mock_instance
            yield mock_instance
    
    def test_create_agent_success(self, agent_service, mock_nova_client, mock_memory_service):
        """Test successful agent creation"""
        # Act
        agent = agent_service.create_agent(
            session_id="session123",
            client_id="client123",
            language="en",
            nova_sonic_config={"model_id": "amazon.nova-sonic-2"}
        )
        
        # Assert
        assert agent is not None
        assert agent.config.session_id == "session123"
        assert agent.config.client_id == "client123"
        assert agent.state == AgentState.READY
        assert agent_service.get_agent_count() == 1
    
    def test_get_agent_by_session(self, agent_service, mock_nova_client, mock_memory_service):
        """Test getting agent by session ID"""
        # Arrange
        agent = agent_service.create_agent(
            session_id="session123",
            client_id="client123",
            nova_sonic_config={"model_id": "amazon.nova-sonic-2"}
        )
        
        # Act
        retrieved_agent = agent_service.get_agent_by_session("session123")
        
        # Assert
        assert retrieved_agent is not None
        assert retrieved_agent.config.session_id == "session123"
    
    def test_terminate_agent(self, agent_service, mock_nova_client, mock_memory_service):
        """Test agent termination"""
        # Arrange
        agent = agent_service.create_agent(
            session_id="session123",
            client_id="client123",
            nova_sonic_config={"model_id": "amazon.nova-sonic-2"}
        )
        agent_id = agent.config.agent_id
        
        # Act
        success = agent_service.terminate_agent(agent_id, save_memory=True)
        
        # Assert
        assert success is True
        assert agent_service.get_agent(agent_id) is None
        assert agent_service.get_agent_count() == 0
    
    def test_cleanup_idle_agents(self, agent_service, mock_nova_client, mock_memory_service):
        """Test cleanup of idle agents"""
        # Arrange
        agent = agent_service.create_agent(
            session_id="session123",
            client_id="client123",
            nova_sonic_config={"model_id": "amazon.nova-sonic-2"}
        )
        # Make agent idle
        agent.last_activity = datetime.utcnow() - timedelta(seconds=400)
        
        # Act
        cleanup_count = agent_service.cleanup_idle_agents()
        
        # Assert
        assert cleanup_count == 1
        assert agent_service.get_agent_count() == 0
    
    def test_max_concurrent_agents_limit(self, agent_service, mock_nova_client, mock_memory_service):
        """Test maximum concurrent agents limit"""
        # Arrange
        agent_service.config.MAX_CONCURRENT_AGENTS = 2
        
        # Act - Create agents up to limit
        agent1 = agent_service.create_agent("session1", "client1", nova_sonic_config={"model_id": "amazon.nova-sonic-2"})
        agent2 = agent_service.create_agent("session2", "client2", nova_sonic_config={"model_id": "amazon.nova-sonic-2"})
        
        # Assert - Should succeed
        assert agent_service.get_agent_count() == 2
        
        # Act - Try to exceed limit
        with pytest.raises(AgentLifecycleError):
            agent_service.create_agent("session3", "client3", nova_sonic_config={"model_id": "amazon.nova-sonic-2"})
    
    def test_get_service_status(self, agent_service, mock_nova_client, mock_memory_service):
        """Test service status reporting"""
        # Arrange
        agent1 = agent_service.create_agent("session1", "client1", nova_sonic_config={"model_id": "amazon.nova-sonic-2"})
        agent2 = agent_service.create_agent("session2", "client2", nova_sonic_config={"model_id": "amazon.nova-sonic-2"})
        agent1.start()
        
        # Act
        status = agent_service.get_service_status()
        
        # Assert
        assert status["total_agents"] == 2
        assert status["active_agents"] == 1
        assert "agents_by_state" in status
