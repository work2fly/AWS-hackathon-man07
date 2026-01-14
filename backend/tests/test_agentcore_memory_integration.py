"""
Integration Tests for AgentCore Memory and Persistence
🏆 Breaking Barriers UK 2026 compliant

Task 8.2: Test AgentCore memory and persistence
- Verify conversation context loading and saving
- Test cross-session continuity and memory retrieval
- Validate memory optimization and cleanup procedures
- Test memory-based personalization features

**Validates: Requirements 3.3, 3.6, 3.7**
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

import sys
import os
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.agentcore_memory_service import AgentCoreMemoryService
from src.services.session_continuity_service import SessionContinuityService
from src.services.personalization_engine import PersonalizationEngine
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


class TestConversationContextPersistence:
    """Test conversation context loading and saving"""
    
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
    
    def test_context_save_and_load_cycle(self, memory_service, mock_bedrock_client):
        """
        Test complete save and load cycle for conversation context
        
        **Validates: Requirements 3.3, 3.6**
        """
        client_id = "test-client-001"
        
        # Create initial memory
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        memory = memory_service.create_memory(client_id, language_preference="en")
        
        # Add session data
        session_summary = SessionSummary(
            session_id="session-001",
            duration_seconds=1800,
            key_topics=["anxiety", "work stress"],
            emotional_state=["anxious", "hopeful"],
            therapeutic_progress="Client discussed work-related anxiety and learned breathing techniques"
        )
        
        # Mock get_memory to return the created memory
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Add session summary
        updated_memory = memory_service.add_session_summary(client_id, session_summary)
        
        # Verify save
        assert updated_memory.conversation_context.total_sessions == 1
        assert len(updated_memory.conversation_context.session_history) == 1
        
        # Mock retrieval with updated memory
        updated_data = updated_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(updated_data)
        }
        
        # Load context
        loaded_memory = memory_service.get_memory(client_id)
        
        # Verify loaded data matches saved data
        assert loaded_memory is not None
        assert loaded_memory.client_id == client_id
        assert loaded_memory.conversation_context.total_sessions == 1
        assert len(loaded_memory.conversation_context.session_history) == 1
        assert loaded_memory.conversation_context.session_history[0].session_id == "session-001"
        
        print("✅ Context save and load cycle validated")
    
    def test_incremental_context_updates(self, memory_service, mock_bedrock_client):
        """
        Test incremental updates to conversation context
        
        **Validates: Requirements 3.6, 3.7**
        """
        client_id = "test-client-002"
        
        # Create initial memory
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        memory = memory_service.create_memory(client_id)
        
        # Simulate multiple session updates
        for i in range(5):
            memory_data = memory.to_dict()
            mock_bedrock_client.get_memory.return_value = {
                'memoryContent': json.dumps(memory_data)
            }
            
            session_summary = SessionSummary(
                session_id=f"session-{i:03d}",
                duration_seconds=1800 + (i * 100),
                key_topics=[f"topic-{i}", "general wellness"],
                emotional_state=["calm", "engaged"],
                therapeutic_progress=f"Session {i} progress notes"
            )
            
            memory = memory_service.add_session_summary(client_id, session_summary)
        
        # Verify all sessions recorded
        assert memory.conversation_context.total_sessions == 5
        assert len(memory.conversation_context.session_history) == 5
        
        # Verify session order (most recent first)
        assert memory.conversation_context.session_history[0].session_id == "session-004"
        assert memory.conversation_context.session_history[-1].session_id == "session-000"
        
        print("✅ Incremental context updates validated")
    
    def test_context_serialization_for_ai(self, memory_service, mock_bedrock_client):
        """
        Test context serialization for AI prompt injection
        
        **Validates: Requirements 3.6, 3.7**
        """
        client_id = "test-client-003"
        
        # Create memory with rich context
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                ongoing_topics=["anxiety", "sleep issues", "work stress"],
                therapeutic_goals=["improve sleep quality", "manage work stress"],
                total_sessions=10,
                session_history=[
                    SessionSummary(
                        session_id="recent-session",
                        duration_seconds=1800,
                        key_topics=["sleep", "anxiety"],
                        emotional_state=["tired", "worried"],
                        therapeutic_progress="Discussed sleep hygiene"
                    )
                ]
            ),
            therapeutic_profile=TherapeuticProfile(
                communication_style="empathetic",
                language_preference="en",
                preferred_approaches=["CBT", "mindfulness"],
                triggers_to_avoid=["loud noises"],
                successful_interventions=["breathing exercises"]
            )
        )
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Serialize context
        context_string = memory_service.serialize_context_for_prompt(client_id)
        
        # Verify serialization includes key information
        assert "Communication Style: empathetic" in context_string
        assert "Language Preference: en" in context_string
        assert "Ongoing Topics: anxiety, sleep issues, work stress" in context_string
        assert "Total Sessions: 10" in context_string
        assert "Preferred Approaches: CBT, mindfulness" in context_string
        
        print("✅ Context serialization for AI validated")


class TestCrossSessionContinuity:
    """Test cross-session continuity and memory retrieval"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock-agent-runtime client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def continuity_service(self, mock_bedrock_client):
        """Create session continuity service"""
        return SessionContinuityService()
    
    def test_session_resumption_with_context(self, continuity_service, mock_bedrock_client):
        """
        Test resuming a session with previous context
        
        **Validates: Requirements 3.7, 7.1, 7.2**
        """
        client_id = "test-client-004"
        session_id = "new-session-001"
        
        # Create previous session memory
        previous_memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                ongoing_topics=["anxiety", "relationships"],
                therapeutic_goals=["improve communication"],
                total_sessions=3,
                last_session_date=datetime.now() - timedelta(days=7)
            ),
            therapeutic_profile=TherapeuticProfile(
                communication_style="direct",
                language_preference="en"
            )
        )
        
        memory_data = previous_memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Resume session
        context = continuity_service.load_session_context(client_id, session_id)
        
        # Verify context loaded
        assert context is not None
        assert context['client_id'] == client_id
        assert context['session_id'] == session_id
        assert 'previous_topics' in context
        assert 'therapeutic_goals' in context
        assert context['session_number'] == 4  # Previous 3 + 1
        
        print("✅ Session resumption with context validated")
    
    def test_therapeutic_relationship_continuity(self, continuity_service, mock_bedrock_client):
        """
        Test therapeutic relationship continuity across sessions
        
        **Validates: Requirements 3.7, 7.1**
        """
        client_id = "test-client-005"
        
        # Create memory with relationship history
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                ongoing_topics=["trust", "vulnerability"],
                therapeutic_goals=["build trust", "open communication"],
                total_sessions=15,
                progress_notes=[
                    ProgressNote(
                        note_id="note-001",
                        content="Client is becoming more comfortable sharing",
                        category="relationship_building",
                        importance=5
                    ),
                    ProgressNote(
                        note_id="note-002",
                        content="Breakthrough moment discussing childhood",
                        category="therapeutic_progress",
                        importance=5
                    )
                ]
            ),
            therapeutic_profile=TherapeuticProfile(
                communication_style="gentle",
                successful_interventions=["reflective listening", "validation"]
            )
        )
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Load context for new session
        context = continuity_service.load_session_context(client_id, "session-016")
        
        # Verify relationship continuity
        assert context['session_number'] == 16
        assert 'trust' in context['previous_topics']
        assert 'build trust' in context['therapeutic_goals']
        assert len(context.get('progress_notes', [])) > 0
        
        print("✅ Therapeutic relationship continuity validated")
    
    def test_long_term_memory_retrieval(self, continuity_service, mock_bedrock_client):
        """
        Test retrieval of long-term memory patterns
        
        **Validates: Requirements 3.6, 3.7, 7.2**
        """
        client_id = "test-client-006"
        
        # Create memory with long history
        session_history = [
            SessionSummary(
                session_id=f"session-{i:03d}",
                duration_seconds=1800,
                key_topics=["anxiety", "coping"] if i % 2 == 0 else ["progress", "goals"],
                emotional_state=["calm", "hopeful"],
                therapeutic_progress=f"Session {i} notes",
                timestamp=datetime.now() - timedelta(days=30-i)
            )
            for i in range(20)
        ]
        
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                session_history=session_history,
                total_sessions=20
            ),
            therapeutic_profile=TherapeuticProfile()
        )
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Load context
        context = continuity_service.load_session_context(client_id, "session-021")
        
        # Verify long-term patterns accessible
        assert context['session_number'] == 21
        assert len(context.get('session_history', [])) > 0
        
        print("✅ Long-term memory retrieval validated")


