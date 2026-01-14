"""
WebSocket Message Protocol Definitions for AI Therapy Platform
Defines standardized message formats for audio streaming and session management
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """WebSocket message types"""
    # Connection management
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_ERROR = "connection_error"
    PING = "ping"
    PONG = "pong"
    
    # Session management
    JOIN_SESSION = "join_session"
    SESSION_JOINED = "session_joined"
    LEAVE_SESSION = "leave_session"
    SESSION_LEFT = "session_left"
    PARTICIPANT_JOINED = "participant_joined"
    PARTICIPANT_LEFT = "participant_left"
    PARTICIPANT_DISCONNECTED = "participant_disconnected"
    
    # Audio streaming
    AUDIO_STREAM_INIT = "audio_stream_init"
    AUDIO_STREAM_READY = "audio_stream_ready"
    AUDIO_CHUNK = "audio_chunk"
    AUDIO_CHUNK_ACK = "audio_chunk_ack"
    AUDIO_STREAM_PAUSE = "audio_stream_pause"
    AUDIO_STREAM_RESUME = "audio_stream_resume"
    AUDIO_STREAM_CLOSE = "audio_stream_close"
    
    # Quality and monitoring
    QUALITY_METRICS = "quality_metrics"
    QUALITY_CHANGE = "quality_change"
    BUFFER_STATUS = "buffer_status"
    
    # Nova Sonic 2 integration
    NOVA_PROCESSING = "nova_processing"
    NOVA_RESPONSE = "nova_response"
    NOVA_ERROR = "nova_error"
    
    # General
    SESSION_MESSAGE = "session_message"
    ERROR = "error"
    ACK = "ack"


class BaseMessage(BaseModel):
    """Base WebSocket message"""
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConnectionEstablishedMessage(BaseMessage):
    """Connection established confirmation"""
    type: MessageType = MessageType.CONNECTION_ESTABLISHED
    user_id: str
    role: str
    message: str = "WebSocket connection established successfully"


class ConnectionErrorMessage(BaseMessage):
    """Connection error message"""
    type: MessageType = MessageType.CONNECTION_ERROR
    error: str
    error_code: Optional[str] = None


class PingMessage(BaseMessage):
    """Ping message for connection health check"""
    type: MessageType = MessageType.PING


class PongMessage(BaseMessage):
    """Pong response to ping"""
    type: MessageType = MessageType.PONG
    original_timestamp: Optional[datetime] = None


class JoinSessionMessage(BaseMessage):
    """Request to join a session"""
    type: MessageType = MessageType.JOIN_SESSION
    session_id: str


class SessionJoinedMessage(BaseMessage):
    """Confirmation of session join"""
    type: MessageType = MessageType.SESSION_JOINED
    session_id: str
    message: str = "Successfully joined session"


class LeaveSessionMessage(BaseMessage):
    """Request to leave a session"""
    type: MessageType = MessageType.LEAVE_SESSION
    session_id: Optional[str] = None


class SessionLeftMessage(BaseMessage):
    """Confirmation of session leave"""
    type: MessageType = MessageType.SESSION_LEFT
    session_id: str
    message: str = "Successfully left session"


class ParticipantJoinedMessage(BaseMessage):
    """Notification that a participant joined"""
    type: MessageType = MessageType.PARTICIPANT_JOINED
    session_id: str
    user_id: str


class ParticipantLeftMessage(BaseMessage):
    """Notification that a participant left"""
    type: MessageType = MessageType.PARTICIPANT_LEFT
    session_id: str
    user_id: str


class ParticipantDisconnectedMessage(BaseMessage):
    """Notification that a participant disconnected"""
    type: MessageType = MessageType.PARTICIPANT_DISCONNECTED
    session_id: str
    user_id: str
    message: str = "A participant has disconnected"


class AudioStreamInitMessage(BaseMessage):
    """Initialize audio stream"""
    type: MessageType = MessageType.AUDIO_STREAM_INIT
    session_id: str
    config: Dict[str, Any]  # AudioStreamConfig as dict


class AudioStreamReadyMessage(BaseMessage):
    """Audio stream ready confirmation"""
    type: MessageType = MessageType.AUDIO_STREAM_READY
    session_id: str
    config: Dict[str, Any]
    message: str = "Audio stream initialized and ready"


class AudioChunkMessage(BaseMessage):
    """Audio chunk data"""
    type: MessageType = MessageType.AUDIO_CHUNK
    chunk_id: str
    session_id: str
    sequence_number: int
    audio_data: str  # Base64 encoded
    format: str
    sample_rate: int
    channels: int
    duration_ms: float


class AudioChunkAckMessage(BaseMessage):
    """Acknowledgment of audio chunk receipt"""
    type: MessageType = MessageType.AUDIO_CHUNK_ACK
    session_id: str
    chunk_id: str
    sequence_number: int
    buffer_fill: float
    state: str


class AudioStreamPauseMessage(BaseMessage):
    """Pause audio stream"""
    type: MessageType = MessageType.AUDIO_STREAM_PAUSE
    session_id: str


class AudioStreamResumeMessage(BaseMessage):
    """Resume audio stream"""
    type: MessageType = MessageType.AUDIO_STREAM_RESUME
    session_id: str


class AudioStreamCloseMessage(BaseMessage):
    """Close audio stream"""
    type: MessageType = MessageType.AUDIO_STREAM_CLOSE
    session_id: str


class QualityMetricsMessage(BaseMessage):
    """Real-time quality metrics"""
    type: MessageType = MessageType.QUALITY_METRICS
    session_id: str
    metrics: Dict[str, Any]


class QualityChangeMessage(BaseMessage):
    """Notification of quality adaptation"""
    type: MessageType = MessageType.QUALITY_CHANGE
    session_id: str
    old_quality: str
    new_quality: str
    reason: str
    new_config: Dict[str, Any]


class BufferStatusMessage(BaseMessage):
    """Buffer status update"""
    type: MessageType = MessageType.BUFFER_STATUS
    session_id: str
    fill_level: float
    state: str
    underruns: int
    overruns: int


class NovaProcessingMessage(BaseMessage):
    """Nova Sonic 2 processing notification"""
    type: MessageType = MessageType.NOVA_PROCESSING
    session_id: str
    chunk_id: str
    message: str = "Processing audio with Nova Sonic 2"


class NovaResponseMessage(BaseMessage):
    """Nova Sonic 2 response"""
    type: MessageType = MessageType.NOVA_RESPONSE
    session_id: str
    response_id: str
    audio_data: str  # Base64 encoded response audio
    format: str
    sample_rate: int
    channels: int
    duration_ms: float
    transcript: Optional[str] = None
    language: Optional[str] = None


class NovaErrorMessage(BaseMessage):
    """Nova Sonic 2 error"""
    type: MessageType = MessageType.NOVA_ERROR
    session_id: str
    error: str
    error_code: Optional[str] = None
    recoverable: bool = True


class SessionMessage(BaseMessage):
    """General session message"""
    type: MessageType = MessageType.SESSION_MESSAGE
    session_id: str
    user_id: str
    content: str


class ErrorMessage(BaseMessage):
    """General error message"""
    type: MessageType = MessageType.ERROR
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AckMessage(BaseMessage):
    """General acknowledgment"""
    type: MessageType = MessageType.ACK
    message_id: Optional[str] = None
    message: str = "Acknowledged"


# Message type mapping for deserialization
MESSAGE_TYPE_MAP = {
    MessageType.CONNECTION_ESTABLISHED: ConnectionEstablishedMessage,
    MessageType.CONNECTION_ERROR: ConnectionErrorMessage,
    MessageType.PING: PingMessage,
    MessageType.PONG: PongMessage,
    MessageType.JOIN_SESSION: JoinSessionMessage,
    MessageType.SESSION_JOINED: SessionJoinedMessage,
    MessageType.LEAVE_SESSION: LeaveSessionMessage,
    MessageType.SESSION_LEFT: SessionLeftMessage,
    MessageType.PARTICIPANT_JOINED: ParticipantJoinedMessage,
    MessageType.PARTICIPANT_LEFT: ParticipantLeftMessage,
    MessageType.PARTICIPANT_DISCONNECTED: ParticipantDisconnectedMessage,
    MessageType.AUDIO_STREAM_INIT: AudioStreamInitMessage,
    MessageType.AUDIO_STREAM_READY: AudioStreamReadyMessage,
    MessageType.AUDIO_CHUNK: AudioChunkMessage,
    MessageType.AUDIO_CHUNK_ACK: AudioChunkAckMessage,
    MessageType.AUDIO_STREAM_PAUSE: AudioStreamPauseMessage,
    MessageType.AUDIO_STREAM_RESUME: AudioStreamResumeMessage,
    MessageType.AUDIO_STREAM_CLOSE: AudioStreamCloseMessage,
    MessageType.QUALITY_METRICS: QualityMetricsMessage,
    MessageType.QUALITY_CHANGE: QualityChangeMessage,
    MessageType.BUFFER_STATUS: BufferStatusMessage,
    MessageType.NOVA_PROCESSING: NovaProcessingMessage,
    MessageType.NOVA_RESPONSE: NovaResponseMessage,
    MessageType.NOVA_ERROR: NovaErrorMessage,
    MessageType.SESSION_MESSAGE: SessionMessage,
    MessageType.ERROR: ErrorMessage,
    MessageType.ACK: AckMessage
}


def parse_websocket_message(data: Dict[str, Any]) -> BaseMessage:
    """
    Parse WebSocket message data into appropriate message type
    
    Args:
        data: Raw message data dictionary
        
    Returns:
        Parsed message object
        
    Raises:
        ValueError: If message type is unknown or parsing fails
    """
    try:
        message_type = MessageType(data.get('type'))
        message_class = MESSAGE_TYPE_MAP.get(message_type)
        
        if not message_class:
            raise ValueError(f"Unknown message type: {message_type}")
        
        return message_class(**data)
        
    except Exception as e:
        raise ValueError(f"Failed to parse WebSocket message: {str(e)}")


def create_error_message(error: str, error_code: Optional[str] = None,
                        details: Optional[Dict[str, Any]] = None) -> ErrorMessage:
    """
    Create standardized error message
    
    Args:
        error: Error description
        error_code: Optional error code
        details: Optional error details
        
    Returns:
        ErrorMessage object
    """
    return ErrorMessage(
        error=error,
        error_code=error_code,
        details=details
    )


def create_quality_metrics_message(session_id: str, 
                                  metrics: Dict[str, Any]) -> QualityMetricsMessage:
    """
    Create quality metrics message
    
    Args:
        session_id: Session identifier
        metrics: Metrics dictionary
        
    Returns:
        QualityMetricsMessage object
    """
    return QualityMetricsMessage(
        session_id=session_id,
        metrics=metrics
    )
