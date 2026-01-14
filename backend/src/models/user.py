"""
User data models for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    CLIENT = "client"
    THERAPIST = "therapist"
    ADMIN = "admin"


class DomesticAbuseType(str, Enum):
    """Types of domestic abuse (internal use only)"""
    PHYSICAL = "physical"
    EMOTIONAL_PSYCHOLOGICAL = "emotional_psychological"
    SEXUAL = "sexual"
    FINANCIAL_ECONOMIC = "financial_economic"
    DIGITAL_TECHNOLOGICAL = "digital_technological"
    NONE = "none"


class EmotionalState(str, Enum):
    """Current emotional state (internal use only)"""
    FEAR = "fear"
    SHAME = "shame"
    GUILT = "guilt"
    CONFUSION = "confusion"
    ANGER = "anger"
    SADNESS = "sadness"
    HOPELESSNESS = "hopelessness"
    ANXIETY = "anxiety"
    NUMBNESS = "numbness"
    LOW_SELF_ESTEEM = "low_self_esteem"


class ConversationPreference(str, Enum):
    """User's conversation preference (internal use only)"""
    JUST_LISTENING = "just_listening"
    COPING_TOOLS = "coping_tools"
    CHECK_IN = "check_in"
    VENTING = "venting"
    SELF_COMPASSION = "self_compassion"


class SelfHarmRiskSignal(str, Enum):
    """Self-harm risk level (internal use only)"""
    NONE = "none"
    PASSIVE = "passive"
    CONCERNING = "concerning"
    ACUTE = "acute"
    UNKNOWN = "unknown"


class UserRisk(str, Enum):
    """Overall user risk level (internal use only)"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    relationship: str = Field(..., min_length=1, max_length=50)


class VoiceSettings(BaseModel):
    """Voice synthesis settings"""
    voice_id: str = Field(default="default")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: float = Field(default=1.0, ge=0.1, le=1.0)


class NotificationSettings(BaseModel):
    """User notification preferences"""
    email_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=False)
    push_enabled: bool = Field(default=True)
    red_flag_alerts: bool = Field(default=True)
    session_reminders: bool = Field(default=True)


class PrivacySettings(BaseModel):
    """User privacy preferences"""
    data_sharing_consent: bool = Field(default=False)
    analytics_consent: bool = Field(default=False)
    marketing_consent: bool = Field(default=False)
    session_recording_consent: bool = Field(default=True)


class UserProfile(BaseModel):
    """User profile information"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    timezone: str = Field(default="UTC")
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    emergency_contact: Optional[EmergencyContact] = None


class ClinicalProfile(BaseModel):
    """Internal clinical profile (NOT visible to user)"""
    age: int = Field(..., ge=13, le=120)
    gender: str = Field(..., min_length=1, max_length=50)
    note_on_user: Optional[str] = Field(None, max_length=2000)
    medical_conditions: List[str] = Field(default_factory=list)  # List of conditions or empty
    domestic_abuse_type: DomesticAbuseType = Field(default=DomesticAbuseType.NONE)
    emotional_state: EmotionalState = Field(default=EmotionalState.ANXIETY)
    conversation_preference: ConversationPreference = Field(default=ConversationPreference.JUST_LISTENING)
    self_harm_risk_signal: SelfHarmRiskSignal = Field(default=SelfHarmRiskSignal.UNKNOWN)
    user_risk: UserRisk = Field(default=UserRisk.UNKNOWN)
    last_session_timestamp: Optional[datetime] = None
    total_goals: int = Field(default=0, ge=0)
    goals_achieved: int = Field(default=0, ge=0)
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UserPreferences(BaseModel):
    """User preferences and settings"""
    language: str = Field(default="en")
    voice_settings: VoiceSettings = Field(default_factory=VoiceSettings)
    notification_settings: NotificationSettings = Field(default_factory=NotificationSettings)
    privacy_settings: PrivacySettings = Field(default_factory=PrivacySettings)


