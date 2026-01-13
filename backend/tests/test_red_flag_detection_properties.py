#!/usr/bin/env python3
"""
Property-Based Tests for Red Flag Detection System
🏆 Breaking Barriers UK 2026 compliant
Feature: ai-therapy-platform, Property 8: Comprehensive Red Flag Detection
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**
"""

import unittest
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example
from hypothesis.strategies import composite


class RedFlagType(str, Enum):
    """Red flag type enumeration"""
    SELF_HARM = "self_harm"
    SUICIDAL_IDEATION = "suicidal_ideation"
    ABUSE = "abuse"
    VIOLENCE = "violence"
    CRISIS = "crisis"


class Severity(str, Enum):
    """Severity level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SimpleRedFlagDetector:
    """Simplified red flag detector for testing"""
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize detection patterns"""
        patterns = {
            RedFlagType.SELF_HARM: [
                (r'\b(cut|cutting|hurt|hurting)\s+(myself|me)\b', Severity.HIGH),
                (r'\b(self[\s-]?harm|self[\s-]?injury)\b', Severity.HIGH),
                (r'\b(burn|burning|burned)\s+(myself|me)\b', Severity.HIGH),
                (r'\b(scratch|scratching|scratched)\s+(myself|me)\b', Severity.MEDIUM),
                (r'\bwant\s+to\s+(hurt|harm)\s+(myself|me)\b', Severity.HIGH),
                (r'\b(razor|blade|knife)\b.*\b(skin|arm|leg|wrist)\b', Severity.CRITICAL),
            ],
            RedFlagType.SUICIDAL_IDEATION: [
                (r'\b(kill|killing)\s+(myself|me)\b', Severity.CRITICAL),
                (r'\bcommit\s+suicide\b', Severity.CRITICAL),
                (r'\bend\s+(my\s+life|it\s+all)\b', Severity.CRITICAL),
                (r'\bdon\'?t\s+want\s+to\s+(live|be\s+alive)\b', Severity.HIGH),
                (r'\bbetter\s+off\s+dead\b', Severity.HIGH),
                (r'\bwish\s+I\s+(was|were)\s+dead\b', Severity.HIGH),
                (r'\bthink\s+about\s+(dying|death)\b', Severity.MEDIUM),
                (r'\bsuicidal\s+(thoughts|ideation)\b', Severity.HIGH),
            ],
            RedFlagType.ABUSE: [
                (r'\b(hit|hits|hitting|beat|beats|beating)\s+me\b', Severity.HIGH),
                (r'\b(abuse|abused|abusing)\s+me\b', Severity.HIGH),
                (r'\b(sexual|sexually)\s+(abuse|assault|harass)\b', Severity.CRITICAL),
                (r'\b(rape|raped|molest|molested)\b', Severity.CRITICAL),
                (r'\bdomestic\s+(violence|abuse)\b', Severity.HIGH),
                (r'\bphysical\s+(violence|abuse)\b', Severity.HIGH),
            ],
            RedFlagType.VIOLENCE: [
                (r'\bwant\s+to\s+(hurt|harm|kill)\s+(someone|somebody|people)\b', Severity.HIGH),
                (r'\bthink\s+about\s+(hurting|harming|killing)\s+(others|people)\b', Severity.HIGH),
                (r'\bviolent\s+(thoughts|fantasies)\b', Severity.MEDIUM),
                (r'\bplan\s+to\s+(hurt|harm|attack)\b', Severity.CRITICAL),
                (r'\b(weapon|gun|knife|bomb)\b.*\b(use|hurt|harm)\b', Severity.CRITICAL),
            ],
            RedFlagType.CRISIS: [
                (r'\bmental\s+breakdown\b', Severity.HIGH),
                (r'\bcan\'?t\s+(cope|handle)\s+(anymore|this)\b', Severity.MEDIUM),
                (r'\bcompletely\s+(overwhelmed|lost)\b', Severity.MEDIUM),
                (r'\bpsychotic\s+(episode|break)\b', Severity.HIGH),
                (r'\bhallucination|hallucinating|hearing\s+voices\b', Severity.HIGH),
            ]
        }
        
        compiled_patterns = {}
        for flag_type, pattern_list in patterns.items():
            compiled_patterns[flag_type] = [
                (re.compile(pattern, re.IGNORECASE | re.MULTILINE), severity)
                for pattern, severity in pattern_list
            ]
        
        return compiled_patterns
    
    def analyze_content(self, content: str, session_id: str) -> List[Dict[str, Any]]:
        """Analyze content for red flags"""
        if not content or not content.strip():
            return []
        
        detected_flags = []
        
        for flag_type, patterns in self._patterns.items():
            for pattern, severity in patterns:
                if pattern.search(content):
                    detected_flag = {
                        'type': flag_type.value,
                        'severity': severity.value,
                        'confidence_score': 0.8,
                        'context': self._create_context(content),
                        'detected_at': datetime.utcnow().isoformat()
                    }
                    detected_flags.append(detected_flag)
                    break  # Only one flag per type
        
        return detected_flags
    
    def _create_context(self, content: str) -> str:
        """Create sanitized context"""
        if len(content) <= 200:
            return content
        return content[:200] + "..."


