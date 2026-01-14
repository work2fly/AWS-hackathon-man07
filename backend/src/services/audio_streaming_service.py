"""
Audio Streaming Service for AI Therapy Platform
Handles real-time audio streaming protocols, buffering, and quality monitoring
🏆 Breaking Barriers UK 2026 compliant
"""

import base64
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AudioFormat(str, Enum):
    """Supported audio formats"""
    PCM_16BIT = "pcm_16bit"
    OPUS = "opus"
    MP3 = "mp3"
    WAV = "wav"


class AudioQuality(str, Enum):
    """Audio quality presets"""
    LOW = "low"          # 8kHz, optimized for poor connections
    MEDIUM = "medium"    # 16kHz, balanced quality/bandwidth
    HIGH = "high"        # 24kHz, high quality
    ULTRA = "ultra"      # 48kHz, maximum quality


class StreamingState(str, Enum):
    """Audio streaming state"""
    IDLE = "idle"
    BUFFERING = "buffering"
    STREAMING = "streaming"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class AudioChunk:
    """Represents a single audio chunk"""
    chunk_id: str
    session_id: str
    sequence_number: int
    audio_data: bytes
    format: AudioFormat
    sample_rate: int
    channels: int
    timestamp: float
    duration_ms: float
    
    def to_websocket_message(self) -> Dict[str, Any]:
        """Convert to WebSocket message format"""
        return {
            'type': 'audio_chunk',
            'chunk_id': self.chunk_id,
            'session_id': self.session_id,
            'sequence_number': self.sequence_number,
            'audio_data': base64.b64encode(self.audio_data).decode('utf-8'),
            'format': self.format.value,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'timestamp': self.timestamp,
            'duration_ms': self.duration_ms
        }
    
    @classmethod
    def from_websocket_message(cls, message: Dict[str, Any]) -> 'AudioChunk':
        """Create AudioChunk from WebSocket message"""
        return cls(
            chunk_id=message['chunk_id'],
            session_id=message['session_id'],
            sequence_number=message['sequence_number'],
            audio_data=base64.b64decode(message['audio_data']),
            format=AudioFormat(message['format']),
            sample_rate=message['sample_rate'],
            channels=message['channels'],
            timestamp=message['timestamp'],
            duration_ms=message['duration_ms']
        )


@dataclass
class AudioStreamConfig:
    """Configuration for audio streaming"""
    format: AudioFormat = AudioFormat.OPUS
    sample_rate: int = 16000  # Hz
    channels: int = 1  # Mono
    chunk_size_ms: int = 100  # Milliseconds per chunk
    buffer_size_chunks: int = 5  # Number of chunks to buffer
    max_latency_ms: float = 200.0  # Maximum acceptable latency
    quality: AudioQuality = AudioQuality.MEDIUM
    enable_adaptation: bool = True  # Enable quality adaptation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'format': self.format.value,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'chunk_size_ms': self.chunk_size_ms,
            'buffer_size_chunks': self.buffer_size_chunks,
            'max_latency_ms': self.max_latency_ms,
            'quality': self.quality.value,
            'enable_adaptation': self.enable_adaptation
        }
    
    @classmethod
    def from_quality_preset(cls, quality: AudioQuality) -> 'AudioStreamConfig':
        """Create configuration from quality preset"""
        configs = {
            AudioQuality.LOW: cls(
                format=AudioFormat.OPUS,
                sample_rate=8000,
                channels=1,
                chunk_size_ms=120,
                buffer_size_chunks=3,
                quality=AudioQuality.LOW
            ),
            AudioQuality.MEDIUM: cls(
                format=AudioFormat.OPUS,
                sample_rate=16000,
                channels=1,
                chunk_size_ms=100,
                buffer_size_chunks=5,
                quality=AudioQuality.MEDIUM
            ),
            AudioQuality.HIGH: cls(
                format=AudioFormat.OPUS,
                sample_rate=24000,
                channels=1,
                chunk_size_ms=80,
                buffer_size_chunks=7,
                quality=AudioQuality.HIGH
            ),
            AudioQuality.ULTRA: cls(
                format=AudioFormat.OPUS,
                sample_rate=48000,
                channels=2,
                chunk_size_ms=60,
                buffer_size_chunks=10,
                quality=AudioQuality.ULTRA
            )
        }
        return configs.get(quality, configs[AudioQuality.MEDIUM])


