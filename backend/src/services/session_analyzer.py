"""
Session Analysis Service - Analyzes chat sessions and updates clinical profile
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from ..models.user import (
    EmotionalState, ConversationPreference, 
    SelfHarmRiskSignal, UserRisk, ClinicalProfile
)
from ..models.red_flag import RedFlag, RedFlagType, Severity
from ..data.user_repository import UserRepository
from ..data.red_flag_repository import RedFlagRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionAnalyzer:
    """Analyzes therapy sessions and updates user clinical profiles"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.red_flag_repo = RedFlagRepository()
    
    def analyze_session(self, user_id: str, session_id: str, 
                       messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze a completed session and update clinical profile
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            messages: List of message dicts with 'role' and 'content'
        
        Returns:
            Analysis results with updated profile data and sentiment score
        """
        try:
            from ..data.session_repository import SessionRepository
            
            # Get current user
            user = self.user_repo.get_user(user_id)
            if not user or not user.clinical_profile:
                logger.error(f"User {user_id} not found or missing clinical profile")
                return {'success': False, 'error': 'User not found'}
            
            # Analyze conversation content
            analysis = self._analyze_conversation(messages)
            
            # Calculate sentiment score (1-10)
            sentiment_score = self._calculate_sentiment_score(analysis)
            
            # Update clinical profile
            updates = {}
            
            # Update emotional state
            if analysis['emotional_state']:
                updates['emotional_state'] = analysis['emotional_state']
            
            # Update conversation preference
            if analysis['conversation_preference']:
                updates['conversation_preference'] = analysis['conversation_preference']
            
            # Update self-harm risk signal
            if analysis['self_harm_risk']:
                updates['self_harm_risk_signal'] = analysis['self_harm_risk']
            
            # Update overall user risk
            if analysis['user_risk']:
                updates['user_risk'] = analysis['user_risk']
            
            # Update last session timestamp
            updates['last_session_timestamp'] = datetime.utcnow()
            
            # Apply updates
            success = self.user_repo.update_clinical_profile(user_id, updates)
            
            # Update session with sentiment score
            session_repo = SessionRepository()
            session_repo.update_session_sentiment_score(session_id, sentiment_score)
            
            # Create red flags if needed
            red_flags_created = []
            if analysis['red_flags']:
                for flag_data in analysis['red_flags']:
                    red_flag = RedFlag(
                        session_id=session_id,
                        flag_id=f"{int(datetime.utcnow().timestamp() * 1000)}",
                        type=flag_data['type'],
                        severity=flag_data['severity'],
                        context=flag_data['context']
                    )
                    if self.red_flag_repo.create_red_flag(red_flag):
                        red_flags_created.append(red_flag.flag_id)
            
            return {
                'success': success,
                'sentiment_score': sentiment_score,
                'updates_applied': updates,
                'red_flags_created': red_flags_created,
                'analysis_summary': analysis['summary']
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze session {session_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_conversation(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze conversation content using pattern matching and keyword detection
        
        This is a simplified analysis - in production, use Bedrock for AI analysis
        """
        user_messages = [msg['content'].lower() for msg in messages if msg['role'] == 'user']
        full_text = ' '.join(user_messages)
        
        analysis = {
            'emotional_state': None,
            'conversation_preference': None,
            'self_harm_risk': None,
            'user_risk': None,
            'red_flags': [],
            'summary': {}
        }
        
        # Detect emotional state
        emotional_keywords = {
            EmotionalState.FEAR: ['scared', 'afraid', 'terrified', 'frightened', 'panic'],
            EmotionalState.SHAME: ['ashamed', 'embarrassed', 'humiliated', 'disgrace'],
            EmotionalState.GUILT: ['guilty', 'fault', 'blame myself', 'regret'],
            EmotionalState.CONFUSION: ['confused', 'don\'t understand', 'lost', 'unclear'],
            EmotionalState.ANGER: ['angry', 'furious', 'rage', 'mad', 'frustrated'],
            EmotionalState.SADNESS: ['sad', 'depressed', 'down', 'miserable', 'unhappy'],
            EmotionalState.HOPELESSNESS: ['hopeless', 'no point', 'give up', 'pointless'],
            EmotionalState.ANXIETY: ['anxious', 'worried', 'nervous', 'stress', 'overwhelmed'],
            EmotionalState.NUMBNESS: ['numb', 'empty', 'nothing', 'disconnected', 'detached'],
            EmotionalState.LOW_SELF_ESTEEM: ['worthless', 'useless', 'failure', 'not good enough']
        }
        
        emotion_scores = {}
        for emotion, keywords in emotional_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            analysis['emotional_state'] = max(emotion_scores, key=emotion_scores.get)
            analysis['summary']['detected_emotions'] = list(emotion_scores.keys())
        
        # Detect conversation preference
        preference_keywords = {
            ConversationPreference.JUST_LISTENING: ['just listen', 'hear me', 'need to talk'],
            ConversationPreference.COPING_TOOLS: ['how to cope', 'strategies', 'techniques', 'help me deal'],
            ConversationPreference.CHECK_IN: ['how am i doing', 'check in', 'progress'],
            ConversationPreference.VENTING: ['vent', 'get it out', 'need to express'],
            ConversationPreference.SELF_COMPASSION: ['be kind to myself', 'self-care', 'forgive myself']
        }
        
        for preference, keywords in preference_keywords.items():
            if any(keyword in full_text for keyword in keywords):
                analysis['conversation_preference'] = preference
                break
        
        # Detect self-harm risk
        self_harm_keywords = {
            'acute': ['want to die', 'kill myself', 'end it all', 'suicide plan'],
            'concerning': ['hurt myself', 'self-harm', 'cut myself', 'harm'],
            'passive': ['better off dead', 'wish i wasn\'t here', 'don\'t want to exist']
        }
        
        for level, keywords in self_harm_keywords.items():
            if any(keyword in full_text for keyword in keywords):
                if level == 'acute':
                    analysis['self_harm_risk'] = SelfHarmRiskSignal.ACUTE
                    analysis['user_risk'] = UserRisk.HIGH
                    analysis['red_flags'].append({
                        'type': RedFlagType.SUICIDAL_IDEATION,
                        'severity': Severity.CRITICAL,
                        'context': 'Acute suicidal ideation detected in session'
                    })
                elif level == 'concerning':
                    analysis['self_harm_risk'] = SelfHarmRiskSignal.CONCERNING
                    analysis['user_risk'] = UserRisk.MEDIUM
                    analysis['red_flags'].append({
                        'type': RedFlagType.SELF_HARM,
                        'severity': Severity.HIGH,
                        'context': 'Self-harm indicators detected in session'
                    })
                elif level == 'passive':
                    analysis['self_harm_risk'] = SelfHarmRiskSignal.PASSIVE
                    if not analysis['user_risk']:
                        analysis['user_risk'] = UserRisk.MEDIUM
                break
        
        # Detect abuse indicators
        abuse_keywords = ['abuse', 'hit me', 'hurt me', 'control', 'threatened']
        if any(keyword in full_text for keyword in abuse_keywords):
            analysis['red_flags'].append({
                'type': RedFlagType.ABUSE,
                'severity': Severity.HIGH,
                'context': 'Potential abuse indicators detected in session'
            })
            if not analysis['user_risk']:
                analysis['user_risk'] = UserRisk.MEDIUM
        
        # Detect violence indicators
        violence_keywords = ['violent', 'hurt someone', 'attack', 'weapon']
        if any(keyword in full_text for keyword in violence_keywords):
            analysis['red_flags'].append({
                'type': RedFlagType.VIOLENCE,
                'severity': Severity.HIGH,
                'context': 'Violence indicators detected in session'
            })
            if not analysis['user_risk']:
                analysis['user_risk'] = UserRisk.MEDIUM
        
        # Detect crisis
        crisis_keywords = ['crisis', 'emergency', 'can\'t cope', 'breaking down']
        if any(keyword in full_text for keyword in crisis_keywords):
            analysis['red_flags'].append({
                'type': RedFlagType.CRISIS,
                'severity': Severity.HIGH,
                'context': 'Crisis state detected in session'
            })
            if not analysis['user_risk']:
                analysis['user_risk'] = UserRisk.HIGH
        
        # Default risk if none detected
        if not analysis['self_harm_risk']:
            analysis['self_harm_risk'] = SelfHarmRiskSignal.NONE
        
        if not analysis['user_risk']:
            analysis['user_risk'] = UserRisk.LOW
        
        analysis['summary']['total_messages'] = len(user_messages)
        analysis['summary']['red_flags_detected'] = len(analysis['red_flags'])
        
        return analysis
    
    def _calculate_sentiment_score(self, analysis: Dict[str, Any]) -> int:
        """
        Calculate sentiment score (1-10) based on analysis
        
        Score interpretation:
        1-3: Very negative (high risk, severe emotional distress)
        4-5: Negative (concerning patterns, moderate distress)
        6-7: Neutral to slightly positive (stable, some challenges)
        8-9: Positive (improving, good coping)
        10: Very positive (excellent progress, strong wellbeing)
        """
        score = 5  # Start at neutral
        
        # Adjust based on emotional state
        emotional_adjustments = {
            EmotionalState.HOPELESSNESS: -3,
            EmotionalState.SADNESS: -2,
            EmotionalState.FEAR: -2,
            EmotionalState.ANXIETY: -1,
            EmotionalState.ANGER: -1,
            EmotionalState.GUILT: -1,
            EmotionalState.SHAME: -2,
            EmotionalState.NUMBNESS: -2,
            EmotionalState.LOW_SELF_ESTEEM: -2,
            EmotionalState.CONFUSION: -1
        }
        
        if analysis['emotional_state']:
            score += emotional_adjustments.get(analysis['emotional_state'], 0)
        
        # Adjust based on self-harm risk
        risk_adjustments = {
            SelfHarmRiskSignal.ACUTE: -4,
            SelfHarmRiskSignal.CONCERNING: -3,
            SelfHarmRiskSignal.PASSIVE: -2,
            SelfHarmRiskSignal.NONE: +1
        }
        
        if analysis['self_harm_risk']:
            score += risk_adjustments.get(analysis['self_harm_risk'], 0)
        
        # Adjust based on overall user risk
        user_risk_adjustments = {
            UserRisk.HIGH: -2,
            UserRisk.MEDIUM: -1,
            UserRisk.LOW: +1
        }
        
        if analysis['user_risk']:
            score += user_risk_adjustments.get(analysis['user_risk'], 0)
        
        # Adjust based on conversation preference (positive engagement)
        preference_adjustments = {
            ConversationPreference.COPING_TOOLS: +1,  # Actively seeking help
            ConversationPreference.SELF_COMPASSION: +1,  # Positive self-work
            ConversationPreference.CHECK_IN: +1,  # Monitoring progress
            ConversationPreference.VENTING: 0,  # Neutral
            ConversationPreference.JUST_LISTENING: 0  # Neutral
        }
        
        if analysis['conversation_preference']:
            score += preference_adjustments.get(analysis['conversation_preference'], 0)
        
        # Red flags significantly lower score
        if analysis['red_flags']:
            score -= len(analysis['red_flags']) * 2
        
        # Ensure score is within 1-10 range
        score = max(1, min(10, score))
        
        return score
    
    def analyze_with_bedrock(self, user_id: str, session_id: str,
                            messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Advanced analysis using AWS Bedrock (Claude)
        Use this for production - more accurate than keyword matching
        """
        # TODO: Implement Bedrock integration
        # Use Claude Sonnet 4.5 for analysis
        # Rate limit: Stay below 1 RPS
        pass