class User(BaseModel):
    """Main user model"""
    user_id: str = Field(..., min_length=1)
    email: EmailStr
    role: UserRole
    profile: UserProfile
    clinical_profile: Optional[ClinicalProfile] = None  # Internal use only
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    mfa_enabled: bool = Field(default=False)
    language_preference: str = Field(default="en")
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert to DynamoDB item format"""
        item = {
            'userId': {'S': self.user_id},
            'email': {'S': self.email},
            'role': {'S': self.role.value},
            'profile': {'M': {
                'firstName': {'S': self.profile.first_name},
                'lastName': {'S': self.profile.last_name},
                'timezone': {'S': self.profile.timezone}
            }},
            'preferences': {'M': {
                'language': {'S': self.preferences.language},
                'voiceSettings': {'M': {
                    'voiceId': {'S': self.preferences.voice_settings.voice_id},
                    'speed': {'N': str(self.preferences.voice_settings.speed)},
                    'pitch': {'N': str(self.preferences.voice_settings.pitch)},
                    'volume': {'N': str(self.preferences.voice_settings.volume)}
                }},
                'notificationSettings': {'M': {
                    'emailEnabled': {'BOOL': self.preferences.notification_settings.email_enabled},
                    'smsEnabled': {'BOOL': self.preferences.notification_settings.sms_enabled},
                    'pushEnabled': {'BOOL': self.preferences.notification_settings.push_enabled},
                    'redFlagAlerts': {'BOOL': self.preferences.notification_settings.red_flag_alerts},
                    'sessionReminders': {'BOOL': self.preferences.notification_settings.session_reminders}
                }},
                'privacySettings': {'M': {
                    'dataSharingConsent': {'BOOL': self.preferences.privacy_settings.data_sharing_consent},
                    'analyticsConsent': {'BOOL': self.preferences.privacy_settings.analytics_consent},
                    'marketingConsent': {'BOOL': self.preferences.privacy_settings.marketing_consent},
                    'sessionRecordingConsent': {'BOOL': self.preferences.privacy_settings.session_recording_consent}
                }}
            }},
            'createdAt': {'S': self.created_at.isoformat()},
            'updatedAt': {'S': self.updated_at.isoformat()},
            'isActive': {'BOOL': self.is_active},
            'mfaEnabled': {'BOOL': self.mfa_enabled},
            'languagePreference': {'S': self.language_preference},
            'GSI1PK': {'S': self.email}  # For email-based queries
        }
        
        # Add optional fields
        if self.profile.phone_number:
            item['profile']['M']['phoneNumber'] = {'S': self.profile.phone_number}
        
        if self.profile.emergency_contact:
            item['profile']['M']['emergencyContact'] = {'M': {
                'name': {'S': self.profile.emergency_contact.name},
                'phone': {'S': self.profile.emergency_contact.phone},
                'relationship': {'S': self.profile.emergency_contact.relationship}
            }}
        
        # Add clinical profile (internal use only)
        if self.clinical_profile:
            clinical_item = {
                'age': {'N': str(self.clinical_profile.age)},
                'gender': {'S': self.clinical_profile.gender},
                'domesticAbuseType': {'S': self.clinical_profile.domestic_abuse_type.value},
                'emotionalState': {'S': self.clinical_profile.emotional_state.value},
                'conversationPreference': {'S': self.clinical_profile.conversation_preference.value},
                'selfHarmRiskSignal': {'S': self.clinical_profile.self_harm_risk_signal.value},
                'userRisk': {'S': self.clinical_profile.user_risk.value},
                'totalGoals': {'N': str(self.clinical_profile.total_goals)},
                'goalsAchieved': {'N': str(self.clinical_profile.goals_achieved)}
            }
            
            if self.clinical_profile.note_on_user:
                clinical_item['noteOnUser'] = {'S': self.clinical_profile.note_on_user}
            
            if self.clinical_profile.medical_conditions:
                clinical_item['medicalConditions'] = {
                    'L': [{'S': condition} for condition in self.clinical_profile.medical_conditions]
                }
            
            if self.clinical_profile.last_session_timestamp:
                clinical_item['lastSessionTimestamp'] = {'S': self.clinical_profile.last_session_timestamp.isoformat()}
            
            item['clinicalProfile'] = {'M': clinical_item}
        
        return item
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> 'User':
        """Create User from DynamoDB item"""
        profile_data = item['profile']['M']
        preferences_data = item['preferences']['M']
        
        # Build profile
        profile = UserProfile(
            first_name=profile_data['firstName']['S'],
            last_name=profile_data['lastName']['S'],
            timezone=profile_data['timezone']['S'],
            phone_number=profile_data.get('phoneNumber', {}).get('S'),
        )
        
        # Add emergency contact if present
        if 'emergencyContact' in profile_data:
            ec_data = profile_data['emergencyContact']['M']
            profile.emergency_contact = EmergencyContact(
                name=ec_data['name']['S'],
                phone=ec_data['phone']['S'],
                relationship=ec_data['relationship']['S']
            )
        
        # Build preferences
        voice_settings = VoiceSettings(
            voice_id=preferences_data['voiceSettings']['M']['voiceId']['S'],
            speed=float(preferences_data['voiceSettings']['M']['speed']['N']),
            pitch=float(preferences_data['voiceSettings']['M']['pitch']['N']),
            volume=float(preferences_data['voiceSettings']['M']['volume']['N'])
        )
        
        notification_settings = NotificationSettings(
            email_enabled=preferences_data['notificationSettings']['M']['emailEnabled']['BOOL'],
            sms_enabled=preferences_data['notificationSettings']['M']['smsEnabled']['BOOL'],
            push_enabled=preferences_data['notificationSettings']['M']['pushEnabled']['BOOL'],
            red_flag_alerts=preferences_data['notificationSettings']['M']['redFlagAlerts']['BOOL'],
            session_reminders=preferences_data['notificationSettings']['M']['sessionReminders']['BOOL']
        )
        
        privacy_settings = PrivacySettings(
            data_sharing_consent=preferences_data['privacySettings']['M']['dataSharingConsent']['BOOL'],
            analytics_consent=preferences_data['privacySettings']['M']['analyticsConsent']['BOOL'],
            marketing_consent=preferences_data['privacySettings']['M']['marketingConsent']['BOOL'],
            session_recording_consent=preferences_data['privacySettings']['M']['sessionRecordingConsent']['BOOL']
        )
        
        preferences = UserPreferences(
            language=preferences_data['language']['S'],
            voice_settings=voice_settings,
            notification_settings=notification_settings,
            privacy_settings=privacy_settings
        )
        
        # Build clinical profile if present
        clinical_profile = None
        if 'clinicalProfile' in item:
            clinical_data = item['clinicalProfile']['M']
            
            medical_conditions = []
            if 'medicalConditions' in clinical_data:
                medical_conditions = [cond['S'] for cond in clinical_data['medicalConditions']['L']]
            
            last_session = None
            if 'lastSessionTimestamp' in clinical_data:
                last_session = datetime.fromisoformat(clinical_data['lastSessionTimestamp']['S'])
            
            clinical_profile = ClinicalProfile(
                age=int(clinical_data['age']['N']),
                gender=clinical_data['gender']['S'],
                note_on_user=clinical_data.get('noteOnUser', {}).get('S'),
                medical_conditions=medical_conditions,
                domestic_abuse_type=DomesticAbuseType(clinical_data['domesticAbuseType']['S']),
                emotional_state=EmotionalState(clinical_data['emotionalState']['S']),
                conversation_preference=ConversationPreference(clinical_data['conversationPreference']['S']),
                self_harm_risk_signal=SelfHarmRiskSignal(clinical_data['selfHarmRiskSignal']['S']),
                user_risk=UserRisk(clinical_data['userRisk']['S']),
                last_session_timestamp=last_session,
                total_goals=int(clinical_data['totalGoals']['N']),
                goals_achieved=int(clinical_data['goalsAchieved']['N'])
            )
        
        return cls(
            user_id=item['userId']['S'],
            email=item['email']['S'],
            role=UserRole(item['role']['S']),
            profile=profile,
            clinical_profile=clinical_profile,
            preferences=preferences,
            created_at=datetime.fromisoformat(item['createdAt']['S']),
            updated_at=datetime.fromisoformat(item['updatedAt']['S']),
            is_active=item['isActive']['BOOL'],
            mfa_enabled=item['mfaEnabled']['BOOL'],
            language_preference=item['languagePreference']['S']
        )