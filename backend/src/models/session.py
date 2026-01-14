"""
Session data models for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class SentimentType(str, Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class RiskLevel(str, Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AudioQualityMetrics(BaseModel):
    """Audio quality metrics"""
    average_latency_ms: float = Field(default=0.0, ge=0)
    packet_loss_rate: float = Field(default=0.0, ge=0, le=1)
    audio_clarity_score: float = Field(default=1.0, ge=0, le=1)
    connection_stability: float = Field(default=1.0, ge=0, le=1)


class ConnectionMetrics(BaseModel):
    """Connection quality metrics"""
    connection_duration_ms: int = Field(default=0, ge=0)
    reconnection_count: int = Field(default=0, ge=0)
    average_response_time_ms: float = Field(default=0.0, ge=0)
    data_transfer_mb: float = Field(default=0.0, ge=0)


class ProgressIndicator(BaseModel):
    """Therapeutic progress indicator"""
    metric_name: str = Field(..., min_length=1, max_length=100)
    value: float = Field(..., ge=0, le=1)
    description: str = Field(..., min_length=1, max_length=500)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionMetadata(BaseModel):
    """Session metadata and metrics"""
    audio_quality: AudioQualityMetrics = Field(default_factory=AudioQualityMetrics)
    connection_metrics: ConnectionMetrics = Field(default_factory=ConnectionMetrics)
    therapeutic_milestones: List[str] = Field(default_factory=list)
    exercises_completed: List[str] = Field(default_factory=list)


class SentimentSummary(BaseModel):
    """AI-generated sentiment summary for therapists"""
    overall_sentiment: SentimentType
    emotional_state: List[str] = Field(default_factory=list)
    progress_indicators: List[ProgressIndicator] = Field(default_factory=list)
    key_topics: List[str] = Field(default_factory=list)
    risk_level: RiskLevel
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class TherapySession(BaseModel):
    """Main therapy session model"""
    session_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    client_id: str = Field(..., min_length=1)
    agent_id: str = Field(..., min_length=1)
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # Duration in seconds
    language: str = Field(default="en")
    metadata: SessionMetadata = Field(default_factory=SessionMetadata)
    sentiment_summary: Optional[SentimentSummary] = None
    sentiment_score: Optional[int] = Field(None, ge=1, le=10)  # User sentiment score 1-10 (internal use)
    agent_memory_id: str = Field(..., min_length=1)
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item format"""
        item = {
            'sessionId': {'S': self.session_id},
            'timestamp': {'S': self.timestamp.isoformat()},
            'clientId': {'S': self.client_id},
            'agentId': {'S': self.agent_id},
            'status': {'S': self.status.value},
            'startTime': {'S': self.start_time.isoformat()},
            'language': {'S': self.language},
            'metadata': {'M': {
                'audioQuality': {'M': {
                    'averageLatencyMs': {'N': str(self.metadata.audio_quality.average_latency_ms)},
                    'packetLossRate': {'N': str(self.metadata.audio_quality.packet_loss_rate)},
                    'audioClarityScore': {'N': str(self.metadata.audio_quality.audio_clarity_score)},
                    'connectionStability': {'N': str(self.metadata.audio_quality.connection_stability)}
                }},
                'connectionMetrics': {'M': {
                    'connectionDurationMs': {'N': str(self.metadata.connection_metrics.connection_duration_ms)},
                    'reconnectionCount': {'N': str(self.metadata.connection_metrics.reconnection_count)},
                    'averageResponseTimeMs': {'N': str(self.metadata.connection_metrics.average_response_time_ms)},
                    'dataTransferMb': {'N': str(self.metadata.connection_metrics.data_transfer_mb)}
                }},
                'therapeuticMilestones': {'SS': self.metadata.therapeutic_milestones or []},
                'exercisesCompleted': {'SS': self.metadata.exercises_completed or []}
            }},
            'agentMemoryId': {'S': self.agent_memory_id},
            'GSI1PK': {'S': self.client_id},  # For client-based queries
            'GSI1SK': {'S': self.timestamp.isoformat()}  # For sorting
        }
        
        # Add optional fields
        if self.end_time:
            item['endTime'] = {'S': self.end_time.isoformat()}
        
        if self.duration:
            item['duration'] = {'N': str(self.duration)}
        
        if self.sentiment_score:
            item['sentimentScore'] = {'N': str(self.sentiment_score)}
        
        if self.sentiment_summary:
            progress_indicators = []
            for pi in self.sentiment_summary.progress_indicators:
                progress_indicators.append({'M': {
                    'metricName': {'S': pi.metric_name},
                    'value': {'N': str(pi.value)},
                    'description': {'S': pi.description},
                    'timestamp': {'S': pi.timestamp.isoformat()}
                }})
            
            item['sentimentSummary'] = {'M': {
                'overallSentiment': {'S': self.sentiment_summary.overall_sentiment.value},
                'emotionalState': {'SS': self.sentiment_summary.emotional_state or []},
                'progressIndicators': {'L': progress_indicators},
                'keyTopics': {'SS': self.sentiment_summary.key_topics or []},
                'riskLevel': {'S': self.sentiment_summary.risk_level.value},
                'generatedAt': {'S': self.sentiment_summary.generated_at.isoformat()}
            }}
        
        return item
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> 'TherapySession':
        """Create TherapySession from DynamoDB item"""
        metadata_data = item['metadata']['M']
        
        # Build audio quality metrics
        audio_quality = AudioQualityMetrics(
            average_latency_ms=float(metadata_data['audioQuality']['M']['averageLatencyMs']['N']),
            packet_loss_rate=float(metadata_data['audioQuality']['M']['packetLossRate']['N']),
            audio_clarity_score=float(metadata_data['audioQuality']['M']['audioClarityScore']['N']),
            connection_stability=float(metadata_data['audioQuality']['M']['connectionStability']['N'])
        )
        
        # Build connection metrics
        connection_metrics = ConnectionMetrics(
            connection_duration_ms=int(metadata_data['connectionMetrics']['M']['connectionDurationMs']['N']),
            reconnection_count=int(metadata_data['connectionMetrics']['M']['reconnectionCount']['N']),
            average_response_time_ms=float(metadata_data['connectionMetrics']['M']['averageResponseTimeMs']['N']),
            data_transfer_mb=float(metadata_data['connectionMetrics']['M']['dataTransferMb']['N'])
        )
        
        # Build metadata
        metadata = SessionMetadata(
            audio_quality=audio_quality,
            connection_metrics=connection_metrics,
            therapeutic_milestones=metadata_data.get('therapeuticMilestones', {}).get('SS', []),
            exercises_completed=metadata_data.get('exercisesCompleted', {}).get('SS', [])
        )
        
        # Build sentiment summary if present
        sentiment_summary = None
        if 'sentimentSummary' in item:
            ss_data = item['sentimentSummary']['M']
            
            # Build progress indicators
            progress_indicators = []
            for pi_item in ss_data.get('progressIndicators', {}).get('L', []):
                pi_data = pi_item['M']
                progress_indicators.append(ProgressIndicator(
                    metric_name=pi_data['metricName']['S'],
                    value=float(pi_data['value']['N']),
                    description=pi_data['description']['S'],
                    timestamp=datetime.fromisoformat(pi_data['timestamp']['S'])
                ))
            
            sentiment_summary = SentimentSummary(
                overall_sentiment=SentimentType(ss_data['overallSentiment']['S']),
                emotional_state=ss_data.get('emotionalState', {}).get('SS', []),
                progress_indicators=progress_indicators,
                key_topics=ss_data.get('keyTopics', {}).get('SS', []),
                risk_level=RiskLevel(ss_data['riskLevel']['S']),
                generated_at=datetime.fromisoformat(ss_data['generatedAt']['S'])
            )
        
        return cls(
            session_id=item['sessionId']['S'],
            timestamp=datetime.fromisoformat(item['timestamp']['S']),
            client_id=item['clientId']['S'],
            agent_id=item['agentId']['S'],
            status=SessionStatus(item['status']['S']),
            start_time=datetime.fromisoformat(item['startTime']['S']),
            end_time=datetime.fromisoformat(item['endTime']['S']) if 'endTime' in item else None,
            duration=int(item['duration']['N']) if 'duration' in item else None,
            language=item['language']['S'],
            metadata=metadata,
            sentiment_summary=sentiment_summary,
            sentiment_score=int(item['sentimentScore']['N']) if 'sentimentScore' in item else None,
            agent_memory_id=item['agentMemoryId']['S']
        )