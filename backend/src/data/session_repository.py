"""
Session repository for DynamoDB operations
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .base import BaseRepository, DynamoDBError
from ..models.session import TherapySession, SessionStatus, SentimentSummary
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionRepository(BaseRepository):
    """Repository for TherapySession operations"""
    
    def __init__(self):
        super().__init__("sessions")
    
    def create_session(self, session: TherapySession) -> bool:
        """Create a new therapy session"""
        try:
            # Convert to DynamoDB format
            item = session.to_dynamodb_item()
            
            # Use condition to prevent overwriting existing sessions
            condition = "attribute_not_exists(sessionId)"
            
            return self.put_item(item, condition)
            
        except Exception as e:
            logger.error(f"Failed to create session {session.session_id}: {str(e)}")
            return False
    
    def get_session_by_id(self, session_id: str, timestamp: str) -> Optional[TherapySession]:
        """Get session by ID and timestamp"""
        try:
            key = {
                'sessionId': session_id,
                'timestamp': timestamp
            }
            item = self.get_item(key)
            
            if item:
                return TherapySession.from_dynamodb_item(item)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {str(e)}")
            return None
    
    def get_sessions_by_client(self, client_id: str, limit: Optional[int] = None,
                              exclusive_start_key: Optional[Dict[str, Any]] = None,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get sessions for a specific client"""
        try:
            key_condition = "GSI1PK = :client_id"
            expression_values = {":client_id": client_id}
            
            # Add date range filtering if provided
            if start_date and end_date:
                key_condition += " AND GSI1SK BETWEEN :start_date AND :end_date"
                expression_values[":start_date"] = start_date.isoformat()
                expression_values[":end_date"] = end_date.isoformat()
            elif start_date:
                key_condition += " AND GSI1SK >= :start_date"
                expression_values[":start_date"] = start_date.isoformat()
            elif end_date:
                key_condition += " AND GSI1SK <= :end_date"
                expression_values[":end_date"] = end_date.isoformat()
            
            response = self.query(
                key_condition_expression=key_condition,
                expression_attribute_values=expression_values,
                index_name="ClientIndex",
                limit=limit,
                scan_index_forward=False,  # Most recent first
                exclusive_start_key=exclusive_start_key
            )
            
            # Convert items to TherapySession objects
            sessions = []
            for item in response.get('Items', []):
                try:
                    session = TherapySession.from_dynamodb_item(item)
                    sessions.append(session)
                except Exception as e:
                    logger.warning(f"Failed to parse session item: {str(e)}")
                    continue
            
            return {
                'sessions': sessions,
                'count': len(sessions),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
        except Exception as e:
            logger.error(f"Failed to get sessions for client {client_id}: {str(e)}")
            return {'sessions': [], 'count': 0, 'last_evaluated_key': None}
    
    def update_session_status(self, session_id: str, timestamp: str, 
                             status: SessionStatus, end_time: Optional[datetime] = None,
                             duration: Optional[int] = None) -> bool:
        """Update session status"""
        try:
            key = {
                'sessionId': session_id,
                'timestamp': timestamp
            }
            
            update_expression = "SET #status = :status"
            expression_attribute_names = {"#status": "status"}
            expression_attribute_values = {":status": status.value}
            
            if end_time:
                update_expression += ", endTime = :end_time"
                expression_attribute_values[":end_time"] = end_time.isoformat()
            
            if duration:
                update_expression += ", duration = :duration"
                expression_attribute_values[":duration"] = duration
            
            condition = "attribute_exists(sessionId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                expression_attribute_names=expression_attribute_names,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to update session status {session_id}: {str(e)}")
            return False
    
    def add_sentiment_summary(self, session_id: str, timestamp: str, 
                             sentiment_summary: SentimentSummary) -> bool:
        """Add sentiment summary to session"""
        try:
            key = {
                'sessionId': session_id,
                'timestamp': timestamp
            }
            
            # Convert sentiment summary to DynamoDB format
            progress_indicators = []
            for pi in sentiment_summary.progress_indicators:
                progress_indicators.append({
                    'metricName': pi.metric_name,
                    'value': pi.value,
                    'description': pi.description,
                    'timestamp': pi.timestamp.isoformat()
                })
            
            sentiment_data = {
                'overallSentiment': sentiment_summary.overall_sentiment.value,
                'emotionalState': sentiment_summary.emotional_state,
                'progressIndicators': progress_indicators,
                'keyTopics': sentiment_summary.key_topics,
                'riskLevel': sentiment_summary.risk_level.value,
                'generatedAt': sentiment_summary.generated_at.isoformat()
            }
            
            update_expression = "SET sentimentSummary = :sentiment"
            expression_attribute_values = {":sentiment": sentiment_data}
            condition = "attribute_exists(sessionId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to add sentiment summary to session {session_id}: {str(e)}")
            return False
    
    def get_active_sessions(self, limit: Optional[int] = None) -> List[TherapySession]:
        """Get all active sessions"""
        try:
            response = self.scan(
                filter_expression="#status = :status",
                expression_attribute_names={"#status": "status"},
                expression_attribute_values={":status": SessionStatus.ACTIVE.value},
                limit=limit
            )
            
            sessions = []
            for item in response.get('Items', []):
                try:
                    session = TherapySession.from_dynamodb_item(item)
                    sessions.append(session)
                except Exception as e:
                    logger.warning(f"Failed to parse session item: {str(e)}")
                    continue
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get active sessions: {str(e)}")
            return []
    
    def get_recent_sessions(self, hours: int = 24, limit: Optional[int] = None) -> List[TherapySession]:
        """Get recent sessions within specified hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            response = self.scan(
                filter_expression="#timestamp >= :cutoff_time",
                expression_attribute_names={"#timestamp": "timestamp"},
                expression_attribute_values={":cutoff_time": cutoff_time.isoformat()},
                limit=limit
            )
            
            sessions = []
            for item in response.get('Items', []):
                try:
                    session = TherapySession.from_dynamodb_item(item)
                    sessions.append(session)
                except Exception as e:
                    logger.warning(f"Failed to parse session item: {str(e)}")
                    continue
            
            # Sort by timestamp (most recent first)
            sessions.sort(key=lambda x: x.timestamp, reverse=True)
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get recent sessions: {str(e)}")
            return []
    
    def update_session_metadata(self, session_id: str, timestamp: str,
                               therapeutic_milestones: Optional[List[str]] = None,
                               exercises_completed: Optional[List[str]] = None) -> bool:
        """Update session metadata"""
        try:
            key = {
                'sessionId': session_id,
                'timestamp': timestamp
            }
            
            update_parts = []
            expression_values = {}
            
            if therapeutic_milestones is not None:
                update_parts.append("metadata.therapeuticMilestones = :milestones")
                expression_values[":milestones"] = therapeutic_milestones
            
            if exercises_completed is not None:
                update_parts.append("metadata.exercisesCompleted = :exercises")
                expression_values[":exercises"] = exercises_completed
            
            if not update_parts:
                return True  # Nothing to update
            
            update_expression = "SET " + ", ".join(update_parts)
            condition = "attribute_exists(sessionId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to update session metadata {session_id}: {str(e)}")
            return False
    
    def delete_session(self, session_id: str, timestamp: str) -> bool:
        """Delete session (GDPR compliance)"""
        try:
            key = {
                'sessionId': session_id,
                'timestamp': timestamp
            }
            condition = "attribute_exists(sessionId)"
            
            return self.delete_item(key, condition)
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            return False
    
    def get_sessions_for_sentiment_analysis(self, limit: Optional[int] = None) -> List[TherapySession]:
        """Get completed sessions without sentiment summaries"""
        try:
            response = self.scan(
                filter_expression="#status = :status AND attribute_not_exists(sentimentSummary)",
                expression_attribute_names={"#status": "status"},
                expression_attribute_values={":status": SessionStatus.COMPLETED.value},
                limit=limit
            )
            
            sessions = []
            for item in response.get('Items', []):
                try:
                    session = TherapySession.from_dynamodb_item(item)
                    sessions.append(session)
                except Exception as e:
                    logger.warning(f"Failed to parse session item: {str(e)}")
                    continue
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get sessions for sentiment analysis: {str(e)}")
            return []
    
    def update_session_sentiment_score(self, session_id: str, sentiment_score: int) -> bool:
        """
        Update session sentiment score (1-10)
        
        Args:
            session_id: Session identifier
            sentiment_score: Score from 1-10 indicating user sentiment
        """
        try:
            # Query to find the session by sessionId (need timestamp for key)
            response = self.query(
                key_condition_expression="sessionId = :session_id",
                expression_attribute_values={":session_id": session_id},
                limit=1
            )
            
            items = response.get('Items', [])
            if not items:
                logger.error(f"Session {session_id} not found")
                return False
            
            # Get timestamp from the found item
            timestamp = items[0]['timestamp']['S']
            
            key = {
                'sessionId': session_id,
                'timestamp': timestamp
            }
            
            update_expression = "SET sentimentScore = :score"
            expression_attribute_values = {":score": sentiment_score}
            condition = "attribute_exists(sessionId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to update sentiment score for session {session_id}: {str(e)}")
            return False
    
    def get_sentiment_score_history(self, client_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get sentiment score history for a client (for progress tracking)
        
        Returns list of {session_id, timestamp, sentiment_score, status}
        """
        try:
            response = self.query(
                key_condition_expression="GSI1PK = :client_id",
                expression_attribute_values={":client_id": client_id},
                index_name="ClientIndex",
                limit=limit,
                scan_index_forward=True  # Oldest first for chronological order
            )
            
            history = []
            for item in response.get('Items', []):
                if 'sentimentScore' in item:
                    history.append({
                        'session_id': item['sessionId']['S'],
                        'timestamp': item['timestamp']['S'],
                        'sentiment_score': int(item['sentimentScore']['N']),
                        'status': item['status']['S'],
                        'duration': int(item['duration']['N']) if 'duration' in item else None
                    })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get sentiment score history for client {client_id}: {str(e)}")
            return []