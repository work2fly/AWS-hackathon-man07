"""
Unit tests for AgentCore Memory Service
🏆 Breaking Barriers UK 2026 compliant
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

from src.services.agentcore_memory_service import AgentCoreMemoryService
from src.models.agent_memory import (
    AgentMemory,
    ConversationContext,
    TherapeuticProfile,
    RetentionPolicy,
    RetentionPolicyType,
    SessionSummary,
    ProgressNote,
    PersonalityAdaptation
)


class TestAgentCoreMemoryService:
    """Test suite for AgentCore Memory Service"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock-agent-runtime client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def memory_service(self, mock_bedrock_client):
        """Create memory service with mocked client"""
        return AgentCoreMemoryService()
    
    @pytest.fixture
    def sample_memory(self):
        """Create sample memory for testing"""
        return AgentMemory(
            memory_id="therapy_session_client123",
            client_id="client123",
            conversation_context=ConversationContext(
                ongoing_topics=["anxiety", "work stress"],
                therapeutic_goals=["manage stress", "improve sleep"],
                total_sessions=5
            ),
            therapeutic_profile=TherapeuticProfile(
                communication_style="empathetic",
                language_preference="en",
                preferred_approaches=["CBT", "mindfulness"]
            ),
            retention_policy=RetentionPolicy(
                policy_type=RetentionPolicyType.STANDARD
            )
        )
    
    def test_create_memory_success(self, memory_service, mock_bedrock_client):
        """Test successful memory creation"""
        # Arrange
        client_id = "client123"
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Act
        memory = memory_service.create_memory(client_id, language_preference="en")
        
        # Assert
        assert memory.client_id == client_id
        assert memory.memory_id == f"therapy_session_{client_id}"
        assert memory.therapeutic_profile.language_preference == "en"
        assert memory.retention_policy.policy_type == RetentionPolicyType.STANDARD
        mock_bedrock_client.put_memory.assert_called_once()
    
    def test_create_memory_with_extended_retention(self, memory_service, mock_bedrock_client):
        """Test memory creation with extended retention policy"""
        # Arrange
        client_id = "client456"
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Act
        memory = memory_service.create_memory(
            client_id,
            retention_policy_type=RetentionPolicyType.EXTENDED
        )
        
        # Assert
        assert memory.retention_policy.policy_type == RetentionPolicyType.EXTENDED
        assert memory.retention_policy.expiration_date is not None
    
    def test_get_memory_success(self, memory_service, mock_bedrock_client, sample_memory):
        """Test successful memory retrieval"""
        # Arrange
        client_id = "client123"
        memory_data = sample_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Act
        memory = memory_service.get_memory(client_id)
        
        # Assert
        assert memory is not None
        assert memory.client_id == client_id
        assert len(memory.conversation_context.ongoing_topics) == 2
        mock_bedrock_client.get_memory.assert_called_once()
    
    def test_get_memory_not_found(self, memory_service, mock_bedrock_client):
        """Test memory retrieval when memory doesn't exist"""
        # Arrange
        client_id = "nonexistent"
        error_response = {'Error': {'Code': 'ResourceNotFoundException'}}
        mock_bedrock_client.get_memory.side_effect = ClientError(error_response, 'get_memory')
        
        # Act
        memory = memory_service.get_memory(client_id)
        
        # Assert
        assert memory is None
    
    def test_update_memory_success(self, memory_service, mock_bedrock_client, sample_memory):
        """Test successful memory update"""
        # Arrange
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        original_version = sample_memory.version
        
        # Act
        updated_memory = memory_service.update_memory(sample_memory)
        
        # Assert
        assert updated_memory.version == original_version + 1
        assert updated_memory.last_updated is not None
        mock_bedrock_client.put_memory.assert_called_once()
    
    def test_add_session_summary(self, memory_service, mock_bedrock_client, sample_memory):
        """Test adding session summary to memory"""
        # Arrange
        client_id = "client123"
        memory_data = sample_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        session_summary = SessionSummary(
            session_id="session789",
            duration_seconds=1800,
            key_topics=["anxiety", "coping strategies"],
            emotional_state=["calm", "hopeful"],
            therapeutic_progress="Client showed improvement in managing anxiety"
        )
        
        # Act
        updated_memory = memory_service.add_session_summary(client_id, session_summary)
        
        # Assert
        assert len(updated_memory.conversation_context.session_history) == 1
        assert updated_memory.conversation_context.total_sessions == 6  # Original 5 + 1
        assert updated_memory.conversation_context.last_session_date is not None
    
    def test_add_progress_note(self, memory_service, mock_bedrock_client, sample_memory):
        """Test adding progress note to memory"""
        # Arrange
        client_id = "client123"
        memory_data = sample_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        progress_note = ProgressNote(
            note_id="note001",
            content="Client demonstrated effective use of breathing techniques",
            category="coping_skills",
            importance=4
        )
        
        # Act
        updated_memory = memory_service.add_progress_note(client_id, progress_note)
        
        # Assert
        assert len(updated_memory.conversation_context.progress_notes) == 1
        assert updated_memory.conversation_context.progress_notes[0].content == progress_note.content
    
    def test_update_therapeutic_profile(self, memory_service, mock_bedrock_client, sample_memory):
        """Test updating therapeutic profile"""
        # Arrange
        client_id = "client123"
        memory_data = sample_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        profile_updates = {
            'communication_style': 'direct',
            'triggers_to_avoid': ['loud noises', 'crowded spaces']
        }
        
        # Act
        updated_memory = memory_service.update_therapeutic_profile(client_id, profile_updates)
        
        # Assert
        assert updated_memory.therapeutic_profile.communication_style == 'direct'
        assert len(updated_memory.therapeutic_profile.triggers_to_avoid) == 2
    
    def test_delete_memory_success(self, memory_service, mock_bedrock_client):
        """Test successful memory deletion"""
        # Arrange
        client_id = "client123"
        mock_bedrock_client.delete_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Act
        result = memory_service.delete_memory(client_id)
        
        # Assert
        assert result is True
        mock_bedrock_client.delete_memory.assert_called_once()
    
    def test_delete_memory_not_found(self, memory_service, mock_bedrock_client):
        """Test memory deletion when memory doesn't exist"""
        # Arrange
        client_id = "nonexistent"
        error_response = {'Error': {'Code': 'ResourceNotFoundException'}}
        mock_bedrock_client.delete_memory.side_effect = ClientError(error_response, 'delete_memory')
        
        # Act
        result = memory_service.delete_memory(client_id)
        
        # Assert
        assert result is False
    
    def test_serialize_context_for_prompt(self, memory_service, mock_bedrock_client, sample_memory):
        """Test serializing context for AI prompts"""
        # Arrange
        client_id = "client123"
        memory_data = sample_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Act
        context_string = memory_service.serialize_context_for_prompt(client_id)
        
        # Assert
        assert "Communication Style: empathetic" in context_string
        assert "Language Preference: en" in context_string
        assert "Ongoing Topics: anxiety, work stress" in context_string
        assert "Total Sessions: 5" in context_string
    
    def test_memory_optimization(self, memory_service, mock_bedrock_client):
        """Test memory optimization when size limit is exceeded"""
        # Arrange
        client_id = "client123"
        
        # Create memory with many session summaries
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                session_history=[
                    SessionSummary(
                        session_id=f"session{i}",
                        duration_seconds=1800,
                        key_topics=["topic1", "topic2"],
                        emotional_state=["calm"],
                        therapeutic_progress="Progress note"
                    )
                    for i in range(100)  # Exceed MAX_CONVERSATION_HISTORY_ITEMS
                ]
            ),
            therapeutic_profile=TherapeuticProfile()
        )
        
        # Act
        optimized_memory = memory_service._optimize_memory(memory)
        
        # Assert
        assert len(optimized_memory.conversation_context.session_history) <= 50  # MAX_CONVERSATION_HISTORY_ITEMS
    
    def test_get_conversation_context(self, memory_service, mock_bedrock_client, sample_memory):
        """Test getting conversation context"""
        # Arrange
        client_id = "client123"
        memory_data = sample_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Act
        context = memory_service.get_conversation_context(client_id)
        
        # Assert
        assert context is not None
        assert len(context.ongoing_topics) == 2
        assert context.total_sessions == 5
    
    def test_get_therapeutic_profile(self, memory_service, mock_bedrock_client, sample_memory):
        """Test getting therapeutic profile"""
        # Arrange
        client_id = "client123"
        memory_data = sample_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Act
        profile = memory_service.get_therapeutic_profile(client_id)
        
        # Assert
        assert profile is not None
        assert profile.communication_style == "empathetic"
        assert profile.language_preference == "en"