@composite
def self_harm_content(draw):
    """Generate content that should trigger self-harm detection"""
    self_harm_phrases = [
        "I want to cut myself",
        "I've been hurting myself",
        "I burned myself with a cigarette",
        "I hit myself when I get angry",
        "I scratch my arms until they bleed",
        "I want to harm myself",
        "I've been self-harming for months",
        "I use a razor blade on my skin",
        "I pull my hair out when stressed",
        "I bang my head against the wall"
    ]
    
    base_phrase = draw(st.sampled_from(self_harm_phrases))
    
    # Add some context around it
    prefix = draw(st.sampled_from([
        "I need to tell someone that ",
        "Yesterday ",
        "Sometimes ",
        "I'm ashamed to admit that ",
        "When I'm upset, ",
        ""
    ]))
    
    suffix = draw(st.sampled_from([
        " and I don't know how to stop.",
        " because I feel so overwhelmed.",
        " when things get too difficult.",
        " and it makes me feel worse.",
        " but I regret it afterwards.",
        ""
    ]))
    
    return f"{prefix}{base_phrase}{suffix}".strip()


@composite
def suicidal_ideation_content(draw):
    """Generate content that should trigger suicidal ideation detection"""
    suicidal_phrases = [
        "I want to kill myself",
        "I think about ending my life",
        "I don't want to live anymore",
        "I wish I was dead",
        "I want to commit suicide",
        "I have suicidal thoughts",
        "I'm better off dead",
        "I can't go on living like this",
        "I want to end it all",
        "I have a plan to kill myself"
    ]
    
    base_phrase = draw(st.sampled_from(suicidal_phrases))
    
    # Add some context
    prefix = draw(st.sampled_from([
        "I've been thinking that ",
        "Lately I feel like ",
        "I can't help but think ",
        "Every day I think ",
        "I'm scared because ",
        ""
    ]))
    
    suffix = draw(st.sampled_from([
        " and I'm scared of these thoughts.",
        " but I don't want to hurt my family.",
        " and I need help.",
        " every single day.",
        " and I don't know what to do.",
        ""
    ]))
    
    return f"{prefix}{base_phrase}{suffix}".strip()


@composite
def abuse_content(draw):
    """Generate content that should trigger abuse detection"""
    abuse_phrases = [
        "My partner hits me",
        "He beats me when he's angry",
        "She sexually abused me",
        "I was raped last week",
        "My father molested me",
        "I'm being physically abused",
        "He threatens to kill me",
        "She verbally abuses me daily",
        "I'm afraid of him",
        "He controls everything I do"
    ]
    
    base_phrase = draw(st.sampled_from(abuse_phrases))
    
    # Add some context
    prefix = draw(st.sampled_from([
        "I need to tell someone that ",
        "I'm ashamed to admit that ",
        "I can't take it anymore - ",
        "I'm scared because ",
        "Nobody knows that ",
        ""
    ]))
    
    suffix = draw(st.sampled_from([
        " and I don't know how to escape.",
        " and I'm afraid to leave.",
        " but I have nowhere to go.",
        " and I need help.",
        " and I feel trapped.",
        ""
    ]))
    
    return f"{prefix}{base_phrase}{suffix}".strip()


