"""
Real-Time Sentiment Analysis Service for AI Therapy Platform
Implements conversation sentiment monitoring, emotional state tracking, mood pattern recognition, and therapeutic progress measurement
🏆 Breaking Barriers UK 2026 compliant

Validates: Requirements 7.3
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from enum import Enum

from ..models.session import SentimentType, RiskLevel, ProgressIndicator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EmotionalState(str, Enum):
    """Emotional state classifications"""
    CALM = "calm"
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    HOPEFUL = "hopeful"
    FRUSTRATED = "frustrated"
    CONTENT = "content"
    DISTRESSED = "distressed"
    MOTIVATED = "motivated"
    CONFUSED = "confused"
    RELIEVED = "relieved"


class MoodTrend(str, Enum):
    """Mood trend directions"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    FLUCTUATING = "fluctuating"


class SentimentAnalysisService:
    """
    Service for real-time sentiment analysis and emotional state tracking
    Monitors conversation sentiment, tracks emotional states, recognizes mood patterns,
    and measures therapeutic progress
    """
    
    def __init__(self):
        """Initialize sentiment analysis service"""
        # Sentiment keywords for simple analysis
        self.positive_keywords = {
            'happy', 'joy', 'excited', 'grateful', 'thankful', 'better', 'improved',
            'progress', 'hopeful', 'optimistic', 'confident', 'proud', 'relieved',
            'calm', 'peaceful', 'content', 'satisfied', 'motivated', 'energized'
        }
        
        self.negative_keywords = {
            'sad', 'depressed', 'anxious', 'worried', 'scared', 'afraid', 'angry',
            'frustrated', 'hopeless', 'helpless', 'overwhelmed', 'stressed', 'tired',
            'exhausted', 'lonely', 'isolated', 'worthless', 'guilty', 'ashamed'
        }
        
        self.neutral_keywords = {
            'okay', 'fine', 'alright', 'normal', 'usual', 'same', 'unchanged'
        }
        
        # Emotional state indicators
        self.emotional_indicators = {
            EmotionalState.CALM: ['calm', 'peaceful', 'relaxed', 'tranquil', 'serene'],
            EmotionalState.ANXIOUS: ['anxious', 'worried', 'nervous', 'tense', 'uneasy'],
            EmotionalState.DEPRESSED: ['depressed', 'sad', 'down', 'hopeless', 'empty'],
            EmotionalState.HOPEFUL: ['hopeful', 'optimistic', 'positive', 'encouraged'],
            EmotionalState.FRUSTRATED: ['frustrated', 'annoyed', 'irritated', 'angry'],
            EmotionalState.CONTENT: ['content', 'satisfied', 'happy', 'pleased'],
            EmotionalState.DISTRESSED: ['distressed', 'upset', 'troubled', 'disturbed'],
            EmotionalState.MOTIVATED: ['motivated', 'determined', 'driven', 'inspired'],
            EmotionalState.CONFUSED: ['confused', 'uncertain', 'unclear', 'lost'],
            EmotionalState.RELIEVED: ['relieved', 'better', 'lighter', 'unburdened']
        }
        
        logger.info("Sentiment Analysis Service initialized")
    
    # ========== Real-Time Sentiment Monitoring ==========
    
    def analyze_message_sentiment(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of a single message in real-time
        
        Args:
            message: Message text to analyze
            context: Optional context (previous messages, session info)
            
        Returns:
            Dictionary with sentiment analysis results
        """
        message_lower = message.lower()
        
        # Count sentiment keywords
        positive_count = sum(1 for word in self.positive_keywords if word in message_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in message_lower)
        neutral_count = sum(1 for word in self.neutral_keywords if word in message_lower)
        
        # Determine overall sentiment
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            sentiment = SentimentType.NEUTRAL
            confidence = 0.5
        elif positive_count > negative_count:
            sentiment = SentimentType.POSITIVE
            confidence = min(0.5 + (positive_count / max(total_sentiment_words, 1)) * 0.5, 1.0)
        elif negative_count > positive_count:
            sentiment = SentimentType.NEGATIVE
            confidence = min(0.5 + (negative_count / max(total_sentiment_words, 1)) * 0.5, 1.0)
        else:
            sentiment = SentimentType.NEUTRAL
            confidence = 0.6
        
        # Detect emotional states
        emotional_states = self.detect_emotional_states(message)
        
        # Calculate intensity (based on word count and sentiment strength)
        word_count = len(message.split())
        intensity = min((total_sentiment_words / max(word_count, 1)) * 2, 1.0)
        
        result = {
            'sentiment': sentiment.value,
            'confidence': round(confidence, 2),
            'intensity': round(intensity, 2),
            'emotional_states': [state.value for state in emotional_states],
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'neutral_indicators': neutral_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.debug(f"Analyzed message sentiment: {sentiment.value} (confidence: {confidence:.2f})")
        return result
    
    def analyze_conversation_sentiment(
        self,
        messages: List[Dict[str, str]],
        window_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment across multiple conversation messages
        
        Args:
            messages: List of messages with 'role' and 'content' keys
            window_size: Number of recent messages to analyze (None for all)
            
        Returns:
            Dictionary with aggregated sentiment analysis
        """
        if not messages:
            return {
                'overall_sentiment': SentimentType.NEUTRAL.value,
                'confidence': 0.0,
                'message_count': 0,
                'sentiment_distribution': {},
                'emotional_states': []
            }
        
        # Apply window if specified
        if window_size:
            messages = messages[-window_size:]
        
        # Analyze each message
        message_sentiments = []
        all_emotional_states = []
        
        for msg in messages:
            content = msg.get('content', '')
            if content:
                analysis = self.analyze_message_sentiment(content)
                message_sentiments.append(analysis)
                all_emotional_states.extend(analysis['emotional_states'])
        
        if not message_sentiments:
            return {
                'overall_sentiment': SentimentType.NEUTRAL.value,
                'confidence': 0.0,
                'message_count': 0,
                'sentiment_distribution': {},
                'emotional_states': []
            }
        
        # Calculate overall sentiment
        sentiment_counts = Counter(s['sentiment'] for s in message_sentiments)
        overall_sentiment = sentiment_counts.most_common(1)[0][0]
        
        # Calculate average confidence
        avg_confidence = sum(s['confidence'] for s in message_sentiments) / len(message_sentiments)
        
        # Calculate sentiment distribution
        total_messages = len(message_sentiments)
        sentiment_distribution = {
            sentiment: count / total_messages
            for sentiment, count in sentiment_counts.items()
        }
        
        # Get most common emotional states
        emotional_state_counts = Counter(all_emotional_states)
        top_emotional_states = [state for state, _ in emotional_state_counts.most_common(5)]
        
        result = {
            'overall_sentiment': overall_sentiment,
            'confidence': round(avg_confidence, 2),
            'message_count': total_messages,
            'sentiment_distribution': {
                k: round(v, 2) for k, v in sentiment_distribution.items()
            },
            'emotional_states': top_emotional_states,
            'sentiment_trajectory': self._calculate_sentiment_trajectory(message_sentiments),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Analyzed conversation sentiment: {overall_sentiment} "
            f"({total_messages} messages, confidence: {avg_confidence:.2f})"
        )
        return result
    
    # ========== Emotional State Tracking ==========
    
    def detect_emotional_states(
        self,
        text: str,
        threshold: float = 0.3
    ) -> List[EmotionalState]:
        """
        Detect emotional states from text
        
        Args:
            text: Text to analyze
            threshold: Minimum match ratio to detect state
            
        Returns:
            List of detected EmotionalState enums
        """
        text_lower = text.lower()
        detected_states = []
        
        for state, indicators in self.emotional_indicators.items():
            # Count how many indicators are present
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            match_ratio = matches / len(indicators)
            
            if match_ratio >= threshold:
                detected_states.append(state)
        
        # If no states detected, default to neutral/calm
        if not detected_states:
            detected_states.append(EmotionalState.CALM)
        
        return detected_states
    
    def track_emotional_state_changes(
        self,
        session_messages: List[Dict[str, Any]],
        time_window_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Track how emotional states change over time during a session
        
        Args:
            session_messages: List of messages with 'content' and 'timestamp'
            time_window_minutes: Time window for grouping state changes
            
        Returns:
            List of emotional state change events
        """
        if not session_messages:
            return []
        
        state_changes = []
        current_states = set()
        window_start = None
        
        for msg in session_messages:
            content = msg.get('content', '')
            timestamp = msg.get('timestamp')
            
            if not content or not timestamp:
                continue
            
            # Parse timestamp
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Detect states in this message
            detected_states = set(self.detect_emotional_states(content))
            
            # Check if states changed
            if detected_states != current_states:
                # Calculate time since last change
                time_since_last = None
                if window_start:
                    time_since_last = (timestamp - window_start).total_seconds() / 60
                
                state_changes.append({
                    'timestamp': timestamp.isoformat(),
                    'previous_states': [s.value for s in current_states],
                    'new_states': [s.value for s in detected_states],
                    'added_states': [s.value for s in (detected_states - current_states)],
                    'removed_states': [s.value for s in (current_states - detected_states)],
                    'time_since_last_change_minutes': round(time_since_last, 1) if time_since_last else None
                })
                
                current_states = detected_states
                window_start = timestamp
        
        logger.info(f"Tracked {len(state_changes)} emotional state changes")
        return state_changes
    
    def get_emotional_state_summary(
        self,
        session_messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get summary of emotional states throughout a session
        
        Args:
            session_messages: List of messages with 'content'
            
        Returns:
            Dictionary with emotional state summary
        """
        all_states = []
        
        for msg in session_messages:
            content = msg.get('content', '')
            if content:
                states = self.detect_emotional_states(content)
                all_states.extend(states)
        
        if not all_states:
            return {
                'dominant_states': [],
                'state_distribution': {},
                'state_count': 0,
                'unique_states': 0
            }
        
        # Count state occurrences
        state_counts = Counter(all_states)
        total_states = len(all_states)
        
        # Get dominant states (top 3)
        dominant_states = [
            {
                'state': state.value,
                'count': count,
                'percentage': round((count / total_states) * 100, 1)
            }
            for state, count in state_counts.most_common(3)
        ]
        
        # Calculate distribution
        state_distribution = {
            state.value: round((count / total_states) * 100, 1)
            for state, count in state_counts.items()
        }
        
        return {
            'dominant_states': dominant_states,
            'state_distribution': state_distribution,
            'state_count': total_states,
            'unique_states': len(state_counts)
        }
    
    # ========== Mood Pattern Recognition ==========
    
    def analyze_mood_patterns(
        self,
        session_history: List[Dict[str, Any]],
        lookback_sessions: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze mood patterns across multiple sessions
        
        Args:
            session_history: List of session data with sentiment information
            lookback_sessions: Number of recent sessions to analyze
            
        Returns:
            Dictionary with mood pattern analysis
        """
        if not session_history:
            return {
                'trend': MoodTrend.STABLE.value,
                'pattern_detected': False,
                'sessions_analyzed': 0
            }
        
        # Limit to recent sessions
        recent_sessions = session_history[-lookback_sessions:]
        
        # Extract sentiment scores
        sentiment_scores = []
        for session in recent_sessions:
            sentiment = session.get('sentiment', SentimentType.NEUTRAL.value)
            # Convert sentiment to numeric score
            score = self._sentiment_to_score(sentiment)
            sentiment_scores.append(score)
        
        if len(sentiment_scores) < 2:
            return {
                'trend': MoodTrend.STABLE.value,
                'pattern_detected': False,
                'sessions_analyzed': len(sentiment_scores),
                'average_mood_score': sentiment_scores[0] if sentiment_scores else 0.5
            }
        
        # Calculate trend
        trend = self._calculate_mood_trend(sentiment_scores)
        
        # Detect patterns
        patterns = self._detect_mood_patterns(sentiment_scores)
        
        # Calculate statistics
        avg_score = sum(sentiment_scores) / len(sentiment_scores)
        score_variance = sum((s - avg_score) ** 2 for s in sentiment_scores) / len(sentiment_scores)
        
        result = {
            'trend': trend.value,
            'pattern_detected': len(patterns) > 0,
            'patterns': patterns,
            'sessions_analyzed': len(sentiment_scores),
            'average_mood_score': round(avg_score, 2),
            'mood_variance': round(score_variance, 3),
            'mood_stability': round(1 - min(score_variance, 1.0), 2),
            'recent_scores': [round(s, 2) for s in sentiment_scores[-5:]],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Analyzed mood patterns: {trend.value} trend, "
            f"{len(patterns)} patterns detected"
        )
        return result
    
    def detect_mood_cycles(
        self,
        session_history: List[Dict[str, Any]],
        min_cycle_length: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Detect cyclical mood patterns
        
        Args:
            session_history: List of session data with sentiment information
            min_cycle_length: Minimum number of sessions for a cycle
            
        Returns:
            List of detected mood cycles
        """
        if len(session_history) < min_cycle_length * 2:
            return []
        
        # Extract sentiment scores
        sentiment_scores = [
            self._sentiment_to_score(session.get('sentiment', SentimentType.NEUTRAL.value))
            for session in session_history
        ]
        
        cycles = []
        
        # Simple cycle detection: look for peaks and troughs
        for i in range(1, len(sentiment_scores) - 1):
            # Peak detection
            if sentiment_scores[i] > sentiment_scores[i-1] and sentiment_scores[i] > sentiment_scores[i+1]:
                cycles.append({
                    'type': 'peak',
                    'session_index': i,
                    'score': round(sentiment_scores[i], 2),
                    'timestamp': session_history[i].get('timestamp')
                })
            # Trough detection
            elif sentiment_scores[i] < sentiment_scores[i-1] and sentiment_scores[i] < sentiment_scores[i+1]:
                cycles.append({
                    'type': 'trough',
                    'session_index': i,
                    'score': round(sentiment_scores[i], 2),
                    'timestamp': session_history[i].get('timestamp')
                })
        
        logger.info(f"Detected {len(cycles)} mood cycle points")
        return cycles
    
    # ========== Therapeutic Progress Measurement ==========
    
    def measure_therapeutic_progress(
        self,
        session_history: List[Dict[str, Any]],
        baseline_sessions: int = 3
    ) -> List[ProgressIndicator]:
        """
        Measure therapeutic progress based on sentiment and emotional state trends
        
        Args:
            session_history: List of session data with sentiment information
            baseline_sessions: Number of initial sessions to use as baseline
            
        Returns:
            List of ProgressIndicator objects
        """
        if len(session_history) < baseline_sessions + 1:
            return []
        
        progress_indicators = []
        
        # Calculate baseline metrics
        baseline = session_history[:baseline_sessions]
        recent = session_history[baseline_sessions:]
        
        # Sentiment improvement
        baseline_sentiment = self._average_sentiment_score(baseline)
        recent_sentiment = self._average_sentiment_score(recent)
        sentiment_improvement = recent_sentiment - baseline_sentiment
        
        if abs(sentiment_improvement) > 0.1:
            progress_indicators.append(ProgressIndicator(
                metric_name="Overall Sentiment",
                value=min(max((recent_sentiment + 1) / 2, 0), 1),  # Normalize to 0-1
                description=f"Sentiment {'improved' if sentiment_improvement > 0 else 'declined'} "
                           f"by {abs(sentiment_improvement):.2f} points from baseline",
                timestamp=datetime.utcnow()
            ))
        
        # Emotional stability
        baseline_variance = self._calculate_sentiment_variance(baseline)
        recent_variance = self._calculate_sentiment_variance(recent)
        stability_improvement = baseline_variance - recent_variance
        
        if abs(stability_improvement) > 0.05:
            progress_indicators.append(ProgressIndicator(
                metric_name="Emotional Stability",
                value=min(max(1 - recent_variance, 0), 1),
                description=f"Emotional stability {'improved' if stability_improvement > 0 else 'decreased'} "
                           f"(variance change: {stability_improvement:.3f})",
                timestamp=datetime.utcnow()
            ))
        
        # Positive sentiment frequency
        baseline_positive = sum(
            1 for s in baseline
            if s.get('sentiment') == SentimentType.POSITIVE.value
        ) / len(baseline)
        recent_positive = sum(
            1 for s in recent
            if s.get('sentiment') == SentimentType.POSITIVE.value
        ) / len(recent)
        
        if abs(recent_positive - baseline_positive) > 0.1:
            progress_indicators.append(ProgressIndicator(
                metric_name="Positive Outlook",
                value=round(recent_positive, 2),
                description=f"Positive sentiment frequency: {recent_positive:.1%} "
                           f"(baseline: {baseline_positive:.1%})",
                timestamp=datetime.utcnow()
            ))
        
        # Engagement level (based on message count/length if available)
        if all('message_count' in s for s in session_history):
            baseline_engagement = sum(s['message_count'] for s in baseline) / len(baseline)
            recent_engagement = sum(s['message_count'] for s in recent) / len(recent)
            engagement_change = (recent_engagement - baseline_engagement) / max(baseline_engagement, 1)
            
            if abs(engagement_change) > 0.2:
                progress_indicators.append(ProgressIndicator(
                    metric_name="Session Engagement",
                    value=min(max(recent_engagement / 20, 0), 1),  # Normalize assuming 20 messages is high
                    description=f"Engagement {'increased' if engagement_change > 0 else 'decreased'} "
                               f"by {abs(engagement_change):.1%}",
                    timestamp=datetime.utcnow()
                ))
        
        logger.info(f"Measured {len(progress_indicators)} therapeutic progress indicators")
        return progress_indicators
    
    def calculate_progress_score(
        self,
        session_history: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall therapeutic progress score
        
        Args:
            session_history: List of session data
            weights: Optional weights for different metrics
            
        Returns:
            Dictionary with progress score and breakdown
        """
        if not session_history:
            return {
                'overall_score': 0.0,
                'confidence': 0.0,
                'breakdown': {}
            }
        
        # Default weights
        if weights is None:
            weights = {
                'sentiment_trend': 0.3,
                'emotional_stability': 0.25,
                'positive_frequency': 0.25,
                'engagement': 0.2
            }
        
        scores = {}
        
        # Sentiment trend score
        sentiment_scores = [
            self._sentiment_to_score(s.get('sentiment', SentimentType.NEUTRAL.value))
            for s in session_history
        ]
        if len(sentiment_scores) >= 2:
            trend = self._calculate_linear_trend(sentiment_scores)
            scores['sentiment_trend'] = min(max((trend + 1) / 2, 0), 1)  # Normalize to 0-1
        else:
            scores['sentiment_trend'] = 0.5
        
        # Emotional stability score
        variance = self._calculate_sentiment_variance(session_history)
        scores['emotional_stability'] = min(max(1 - variance, 0), 1)
        
        # Positive frequency score
        positive_count = sum(
            1 for s in session_history
            if s.get('sentiment') == SentimentType.POSITIVE.value
        )
        scores['positive_frequency'] = positive_count / len(session_history)
        
        # Engagement score (if available)
        if all('message_count' in s for s in session_history):
            avg_messages = sum(s['message_count'] for s in session_history) / len(session_history)
            scores['engagement'] = min(avg_messages / 20, 1.0)  # Normalize assuming 20 is high
        else:
            scores['engagement'] = 0.5
        
        # Calculate weighted overall score
        overall_score = sum(scores[metric] * weights[metric] for metric in weights)
        
        # Calculate confidence based on data availability
        confidence = min(len(session_history) / 10, 1.0)  # Full confidence at 10+ sessions
        
        result = {
            'overall_score': round(overall_score, 2),
            'confidence': round(confidence, 2),
            'breakdown': {k: round(v, 2) for k, v in scores.items()},
            'sessions_analyzed': len(session_history),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Calculated progress score: {overall_score:.2f} "
            f"(confidence: {confidence:.2f}, {len(session_history)} sessions)"
        )
        return result
    
    # ========== Helper Methods ==========
    
    def _sentiment_to_score(self, sentiment: str) -> float:
        """Convert sentiment to numeric score (-1 to 1)"""
        sentiment_map = {
            SentimentType.POSITIVE.value: 1.0,
            SentimentType.NEUTRAL.value: 0.0,
            SentimentType.NEGATIVE.value: -1.0
        }
        return sentiment_map.get(sentiment, 0.0)
    
    def _calculate_sentiment_trajectory(
        self,
        message_sentiments: List[Dict[str, Any]]
    ) -> str:
        """Calculate sentiment trajectory (improving, declining, stable)"""
        if len(message_sentiments) < 3:
            return "insufficient_data"
        
        scores = [self._sentiment_to_score(s['sentiment']) for s in message_sentiments]
        
        # Calculate trend
        trend = self._calculate_linear_trend(scores)
        
        if trend > 0.1:
            return "improving"
        elif trend < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_linear_trend(self, scores: List[float]) -> float:
        """Calculate linear trend of scores"""
        if len(scores) < 2:
            return 0.0
        
        n = len(scores)
        x = list(range(n))
        
        # Calculate linear regression slope
        x_mean = sum(x) / n
        y_mean = sum(scores) / n
        
        numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def _calculate_mood_trend(self, sentiment_scores: List[float]) -> MoodTrend:
        """Calculate mood trend from sentiment scores"""
        if len(sentiment_scores) < 2:
            return MoodTrend.STABLE
        
        # Calculate trend
        trend = self._calculate_linear_trend(sentiment_scores)
        
        # Calculate variance
        mean_score = sum(sentiment_scores) / len(sentiment_scores)
        variance = sum((s - mean_score) ** 2 for s in sentiment_scores) / len(sentiment_scores)
        
        # Determine trend type
        if variance > 0.3:
            return MoodTrend.FLUCTUATING
        elif trend > 0.15:
            return MoodTrend.IMPROVING
        elif trend < -0.15:
            return MoodTrend.DECLINING
        else:
            return MoodTrend.STABLE
    
    def _detect_mood_patterns(self, sentiment_scores: List[float]) -> List[str]:
        """Detect specific mood patterns"""
        patterns = []
        
        if len(sentiment_scores) < 3:
            return patterns
        
        # Check for consistent improvement
        if all(sentiment_scores[i] >= sentiment_scores[i-1] for i in range(1, len(sentiment_scores))):
            patterns.append("consistent_improvement")
        
        # Check for consistent decline
        if all(sentiment_scores[i] <= sentiment_scores[i-1] for i in range(1, len(sentiment_scores))):
            patterns.append("consistent_decline")
        
        # Check for volatility
        mean_score = sum(sentiment_scores) / len(sentiment_scores)
        if sum(abs(s - mean_score) > 0.5 for s in sentiment_scores) > len(sentiment_scores) / 2:
            patterns.append("high_volatility")
        
        # Check for recent improvement
        if len(sentiment_scores) >= 5:
            recent_avg = sum(sentiment_scores[-3:]) / 3
            earlier_avg = sum(sentiment_scores[-5:-3]) / 2
            if recent_avg > earlier_avg + 0.2:
                patterns.append("recent_improvement")
        
        return patterns
    
    def _average_sentiment_score(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate average sentiment score for sessions"""
        if not sessions:
            return 0.0
        
        scores = [
            self._sentiment_to_score(s.get('sentiment', SentimentType.NEUTRAL.value))
            for s in sessions
        ]
        return sum(scores) / len(scores)
    
    def _calculate_sentiment_variance(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate sentiment variance for sessions"""
        if not sessions:
            return 0.0
        
        scores = [
            self._sentiment_to_score(s.get('sentiment', SentimentType.NEUTRAL.value))
            for s in sessions
        ]
        
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        return variance
