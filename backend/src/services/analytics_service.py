"""
Analytics and Insights Service for AI Therapy Platform
Provides system-wide analytics, performance monitoring, and predictive insights
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.session import TherapySession, SentimentType, RiskLevel, SessionStatus
from ..data.session_repository import SessionRepository
from ..services.sentiment_analysis_service import SentimentAnalysisService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Service for system-wide analytics and insights generation"""
    
    def __init__(self):
        self.session_repo = SessionRepository()
        self.sentiment_service = SentimentAnalysisService()
    
    def generate_system_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive system-wide analytics
        
        Args:
            days: Number of days to include in analytics
            
        Returns:
            Dictionary containing system analytics
        """
        try:
            # Get recent sessions
            sessions = self.session_repo.get_recent_sessions(hours=days * 24, limit=10000)
            
            if not sessions:
                return {
                    'period_days': days,
                    'total_sessions': 0,
                    'message': 'No sessions found in the specified period'
                }
            
            # Calculate basic metrics
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.status == SessionStatus.COMPLETED])
            active_sessions = len([s for s in sessions if s.status == SessionStatus.ACTIVE])
            terminated_sessions = len([s for s in sessions if s.status == SessionStatus.TERMINATED])
            
            # Calculate completion rate
            completion_rate = completed_sessions / total_sessions if total_sessions > 0 else 0
            
            # Calculate average session duration
            completed_durations = [s.duration for s in sessions if s.duration and s.status == SessionStatus.COMPLETED]
            avg_duration = sum(completed_durations) / len(completed_durations) if completed_durations else 0
            
            # Unique users
            unique_clients = len(set([s.client_id for s in sessions]))
            
            # Language distribution
            language_distribution = defaultdict(int)
            for session in sessions:
                language_distribution[session.language] += 1
            
            # Sentiment distribution
            sentiment_distribution = {
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'not_analyzed': 0
            }
            
            for session in sessions:
                if session.sentiment_summary:
                    sentiment_distribution[session.sentiment_summary.overall_sentiment.value] += 1
                else:
                    sentiment_distribution['not_analyzed'] += 1
            
            # Risk level distribution
            risk_distribution = {
                'low': 0,
                'medium': 0,
                'high': 0,
                'not_analyzed': 0
            }
            
            for session in sessions:
                if session.sentiment_summary:
                    risk_distribution[session.sentiment_summary.risk_level.value] += 1
                else:
                    risk_distribution['not_analyzed'] += 1
            
            # Daily session counts
            daily_counts = defaultdict(int)
            for session in sessions:
                date_key = session.timestamp.date().isoformat()
                daily_counts[date_key] += 1
            
            # Peak usage analysis
            hourly_counts = defaultdict(int)
            for session in sessions:
                hour_key = session.timestamp.hour
                hourly_counts[hour_key] += 1
            
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else 0
            
            return {
                'period_days': days,
                'period_start': (datetime.utcnow() - timedelta(days=days)).date().isoformat(),
                'period_end': datetime.utcnow().date().isoformat(),
                'session_metrics': {
                    'total_sessions': total_sessions,
                    'completed_sessions': completed_sessions,
                    'active_sessions': active_sessions,
                    'terminated_sessions': terminated_sessions,
                    'completion_rate': round(completion_rate, 3),
                    'average_duration_minutes': int(avg_duration // 60) if avg_duration else 0
                },
                'user_metrics': {
                    'unique_clients': unique_clients,
                    'average_sessions_per_client': round(total_sessions / unique_clients, 2) if unique_clients > 0 else 0
                },
                'language_distribution': dict(language_distribution),
                'sentiment_distribution': sentiment_distribution,
                'risk_distribution': risk_distribution,
                'usage_patterns': {
                    'daily_session_counts': dict(sorted(daily_counts.items())),
                    'peak_usage_hour': peak_hour,
                    'hourly_distribution': dict(sorted(hourly_counts.items()))
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate system analytics: {str(e)}")
            return {
                'period_days': days,
                'error': str(e),
                'success': False
            }
    
    def generate_performance_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate performance monitoring metrics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            # Get recent sessions
            sessions = self.session_repo.get_recent_sessions(hours=days * 24, limit=10000)
            
            if not sessions:
                return {
                    'period_days': days,
                    'message': 'No sessions found for performance analysis'
                }
            
            # Audio quality metrics
            audio_metrics = {
                'average_latency_ms': [],
                'packet_loss_rates': [],
                'audio_clarity_scores': [],
                'connection_stability_scores': []
            }
            
            for session in sessions:
                if session.metadata and session.metadata.audio_quality:
                    aq = session.metadata.audio_quality
                    audio_metrics['average_latency_ms'].append(aq.average_latency_ms)
                    audio_metrics['packet_loss_rates'].append(aq.packet_loss_rate)
                    audio_metrics['audio_clarity_scores'].append(aq.audio_clarity_score)
                    audio_metrics['connection_stability_scores'].append(aq.connection_stability)
            
            # Calculate averages
            avg_audio_metrics = {}
            for key, values in audio_metrics.items():
                if values:
                    avg_audio_metrics[key] = round(sum(values) / len(values), 3)
                else:
                    avg_audio_metrics[key] = 0
            
            # Connection metrics
            connection_metrics = {
                'reconnection_counts': [],
                'average_response_times': [],
                'data_transfer_mb': []
            }
            
            for session in sessions:
                if session.metadata and session.metadata.connection_metrics:
                    cm = session.metadata.connection_metrics
                    connection_metrics['reconnection_counts'].append(cm.reconnection_count)
                    connection_metrics['average_response_times'].append(cm.average_response_time_ms)
                    connection_metrics['data_transfer_mb'].append(cm.data_transfer_mb)
            
            # Calculate connection averages
            avg_connection_metrics = {}
            for key, values in connection_metrics.items():
                if values:
                    avg_connection_metrics[key] = round(sum(values) / len(values), 3)
                else:
                    avg_connection_metrics[key] = 0
            
            # Session completion metrics
            completed_sessions = [s for s in sessions if s.status == SessionStatus.COMPLETED]
            terminated_sessions = [s for s in sessions if s.status == SessionStatus.TERMINATED]
            
            # Calculate success rate
            success_rate = len(completed_sessions) / len(sessions) if sessions else 0
            
            # Identify performance issues
            performance_issues = []
            
            if avg_audio_metrics.get('average_latency_ms', 0) > 200:
                performance_issues.append({
                    'type': 'high_latency',
                    'severity': 'medium',
                    'description': f"Average latency ({avg_audio_metrics['average_latency_ms']}ms) exceeds target (200ms)"
                })
            
            if avg_audio_metrics.get('packet_loss_rates', 0) > 0.05:
                performance_issues.append({
                    'type': 'packet_loss',
                    'severity': 'high',
                    'description': f"Packet loss rate ({avg_audio_metrics['packet_loss_rates']}) exceeds acceptable threshold (5%)"
                })
            
            if success_rate < 0.9:
                performance_issues.append({
                    'type': 'low_completion_rate',
                    'severity': 'medium',
                    'description': f"Session completion rate ({round(success_rate * 100, 1)}%) below target (90%)"
                })
            
            return {
                'period_days': days,
                'sessions_analyzed': len(sessions),
                'audio_quality_metrics': avg_audio_metrics,
                'connection_metrics': avg_connection_metrics,
                'session_success_rate': round(success_rate, 3),
                'performance_issues': performance_issues,
                'performance_score': self._calculate_performance_score(
                    avg_audio_metrics,
                    avg_connection_metrics,
                    success_rate
                ),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance metrics: {str(e)}")
            return {
                'period_days': days,
                'error': str(e),
                'success': False
            }
    
    def _calculate_performance_score(self, audio_metrics: Dict[str, float],
                                    connection_metrics: Dict[str, float],
                                    success_rate: float) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            # Audio quality score (0-40 points)
            latency_score = max(0, 40 - (audio_metrics.get('average_latency_ms', 0) / 10))
            latency_score = min(latency_score, 40)
            
            # Connection quality score (0-30 points)
            stability_score = audio_metrics.get('connection_stability_scores', 0) * 30
            
            # Success rate score (0-30 points)
            success_score = success_rate * 30
            
            total_score = latency_score + stability_score + success_score
            return round(min(total_score, 100), 1)
            
        except Exception as e:
            logger.error(f"Failed to calculate performance score: {str(e)}")
            return 0.0
    
    def generate_predictive_insights(self, client_id: Optional[str] = None,
                                    days: int = 90) -> Dict[str, Any]:
        """
        Generate predictive analytics for therapeutic outcomes
        
        Args:
            client_id: Optional client ID for individual predictions
            days: Number of days of historical data to analyze
            
        Returns:
            Dictionary containing predictive insights
        """
        try:
            if client_id:
                # Get client-specific sessions
                result = self.session_repo.get_sessions_by_client(
                    client_id=client_id,
                    limit=1000
                )
                sessions = result['sessions']
                
                if len(sessions) < 5:
                    return {
                        'client_id': client_id,
                        'prediction_available': False,
                        'message': 'Insufficient session history for predictions (minimum 5 sessions required)'
                    }
                
                # Analyze trends
                trends = self.sentiment_service.analyze_progress_trends(sessions)
                
                # Predict future trajectory
                sentiment_trajectory = trends.get('sentiment_trajectory', [])
                
                if len(sentiment_trajectory) >= 3:
                    # Simple linear trend prediction
                    recent_trend = sentiment_trajectory[-3:]
                    trend_direction = recent_trend[-1] - recent_trend[0]
                    
                    if trend_direction > 0.2:
                        prediction = 'improving'
                        confidence = 'high'
                    elif trend_direction < -0.2:
                        prediction = 'declining'
                        confidence = 'high'
                    else:
                        prediction = 'stable'
                        confidence = 'medium'
                else:
                    prediction = 'insufficient_data'
                    confidence = 'low'
                
                # Identify risk factors
                risk_factors = []
                recent_sessions = sorted(sessions, key=lambda x: x.timestamp, reverse=True)[:5]
                
                high_risk_count = sum(1 for s in recent_sessions 
                                     if s.sentiment_summary and s.sentiment_summary.risk_level == RiskLevel.HIGH)
                
                if high_risk_count >= 2:
                    risk_factors.append({
                        'factor': 'multiple_high_risk_sessions',
                        'severity': 'high',
                        'description': f'{high_risk_count} high-risk sessions in last 5 sessions'
                    })
                
                # Calculate engagement score
                total_duration = sum([s.duration for s in sessions if s.duration]) or 0
                avg_duration = total_duration / len(sessions) if sessions else 0
                engagement_score = min(avg_duration / 1800, 1.0)  # Normalize to 30-minute sessions
                
                return {
                    'client_id': client_id,
                    'prediction_available': True,
                    'predicted_trajectory': prediction,
                    'confidence_level': confidence,
                    'risk_factors': risk_factors,
                    'engagement_score': round(engagement_score, 3),
                    'sessions_analyzed': len(sessions),
                    'current_trend': trends.get('trend'),
                    'recommendations': self._generate_recommendations(
                        prediction, risk_factors, engagement_score
                    ),
                    'generated_at': datetime.utcnow().isoformat()
                }
            else:
                # System-wide predictions
                sessions = self.session_repo.get_recent_sessions(hours=days * 24, limit=10000)
                
                # Analyze system-wide trends
                unique_clients = set([s.client_id for s in sessions])
                
                # Predict system load
                daily_sessions = defaultdict(int)
                for session in sessions:
                    date_key = session.timestamp.date().isoformat()
                    daily_sessions[date_key] += 1
                
                if len(daily_sessions) >= 7:
                    recent_avg = sum(list(daily_sessions.values())[-7:]) / 7
                    predicted_daily_load = int(recent_avg * 1.1)  # 10% growth assumption
                else:
                    predicted_daily_load = 0
                
                return {
                    'prediction_type': 'system_wide',
                    'prediction_available': True,
                    'predicted_daily_session_load': predicted_daily_load,
                    'active_clients': len(unique_clients),
                    'sessions_analyzed': len(sessions),
                    'generated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to generate predictive insights: {str(e)}")
            return {
                'client_id': client_id,
                'prediction_available': False,
                'error': str(e)
            }
    
    def _generate_recommendations(self, prediction: str, risk_factors: List[Dict],
                                 engagement_score: float) -> List[str]:
        """Generate recommendations based on predictions"""
        recommendations = []
        
        if prediction == 'declining':
            recommendations.append("Consider scheduling a check-in session to address recent challenges")
            recommendations.append("Review recent session topics for emerging concerns")
        
        if risk_factors:
            recommendations.append("Immediate therapist review recommended due to identified risk factors")
        
        if engagement_score < 0.5:
            recommendations.append("Low engagement detected - consider adjusting session format or frequency")
        
        if prediction == 'improving':
            recommendations.append("Positive progress trend - continue current therapeutic approach")
        
        return recommendations
    
    def export_analytics_data(self, export_type: str, 
                             parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export analytics data in various formats
        
        Args:
            export_type: Type of export ('csv', 'json', 'summary')
            parameters: Export parameters
            
        Returns:
            Dictionary containing exported data
        """
        try:
            days = parameters.get('days', 30)
            include_details = parameters.get('include_details', False)
            
            # Generate analytics
            analytics = self.generate_system_analytics(days=days)
            performance = self.generate_performance_metrics(days=min(days, 7))
            
            export_data = {
                'export_type': export_type,
                'export_timestamp': datetime.utcnow().isoformat(),
                'period_days': days,
                'system_analytics': analytics,
                'performance_metrics': performance
            }
            
            if include_details:
                # Add detailed session data
                sessions = self.session_repo.get_recent_sessions(hours=days * 24, limit=1000)
                export_data['session_count'] = len(sessions)
                export_data['detailed_sessions'] = [
                    {
                        'session_id': s.session_id,
                        'timestamp': s.timestamp.isoformat(),
                        'status': s.status.value,
                        'duration': s.duration,
                        'language': s.language
                    }
                    for s in sessions
                ]
            
            return {
                'success': True,
                'export_type': export_type,
                'data': export_data,
                'size_bytes': len(str(export_data))
            }
            
        except Exception as e:
            logger.error(f"Failed to export analytics data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_usage_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive usage report
        
        Args:
            days: Number of days to include
            
        Returns:
            Dictionary containing usage metrics
        """
        try:
            sessions = self.session_repo.get_recent_sessions(hours=days * 24, limit=10000)
            
            # Calculate usage metrics
            total_sessions = len(sessions)
            unique_clients = len(set([s.client_id for s in sessions]))
            
            # Time-based analysis
            weekday_counts = defaultdict(int)
            for session in sessions:
                weekday = session.timestamp.strftime('%A')
                weekday_counts[weekday] += 1
            
            # Duration analysis
            duration_buckets = {
                '0-10min': 0,
                '10-20min': 0,
                '20-30min': 0,
                '30-45min': 0,
                '45min+': 0
            }
            
            for session in sessions:
                if session.duration:
                    minutes = session.duration // 60
                    if minutes < 10:
                        duration_buckets['0-10min'] += 1
                    elif minutes < 20:
                        duration_buckets['10-20min'] += 1
                    elif minutes < 30:
                        duration_buckets['20-30min'] += 1
                    elif minutes < 45:
                        duration_buckets['30-45min'] += 1
                    else:
                        duration_buckets['45min+'] += 1
            
            return {
                'period_days': days,
                'total_sessions': total_sessions,
                'unique_clients': unique_clients,
                'sessions_per_client': round(total_sessions / unique_clients, 2) if unique_clients > 0 else 0,
                'weekday_distribution': dict(weekday_counts),
                'duration_distribution': duration_buckets,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate usage report: {str(e)}")
            return {
                'period_days': days,
                'error': str(e),
                'success': False
            }
