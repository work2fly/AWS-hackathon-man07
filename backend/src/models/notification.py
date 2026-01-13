"""
Notification data models for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification type enumeration"""
    RED_FLAG = "red_flag"
    SESSION_COMPLETE = "session_complete"
    SYSTEM_ALERT = "system_alert"


class Priority(str, Enum):
    """Priority level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(BaseModel):
    """Notification model for therapists and admins"""
    recipient_id: str = Field(..., min_length=1)  # therapist/admin ID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: NotificationType
    priority: Priority
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    related_session_id: Optional[str] = None
    related_flag_id: Optional[str] = None
    read: bool = Field(default=False)
    read_at: Optional[datetime] = None
    action_required: bool = Field(default=False)
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item format"""
        item = {
            'recipientId': {'S': self.recipient_id},
            'timestamp': {'S': self.timestamp.isoformat()},
            'type': {'S': self.type.value},
            'priority': {'S': self.priority.value},
            'title': {'S': self.title},
            'message': {'S': self.message},
            'read': {'BOOL': self.read},
            'actionRequired': {'BOOL': self.action_required}
        }
        
        # Add optional fields
        if self.related_session_id:
            item['relatedSessionId'] = {'S': self.related_session_id}
        
        if self.related_flag_id:
            item['relatedFlagId'] = {'S': self.related_flag_id}
        
        if self.read_at:
            item['readAt'] = {'S': self.read_at.isoformat()}
        
        return item
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> 'Notification':
        """Create Notification from DynamoDB item"""
        return cls(
            recipient_id=item['recipientId']['S'],
            timestamp=datetime.fromisoformat(item['timestamp']['S']),
            type=NotificationType(item['type']['S']),
            priority=Priority(item['priority']['S']),
            title=item['title']['S'],
            message=item['message']['S'],
            related_session_id=item.get('relatedSessionId', {}).get('S'),
            related_flag_id=item.get('relatedFlagId', {}).get('S'),
            read=item['read']['BOOL'],
            read_at=datetime.fromisoformat(item['readAt']['S']) if 'readAt' in item else None,
            action_required=item['actionRequired']['BOOL']
        )