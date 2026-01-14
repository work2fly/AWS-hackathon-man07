"""
Sentiment Analysis Service for AI Therapy Platform
Implements AI-powered sentiment analysis using session context
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from ..models.session import (
    TherapySession, SentimentSummary, SentimentType, RiskLevel,
    ProgressIndicator
)
from ..utils.logger import get_logger
from ..config.aws_config import get_aws_config

logger = get_logger(__name__)


class SentimentAnalysisService:
    """Service for AI-powered sentiment analysis of therapy sessions"""
    
    def __init__(self):
        """Initialize sentiment analysis service with AWS Bedrock client"""
        config = get_aws_config()
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=config.get('region', 'us-west-2')
        )
        self.model_id = "anthropic.claude-sonnet-4-5-v2:0"  # Permitted model for hackathon
        
    def analyze_session_sentiment(self, session: TherapySession, 
                                  conversation_context: Optional[str] = None) -> Optional[SentimentSummary]:
        """
        Analyze sentiment and therapeutic progress for a completed session
        
        Args:
            session: TherapySession object to analyze
            conversation_context: Optional conversation context from AgentCore memory
            
        Returns:
            SentimentSummary object if successful, None otherwise
        """
        try:
            # Build analysis prompt
            prompt = self._build_sentiment_analysis_prompt(session, conversation_context)
            
            # Call Bedrock for sentiment analysis
            response = self._call_bedrock_for_analysis(prompt)
            
            if not response:
                logger.error(f"Failed to get Bedrock response for session {session.session_id}")
                return None
            
            # Parse response and create sentiment summary
            sentiment_summary = self._parse_sentiment_response(response, session)
            
            logger.info(f"Sentiment analysis completed for session {session.session_id}")
            return sentiment_summary
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment for session {session.session_id}: {str(e)}")
            return None
    
    def _build_sentiment_analysis_prompt(self, session: TherapySession, 
                                        conversation_context: Optional[str]) -> str:
        """Build prompt for sentiment analysis"""
        
        # Extract session metadata
        milestones = ', '.join(session.metadata.therapeutic_milestones) if session.metadata.therapeutic_milestones else 'None'
        exercises = ', '.join(session.metadata.exercises_completed) if session.metadata.exercises_completed else 'None'
        duration_minutes = (session.duration // 60) if session.duration else 0
        
        prompt = f"""You are a clinical psychologist analyzing a therapy session for therapeutic progress and client wellbeing.

Session Information:
- Session ID: {session.session_id}
- Duration: {duration_minutes} minutes
- Language: {session.language}
- Therapeutic Milestones Achieved: {milestones}
- Exercises Completed: {exercises}

"""
        
        if conversation_context:
            prompt += f"""Conversation Context Summary:
{conversation_context}

"""
        
        prompt += """Please analyze this therapy session and provide:

1. Overall Sentiment: Classify as 'positive', 'neutral', or 'negative'
2. Emotional States: List 3-5 emotional states observed (e.g., anxious, hopeful, frustrated, calm)
3. Key Topics: List 3-5 main topics discussed
4. Risk Level: Assess as 'low', 'medium', or 'high' based on client wellbeing
5. Progress Indicators: Provide 2-4 specific therapeutic progress metrics with scores (0.0 to 1.0)

Format your response as JSON:
{
  "overall_sentiment": "positive|neutral|negative",
  "emotional_state": ["emotion1", "emotion2", ...],
  "key_topics": ["topic1", "topic2", ...],
  "risk_level": "low|medium|high",
  "progress_indicators": [
    {
      "metric_name": "Emotional Regulation",
      "value": 0.75,
      "description": "Client demonstrated improved ability to identify and manage emotions"
    }
  ]
}