class TestMemoryOptimization:
    """Test memory optimization and cleanup procedures"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock-agent-runtime client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def memory_service(self, mock_bedrock_client):
        """Create memory service"""
        return AgentCoreMemoryService()
    
    def test_session_history_pruning(self, memory_service, mock_bedrock_client):
        """
        Test automatic pruning of old session history
        
        **Validates: Requirements 3.6, 7.6**
        """
        client_id = "test-client-007"
        
        # Create memory with excessive history
        session_history = [
            SessionSummary(
                session_id=f"session-{i:03d}",
                duration_seconds=1800,
                key_topics=["topic"],
                emotional_state=["calm"],
                therapeutic_progress="Progress"
            )
            for i in range(100)  # Exceeds MAX_CONVERSATION_HISTORY_ITEMS
        ]
        
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                session_history=session_history,
                total_sessions=100
            ),
            therapeutic_profile=TherapeuticProfile()
        )
        
        # Optimize memory
        optimized = memory_service._optimize_memory(memory)
        
        # Verify pruning occurred
        assert len(optimized.conversation_context.session_history) <= 50  # MAX_CONVERSATION_HISTORY_ITEMS
        assert optimized.conversation_context.total_sessions == 100  # Count preserved
        
        # Verify most recent sessions kept
        assert optimized.conversation_context.session_history[0].session_id == "session-099"
        
        print("✅ Session history pruning validated")
    
    def test_progress_notes_consolidation(self, memory_service, mock_bedrock_client):
        """
        Test consolidation of progress notes
        
        **Validates: Requirements 3.6, 7.6**
        """
        client_id = "test-client-008"
        
        # Create memory with many progress notes
        progress_notes = [
            ProgressNote(
                note_id=f"note-{i:03d}",
                content=f"Progress note {i}",
                category="general",
                importance=i % 5 + 1  # Importance 1-5
            )
            for i in range(100)
        ]
        
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                progress_notes=progress_notes
            ),
            therapeutic_profile=TherapeuticProfile()
        )
        
        # Optimize memory
        optimized = memory_service._optimize_memory(memory)
        
        # Verify consolidation (keeps high importance notes)
        assert len(optimized.conversation_context.progress_notes) < len(progress_notes)
        
        # Verify high importance notes preserved
        for note in optimized.conversation_context.progress_notes:
            assert note.importance >= 3  # Only important notes kept
        
        print("✅ Progress notes consolidation validated")
    
    def test_retention_policy_enforcement(self, memory_service, mock_bedrock_client):
        """
        Test enforcement of retention policies
        
        **Validates: Requirements 3.6, 6.4, 7.6**
        """
        client_id = "test-client-009"
        
        # Create memory with expired retention
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(),
            therapeutic_profile=TherapeuticProfile(),
            retention_policy=RetentionPolicy(
                policy_type=RetentionPolicyType.STANDARD,
                expiration_date=datetime.now() - timedelta(days=1)  # Expired
            )
        )
        
        # Check if memory should be deleted
        should_delete = memory.retention_policy.is_expired()
        
        assert should_delete is True, "Expired memory should be flagged for deletion"
        
        print("✅ Retention policy enforcement validated")


class TestMemoryBasedPersonalization:
    """Test memory-based personalization features"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock-agent-runtime client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def personalization_engine(self, mock_bedrock_client):
        """Create personalization engine"""
        return PersonalizationEngine()
    
    def test_communication_style_adaptation(self, personalization_engine, mock_bedrock_client):
        """
        Test adaptation of communication style based on memory
        
        **Validates: Requirements 3.7, 10.6**
        """
        client_id = "test-client-010"
        
        # Create memory with communication preferences
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                personality_adaptations=[
                    PersonalityAdaptation(
                        adaptation_type="communication_style",
                        from_value="formal",
                        to_value="casual",
                        reason="Client responds better to casual tone",
                        effectiveness_score=0.85
                    )
                ]
            ),
            therapeutic_profile=TherapeuticProfile(
                communication_style="casual"
            )
        )
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Get personalized settings
        settings = personalization_engine.get_personalized_settings(client_id)
        
        # Verify adaptation applied
        assert settings is not None
        assert settings.get('communication_style') == 'casual'
        
        print("✅ Communication style adaptation validated")
    
    def test_therapeutic_approach_personalization(self, personalization_engine, mock_bedrock_client):
        """
        Test personalization of therapeutic approaches
        
        **Validates: Requirements 3.7, 7.3**
        """
        client_id = "test-client-011"
        
        # Create memory with approach preferences
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(),
            therapeutic_profile=TherapeuticProfile(
                preferred_approaches=["CBT", "mindfulness"],
                successful_interventions=["breathing exercises", "thought challenging"],
                triggers_to_avoid=["confrontational language"]
            )
        )
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Get personalized settings
        settings = personalization_engine.get_personalized_settings(client_id)
        
        # Verify personalization
        assert settings is not None
        assert 'preferred_approaches' in settings
        assert 'CBT' in settings['preferred_approaches']
        assert 'mindfulness' in settings['preferred_approaches']
        
        print("✅ Therapeutic approach personalization validated")
    
    def test_language_preference_persistence(self, personalization_engine, mock_bedrock_client):
        """
        Test persistence of language preferences
        
        **Validates: Requirements 10.5, 10.6**
        """
        client_id = "test-client-012"
        
        # Create memory with language preferences
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(),
            therapeutic_profile=TherapeuticProfile(
                language_preference="es",
                cultural_considerations=["Latin American cultural context"]
            )
        )
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Get personalized settings
        settings = personalization_engine.get_personalized_settings(client_id)
        
        # Verify language preference
        assert settings is not None
        assert settings.get('language_preference') == 'es'
        assert 'cultural_considerations' in settings
        
        print("✅ Language preference persistence validated")


