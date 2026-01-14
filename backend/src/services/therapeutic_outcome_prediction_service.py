"""
Therapeutic Outcome Prediction Service for AI Therapy Platform
Builds predictive models for therapeutic success, implements intervention recommendations,
adds risk assessment and early warning systems, creates personalized treatment path optimization
🏆 Breaking Barriers UK 2026 compliant

Validates: Requirements 7.3, 7.5
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from enum import Enum

from ..models.session import SentimentType, RiskLevel, ProgressIndicator
from ..services.sentiment_analysis_service import SentimentAnalysisService, MoodTrend
from ..services.progress_summarization_service import ProgressSummarizationService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OutcomePrediction(str, Enum):
    """Therapeutic outcome predictions"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    UNCERTAIN = "uncertain"


class InterventionType(str, Enum):
    """Types of therapeutic interventions"""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    MINDFULNESS = "mindfulness"
    EMOTIONAL_REGULATION = "emotional_regulation"
    RELATIONSHIP_FOCUSED = "relationship_focused"
    TRAUMA_INFORMED = "trauma_informed"
    GOAL_SETTING = "goal_setting"
    COPING_SKILLS = "coping_skills"
    CRISIS_INTERVENTION = "crisis_intervention"


class RiskCategory(str, Enum):
    """Risk assessment categories"""
    IMMEDIATE_CRISIS = "immediate_crisis"
    HIGH_RISK = "high_risk"
    MODERATE_RISK = "moderate_risk"
    LOW_RISK = "low_risk"
    MINIMAL_RISK = "minimal_risk"


