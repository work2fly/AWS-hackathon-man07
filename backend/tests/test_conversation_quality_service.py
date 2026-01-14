"""
Unit tests for Conversation Quality Service
🏆 Breaking Barriers UK 2026 compliant

Tests response quality monitoring, therapeutic appropriateness validation,
coherence checking, and feedback loops.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.services.conversation_quality_service import (
    ConversationQualityService,
    QualityDimension,
    QualityLevel,
    QualityScore,
    ResponseQualityAssessment,
    ConversationCoherenceMetrics
)
from src.services.therapeutic_conversation_engine import (
    ConversationPhase,
    EmotionalState,
    InterventionType,
    ConversationTurn,
    TurnType
)


class TestConversationQualityService:
    """Test suite for conversation quality service"""
    
    @pytest.fixture
    def quality_service(self):
        """Create quality service instance"""
        return ConversationQualityService()
    
    @pytest.fixture
    def sample_conversation_turns(self):
        """Create sample conversation turns"""
        return [
            ConversationTurn(
                turn_id="turn_1",
                turn_type=TurnType.CLIENT_SPEAKING,
                speaker="client",
                content="I've been feeling really anxious lately",
                timestamp=datetime.utcnow(),
                duration_seconds=3.0,
                emotional_state=EmotionalState.ANXIOUS
            ),
            ConversationTurn(
                turn_id="turn_2",
                turn_type=TurnType.AGENT_SPEAKING,
                speaker="agent",
                content="I hear that you're feeling anxious. Can you tell me more about what's been causing these feelings?",
                timestamp=datetime.utcnow(),
                duration_seconds=4.0,
                intervention_type=InterventionType.REFLECTION
            ),
            ConversationTurn(
                turn_id="turn_3",
                turn_type=TurnType.CLIENT_SPEAKING,
                speaker="client",
                content="It's mostly work stress and deadlines",
                timestamp=datetime.utcnow(),
                duration_seconds=2.5,
                emotional_state=EmotionalState.ANXIOUS
            )
        ]
    
    # ========== Response Quality Assessment Tests ==========
    
    def test_assess_response_quality_good_response(self, quality_service):
        """Test assessing a good quality response"""
        assessment = quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_1",
            response_text="I understand that you're feeling anxious. That must be difficult. Can you tell me more about what's been happening?",
            intervention_type=InterventionType.REFLECTION,
            client_emotional_state=EmotionalState.ANXIOUS,
            conversation_phase=ConversationPhase.EXPLORATION
        )
        
        assert assessment is not None
        assert assessment.session_id == "session_123"
        assert assessment.turn_id == "turn_1"
        assert assessment.overall_score > 0.6
        assert assessment.overall_level in [QualityLevel.GOOD, QualityLevel.EXCELLENT, QualityLevel.ACCEPTABLE]
        assert len(assessment.dimension_scores) == 6  # All dimensions assessed
    
    def test_assess_response_quality_poor_response(self, quality_service):
        """Test assessing a poor quality response"""
        assessment = quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_2",
            response_text="Ok",  # Too brief
            intervention_type=InterventionType.REFLECTION,
            client_emotional_state=EmotionalState.DISTRESSED,
            conversation_phase=ConversationPhase.EXPLORATION
        )
        
        assert assessment is not None
        assert assessment.overall_score < 0.8  # Should be lower due to brevity
        assert len(assessment.issues_detected) > 0
        assert len(assessment.recommendations) > 0
    
    def test_assess_therapeutic_appropriateness(self, quality_service):
        """Test therapeutic appropriateness assessment"""
        assessment = quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_3",
            response_text="I hear that you're feeling distressed. Let's take a moment to ground ourselves.",
            intervention_type=InterventionType.VALIDATION,
            client_emotional_state=EmotionalState.DISTRESSED,
            conversation_phase=ConversationPhase.INTERVENTION
        )
        
        # Find therapeutic appropriateness score
        therapeutic_score = next(
            (s for s in assessment.dimension_scores 
             if s.dimension == QualityDimension.THERAPEUTIC_APPROPRIATENESS),
            None
        )
        
        assert therapeutic_score is not None
        assert therapeutic_score.score > 0.6  # Should be appropriate
    
    def test_assess_empathy_high(self, quality_service):
        """Test empathy assessment for empathetic response"""
        assessment = quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_4",
            response_text="I understand how difficult this must be for you. I hear your pain and I'm here to support you.",
            intervention_type=InterventionType.VALIDATION,
            client_emotional_state=EmotionalState.SAD,
            conversation_phase=ConversationPhase.EXPLORATION
        )
        
        empathy_score = next(
            (s for s in assessment.dimension_scores 
             if s.dimension == QualityDimension.EMPATHY),
            None
        )
        
        assert empathy_score is not None
        assert empathy_score.score > 0.7  # Should be high empathy
    
    def test_assess_safety_harmful_content(self, quality_service):
        """Test safety assessment detects harmful content"""
        assessment = quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_5",
            response_text="Maybe you should just give up",  # Harmful
            intervention_type=InterventionType.REFLECTION,
            client_emotional_state=EmotionalState.SAD,
            conversation_phase=ConversationPhase.EXPLORATION
        )
        
        safety_score = next(
            (s for s in assessment.dimension_scores 
             if s.dimension == QualityDimension.SAFETY),
            None
        )
        
        assert safety_score is not None
        assert safety_score.score < 0.5  # Should be very low
        assert "harmful" in safety_score.feedback.lower()
    
    def test_assess_professionalism(self, quality_service):
        """Test professionalism assessment"""
        assessment = quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_6",
            response_text="Let's explore your feelings and consider different perspectives on this situation.",
            intervention_type=InterventionType.REFLECTION,
            client_emotional_state=EmotionalState.NEUTRAL,
            conversation_phase=ConversationPhase.EXPLORATION
        )
        
        professionalism_score = next(
            (s for s in assessment.dimension_scores 
             if s.dimension == QualityDimension.PROFESSIONALISM),
            None
        )
        
        assert professionalism_score is not None
        assert professionalism_score.score > 0.8  # Should be professional
    
    # ========== Coherence Checking Tests ==========
    
    def test_check_conversation_coherence(self, quality_service, sample_conversation_turns):
        """Test checking conversation coherence"""
        metrics = quality_service.check_conversation_coherence(
            session_id="session_123",
            conversation_turns=sample_conversation_turns
        )
        
        assert metrics is not None
        assert 0.0 <= metrics.overall_coherence_score <= 1.0
        assert 0.0 <= metrics.topic_consistency_score <= 1.0
        assert 0.0 <= metrics.context_continuity_score <= 1.0
        assert 0.0 <= metrics.logical_flow_score <= 1.0
        assert isinstance(metrics.coherence_issues, list)
    
    def test_coherence_with_few_turns(self, quality_service):
        """Test coherence checking with minimal turns"""
        turns = [
            ConversationTurn(
                turn_id="turn_1",
                turn_type=TurnType.CLIENT_SPEAKING,
                speaker="client",
                content="Hello",
                timestamp=datetime.utcnow(),
                duration_seconds=1.0
            )
        ]
        
        metrics = quality_service.check_conversation_coherence(
            session_id="session_123",
            conversation_turns=turns
        )
        
        assert metrics is not None
        # Should have high scores with minimal turns (not enough to assess)
        assert metrics.overall_coherence_score >= 0.5
    
    # ========== Feedback and Improvement Tests ==========
    
    def test_record_feedback(self, quality_service):
        """Test recording feedback"""
        feedback = quality_service.record_feedback(
            session_id="session_123",
            turn_id="turn_1",
            feedback_type="user_rating",
            feedback_score=0.8,
            feedback_notes="Good response"
        )
        
        assert feedback is not None
        assert feedback['session_id'] == "session_123"
        assert feedback['turn_id'] == "turn_1"
        assert feedback['feedback_type'] == "user_rating"
        assert feedback['feedback_score'] == 0.8
        assert feedback['feedback_notes'] == "Good response"
        assert 'timestamp' in feedback
    
    def test_get_quality_trends_no_data(self, quality_service):
        """Test getting quality trends with no data"""
        trends = quality_service.get_quality_trends(session_id="nonexistent_session")
        
        assert trends is not None
        assert trends['assessment_count'] == 0
    
    def test_get_quality_trends_with_data(self, quality_service):
        """Test getting quality trends with assessment data"""
        # Create some assessments
        for i in range(3):
            quality_service.assess_response_quality(
                session_id="session_123",
                turn_id=f"turn_{i}",
                response_text="I understand your feelings. Let's explore this together.",
                intervention_type=InterventionType.REFLECTION,
                client_emotional_state=EmotionalState.NEUTRAL,
                conversation_phase=ConversationPhase.EXPLORATION
            )
        
        trends = quality_service.get_quality_trends(session_id="session_123")
        
        assert trends is not None
        assert trends['assessment_count'] == 3
        assert 'average_score' in trends
        assert 'min_score' in trends
        assert 'max_score' in trends
        assert 'trend' in trends
    
    def test_get_quality_trends_specific_dimension(self, quality_service):
        """Test getting quality trends for specific dimension"""
        # Create assessment
        quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_1",
            response_text="I understand your feelings.",
            intervention_type=InterventionType.REFLECTION,
            client_emotional_state=EmotionalState.NEUTRAL,
            conversation_phase=ConversationPhase.EXPLORATION
        )
        
        trends = quality_service.get_quality_trends(
            session_id="session_123",
            dimension=QualityDimension.EMPATHY
        )
        
        assert trends is not None
        assert trends['dimension'] == QualityDimension.EMPATHY.value
        assert 'average_score' in trends
    
    def test_get_improvement_recommendations_no_data(self, quality_service):
        """Test getting recommendations with no data"""
        recommendations = quality_service.get_improvement_recommendations(
            session_id="nonexistent_session"
        )
        
        assert recommendations is not None
        assert len(recommendations) > 0
        assert "No quality assessments" in recommendations[0]
    
    def test_get_improvement_recommendations_with_data(self, quality_service):
        """Test getting recommendations with assessment data"""
        # Create assessments with issues
        quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_1",
            response_text="Ok",  # Too brief
            intervention_type=InterventionType.REFLECTION,
            client_emotional_state=EmotionalState.ANXIOUS,
            conversation_phase=ConversationPhase.EXPLORATION
        )
        
        recommendations = quality_service.get_improvement_recommendations(
            session_id="session_123"
        )
        
        assert recommendations is not None
        assert len(recommendations) > 0
        assert isinstance(recommendations[0], str)
    
    # ========== Edge Cases ==========
    
    def test_assess_response_with_context(self, quality_service, sample_conversation_turns):
        """Test assessing response with conversation context"""
        assessment = quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_4",
            response_text="Let's talk more about the work stress you mentioned.",
            intervention_type=InterventionType.CLARIFICATION,
            client_emotional_state=EmotionalState.ANXIOUS,
            conversation_phase=ConversationPhase.EXPLORATION,
            conversation_context=sample_conversation_turns
        )
        
        assert assessment is not None
        # Should have good coherence since it references previous content
        coherence_score = next(
            (s for s in assessment.dimension_scores 
             if s.dimension == QualityDimension.COHERENCE),
            None
        )
        assert coherence_score is not None
        assert coherence_score.score > 0.5
    
    def test_score_to_level_conversion(self, quality_service):
        """Test score to level conversion"""
        # Test through assessment
        assessment = quality_service.assess_response_quality(
            session_id="session_123",
            turn_id="turn_1",
            response_text="I understand how you feel. Let's explore this together with empathy and care.",
            intervention_type=InterventionType.REFLECTION,
            client_emotional_state=EmotionalState.NEUTRAL,
            conversation_phase=ConversationPhase.EXPLORATION
        )
        
        # Verify level matches score
        if assessment.overall_score >= 0.9:
            assert assessment.overall_level == QualityLevel.EXCELLENT
        elif assessment.overall_score >= 0.75:
            assert assessment.overall_level == QualityLevel.GOOD
        elif assessment.overall_score >= 0.6:
            assert assessment.overall_level == QualityLevel.ACCEPTABLE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
