"""
Standalone unit tests for AgentCore Memory models and serialization
Tests core functionality without full service dependencies
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.agent_memory import (
    AgentMemory,
    ConversationContext,
    TherapeuticProfile,
    RetentionPolicy,
    RetentionPolicyType,
    SessionSummary,
    ProgressNote,
    PersonalityAdaptation
)


def test_agent_memory_creation():
    """Test creating an AgentMemory object"""
    memory = AgentMemory(
        memory_id="therapy_session_client123",
        client_id="client123",
        conversation_context=ConversationContext(),
        therapeutic_profile=TherapeuticProfile()
    )
    
    assert memory.client_id == "client123"
    assert memory.memory_id == "therapy_session_client123"
    assert memory.version == 1
    print("✓ AgentMemory creation test passed")


def test_session_summary_creation():
    """Test creating a SessionSummary"""
    summary = SessionSummary(
        session_id="session123",
        duration_seconds=1800,
        key_topics=["anxiety", "work stress"],
        emotional_state=["calm", "hopeful"],
        therapeutic_progress="Client showed improvement"
    )
    
    assert summary.session_id == "session123"
    assert summary.duration_seconds == 1800
    assert len(summary.key_topics) == 2
    print("✓ SessionSummary creation test passed")


def test_conversation_context_with_history():
    """Test ConversationContext with session history"""
    context = ConversationContext(
        ongoing_topics=["anxiety", "sleep issues"],
        therapeutic_goals=["manage stress", "improve sleep quality"],
        total_sessions=5
    )
    
    # Add session summaries
    for i in range(3):
        summary = SessionSummary(
            session_id=f"session{i}",
            duration_seconds=1800,
            key_topics=["anxiety"],
            emotional_state=["calm"],
            therapeutic_progress=f"Session {i} progress"
        )
        context.session_history.append(summary)
    
    assert len(context.session_history) == 3
    assert context.total_sessions == 5
    assert len(context.ongoing_topics) == 2
    print("✓ ConversationContext with history test passed")


def test_therapeutic_profile():
    """Test TherapeuticProfile creation and attributes"""
    profile = TherapeuticProfile(
        communication_style="empathetic",
        language_preference="en",
        preferred_approaches=["CBT", "mindfulness"],
        triggers_to_avoid=["loud noises"],
        successful_interventions=["breathing exercises"]
    )
    
    assert profile.communication_style == "empathetic"
    assert profile.language_preference == "en"
    assert len(profile.preferred_approaches) == 2
    assert "CBT" in profile.preferred_approaches
    print("✓ TherapeuticProfile test passed")


def test_retention_policy():
    """Test RetentionPolicy with different types"""
    # Standard policy
    standard_policy = RetentionPolicy(
        policy_type=RetentionPolicyType.STANDARD,
        expiration_date=datetime.utcnow() + timedelta(days=90)
    )
    assert standard_policy.policy_type == RetentionPolicyType.STANDARD
    assert standard_policy.auto_cleanup_enabled is True
    
    # Permanent policy
    permanent_policy = RetentionPolicy(
        policy_type=RetentionPolicyType.PERMANENT
    )
    assert permanent_policy.policy_type == RetentionPolicyType.PERMANENT
    assert permanent_policy.expiration_date is None
    
    print("✓ RetentionPolicy test passed")


def test_progress_note():
    """Test ProgressNote creation"""
    note = ProgressNote(
        note_id="note001",
        content="Client demonstrated effective coping strategies",
        category="coping_skills",
        importance=4
    )
    
    assert note.note_id == "note001"
    assert note.importance == 4
    assert note.category == "coping_skills"
    print("✓ ProgressNote test passed")


def test_personality_adaptation():
    """Test PersonalityAdaptation creation"""
    adaptation = PersonalityAdaptation(
        adaptation_id="adapt001",
        adaptation_type="communication_style",
        description="Adjusted to more direct communication",
        effectiveness_score=0.8
    )
    
    assert adaptation.adaptation_id == "adapt001"
    assert adaptation.effectiveness_score == 0.8
    assert 0 <= adaptation.effectiveness_score <= 1
    print("✓ PersonalityAdaptation test passed")


def test_agent_memory_serialization():
    """Test AgentMemory to_dict and from_dict round trip"""
    # Create a complete memory object
    original_memory = AgentMemory(
        memory_id="therapy_session_client456",
        client_id="client456",
        conversation_context=ConversationContext(
            ongoing_topics=["anxiety", "relationships"],
            therapeutic_goals=["improve communication"],
            total_sessions=3
        ),
        therapeutic_profile=TherapeuticProfile(
            communication_style="supportive",
            language_preference="es",
            preferred_approaches=["DBT"]
        )
    )
    
    # Add a session summary
    summary = SessionSummary(
        session_id="session789",
        duration_seconds=2400,
        key_topics=["communication"],
        emotional_state=["hopeful"],
        therapeutic_progress="Good progress on communication skills"
    )
    original_memory.conversation_context.session_history.append(summary)
    
    # Serialize to dict
    memory_dict = original_memory.to_dict()
    
    # Verify dict structure
    assert memory_dict['client_id'] == "client456"
    assert memory_dict['memory_id'] == "therapy_session_client456"
    assert len(memory_dict['conversation_context']['session_history']) == 1
    assert memory_dict['therapeutic_profile']['language_preference'] == "es"
    
    # Deserialize from dict
    restored_memory = AgentMemory.from_dict(memory_dict)
    
    # Verify restored object
    assert restored_memory.client_id == original_memory.client_id
    assert restored_memory.memory_id == original_memory.memory_id
    assert len(restored_memory.conversation_context.session_history) == 1
    assert restored_memory.therapeutic_profile.language_preference == "es"
    assert restored_memory.conversation_context.total_sessions == 3
    
    print("✓ AgentMemory serialization round trip test passed")


def test_agent_memory_json_serialization():
    """Test AgentMemory JSON serialization"""
    memory = AgentMemory(
        memory_id="therapy_session_client789",
        client_id="client789",
        conversation_context=ConversationContext(
            ongoing_topics=["stress management"],
            therapeutic_goals=["reduce anxiety"]
        ),
        therapeutic_profile=TherapeuticProfile(
            language_preference="fr"
        )
    )
    
    # Convert to dict and then to JSON
    memory_dict = memory.to_dict()
    json_str = json.dumps(memory_dict)
    
    # Verify JSON is valid
    assert isinstance(json_str, str)
    assert len(json_str) > 0
    
    # Parse back from JSON
    parsed_dict = json.loads(json_str)
    restored_memory = AgentMemory.from_dict(parsed_dict)
    
    assert restored_memory.client_id == "client789"
    assert restored_memory.therapeutic_profile.language_preference == "fr"
    
    print("✓ AgentMemory JSON serialization test passed")


def test_memory_size_validation():
    """Test memory size stays within reasonable limits"""
    from config.agentcore_config import validate_memory_size
    
    # Create a small memory
    small_memory = AgentMemory(
        memory_id="therapy_session_small",
        client_id="small_client",
        conversation_context=ConversationContext(),
        therapeutic_profile=TherapeuticProfile()
    )
    
    small_dict = small_memory.to_dict()
    assert validate_memory_size(small_dict) is True
    
    print("✓ Memory size validation test passed")


def test_complete_memory_workflow():
    """Test a complete memory workflow"""
    # 1. Create initial memory
    memory = AgentMemory(
        memory_id="therapy_session_workflow",
        client_id="workflow_client",
        conversation_context=ConversationContext(),
        therapeutic_profile=TherapeuticProfile(
            language_preference="en"
        )
    )
    
    # 2. Add session summaries over time
    for i in range(5):
        summary = SessionSummary(
            session_id=f"session{i}",
            duration_seconds=1800 + (i * 300),
            key_topics=["anxiety", "coping"],
            emotional_state=["improving"],
            therapeutic_progress=f"Session {i+1} completed successfully"
        )
        memory.conversation_context.session_history.append(summary)
        memory.conversation_context.total_sessions += 1
    
    # 3. Add progress notes
    note = ProgressNote(
        note_id="note_workflow",
        content="Client showing consistent improvement",
        category="progress",
        importance=5
    )
    memory.conversation_context.progress_notes.append(note)
    
    # 4. Update therapeutic profile
    memory.therapeutic_profile.preferred_approaches.append("CBT")
    memory.therapeutic_profile.successful_interventions.append("breathing exercises")
    
    # 5. Add personality adaptation
    adaptation = PersonalityAdaptation(
        adaptation_id="adapt_workflow",
        adaptation_type="pacing",
        description="Adjusted conversation pacing",
        effectiveness_score=0.85
    )
    memory.conversation_context.personality_adaptations.append(adaptation)
    
    # 6. Verify final state
    assert memory.conversation_context.total_sessions == 5
    assert len(memory.conversation_context.session_history) == 5
    assert len(memory.conversation_context.progress_notes) == 1
    assert len(memory.therapeutic_profile.preferred_approaches) == 1
    assert len(memory.conversation_context.personality_adaptations) == 1
    
    # 7. Serialize and deserialize
    memory_dict = memory.to_dict()
    restored = AgentMemory.from_dict(memory_dict)
    
    assert restored.conversation_context.total_sessions == 5
    assert len(restored.conversation_context.session_history) == 5
    
    print("✓ Complete memory workflow test passed")


if __name__ == "__main__":
    print("\n🧪 Running AgentCore Memory Standalone Tests\n")
    
    test_agent_memory_creation()
    test_session_summary_creation()
    test_conversation_context_with_history()
    test_therapeutic_profile()
    test_retention_policy()
    test_progress_note()
    test_personality_adaptation()
    test_agent_memory_serialization()
    test_agent_memory_json_serialization()
    test_memory_size_validation()
    test_complete_memory_workflow()
    
    print("\n✅ All AgentCore Memory tests passed!\n")
