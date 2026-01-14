"""
AgentCore Memory data models for AI Therapy Platform
Handles conversation context and therapeutic profile storage
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class RetentionPolicyType(str, Enum):
    """Memory retention policy types"""
    STANDARD = "standard"  # 90 days
    EXTENDED = "extended"  # 180 days
    PERMANENT = "permanent"  # No expiration


class SessionSummary(BaseModel):
    """Summary of a therapy session for memory context"""
    session_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: int = Field(..., ge=0)
    key_topics: List[str] = Field(default_factory=list)
    emotional_state: List[str] = Field(default_factory=list)
    therapeutic_progress: str = Field(..., min_length=1, max_length=1000)
    milestones_achieved: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProgressNote(BaseModel):
    """Therapeutic progress note"""
    note_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content: str = Field(..., min_length=1, max_length=2000)
    category: str = Field(..., min_length=1, max_length=100)
    importance: int = Field(default=1, ge=1, le=5)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PersonalityAdaptation(BaseModel):
    """AI personality adaptation based on client interactions"""
    adaptation_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    adaptation_type: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    effectiveness_score: float = Field(default=0.5, ge=0, le=1)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationContext(BaseModel):
    """Conversation context for therapeutic continuity"""
    session_history: List[SessionSummary] = Field(default_factory=list)
    ongoing_topics: List[str] = Field(default_factory=list)
    therapeutic_goals: List[str] = Field(default_factory=list)
    progress_notes: List[ProgressNote] = Field(default_factory=list)
    personality_adaptations: List[PersonalityAdaptation] = Field(default_factory=list)
    last_session_date: Optional[datetime] = None
    total_sessions: int = Field(default=0, ge=0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TherapeuticProfile(BaseModel):
    """Therapeutic profile for personalized care"""
    communication_style: str = Field(default="empathetic")
    preferred_approaches: List[str] = Field(default_factory=list)
    triggers_to_avoid: List[str] = Field(default_factory=list)
    successful_interventions: List[str] = Field(default_factory=list)
    cultural_considerations: List[str] = Field(default_factory=list)
    language_preference: str = Field(default="en")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RetentionPolicy(BaseModel):
    """Memory retention policy"""
    policy_type: RetentionPolicyType = Field(default=RetentionPolicyType.STANDARD)
    expiration_date: Optional[datetime] = None
    auto_cleanup_enabled: bool = Field(default=True)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentMemory(BaseModel):
    """Complete AgentCore memory structure"""
    memory_id: str = Field(..., min_length=1)
    client_id: str = Field(..., min_length=1)
    conversation_context: ConversationContext = Field(default_factory=ConversationContext)
    therapeutic_profile: TherapeuticProfile = Field(default_factory=TherapeuticProfile)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    retention_policy: RetentionPolicy = Field(default_factory=RetentionPolicy)
    version: int = Field(default=1, ge=1)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for AgentCore storage"""
        return {
            'memory_id': self.memory_id,
            'client_id': self.client_id,
            'conversation_context': {
                'session_history': [
                    {
                        'session_id': s.session_id,
                        'timestamp': s.timestamp.isoformat(),
                        'duration_seconds': s.duration_seconds,
                        'key_topics': s.key_topics,
                        'emotional_state': s.emotional_state,
                        'therapeutic_progress': s.therapeutic_progress,
                        'milestones_achieved': s.milestones_achieved
                    }
                    for s in self.conversation_context.session_history
                ],
                'ongoing_topics': self.conversation_context.ongoing_topics,
                'therapeutic_goals': self.conversation_context.therapeutic_goals,
                'progress_notes': [
                    {
                        'note_id': n.note_id,
                        'timestamp': n.timestamp.isoformat(),
                        'content': n.content,
                        'category': n.category,
                        'importance': n.importance
                    }
                    for n in self.conversation_context.progress_notes
                ],
                'personality_adaptations': [
                    {
                        'adaptation_id': a.adaptation_id,
                        'timestamp': a.timestamp.isoformat(),
                        'adaptation_type': a.adaptation_type,
                        'description': a.description,
                        'effectiveness_score': a.effectiveness_score
                    }
                    for a in self.conversation_context.personality_adaptations
                ],
                'last_session_date': self.conversation_context.last_session_date.isoformat() if self.conversation_context.last_session_date else None,
                'total_sessions': self.conversation_context.total_sessions
            },
            'therapeutic_profile': {
                'communication_style': self.therapeutic_profile.communication_style,
                'preferred_approaches': self.therapeutic_profile.preferred_approaches,
                'triggers_to_avoid': self.therapeutic_profile.triggers_to_avoid,
                'successful_interventions': self.therapeutic_profile.successful_interventions,
                'cultural_considerations': self.therapeutic_profile.cultural_considerations,
                'language_preference': self.therapeutic_profile.language_preference
            },
            'last_updated': self.last_updated.isoformat(),
            'retention_policy': {
                'policy_type': self.retention_policy.policy_type if isinstance(self.retention_policy.policy_type, str) else self.retention_policy.policy_type.value,
                'expiration_date': self.retention_policy.expiration_date.isoformat() if self.retention_policy.expiration_date else None,
                'auto_cleanup_enabled': self.retention_policy.auto_cleanup_enabled
            },
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMemory':
        """Create AgentMemory from dictionary"""
        # Parse conversation context
        context_data = data.get('conversation_context', {})
        
        session_history = [
            SessionSummary(
                session_id=s['session_id'],
                timestamp=datetime.fromisoformat(s['timestamp']),
                duration_seconds=s['duration_seconds'],
                key_topics=s.get('key_topics', []),
                emotional_state=s.get('emotional_state', []),
                therapeutic_progress=s['therapeutic_progress'],
                milestones_achieved=s.get('milestones_achieved', [])
            )
            for s in context_data.get('session_history', [])
        ]
        
        progress_notes = [
            ProgressNote(
                note_id=n['note_id'],
                timestamp=datetime.fromisoformat(n['timestamp']),
                content=n['content'],
                category=n['category'],
                importance=n.get('importance', 1)
            )
            for n in context_data.get('progress_notes', [])
        ]
        
        personality_adaptations = [
            PersonalityAdaptation(
                adaptation_id=a['adaptation_id'],
                timestamp=datetime.fromisoformat(a['timestamp']),
                adaptation_type=a['adaptation_type'],
                description=a['description'],
                effectiveness_score=a.get('effectiveness_score', 0.5)
            )
            for a in context_data.get('personality_adaptations', [])
        ]
        
        conversation_context = ConversationContext(
            session_history=session_history,
            ongoing_topics=context_data.get('ongoing_topics', []),
            therapeutic_goals=context_data.get('therapeutic_goals', []),
            progress_notes=progress_notes,
            personality_adaptations=personality_adaptations,
            last_session_date=datetime.fromisoformat(context_data['last_session_date']) if context_data.get('last_session_date') else None,
            total_sessions=context_data.get('total_sessions', 0)
        )
        
        # Parse therapeutic profile
        profile_data = data.get('therapeutic_profile', {})
        therapeutic_profile = TherapeuticProfile(
            communication_style=profile_data.get('communication_style', 'empathetic'),
            preferred_approaches=profile_data.get('preferred_approaches', []),
            triggers_to_avoid=profile_data.get('triggers_to_avoid', []),
            successful_interventions=profile_data.get('successful_interventions', []),
            cultural_considerations=profile_data.get('cultural_considerations', []),
            language_preference=profile_data.get('language_preference', 'en')
        )
        
        # Parse retention policy
        policy_data = data.get('retention_policy', {})
        retention_policy = RetentionPolicy(
            policy_type=RetentionPolicyType(policy_data.get('policy_type', 'standard')),
            expiration_date=datetime.fromisoformat(policy_data['expiration_date']) if policy_data.get('expiration_date') else None,
            auto_cleanup_enabled=policy_data.get('auto_cleanup_enabled', True)
        )
        
        return cls(
            memory_id=data['memory_id'],
            client_id=data['client_id'],
            conversation_context=conversation_context,
            therapeutic_profile=therapeutic_profile,
            last_updated=datetime.fromisoformat(data['last_updated']),
            retention_policy=retention_policy,
            version=data.get('version', 1)
        )
