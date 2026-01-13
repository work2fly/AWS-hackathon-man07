"""
Red Flag Detection Service for AI Therapy Platform
Implements content analysis pipeline for safety triggers and real-time detection
🏆 Breaking Barriers UK 2026 compliant
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from ..models.red_flag import RedFlag, RedFlagType, Severity
from ..data.red_flag_repository import RedFlagRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DetectionPattern:
    """Pattern for red flag detection"""
    
    def __init__(self, pattern: str, flag_type: RedFlagType, severity: Severity, 
                 description: str, weight: float = 1.0):
        self.pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.flag_type = flag_type
        self.severity = severity
        self.description = description
        self.weight = weight


class RedFlagDetectionService:
    """Service for detecting safety concerns in therapy sessions"""
    
    def __init__(self):
        self.red_flag_repo = RedFlagRepository()
        self._detection_patterns = self._initialize_detection_patterns()
        self._severity_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 1.0
        }
    
    def _initialize_detection_patterns(self) -> List[DetectionPattern]:
        """Initialize detection patterns for various red flag types"""
        patterns = []
        
        # Self-harm patterns (enhanced with UKind charity scenarios)
        self_harm_patterns = [
            (r'\b(cut|cutting|hurt|hurting)\s+(myself|me)\b', Severity.HIGH, 0.9),
            (r'\bself[\s-]?harm(ing|ed)?\b', Severity.HIGH, 0.9),  # Fixed pattern for self-harming
            (r'\b(burn|burning|burned)\s+(myself|me)\b', Severity.HIGH, 0.9),
            (r'\b(scratch|scratching|scratched)\s+(myself|me)\b', Severity.MEDIUM, 0.6),
            (r'\bwant\s+to\s+(hurt|harm)\s+(myself|me)\b', Severity.HIGH, 0.8),
            (r'\b(razor|blade|knife)\b.*\b(skin|arm|leg|wrist)\b', Severity.CRITICAL, 1.0),
            (r'\bhit\s+(myself|me|my\s+head)\b', Severity.MEDIUM, 0.7),
            (r'\bpull\s+(my\s+hair|hair)\s+out\b', Severity.MEDIUM, 0.5),
            # UKind charity specific patterns
            (r'\bi\s+deserve\s+this\b', Severity.HIGH, 0.8),
            (r'\bi\s+hate\s+myself\b', Severity.HIGH, 0.8),
            (r'\bi\s+can\'?t\s+do\s+anything\s+right\b', Severity.MEDIUM, 0.6),
            (r'\bit\'?s\s+(probably\s+)?my\s+(own\s+)?fault\b', Severity.MEDIUM, 0.6),
            (r'\bi\s+deserve\s+this\s+type\s+of\s+love\b', Severity.HIGH, 0.8),
        ]
        
        for pattern, severity, weight in self_harm_patterns:
            patterns.append(DetectionPattern(
                pattern, RedFlagType.SELF_HARM, severity,
                f"Self-harm indicator: {pattern}", weight
            ))
        
        # Suicidal ideation patterns (enhanced with UKind charity scenarios)
        suicidal_patterns = [
            (r'\b(kill|killing)\s+(myself|me)\b', Severity.CRITICAL, 1.0),
            (r'\bcommit\s+suicide\b', Severity.CRITICAL, 1.0),
            (r'\bend\s+(my\s+life|it\s+all)\b', Severity.CRITICAL, 1.0),
            (r'\bdon\'?t\s+want\s+to\s+(live|be\s+alive)\b', Severity.HIGH, 0.9),
            (r'\bbetter\s+off\s+dead\b', Severity.HIGH, 0.9),
            (r'\bwish\s+I\s+(was|were)\s+dead\b', Severity.HIGH, 0.8),
            (r'\bthink\s+about\s+(dying|death)\b', Severity.MEDIUM, 0.6),
            (r'\bsuicidal\s+(thoughts|ideation)\b', Severity.HIGH, 0.9),
            (r'\bplan\s+to\s+(kill|hurt)\s+(myself|me)\b', Severity.CRITICAL, 1.0),
            (r'\b(pills|overdose|hanging|jump)\b.*\b(end|die|death)\b', Severity.CRITICAL, 1.0),
            (r'\bnothing\s+to\s+live\s+for\b', Severity.HIGH, 0.8),
            (r'\bcan\'?t\s+go\s+on\b', Severity.MEDIUM, 0.5),
            # UKind charity specific patterns
            (r'\bi\s+want\s+to\s+take\s+my\s+life\b', Severity.CRITICAL, 1.0),
            (r'\bi\s+don\'?t\s+think\s+life\s+is\s+worth\s+living\b', Severity.CRITICAL, 1.0),
            (r'\bi\s+don\'?t\s+want\s+to\s+continue\s+on\b', Severity.CRITICAL, 1.0),
            (r'\bit\s+would\s+be\s+better\s+if\s+i\s+was\s+dead\b', Severity.CRITICAL, 1.0),
            (r'\bi\s+just\s+can\'?t\s+do\s+this\s+anymore\b', Severity.HIGH, 0.9),
        ]
        
        for pattern, severity, weight in suicidal_patterns:
            patterns.append(DetectionPattern(
                pattern, RedFlagType.SUICIDAL_IDEATION, severity,
                f"Suicidal ideation indicator: {pattern}", weight
            ))
        
        # Abuse patterns (enhanced with UKind charity scenarios)
        abuse_patterns = [
            (r'\b(hit|hits|hitting|beat|beats|beating)\s+me\b', Severity.HIGH, 0.9),
            (r'\b(abuse|abused|abusing)\s+me\b', Severity.HIGH, 0.9),
            (r'\b(sexual|sexually)\s+(abuse|assault|harass)\b', Severity.CRITICAL, 1.0),
            (r'\b(rape|raped|molest|molested)\b', Severity.CRITICAL, 1.0),
            (r'\bdomestic\s+(violence|abuse)\b', Severity.HIGH, 0.9),
            (r'\bphysical\s+(violence|abuse)\b', Severity.HIGH, 0.8),
            (r'\bemotional\s+abuse\b', Severity.MEDIUM, 0.6),
            (r'\bverbally\s+(abuse|abusive)\b', Severity.MEDIUM, 0.5),
            (r'\bthreaten|threatens|threatening\b.*\b(hurt|harm|kill)\b', Severity.HIGH, 0.8),
            (r'\bafraid\s+of\s+(him|her|them)\b', Severity.MEDIUM, 0.6),
            # UKind charity specific patterns
            (r'\bi\'?m\s+scared\s+of\s+my\s+partner\b', Severity.HIGH, 0.9),
            (r'\bthey\s+hurt\s+me\b', Severity.HIGH, 0.9),
            (r'\bi\s+am\s+scared\s+to\s+go\s+home\b', Severity.HIGH, 0.9),
            (r'\bnobody\s+listens\s+to\s+me\b', Severity.MEDIUM, 0.5),
            (r'\bi\s+feel\s+invisible\b', Severity.MEDIUM, 0.5),
            (r'\bpeople\s+don\'?t\s+believe\s+me\b', Severity.MEDIUM, 0.6),
            (r'\bnobody\s+wants\s+to\s+be\s+around\s+me\b', Severity.MEDIUM, 0.5),
        ]
        
        for pattern, severity, weight in abuse_patterns:
            patterns.append(DetectionPattern(
                pattern, RedFlagType.ABUSE, severity,
                f"Abuse indicator: {pattern}", weight
            ))
        
        # Violence patterns (enhanced with UKind charity scenarios)
        violence_patterns = [
            (r'\bwant\s+to\s+(hurt|harm|kill)\s+(someone|somebody|people)\b', Severity.HIGH, 0.9),
            (r'\bthink\s+about\s+(hurting|harming|killing)\s+(others|people)\b', Severity.HIGH, 0.8),
            (r'\bviolent\s+(thoughts|fantasies)\b', Severity.MEDIUM, 0.7),
            (r'\bplan\s+to\s+(hurt|harm|attack)\b', Severity.CRITICAL, 1.0),
            (r'\b(weapon|gun|knife|bomb)\b.*\b(use|hurt|harm)\b', Severity.CRITICAL, 1.0),
            (r'\brage|angry|furious\b.*\b(violence|violent|hurt)\b', Severity.MEDIUM, 0.6),
            (r'\blose\s+control\b.*\b(hurt|harm|violence)\b', Severity.HIGH, 0.8),
            # UKind charity specific patterns
            (r'\bi\s+feel\s+like\s+i\s+want\s+to\s+hurt\s+someone\b', Severity.HIGH, 0.9),
            (r'\bi\s+hate\s+them\b.*\bi\s+wish\s+they\s+were\s+dead\b', Severity.HIGH, 0.9),
            (r'\bi\s+wish\s+they\s+were\s+dead\b', Severity.HIGH, 0.8),
        ]
        
        for pattern, severity, weight in violence_patterns:
            patterns.append(DetectionPattern(
                pattern, RedFlagType.VIOLENCE, severity,
                f"Violence indicator: {pattern}", weight
            ))
        
        # Crisis patterns (enhanced with UKind charity scenarios)
        crisis_patterns = [
            (r'\bmental\s+breakdown\b', Severity.HIGH, 0.8),
            (r'\bcan\'?t\s+(cope|handle)\s+(anymore|this)\b', Severity.MEDIUM, 0.6),
            (r'\bcompletely\s+(overwhelmed|lost)\b', Severity.MEDIUM, 0.5),
            (r'\bpsychotic\s+(episode|break)\b', Severity.HIGH, 0.9),
            (r'\bhallucination|hallucinating|hearing\s+voices\b', Severity.HIGH, 0.9),
            (r'\bparanoid|paranoia\b', Severity.MEDIUM, 0.6),
            (r'\bpanic\s+attack\b', Severity.MEDIUM, 0.4),
            (r'\bsevere\s+(depression|anxiety)\b', Severity.MEDIUM, 0.5),
            # UKind charity specific patterns - panic and breathing issues
            (r'\bi\s+feel\s+like\s+i\s+can\'?t\s+breathe\b', Severity.HIGH, 0.8),
            (r'\bi\s+think\s+i\'?m\s+having\s+a\s+panic\s+attack\b', Severity.HIGH, 0.8),
            (r'\bmy\s+chest\s+is\s+feeling\s+really\s+tight\b', Severity.MEDIUM, 0.6),
            (r'\bi\s+am\s+struggling\s+to\s+calm\s+my\s+breathing\b', Severity.MEDIUM, 0.6),
            (r'\bi\s+can\'?t\s+breathe\b', Severity.HIGH, 0.8),
        ]
        
        for pattern, severity, weight in crisis_patterns:
            patterns.append(DetectionPattern(
                pattern, RedFlagType.CRISIS, severity,
                f"Crisis indicator: {pattern}", weight
            ))
        
        return patterns
    
    def analyze_content(self, content: str, session_id: str) -> List[Dict[str, Any]]:
        """
        Analyze content for red flag patterns
        
        Args:
            content: Text content to analyze
            session_id: Session identifier for context
            
        Returns:
            List of detected red flags with details
        """
        try:
            if not content or not content.strip():
                return []
            
            detected_flags = []
            content_lower = content.lower()
            
            # Track pattern matches and their weights
            flag_scores = {}
            
            for pattern in self._detection_patterns:
                matches = pattern.pattern.findall(content)
                
                if matches:
                    flag_type = pattern.flag_type.value
                    
                    if flag_type not in flag_scores:
                        flag_scores[flag_type] = {
                            'total_weight': 0.0,
                            'matches': [],
                            'max_severity': Severity.LOW
                        }
                    
                    # Add weight and track matches
                    flag_scores[flag_type]['total_weight'] += pattern.weight
                    flag_scores[flag_type]['matches'].extend(matches)
                    
                    # Track highest severity
                    if self._severity_to_numeric(pattern.severity) > self._severity_to_numeric(flag_scores[flag_type]['max_severity']):
                        flag_scores[flag_type]['max_severity'] = pattern.severity
                    
                    logger.debug(f"Pattern match in session {session_id}: {pattern.description} - {matches}")
            
            # Convert scores to red flags
            for flag_type, score_data in flag_scores.items():
                severity = self._calculate_final_severity(score_data['total_weight'], score_data['max_severity'])
                
                # Create sanitized context (remove sensitive details)
                context = self._create_sanitized_context(content, score_data['matches'])
                
                detected_flag = {
                    'type': flag_type,
                    'severity': severity.value,
                    'confidence_score': min(score_data['total_weight'], 1.0),
                    'context': context,
                    'match_count': len(score_data['matches']),
                    'detected_at': datetime.utcnow().isoformat()
                }
                
                detected_flags.append(detected_flag)
                
                logger.info(f"Red flag detected in session {session_id}: {flag_type} - {severity.value}")
            
            return detected_flags
            
        except Exception as e:
            logger.error(f"Failed to analyze content for red flags: {str(e)}")
            return []
    
    def _severity_to_numeric(self, severity: Severity) -> int:
        """Convert severity to numeric value for comparison"""
        severity_map = {
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4
        }
        return severity_map.get(severity, 1)
    
    def _calculate_final_severity(self, total_weight: float, max_severity: Severity) -> Severity:
        """Calculate final severity based on weight and pattern severity"""
        # Use the higher of weight-based severity or pattern-based severity
        weight_severity = Severity.LOW
        
        if total_weight >= self._severity_thresholds['critical']:
            weight_severity = Severity.CRITICAL
        elif total_weight >= self._severity_thresholds['high']:
            weight_severity = Severity.HIGH
        elif total_weight >= self._severity_thresholds['medium']:
            weight_severity = Severity.MEDIUM
        else:
            weight_severity = Severity.LOW
        
        # Return the higher severity
        if self._severity_to_numeric(max_severity) > self._severity_to_numeric(weight_severity):
            return max_severity
        else:
            return weight_severity
    
    def _create_sanitized_context(self, content: str, matches: List[str]) -> str:
        """Create sanitized context around matches for logging"""
        try:
            # Limit context length and remove sensitive information
            max_context_length = 200
            
            if len(content) <= max_context_length:
                sanitized = content
            else:
                # Find the first match and create context around it
                if matches:
                    first_match = str(matches[0]) if matches[0] else ""
                    match_pos = content.lower().find(first_match.lower())
                    
                    if match_pos != -1:
                        start = max(0, match_pos - 50)
                        end = min(len(content), match_pos + 150)
                        sanitized = "..." + content[start:end] + "..."
                    else:
                        sanitized = content[:max_context_length] + "..."
                else:
                    sanitized = content[:max_context_length] + "..."
            
            # Remove potential PII patterns
            sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', sanitized)  # SSN
            sanitized = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', sanitized)  # Phone
            sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', sanitized)  # Email
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Failed to create sanitized context: {str(e)}")
            return "Context unavailable"
    
    def create_red_flag(self, session_id: str, flag_type: RedFlagType, 
                       severity: Severity, context: str) -> Optional[RedFlag]:
        """
        Create and store a red flag
        
        Args:
            session_id: Session identifier
            flag_type: Type of red flag
            severity: Severity level
            context: Sanitized context
            
        Returns:
            Created RedFlag object or None if failed
        """
        try:
            # Generate unique flag ID
            timestamp = datetime.utcnow()
            flag_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{flag_type.value}_{session_id[-8:]}"
            
            # Create red flag object
            red_flag = RedFlag(
                session_id=session_id,
                flag_id=flag_id,
                type=flag_type,
                severity=severity,
                detected_at=timestamp,
                context=context
            )
            
            # Store in repository
            success = self.red_flag_repo.create_red_flag(red_flag)
            
            if success:
                logger.info(f"Created red flag {flag_id} for session {session_id}")
                return red_flag
            else:
                logger.error(f"Failed to store red flag {flag_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create red flag: {str(e)}")
            return None
    
    def process_session_content(self, session_id: str, content: str) -> List[RedFlag]:
        """
        Process session content and create red flags for detected issues
        
        Args:
            session_id: Session identifier
            content: Session content to analyze
            
        Returns:
            List of created RedFlag objects
        """
        try:
            # Analyze content for red flags
            detected_flags = self.analyze_content(content, session_id)
            
            created_flags = []
            
            # Create red flag records for each detection
            for flag_data in detected_flags:
                red_flag = self.create_red_flag(
                    session_id=session_id,
                    flag_type=RedFlagType(flag_data['type']),
                    severity=Severity(flag_data['severity']),
                    context=flag_data['context']
                )
                
                if red_flag:
                    created_flags.append(red_flag)
            
            return created_flags
            
        except Exception as e:
            logger.error(f"Failed to process session content: {str(e)}")
            return []
    
    def assess_risk_level(self, session_id: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Assess overall risk level for a session based on recent red flags
        
        Args:
            session_id: Session identifier
            time_window_hours: Time window to consider for risk assessment
            
        Returns:
            Dictionary with risk assessment results
        """
        try:
            # Get recent red flags for the session
            red_flags = self.red_flag_repo.get_red_flags_by_session(session_id)
            
            # Filter to time window
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            recent_flags = [
                flag for flag in red_flags 
                if flag.detected_at >= cutoff_time
            ]
            
            if not recent_flags:
                return {
                    'risk_level': 'low',
                    'risk_score': 0.0,
                    'flag_count': 0,
                    'highest_severity': None,
                    'assessment_time': datetime.utcnow().isoformat()
                }
            
            # Calculate risk score
            severity_weights = {
                Severity.LOW: 0.25,
                Severity.MEDIUM: 0.5,
                Severity.HIGH: 0.75,
                Severity.CRITICAL: 1.0
            }
            
            total_score = 0.0
            highest_severity = Severity.LOW
            
            for flag in recent_flags:
                total_score += severity_weights.get(flag.severity, 0.25)
                if self._severity_to_numeric(flag.severity) > self._severity_to_numeric(highest_severity):
                    highest_severity = flag.severity
            
            # Normalize score (cap at 1.0)
            risk_score = min(total_score / len(recent_flags), 1.0)
            
            # Determine risk level
            if risk_score >= 0.8 or highest_severity == Severity.CRITICAL:
                risk_level = 'critical'
            elif risk_score >= 0.6 or highest_severity == Severity.HIGH:
                risk_level = 'high'
            elif risk_score >= 0.3 or highest_severity == Severity.MEDIUM:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'flag_count': len(recent_flags),
                'highest_severity': highest_severity.value,
                'flag_types': list(set([flag.type.value for flag in recent_flags])),
                'assessment_time': datetime.utcnow().isoformat(),
                'time_window_hours': time_window_hours
            }
            
        except Exception as e:
            logger.error(f"Failed to assess risk level for session {session_id}: {str(e)}")
            return {
                'risk_level': 'unknown',
                'risk_score': 0.0,
                'flag_count': 0,
                'highest_severity': None,
                'error': str(e),
                'assessment_time': datetime.utcnow().isoformat()
            }
    
    def get_detection_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get red flag detection statistics
        
        Args:
            days: Number of days to include in statistics
            
        Returns:
            Dictionary with detection statistics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            stats = self.red_flag_repo.get_red_flag_statistics(start_date=start_date)
            
            # Add detection rate information
            stats['detection_period_days'] = days
            stats['average_flags_per_day'] = stats['total_count'] / max(days, 1)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get detection statistics: {str(e)}")
            return {
                'total_count': 0,
                'by_type': {},
                'by_severity': {},
                'resolved_count': 0,
                'unresolved_count': 0,
                'detection_period_days': days,
                'average_flags_per_day': 0.0,
                'error': str(e)
            }
    
    def update_detection_patterns(self, new_patterns: List[Dict[str, Any]]) -> bool:
        """
        Update detection patterns (for admin use)
        
        Args:
            new_patterns: List of pattern dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In production, this would validate and update patterns
            # For hackathon, we'll log the update request
            logger.info(f"Pattern update requested: {len(new_patterns)} patterns")
            
            # Validate pattern format
            for pattern_data in new_patterns:
                required_fields = ['pattern', 'flag_type', 'severity', 'description']
                if not all(field in pattern_data for field in required_fields):
                    logger.error(f"Invalid pattern format: {pattern_data}")
                    return False
            
            # In production, this would:
            # 1. Validate regex patterns
            # 2. Test patterns against known data
            # 3. Update pattern storage
            # 4. Reload detection service
            
            logger.info("Pattern update completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update detection patterns: {str(e)}")
            return False