@dataclass
class StreamingMetrics:
    """Real-time streaming quality metrics"""
    session_id: str
    current_latency_ms: float = 0.0
    average_latency_ms: float = 0.0
    packet_loss_rate: float = 0.0
    jitter_ms: float = 0.0
    buffer_underruns: int = 0
    buffer_overruns: int = 0
    chunks_received: int = 0
    chunks_dropped: int = 0
    bytes_transferred: int = 0
    connection_quality: float = 1.0  # 0.0 to 1.0
    last_updated: float = 0.0
    
    def update_latency(self, latency_ms: float) -> None:
        """Update latency metrics"""
        self.current_latency_ms = latency_ms
        
        # Calculate running average
        if self.chunks_received == 0:
            self.average_latency_ms = latency_ms
        else:
            alpha = 0.1  # Smoothing factor
            self.average_latency_ms = (alpha * latency_ms + 
                                      (1 - alpha) * self.average_latency_ms)
        
        self.last_updated = time.time()
    
    def update_packet_loss(self, expected_seq: int, received_seq: int) -> None:
        """Update packet loss metrics"""
        if expected_seq != received_seq:
            dropped = abs(received_seq - expected_seq)
            self.chunks_dropped += dropped
        
        self.chunks_received += 1
        
        # Calculate packet loss rate
        total_expected = self.chunks_received + self.chunks_dropped
        if total_expected > 0:
            self.packet_loss_rate = self.chunks_dropped / total_expected
        
        self.last_updated = time.time()
    
    def calculate_connection_quality(self) -> float:
        """Calculate overall connection quality score (0.0 to 1.0)"""
        # Factors: latency, packet loss, jitter
        latency_score = max(0.0, 1.0 - (self.average_latency_ms / 500.0))
        packet_loss_score = max(0.0, 1.0 - (self.packet_loss_rate * 10.0))
        jitter_score = max(0.0, 1.0 - (self.jitter_ms / 100.0))
        
        # Weighted average
        self.connection_quality = (
            0.4 * latency_score +
            0.4 * packet_loss_score +
            0.2 * jitter_score
        )
        
        return self.connection_quality
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'current_latency_ms': round(self.current_latency_ms, 2),
            'average_latency_ms': round(self.average_latency_ms, 2),
            'packet_loss_rate': round(self.packet_loss_rate, 4),
            'jitter_ms': round(self.jitter_ms, 2),
            'buffer_underruns': self.buffer_underruns,
            'buffer_overruns': self.buffer_overruns,
            'chunks_received': self.chunks_received,
            'chunks_dropped': self.chunks_dropped,
            'bytes_transferred': self.bytes_transferred,
            'connection_quality': round(self.connection_quality, 2),
            'last_updated': self.last_updated
        }


class AudioBuffer:
    """Circular buffer for audio chunks with adaptive sizing"""
    
    def __init__(self, max_size: int, session_id: str):
        self.max_size = max_size
        self.session_id = session_id
        self.buffer: List[Optional[AudioChunk]] = [None] * max_size
        self.write_index = 0
        self.read_index = 0
        self.size = 0
        self.expected_sequence = 0
        self.underrun_count = 0
        self.overrun_count = 0
        
    def write(self, chunk: AudioChunk) -> bool:
        """Write chunk to buffer"""
        if self.size >= self.max_size:
            # Buffer full - overrun
            self.overrun_count += 1
            logger.warning(f"Buffer overrun for session {self.session_id}")
            return False
        
        self.buffer[self.write_index] = chunk
        self.write_index = (self.write_index + 1) % self.max_size
        self.size += 1
        
        return True
    
    def read(self) -> Optional[AudioChunk]:
        """Read chunk from buffer"""
        if self.size == 0:
            # Buffer empty - underrun
            self.underrun_count += 1
            logger.warning(f"Buffer underrun for session {self.session_id}")
            return None
        
        chunk = self.buffer[self.read_index]
        self.buffer[self.read_index] = None
        self.read_index = (self.read_index + 1) % self.max_size
        self.size -= 1
        
        return chunk
    
    def peek(self) -> Optional[AudioChunk]:
        """Peek at next chunk without removing it"""
        if self.size == 0:
            return None
        return self.buffer[self.read_index]
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return self.size == 0
    
    def is_full(self) -> bool:
        """Check if buffer is full"""
        return self.size >= self.max_size
    
    def get_fill_level(self) -> float:
        """Get buffer fill level (0.0 to 1.0)"""
        return self.size / self.max_size if self.max_size > 0 else 0.0
    
    def clear(self) -> None:
        """Clear all chunks from buffer"""
        self.buffer = [None] * self.max_size
        self.write_index = 0
        self.read_index = 0
        self.size = 0
    
    def resize(self, new_size: int) -> None:
        """Resize buffer (adaptive buffering)"""
        if new_size == self.max_size:
            return
        
        # Create new buffer
        new_buffer = [None] * new_size
        
        # Copy existing chunks
        copy_count = min(self.size, new_size)
        for i in range(copy_count):
            chunk = self.read()
            if chunk:
                new_buffer[i] = chunk
        
        # Update buffer
        self.buffer = new_buffer
        self.max_size = new_size
        self.write_index = copy_count
        self.read_index = 0
        self.size = copy_count
        
        logger.info(f"Buffer resized to {new_size} for session {self.session_id}")


