"""
Red Flag data models for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class RedFlagType(str, Enum):
    """Red flag type enumeration"""
    SELF_HARM = "self_harm"
    SUICIDAL_IDEATION = "suicidal_ideation"
    ABUSE = "abuse"
    VIOLENCE = "violence"
    CRISIS = "crisis"


class Severity(str, Enum):
    """Severity level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationMethod(str, Enum):
    """Notification delivery method"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationRecord(BaseModel):
    """Record of notification sent"""
    recipient_id: str = Field(..., min_length=1)
    method: NotificationMethod
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = Field(default=False)
    acknowledged_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RedFlag(BaseModel):
    """Red flag incident model"""
    session_id: str = Field(..., min_length=1)
    flag_id: str = Field(..., min_length=1)  # timestamp-based ID
    type: RedFlagType
    severity: Severity
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    context: str = Field(..., min_length=1, max_length=1000)  # Sanitized context, not full transcript
    notifications_sent: List[NotificationRecord] = Field(default_factory=list)
    resolved: bool = Field(default=False)
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
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
            'flagId': {'S': self.flag_id},
            'type': {'S': self.type.value},
            'severity': {'S': self.severity.value},
            'detectedAt': {'S': self.detected_at.isoformat()},
            'context': {'S': self.context},
            'resolved': {'BOOL': self.resolved},
            'GSI1PK': {'S': f"severity#{self.severity.value}"},  # For severity-based queries
            'GSI1SK': {'S': self.detected_at.isoformat()}  # For time-based sorting
        }
        
        # Add notifications sent
        if self.notifications_sent:
            notifications = []
            for notification in self.notifications_sent:
                notif_item = {
                    'M': {
                        'recipientId': {'S': notification.recipient_id},
                        'method': {'S': notification.method.value},
                        'sentAt': {'S': notification.sent_at.isoformat()},
                        'acknowledged': {'BOOL': notification.acknowledged}
                    }
                }
                if notification.acknowledged_at:
                    notif_item['M']['acknowledgedAt'] = {'S': notification.acknowledged_at.isoformat()}
                notifications.append(notif_item)
            item['notificationsSent'] = {'L': notifications}
        
        # Add optional resolution fields
        if self.resolved_by:
            item['resolvedBy'] = {'S': self.resolved_by}
        
        if self.resolved_at:
            item['resolvedAt'] = {'S': self.resolved_at.isoformat()}
        
        return item
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> 'RedFlag':
        """Create RedFlag from DynamoDB item"""
        # Parse notifications
        notifications_sent = []
        if 'notificationsSent' in item:
            for notif_item in item['notificationsSent']['L']:
                notif_data = notif_item['M']
                notification = NotificationRecord(
                    recipient_id=notif_data['recipientId']['S'],
                    method=NotificationMethod(notif_data['method']['S']),
                    sent_at=datetime.fromisoformat(notif_data['sentAt']['S']),
                    acknowledged=notif_data['acknowledged']['BOOL'],
                    acknowledged_at=datetime.fromisoformat(notif_data['acknowledgedAt']['S']) if 'acknowledgedAt' in notif_data else None
                )
                notifications_sent.append(notification)
        
        return cls(
            session_id=item['sessionId']['S'],
            flag_id=item['flagId']['S'],
            type=RedFlagType(item['type']['S']),
            severity=Severity(item['severity']['S']),
            detected_at=datetime.fromisoformat(item['detectedAt']['S']),
            context=item['context']['S'],
            notifications_sent=notifications_sent,
            resolved=item['resolved']['BOOL'],
            resolved_by=item.get('resolvedBy', {}).get('S'),
            resolved_at=datetime.fromisoformat(item['resolvedAt']['S']) if 'resolvedAt' in item else None
        )