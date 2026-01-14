"""
Therapist Reporting Service for AI Therapy Platform
Provides privacy-compliant reporting and insights for therapists
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from ..models.session import TherapySession, SentimentType, RiskLevel
from ..data.session_repository import SessionRepository
from ..services.sentiment_analysis_service import SentimentAnalysisService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TherapistReportingService:
    """Service for generating therapist-facing reports and dashboards"""
    
    def __init__(self):
        self.session_repo = SessionRepository()
        self.sentiment_service = SentimentAnalysisService()
    
    def generate_client_summary(self, client_id: str, therapist_id: str,
                               days: int = 30) -> Dict[str, Any]:
        """
        Generate privacy-compliant client summary for therapist
        
        Args:
            client_id: Client identifier
            therapist_id: Therapist identifier (for access control)
            days: Number of days to include in summary
            
        Returns:
            Dictionary containing client summary (no full transcripts)
        """
        try:
            # Get client sessions
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            result = self.session_repo.get_sessions_by_client(
                client_id=client_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
            sessions = result['sessions']
            
            if not sessions:
                return {
                    'client_id': client_id,
                    'therapist_id': therapist_id,
                    'period_days': days,
                    'sessions_found': 0,
                    'message': 'No sessions found for this client in the specified period'
                }
            
            # Generate insights
            insights = self.sentiment_service.generate_therapeutic_insights(
                client_id=client_id,
                sessions=sessions
            )
            
            # Calculate session statistics
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.status.value == 'completed'])
            total_duration = sum([s.duration for s in sessions if s.duration]) or 0
            avg_duration = total_duration / completed_sessions if completed_sessions > 0 else 0
            
            # Get recent sentiment summaries (privacy-compliant)
            recent_summaries = []
            for session in sorted(sessions, key=lambda x: x.timestamp, reverse=True)[:10]:
                if session.sentiment_summary:
                    recent_summaries.append({
                        'session_id': session.session_id,
                        'date': session.timestamp.date().isoformat(),
                        'duration_minutes': (session.duration // 60) if session.duration else 0,
                        'overall_sentiment': session.sentiment_summary.overall_sentiment.value,
                        'emotional_state': session.sentiment_summary.emotional_state,
                        'key_topics': session.sentiment_summary.key_topics,
                        'risk_level': session.sentiment_summary.risk_level.value,
                        'progress_indicators': [
                            {
                                'metric': pi.metric_name,
                                'score': pi.value,
                                'description': pi.description
                            }
                            for pi in session.sentiment_summary.progress_indicators
                        ]
                    })
            
            # Identify sessions requiring attention
            high_risk_sessions = []
            for session in sessions:
                if session.sentiment_summary and session.sentiment_summary.risk_level == RiskLevel.HIGH:
                    high_risk_sessions.append({
                        'session_id': session.session_id,
                        'date': session.timestamp.date().isoformat(),
                        'risk_level': session.sentiment_summary.risk_level.value,
                        'key_topics': session.sentiment_summary.key_topics
                    })
            
            return {
                'client_id': client_id,
                'therapist_id': therapist_id,
                'period_days': days,
                'period_start': start_date.date().isoformat(),
                'period_end': end_date.date().isoformat(),
                'session_statistics': {
                    'total_sessions': total_sessions,
                    'completed_sessions': completed_sessions,
                    'total_duration_minutes': total_duration // 60,
                    'average_duration_minutes': int(avg_duration // 60)
                },
                'therapeutic_insights': insights,
                'recent_session_summaries': recent_summaries,
                'sessions_requiring_attention': high_risk_sessions,
                'generated_at': datetime.utcnow().isoformat(),
                'privacy_note': 'This report contains sentiment summaries only. Full conversation transcripts are not included to maintain client privacy.'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate client summary for therapist {therapist_id}: {str(e)}")
            return {
                'client_id': client_id,
                'therapist_id': therapist_id,
                'error': str(e),
                'success': False
            }
    
    def generate_dashboard_data(self, therapist_id: str, 
                               assigned_clients: List[str]) -> Dict[str, Any]:
        """
        Generate dashboard data for therapist overview
        
        Args:
            therapist_id: Therapist identifier
            assigned_clients: List of client IDs assigned to this therapist
            
        Returns:
            Dictionary containing dashboard metrics
        """
        try:
            # Get recent sessions for all assigned clients
            recent_sessions = []
            for client_id in assigned_clients:
                result = self.session_repo.get_sessions_by_client(
                    client_id=client_id,
                    limit=50
                )
                recent_sessions.extend(result['sessions'])
            
            # Sort by timestamp
            recent_sessions.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Calculate metrics
            total_clients = len(assigned_clients)
            active_clients = len(set([s.client_id for s in recent_sessions 
                                     if (datetime.utcnow() - s.timestamp).days <= 7]))
            
            # Count sessions by status
            completed_today = len([s for s in recent_sessions 
                                  if s.status.value == 'completed' 
                                  and s.timestamp.date() == datetime.utcnow().date()])
            
            # Identify high-risk clients
            high_risk_clients = set()
            for session in recent_sessions:
                if session.sentiment_summary and session.sentiment_summary.risk_level == RiskLevel.HIGH:
                    high_risk_clients.add(session.client_id)
            
            # Get pending notifications (sessions requiring review)
            pending_reviews = []
            for session in recent_sessions[:20]:  # Last 20 sessions
                if session.sentiment_summary and session.sentiment_summary.risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
                    pending_reviews.append({
                        'session_id': session.session_id,
                        'client_id': session.client_id,
                        'date': session.timestamp.isoformat(),
                        'risk_level': session.sentiment_summary.risk_level.value,
                        'requires_attention': session.sentiment_summary.risk_level == RiskLevel.HIGH
                    })
            
            # Calculate sentiment distribution
            sentiment_distribution = {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            }
            
            for session in recent_sessions:
                if session.sentiment_summary:
                    sentiment_distribution[session.sentiment_summary.overall_sentiment.value] += 1
            
            return {
                'therapist_id': therapist_id,
                'overview': {
                    'total_assigned_clients': total_clients,
                    'active_clients_this_week': active_clients,
                    'sessions_completed_today': completed_today,
                    'high_risk_clients': len(high_risk_clients)
                },
                'pending_reviews': pending_reviews,
                'sentiment_distribution': sentiment_distribution,
                'recent_activity': [
                    {
                        'session_id': s.session_id,
                        'client_id': s.client_id,
                        'timestamp': s.timestamp.isoformat(),
                        'status': s.status.value,
                        'duration_minutes': (s.duration // 60) if s.duration else 0
                    }
                    for s in recent_sessions[:10]
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard data for therapist {therapist_id}: {str(e)}")
            return {
                'therapist_id': therapist_id,
                'error': str(e),
                'success': False
            }
    
    def generate_progress_visualization(self, client_id: str, therapist_id: str,
                                       days: int = 90) -> Dict[str, Any]:
        """
        Generate data for client progress visualization
        
        Args:
            client_id: Client identifier
            therapist_id: Therapist identifier
            days: Number of days to include
            
        Returns:
            Dictionary containing visualization data
        """
        try:
            # Get client sessions
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            result = self.session_repo.get_sessions_by_client(
                client_id=client_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
            sessions = result['sessions']
            
            # Sort by timestamp
            sessions.sort(key=lambda x: x.timestamp)
            
            # Build sentiment timeline
            sentiment_timeline = []
            for session in sessions:
                if session.sentiment_summary:
                    sentiment_score = 1.0 if session.sentiment_summary.overall_sentiment == SentimentType.POSITIVE else \
                                    0.5 if session.sentiment_summary.overall_sentiment == SentimentType.NEUTRAL else 0.0
                    
                    sentiment_timeline.append({
                        'date': session.timestamp.date().isoformat(),
                        'sentiment_score': sentiment_score,
                        'sentiment_label': session.sentiment_summary.overall_sentiment.value,
                        'risk_level': session.sentiment_summary.risk_level.value
                    })
            
            # Build progress metrics timeline
            progress_metrics = {}
            for session in sessions:
                if session.sentiment_summary:
                    for pi in session.sentiment_summary.progress_indicators:
                        if pi.metric_name not in progress_metrics:
                            progress_metrics[pi.metric_name] = []
                        
                        progress_metrics[pi.metric_name].append({
                            'date': session.timestamp.date().isoformat(),
                            'value': pi.value,
                            'description': pi.description
                        })
            
            # Build milestones timeline
            milestones_timeline = []
            for session in sessions:
                if session.metadata.therapeutic_milestones:
                    for milestone in session.metadata.therapeutic_milestones:
                        milestones_timeline.append({
                            'date': session.timestamp.date().isoformat(),
                            'milestone': milestone,
                            'session_id': session.session_id
                        })
            
            # Calculate overall progress trend
            if len(sentiment_timeline) >= 2:
                recent_avg = sum([s['sentiment_score'] for s in sentiment_timeline[-5:]]) / len(sentiment_timeline[-5:])
                early_avg = sum([s['sentiment_score'] for s in sentiment_timeline[:5]]) / len(sentiment_timeline[:5])
                
                if recent_avg > early_avg + 0.2:
                    trend = 'improving'
                elif recent_avg < early_avg - 0.2:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'client_id': client_id,
                'therapist_id': therapist_id,
                'period_days': days,
                'period_start': start_date.date().isoformat(),
                'period_end': end_date.date().isoformat(),
                'overall_trend': trend,
                'sentiment_timeline': sentiment_timeline,
                'progress_metrics': progress_metrics,
                'milestones_timeline': milestones_timeline,
                'total_sessions': len(sessions),
                'sessions_with_analysis': len([s for s in sessions if s.sentiment_summary]),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate progress visualization for client {client_id}: {str(e)}")
            return {
                'client_id': client_id,
                'therapist_id': therapist_id,
                'error': str(e),
                'success': False
            }
    
    def generate_custom_report(self, therapist_id: str, 
                              report_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate customizable report based on therapist preferences
        
        Args:
            therapist_id: Therapist identifier
            report_config: Configuration for custom report
            
        Returns:
            Dictionary containing custom report data
        """
        try:
            report_type = report_config.get('type', 'client_summary')
            client_ids = report_config.get('client_ids', [])
            date_range = report_config.get('date_range', 30)
            include_metrics = report_config.get('include_metrics', [])
            
            if report_type == 'multi_client_comparison':
                return self._generate_multi_client_comparison(
                    therapist_id=therapist_id,
                    client_ids=client_ids,
                    days=date_range
                )
            elif report_type == 'risk_assessment':
                return self._generate_risk_assessment_report(
                    therapist_id=therapist_id,
                    client_ids=client_ids,
                    days=date_range
                )
            elif report_type == 'therapeutic_outcomes':
                return self._generate_outcomes_report(
                    therapist_id=therapist_id,
                    client_ids=client_ids,
                    days=date_range
                )
            else:
                return {
                    'therapist_id': therapist_id,
                    'error': f'Unsupported report type: {report_type}',
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Failed to generate custom report for therapist {therapist_id}: {str(e)}")
            return {
                'therapist_id': therapist_id,
                'error': str(e),
                'success': False
            }
    
    def _generate_multi_client_comparison(self, therapist_id: str,
                                         client_ids: List[str],
                                         days: int) -> Dict[str, Any]:
        """Generate comparison report across multiple clients"""
        try:
            client_summaries = []
            
            for client_id in client_ids:
                summary = self.generate_client_summary(
                    client_id=client_id,
                    therapist_id=therapist_id,
                    days=days
                )
                client_summaries.append(summary)
            
            return {
                'report_type': 'multi_client_comparison',
                'therapist_id': therapist_id,
                'clients_compared': len(client_ids),
                'period_days': days,
                'client_summaries': client_summaries,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate multi-client comparison: {str(e)}")
            return {'error': str(e), 'success': False}
    
    def _generate_risk_assessment_report(self, therapist_id: str,
                                        client_ids: List[str],
                                        days: int) -> Dict[str, Any]:
        """Generate risk assessment report"""
        try:
            risk_assessments = []
            
            for client_id in client_ids:
                # Get recent sessions
                result = self.session_repo.get_sessions_by_client(
                    client_id=client_id,
                    limit=50
                )
                sessions = result['sessions']
                
                # Analyze risk levels
                high_risk_count = 0
                medium_risk_count = 0
                low_risk_count = 0
                
                for session in sessions:
                    if session.sentiment_summary:
                        if session.sentiment_summary.risk_level == RiskLevel.HIGH:
                            high_risk_count += 1
                        elif session.sentiment_summary.risk_level == RiskLevel.MEDIUM:
                            medium_risk_count += 1
                        else:
                            low_risk_count += 1
                
                # Determine current risk status
                recent_sessions = sorted(sessions, key=lambda x: x.timestamp, reverse=True)[:5]
                recent_risk_levels = [s.sentiment_summary.risk_level.value 
                                     for s in recent_sessions if s.sentiment_summary]
                
                current_risk = recent_risk_levels[0] if recent_risk_levels else 'unknown'
                
                risk_assessments.append({
                    'client_id': client_id,
                    'current_risk_level': current_risk,
                    'risk_distribution': {
                        'high': high_risk_count,
                        'medium': medium_risk_count,
                        'low': low_risk_count
                    },
                    'total_sessions_analyzed': len([s for s in sessions if s.sentiment_summary]),
                    'requires_immediate_attention': current_risk == 'high'
                })
            
            return {
                'report_type': 'risk_assessment',
                'therapist_id': therapist_id,
                'period_days': days,
                'risk_assessments': risk_assessments,
                'high_risk_clients': len([r for r in risk_assessments if r['current_risk_level'] == 'high']),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate risk assessment report: {str(e)}")
            return {'error': str(e), 'success': False}
    
    def _generate_outcomes_report(self, therapist_id: str,
                                 client_ids: List[str],
                                 days: int) -> Dict[str, Any]:
        """Generate therapeutic outcomes report"""
        try:
            outcomes = []
            
            for client_id in client_ids:
                # Get sessions
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=days)
                
                result = self.session_repo.get_sessions_by_client(
                    client_id=client_id,
                    start_date=start_date,
                    end_date=end_date,
                    limit=1000
                )
                sessions = result['sessions']
                
                # Analyze progress
                trends = self.sentiment_service.analyze_progress_trends(sessions)
                
                # Count milestones
                total_milestones = set()
                for session in sessions:
                    total_milestones.update(session.metadata.therapeutic_milestones)
                
                outcomes.append({
                    'client_id': client_id,
                    'progress_trend': trends.get('trend'),
                    'total_sessions': len(sessions),
                    'milestones_achieved': len(total_milestones),
                    'current_risk_level': trends.get('current_risk_level'),
                    'sentiment_trajectory': trends.get('sentiment_trajectory', [])
                })
            
            return {
                'report_type': 'therapeutic_outcomes',
                'therapist_id': therapist_id,
                'period_days': days,
                'outcomes': outcomes,
                'clients_improving': len([o for o in outcomes if o['progress_trend'] == 'improving']),
                'clients_stable': len([o for o in outcomes if o['progress_trend'] == 'stable']),
                'clients_declining': len([o for o in outcomes if o['progress_trend'] == 'declining']),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate outcomes report: {str(e)}")
            return {'error': str(e), 'success': False}
