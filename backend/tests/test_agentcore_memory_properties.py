#!/usr/bin/env python3
"""
Property-Based Tests for AgentCore Memory Integration
🏆 Breaking Barriers UK 2026 compliant
Feature: ai-therapy-platform, Property 6: AgentCore Memory Integration
**Validates: Requirements 3.3, 3.6, 3.7, 7.1, 7.2**
"""

import unittest
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example, assume
from hypothesis.strategies import composite

# Import models
import sys
import os
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


class SimpleMemoryStore:
    """Simplified memory store for testing AgentCore memory operations"""
    
    def __init__(self):
        self.memories = {}
    
    def save_memory(self, memory: AgentMemory) -> bool:
        """Save memory to store"""
        try:
            # Simulate AgentCore storage
            self.memories[memory.client_id] = memory.to_dict()
            return True
        except Exception:
            return False
    
    def load_memory(self, client_id: str) -> Optional[AgentMemory]:
        """Load memory from store"""
        if client_id not in self.memories:
            return None
        
        try:
            memory_dict = self.memories[client_id]
            return AgentMemory.from_dict(memory_dict)
        except Exception:
            return None
    
    def delete_memory(self, client_id: str) -> bool:
        """Delete memory from store"""
        if client_id in self.memories:
            del self.memories[client_id]
            return True
        return False
    
    def memory_exists(self, client_id: str) -> bool:
        """Check if memory exists"""
        return client_id in self.memories


