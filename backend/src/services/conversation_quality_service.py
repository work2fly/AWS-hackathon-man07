"""
Conversation Quality Assurance Service for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Response quality monitoring, therapeutic appropriateness validation,
conversation coherence checks, and feedback loops for continuous improvement.

Validates: Requirements 3.4, 3.7
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

from ..services.therapeutic_conversation_engine import (
    ConversationPhase,
    EmotionalState,
    InterventionType,
    ConversationTurn
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class QualityDimension(Enum):
    """Quality dimensions for assessment"""
    THERAPEUTIC_APPROPRIATENESS = "therapeutic_appropriateness"
    EMPATHY = "empathy"
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    SAFETY = "safety"
    PROFESSIONALISM = "professionalism"


class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@dataclass
class QualityScore:
    """Quality score for a specific dimension"""
    dimension: QualityDimension
    score: float  # 0.0 to 1.0
    level: QualityLevel
    feedback: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResponseQualityAssessment:
    """Comprehensive quality assessment for a response"""
    turn_id: str
    session_id: str
    overall_score: float
    overall_level: QualityLevel
    dimension_scores: List[QualityScore]
    issues_detected: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationCoherenceMetrics:
    """Metrics for conversation coherence"""
    topic_consistency_score: float
    context_continuity_score: float
    logical_flow_score: float
    overall_coherence_score: float
    coherence_issues: List[str]


class ConversationQualityService:
    """
    Service for monitoring and assuring conversation quality
    
    Provides response quality monitoring, therapeutic appropriateness validation,
    coherence checking, and feedback loops for improvement.
    """
    
    def __init__(self):
        """Initialize conversation quality service"""
        # Track quality metrics per session
        self._session_quality_history: Dict[str, List[ResponseQualityAssessment]] = defaultdict(list)
        
        # Track feedback for continuous improvement
        self._feedback_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        logger.info("Conversation Quality Service initialized")
    
    # ========== Response Quality Monitoring ==========
    
    def assess_response_quality(
        self,
        session_id: str,
        turn_id: str,
        response_text: str,
        intervention_type: InterventionType,
        client_emotional_state: EmotionalState,
        conversation_phase: ConversationPhase,
        conversation_context: Optional[List[ConversationTurn]] = None
    ) -> ResponseQualityAssessment:
        """
        Assess the quality of an AI response
        
        Args:
            session_id: Session identifier
            turn_id: Turn identifier
            response_text: AI response text
            intervention_type: Type of intervention used
            client_emotional_state: Client's emotional state
            conversation_phase: Current conversation phase
            conversation_context: Recent conversation turns
            
        Returns:
            ResponseQualityAssessment object
        """
        dimension_scores = []
        issues = []
        recommendations = []
        
        # Assess therapeutic appropriateness
        therapeutic_score = self._assess_therapeutic_appropriateness(
            response_text,
            intervention_type,
            client_emotional_state,
            conversation_phase
        )
        dimension_scores.append(therapeutic_score)
        
        if therapeutic_score.score < 0.6:
            issues.append(f"Low therapeutic appropriateness: {therapeutic_score.feedback}")
            recommendations.append("Review therapeutic intervention guidelines")
        
        # Assess empathy
        empathy_score = self._assess_empathy(
            response_text,
            client_emotional_state
        )
        dimension_scores.append(empathy_score)
        
        if empathy_score.score < 0.6:
            issues.append(f"Low empathy: {empathy_score.feedback}")
            recommendations.append("Increase empathetic language and validation")
        
        # Assess coherence
        coherence_score = self._assess_coherence(
            response_text,
            conversation_context or []
        )
        dimension_scores.append(coherence_score)
        
        if coherence_score.score < 0.6:
            issues.append(f"Low coherence: {coherence_score.feedback}")
            recommendations.append("Ensure response relates to recent conversation")
        
        # Assess relevance
        relevance_score = self._assess_relevance(
            response_text,
            conversation_context or []
        )
        dimension_scores.append(relevance_score)
        
        if relevance_score.score < 0.6:
            issues.append(f"Low relevance: {relevance_score.feedback}")
            recommendations.append("Focus on client's current concerns")
        
        # Assess safety
        safety_score = self._assess_safety(response_text)
        dimension_scores.append(safety_score)
        
        if safety_score.score < 0.8:
            issues.append(f"Safety concern: {safety_score.feedback}")
            recommendations.append("Review safety guidelines immediately")
        
        # Assess professionalism
        professionalism_score = self._assess_professionalism(response_text)
        dimension_scores.append(professionalism_score)
        
        if professionalism_score.score < 0.7:
            issues.append(f"Professionalism issue: {professionalism_score.feedback}")
            recommendations.append("Maintain professional therapeutic boundaries")
        
        # Calculate overall score
        overall_score = sum(s.score for s in dimension_scores) / len(dimension_scores)
        overall_level = self._score_to_level(overall_score)
        
        # Create assessment
        assessment = ResponseQualityAssessment(
            turn_id=turn_id,
            session_id=session_id,
            overall_score=overall_score,
            overall_level=overall_level,
            dimension_scores=dimension_scores,
            issues_detected=issues,
            recommendations=recommendations
        )
        
        # Store in history
        self._session_quality_history[session_id].append(assessment)
        
        logger.info(
            f"Assessed response quality for session {session_id}, turn {turn_id}: "
            f"{overall_level.value} ({overall_score:.2f})"
        )
        
        return assessment
    
    def _assess_therapeutic_appropriateness(
        self,
        response_text: str,
        intervention_type: InterventionType,
        client_emotional_state: EmotionalState,
        conversation_phase: ConversationPhase
    ) -> QualityScore:
        """Assess therapeutic appropriateness of response"""
        score = 0.8  # Default good score
        feedback = "Response is therapeutically appropriate"
        
        # Check intervention matches emotional state
        if client_emotional_state == EmotionalState.DISTRESSED:
            if intervention_type not in [InterventionType.VALIDATION, InterventionType.CRISIS_RESPONSE]:
                score -= 0.2
                feedback = "Intervention may not match client's distressed state"
        
        # Check phase appropriateness
        if conversation_phase == ConversationPhase.OPENING:
            if intervention_type in [InterventionType.HOMEWORK, InterventionType.GOAL_SETTING]:
                score -= 0.1
                feedback = "Intervention may be premature for opening phase"
        
        # Check response length (therapeutic responses should be moderate)
        word_count = len(response_text.split())
        if word_count < 10:
            score -= 0.1
            feedback = "Response may be too brief for therapeutic context"
        elif word_count > 150:
            score -= 0.1
            feedback = "Response may be too lengthy, consider brevity"
        
        level = self._score_to_level(score)
        
        return QualityScore(
            dimension=QualityDimension.THERAPEUTIC_APPROPRIATENESS,
            score=max(0.0, min(1.0, score)),
            level=level,
            feedback=feedback
        )
    
    def _assess_empathy(
        self,
        response_text: str,
        client_emotional_state: EmotionalState
    ) -> QualityScore:
        """Assess empathy in response"""
        score = 0.7  # Default moderate score
        feedback = "Response shows adequate empathy"
        
        response_lower = response_text.lower()
        
        # Check for empathetic language
        empathy_indicators = [
            'understand', 'hear', 'feel', 'sounds like', 'seems like',
            'must be', 'appreciate', 'recognize', 'acknowledge'
        ]
        
        empathy_count = sum(1 for indicator in empathy_indicators if indicator in response_lower)
        
        if empathy_count >= 2:
            score = 0.9
            feedback = "Response demonstrates strong empathy"
        elif empathy_count == 1:
            score = 0.75
            feedback = "Response shows good empathy"
        else:
            score = 0.5
            feedback = "Response could benefit from more empathetic language"
        
        # Adjust for emotional state
        if client_emotional_state in [EmotionalState.DISTRESSED, EmotionalState.SAD]:
            if empathy_count == 0:
                score -= 0.2
                feedback = "Response lacks empathy for client's emotional state"
        
        level = self._score_to_level(score)
        
        return QualityScore(
            dimension=QualityDimension.EMPATHY,
            score=max(0.0, min(1.0, score)),
            level=level,
            feedback=feedback
        )
    
    def _assess_coherence(
        self,
        response_text: str,
        conversation_context: List[ConversationTurn]
    ) -> QualityScore:
        """Assess coherence with conversation context"""
        score = 0.8  # Default good score
        feedback = "Response is coherent with conversation"
        
        if not conversation_context:
            return QualityScore(
                dimension=QualityDimension.COHERENCE,
                score=score,
                level=self._score_to_level(score),
                feedback="No context available for coherence assessment"
            )
        
        # Get recent client turns
        recent_client_turns = [
            turn for turn in conversation_context[-5:]
            if turn.speaker == "client"
        ]
        
        if not recent_client_turns:
            score = 0.7
            feedback = "Limited context for coherence assessment"
        else:
            # Simple coherence check: look for topic continuity
            # In production, this would use NLP for semantic similarity
            last_client_text = recent_client_turns[-1].content.lower()
            response_lower = response_text.lower()
            
            # Extract key words from client's last message
            client_words = set(last_client_text.split())
            response_words = set(response_lower.split())
            
            # Calculate word overlap (simple coherence metric)
            overlap = len(client_words.intersection(response_words))
            
            if overlap >= 3:
                score = 0.9
                feedback = "Response shows strong coherence with client's message"
            elif overlap >= 1:
                score = 0.75
                feedback = "Response maintains coherence with conversation"
            else:
                score = 0.6
                feedback = "Response may lack clear connection to client's message"
        
        level = self._score_to_level(score)
        
        return QualityScore(
            dimension=QualityDimension.COHERENCE,
            score=max(0.0, min(1.0, score)),
            level=level,
            feedback=feedback
        )
    
    def _assess_relevance(
        self,
        response_text: str,
        conversation_context: List[ConversationTurn]
    ) -> QualityScore:
        """Assess relevance to client's concerns"""
        score = 0.8  # Default good score
        feedback = "Response is relevant to client's concerns"
        
        # Similar to coherence but focuses on addressing client's needs
        # In production, this would use more sophisticated NLP
        
        if not conversation_context:
            return QualityScore(
                dimension=QualityDimension.RELEVANCE,
                score=score,
                level=self._score_to_level(score),
                feedback="No context available for relevance assessment"
            )
        
        # Check if response addresses client's concerns
        response_lower = response_text.lower()
        
        # Look for question words (indicates engagement)
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        has_questions = any(indicator in response_lower for indicator in question_indicators)
        
        if has_questions:
            score += 0.1
            feedback = "Response engages with client through questions"
        
        level = self._score_to_level(score)
        
        return QualityScore(
            dimension=QualityDimension.RELEVANCE,
            score=max(0.0, min(1.0, score)),
            level=level,
            feedback=feedback
        )
    
    def _assess_safety(self, response_text: str) -> QualityScore:
        """Assess safety of response"""
        score = 1.0  # Default perfect score
        feedback = "Response is safe and appropriate"
        
        response_lower = response_text.lower()
        
        # Check for potentially harmful content
        harmful_indicators = [
            'kill yourself', 'end it all', 'give up', 'hopeless',
            'no point', 'better off dead'
        ]
        
        for indicator in harmful_indicators:
            if indicator in response_lower:
                score = 0.0
                feedback = f"CRITICAL: Response contains harmful content: '{indicator}'"
                break
        
        # Check for inappropriate personal disclosure
        inappropriate_indicators = [
            'my personal', 'i also', 'i have', 'i feel', 'i think'
        ]
        
        inappropriate_count = sum(1 for indicator in inappropriate_indicators if indicator in response_lower)
        
        if inappropriate_count >= 2:
            score -= 0.2
            feedback = "Response may contain inappropriate personal disclosure"
        
        level = self._score_to_level(score)
        
        return QualityScore(
            dimension=QualityDimension.SAFETY,
            score=max(0.0, min(1.0, score)),
            level=level,
            feedback=feedback
        )
    
    def _assess_professionalism(self, response_text: str) -> QualityScore:
        """Assess professionalism of response"""
        score = 0.9  # Default high score
        feedback = "Response maintains professional standards"
        
        response_lower = response_text.lower()
        
        # Check for unprofessional language
        unprofessional_indicators = [
            'dude', 'bro', 'lol', 'omg', 'wtf', 'damn', 'hell'
        ]
        
        for indicator in unprofessional_indicators:
            if indicator in response_lower:
                score -= 0.3
                feedback = f"Response contains unprofessional language: '{indicator}'"
                break
        
        # Check for appropriate therapeutic language
        professional_indicators = [
            'explore', 'consider', 'reflect', 'notice', 'observe',
            'experience', 'perspective', 'feelings', 'thoughts'
        ]
        
        professional_count = sum(1 for indicator in professional_indicators if indicator in response_lower)
        
        if professional_count >= 2:
            score = min(1.0, score + 0.1)
            feedback = "Response uses appropriate therapeutic language"
        
        level = self._score_to_level(score)
        
        return QualityScore(
            dimension=QualityDimension.PROFESSIONALISM,
            score=max(0.0, min(1.0, score)),
            level=level,
            feedback=feedback
        )
    
    def _score_to_level(self, score: float) -> QualityLevel:
        """Convert numeric score to quality level"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.75:
            return QualityLevel.GOOD
        elif score >= 0.6:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.4:
            return QualityLevel.NEEDS_IMPROVEMENT
        else:
            return QualityLevel.POOR
    
    # ========== Conversation Coherence Checking ==========
    
    def check_conversation_coherence(
        self,
        session_id: str,
        conversation_turns: List[ConversationTurn]
    ) -> ConversationCoherenceMetrics:
        """
        Check overall conversation coherence
        
        Args:
            session_id: Session identifier
            conversation_turns: List of conversation turns
            
        Returns:
            ConversationCoherenceMetrics object
        """
        issues = []
        
        # Assess topic consistency
        topic_score = self._assess_topic_consistency(conversation_turns)
        if topic_score < 0.6:
            issues.append("Conversation jumps between topics too frequently")
        
        # Assess context continuity
        context_score = self._assess_context_continuity(conversation_turns)
        if context_score < 0.6:
            issues.append("Conversation lacks continuity between turns")
        
        # Assess logical flow
        flow_score = self._assess_logical_flow(conversation_turns)
        if flow_score < 0.6:
            issues.append("Conversation flow is disjointed")
        
        # Calculate overall coherence
        overall_score = (topic_score + context_score + flow_score) / 3.0
        
        metrics = ConversationCoherenceMetrics(
            topic_consistency_score=topic_score,
            context_continuity_score=context_score,
            logical_flow_score=flow_score,
            overall_coherence_score=overall_score,
            coherence_issues=issues
        )
        
        logger.info(
            f"Checked conversation coherence for session {session_id}: "
            f"{overall_score:.2f}"
        )
        
        return metrics
    
    def _assess_topic_consistency(self, turns: List[ConversationTurn]) -> float:
        """Assess topic consistency across turns"""
        if len(turns) < 3:
            return 1.0  # Not enough turns to assess
        
        # Simple heuristic: check if consecutive turns share keywords
        # In production, use topic modeling
        
        consistency_scores = []
        
        for i in range(len(turns) - 1):
            current_words = set(turns[i].content.lower().split())
            next_words = set(turns[i + 1].content.lower().split())
            
            overlap = len(current_words.intersection(next_words))
            total = len(current_words.union(next_words))
            
            if total > 0:
                consistency_scores.append(overlap / total)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.5
    
    def _assess_context_continuity(self, turns: List[ConversationTurn]) -> float:
        """Assess context continuity across turns"""
        if len(turns) < 2:
            return 1.0
        
        # Check if agent responses reference client's previous statements
        continuity_score = 0.8  # Default good score
        
        for i in range(1, len(turns)):
            if turns[i].speaker == "agent" and i > 0:
                # Check if agent response relates to previous client turn
                prev_client_turns = [t for t in turns[:i] if t.speaker == "client"]
                if prev_client_turns:
                    # Simple check: does response reference recent client content
                    # In production, use semantic similarity
                    continuity_score += 0.1
        
        return min(1.0, continuity_score / len(turns))
    
    def _assess_logical_flow(self, turns: List[ConversationTurn]) -> float:
        """Assess logical flow of conversation"""
        if len(turns) < 3:
            return 1.0
        
        # Check for abrupt topic changes or non-sequiturs
        # In production, use discourse analysis
        
        flow_score = 0.8  # Default good score
        
        # Simple heuristic: check turn lengths are reasonable
        for turn in turns:
            word_count = len(turn.content.split())
            if word_count < 3:
                flow_score -= 0.05  # Very short turns may indicate issues
            elif word_count > 200:
                flow_score -= 0.05  # Very long turns may indicate monologuing
        
        return max(0.0, min(1.0, flow_score))
    
    # ========== Feedback and Continuous Improvement ==========
    
    def record_feedback(
        self,
        session_id: str,
        turn_id: str,
        feedback_type: str,
        feedback_score: float,
        feedback_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record feedback for continuous improvement
        
        Args:
            session_id: Session identifier
            turn_id: Turn identifier
            feedback_type: Type of feedback (e.g., 'user_rating', 'therapist_review')
            feedback_score: Feedback score (0.0-1.0)
            feedback_notes: Optional feedback notes
            
        Returns:
            Feedback record
        """
        feedback_record = {
            'session_id': session_id,
            'turn_id': turn_id,
            'feedback_type': feedback_type,
            'feedback_score': feedback_score,
            'feedback_notes': feedback_notes,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._feedback_history[session_id].append(feedback_record)
        
        logger.info(
            f"Recorded feedback for session {session_id}, turn {turn_id}: "
            f"{feedback_type} = {feedback_score}"
        )
        
        return feedback_record
    
    def get_quality_trends(
        self,
        session_id: str,
        dimension: Optional[QualityDimension] = None
    ) -> Dict[str, Any]:
        """
        Get quality trends for a session
        
        Args:
            session_id: Session identifier
            dimension: Optional specific dimension to analyze
            
        Returns:
            Quality trends dictionary
        """
        assessments = self._session_quality_history.get(session_id, [])
        
        if not assessments:
            return {
                'session_id': session_id,
                'assessment_count': 0,
                'trends': {}
            }
        
        if dimension:
            # Get trends for specific dimension
            scores = [
                score.score
                for assessment in assessments
                for score in assessment.dimension_scores
                if score.dimension == dimension
            ]
            
            return {
                'session_id': session_id,
                'dimension': dimension.value,
                'assessment_count': len(scores),
                'average_score': sum(scores) / len(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'trend': 'improving' if len(scores) > 1 and scores[-1] > scores[0] else 'stable'
            }
        else:
            # Get overall trends
            overall_scores = [a.overall_score for a in assessments]
            
            return {
                'session_id': session_id,
                'assessment_count': len(assessments),
                'average_score': sum(overall_scores) / len(overall_scores),
                'min_score': min(overall_scores),
                'max_score': max(overall_scores),
                'trend': 'improving' if len(overall_scores) > 1 and overall_scores[-1] > overall_scores[0] else 'stable',
                'recent_issues': [
                    issue
                    for assessment in assessments[-5:]
                    for issue in assessment.issues_detected
                ]
            }
    
    def get_improvement_recommendations(
        self,
        session_id: str
    ) -> List[str]:
        """
        Get improvement recommendations based on quality assessments
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of recommendations
        """
        assessments = self._session_quality_history.get(session_id, [])
        
        if not assessments:
            return ["No quality assessments available yet"]
        
        # Aggregate recommendations
        all_recommendations = []
        recommendation_counts = defaultdict(int)
        
        for assessment in assessments:
            for rec in assessment.recommendations:
                recommendation_counts[rec] += 1
        
        # Sort by frequency
        sorted_recs = sorted(
            recommendation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top recommendations
        return [rec for rec, count in sorted_recs[:5]]