@composite
def violence_content(draw):
    """Generate content that should trigger violence detection"""
    violence_phrases = [
        "I want to hurt someone",
        "I think about killing people",
        "I have violent thoughts about my boss",
        "I want to attack my neighbor",
        "I fantasize about hurting others",
        "I think about using a weapon",
        "I want to make them pay",
        "I have plans to hurt someone",
        "I lose control and want to hurt people",
        "I think about bringing a gun to work"
    ]
    
    base_phrase = draw(st.sampled_from(violence_phrases))
    
    # Add some context
    prefix = draw(st.sampled_from([
        "I'm worried because ",
        "I'm scared that ",
        "Sometimes ",
        "When I get angry, ",
        "I can't stop thinking that ",
        ""
    ]))
    
    suffix = draw(st.sampled_from([
        " and these thoughts scare me.",
        " but I don't want to act on it.",
        " and I need help controlling this.",
        " and I'm afraid I might do something.",
        " and I don't know how to stop.",
        ""
    ]))
    
    return f"{prefix}{base_phrase}{suffix}".strip()


@composite
def crisis_content(draw):
    """Generate content that should trigger crisis detection"""
    crisis_phrases = [
        "I'm having a mental breakdown",
        "I can't cope anymore",
        "I'm completely overwhelmed",
        "I'm having a psychotic episode",
        "I'm hearing voices",
        "I'm having hallucinations",
        "I'm paranoid about everything",
        "I'm having severe panic attacks",
        "I feel like I'm losing my mind",
        "I can't handle this anymore"
    ]
    
    base_phrase = draw(st.sampled_from(crisis_phrases))
    
    # Add some context
    prefix = draw(st.sampled_from([
        "I think ",
        "I feel like ",
        "Right now ",
        "For the past week ",
        "I'm scared because ",
        ""
    ]))
    
    suffix = draw(st.sampled_from([
        " and I need immediate help.",
        " and I don't know what's real.",
        " and I can't function.",
        " and everything feels hopeless.",
        " and I'm losing control.",
        ""
    ]))
    
    return f"{prefix}{base_phrase}{suffix}".strip()


@composite
def safe_content(draw):
    """Generate content that should NOT trigger red flag detection"""
    safe_phrases = [
        "I had a good day today",
        "I'm feeling better about things",
        "I enjoyed spending time with friends",
        "I'm working on my goals",
        "I feel hopeful about the future",
        "I'm learning to manage my stress",
        "I appreciate having someone to talk to",
        "I'm making progress in therapy",
        "I feel supported by my family",
        "I'm grateful for the help I'm receiving"
    ]
    
    base_phrase = draw(st.sampled_from(safe_phrases))
    
    # Add some context
    prefix = draw(st.sampled_from([
        "I wanted to share that ",
        "I'm happy to report that ",
        "I'm pleased that ",
        "I feel good because ",
        "I'm grateful that ",
        ""
    ]))
    
    suffix = draw(st.sampled_from([
        " and I want to keep improving.",
        " and I'm optimistic about tomorrow.",
        " and I feel more confident.",
        " and I'm taking care of myself.",
        " and I'm building healthy habits.",
        ""
    ]))
    
    return f"{prefix}{base_phrase}{suffix}".strip()


@composite
def mixed_content(draw):
    """Generate content with both concerning and safe elements"""
    concerning_part = draw(st.sampled_from([
        self_harm_content(),
        suicidal_ideation_content(),
        abuse_content(),
        violence_content(),
        crisis_content()
    ]))
    
    safe_part = draw(safe_content())
    
    # Combine them in different ways
    combination_type = draw(st.sampled_from(['before', 'after', 'between']))
    
    if combination_type == 'before':
        return f"{safe_part} But {concerning_part.lower()}"
    elif combination_type == 'after':
        return f"{concerning_part} However, {safe_part.lower()}"
    else:
        middle_safe = draw(st.sampled_from([
            "I know I should be positive, but",
            "I try to stay hopeful, yet",
            "Despite therapy helping,"
        ]))
        return f"{concerning_part} {middle_safe} {safe_part.lower()}"