class AudioStreamingService:
    """Service for managing audio streaming protocols"""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, StreamingMetrics] = {}
        
    def initialize_stream(self, session_id: str, 
                         config: Optional[AudioStreamConfig] = None) -> Dict[str, Any]:
        """
        Initialize audio stream for a session
        
        Args:
            session_id: Session identifier
            config: Optional stream configuration
            
        Returns:
            Stream initialization response
        """
        try:
            # Use default config if not provided
            if config is None:
                config = AudioStreamConfig.from_quality_preset(AudioQuality.MEDIUM)
            
            # Create buffer
            buffer = AudioBuffer(
                max_size=config.buffer_size_chunks,
                session_id=session_id
            )
            
            # Create metrics tracker
            metrics = StreamingMetrics(session_id=session_id)
            
            # Store stream state
            self.active_streams[session_id] = {
                'config': config,
                'buffer': buffer,
                'state': StreamingState.IDLE,
                'sequence_number': 0,
                'start_time': time.time(),
                'last_chunk_time': 0.0
            }
            
            self.metrics[session_id] = metrics
            
            logger.info(f"Audio stream initialized for session {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'config': config.to_dict(),
                'message': 'Audio stream initialized successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize stream for session {session_id}: {str(e)}")
            return {
                'success': False,
                'session_id': session_id,
                'error': str(e)
            }
    
    def process_audio_chunk(self, session_id: str, 
                           chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming audio chunk
        
        Args:
            session_id: Session identifier
            chunk_data: Audio chunk data from WebSocket
            
        Returns:
            Processing result
        """
        try:
            # Check if stream exists
            if session_id not in self.active_streams:
                return {
                    'success': False,
                    'error': 'Stream not initialized',
                    'session_id': session_id
                }
            
            stream = self.active_streams[session_id]
            metrics = self.metrics[session_id]
            
            # Parse audio chunk
            chunk = AudioChunk.from_websocket_message(chunk_data)
            
            # Update metrics
            current_time = time.time()
            latency_ms = (current_time - chunk.timestamp) * 1000
            metrics.update_latency(latency_ms)
            metrics.update_packet_loss(stream['sequence_number'], chunk.sequence_number)
            metrics.bytes_transferred += len(chunk.audio_data)
            
            # Update sequence number
            stream['sequence_number'] = chunk.sequence_number + 1
            stream['last_chunk_time'] = current_time
            
            # Write to buffer
            buffer: AudioBuffer = stream['buffer']
            if not buffer.write(chunk):
                metrics.buffer_overruns += 1
                return {
                    'success': False,
                    'error': 'Buffer overrun',
                    'session_id': session_id,
                    'metrics': metrics.to_dict()
                }
            
            # Update streaming state
            if stream['state'] == StreamingState.IDLE:
                stream['state'] = StreamingState.BUFFERING
            elif stream['state'] == StreamingState.BUFFERING:
                # Check if buffer is sufficiently filled
                if buffer.get_fill_level() >= 0.5:
                    stream['state'] = StreamingState.STREAMING
            
            # Check for quality adaptation
            if stream['config'].enable_adaptation:
                self._adapt_stream_quality(session_id)
            
            return {
                'success': True,
                'session_id': session_id,
                'chunk_id': chunk.chunk_id,
                'sequence_number': chunk.sequence_number,
                'buffer_fill': buffer.get_fill_level(),
                'state': stream['state'].value,
                'metrics': metrics.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to process audio chunk for session {session_id}: {str(e)}")
            return {
                'success': False,
                'session_id': session_id,
                'error': str(e)
            }
    
    def get_next_chunk(self, session_id: str) -> Optional[AudioChunk]:
        """
        Get next audio chunk for playback
        
        Args:
            session_id: Session identifier
            
        Returns:
            Next audio chunk or None
        """
        try:
            if session_id not in self.active_streams:
                return None
            
            stream = self.active_streams[session_id]
            buffer: AudioBuffer = stream['buffer']
            metrics = self.metrics[session_id]
            
            # Read from buffer
            chunk = buffer.read()
            
            if chunk is None:
                metrics.buffer_underruns += 1
                
                # Check if stream should transition to buffering
                if stream['state'] == StreamingState.STREAMING:
                    stream['state'] = StreamingState.BUFFERING
                    logger.warning(f"Stream {session_id} transitioning to buffering due to underrun")
            
            return chunk
            
        except Exception as e:
            logger.error(f"Failed to get next chunk for session {session_id}: {str(e)}")
            return None
    
    def get_stream_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current streaming metrics
        
        Args:
            session_id: Session identifier
            
        Returns:
            Metrics dictionary or None
        """
        if session_id not in self.metrics:
            return None
        
        metrics = self.metrics[session_id]
        metrics.calculate_connection_quality()
        
        return metrics.to_dict()
    
    def _adapt_stream_quality(self, session_id: str) -> None:
        """
        Adapt stream quality based on network conditions
        
        Args:
            session_id: Session identifier
        """
        try:
            stream = self.active_streams[session_id]
            metrics = self.metrics[session_id]
            config: AudioStreamConfig = stream['config']
            buffer: AudioBuffer = stream['buffer']
            
            # Calculate connection quality
            quality_score = metrics.calculate_connection_quality()
            
            # Determine if adaptation is needed
            current_quality = config.quality
            new_quality = current_quality
            
            if quality_score < 0.3:
                # Poor connection - downgrade to LOW
                new_quality = AudioQuality.LOW
            elif quality_score < 0.6:
                # Fair connection - use MEDIUM
                new_quality = AudioQuality.MEDIUM
            elif quality_score > 0.8 and current_quality != AudioQuality.HIGH:
                # Good connection - upgrade to HIGH
                new_quality = AudioQuality.HIGH
            
            # Apply adaptation if quality changed
            if new_quality != current_quality:
                logger.info(f"Adapting stream quality for session {session_id}: "
                          f"{current_quality.value} -> {new_quality.value}")
                
                # Create new config
                new_config = AudioStreamConfig.from_quality_preset(new_quality)
                stream['config'] = new_config
                
                # Resize buffer if needed
                if new_config.buffer_size_chunks != buffer.max_size:
                    buffer.resize(new_config.buffer_size_chunks)
                
                # Send quality change notification
                self._send_quality_change_notification(session_id, new_quality)
            
        except Exception as e:
            logger.error(f"Failed to adapt stream quality for session {session_id}: {str(e)}")
    
    def _send_quality_change_notification(self, session_id: str, 
                                         new_quality: AudioQuality) -> None:
        """
        Send quality change notification to client
        
        Args:
            session_id: Session identifier
            new_quality: New quality setting
        """
        # This would send a WebSocket message to the client
        # Implementation depends on WebSocket handler integration
        logger.info(f"Quality change notification for session {session_id}: {new_quality.value}")
    
    def pause_stream(self, session_id: str) -> bool:
        """
        Pause audio stream
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            if session_id not in self.active_streams:
                return False
            
            stream = self.active_streams[session_id]
            stream['state'] = StreamingState.PAUSED
            
            logger.info(f"Stream paused for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause stream for session {session_id}: {str(e)}")
            return False
    
    def resume_stream(self, session_id: str) -> bool:
        """
        Resume audio stream
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            if session_id not in self.active_streams:
                return False
            
            stream = self.active_streams[session_id]
            buffer: AudioBuffer = stream['buffer']
            
            # Transition to appropriate state based on buffer fill
            if buffer.get_fill_level() >= 0.5:
                stream['state'] = StreamingState.STREAMING
            else:
                stream['state'] = StreamingState.BUFFERING
            
            logger.info(f"Stream resumed for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume stream for session {session_id}: {str(e)}")
            return False
    
    def close_stream(self, session_id: str) -> bool:
        """
        Close audio stream and cleanup resources
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            if session_id not in self.active_streams:
                return False
            
            # Get final metrics
            final_metrics = self.get_stream_metrics(session_id)
            
            # Cleanup
            stream = self.active_streams[session_id]
            buffer: AudioBuffer = stream['buffer']
            buffer.clear()
            
            del self.active_streams[session_id]
            del self.metrics[session_id]
            
            logger.info(f"Stream closed for session {session_id}. "
                       f"Final metrics: {final_metrics}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close stream for session {session_id}: {str(e)}")
            return False
    
    def get_active_stream_count(self) -> int:
        """Get number of active streams"""
        return len(self.active_streams)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all active streams"""
        return {
            session_id: self.get_stream_metrics(session_id)
            for session_id in self.active_streams.keys()
        }


# Global service instance
audio_streaming_service = AudioStreamingService()