class TestEndToEndMemoryIntegration:
    """Test complete end-to-end memory integration"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock-agent-runtime client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    def test_complete_therapy_journey(self, mock_bedrock_client):
        """
        Test complete therapy journey with memory persistence
        
        **Validates: Requirements 3.3, 3.6, 3.7, 7.1, 7.2**
        """
        memory_service = AgentCoreMemoryService()
        continuity_service = SessionContinuityService()
        personalization_engine = PersonalizationEngine()
        
        client_id = "test-client-013"
        
        # Session 1: Initial session
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        memory = memory_service.create_memory(client_id, language_preference="en")
        
        session1_summary = SessionSummary(
            session_id="session-001",
            duration_seconds=1800,
            key_topics=["introduction", "anxiety"],
            emotional_state=["nervous", "hopeful"],
            therapeutic_progress="Initial assessment completed"
        )
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        memory = memory_service.add_session_summary(client_id, session1_summary)
        
        # Session 2: Follow-up with progress
        updated_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(updated_data)
        }
        
        session2_summary = SessionSummary(
            session_id="session-002",
            duration_seconds=1800,
            key_topics=["anxiety", "coping strategies"],
            emotional_state=["calm", "engaged"],
            therapeutic_progress="Learned breathing techniques"
        )
        
        memory = memory_service.add_session_summary(client_id, session2_summary)
        
        # Add progress note
        progress_note = ProgressNote(
            note_id="note-001",
            content="Client showing good progress with anxiety management",
            category="therapeutic_progress",
            importance=4
        )
        
        updated_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(updated_data)
        }
        
        memory = memory_service.add_progress_note(client_id, progress_note)
        
        # Session 3: Load context and verify continuity
        final_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(final_data)
        }
        
        context = continuity_service.load_session_context(client_id, "session-003")
        
        # Verify complete journey
        assert context['session_number'] == 3
        assert 'anxiety' in context['previous_topics']
        assert len(context.get('session_history', [])) >= 2
        
        # Get personalized settings
        settings = personalization_engine.get_personalized_settings(client_id)
        assert settings is not None
        
        print("✅ Complete therapy journey with memory persistence validated")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