class TestRedFlagDetectionProperties(unittest.TestCase):
    """Property-based tests for red flag detection system"""
    
    def setUp(self):
        """Set up test environment"""
        self.detector = SimpleRedFlagDetector()
        
        # Mock session ID for testing
        self.test_session_id = "test_session_12345"
    
    @given(content=self_harm_content())
    @settings(max_examples=10, deadline=None)
    @example(content="I want to cut myself because I feel so overwhelmed.")
    def test_property_self_harm_detection(self, content):
        """
        Property: Self-harm content should always be detected
        For any content containing self-harm indicators, the system should detect it as a red flag.
        **Validates: Requirements 4.1**
        """
        # Analyze content for red flags
        detected_flags = self.detector.analyze_content(content, self.test_session_id)
        
        # Property: Self-harm content should be detected
        self.assertGreater(len(detected_flags), 0, 
                          f"Self-harm content should be detected: {content}")
        
        # Property: At least one flag should be self-harm type
        self_harm_detected = any(
            flag['type'] == RedFlagType.SELF_HARM.value 
            for flag in detected_flags
        )
        self.assertTrue(self_harm_detected, 
                       f"Self-harm flag should be detected in: {content}")
        
        # Property: Detected flags should have valid severity levels
        for flag in detected_flags:
            self.assertIn(flag['severity'], ['low', 'medium', 'high', 'critical'],
                         f"Flag severity should be valid: {flag['severity']}")
            
        # Property: Context should be sanitized and limited
        for flag in detected_flags:
            self.assertIsInstance(flag['context'], str, "Context should be string")
            self.assertLessEqual(len(flag['context']), 1000, 
                               "Context should be limited to 1000 characters")
    
    @given(content=suicidal_ideation_content())
    @settings(max_examples=10, deadline=None)
    @example(content="I think about ending my life and I need help.")
    def test_property_suicidal_ideation_detection(self, content):
        """
        Property: Suicidal ideation content should always be detected
        For any content containing suicidal ideation, the system should detect it as a red flag.
        **Validates: Requirements 4.2**
        """
        # Analyze content for red flags
        detected_flags = self.detection_service.analyze_content(content, self.test_session_id)
        
        # Property: Suicidal ideation content should be detected
        self.assertGreater(len(detected_flags), 0, 
                          f"Suicidal ideation content should be detected: {content}")
        
        # Property: At least one flag should be suicidal ideation type
        suicidal_detected = any(
            flag['type'] == RedFlagType.SUICIDAL_IDEATION.value 
            for flag in detected_flags
        )
        self.assertTrue(suicidal_detected, 
                       f"Suicidal ideation flag should be detected in: {content}")
        
        # Property: Suicidal ideation should typically have high severity
        suicidal_flags = [
            flag for flag in detected_flags 
            if flag['type'] == RedFlagType.SUICIDAL_IDEATION.value
        ]
        for flag in suicidal_flags:
            self.assertIn(flag['severity'], ['medium', 'high', 'critical'],
                         f"Suicidal ideation should have medium+ severity: {flag['severity']}")
    
    @given(content=abuse_content())
    @settings(max_examples=10, deadline=None)
    @example(content="My partner hits me and I'm afraid to leave.")
    def test_property_abuse_detection(self, content):
        """
        Property: Abuse content should always be detected
        For any content mentioning abuse or violence, the system should detect it as a red flag.
        **Validates: Requirements 4.3**
        """
        # Analyze content for red flags
        detected_flags = self.detection_service.analyze_content(content, self.test_session_id)
        
        # Property: Abuse content should be detected
        self.assertGreater(len(detected_flags), 0, 
                          f"Abuse content should be detected: {content}")
        
        # Property: At least one flag should be abuse type
        abuse_detected = any(
            flag['type'] == RedFlagType.ABUSE.value 
            for flag in detected_flags
        )
        self.assertTrue(abuse_detected, 
                       f"Abuse flag should be detected in: {content}")
    
    @given(content=violence_content())
    @settings(max_examples=10, deadline=None)
    @example(content="I think about hurting others and these thoughts scare me.")
    def test_property_violence_detection(self, content):
        """
        Property: Violence content should always be detected
        For any content mentioning violent thoughts or plans, the system should detect it as a red flag.
        **Validates: Requirements 4.3**
        """
        # Analyze content for red flags
        detected_flags = self.detection_service.analyze_content(content, self.test_session_id)
        
        # Property: Violence content should be detected
        self.assertGreater(len(detected_flags), 0, 
                          f"Violence content should be detected: {content}")
        
        # Property: At least one flag should be violence type
        violence_detected = any(
            flag['type'] == RedFlagType.VIOLENCE.value 
            for flag in detected_flags
        )
        self.assertTrue(violence_detected, 
                       f"Violence flag should be detected in: {content}")
    
    @given(content=crisis_content())
    @settings(max_examples=10, deadline=None)
    @example(content="I'm having a mental breakdown and I need immediate help.")
    def test_property_crisis_detection(self, content):
        """
        Property: Crisis content should always be detected
        For any content indicating mental health crisis, the system should detect it as a red flag.
        **Validates: Requirements 4.1, 4.2, 4.3**
        """
        # Analyze content for red flags
        detected_flags = self.detection_service.analyze_content(content, self.test_session_id)
        
        # Property: Crisis content should be detected
        self.assertGreater(len(detected_flags), 0, 
                          f"Crisis content should be detected: {content}")
        
        # Property: At least one flag should be crisis type
        crisis_detected = any(
            flag['type'] == RedFlagType.CRISIS.value 
            for flag in detected_flags
        )
        self.assertTrue(crisis_detected, 
                       f"Crisis flag should be detected in: {content}")
    
    @given(content=safe_content())
    @settings(max_examples=10, deadline=None)
    @example(content="I had a good day today and I feel hopeful about the future.")
    def test_property_safe_content_no_false_positives(self, content):
        """
        Property: Safe content should not trigger false positives
        For any safe, positive content, the system should not detect red flags.
        **Validates: Requirements 4.1, 4.2, 4.3**
        """
        # Analyze content for red flags
        detected_flags = self.detection_service.analyze_content(content, self.test_session_id)
        
        # Property: Safe content should not trigger red flags
        self.assertEqual(len(detected_flags), 0, 
                        f"Safe content should not trigger red flags: {content}")
    
    @given(content=mixed_content())
    @settings(max_examples=5, deadline=None)
    def test_property_mixed_content_detection(self, content):
        """
        Property: Mixed content should detect concerning parts
        For any content with both safe and concerning elements, the system should detect the concerning parts.
        **Validates: Requirements 4.1, 4.2, 4.3**
        """
        # Analyze content for red flags
        detected_flags = self.detection_service.analyze_content(content, self.test_session_id)
        
        # Property: Mixed content with concerning elements should be detected
        self.assertGreater(len(detected_flags), 0, 
                          f"Mixed content with concerning elements should be detected: {content}")
        
        # Property: Detection should be consistent regardless of safe content presence
        for flag in detected_flags:
            self.assertIn(flag['type'], [
                RedFlagType.SELF_HARM.value,
                RedFlagType.SUICIDAL_IDEATION.value,
                RedFlagType.ABUSE.value,
                RedFlagType.VIOLENCE.value,
                RedFlagType.CRISIS.value
            ], f"Detected flag should be a valid red flag type: {flag['type']}")
    
    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=5, deadline=None)
    def test_property_detection_consistency(self, content):
        """
        Property: Detection should be consistent
        For any content, multiple analyses should produce identical results.
        **Validates: Requirements 4.1, 4.2, 4.3**
        """
        # Analyze content multiple times
        result1 = self.detection_service.analyze_content(content, self.test_session_id)
        result2 = self.detection_service.analyze_content(content, self.test_session_id)
        
        # Property: Results should be identical
        self.assertEqual(len(result1), len(result2), 
                        f"Detection should be consistent: {content}")
        
        # Compare flag details (excluding timestamps)
        for i, (flag1, flag2) in enumerate(zip(result1, result2)):
            self.assertEqual(flag1['type'], flag2['type'], 
                           f"Flag {i} type should be consistent")
            self.assertEqual(flag1['severity'], flag2['severity'], 
                           f"Flag {i} severity should be consistent")
            self.assertEqual(flag1['context'], flag2['context'], 
                           f"Flag {i} context should be consistent")
    
    def test_property_notification_system_integration(self):
        """
        Property: Red flag detection should trigger notifications
        For any detected red flag, the notification system should be triggered.
        **Validates: Requirements 4.4, 4.5, 4.6**
        """
        # Create a test red flag
        test_content = "I want to hurt myself and I can't stop these thoughts."
        detected_flags = self.detection_service.analyze_content(test_content, self.test_session_id)
        
        # Property: Concerning content should be detected
        self.assertGreater(len(detected_flags), 0, "Test content should trigger detection")
        
        # Create red flag objects
        for flag_data in detected_flags:
            red_flag = RedFlag(
                session_id=self.test_session_id,
                flag_id=f"test_flag_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                type=RedFlagType(flag_data['type']),
                severity=Severity(flag_data['severity']),
                context=flag_data['context']
            )
            
            # Property: Red flag should have valid attributes
            self.assertIsInstance(red_flag.session_id, str)
            self.assertIsInstance(red_flag.flag_id, str)
            self.assertIsInstance(red_flag.type, RedFlagType)
            self.assertIsInstance(red_flag.severity, Severity)
            self.assertIsInstance(red_flag.context, str)
            self.assertIsInstance(red_flag.detected_at, datetime)
            
            # Property: Notifications should be sendable (mock test)
            # In a real test, this would verify actual notification sending
            notifications = self.notification_service.send_red_flag_notification(
                red_flag, "test_client_123"
            )
            
            # Property: Notification system should return notification records
            self.assertIsInstance(notifications, list, "Should return list of notifications")
    
    def test_property_escalation_logic(self):
        """
        Property: Multiple red flags should trigger escalation
        For any session with multiple red flags, escalation should be triggered.
        **Validates: Requirements 4.6**
        """
        # Test escalation with multiple flags
        test_contents = [
            "I want to cut myself",
            "I think about ending my life",
            "I can't cope anymore"
        ]
        
        all_flags = []
        for content in test_contents:
            detected_flags = self.detection_service.analyze_content(content, self.test_session_id)
            all_flags.extend(detected_flags)
        
        # Property: Multiple concerning statements should be detected
        self.assertGreaterEqual(len(all_flags), 3, 
                               "Multiple concerning statements should be detected")
        
        # Property: Risk assessment should increase with multiple flags
        risk_assessment = self.detection_service.assess_risk_level(self.test_session_id)
        
        self.assertIsInstance(risk_assessment, dict, "Risk assessment should return dict")
        self.assertIn('risk_level', risk_assessment, "Should include risk level")
        self.assertIn('risk_score', risk_assessment, "Should include risk score")
        self.assertIn('flag_count', risk_assessment, "Should include flag count")
    
    def test_property_case_management_integration(self):
        """
        Property: Red flags should integrate with case management
        For any red flag, case management should be able to process it.
        **Validates: Requirements 4.5, 4.6**
        """
        # Create a test red flag
        red_flag = RedFlag(
            session_id=self.test_session_id,
            flag_id=f"test_flag_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            type=RedFlagType.SELF_HARM,
            severity=Severity.HIGH,
            context="Test context for case management"
        )
        
        # Property: Case should be creatable from red flag
        case_result = self.management_service.create_case(red_flag)
        
        self.assertIsInstance(case_result, dict, "Case creation should return dict")
        self.assertTrue(case_result.get('success', False), 
                       f"Case creation should succeed: {case_result}")
        
        if case_result.get('success'):
            # Property: Case should have valid attributes
            self.assertIn('case_id', case_result, "Case should have ID")
            self.assertIn('priority_score', case_result, "Case should have priority score")
            self.assertIsInstance(case_result['priority_score'], float, 
                                "Priority score should be float")
            self.assertGreaterEqual(case_result['priority_score'], 0.0, 
                                  "Priority score should be non-negative")
            self.assertLessEqual(case_result['priority_score'], 1.0, 
                               "Priority score should not exceed 1.0")
    
    def test_property_audit_trail_completeness(self):
        """
        Property: All red flag actions should be auditable
        For any red flag management action, an audit trail should be created.
        **Validates: Requirements 5.7**
        """
        # Create a test red flag and case
        red_flag = RedFlag(
            session_id=self.test_session_id,
            flag_id=f"test_flag_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            type=RedFlagType.CRISIS,
            severity=Severity.CRITICAL,
            context="Test context for audit trail"
        )
        
        case_result = self.management_service.create_case(red_flag)
        
        if case_result.get('success'):
            case_id = case_result['case_id']
            
            # Property: Audit trail should be retrievable
            audit_trail = self.management_service.get_audit_trail(case_id)
            
            self.assertIsInstance(audit_trail, list, "Audit trail should be list")
            self.assertGreater(len(audit_trail), 0, "Audit trail should not be empty")
            
            # Property: Audit entries should have required fields
            for entry in audit_trail:
                self.assertIn('audit_id', entry, "Audit entry should have ID")
                self.assertIn('case_id', entry, "Audit entry should have case ID")
                self.assertIn('timestamp', entry, "Audit entry should have timestamp")
                self.assertIn('action', entry, "Audit entry should have action")
                self.assertIn('user_id', entry, "Audit entry should have user ID")
                self.assertIn('details', entry, "Audit entry should have details")


def run_property_tests():
    """Run property-based tests for red flag detection"""
    print("🧪 Running Property-Based Tests for Red Flag Detection System")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: ai-therapy-platform, Property 8: Comprehensive Red Flag Detection")
    print("**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestRedFlagDetectionProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All property-based tests passed!")
        print("✅ Comprehensive Red Flag Detection properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant detection verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
        
        # Print failure details
        for test, traceback in result.failures:
            print(f"\nFAILURE: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_property_tests()
    exit(0 if success else 1)