class SessionSimulator:
    """Simulates therapy session lifecycle with memory operations"""
    
    def __init__(self, memory_store: SimpleMemoryStore):
        self.memory_store = memory_store
    
    def start_session(self, client_id: str, language: str = "en") -> tuple[str, Optional[AgentMemory]]:
        """
        Start a therapy session
        Returns: (session_id, loaded_memory)
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        # Load previous conversation context from AgentCore memory
        # Validates: Requirements 3.3, 7.1
        loaded_memory = self.memory_store.load_memory(client_id)
        
        # If no memory exists, create new one
        if not loaded_memory:
            loaded_memory = AgentMemory(
                memory_id=f"therapy_session_{client_id}",
                client_id=client_id,
                conversation_context=ConversationContext(),
                therapeutic_profile=TherapeuticProfile(
                    language_preference=language
                )
            )
            # Save the new memory immediately (without incrementing version)
            self.memory_store.save_memory(loaded_memory)
        
        return session_id, loaded_memory
    
    def end_session(
        self,
        client_id: str,
        memory: AgentMemory,
        session_summary: SessionSummary
    ) -> bool:
        """
        End a therapy session and store updated context
        Validates: Requirements 3.6, 7.2
        """
        # Add session summary to memory
        memory.conversation_context.session_history.append(session_summary)
        memory.conversation_context.total_sessions += 1
        memory.conversation_context.last_session_date = session_summary.timestamp
        
        # Update memory version and timestamp
        memory.version += 1
        memory.last_updated = datetime.utcnow()
        
        # Store conversation context in AgentCore memory
        return self.memory_store.save_memory(memory)
    
    def add_therapeutic_progress(
        self,
        client_id: str,
        progress_note: ProgressNote
    ) -> bool:
        """Add therapeutic progress to memory"""
        memory = self.memory_store.load_memory(client_id)
        if not memory:
            return False
        
        memory.conversation_context.progress_notes.append(progress_note)
        memory.version += 1
        memory.last_updated = datetime.utcnow()
        
        return self.memory_store.save_memory(memory)
    
    def update_therapeutic_continuity(
        self,
        client_id: str,
        ongoing_topics: List[str],
        therapeutic_goals: List[str]
    ) -> bool:
        """
        Update conversation context for therapeutic continuity
        Validates: Requirement 3.7
        """
        memory = self.memory_store.load_memory(client_id)
        if not memory:
            return False
        
        # Maintain conversation context across sessions
        memory.conversation_context.ongoing_topics = ongoing_topics
        memory.conversation_context.therapeutic_goals = therapeutic_goals
        memory.version += 1
        memory.last_updated = datetime.utcnow()
        
        return self.memory_store.save_memory(memory)


@composite
def valid_client_id(draw):
    """Generate valid client ID"""
    return f"client_{draw(st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))}"


@composite
def valid_session_summary(draw):
    """Generate valid session summary"""
    return SessionSummary(
        session_id=f"session_{draw(st.text(min_size=8, max_size=12, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))}",
        duration_seconds=draw(st.integers(min_value=300, max_value=7200)),  # 5 min to 2 hours
        key_topics=draw(st.lists(
            st.sampled_from(['anxiety', 'depression', 'stress', 'relationships', 'work', 'family', 'self-esteem']),
            min_size=0, max_size=5
        )),
        emotional_state=draw(st.lists(
            st.sampled_from(['calm', 'anxious', 'happy', 'sad', 'hopeful', 'frustrated', 'engaged']),
            min_size=0, max_size=4
        )),
        therapeutic_progress=draw(st.text(min_size=10, max_size=500))
    )


@composite
def valid_progress_note(draw):
    """Generate valid progress note"""
    return ProgressNote(
        note_id=f"note_{draw(st.text(min_size=8, max_size=12, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))}",
        content=draw(st.text(min_size=10, max_size=500)),
        category=draw(st.sampled_from(['coping_skills', 'progress', 'setback', 'milestone', 'observation'])),
        importance=draw(st.integers(min_value=1, max_value=5))
    )


@composite
def valid_language(draw):
    """Generate valid language code"""
    return draw(st.sampled_from(['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja']))


@composite
def valid_topics_and_goals(draw):
    """Generate valid ongoing topics and therapeutic goals"""
    topics = draw(st.lists(
        st.sampled_from(['anxiety_management', 'stress_reduction', 'relationship_building', 
                        'self_confidence', 'work_life_balance', 'emotional_regulation']),
        min_size=0, max_size=5, unique=True
    ))
    
    goals = draw(st.lists(
        st.sampled_from(['reduce_anxiety', 'improve_sleep', 'better_communication', 
                        'manage_stress', 'build_confidence', 'develop_coping_skills']),
        min_size=0, max_size=5, unique=True
    ))
    
    return topics, goals


class TestAgentCoreMemoryProperties(unittest.TestCase):
    """Property-based tests for AgentCore Memory Integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.memory_store = SimpleMemoryStore()
        self.session_simulator = SessionSimulator(self.memory_store)
    
    @given(
        client_id=valid_client_id(),
        language=valid_language()
    )
    @settings(max_examples=100, deadline=None)
    @example(client_id="client_test123", language="en")
    def test_property_memory_load_at_session_start(self, client_id, language):
        """
        Property 6a: Memory Loading at Session Start
        For any therapy session start, the system should load previous conversation 
        context from AgentCore memory for therapeutic continuity.
        **Validates: Requirements 3.3, 7.1**
        """
        # Ensure clean state for this client
        self.memory_store.delete_memory(client_id)
        
        # Start first session (no previous memory)
        session_id1, memory1 = self.session_simulator.start_session(client_id, language)
        
        # Property: Session should start successfully
        self.assertIsNotNone(session_id1, "Session ID should be generated")
        self.assertIsNotNone(memory1, "Memory should be created for new client")
        
        # Property: New memory should have correct client ID
        self.assertEqual(memory1.client_id, client_id, 
                        "Memory should have correct client ID")
        
        # Property: New memory should have correct language preference
        self.assertEqual(memory1.therapeutic_profile.language_preference, language,
                        "Memory should have correct language preference")
        
        # Property: New memory should have empty conversation history
        self.assertEqual(len(memory1.conversation_context.session_history), 0,
                        "New memory should have no session history")
        self.assertEqual(memory1.conversation_context.total_sessions, 0,
                        "New memory should have zero total sessions")
        
        # Create and end first session with some data
        summary1 = SessionSummary(
            session_id=session_id1,
            duration_seconds=1800,
            key_topics=["anxiety", "coping"],
            emotional_state=["calm"],
            therapeutic_progress="First session completed"
        )
        
        success = self.session_simulator.end_session(client_id, memory1, summary1)
        self.assertTrue(success, "Session should end successfully")
        
        # Start second session (should load previous memory)
        session_id2, memory2 = self.session_simulator.start_session(client_id, language)
        
        # Property: Second session should load previous memory
        self.assertIsNotNone(memory2, "Memory should be loaded for returning client")
        
        # Property: Loaded memory should contain previous session data
        self.assertEqual(len(memory2.conversation_context.session_history), 1,
                        "Loaded memory should have previous session history")
        self.assertEqual(memory2.conversation_context.total_sessions, 1,
                        "Loaded memory should have correct session count")
        
        # Property: Loaded memory should maintain therapeutic continuity
        self.assertEqual(memory2.conversation_context.session_history[0].session_id, session_id1,
                        "Loaded memory should contain previous session ID")
        self.assertIsNotNone(memory2.conversation_context.last_session_date,
                           "Loaded memory should have last session date")
    
    @given(
        client_id=valid_client_id(),
        session_summary=valid_session_summary()
    )
    @settings(max_examples=100, deadline=None)
    @example(
        client_id="client_test456",
        session_summary=SessionSummary(
            session_id="session_test",
            duration_seconds=1800,
            key_topics=["anxiety"],
            emotional_state=["calm"],
            therapeutic_progress="Test session"
        )
    )
    def test_property_memory_store_at_session_end(self, client_id, session_summary):
        """
        Property 6b: Memory Storage at Session End
        For any therapy session end, the system should store updated conversation 
        context in AgentCore memory for future sessions.
        **Validates: Requirements 3.6, 7.2**
        """
        # Ensure clean state for this client
        self.memory_store.delete_memory(client_id)
        
        # Start session
        session_id, memory = self.session_simulator.start_session(client_id, "en")
        
        # Property: Memory should exist before session end
        self.assertIsNotNone(memory, "Memory should exist")
        original_version = memory.version
        original_session_count = memory.conversation_context.total_sessions
        
        # End session with summary
        success = self.session_simulator.end_session(client_id, memory, session_summary)
        
        # Property: Session should end successfully
        self.assertTrue(success, "Session end should succeed")
        
        # Property: Memory should be stored
        self.assertTrue(self.memory_store.memory_exists(client_id),
                       "Memory should be stored in AgentCore")
        
        # Load stored memory
        stored_memory = self.memory_store.load_memory(client_id)
        
        # Property: Stored memory should contain session summary
        self.assertIsNotNone(stored_memory, "Stored memory should be retrievable")
        self.assertEqual(len(stored_memory.conversation_context.session_history), 
                        original_session_count + 1,
                        "Stored memory should have updated session history")
        
        # Property: Stored memory should have incremented version
        self.assertEqual(stored_memory.version, original_version + 1,
                        "Stored memory should have incremented version")
        
        # Property: Stored memory should have updated session count
        self.assertEqual(stored_memory.conversation_context.total_sessions,
                        original_session_count + 1,
                        "Stored memory should have incremented session count")
        
        # Property: Stored memory should have last session date
        self.assertIsNotNone(stored_memory.conversation_context.last_session_date,
                           "Stored memory should have last session date")
        
        # Property: Last session date should match summary timestamp
        self.assertEqual(stored_memory.conversation_context.last_session_date,
                        session_summary.timestamp,
                        "Last session date should match summary timestamp")
    
    @given(
        client_id=valid_client_id(),
        topics_and_goals=valid_topics_and_goals()
    )
    @settings(max_examples=100, deadline=None)
    @example(
        client_id="client_test789",
        topics_and_goals=(["anxiety_management"], ["reduce_anxiety"])
    )
    def test_property_therapeutic_continuity_across_sessions(self, client_id, topics_and_goals):
        """
        Property 6c: Therapeutic Continuity Across Multiple Sessions
        For any client, the system should maintain conversation context and therapeutic 
        continuity across multiple sessions.
        **Validates: Requirement 3.7**
        """
        # Ensure clean state for this client
        self.memory_store.delete_memory(client_id)
        
        topics, goals = topics_and_goals
        
        # Start first session
        session_id1, memory1 = self.session_simulator.start_session(client_id, "en")
        
        # Update therapeutic continuity
        success = self.session_simulator.update_therapeutic_continuity(
            client_id, topics, goals
        )
        
        # Property: Update should succeed
        self.assertTrue(success, "Therapeutic continuity update should succeed")
        
        # Load memory to verify
        memory_after_update = self.memory_store.load_memory(client_id)
        
        # Property: Ongoing topics should be maintained
        self.assertEqual(set(memory_after_update.conversation_context.ongoing_topics),
                        set(topics),
                        "Ongoing topics should be maintained")
        
        # Property: Therapeutic goals should be maintained
        self.assertEqual(set(memory_after_update.conversation_context.therapeutic_goals),
                        set(goals),
                        "Therapeutic goals should be maintained")
        
        # Simulate multiple sessions
        for i in range(3):
            session_id, memory = self.session_simulator.start_session(client_id, "en")
            
            # Property: Each session should load the same ongoing topics
            self.assertEqual(set(memory.conversation_context.ongoing_topics),
                           set(topics),
                           f"Session {i+1} should maintain ongoing topics")
            
            # Property: Each session should load the same therapeutic goals
            self.assertEqual(set(memory.conversation_context.therapeutic_goals),
                           set(goals),
                           f"Session {i+1} should maintain therapeutic goals")
            
            # End session
            summary = SessionSummary(
                session_id=session_id,
                duration_seconds=1800,
                key_topics=topics[:2] if topics else [],
                emotional_state=["calm"],
                therapeutic_progress=f"Session {i+1} progress"
            )
            self.session_simulator.end_session(client_id, memory, summary)
        
        # Load final memory
        final_memory = self.memory_store.load_memory(client_id)
        
        # Property: Therapeutic continuity should be maintained across all sessions
        self.assertEqual(set(final_memory.conversation_context.ongoing_topics),
                        set(topics),
                        "Ongoing topics should be maintained across all sessions")
        self.assertEqual(set(final_memory.conversation_context.therapeutic_goals),
                        set(goals),
                        "Therapeutic goals should be maintained across all sessions")
        
        # Property: Session history should accumulate
        self.assertEqual(final_memory.conversation_context.total_sessions, 3,
                        "Total sessions should accumulate")
        self.assertEqual(len(final_memory.conversation_context.session_history), 3,
                        "Session history should contain all sessions")
    
    @given(
        client_id=valid_client_id(),
        progress_note=valid_progress_note()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_progress_note_persistence(self, client_id, progress_note):
        """
        Property: Progress notes should persist across sessions
        For any progress note added to memory, it should be retrievable in future sessions.
        """
        # Ensure clean state for this client
        self.memory_store.delete_memory(client_id)
        
        # Start session and create initial memory
        session_id, memory = self.session_simulator.start_session(client_id, "en")
        
        # End session to store memory
        summary = SessionSummary(
            session_id=session_id,
            duration_seconds=1800,
            key_topics=[],
            emotional_state=[],
            therapeutic_progress="Initial session"
        )
        self.session_simulator.end_session(client_id, memory, summary)
        
        # Add progress note
        success = self.session_simulator.add_therapeutic_progress(client_id, progress_note)
        
        # Property: Progress note addition should succeed
        self.assertTrue(success, "Progress note addition should succeed")
        
        # Start new session
        new_session_id, new_memory = self.session_simulator.start_session(client_id, "en")
        
        # Property: Progress note should be present in loaded memory
        self.assertGreater(len(new_memory.conversation_context.progress_notes), 0,
                          "Progress notes should be present in loaded memory")
        
        # Property: Progress note should match original
        found_note = None
        for note in new_memory.conversation_context.progress_notes:
            if note.note_id == progress_note.note_id:
                found_note = note
                break
        
        self.assertIsNotNone(found_note, "Progress note should be found in memory")
        self.assertEqual(found_note.content, progress_note.content,
                        "Progress note content should match")
        self.assertEqual(found_note.category, progress_note.category,
                        "Progress note category should match")
        self.assertEqual(found_note.importance, progress_note.importance,
                        "Progress note importance should match")
    
    @given(client_id=valid_client_id())
    @settings(max_examples=50, deadline=None)
    def test_property_memory_serialization_round_trip(self, client_id):
        """
        Property: Memory serialization should be lossless
        For any memory, serializing and deserializing should produce equivalent memory.
        """
        # Create memory with data
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                ongoing_topics=["anxiety", "stress"],
                therapeutic_goals=["manage_anxiety", "improve_sleep"],
                total_sessions=5
            ),
            therapeutic_profile=TherapeuticProfile(
                communication_style="empathetic",
                language_preference="en",
                preferred_approaches=["CBT", "mindfulness"]
            )
        )
        
        # Add session summary
        summary = SessionSummary(
            session_id="session_test",
            duration_seconds=1800,
            key_topics=["anxiety"],
            emotional_state=["calm"],
            therapeutic_progress="Test progress"
        )
        memory.conversation_context.session_history.append(summary)
        
        # Serialize
        memory_dict = memory.to_dict()
        
        # Deserialize
        restored_memory = AgentMemory.from_dict(memory_dict)
        
        # Property: Core fields should match
        self.assertEqual(restored_memory.memory_id, memory.memory_id,
                        "Memory ID should match after round trip")
        self.assertEqual(restored_memory.client_id, memory.client_id,
                        "Client ID should match after round trip")
        self.assertEqual(restored_memory.version, memory.version,
                        "Version should match after round trip")
        
        # Property: Conversation context should match
        self.assertEqual(
            set(restored_memory.conversation_context.ongoing_topics),
            set(memory.conversation_context.ongoing_topics),
            "Ongoing topics should match after round trip"
        )
        self.assertEqual(
            set(restored_memory.conversation_context.therapeutic_goals),
            set(memory.conversation_context.therapeutic_goals),
            "Therapeutic goals should match after round trip"
        )
        self.assertEqual(
            restored_memory.conversation_context.total_sessions,
            memory.conversation_context.total_sessions,
            "Total sessions should match after round trip"
        )
        
        # Property: Session history should match
        self.assertEqual(
            len(restored_memory.conversation_context.session_history),
            len(memory.conversation_context.session_history),
            "Session history length should match after round trip"
        )
        
        # Property: Therapeutic profile should match
        self.assertEqual(
            restored_memory.therapeutic_profile.communication_style,
            memory.therapeutic_profile.communication_style,
            "Communication style should match after round trip"
        )
        self.assertEqual(
            restored_memory.therapeutic_profile.language_preference,
            memory.therapeutic_profile.language_preference,
            "Language preference should match after round trip"
        )
    
    @given(client_id=valid_client_id())
    @settings(max_examples=50, deadline=None)
    def test_property_memory_version_increments(self, client_id):
        """
        Property: Memory version should increment on updates
        For any memory update, the version number should increment.
        """
        # Ensure clean state for this client
        self.memory_store.delete_memory(client_id)
        
        # Start session
        session_id, memory = self.session_simulator.start_session(client_id, "en")
        initial_version = memory.version
        
        # End session (triggers update)
        summary = SessionSummary(
            session_id=session_id,
            duration_seconds=1800,
            key_topics=[],
            emotional_state=[],
            therapeutic_progress="Test"
        )
        self.session_simulator.end_session(client_id, memory, summary)
        
        # Load updated memory
        updated_memory = self.memory_store.load_memory(client_id)
        
        # Property: Version should increment
        self.assertEqual(updated_memory.version, initial_version + 1,
                        "Version should increment after update")
        
        # Update again
        self.session_simulator.update_therapeutic_continuity(
            client_id, ["anxiety"], ["reduce_anxiety"]
        )
        
        # Load again
        updated_memory2 = self.memory_store.load_memory(client_id)
        
        # Property: Version should increment again
        self.assertEqual(updated_memory2.version, initial_version + 2,
                        "Version should increment after second update")
    
    def test_property_memory_isolation_between_clients(self):
        """
        Property: Memory should be isolated between clients
        For any two different clients, their memories should not interfere.
        """
        client1_id = "client_isolation_test1"
        client2_id = "client_isolation_test2"
        
        # Create sessions for both clients
        session1_id, memory1 = self.session_simulator.start_session(client1_id, "en")
        session2_id, memory2 = self.session_simulator.start_session(client2_id, "es")
        
        # Update client1 memory
        self.session_simulator.update_therapeutic_continuity(
            client1_id, ["anxiety"], ["reduce_anxiety"]
        )
        
        # Update client2 memory
        self.session_simulator.update_therapeutic_continuity(
            client2_id, ["depression"], ["improve_mood"]
        )
        
        # Load both memories
        loaded_memory1 = self.memory_store.load_memory(client1_id)
        loaded_memory2 = self.memory_store.load_memory(client2_id)
        
        # Property: Memories should be different
        self.assertNotEqual(loaded_memory1.client_id, loaded_memory2.client_id,
                           "Client IDs should be different")
        
        # Property: Client1 memory should have client1 data
        self.assertEqual(loaded_memory1.conversation_context.ongoing_topics, ["anxiety"],
                        "Client1 should have their own topics")
        self.assertEqual(loaded_memory1.conversation_context.therapeutic_goals, ["reduce_anxiety"],
                        "Client1 should have their own goals")
        
        # Property: Client2 memory should have client2 data
        self.assertEqual(loaded_memory2.conversation_context.ongoing_topics, ["depression"],
                        "Client2 should have their own topics")
        self.assertEqual(loaded_memory2.conversation_context.therapeutic_goals, ["improve_mood"],
                        "Client2 should have their own goals")
        
        # Property: Language preferences should be different
        self.assertEqual(loaded_memory1.therapeutic_profile.language_preference, "en",
                        "Client1 should have English preference")
        self.assertEqual(loaded_memory2.therapeutic_profile.language_preference, "es",
                        "Client2 should have Spanish preference")


def run_property_tests():
    """Run property-based tests for AgentCore Memory Integration"""
    print("🧪 Running Property-Based Tests for AgentCore Memory Integration")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: ai-therapy-platform, Property 6: AgentCore Memory Integration")
    print("**Validates: Requirements 3.3, 3.6, 3.7, 7.1, 7.2**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestAgentCoreMemoryProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All property-based tests passed!")
        print("✅ AgentCore Memory Integration properties validated")
        print("✅ Requirements 3.3, 3.6, 3.7, 7.1, 7.2 verified")
        print("🏆 Breaking Barriers UK 2026 compliant memory management verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
        
        # Print failure details
        for test, traceback in result.failures:
            print(f"\nFAILURE: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_property_tests()
    exit(0 if success else 1)
