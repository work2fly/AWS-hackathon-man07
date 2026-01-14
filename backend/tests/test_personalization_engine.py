"""
Unit tests for Personalization Engine
🏆 Breaking Barriers UK 2026 compliant

Tests user preference learning, conversation style personalization,
therapeutic approach customization, and relationship building.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.services.personalization_engine import (
    PersonalizationEngine,
    ConversationStyle,
    TherapeuticApproach,
    CommunicationPreference,
    UserPreferences,
    AdaptationRecommendation
)


class TestPersonalizationEngine:
    """Test suite for personalization engine"""
    
    @pytest.fixture
    def mock_context_service(self):
        """Create mock context service"""
        service = Mock()
        service.get_conversation_history.return_value = []
        service.get_therapeutic_progress.return_value = {
            'milestones': [],
            'ongoing_topics': []
        }
        return service
    
    @pytest.fixture
    def mock_memory_service(self):
        """Create mock memory service"""
        service = Mock()
        service.get_memory.return_value = Mock(
            therapeutic_profile=Mock(
                communication_style="supportive",
                language_preference="en",
                preferred_approaches=[]
            )
        )
        service.update_memory.return_value = Mock()
        return service
    
    @pytest.fixture
    def personalization_engine(self, mock_context_service, mock_memory_service):
        """Create personalization engine with mocked dependencies"""
        return PersonalizationEngine(
            context_service=mock_context_service,
            memory_service=mock_memory_service
        )
    
    # ========== Preference Learning Tests ==========
    
    def test_learn_preferences_from_session(self, personalization_engine):
        """Test learning preferences from session data"""
        session_data = {
            'response_lengths': [25, 30, 28],  # Concise
            'interaction_pace': 'normal',
            'topics_discussed': ['anxiety', 'work_stress'],
            'topic_engagement': {'anxiety': 0.8, 'work_stress': 0.6},
            'therapeutic_interventions': ['cognitive_restructuring', 'thought_records'],
            'intervention_effectiveness': {'cognitive_restructuring': 0.9, 'thought_records': 0.8}
        }
        
        preferences = personalization_engine.learn_preferences_from_session(
            client_id="client_123",
            session_id="session_456",
            session_data=session_data
        )
        
        assert preferences is not None
        assert preferences.client_id == "client_123"
        assert preferences.communication_preference == CommunicationPreference.CONCISE
        assert preferences.pacing_preference == "moderate"
        assert 'anxiety' in preferences.topics_of_interest
    
    def test_initialize_default_preferences(self, personalization_engine):
        """Test initializing default preferences"""
        preferences = personalization_engine._initialize_default_preferences("client_123")
        
        assert preferences.client_id == "client_123"
        assert preferences.conversation_style == ConversationStyle.SUPPORTIVE
        assert preferences.therapeutic_approach == TherapeuticApproach.ECLECTIC
        assert preferences.communication_preference == CommunicationPreference.BALANCED
        assert preferences.language_preference == "en"
    
    def test_learn_communication_preference_concise(self, personalization_engine):
        """Test learning concise communication preference"""
        preferences = UserPreferences(
            client_id="client_123",
            conversation_style=ConversationStyle.SUPPORTIVE,
            therapeutic_approach=TherapeuticApproach.ECLECTIC,
            communication_preference=CommunicationPreference.BALANCED,
            language_preference="en",
            pacing_preference="moderate",
            formality_level="professional",
            preferred_session_length=45
        )
        
        updated = personalization_engine._learn_communication_preference(
            preferences,
            [20, 25, 22]  # Short responses
        )
        
        assert updated.communication_preference == CommunicationPreference.CONCISE
    
    def test_learn_communication_preference_detailed(self, personalization_engine):
        """Test learning detailed communication preference"""
        preferences = UserPreferences(
            client_id="client_123",
            conversation_style=ConversationStyle.SUPPORTIVE,
            therapeutic_approach=TherapeuticApproach.ECLECTIC,
            communication_preference=CommunicationPreference.BALANCED,
            language_preference="en",
            pacing_preference="moderate",
            formality_level="professional",
            preferred_session_length=45
        )
        
        updated = personalization_engine._learn_communication_preference(
            preferences,
            [90, 100, 95]  # Long responses
        )
        
        assert updated.communication_preference == CommunicationPreference.DETAILED
    
    # ========== Conversation Style Personalization Tests ==========
    
    def test_personalize_conversation_style_no_preferences(self, personalization_engine):
        """Test personalization with no preferences returns original"""
        response = "I understand how you feel."
        personalized = personalization_engine.personalize_conversation_style(
            client_id="unknown_client",
            base_response=response
        )
        
        assert personalized == response
    
    def test_personalize_conversation_style_concise(self, personalization_engine):
        """Test making response concise"""
        # Set up preferences
        preferences = UserPreferences(
            client_id="client_123",
            conversation_style=ConversationStyle.SUPPORTIVE,
            therapeutic_approach=TherapeuticApproach.ECLECTIC,
            communication_preference=CommunicationPreference.CONCISE,
            language_preference="en",
            pacing_preference="moderate",
            formality_level="professional",
            preferred_session_length=45
        )
        personalization_engine._user_preferences["client_123"] = preferences
        
        response = "I understand how you feel. That must be difficult. Let me help you explore this further. We can work through this together."
        personalized = personalization_engine.personalize_conversation_style(
            client_id="client_123",
            base_response=response
        )
        
        # Should be shorter
        assert len(personalized) < len(response)
    
    def test_make_casual(self, personalization_engine):
        """Test making response more casual"""
        formal = "I understand that you are experiencing difficulties. Perhaps we should explore this further."
        casual = personalization_engine._make_casual(formal)
        
        assert "I get" in casual
        assert "Maybe" in casual
    
    def test_make_formal(self, personalization_engine):
        """Test making response more formal"""
        casual = "I get what you're saying. Maybe we should talk about it more."
        formal = personalization_engine._make_formal(casual)
        
        assert "I understand" in formal
        assert "Perhaps" in formal
    
    # ========== Therapeutic Approach Customization Tests ==========
    
    def test_customize_therapeutic_approach_no_preferences(self, personalization_engine):
        """Test customization with no preferences returns eclectic"""
        customization = personalization_engine.customize_therapeutic_approach(
            client_id="unknown_client",
            intervention_type="reflection",
            context={}
        )
        
        assert customization['approach'] == TherapeuticApproach.ECLECTIC.value
    
    def test_customize_cbt_approach(self, personalization_engine):
        """Test CBT approach customization"""
        # Set up CBT preference
        preferences = UserPreferences(
            client_id="client_123",
            conversation_style=ConversationStyle.SUPPORTIVE,
            therapeutic_approach=TherapeuticApproach.CBT,
            communication_preference=CommunicationPreference.BALANCED,
            language_preference="en",
            pacing_preference="moderate",
            formality_level="professional",
            preferred_session_length=45
        )
        personalization_engine._user_preferences["client_123"] = preferences
        
        customization = personalization_engine.customize_therapeutic_approach(
            client_id="client_123",
            intervention_type="reflection",
            context={}
        )
        
        assert customization['approach'] == TherapeuticApproach.CBT.value
        assert 'cognitive' in customization['guidance'].lower() or 'thought' in customization['guidance'].lower()
        assert len(customization['techniques']) > 0
    
    def test_customize_person_centered_approach(self, personalization_engine):
        """Test person-centered approach customization"""
        preferences = UserPreferences(
            client_id="client_123",
            conversation_style=ConversationStyle.SUPPORTIVE,
            therapeutic_approach=TherapeuticApproach.PERSON_CENTERED,
            communication_preference=CommunicationPreference.BALANCED,
            language_preference="en",
            pacing_preference="moderate",
            formality_level="professional",
            preferred_session_length=45
        )
        personalization_engine._user_preferences["client_123"] = preferences
        
        customization = personalization_engine.customize_therapeutic_approach(
            client_id="client_123",
            intervention_type="validation",
            context={}
        )
        
        assert customization['approach'] == TherapeuticApproach.PERSON_CENTERED.value
        assert 'empathy' in customization['guidance'].lower()
    
    # ========== Relationship Building Tests ==========
    
    def test_build_relationship_continuity_early_stage(self, personalization_engine):
        """Test relationship building in early stage"""
        guidance = personalization_engine.build_relationship_continuity(
            client_id="client_123",
            session_count=2
        )
        
        assert guidance['relationship_stage'] == "building_rapport"
        assert guidance['session_count'] == 2
        assert len(guidance['continuity_elements']) > 0
        assert len(guidance['relationship_building_focus']) > 0
    
    def test_build_relationship_continuity_established(self, personalization_engine):
        """Test relationship building in established stage"""
        guidance = personalization_engine.build_relationship_continuity(
            client_id="client_123",
            session_count=15
        )
        
        assert guidance['relationship_stage'] == "deepening_work"
        assert guidance['session_count'] == 15
    
    def test_build_relationship_continuity_maintenance(self, personalization_engine):
        """Test relationship building in maintenance stage"""
        guidance = personalization_engine.build_relationship_continuity(
            client_id="client_123",
            session_count=25
        )
        
        assert guidance['relationship_stage'] == "maintenance"
        assert guidance['session_count'] == 25
    
    # ========== Adaptation Recommendations Tests ==========
    
    def test_get_adaptation_recommendations_no_preferences(self, personalization_engine):
        """Test getting recommendations with no preferences"""
        recommendations = personalization_engine.get_adaptation_recommendations(
            client_id="unknown_client",
            current_session_data={}
        )
        
        assert recommendations == []
    
    def test_get_adaptation_recommendations_with_mismatch(self, personalization_engine):
        """Test getting recommendations when current approach doesn't match preferences"""
        # Set up preferences
        preferences = UserPreferences(
            client_id="client_123",
            conversation_style=ConversationStyle.DIRECT,
            therapeutic_approach=TherapeuticApproach.CBT,
            communication_preference=CommunicationPreference.CONCISE,
            language_preference="en",
            pacing_preference="fast",
            formality_level="professional",
            preferred_session_length=45
        )
        personalization_engine._user_preferences["client_123"] = preferences
        
        current_session_data = {
            'therapeutic_approach': 'person_centered',
            'communication_style': 'gentle',
            'pacing': 'slow'
        }
        
        recommendations = personalization_engine.get_adaptation_recommendations(
            client_id="client_123",
            current_session_data=current_session_data
        )
        
        assert len(recommendations) > 0
        # Should be sorted by priority
        assert all(
            recommendations[i].priority >= recommendations[i+1].priority
            for i in range(len(recommendations)-1)
        )
    
    def test_get_user_preferences(self, personalization_engine):
        """Test getting user preferences"""
        # Set up preferences
        preferences = UserPreferences(
            client_id="client_123",
            conversation_style=ConversationStyle.SUPPORTIVE,
            therapeutic_approach=TherapeuticApproach.ECLECTIC,
            communication_preference=CommunicationPreference.BALANCED,
            language_preference="en",
            pacing_preference="moderate",
            formality_level="professional",
            preferred_session_length=45
        )
        personalization_engine._user_preferences["client_123"] = preferences
        
        retrieved = personalization_engine.get_user_preferences("client_123")
        
        assert retrieved is not None
        assert retrieved.client_id == "client_123"
        assert retrieved.conversation_style == ConversationStyle.SUPPORTIVE
    
    def test_get_user_preferences_not_found(self, personalization_engine):
        """Test getting preferences for unknown user"""
        retrieved = personalization_engine.get_user_preferences("unknown_client")
        
        assert retrieved is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