Provide only the JSON response, no additional text."""
        
        return prompt
    
    def _call_bedrock_for_analysis(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Call AWS Bedrock for sentiment analysis
        
        Args:
            prompt: Analysis prompt
            
        Returns:
            Parsed response dictionary or None
        """
        try:
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.3,  # Lower temperature for more consistent analysis
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Call Bedrock with rate limiting consideration
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content from Claude response
            if 'content' in response_body and len(response_body['content']) > 0:
                content_text = response_body['content'][0]['text']
                
                # Parse JSON from response
                # Handle potential markdown code blocks
                if '```json' in content_text:
                    content_text = content_text.split('```json')[1].split('```')[0].strip()
                elif '```' in content_text:
                    content_text = content_text.split('```')[1].split('```')[0].strip()
                
                return json.loads(content_text)
            
            logger.error("No content in Bedrock response")
            return None
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ThrottlingException':
                logger.warning("Bedrock API throttled - rate limit exceeded")
            else:
                logger.error(f"Bedrock API error: {error_code} - {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bedrock response as JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to call Bedrock for analysis: {str(e)}")
            return None
    
    def _parse_sentiment_response(self, response: Dict[str, Any], 
                                  session: TherapySession) -> SentimentSummary:
        """
        Parse Bedrock response into SentimentSummary object
        
        Args:
            response: Parsed JSON response from Bedrock
            session: Original session object
            
        Returns:
            SentimentSummary object
        """
        try:
            # Parse overall sentiment
            sentiment_str = response.get('overall_sentiment', 'neutral').lower()
            overall_sentiment = SentimentType(sentiment_str)
            
            # Parse emotional states
            emotional_state = response.get('emotional_state', [])
            if not isinstance(emotional_state, list):
                emotional_state = []
            
            # Parse key topics
            key_topics = response.get('key_topics', [])
            if not isinstance(key_topics, list):
                key_topics = []
            
            # Parse risk level
            risk_str = response.get('risk_level', 'low').lower()
            risk_level = RiskLevel(risk_str)
            
            # Parse progress indicators
            progress_indicators = []
            for pi_data in response.get('progress_indicators', []):
                try:
                    progress_indicator = ProgressIndicator(
                        metric_name=pi_data.get('metric_name', 'Unknown Metric'),
                        value=float(pi_data.get('value', 0.5)),
                        description=pi_data.get('description', 'No description provided'),
                        timestamp=datetime.utcnow()
                    )
                    progress_indicators.append(progress_indicator)
                except Exception as e:
                    logger.warning(f"Failed to parse progress indicator: {str(e)}")
                    continue
            
            # Create sentiment summary
            sentiment_summary = SentimentSummary(
                overall_sentiment=overall_sentiment,
                emotional_state=emotional_state,
                progress_indicators=progress_indicators,
                key_topics=key_topics,
                risk_level=risk_level,
                generated_at=datetime.utcnow()
            )
            
            return sentiment_summary
            
        except Exception as e:
            logger.error(f"Failed to parse sentiment response: {str(e)}")
            # Return default sentiment summary
            return SentimentSummary(
                overall_sentiment=SentimentType.NEUTRAL,
                emotional_state=[],
                progress_indicators=[],
                key_topics=[],
                risk_level=RiskLevel.LOW,
                generated_at=datetime.utcnow()
            )
    
    def detect_therapeutic_milestones(self, session: TherapySession,
                                     conversation_context: Optional[str] = None) -> List[str]:
        """
        Detect therapeutic milestones achieved during session
        
        Args:
            session: TherapySession object
            conversation_context: Optional conversation context
            
        Returns:
            List of milestone descriptions
        """
        try:
            prompt = f"""Analyze this therapy session and identify any therapeutic milestones achieved.

Session Duration: {(session.duration // 60) if session.duration else 0} minutes
Language: {session.language}

"""
            
            if conversation_context:
                prompt += f"""Conversation Context:
{conversation_context}

"""
            
            prompt += """Therapeutic milestones might include:
- First time discussing a difficult topic
- Breakthrough in understanding a pattern
- Successful use of a coping strategy
- Improved emotional regulation
- Progress toward treatment goals
- Increased self-awareness

List 0-3 specific milestones achieved in this session. Format as JSON array:
["milestone 1", "milestone 2", ...]

Provide only the JSON array, no additional text."""
            
            response = self._call_bedrock_for_analysis(prompt)
            
            if response and isinstance(response, list):
                return response
            elif response and 'milestones' in response:
                return response['milestones']
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to detect therapeutic milestones: {str(e)}")
            return []
    
    def analyze_progress_trends(self, sessions: List[TherapySession]) -> Dict[str, Any]:
        """
        Analyze therapeutic progress trends across multiple sessions
        
        Args:
            sessions: List of TherapySession objects with sentiment summaries
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            if not sessions:
                return {
                    'trend': 'insufficient_data',
                    'sessions_analyzed': 0,
                    'message': 'No sessions provided for trend analysis'
                }
            
            # Filter sessions with sentiment summaries
            sessions_with_sentiment = [s for s in sessions if s.sentiment_summary]
            
            if len(sessions_with_sentiment) < 2:
                return {
                    'trend': 'insufficient_data',
                    'sessions_analyzed': len(sessions_with_sentiment),
                    'message': 'At least 2 sessions with sentiment analysis required'
                }
            
            # Sort by timestamp
            sorted_sessions = sorted(sessions_with_sentiment, key=lambda x: x.timestamp)
            
            # Analyze sentiment trend
            sentiment_scores = []
            for session in sorted_sessions:
                if session.sentiment_summary.overall_sentiment == SentimentType.POSITIVE:
                    sentiment_scores.append(1.0)
                elif session.sentiment_summary.overall_sentiment == SentimentType.NEUTRAL:
                    sentiment_scores.append(0.5)
                else:
                    sentiment_scores.append(0.0)
            
            # Calculate trend
            if len(sentiment_scores) >= 2:
                recent_avg = sum(sentiment_scores[-3:]) / len(sentiment_scores[-3:])
                early_avg = sum(sentiment_scores[:3]) / len(sentiment_scores[:3])
                
                if recent_avg > early_avg + 0.2:
                    trend = 'improving'
                elif recent_avg < early_avg - 0.2:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Analyze risk level trend
            risk_levels = [s.sentiment_summary.risk_level for s in sorted_sessions]
            current_risk = risk_levels[-1]
            
            # Collect all progress indicators
            all_progress_metrics = {}
            for session in sorted_sessions:
                if session.sentiment_summary:
                    for pi in session.sentiment_summary.progress_indicators:
                        if pi.metric_name not in all_progress_metrics:
                            all_progress_metrics[pi.metric_name] = []
                        all_progress_metrics[pi.metric_name].append({
                            'value': pi.value,
                            'timestamp': session.timestamp.isoformat()
                        })
            
            return {
                'trend': trend,
                'sessions_analyzed': len(sorted_sessions),
                'sentiment_trajectory': sentiment_scores,
                'current_risk_level': current_risk.value,
                'progress_metrics': all_progress_metrics,
                'period_start': sorted_sessions[0].timestamp.isoformat(),
                'period_end': sorted_sessions[-1].timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze progress trends: {str(e)}")
            return {
                'trend': 'error',
                'sessions_analyzed': 0,
                'error': str(e)
            }
    
    def generate_therapeutic_insights(self, client_id: str, 
                                     sessions: List[TherapySession]) -> Dict[str, Any]:
        """
        Generate comprehensive therapeutic insights for a client
        
        Args:
            client_id: Client identifier
            sessions: List of client's therapy sessions
            
        Returns:
            Dictionary containing therapeutic insights
        """
        try:
            # Filter sessions with sentiment summaries
            analyzed_sessions = [s for s in sessions if s.sentiment_summary]
            
            if not analyzed_sessions:
                return {
                    'client_id': client_id,
                    'insights_available': False,
                    'message': 'No analyzed sessions available for insights'
                }
            
            # Analyze trends
            trends = self.analyze_progress_trends(analyzed_sessions)
            
            # Collect common themes
            all_topics = []
            all_emotions = []
            for session in analyzed_sessions:
                if session.sentiment_summary:
                    all_topics.extend(session.sentiment_summary.key_topics)
                    all_emotions.extend(session.sentiment_summary.emotional_state)
            
            # Count frequency
            topic_frequency = {}
            for topic in all_topics:
                topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
            
            emotion_frequency = {}
            for emotion in all_emotions:
                emotion_frequency[emotion] = emotion_frequency.get(emotion, 0) + 1
            
            # Get top themes
            top_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            top_emotions = sorted(emotion_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Collect all milestones
            all_milestones = set()
            for session in sessions:
                all_milestones.update(session.metadata.therapeutic_milestones)
            
            return {
                'client_id': client_id,
                'insights_available': True,
                'total_sessions': len(sessions),
                'analyzed_sessions': len(analyzed_sessions),
                'progress_trend': trends.get('trend'),
                'current_risk_level': trends.get('current_risk_level'),
                'recurring_topics': [{'topic': t, 'frequency': f} for t, f in top_topics],
                'common_emotions': [{'emotion': e, 'frequency': f} for e, f in top_emotions],
                'milestones_achieved': list(all_milestones),
                'total_milestones': len(all_milestones),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate therapeutic insights for client {client_id}: {str(e)}")
            return {
                'client_id': client_id,
                'insights_available': False,
                'error': str(e)
            }
