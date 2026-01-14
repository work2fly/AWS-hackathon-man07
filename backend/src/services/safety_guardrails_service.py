"""
Safety Guardrails Service for AI Therapy Platform
Implements content filtering, therapeutic boundary enforcement, and response quality assurance
🏆 Breaking Barriers UK 2026 compliant
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from ..utils.logger import get_logger

logger = get_logger(__name__)


class GuardrailViolationType(str, Enum):
    """Types of guardrail violations"""
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    THERAPEUTIC_BOUNDARY = "therapeutic_boundary"
    HARMFUL_ADVICE = "harmful_advice"
    MEDICAL_DIAGNOSIS = "medical_diagnosis"
    PERSONAL_DISCLOSURE = "personal_disclosure"
    UNPROFESSIONAL_LANGUAGE = "unprofessional_language"
    TRIGGERING_CONTENT = "triggering_content"


class ResponseQuality(str, Enum):
    """Response quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


class SafetyGuardrailsService:
    """Service for enforcing safety guardrails and content filtering"""
    
    def __init__(self):
        self._inappropriate_patterns = self._initialize_inappropriate_patterns()
        self._boundary_patterns = self._initialize_boundary_patterns()
        self._harmful_advice_patterns = self._initialize_harmful_advice_patterns()
        self._medical_diagnosis_patterns = self._initialize_medical_diagnosis_patterns()
        self._triggering_content_patterns = self._initialize_triggering_content_patterns()
        
        # Quality assurance thresholds
        self._quality_thresholds = {
            'min_validation_phrases': 1,
            'max_directive_phrases': 2,
            'min_empathy_indicators': 1,
            'max_clinical_terms': 3
        }
    
    def _initialize_inappropriate_patterns(self) -> List[Tuple[str, str]]:
        """Initialize patterns for inappropriate content"""
        return [
            # Sexual content
            (r'\b(sexual|sex|intimate)\s+(relationship|encounter|activity)\b', 'sexual_content'),
            (r'\b(flirt|dating|romantic)\s+(interest|relationship)\b', 'romantic_content'),
            
            # Discriminatory language
            (r'\b(racist|sexist|homophobic|transphobic)\b', 'discriminatory'),
            (r'\b(hate|hatred)\s+(towards|against)\s+(group|people)\b', 'hate_speech'),
            
            # Profanity (mild detection - not comprehensive)
            (r'\b(damn|hell|crap)\b', 'mild_profanity'),
            
            # Inappropriate personal questions
            (r'\bwhere\s+do\s+you\s+live\b', 'personal_location'),
            (r'\bwhat\'?s\s+your\s+(phone|number|address)\b', 'personal_contact'),
        ]
    
    def _initialize_boundary_patterns(self) -> List[Tuple[str, str]]:
        """Initialize patterns for therapeutic boundary violations"""
        return [
            # Friendship/relationship offers
            (r'\b(we|let\'?s)\s+(be|become)\s+friends\b', 'friendship_offer'),
            (r'\bi\s+(love|care\s+about)\s+you\b', 'inappropriate_attachment'),
            (r'\byou\'?re\s+(special|unique)\s+to\s+me\b', 'personal_favoritism'),
            
            # Meeting outside therapy
            (r'\b(meet|see)\s+you\s+(outside|in\s+person)\b', 'outside_meeting'),
            (r'\blet\'?s\s+(hang\s+out|get\s+together)\b', 'social_invitation'),
            
            # Personal disclosure from AI
            (r'\bi\s+(also|too)\s+(have|had|experienced)\b', 'ai_personal_disclosure'),
            (r'\bwhen\s+i\s+was\b', 'ai_personal_history'),
            (r'\bmy\s+(family|friend|partner)\b', 'ai_personal_relationships'),
            
            # Dual relationships
            (r'\bi\s+can\s+help\s+you\s+with\s+(work|business|legal)\b', 'dual_relationship'),
        ]
    
    def _initialize_harmful_advice_patterns(self) -> List[Tuple[str, str]]:
        """Initialize patterns for harmful advice"""
        return [
            # Encouraging substance use - more flexible patterns
            (r'\b(drink|drinking|alcohol|drugs?)\s+(?:\w+\s+)?(will|can|might|could|would|should)\s+help\b', 'substance_encouragement'),
            (r'\btry\s+(drinking|smoking|drugs)\b', 'substance_suggestion'),
            
            # Minimizing concerns
            (r'\bit\'?s\s+not\s+(that|so)\s+bad\b', 'minimizing'),
            (r'\byou\'?re\s+overreacting\b', 'invalidating'),
            (r'\bjust\s+(get\s+over|forget|ignore)\s+it\b', 'dismissive'),
            
            # Dangerous coping strategies
            (r'\bisolate\s+yourself\b', 'isolation_advice'),
            (r'\bavoid\s+(all|everyone)\b', 'avoidance_advice'),
            
            # Relationship advice that could be harmful (allow optional words between)
            (r'\byou\s+should\s+(?:\w+\s+)?(leave|stay\s+with)\s+(?:your\s+)?(partner|him|her|them|relationship)\b', 'relationship_directive'),
            (r'\bbreak\s+up\s+with\b', 'relationship_directive'),
            
            # Financial/legal advice
            (r'\byou\s+should\s+(sue|file|report)\b', 'legal_advice'),
            (r'\binvest\s+in\b', 'financial_advice'),
        ]
    
    def _initialize_medical_diagnosis_patterns(self) -> List[Tuple[str, str]]:
        """Initialize patterns for medical diagnosis attempts"""
        return [
            # Diagnostic statements
            (r'\byou\s+(have|are|suffer\s+from)\s+(depression|anxiety|ptsd|bipolar|schizophrenia)\b', 'diagnosis'),
            (r'\byou\'?re\s+(definitely|clearly|obviously)\s+(depressed|anxious|bipolar)\b', 'diagnosis'),
            (r'\bthis\s+is\s+(definitely|clearly)\s+a\s+case\s+of\b', 'diagnosis'),
            
            # Medication advice
            (r'\byou\s+should\s+(take|try|stop)\s+(medication|pills|antidepressants)\b', 'medication_advice'),
            (r'\b(increase|decrease|stop)\s+your\s+(dose|medication)\b', 'medication_adjustment'),
            
            # Medical procedures
            (r'\byou\s+need\s+(surgery|hospitalization|medical\s+treatment)\b', 'medical_procedure'),
        ]
    
    def _initialize_triggering_content_patterns(self) -> List[Tuple[str, str]]:
        """Initialize patterns for potentially triggering content"""
        return [
            # Graphic descriptions
            (r'\b(graphic|explicit|detailed)\s+(description|account)\s+of\b', 'graphic_content'),
            (r'\b(blood|gore|violence)\s+(details|description)\b', 'graphic_violence'),
            
            # Triggering questions - these should be violations, not just warnings
            (r'\btell\s+me\s+(exactly|in\s+detail)\s+what\s+happened\b', 'detailed_trauma_inquiry'),
            (r'\bdescribe\s+the\s+(abuse|assault|trauma)\s+in\s+detail\b', 'detailed_trauma_inquiry'),
            (r'\bwhat\s+happened\s+in\s+graphic\s+detail\b', 'detailed_trauma_inquiry'),
        ]
    
    def validate_ai_response(self, response_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate AI response against safety guardrails
        
        Args:
            response_text: AI-generated response to validate
            context: Optional context about the conversation
            
        Returns:
            Validation results with violations and recommendations
        """
        try:
            violations = []
            warnings = []
            
            # Check for inappropriate content
            inappropriate_violations = self._check_inappropriate_content(response_text)
            violations.extend(inappropriate_violations)
            
            # Check for therapeutic boundary violations
            boundary_violations = self._check_therapeutic_boundaries(response_text)
            violations.extend(boundary_violations)
            
            # Check for harmful advice
            harmful_advice_violations = self._check_harmful_advice(response_text)
            violations.extend(harmful_advice_violations)
            
            # Check for medical diagnosis attempts
            diagnosis_violations = self._check_medical_diagnosis(response_text)
            violations.extend(diagnosis_violations)
            
            # Check for triggering content - treat as violations, not warnings
            triggering_violations = self._check_triggering_content(response_text)
            violations.extend(triggering_violations)
            
            # Assess response quality
            quality_assessment = self._assess_response_quality(response_text)
            
            # Determine if response is safe to send
            is_safe = len(violations) == 0
            needs_revision = len(violations) > 0 or quality_assessment['quality'] == ResponseQuality.UNACCEPTABLE
            
            return {
                'is_safe': is_safe,
                'needs_revision': needs_revision,
                'violations': violations,
                'warnings': warnings,
                'quality_assessment': quality_assessment,
                'validated_at': datetime.utcnow().isoformat(),
                'recommendation': self._get_recommendation(violations, warnings, quality_assessment)
            }
            
        except Exception as e:
            logger.error(f"Failed to validate AI response: {str(e)}")
            return {
                'is_safe': False,
                'needs_revision': True,
                'violations': [{'type': 'validation_error', 'description': str(e)}],
                'warnings': [],
                'quality_assessment': {'quality': ResponseQuality.UNACCEPTABLE},
                'validated_at': datetime.utcnow().isoformat(),
                'recommendation': 'Use fallback response due to validation error'
            }
    
    def _check_inappropriate_content(self, text: str) -> List[Dict[str, Any]]:
        """Check for inappropriate content"""
        violations = []
        text_lower = text.lower()
        
        for pattern, violation_subtype in self._inappropriate_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append({
                    'type': GuardrailViolationType.INAPPROPRIATE_CONTENT.value,
                    'subtype': violation_subtype,
                    'description': f"Inappropriate content detected: {violation_subtype}",
                    'matched_text': matches[0] if matches else None,
                    'severity': 'high'
                })
        
        return violations
    
    def _check_therapeutic_boundaries(self, text: str) -> List[Dict[str, Any]]:
        """Check for therapeutic boundary violations"""
        violations = []
        text_lower = text.lower()
        
        for pattern, violation_subtype in self._boundary_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append({
                    'type': GuardrailViolationType.THERAPEUTIC_BOUNDARY.value,
                    'subtype': violation_subtype,
                    'description': f"Therapeutic boundary violation: {violation_subtype}",
                    'matched_text': matches[0] if matches else None,
                    'severity': 'high'
                })
        
        return violations
    
    def _check_harmful_advice(self, text: str) -> List[Dict[str, Any]]:
        """Check for harmful advice"""
        violations = []
        text_lower = text.lower()
        
        for pattern, violation_subtype in self._harmful_advice_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append({
                    'type': GuardrailViolationType.HARMFUL_ADVICE.value,
                    'subtype': violation_subtype,
                    'description': f"Harmful advice detected: {violation_subtype}",
                    'matched_text': matches[0] if matches else None,
                    'severity': 'critical'
                })
        
        return violations
    
    def _check_medical_diagnosis(self, text: str) -> List[Dict[str, Any]]:
        """Check for medical diagnosis attempts"""
        violations = []
        text_lower = text.lower()
        
        for pattern, violation_subtype in self._medical_diagnosis_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append({
                    'type': GuardrailViolationType.MEDICAL_DIAGNOSIS.value,
                    'subtype': violation_subtype,
                    'description': f"Medical diagnosis attempt: {violation_subtype}",
                    'matched_text': matches[0] if matches else None,
                    'severity': 'critical'
                })
        
        return violations
    
    def _check_triggering_content(self, text: str) -> List[Dict[str, Any]]:
        """Check for potentially triggering content"""
        violations = []
        text_lower = text.lower()
        
        for pattern, violation_subtype in self._triggering_content_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                violations.append({
                    'type': GuardrailViolationType.TRIGGERING_CONTENT.value,
                    'subtype': violation_subtype,
                    'description': f"Potentially triggering content: {violation_subtype}",
                    'matched_text': matches[0] if matches else None,
                    'severity': 'high'
                })
        
        return violations
    
    def _assess_response_quality(self, text: str) -> Dict[str, Any]:
        """Assess overall response quality"""
        try:
            text_lower = text.lower()
            
            # Count validation phrases
            validation_phrases = [
                'i hear', 'i understand', 'that sounds', 'i can see',
                'it makes sense', 'your feelings', 'you are not alone',
                'i\'m sorry', 'thank you for sharing'
            ]
            validation_count = sum(1 for phrase in validation_phrases if phrase in text_lower)
            
            # Count directive phrases (should be minimal)
            directive_phrases = [
                'you should', 'you must', 'you need to', 'you have to'
            ]
            directive_count = sum(1 for phrase in directive_phrases if phrase in text_lower)
            
            # Count empathy indicators
            empathy_indicators = [
                'difficult', 'challenging', 'understand', 'hear',
                'support', 'help', 'care', 'safe'
            ]
            empathy_count = sum(1 for indicator in empathy_indicators if indicator in text_lower)
            
            # Count clinical terms (should be minimal for accessibility)
            clinical_terms = [
                'diagnosis', 'disorder', 'pathology', 'syndrome',
                'symptom', 'treatment', 'therapy', 'clinical'
            ]
            clinical_count = sum(1 for term in clinical_terms if term in text_lower)
            
            # Calculate quality score
            quality_score = 0.0
            
            # Positive factors
            if validation_count >= self._quality_thresholds['min_validation_phrases']:
                quality_score += 0.3
            if empathy_count >= self._quality_thresholds['min_empathy_indicators']:
                quality_score += 0.3
            if directive_count <= self._quality_thresholds['max_directive_phrases']:
                quality_score += 0.2
            if clinical_count <= self._quality_thresholds['max_clinical_terms']:
                quality_score += 0.2
            
            # Determine quality level
            if quality_score >= 0.8:
                quality = ResponseQuality.EXCELLENT
            elif quality_score >= 0.6:
                quality = ResponseQuality.GOOD
            elif quality_score >= 0.4:
                quality = ResponseQuality.ACCEPTABLE
            elif quality_score >= 0.2:
                quality = ResponseQuality.POOR
            else:
                quality = ResponseQuality.UNACCEPTABLE
            
            return {
                'quality': quality,
                'quality_score': quality_score,
                'validation_count': validation_count,
                'directive_count': directive_count,
                'empathy_count': empathy_count,
                'clinical_count': clinical_count,
                'meets_thresholds': {
                    'validation': validation_count >= self._quality_thresholds['min_validation_phrases'],
                    'directives': directive_count <= self._quality_thresholds['max_directive_phrases'],
                    'empathy': empathy_count >= self._quality_thresholds['min_empathy_indicators'],
                    'clinical': clinical_count <= self._quality_thresholds['max_clinical_terms']
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to assess response quality: {str(e)}")
            return {
                'quality': ResponseQuality.UNACCEPTABLE,
                'quality_score': 0.0,
                'error': str(e)
            }
    
    def _get_recommendation(self, violations: List[Dict[str, Any]], 
                          warnings: List[Dict[str, Any]], 
                          quality_assessment: Dict[str, Any]) -> str:
        """Get recommendation based on validation results"""
        if len(violations) > 0:
            critical_violations = [v for v in violations if v.get('severity') == 'critical']
            if critical_violations:
                return "BLOCK: Critical safety violations detected. Use fallback response."
            else:
                return "REVISE: Safety violations detected. Regenerate response with corrections."
        
        if quality_assessment['quality'] == ResponseQuality.UNACCEPTABLE:
            return "REVISE: Response quality unacceptable. Regenerate with better therapeutic approach."
        
        if quality_assessment['quality'] == ResponseQuality.POOR:
            return "WARN: Response quality is poor. Consider regeneration."
        
        if len(warnings) > 0:
            return "CAUTION: Potentially triggering content detected. Review before sending."
        
        return "APPROVE: Response meets safety and quality standards."
    
    def filter_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Filter and sanitize user input
        
        Args:
            user_input: Raw user input text
            
        Returns:
            Filtered input and metadata
        """
        try:
            # Remove potential PII patterns
            filtered_text = user_input
            pii_removed = []
            
            # Email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if re.search(email_pattern, filtered_text):
                filtered_text = re.sub(email_pattern, '[EMAIL]', filtered_text)
                pii_removed.append('email')
            
            # Postcodes (UK format) - check BEFORE phone numbers to avoid conflicts
            # Matches: SW1A 1AA, M1 1AE, B33 8TH, etc.
            postcode_pattern = r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b'
            if re.search(postcode_pattern, filtered_text, re.IGNORECASE):
                filtered_text = re.sub(postcode_pattern, '[POSTCODE]', filtered_text, flags=re.IGNORECASE)
                pii_removed.append('postcode')
            
            # Phone numbers (UK format) - more specific pattern to avoid matching pure numbers
            # Matches: +44 123 456 7890, 0123 456 7890, 07123456789, etc.
            # Must start with +44 or 0, and have proper spacing/formatting
            phone_pattern = r'\b(?:\+44|0)[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}\b'
            if re.search(phone_pattern, filtered_text):
                filtered_text = re.sub(phone_pattern, '[PHONE]', filtered_text)
                pii_removed.append('phone')
            
            # Check for spam/abuse patterns
            is_spam = self._check_spam_patterns(user_input)
            
            return {
                'original_text': user_input,
                'filtered_text': filtered_text,
                'pii_removed': pii_removed,
                'is_spam': is_spam,
                'is_safe': not is_spam,
                'filtered_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to filter user input: {str(e)}")
            return {
                'original_text': user_input,
                'filtered_text': user_input,
                'pii_removed': [],
                'is_spam': False,
                'is_safe': True,
                'error': str(e),
                'filtered_at': datetime.utcnow().isoformat()
            }
    
    def _check_spam_patterns(self, text: str) -> bool:
        """Check for spam or abuse patterns"""
        text_lower = text.lower()
        
        # Spam indicators
        spam_patterns = [
            r'\b(buy|purchase|order)\s+now\b',
            r'\bclick\s+here\b',
            r'\bfree\s+money\b',
            r'\bwin\s+\$\d+\b',
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Excessive repetition
        words = text_lower.split()
        if len(words) > 10:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:  # Less than 30% unique words
                return True
        
        return False
    
    def get_fallback_response(self, context: Optional[str] = None) -> str:
        """
        Get safe fallback response when guardrails are violated
        
        Args:
            context: Optional context about why fallback is needed
            
        Returns:
            Safe fallback response text
        """
        fallback_responses = [
            "I want to make sure I'm providing you with the best support possible. Let me rephrase that in a more helpful way.",
            "I appreciate you sharing that with me. Let me respond in a way that's more supportive and appropriate.",
            "Thank you for your openness. I want to ensure my response is as helpful and safe as possible for you.",
            "I hear what you're saying. Let me take a moment to respond in the most supportive way I can."
        ]
        
        # Return first fallback for consistency
        return fallback_responses[0]
    
    def log_guardrail_violation(self, violation_data: Dict[str, Any], 
                               session_id: str, response_text: str) -> None:
        """
        Log guardrail violation for monitoring and improvement
        
        Args:
            violation_data: Violation details
            session_id: Session identifier
            response_text: The response that violated guardrails
        """
        try:
            log_entry = {
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'violations': violation_data.get('violations', []),
                'warnings': violation_data.get('warnings', []),
                'quality_assessment': violation_data.get('quality_assessment', {}),
                'response_length': len(response_text),
                'recommendation': violation_data.get('recommendation', 'unknown')
            }
            
            # In production, this would be stored in a GuardrailViolations table
            logger.warning(f"GUARDRAIL VIOLATION: {log_entry}")
            
        except Exception as e:
            logger.error(f"Failed to log guardrail violation: {str(e)}")
    
    def get_guardrail_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get guardrail violation statistics
        
        Args:
            days: Number of days to include in statistics
            
        Returns:
            Statistics dictionary
        """
        try:
            # In production, this would query the GuardrailViolations table
            # For hackathon, return placeholder structure
            
            return {
                'period_days': days,
                'total_validations': 0,
                'total_violations': 0,
                'violation_rate': 0.0,
                'violations_by_type': {},
                'quality_distribution': {},
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get guardrail statistics: {str(e)}")
            return {
                'period_days': days,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