class TherapeuticOutcomePredictionService:
    """
    Service for predicting therapeutic outcomes and recommending interventions
    Provides risk assessment, early warning systems, and personalized treatment optimization
    """
    
    def __init__(
        self,
        sentiment_service: Optional[SentimentAnalysisService] = None,
        summarization_service: Optional[ProgressSummarizationService] = None
    ):
        """
        Initialize therapeutic outcome prediction service
        
        Args:
            sentiment_service: Sentiment analysis service instance
            summarization_service: Progress summarization service instance
        """
        self.sentiment_service = sentiment_service or SentimentAnalysisService()
        self.summarization_service = summarization_service or ProgressSummarizationService()
        
        # Intervention recommendations based on topics and patterns
        self.intervention_mapping = {
            'anxiety': [InterventionType.MINDFULNESS, InterventionType.COGNITIVE_BEHAVIORAL],
            'depression': [InterventionType.COGNITIVE_BEHAVIORAL, InterventionType.GOAL_SETTING],
            'relationships': [InterventionType.RELATIONSHIP_FOCUSED, InterventionType.EMOTIONAL_REGULATION],
            'work_stress': [InterventionType.COPING_SKILLS, InterventionType.MINDFULNESS],
            'trauma': [InterventionType.TRAUMA_INFORMED, InterventionType.EMOTIONAL_REGULATION],
            'anger': [InterventionType.EMOTIONAL_REGULATION, InterventionType.MINDFULNESS],
            'self_esteem': [InterventionType.COGNITIVE_BEHAVIORAL, InterventionType.GOAL_SETTING]
        }
        
        logger.info("Therapeutic Outcome Prediction Service initialized")
    
    # ========== Predictive Models for Therapeutic Success ==========
    
    def predict_therapeutic_outcome(
        self,
        client_id: str,
        session_history: List[Dict[str, Any]],
        current_session_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict therapeutic outcome based on session history and current data
        
        Args:
            client_id: Client identifier
            session_history: List of previous session data
            current_session_data: Optional current session data
            
        Returns:
            Dictionary with outcome prediction and confidence
        """
        if len(session_history) < 3:
            return {
                'prediction': OutcomePrediction.UNCERTAIN.value,
                'confidence': 0.2,
                'reason': 'Insufficient session history for reliable prediction',
                'sessions_analyzed': len(session_history)
            }
        
        # Calculate prediction factors
        factors = self._calculate_prediction_factors(session_history, current_session_data)
        
        # Weighted scoring
        weights = {
            'sentiment_trend': 0.25,
            'engagement_level': 0.20,
            'milestone_frequency': 0.20,
            'emotional_stability': 0.15,
            'topic_resolution': 0.10,
            'risk_trend': 0.10
        }
        
        # Calculate weighted score
        prediction_score = sum(
            factors.get(factor, 0.5) * weight
            for factor, weight in weights.items()
        )
        
        # Determine prediction category
        if prediction_score >= 0.75:
            prediction = OutcomePrediction.EXCELLENT
        elif prediction_score >= 0.60:
            prediction = OutcomePrediction.GOOD
        elif prediction_score >= 0.45:
            prediction = OutcomePrediction.MODERATE
        elif prediction_score >= 0.30:
            prediction = OutcomePrediction.POOR
        else:
            prediction = OutcomePrediction.UNCERTAIN
        
        # Calculate confidence based on data quality
        confidence = self._calculate_prediction_confidence(session_history, factors)
        
        result = {
            'client_id': client_id[:8] + '...',
            'prediction': prediction.value,
            'confidence': round(confidence, 2),
            'prediction_score': round(prediction_score, 2),
            'factors': {k: round(v, 2) for k, v in factors.items()},
            'sessions_analyzed': len(session_history),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Predicted therapeutic outcome for client {client_id}: "
            f"{prediction.value} (confidence: {confidence:.2f})"
        )
        
        return result

    def predict_session_success(
        self,
        session_data: Dict[str, Any],
        client_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predict likelihood of current session being successful
        
        Args:
            session_data: Current session data
            client_history: Client's session history
            
        Returns:
            Dictionary with session success prediction
        """
        success_indicators = []
        success_score = 0.5  # Start neutral
        
        # Check sentiment
        sentiment = session_data.get('sentiment', SentimentType.NEUTRAL.value)
        if sentiment == SentimentType.POSITIVE.value:
            success_score += 0.2
            success_indicators.append('positive_sentiment')
        elif sentiment == SentimentType.NEGATIVE.value:
            success_score -= 0.1
        
        # Check engagement
        message_count = session_data.get('message_count', 0)
        if message_count >= 10:
            success_score += 0.15
            success_indicators.append('high_engagement')
        elif message_count < 5:
            success_score -= 0.1
        
        # Check milestones
        milestones = session_data.get('milestones', [])
        if len(milestones) >= 2:
            success_score += 0.2
            success_indicators.append('multiple_milestones')
        elif len(milestones) == 1:
            success_score += 0.1
            success_indicators.append('milestone_achieved')
        
        # Check emotional states
        emotional_states = session_data.get('emotional_states', [])
        positive_states = {'hopeful', 'content', 'motivated', 'relieved', 'calm'}
        if any(state in positive_states for state in emotional_states):
            success_score += 0.1
            success_indicators.append('positive_emotional_states')
        
        # Compare to historical average
        if client_history:
            avg_historical_sentiment = self._calculate_average_sentiment(client_history)
            current_sentiment_score = self._sentiment_to_score(sentiment)
            if current_sentiment_score > avg_historical_sentiment:
                success_score += 0.1
                success_indicators.append('above_historical_average')
        
        # Normalize score to 0-1
        success_score = min(max(success_score, 0.0), 1.0)
        
        # Determine success likelihood
        if success_score >= 0.7:
            likelihood = 'high'
        elif success_score >= 0.5:
            likelihood = 'moderate'
        else:
            likelihood = 'low'
        
        return {
            'success_likelihood': likelihood,
            'success_score': round(success_score, 2),
            'indicators': success_indicators,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # ========== Intervention Recommendation System ==========
    
    def recommend_interventions(
        self,
        client_id: str,
        session_history: List[Dict[str, Any]],
        current_topics: List[str],
        current_emotional_states: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Recommend therapeutic interventions based on client data
        
        Args:
            client_id: Client identifier
            session_history: Session history
            current_topics: Current session topics
            current_emotional_states: Current emotional states
            
        Returns:
            List of recommended interventions with rationale
        """
        recommendations = []
        
        # Topic-based recommendations
        for topic in current_topics:
            if topic in self.intervention_mapping:
                for intervention in self.intervention_mapping[topic]:
                    recommendations.append({
                        'intervention': intervention.value,
                        'reason': f'Addresses current topic: {topic}',
                        'priority': 'high' if topic in current_topics[:3] else 'medium',
                        'evidence_based': True
                    })
        
        # Emotional state-based recommendations
        if 'anxious' in current_emotional_states or 'distressed' in current_emotional_states:
            recommendations.append({
                'intervention': InterventionType.MINDFULNESS.value,
                'reason': 'Client showing signs of anxiety or distress',
                'priority': 'high',
                'evidence_based': True
            })
        
        if 'depressed' in current_emotional_states or 'hopeless' in current_emotional_states:
            recommendations.append({
                'intervention': InterventionType.COGNITIVE_BEHAVIORAL.value,
                'reason': 'Client showing signs of depression',
                'priority': 'high',
                'evidence_based': True
            })
        
        # Pattern-based recommendations from history
        if session_history:
            patterns = self._analyze_historical_patterns(session_history)
            
            if patterns.get('low_engagement'):
                recommendations.append({
                    'intervention': InterventionType.GOAL_SETTING.value,
                    'reason': 'Historical pattern of low engagement',
                    'priority': 'medium',
                    'evidence_based': True
                })
            
            if patterns.get('recurring_relationship_issues'):
                recommendations.append({
                    'intervention': InterventionType.RELATIONSHIP_FOCUSED.value,
                    'reason': 'Recurring relationship-related topics',
                    'priority': 'high',
                    'evidence_based': True
                })
        
        # Remove duplicates and sort by priority
        unique_recommendations = []
        seen_interventions = set()
        
        for rec in recommendations:
            if rec['intervention'] not in seen_interventions:
                unique_recommendations.append(rec)
                seen_interventions.add(rec['intervention'])
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        unique_recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        logger.info(
            f"Generated {len(unique_recommendations)} intervention recommendations "
            f"for client {client_id}"
        )
        
        return unique_recommendations[:5]  # Return top 5

    def evaluate_intervention_effectiveness(
        self,
        client_id: str,
        intervention_type: str,
        sessions_before: List[Dict[str, Any]],
        sessions_after: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate effectiveness of an intervention
        
        Args:
            client_id: Client identifier
            intervention_type: Type of intervention applied
            sessions_before: Sessions before intervention
            sessions_after: Sessions after intervention
            
        Returns:
            Dictionary with effectiveness evaluation
        """
        if not sessions_before or not sessions_after:
            return {
                'effectiveness': 'insufficient_data',
                'confidence': 0.0
            }
        
        # Compare sentiment before and after
        sentiment_before = self._calculate_average_sentiment(sessions_before)
        sentiment_after = self._calculate_average_sentiment(sessions_after)
        sentiment_improvement = sentiment_after - sentiment_before
        
        # Compare engagement
        engagement_before = self._calculate_average_engagement(sessions_before)
        engagement_after = self._calculate_average_engagement(sessions_after)
        engagement_improvement = engagement_after - engagement_before
        
        # Compare milestone frequency
        milestone_freq_before = self._calculate_milestone_frequency(sessions_before)
        milestone_freq_after = self._calculate_milestone_frequency(sessions_after)
        milestone_improvement = milestone_freq_after - milestone_freq_before
        
        # Calculate overall effectiveness score
        effectiveness_score = (
            sentiment_improvement * 0.4 +
            engagement_improvement * 0.3 +
            milestone_improvement * 0.3
        )
        
        # Normalize to 0-1
        effectiveness_score = (effectiveness_score + 1) / 2
        
        # Determine effectiveness category
        if effectiveness_score >= 0.7:
            effectiveness = 'highly_effective'
        elif effectiveness_score >= 0.55:
            effectiveness = 'effective'
        elif effectiveness_score >= 0.45:
            effectiveness = 'neutral'
        else:
            effectiveness = 'ineffective'
        
        # Calculate confidence
        confidence = min(
            (len(sessions_before) + len(sessions_after)) / 10,
            1.0
        )
        
        return {
            'intervention_type': intervention_type,
            'effectiveness': effectiveness,
            'effectiveness_score': round(effectiveness_score, 2),
            'confidence': round(confidence, 2),
            'improvements': {
                'sentiment': round(sentiment_improvement, 2),
                'engagement': round(engagement_improvement, 2),
                'milestones': round(milestone_improvement, 2)
            },
            'sessions_analyzed': {
                'before': len(sessions_before),
                'after': len(sessions_after)
            }
        }
    
    # ========== Risk Assessment and Early Warning ==========
    
    def assess_comprehensive_risk(
        self,
        client_id: str,
        current_session: Dict[str, Any],
        session_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Comprehensive risk assessment with early warning indicators
        
        Args:
            client_id: Client identifier
            current_session: Current session data
            session_history: Session history
            
        Returns:
            Dictionary with comprehensive risk assessment
        """
        risk_factors = []
        risk_score = 0.0
        
        # Current session risk factors
        current_sentiment = current_session.get('sentiment', SentimentType.NEUTRAL.value)
        if current_sentiment == SentimentType.NEGATIVE.value:
            risk_score += 0.2
            risk_factors.append('negative_sentiment')
        
        current_emotional_states = current_session.get('emotional_states', [])
        high_risk_states = {'distressed', 'hopeless', 'depressed'}
        if any(state in high_risk_states for state in current_emotional_states):
            risk_score += 0.3
            risk_factors.append('high_risk_emotional_states')
        
        # Check for crisis indicators in topics
        current_topics = current_session.get('topics', [])
        crisis_topics = {'trauma', 'grief', 'crisis'}
        if any(topic in crisis_topics for topic in current_topics):
            risk_score += 0.2
            risk_factors.append('crisis_related_topics')
        
        # Historical risk factors
        if session_history:
            # Check for declining trend
            mood_analysis = self.sentiment_service.analyze_mood_patterns(session_history)
            if mood_analysis.get('trend') == MoodTrend.DECLINING.value:
                risk_score += 0.2
                risk_factors.append('declining_mood_trend')
            
            # Check for increasing risk levels
            recent_risk_levels = [
                s.get('risk_level', RiskLevel.LOW.value)
                for s in session_history[-5:]
            ]
            high_risk_count = sum(1 for r in recent_risk_levels if r == RiskLevel.HIGH.value)
            if high_risk_count >= 2:
                risk_score += 0.3
                risk_factors.append('recurring_high_risk_sessions')
            
            # Check for disengagement
            recent_engagement = self._calculate_average_engagement(session_history[-3:])
            if recent_engagement < 0.3:
                risk_score += 0.15
                risk_factors.append('low_engagement')
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Determine risk category
        if risk_score >= 0.8:
            risk_category = RiskCategory.IMMEDIATE_CRISIS
        elif risk_score >= 0.6:
            risk_category = RiskCategory.HIGH_RISK
        elif risk_score >= 0.4:
            risk_category = RiskCategory.MODERATE_RISK
        elif risk_score >= 0.2:
            risk_category = RiskCategory.LOW_RISK
        else:
            risk_category = RiskCategory.MINIMAL_RISK
        
        # Generate recommendations
        recommendations = self._generate_risk_recommendations(risk_category, risk_factors)
        
        assessment = {
            'client_id': client_id[:8] + '...',
            'risk_category': risk_category.value,
            'risk_score': round(risk_score, 2),
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'requires_immediate_attention': risk_category in [
                RiskCategory.IMMEDIATE_CRISIS,
                RiskCategory.HIGH_RISK
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Comprehensive risk assessment for client {client_id}: "
            f"{risk_category.value} (score: {risk_score:.2f})"
        )
        
        return assessment

    def detect_early_warning_signs(
        self,
        client_id: str,
        session_history: List[Dict[str, Any]],
        lookback_sessions: int = 5
    ) -> Dict[str, Any]:
        """
        Detect early warning signs of deterioration or crisis
        
        Args:
            client_id: Client identifier
            session_history: Session history
            lookback_sessions: Number of recent sessions to analyze
            
        Returns:
            Dictionary with early warning indicators
        """
        if len(session_history) < lookback_sessions:
            return {
                'warning_level': 'insufficient_data',
                'warnings': [],
                'confidence': 0.0
            }
        
        recent_sessions = session_history[-lookback_sessions:]
        warnings = []
        warning_score = 0.0
        
        # Check for sentiment decline
        sentiment_scores = [
            self._sentiment_to_score(s.get('sentiment', SentimentType.NEUTRAL.value))
            for s in recent_sessions
        ]
        
        if len(sentiment_scores) >= 3:
            # Check if last 3 sessions show decline
            if all(sentiment_scores[i] <= sentiment_scores[i-1] for i in range(-2, 0)):
                warnings.append({
                    'type': 'sentiment_decline',
                    'severity': 'high',
                    'description': 'Consistent sentiment decline over recent sessions'
                })
                warning_score += 0.3
        
        # Check for disengagement pattern
        engagement_scores = [
            s.get('message_count', 0) / 15  # Normalize to 15 messages
            for s in recent_sessions
        ]
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        
        if avg_engagement < 0.3:
            warnings.append({
                'type': 'low_engagement',
                'severity': 'medium',
                'description': 'Consistently low engagement in recent sessions'
            })
            warning_score += 0.2
        
        # Check for increasing negative emotional states
        negative_states = {'anxious', 'depressed', 'distressed', 'hopeless'}
        negative_state_counts = [
            sum(1 for state in s.get('emotional_states', []) if state in negative_states)
            for s in recent_sessions
        ]
        
        if len(negative_state_counts) >= 3:
            recent_avg = sum(negative_state_counts[-3:]) / 3
            earlier_avg = sum(negative_state_counts[:-3]) / max(len(negative_state_counts) - 3, 1)
            
            if recent_avg > earlier_avg + 1:
                warnings.append({
                    'type': 'increasing_negative_states',
                    'severity': 'high',
                    'description': 'Increase in negative emotional states'
                })
                warning_score += 0.3
        
        # Check for missed milestones
        milestone_counts = [len(s.get('milestones', [])) for s in recent_sessions]
        if sum(milestone_counts) == 0:
            warnings.append({
                'type': 'no_milestones',
                'severity': 'medium',
                'description': 'No therapeutic milestones achieved in recent sessions'
            })
            warning_score += 0.15
        
        # Check for topic stagnation
        all_topics = []
        for session in recent_sessions:
            all_topics.extend(session.get('topics', []))
        
        unique_topics = len(set(all_topics))
        if unique_topics <= 2:
            warnings.append({
                'type': 'topic_stagnation',
                'severity': 'low',
                'description': 'Limited topic diversity in recent sessions'
            })
            warning_score += 0.1
        
        # Determine warning level
        if warning_score >= 0.6:
            warning_level = 'critical'
        elif warning_score >= 0.4:
            warning_level = 'high'
        elif warning_score >= 0.2:
            warning_level = 'moderate'
        else:
            warning_level = 'low'
        
        # Calculate confidence
        confidence = min(len(recent_sessions) / lookback_sessions, 1.0)
        
        result = {
            'client_id': client_id[:8] + '...',
            'warning_level': warning_level,
            'warning_score': round(warning_score, 2),
            'warnings': warnings,
            'confidence': round(confidence, 2),
            'sessions_analyzed': len(recent_sessions),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Early warning detection for client {client_id}: "
            f"{warning_level} level, {len(warnings)} warnings"
        )
        
        return result
    
    # ========== Personalized Treatment Path Optimization ==========
    
    def optimize_treatment_path(
        self,
        client_id: str,
        session_history: List[Dict[str, Any]],
        therapeutic_goals: List[str],
        current_interventions: List[str]
    ) -> Dict[str, Any]:
        """
        Optimize personalized treatment path based on client data
        
        Args:
            client_id: Client identifier
            session_history: Session history
            therapeutic_goals: Client's therapeutic goals
            current_interventions: Currently applied interventions
            
        Returns:
            Dictionary with optimized treatment path recommendations
        """
        # Analyze current progress toward goals
        goal_progress = self._analyze_goal_progress(session_history, therapeutic_goals)
        
        # Evaluate current intervention effectiveness
        intervention_effectiveness = {}
        for intervention in current_interventions:
            # Simple effectiveness based on recent progress
            recent_progress = self._calculate_recent_progress(session_history[-5:])
            intervention_effectiveness[intervention] = recent_progress
        
        # Identify gaps in treatment
        treatment_gaps = self._identify_treatment_gaps(
            session_history,
            therapeutic_goals,
            current_interventions
        )
        
        # Generate optimization recommendations
        recommendations = []
        
        # Recommend continuing effective interventions
        for intervention, effectiveness in intervention_effectiveness.items():
            if effectiveness >= 0.6:
                recommendations.append({
                    'action': 'continue',
                    'intervention': intervention,
                    'reason': f'Showing positive results (effectiveness: {effectiveness:.2f})',
                    'priority': 'high'
                })
            elif effectiveness < 0.4:
                recommendations.append({
                    'action': 'modify_or_replace',
                    'intervention': intervention,
                    'reason': f'Limited effectiveness (score: {effectiveness:.2f})',
                    'priority': 'high'
                })
        
        # Recommend new interventions for gaps
        for gap in treatment_gaps:
            gap_interventions = self._suggest_interventions_for_gap(gap)
            for intervention in gap_interventions:
                recommendations.append({
                    'action': 'add',
                    'intervention': intervention,
                    'reason': f'Addresses treatment gap: {gap}',
                    'priority': 'medium'
                })
        
        # Recommend goal adjustments if needed
        goal_adjustments = []
        for goal, progress in goal_progress.items():
            if progress >= 0.8:
                goal_adjustments.append({
                    'goal': goal,
                    'recommendation': 'consider_new_goal',
                    'reason': 'Goal largely achieved, consider setting new objectives'
                })
            elif progress < 0.2 and len(session_history) >= 10:
                goal_adjustments.append({
                    'goal': goal,
                    'recommendation': 'reassess_goal',
                    'reason': 'Limited progress, may need goal refinement'
                })
        
        optimization = {
            'client_id': client_id[:8] + '...',
            'goal_progress': {k: round(v, 2) for k, v in goal_progress.items()},
            'intervention_effectiveness': {
                k: round(v, 2) for k, v in intervention_effectiveness.items()
            },
            'treatment_gaps': treatment_gaps,
            'recommendations': recommendations,
            'goal_adjustments': goal_adjustments,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Optimized treatment path for client {client_id}: "
            f"{len(recommendations)} recommendations, {len(treatment_gaps)} gaps identified"
        )
        
        return optimization

    # ========== Helper Methods ==========
    
    def _calculate_prediction_factors(
        self,
        session_history: List[Dict[str, Any]],
        current_session: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate factors for outcome prediction"""
        factors = {}
        
        # Sentiment trend
        sentiment_scores = [
            self._sentiment_to_score(s.get('sentiment', SentimentType.NEUTRAL.value))
            for s in session_history
        ]
        
        if len(sentiment_scores) >= 2:
            # Calculate trend
            first_half_avg = sum(sentiment_scores[:len(sentiment_scores)//2]) / (len(sentiment_scores)//2)
            second_half_avg = sum(sentiment_scores[len(sentiment_scores)//2:]) / (len(sentiment_scores) - len(sentiment_scores)//2)
            trend = (second_half_avg - first_half_avg + 1) / 2  # Normalize to 0-1
            factors['sentiment_trend'] = min(max(trend, 0), 1)
        else:
            factors['sentiment_trend'] = 0.5
        
        # Engagement level
        engagement_scores = [
            min(s.get('message_count', 0) / 15, 1.0)
            for s in session_history
        ]
        factors['engagement_level'] = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.5
        
        # Milestone frequency
        total_milestones = sum(len(s.get('milestones', [])) for s in session_history)
        milestone_rate = total_milestones / len(session_history)
        factors['milestone_frequency'] = min(milestone_rate / 2, 1.0)  # Normalize assuming 2 per session is high
        
        # Emotional stability
        sentiment_variance = self._calculate_variance(sentiment_scores)
        factors['emotional_stability'] = min(max(1 - sentiment_variance, 0), 1)
        
        # Topic resolution (topics that appear less frequently over time)
        if len(session_history) >= 6:
            early_topics = set()
            late_topics = set()
            for s in session_history[:len(session_history)//2]:
                early_topics.update(s.get('topics', []))
            for s in session_history[len(session_history)//2:]:
                late_topics.update(s.get('topics', []))
            
            resolved_topics = len(early_topics - late_topics)
            total_topics = len(early_topics)
            factors['topic_resolution'] = resolved_topics / total_topics if total_topics > 0 else 0.5
        else:
            factors['topic_resolution'] = 0.5
        
        # Risk trend (lower risk over time is better)
        risk_scores = []
        for s in session_history:
            risk = s.get('risk_level', RiskLevel.LOW.value)
            if risk == RiskLevel.HIGH.value:
                risk_scores.append(1.0)
            elif risk == RiskLevel.MEDIUM.value:
                risk_scores.append(0.5)
            else:
                risk_scores.append(0.0)
        
        if len(risk_scores) >= 2:
            first_half_risk = sum(risk_scores[:len(risk_scores)//2]) / (len(risk_scores)//2)
            second_half_risk = sum(risk_scores[len(risk_scores)//2:]) / (len(risk_scores) - len(risk_scores)//2)
            risk_improvement = (first_half_risk - second_half_risk + 1) / 2  # Normalize
            factors['risk_trend'] = min(max(risk_improvement, 0), 1)
        else:
            factors['risk_trend'] = 0.5
        
        return factors
    
    def _calculate_prediction_confidence(
        self,
        session_history: List[Dict[str, Any]],
        factors: Dict[str, float]
    ) -> float:
        """Calculate confidence in prediction"""
        # Base confidence on number of sessions
        session_confidence = min(len(session_history) / 10, 1.0)
        
        # Reduce confidence if factors are inconsistent
        factor_variance = self._calculate_variance(list(factors.values()))
        consistency_confidence = 1 - min(factor_variance, 0.5)
        
        # Combined confidence
        confidence = (session_confidence * 0.6 + consistency_confidence * 0.4)
        
        return confidence
    
    def _sentiment_to_score(self, sentiment: str) -> float:
        """Convert sentiment to numeric score"""
        if sentiment == SentimentType.POSITIVE.value:
            return 1.0
        elif sentiment == SentimentType.NEUTRAL.value:
            return 0.0
        else:
            return -1.0
    
    def _calculate_average_sentiment(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate average sentiment score"""
        if not sessions:
            return 0.0
        
        scores = [
            self._sentiment_to_score(s.get('sentiment', SentimentType.NEUTRAL.value))
            for s in sessions
        ]
        return sum(scores) / len(scores)
    
    def _calculate_average_engagement(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate average engagement score"""
        if not sessions:
            return 0.0
        
        engagement_scores = [
            min(s.get('message_count', 0) / 15, 1.0)
            for s in sessions
        ]
        return sum(engagement_scores) / len(engagement_scores)
    
    def _calculate_milestone_frequency(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate milestone frequency"""
        if not sessions:
            return 0.0
        
        total_milestones = sum(len(s.get('milestones', [])) for s in sessions)
        return total_milestones / len(sessions)
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance
    
    def _analyze_historical_patterns(self, session_history: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Analyze historical patterns"""
        patterns = {}
        
        # Check for low engagement
        avg_engagement = self._calculate_average_engagement(session_history)
        patterns['low_engagement'] = avg_engagement < 0.4
        
        # Check for recurring relationship issues
        all_topics = []
        for session in session_history:
            all_topics.extend(session.get('topics', []))
        
        topic_counts = Counter(all_topics)
        patterns['recurring_relationship_issues'] = topic_counts.get('relationships', 0) >= len(session_history) * 0.5
        
        return patterns
    
    def _generate_risk_recommendations(
        self,
        risk_category: RiskCategory,
        risk_factors: List[str]
    ) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        if risk_category == RiskCategory.IMMEDIATE_CRISIS:
            recommendations.append('Immediate therapist intervention required')
            recommendations.append('Consider crisis hotline referral')
            recommendations.append('Ensure safety plan is in place')
        elif risk_category == RiskCategory.HIGH_RISK:
            recommendations.append('Schedule follow-up with human therapist within 24 hours')
            recommendations.append('Increase session frequency')
            recommendations.append('Implement crisis intervention protocols')
        elif risk_category == RiskCategory.MODERATE_RISK:
            recommendations.append('Monitor closely in upcoming sessions')
            recommendations.append('Consider additional support resources')
        
        # Factor-specific recommendations
        if 'declining_mood_trend' in risk_factors:
            recommendations.append('Focus on mood stabilization techniques')
        
        if 'low_engagement' in risk_factors:
            recommendations.append('Explore barriers to engagement')
        
        return recommendations
    
    def _analyze_goal_progress(
        self,
        session_history: List[Dict[str, Any]],
        therapeutic_goals: List[str]
    ) -> Dict[str, float]:
        """Analyze progress toward therapeutic goals"""
        goal_progress = {}
        
        # Simple heuristic: check if goal-related topics appear less frequently over time
        for goal in therapeutic_goals:
            goal_lower = goal.lower()
            
            # Count mentions in first half vs second half
            mid_point = len(session_history) // 2
            first_half_mentions = 0
            second_half_mentions = 0
            
            for i, session in enumerate(session_history):
                topics = session.get('topics', [])
                mentions = sum(1 for topic in topics if goal_lower in topic.lower())
                
                if i < mid_point:
                    first_half_mentions += mentions
                else:
                    second_half_mentions += mentions
            
            # If mentions decrease, assume progress (issue being resolved)
            if first_half_mentions > 0:
                progress = 1 - (second_half_mentions / first_half_mentions)
                goal_progress[goal] = min(max(progress, 0), 1)
            else:
                goal_progress[goal] = 0.5
        
        return goal_progress
    
    def _calculate_recent_progress(self, recent_sessions: List[Dict[str, Any]]) -> float:
        """Calculate recent progress score"""
        if not recent_sessions:
            return 0.5
        
        # Average sentiment
        avg_sentiment = self._calculate_average_sentiment(recent_sessions)
        
        # Milestone frequency
        milestone_freq = self._calculate_milestone_frequency(recent_sessions)
        
        # Combined score
        progress = (avg_sentiment + 1) / 2 * 0.6 + min(milestone_freq / 2, 1.0) * 0.4
        
        return progress
    
    def _identify_treatment_gaps(
        self,
        session_history: List[Dict[str, Any]],
        therapeutic_goals: List[str],
        current_interventions: List[str]
    ) -> List[str]:
        """Identify gaps in current treatment"""
        gaps = []
        
        # Check if all major topic areas are being addressed
        all_topics = []
        for session in session_history:
            all_topics.extend(session.get('topics', []))
        
        topic_counts = Counter(all_topics)
        frequent_topics = [topic for topic, count in topic_counts.items() if count >= 2]
        
        # Check if interventions match frequent topics
        for topic in frequent_topics:
            if topic in self.intervention_mapping:
                recommended_interventions = self.intervention_mapping[topic]
                if not any(interv.value in current_interventions for interv in recommended_interventions):
                    gaps.append(topic)
        
        return gaps
    
    def _suggest_interventions_for_gap(self, gap: str) -> List[str]:
        """Suggest interventions for a treatment gap"""
        if gap in self.intervention_mapping:
            return [interv.value for interv in self.intervention_mapping[gap]]
        return []
