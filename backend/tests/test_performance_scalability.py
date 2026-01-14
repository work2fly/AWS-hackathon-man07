"""
Performance and Scalability Tests
🏆 Breaking Barriers UK 2026 compliant

Task 8.4: Optimize performance and scalability
- Optimize audio processing latency and throughput
- Improve memory usage and conversation context efficiency
- Scale testing for concurrent session handling
- Optimize AI model inference and response times

**Validates: Requirements 2.2, 8.4**
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, MagicMock
import json

import sys
import os
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.audio_streaming_service import AudioStreamingService
from src.services.agentcore_memory_service import AgentCoreMemoryService
from src.services.language_processing_service import LanguageProcessingService
from src.services.voice_synthesis_service import VoiceSynthesisService, VoiceSynthesisRequest, EmotionalTone
from src.models.agent_memory import SessionSummary


class TestAudioProcessingPerformance:
    """Test audio processing latency and throughput"""
    
    def test_audio_chunk_processing_latency(self):
        """
        Test that audio chunk processing meets latency requirements
        
        **Validates: Requirements 2.2**
        """
        service = AudioStreamingService()
        session_id = "perf-audio-session"
        
        # Initialize stream
        service.initialize_stream(session_id)
        
        # Test multiple chunks
        latencies = []
        for i in range(10):
            chunk_data = {
                'chunk_id': f'chunk-{i}',
                'session_id': session_id,
                'sequence_number': i,
                'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
                'format': 'opus',
                'sample_rate': 16000,
                'channels': 1,
                'timestamp': time.time(),
                'duration_ms': 100.0
            }
            
            start_time = time.time()
            service.process_audio_chunk(session_id, chunk_data)
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            latencies.append(latency)
        
        # Calculate statistics
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # Assert performance requirements
        assert avg_latency < 50, f"Average latency {avg_latency:.2f}ms exceeds 50ms target"
        assert max_latency < 100, f"Max latency {max_latency:.2f}ms exceeds 100ms target"
        
        print(f"✅ Audio processing latency: avg={avg_latency:.2f}ms, max={max_latency:.2f}ms")
    
    def test_audio_throughput(self):
        """
        Test audio processing throughput
        
        **Validates: Requirements 2.2, 8.4**
        """
        service = AudioStreamingService()
        session_id = "throughput-session"
        
        # Initialize stream
        service.initialize_stream(session_id)
        
        # Process many chunks
        num_chunks = 100
        start_time = time.time()
        
        for i in range(num_chunks):
            chunk_data = {
                'chunk_id': f'chunk-{i}',
                'session_id': session_id,
                'sequence_number': i,
                'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
                'format': 'opus',
                'sample_rate': 16000,
                'channels': 1,
                'timestamp': time.time(),
                'duration_ms': 100.0
            }
            service.process_audio_chunk(session_id, chunk_data)
        
        elapsed = time.time() - start_time
        throughput = num_chunks / elapsed
        
        # Assert throughput requirement (should handle at least 10 chunks/second)
        assert throughput >= 10, f"Throughput {throughput:.2f} chunks/s below 10 chunks/s target"
        
        print(f"✅ Audio throughput: {throughput:.2f} chunks/second")


class TestMemoryEfficiency:
    """Test memory usage and conversation context efficiency"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    def test_memory_optimization_efficiency(self, mock_bedrock_client):
        """
        Test memory optimization reduces size efficiently
        
        **Validates: Requirements 3.6, 7.6**
        """
        service = AgentCoreMemoryService()
        client_id = "memory-opt-client"
        
        # Create memory with large history
        from src.models.agent_memory import AgentMemory, ConversationContext, TherapeuticProfile
        
        session_history = [
            SessionSummary(
                session_id=f"session-{i:03d}",
                duration_seconds=1800,
                key_topics=["topic1", "topic2"],
                emotional_state=["calm"],
                therapeutic_progress="Progress"
            )
            for i in range(100)
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
        
        # Measure optimization
        original_size = len(json.dumps(memory.to_dict()))
        
        optimized = service._optimize_memory(memory)
        optimized_size = len(json.dumps(optimized.to_dict()))
        
        # Calculate reduction
        reduction_percent = ((original_size - optimized_size) / original_size) * 100
        
        # Assert significant reduction
        assert optimized_size < original_size, "Optimization should reduce size"
        assert reduction_percent > 20, f"Optimization only reduced size by {reduction_percent:.1f}%"
        
        print(f"✅ Memory optimization: {reduction_percent:.1f}% size reduction")
    
    def test_context_serialization_performance(self, mock_bedrock_client):
        """
        Test context serialization performance
        
        **Validates: Requirements 3.6, 3.7**
        """
        service = AgentCoreMemoryService()
        client_id = "serialize-perf-client"
        
        # Create memory with rich context
        from src.models.agent_memory import AgentMemory, ConversationContext, TherapeuticProfile
        
        memory = AgentMemory(
            memory_id=f"therapy_session_{client_id}",
            client_id=client_id,
            conversation_context=ConversationContext(
                ongoing_topics=["anxiety", "stress", "sleep"],
                therapeutic_goals=["manage anxiety", "improve sleep"],
                total_sessions=50
            ),
            therapeutic_profile=TherapeuticProfile(
                communication_style="empathetic",
                preferred_approaches=["CBT", "mindfulness"]
            )
        )
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        # Measure serialization time
        start_time = time.time()
        context_string = service.serialize_context_for_prompt(client_id)
        serialization_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Assert performance requirement
        assert serialization_time < 100, f"Serialization took {serialization_time:.2f}ms, exceeds 100ms"
        assert len(context_string) > 0, "Serialized context should not be empty"
        
        print(f"✅ Context serialization: {serialization_time:.2f}ms")


class TestConcurrentSessionHandling:
    """Test concurrent session handling and scalability"""
    
    def test_concurrent_audio_sessions(self):
        """
        Test handling multiple concurrent audio sessions
        
        **Validates: Requirements 2.6, 8.4**
        """
        service = AudioStreamingService()
        num_sessions = 10
        
        def process_session(session_id):
            """Process a single session"""
            # Initialize stream
            result = service.initialize_stream(session_id)
            assert result['success'] is True
            
            # Process chunks
            for i in range(5):
                chunk_data = {
                    'chunk_id': f'chunk-{i}',
                    'session_id': session_id,
                    'sequence_number': i,
                    'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
                    'format': 'opus',
                    'sample_rate': 16000,
                    'channels': 1,
                    'timestamp': time.time(),
                    'duration_ms': 100.0
                }
                service.process_audio_chunk(session_id, chunk_data)
            
            return session_id
        
        # Process sessions concurrently
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_sessions) as executor:
            futures = [
                executor.submit(process_session, f"concurrent-session-{i}")
                for i in range(num_sessions)
            ]
            
            completed = 0
            for future in as_completed(futures):
                session_id = future.result()
                completed += 1
        
        elapsed = time.time() - start_time
        
        # Assert all sessions completed
        assert completed == num_sessions, f"Only {completed}/{num_sessions} sessions completed"
        
        # Assert reasonable completion time
        assert elapsed < 10, f"Concurrent processing took {elapsed:.2f}s, exceeds 10s"
        
        print(f"✅ Concurrent sessions: {num_sessions} sessions in {elapsed:.2f}s")
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    def test_concurrent_memory_operations(self, mock_bedrock_client):
        """
        Test concurrent memory operations
        
        **Validates: Requirements 3.3, 8.4**
        """
        service = AgentCoreMemoryService()
        num_clients = 10
        
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        def create_and_update_memory(client_id):
            """Create and update memory for a client"""
            # Create memory
            memory = service.create_memory(client_id)
            
            # Add session summary
            memory_data = memory.to_dict()
            mock_bedrock_client.get_memory.return_value = {
                'memoryContent': json.dumps(memory_data)
            }
            
            session_summary = SessionSummary(
                session_id=f"session-{client_id}",
                duration_seconds=1800,
                key_topics=["topic"],
                emotional_state=["calm"],
                therapeutic_progress="Progress"
            )
            
            updated = service.add_session_summary(client_id, session_summary)
            return updated is not None
        
        # Process concurrently
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [
                executor.submit(create_and_update_memory, f"concurrent-client-{i}")
                for i in range(num_clients)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        elapsed = time.time() - start_time
        
        # Assert all operations succeeded
        assert all(results), "Some memory operations failed"
        assert elapsed < 5, f"Concurrent memory operations took {elapsed:.2f}s, exceeds 5s"
        
        print(f"✅ Concurrent memory operations: {num_clients} clients in {elapsed:.2f}s")


class TestAIModelInferencePerformance:
    """Test AI model inference and response times"""
    
    def test_language_detection_performance(self):
        """
        Test language detection performance
        
        **Validates: Requirements 10.1, 10.2**
        """
        service = LanguageProcessingService()
        session_id = "lang-perf-session"
        
        test_texts = [
            "Hello, how are you feeling today?",
            "Hola, ¿cómo te sientes hoy?",
            "Bonjour, comment vous sentez-vous?",
            "Hallo, wie fühlen Sie sich heute?",
            "Ciao, come ti senti oggi?"
        ]
        
        detection_times = []
        
        for text in test_texts:
            start_time = time.time()
            result = service.detect_language_realtime(session_id, text, None)
            detection_time = (time.time() - start_time) * 1000  # Convert to ms
            
            detection_times.append(detection_time)
            assert result is not None
        
        avg_time = sum(detection_times) / len(detection_times)
        max_time = max(detection_times)
        
        # Assert performance requirements
        assert avg_time < 50, f"Average detection time {avg_time:.2f}ms exceeds 50ms"
        assert max_time < 100, f"Max detection time {max_time:.2f}ms exceeds 100ms"
        
        print(f"✅ Language detection: avg={avg_time:.2f}ms, max={max_time:.2f}ms")
    
    def test_voice_synthesis_performance(self):
        """
        Test voice synthesis performance
        
        **Validates: Requirements 10.3, 10.4**
        """
        service = VoiceSynthesisService()
        session_id = "voice-perf-session"
        
        test_texts = [
            "I understand how you're feeling.",
            "Let's explore that together.",
            "That's a very important insight.",
            "How does that make you feel?",
            "I'm here to support you."
        ]
        
        synthesis_times = []
        
        for text in test_texts:
            from src.services.language_processing_service import SupportedLanguage
            
            request = VoiceSynthesisRequest(
                session_id=session_id,
                text=text,
                language=SupportedLanguage.ENGLISH,
                tone=EmotionalTone.EMPATHETIC
            )
            
            start_time = time.time()
            result = service.synthesize_speech(request)
            synthesis_time = (time.time() - start_time) * 1000  # Convert to ms
            
            synthesis_times.append(synthesis_time)
            assert result is not None
        
        avg_time = sum(synthesis_times) / len(synthesis_times)
        max_time = max(synthesis_times)
        
        # Assert performance requirements
        assert avg_time < 200, f"Average synthesis time {avg_time:.2f}ms exceeds 200ms"
        assert max_time < 500, f"Max synthesis time {max_time:.2f}ms exceeds 500ms"
        
        print(f"✅ Voice synthesis: avg={avg_time:.2f}ms, max={max_time:.2f}ms")


class TestEndToEndPerformance:
    """Test end-to-end performance"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock bedrock client"""
        with patch('boto3.client') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    def test_complete_session_performance(self, mock_bedrock_client):
        """
        Test complete session performance from start to finish
        
        **Validates: Requirements 2.2, 8.4**
        """
        # Initialize services
        audio_service = AudioStreamingService()
        language_service = LanguageProcessingService()
        voice_service = VoiceSynthesisService()
        memory_service = AgentCoreMemoryService()
        
        session_id = "e2e-perf-session"
        client_id = "e2e-perf-client"
        
        # Measure complete workflow
        start_time = time.time()
        
        # 1. Initialize audio stream
        audio_service.initialize_stream(session_id)
        
        # 2. Process audio chunk
        chunk_data = {
            'chunk_id': 'chunk-1',
            'session_id': session_id,
            'sequence_number': 0,
            'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
            'format': 'opus',
            'sample_rate': 16000,
            'channels': 1,
            'timestamp': time.time(),
            'duration_ms': 100.0
        }
        audio_service.process_audio_chunk(session_id, chunk_data)
        
        # 3. Detect language
        language_service.detect_language_realtime(
            session_id,
            "I'm feeling anxious today.",
            None
        )
        
        # 4. Synthesize response
        from src.services.language_processing_service import SupportedLanguage
        
        request = VoiceSynthesisRequest(
            session_id=session_id,
            text="I understand. Let's talk about that.",
            language=SupportedLanguage.ENGLISH,
            tone=EmotionalTone.EMPATHETIC
        )
        voice_service.synthesize_speech(request)
        
        # 5. Update memory
        mock_bedrock_client.put_memory.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        memory = memory_service.create_memory(client_id)
        
        memory_data = memory.to_dict()
        mock_bedrock_client.get_memory.return_value = {
            'memoryContent': json.dumps(memory_data)
        }
        
        session_summary = SessionSummary(
            session_id=session_id,
            duration_seconds=1800,
            key_topics=["anxiety"],
            emotional_state=["anxious"],
            therapeutic_progress="Session completed"
        )
        memory_service.add_session_summary(client_id, session_summary)
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Assert end-to-end performance
        assert total_time < 500, f"End-to-end processing took {total_time:.2f}ms, exceeds 500ms"
        
        print(f"✅ End-to-end performance: {total_time:.2f}ms")
    
    def test_sustained_load_performance(self, mock_bedrock_client):
        """
        Test performance under sustained load
        
        **Validates: Requirements 8.4**
        """
        audio_service = AudioStreamingService()
        num_iterations = 50
        
        session_id = "sustained-load-session"
        audio_service.initialize_stream(session_id)
        
        processing_times = []
        
        for i in range(num_iterations):
            chunk_data = {
                'chunk_id': f'chunk-{i}',
                'session_id': session_id,
                'sequence_number': i,
                'audio_data': 'dGVzdCBhdWRpbyBkYXRh',
                'format': 'opus',
                'sample_rate': 16000,
                'channels': 1,
                'timestamp': time.time(),
                'duration_ms': 100.0
            }
            
            start_time = time.time()
            audio_service.process_audio_chunk(session_id, chunk_data)
            processing_time = (time.time() - start_time) * 1000
            
            processing_times.append(processing_time)
        
        # Calculate statistics
        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)
        
        # Check for performance degradation
        first_10_avg = sum(processing_times[:10]) / 10
        last_10_avg = sum(processing_times[-10:]) / 10
        degradation = ((last_10_avg - first_10_avg) / first_10_avg) * 100
        
        # Assert no significant degradation
        assert degradation < 50, f"Performance degraded by {degradation:.1f}% under sustained load"
        assert avg_time < 100, f"Average time {avg_time:.2f}ms exceeds 100ms under sustained load"
        
        print(f"✅ Sustained load: avg={avg_time:.2f}ms, degradation={degradation:.1f}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
