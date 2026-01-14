"""
Progress Summarization Service for AI Therapy Platform
Creates AI-powered session summaries, extracts key topics, detects therapeutic milestones,
and generates privacy-compliant summaries for therapists (no transcripts)
🏆 Breaking Barriers UK 2026 compliant

Validates: Requirements 7.3, 7.4, 5.2, 5.5
"""

import json
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import Counter, defaultdict

from ..models.session import SentimentSummary, SentimentType, RiskLevel, ProgressIndicator
from ..services.sentiment_analysis_service import SentimentAnalysisService, EmotionalState
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ProgressSummarizationService:
    """
    Service for creating AI-powered session summaries and progress tracking
    Generates privacy-compliant summaries for therapists without full transcripts
    """
    
    def __init__(self, sentiment_service: Optional[SentimentAnalysisService] = None):
        """
        Initialize progress summarization service
        
        Args:
            sentiment_service: Sentiment analysis service instance
        """
        self.sentiment_service = sentiment_service or SentimentAnalysisService()
        
        # Therapeutic milestone indicators
        self.milestone_indicators = {
            'insight': ['realize', 'understand', 'see now', 'makes sense', 'clarity', 'aha'],
            'commitment': ['will try', 'going to', 'commit', 'promise', 'plan to'],
            'progress': ['better', 'improved', 'progress', 'forward', 'growth'],
            'breakthrough': ['breakthrough', 'turning point', 'revelation', 'epiphany'],
            'coping_skill': ['technique', 'strategy', 'coping', 'manage', 'handle'],
            'goal_setting': ['goal', 'objective', 'aim', 'target', 'want to achieve']
        }
        
        logger.info("Progress Summarization Service initialized")

    # ========== AI-Powered Session Summaries ==========
    
    def generate_session_summary(
        self,
        session_id: str,
        client_id: str,
        messages: List[Dict[str, str]],
        duration_seconds: int,
        language: str = "en"
    ) -> SentimentSummary:
        """
        Generate comprehensive AI-powered session summary for therapists
        Privacy-compliant: no full transcripts, only sentiment and progress indicators
        
        Args:
            session_id: Session identifier
            client_id: Client identifier
            messages: List of conversation messages (for analysis only, not stored)
            duration_seconds: Session duration
            language: Session language
            
        Returns:
            SentimentSummary object for therapist review
        """
        # Analyze overall sentiment
        sentiment_analysis = self.sentiment_service.analyze_conversation_sentiment(messages)
        overall_sentiment = SentimentType(sentiment_analysis['overall_sentiment'])
        
        # Extract emotional states
        emotional_states = sentiment_analysis.get('emotional_states', [])
        
        # Extract key topics (privacy-safe: topics only, not content)
        key_topics = self.extract_key_topics(messages)
        
        # Detect therapeutic milestones
        milestones = self.detect_therapeutic_milestones(messages)
        
        # Measure progress indicators
        progress_indicators = self._generate_progress_indicators(
            messages,
            sentiment_analysis,
            milestones
        )
        
        # Assess risk level
        risk_level = self._assess_risk_level(
            overall_sentiment,
            emotional_states,
            messages
        )
        
        summary = SentimentSummary(
            overall_sentiment=overall_sentiment,
            emotional_state=emotional_states,
            progress_indicators=progress_indicators,
            key_topics=key_topics,
            risk_level=risk_level,
            generated_at=datetime.utcnow()
        )
        
        logger.info(
            f"Generated session summary for session {session_id}: "
            f"{overall_sentiment.value} sentiment, {len(key_topics)} topics, "
            f"{len(progress_indicators)} progress indicators"
        )
        
        return summary

    def generate_multi_session_summary(
        self,
        client_id: str,
        session_summaries: List[SentimentSummary],
        time_period_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate summary across multiple sessions for therapist review
        
        Args:
            client_id: Client identifier
            session_summaries: List of session summaries
            time_period_days: Optional time period filter
            
        Returns:
            Dictionary with multi-session summary
        """
        if not session_summaries:
            return {
                'client_id': client_id,
                'session_count': 0,
                'summary': 'No sessions available for summary'
            }
        
        # Filter by time period if specified
        if time_period_days:
            cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
            session_summaries = [
                s for s in session_summaries
                if s.generated_at > cutoff_date
            ]
        
        # Aggregate sentiment trends
        sentiment_counts = Counter(s.overall_sentiment for s in session_summaries)
        dominant_sentiment = sentiment_counts.most_common(1)[0][0]
        
        # Aggregate emotional states
        all_emotional_states = []
        for summary in session_summaries:
            all_emotional_states.extend(summary.emotional_state)
        emotional_state_counts = Counter(all_emotional_states)
        top_emotional_states = [state for state, _ in emotional_state_counts.most_common(5)]
        
        # Aggregate key topics
        all_topics = []
        for summary in session_summaries:
            all_topics.extend(summary.key_topics)
        topic_counts = Counter(all_topics)
        recurring_topics = [topic for topic, count in topic_counts.items() if count >= 2]
        
        # Aggregate progress indicators
        all_progress = []
        for summary in session_summaries:
            all_progress.extend(summary.progress_indicators)
        
        # Calculate average progress scores by metric
        progress_by_metric = defaultdict(list)
        for indicator in all_progress:
            progress_by_metric[indicator.metric_name].append(indicator.value)
        
        avg_progress = {
            metric: sum(values) / len(values)
            for metric, values in progress_by_metric.items()
        }
        
        # Assess overall risk trend
        risk_counts = Counter(s.risk_level for s in session_summaries)
        current_risk = session_summaries[-1].risk_level if session_summaries else RiskLevel.LOW
        
        multi_session_summary = {
            'client_id': client_id,
            'session_count': len(session_summaries),
            'time_period_days': time_period_days,
            'dominant_sentiment': dominant_sentiment.value,
            'sentiment_distribution': {
                sentiment.value: count / len(session_summaries)
                for sentiment, count in sentiment_counts.items()
            },
            'top_emotional_states': top_emotional_states,
            'recurring_topics': recurring_topics,
            'average_progress_scores': {k: round(v, 2) for k, v in avg_progress.items()},
            'current_risk_level': current_risk.value,
            'risk_distribution': {
                risk.value: count / len(session_summaries)
                for risk, count in risk_counts.items()
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Generated multi-session summary for client {client_id}: "
            f"{len(session_summaries)} sessions, {len(recurring_topics)} recurring topics"
        )
        
        return multi_session_summary

    # ========== Key Topic Extraction ==========
    
    def extract_key_topics(
        self,
        messages: List[Dict[str, str]],
        max_topics: int = 10
    ) -> List[str]:
        """
        Extract key topics from conversation (privacy-safe: topics only, not content)
        
        Args:
            messages: List of conversation messages
            max_topics: Maximum number of topics to return
            
        Returns:
            List of key topic strings
        """
        # Combine all message content
        all_text = " ".join([
            msg.get('content', '').lower()
            for msg in messages
        ])
        
        # Define therapeutic topic categories with keywords
        topic_categories = {
            'anxiety': ['anxiety', 'anxious', 'worry', 'nervous', 'panic', 'fear'],
            'depression': ['depression', 'depressed', 'sad', 'hopeless', 'empty'],
            'relationships': ['relationship', 'partner', 'family', 'friend', 'spouse'],
            'work_stress': ['work', 'job', 'career', 'boss', 'colleague', 'workplace'],
            'self_esteem': ['confidence', 'self-esteem', 'worth', 'value', 'self-image'],
            'trauma': ['trauma', 'traumatic', 'ptsd', 'flashback', 'trigger'],
            'grief': ['grief', 'loss', 'death', 'mourning', 'bereavement'],
            'anger': ['anger', 'angry', 'rage', 'furious', 'irritated'],
            'sleep': ['sleep', 'insomnia', 'tired', 'exhausted', 'rest'],
            'coping': ['coping', 'manage', 'handle', 'deal with', 'strategy'],
            'goals': ['goal', 'objective', 'aim', 'target', 'achieve'],
            'mindfulness': ['mindfulness', 'meditation', 'breathing', 'present'],
            'boundaries': ['boundary', 'boundaries', 'limit', 'say no'],
            'communication': ['communicate', 'express', 'talk', 'listen', 'conversation'],
            'change': ['change', 'transition', 'adapt', 'adjust', 'transform']
        }
        
        # Count topic occurrences
        topic_scores = {}
        for topic, keywords in topic_categories.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            if score > 0:
                topic_scores[topic] = score
        
        # Sort by score and return top topics
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        key_topics = [topic for topic, _ in sorted_topics[:max_topics]]
        
        logger.debug(f"Extracted {len(key_topics)} key topics from conversation")
        return key_topics
    
    def categorize_topics(
        self,
        topics: List[str]
    ) -> Dict[str, List[str]]:
        """
        Categorize topics into therapeutic domains
        
        Args:
            topics: List of topic strings
            
        Returns:
            Dictionary mapping categories to topics
        """
        categories = {
            'emotional_wellbeing': ['anxiety', 'depression', 'anger', 'grief'],
            'interpersonal': ['relationships', 'communication', 'boundaries'],
            'life_challenges': ['work_stress', 'change', 'trauma'],
            'personal_growth': ['self_esteem', 'goals', 'coping'],
            'wellness': ['sleep', 'mindfulness']
        }
        
        categorized = defaultdict(list)
        
        for topic in topics:
            for category, category_topics in categories.items():
                if topic in category_topics:
                    categorized[category].append(topic)
                    break
        
        return dict(categorized)

    # ========== Therapeutic Milestone Detection ==========
    
    def detect_therapeutic_milestones(
        self,
        messages: List[Dict[str, str]]
    ) -> List[str]:
        """
        Detect therapeutic milestones from conversation patterns
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List of detected milestone types
        """
        # Combine all message content
        all_text = " ".join([
            msg.get('content', '').lower()
            for msg in messages
        ])
        
        detected_milestones = []
        
        # Check for each milestone type
        for milestone_type, indicators in self.milestone_indicators.items():
            if any(indicator in all_text for indicator in indicators):
                detected_milestones.append(milestone_type)
        
        logger.debug(f"Detected {len(detected_milestones)} therapeutic milestones")
        return detected_milestones
    
    def track_milestone_progression(
        self,
        session_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Track milestone progression across sessions
        
        Args:
            session_history: List of session data with milestones
            
        Returns:
            Dictionary with milestone progression analysis
        """
        if not session_history:
            return {
                'total_milestones': 0,
                'milestone_frequency': {},
                'recent_milestones': []
            }
        
        # Collect all milestones
        all_milestones = []
        for session in session_history:
            milestones = session.get('milestones', [])
            all_milestones.extend(milestones)
        
        # Count milestone frequencies
        milestone_counts = Counter(all_milestones)
        
        # Get recent milestones (last 5 sessions)
        recent_sessions = session_history[-5:]
        recent_milestones = []
        for session in recent_sessions:
            session_milestones = session.get('milestones', [])
            if session_milestones:
                recent_milestones.append({
                    'session_id': session.get('session_id'),
                    'timestamp': session.get('timestamp'),
                    'milestones': session_milestones
                })
        
        # Calculate milestone rate (milestones per session)
        milestone_rate = len(all_milestones) / len(session_history)
        
        progression = {
            'total_milestones': len(all_milestones),
            'unique_milestone_types': len(milestone_counts),
            'milestone_frequency': dict(milestone_counts),
            'milestone_rate': round(milestone_rate, 2),
            'recent_milestones': recent_milestones,
            'most_common_milestone': milestone_counts.most_common(1)[0][0] if milestone_counts else None
        }
        
        logger.info(
            f"Tracked milestone progression: {len(all_milestones)} total milestones, "
            f"rate: {milestone_rate:.2f} per session"
        )
        
        return progression

    # ========== Privacy-Compliant Summary Generation ==========
    
    def generate_therapist_summary(
        self,
        session_id: str,
        client_id: str,
        sentiment_summary: SentimentSummary,
        duration_seconds: int,
        milestone_count: int
    ) -> Dict[str, Any]:
        """
        Generate privacy-compliant summary for therapist review
        NO TRANSCRIPTS - only sentiment, topics, and progress indicators
        
        Args:
            session_id: Session identifier
            client_id: Client identifier (anonymized for display)
            sentiment_summary: Session sentiment summary
            duration_seconds: Session duration
            milestone_count: Number of milestones detected
            
        Returns:
            Dictionary with therapist-facing summary
        """
        # Format duration
        duration_minutes = duration_seconds // 60
        
        # Create human-readable summary
        summary_text = self._generate_summary_text(
            sentiment_summary,
            duration_minutes,
            milestone_count
        )
        
        # Categorize topics
        categorized_topics = self.categorize_topics(sentiment_summary.key_topics)
        
        # Format progress indicators
        progress_summary = [
            {
                'metric': indicator.metric_name,
                'value': indicator.value,
                'description': indicator.description
            }
            for indicator in sentiment_summary.progress_indicators
        ]
        
        therapist_summary = {
            'session_id': session_id,
            'client_id': client_id[:8] + '...',  # Partial ID for privacy
            'duration_minutes': duration_minutes,
            'overall_sentiment': sentiment_summary.overall_sentiment.value,
            'emotional_states': sentiment_summary.emotional_state,
            'risk_level': sentiment_summary.risk_level.value,
            'key_topics': sentiment_summary.key_topics,
            'categorized_topics': categorized_topics,
            'milestone_count': milestone_count,
            'progress_indicators': progress_summary,
            'summary_text': summary_text,
            'generated_at': sentiment_summary.generated_at.isoformat(),
            'privacy_note': 'This summary contains no conversation transcripts. '
                          'Only sentiment analysis and progress indicators are included.'
        }
        
        logger.info(f"Generated therapist summary for session {session_id}")
        return therapist_summary
    
    def generate_client_progress_report(
        self,
        client_id: str,
        session_summaries: List[SentimentSummary],
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive progress report for therapist review
        
        Args:
            client_id: Client identifier
            session_summaries: List of session summaries
            time_period_days: Time period for report
            
        Returns:
            Dictionary with comprehensive progress report
        """
        # Filter by time period
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        recent_summaries = [
            s for s in session_summaries
            if s.generated_at > cutoff_date
        ]
        
        if not recent_summaries:
            return {
                'client_id': client_id[:8] + '...',
                'time_period_days': time_period_days,
                'session_count': 0,
                'report': 'No sessions in specified time period'
            }
        
        # Analyze sentiment trends
        sentiment_trend = self._analyze_sentiment_trend(recent_summaries)
        
        # Analyze emotional state patterns
        emotional_patterns = self._analyze_emotional_patterns(recent_summaries)
        
        # Analyze topic evolution
        topic_evolution = self._analyze_topic_evolution(recent_summaries)
        
        # Calculate overall progress
        overall_progress = self._calculate_overall_progress(recent_summaries)
        
        # Assess risk trends
        risk_trend = self._analyze_risk_trend(recent_summaries)
        
        report = {
            'client_id': client_id[:8] + '...',
            'time_period_days': time_period_days,
            'session_count': len(recent_summaries),
            'sentiment_trend': sentiment_trend,
            'emotional_patterns': emotional_patterns,
            'topic_evolution': topic_evolution,
            'overall_progress': overall_progress,
            'risk_trend': risk_trend,
            'generated_at': datetime.utcnow().isoformat(),
            'privacy_note': 'This report contains aggregated data only. '
                          'No conversation transcripts are included.'
        }
        
        logger.info(
            f"Generated progress report for client {client_id}: "
            f"{len(recent_summaries)} sessions over {time_period_days} days"
        )
        
        return report

    # ========== Helper Methods ==========
    
    def _generate_progress_indicators(
        self,
        messages: List[Dict[str, str]],
        sentiment_analysis: Dict[str, Any],
        milestones: List[str]
    ) -> List[ProgressIndicator]:
        """Generate progress indicators from session data"""
        indicators = []
        
        # Sentiment-based indicator
        sentiment = sentiment_analysis.get('overall_sentiment')
        confidence = sentiment_analysis.get('confidence', 0.5)
        
        if sentiment == SentimentType.POSITIVE.value:
            indicators.append(ProgressIndicator(
                metric_name="Session Sentiment",
                value=0.8,
                description="Client expressed predominantly positive sentiment during session",
                timestamp=datetime.utcnow()
            ))
        elif sentiment == SentimentType.NEGATIVE.value:
            indicators.append(ProgressIndicator(
                metric_name="Session Sentiment",
                value=0.3,
                description="Client expressed predominantly negative sentiment during session",
                timestamp=datetime.utcnow()
            ))
        else:
            indicators.append(ProgressIndicator(
                metric_name="Session Sentiment",
                value=0.5,
                description="Client expressed neutral sentiment during session",
                timestamp=datetime.utcnow()
            ))
        
        # Engagement indicator (based on message count)
        message_count = len([m for m in messages if m.get('role') == 'user'])
        engagement_score = min(message_count / 15, 1.0)  # Normalize to 15 messages
        
        indicators.append(ProgressIndicator(
            metric_name="Session Engagement",
            value=round(engagement_score, 2),
            description=f"Client contributed {message_count} messages during session",
            timestamp=datetime.utcnow()
        ))
        
        # Milestone indicator
        if milestones:
            milestone_score = min(len(milestones) / 3, 1.0)  # Normalize to 3 milestones
            indicators.append(ProgressIndicator(
                metric_name="Therapeutic Milestones",
                value=round(milestone_score, 2),
                description=f"Achieved {len(milestones)} therapeutic milestone(s): {', '.join(milestones)}",
                timestamp=datetime.utcnow()
            ))
        
        return indicators
    
    def _assess_risk_level(
        self,
        overall_sentiment: SentimentType,
        emotional_states: List[str],
        messages: List[Dict[str, str]]
    ) -> RiskLevel:
        """Assess risk level based on sentiment and emotional states"""
        # Check for high-risk emotional states
        high_risk_states = {'distressed', 'hopeless', 'depressed'}
        medium_risk_states = {'anxious', 'frustrated', 'confused'}
        
        emotional_state_set = set(emotional_states)
        
        # Check message content for risk indicators (basic check)
        all_text = " ".join([m.get('content', '').lower() for m in messages])
        risk_keywords = ['hopeless', 'give up', 'can\'t go on', 'no point']
        
        has_risk_keywords = any(keyword in all_text for keyword in risk_keywords)
        
        # Determine risk level
        if has_risk_keywords or emotional_state_set & high_risk_states:
            return RiskLevel.HIGH
        elif overall_sentiment == SentimentType.NEGATIVE and emotional_state_set & medium_risk_states:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_summary_text(
        self,
        sentiment_summary: SentimentSummary,
        duration_minutes: int,
        milestone_count: int
    ) -> str:
        """Generate human-readable summary text"""
        parts = []
        
        # Duration and sentiment
        parts.append(
            f"Session lasted {duration_minutes} minutes with "
            f"{sentiment_summary.overall_sentiment.value} overall sentiment."
        )
        
        # Emotional states
        if sentiment_summary.emotional_state:
            states_str = ", ".join(sentiment_summary.emotional_state[:3])
            parts.append(f"Primary emotional states: {states_str}.")
        
        # Topics
        if sentiment_summary.key_topics:
            topics_str = ", ".join(sentiment_summary.key_topics[:5])
            parts.append(f"Key topics discussed: {topics_str}.")
        
        # Milestones
        if milestone_count > 0:
            parts.append(f"Client achieved {milestone_count} therapeutic milestone(s).")
        
        # Risk level
        if sentiment_summary.risk_level != RiskLevel.LOW:
            parts.append(f"Risk level: {sentiment_summary.risk_level.value}.")
        
        return " ".join(parts)
    
    def _analyze_sentiment_trend(
        self,
        summaries: List[SentimentSummary]
    ) -> Dict[str, Any]:
        """Analyze sentiment trend across sessions"""
        sentiment_scores = []
        for summary in summaries:
            if summary.overall_sentiment == SentimentType.POSITIVE:
                sentiment_scores.append(1.0)
            elif summary.overall_sentiment == SentimentType.NEUTRAL:
                sentiment_scores.append(0.0)
            else:
                sentiment_scores.append(-1.0)
        
        if len(sentiment_scores) < 2:
            return {'trend': 'insufficient_data', 'direction': 'stable'}
        
        # Calculate trend
        avg_first_half = sum(sentiment_scores[:len(sentiment_scores)//2]) / (len(sentiment_scores)//2)
        avg_second_half = sum(sentiment_scores[len(sentiment_scores)//2:]) / (len(sentiment_scores) - len(sentiment_scores)//2)
        
        change = avg_second_half - avg_first_half
        
        if change > 0.2:
            direction = 'improving'
        elif change < -0.2:
            direction = 'declining'
        else:
            direction = 'stable'
        
        return {
            'trend': direction,
            'average_sentiment': round(sum(sentiment_scores) / len(sentiment_scores), 2),
            'recent_average': round(avg_second_half, 2),
            'change': round(change, 2)
        }
    
    def _analyze_emotional_patterns(
        self,
        summaries: List[SentimentSummary]
    ) -> Dict[str, Any]:
        """Analyze emotional state patterns"""
        all_states = []
        for summary in summaries:
            all_states.extend(summary.emotional_state)
        
        state_counts = Counter(all_states)
        
        return {
            'most_common_states': [
                {'state': state, 'frequency': count}
                for state, count in state_counts.most_common(5)
            ],
            'total_unique_states': len(state_counts)
        }
    
    def _analyze_topic_evolution(
        self,
        summaries: List[SentimentSummary]
    ) -> Dict[str, Any]:
        """Analyze how topics evolve over time"""
        all_topics = []
        for summary in summaries:
            all_topics.extend(summary.key_topics)
        
        topic_counts = Counter(all_topics)
        
        # Get topics from first half vs second half
        mid_point = len(summaries) // 2
        first_half_topics = set()
        second_half_topics = set()
        
        for i, summary in enumerate(summaries):
            if i < mid_point:
                first_half_topics.update(summary.key_topics)
            else:
                second_half_topics.update(summary.key_topics)
        
        new_topics = second_half_topics - first_half_topics
        resolved_topics = first_half_topics - second_half_topics
        
        return {
            'recurring_topics': [topic for topic, count in topic_counts.items() if count >= 2],
            'new_topics': list(new_topics),
            'resolved_topics': list(resolved_topics),
            'total_unique_topics': len(topic_counts)
        }
    
    def _calculate_overall_progress(
        self,
        summaries: List[SentimentSummary]
    ) -> Dict[str, Any]:
        """Calculate overall progress score"""
        if not summaries:
            return {'score': 0.0, 'confidence': 0.0}
        
        # Aggregate progress indicators
        all_indicators = []
        for summary in summaries:
            all_indicators.extend(summary.progress_indicators)
        
        if not all_indicators:
            return {'score': 0.5, 'confidence': 0.3}
        
        # Calculate average progress
        avg_progress = sum(ind.value for ind in all_indicators) / len(all_indicators)
        
        # Confidence based on number of sessions
        confidence = min(len(summaries) / 10, 1.0)
        
        return {
            'score': round(avg_progress, 2),
            'confidence': round(confidence, 2),
            'indicator_count': len(all_indicators)
        }
    
    def _analyze_risk_trend(
        self,
        summaries: List[SentimentSummary]
    ) -> Dict[str, Any]:
        """Analyze risk level trends"""
        risk_scores = []
        for summary in summaries:
            if summary.risk_level == RiskLevel.LOW:
                risk_scores.append(0.0)
            elif summary.risk_level == RiskLevel.MEDIUM:
                risk_scores.append(0.5)
            else:
                risk_scores.append(1.0)
        
        if not risk_scores:
            return {'trend': 'unknown', 'current_risk': 'low'}
        
        # Calculate trend
        if len(risk_scores) >= 2:
            recent_avg = sum(risk_scores[-3:]) / min(len(risk_scores), 3)
            earlier_avg = sum(risk_scores[:-3]) / max(len(risk_scores) - 3, 1) if len(risk_scores) > 3 else recent_avg
            
            if recent_avg < earlier_avg - 0.1:
                trend = 'decreasing'
            elif recent_avg > earlier_avg + 0.1:
                trend = 'increasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        current_risk = summaries[-1].risk_level.value
        
        return {
            'trend': trend,
            'current_risk': current_risk,
            'average_risk_score': round(sum(risk_scores) / len(risk_scores), 2)
        }
