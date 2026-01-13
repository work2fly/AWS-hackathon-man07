"""
Trauma-Informed Response Service for AI Therapy Platform
Implements UKind charity's trauma-informed response guidelines
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from ..models.red_flag import RedFlag, RedFlagType, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ResponseType(str, Enum):
    """Response type enumeration"""
    ACKNOWLEDGMENT = "acknowledgment"
    VALIDATION = "validation"
    GROUNDING = "grounding"
    RESOURCE_OFFER = "resource_offer"
    EMERGENCY_PROTOCOL = "emergency_protocol"
    SAFETY_CHECK = "safety_check"


class TraumaInformedResponseService:
    """Service for generating trauma-informed responses based on UKind guidelines"""
    
    def __init__(self):
        self._response_templates = self._initialize_response_templates()
        self._grounding_techniques = self._initialize_grounding_techniques()
        self._resource_database = self._initialize_resources()
    
    def _initialize_response_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize trauma-informed response templates based on UKind guidelines"""
        return {
            RedFlagType.SUICIDAL_IDEATION.value: {
                'acknowledgment': [
                    "I'm really sorry to hear you're feeling this way. It sounds like you're going through a very difficult time.",
                    "Thank you for sharing something so difficult with me. I can hear how much pain you're in right now.",
                    "I'm concerned about you and I want to help you get the support you need."
                ],
                'validation': [
                    "Your feelings are valid, and it's understandable that you're struggling.",
                    "It takes courage to share these thoughts, and I'm glad you're talking about them.",
                    "You are not alone in feeling this way, and there are people who care deeply about your well-being."
                ],
                'resource_offer': [
                    "Please consider reaching out to a trusted person or a helpline like Samaritans (116 123). If you're in immediate danger, please contact emergency services.",
                    "Would you like me to help you find resources and support services?",
                    "There are people trained to help with exactly what you're going through. Would you like me to connect you with them?"
                ],
                'emergency_protocol': [
                    "If you're in immediate danger, please call 999 or go to your nearest A&E.",
                    "Would you like me to help you contact emergency services right now?",
                    "Your safety is the most important thing. Let's get you connected with immediate help."
                ]
            },
            
            RedFlagType.SELF_HARM.value: {
                'acknowledgment': [
                    "I'm sorry you're going through this. It sounds like you're dealing with a lot of pain right now.",
                    "Thank you for trusting me with something so personal. I can hear how difficult this is for you.",
                    "I'm concerned about you and want to help you find healthier ways to cope."
                ],
                'validation': [
                    "Sometimes when we're overwhelmed, we look for ways to cope, even if they're not healthy.",
                    "Your pain is real and valid. There are other ways to manage these intense feelings.",
                    "You deserve care and support, not harm."
                ],
                'resource_offer': [
                    "There are people who can help you find healthier coping strategies. Would you like me to help you find support?",
                    "Self-harm support services like Harmless (www.harmless.org.uk) can provide specialized help.",
                    "Would you like to talk about what's driving these feelings?"
                ]
            },
            
            RedFlagType.ABUSE.value: {
                'acknowledgment': [
                    "I'm so sorry you're feeling this way. No one deserves to be hurt or feel unsafe.",
                    "Thank you for sharing something so difficult. I believe you, and I'm concerned for your safety.",
                    "What you're describing sounds frightening and overwhelming."
                ],
                'validation': [
                    "You are not to blame for what's happening to you.",
                    "Your feelings of fear are completely understandable given what you're experiencing.",
                    "It takes incredible strength to talk about abuse."
                ],
                'resource_offer': [
                    "If you feel you're in immediate danger, please call emergency services (999).",
                    "You can contact the National Domestic Abuse Helpline (0808 2000 247) for confidential support and advice.",
                    "Would you like me to help you find support services near you?"
                ],
                'safety_check': [
                    "Are you in a safe place right now?",
                    "Do you have somewhere safe you can go if you need to?",
                    "Is there someone you trust who you could reach out to?"
                ]
            },
            
            RedFlagType.VIOLENCE.value: {
                'acknowledgment': [
                    "It sounds like you're experiencing intense feelings. It's important to talk to someone who can help you process these emotions safely.",
                    "Thank you for sharing these difficult thoughts with me. I can hear how distressing they are for you.",
                    "These feelings can be frightening, and it's good that you're talking about them."
                ],
                'validation': [
                    "Intense anger and frustration are human emotions, but acting on violent thoughts would harm both you and others.",
                    "It's normal to have difficult emotions, but there are healthy ways to process them.",
                    "You don't have to carry these feelings alone."
                ],
                'resource_offer': [
                    "Please consider reaching out to a professional or a trusted person in your life to discuss how you're feeling.",
                    "There are ways to work through these feelings without harming anyone, and you don't have to do it alone.",
                    "Would you like help finding someone to talk to about managing these intense emotions?"
                ]
            },
            
            RedFlagType.CRISIS.value: {
                'acknowledgment': [
                    "I can hear that you're in distress right now. Let's take this one step at a time.",
                    "It sounds like you're feeling overwhelmed. I'm here to help you through this moment.",
                    "What you're experiencing sounds very frightening. You're not alone."
                ],
                'grounding': [
                    "Let's focus on your breathing together. Try to breathe in slowly for 4 seconds, hold for 4 seconds, and breathe out for 4 seconds.",
                    "You are safe right now. Let's ground ourselves in this moment.",
                    "Can you tell me 5 things you can see around you right now?"
                ],
                'validation': [
                    "It's okay to feel this way; these intense feelings will pass.",
                    "You're doing the right thing by reaching out for help.",
                    "These symptoms can be very scary, but you're going to get through this."
                ]
            }
        }
    
    def _initialize_grounding_techniques(self) -> Dict[str, List[str]]:
        """Initialize grounding techniques for crisis situations"""
        return {
            'breathing': [
                "Let's try the 4-7-8 breathing technique: Breathe in for 4 counts, hold for 7 counts, breathe out for 8 counts.",
                "Focus on your breath. Breathe in slowly through your nose, and out slowly through your mouth.",
                "Let's do some deep breathing together. In for 4... hold for 4... out for 4..."
            ],
            'grounding_5_4_3_2_1': [
                "Let's try the 5-4-3-2-1 technique: Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and take 1 deep breath.",
                "Can you tell me 5 things you can see around you right now?",
                "Let's ground ourselves: What are 4 things you can feel or touch right now?"
            ],
            'present_moment': [
                "You are here, you are safe, you are in this moment.",
                "Let's focus on right now. You are safe in this moment.",
                "Ground yourself: Feel your feet on the floor, notice your breathing."
            ],
            'self_compassion': [
                "You are doing the best you can in this difficult moment.",
                "Be gentle with yourself. You deserve kindness and care.",
                "You are worthy of support and help."
            ]
        }
    
    def _initialize_resources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize UK-specific mental health resources"""
        return {
            'crisis_helplines': {
                'samaritans': {
                    'name': 'Samaritans',
                    'phone': '116 123',
                    'description': '24/7 emotional support for anyone in distress',
                    'website': 'www.samaritans.org'
                },
                'crisis_text_line': {
                    'name': 'Crisis Text Line',
                    'text': 'Text SHOUT to 85258',
                    'description': '24/7 text support for mental health crises'
                }
            },
            'domestic_abuse': {
                'national_helpline': {
                    'name': 'National Domestic Abuse Helpline',
                    'phone': '0808 2000 247',
                    'description': '24/7 confidential support for domestic abuse',
                    'website': 'www.nationaldahelpline.org.uk'
                },
                'mens_advice_line': {
                    'name': "Men's Advice Line",
                    'phone': '0808 8010 327',
                    'description': 'Support for men experiencing domestic abuse'
                }
            },
            'self_harm': {
                'harmless': {
                    'name': 'Harmless',
                    'website': 'www.harmless.org.uk',
                    'description': 'Support and information about self-harm'
                },
                'mind': {
                    'name': 'Mind',
                    'phone': '0300 123 3393',
                    'description': 'Mental health support and information',
                    'website': 'www.mind.org.uk'
                }
            },
            'emergency': {
                'emergency_services': {
                    'name': 'Emergency Services',
                    'phone': '999',
                    'description': 'For immediate life-threatening emergencies'
                },
                'nhs_111': {
                    'name': 'NHS 111',
                    'phone': '111',
                    'description': 'For urgent but non-life-threatening health concerns'
                }
            }
        }
    
    def generate_trauma_informed_response(self, red_flag: RedFlag, 
                                        context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate trauma-informed response based on red flag type and UKind guidelines
        
        Args:
            red_flag: RedFlag object
            context: Optional additional context
            
        Returns:
            Dictionary with response components
        """
        try:
            flag_type = red_flag.type.value
            severity = red_flag.severity
            
            response_components = {
                'acknowledgment': self._get_acknowledgment(flag_type),
                'validation': self._get_validation(flag_type),
                'safety_check': self._get_safety_check(flag_type, severity),
                'resources': self._get_relevant_resources(flag_type),
                'grounding_technique': self._get_grounding_technique(flag_type),
                'follow_up': self._get_follow_up_guidance(flag_type, severity),
                'emergency_protocol': self._should_activate_emergency_protocol(severity),
                'response_tone': 'calm_supportive',
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Add specific guidance based on flag type
            if flag_type == RedFlagType.CRISIS.value:
                response_components['immediate_grounding'] = True
                response_components['breathing_exercise'] = self._grounding_techniques['breathing'][0]
            
            if severity == Severity.CRITICAL:
                response_components['urgent_action_required'] = True
                response_components['emergency_resources'] = self._resource_database['emergency']
            
            return response_components
            
        except Exception as e:
            logger.error(f"Failed to generate trauma-informed response: {str(e)}")
            return self._get_fallback_response()
    
    def _get_acknowledgment(self, flag_type: str) -> str:
        """Get acknowledgment response for flag type"""
        templates = self._response_templates.get(flag_type, {}).get('acknowledgment', [])
        if templates:
            return templates[0]  # Use first template for consistency
        return "I hear that you're going through a difficult time right now."
    
    def _get_validation(self, flag_type: str) -> str:
        """Get validation response for flag type"""
        templates = self._response_templates.get(flag_type, {}).get('validation', [])
        if templates:
            return templates[0]
        return "Your feelings are valid, and it's okay to reach out for support."
    
    def _get_safety_check(self, flag_type: str, severity: Severity) -> Optional[str]:
        """Get safety check question if appropriate"""
        if flag_type == RedFlagType.ABUSE.value or severity == Severity.CRITICAL:
            safety_checks = self._response_templates.get(flag_type, {}).get('safety_check', [])
            if safety_checks:
                return safety_checks[0]
            return "Are you in a safe place right now?"
        return None
    
    def _get_relevant_resources(self, flag_type: str) -> Dict[str, Any]:
        """Get relevant resources for flag type"""
        resource_mapping = {
            RedFlagType.SUICIDAL_IDEATION.value: ['crisis_helplines', 'emergency'],
            RedFlagType.SELF_HARM.value: ['self_harm', 'crisis_helplines'],
            RedFlagType.ABUSE.value: ['domestic_abuse', 'emergency'],
            RedFlagType.VIOLENCE.value: ['crisis_helplines'],
            RedFlagType.CRISIS.value: ['crisis_helplines', 'emergency']
        }
        
        relevant_categories = resource_mapping.get(flag_type, ['crisis_helplines'])
        resources = {}
        
        for category in relevant_categories:
            if category in self._resource_database:
                resources[category] = self._resource_database[category]
        
        return resources
    
    def _get_grounding_technique(self, flag_type: str) -> Optional[str]:
        """Get appropriate grounding technique"""
        if flag_type == RedFlagType.CRISIS.value:
            return self._grounding_techniques['breathing'][0]
        elif flag_type in [RedFlagType.SELF_HARM.value, RedFlagType.SUICIDAL_IDEATION.value]:
            return self._grounding_techniques['present_moment'][0]
        return None
    
    def _get_follow_up_guidance(self, flag_type: str, severity: Severity) -> str:
        """Get follow-up guidance"""
        if severity == Severity.CRITICAL:
            return "Please reach out to emergency services or a crisis helpline immediately. Your safety is the most important thing right now."
        elif severity == Severity.HIGH:
            return "I encourage you to speak with a mental health professional or trusted person as soon as possible."
        else:
            return "Consider reaching out to a counselor or support service when you feel ready."
    
    def _should_activate_emergency_protocol(self, severity: Severity) -> bool:
        """Determine if emergency protocol should be activated"""
        return severity == Severity.CRITICAL
    
    def _get_fallback_response(self) -> Dict[str, Any]:
        """Get fallback response for errors"""
        return {
            'acknowledgment': "I can see that you're reaching out for support, and I want to help.",
            'validation': "Your feelings matter, and it's important that you're talking about them.",
            'resources': self._resource_database['crisis_helplines'],
            'follow_up': "Please consider speaking with a mental health professional or calling a support helpline.",
            'response_tone': 'calm_supportive',
            'generated_at': datetime.utcnow().isoformat(),
            'error': 'Used fallback response due to processing error'
        }
    
    def format_response_for_ai_agent(self, response_components: Dict[str, Any]) -> str:
        """
        Format response components into a cohesive message for AI agent
        
        Args:
            response_components: Response components dictionary
            
        Returns:
            Formatted response string for AI agent to use
        """
        try:
            formatted_response = []
            
            # Start with acknowledgment
            if 'acknowledgment' in response_components:
                formatted_response.append(response_components['acknowledgment'])
            
            # Add validation
            if 'validation' in response_components:
                formatted_response.append(response_components['validation'])
            
            # Add safety check if present
            if response_components.get('safety_check'):
                formatted_response.append(response_components['safety_check'])
            
            # Add grounding technique if present
            if response_components.get('grounding_technique'):
                formatted_response.append("Let's take a moment to ground ourselves: " + 
                                        response_components['grounding_technique'])
            
            # Add resource information
            if 'resources' in response_components and response_components['resources']:
                formatted_response.append("Here are some resources that might help:")
                
                for category, resources in response_components['resources'].items():
                    for resource_key, resource_info in resources.items():
                        if 'phone' in resource_info:
                            formatted_response.append(f"• {resource_info['name']}: {resource_info['phone']}")
                        elif 'text' in resource_info:
                            formatted_response.append(f"• {resource_info['name']}: {resource_info['text']}")
                        elif 'website' in resource_info:
                            formatted_response.append(f"• {resource_info['name']}: {resource_info['website']}")
            
            # Add follow-up guidance
            if 'follow_up' in response_components:
                formatted_response.append(response_components['follow_up'])
            
            # Add emergency protocol if needed
            if response_components.get('emergency_protocol'):
                formatted_response.append("If you're in immediate danger, please call 999 or go to your nearest A&E.")
            
            # Add supportive closing
            formatted_response.append("You are not alone, and there are people who want to help you.")
            
            return " ".join(formatted_response)
            
        except Exception as e:
            logger.error(f"Failed to format response: {str(e)}")
            return ("I can see you're reaching out for support. Please consider contacting "
                   "Samaritans at 116 123 or emergency services at 999 if you're in immediate danger. "
                   "You are not alone.")
    
    def get_ai_system_prompt_guidance(self) -> str:
        """
        Get system prompt guidance for AI agent based on UKind principles
        
        Returns:
            System prompt guidance string
        """
        return """
You are a trauma-informed AI therapy assistant for survivors of domestic abuse, complex PTSD, and anxiety. 

CORE PRINCIPLES:
- Your tone is calm, validating, non-judgmental, and never forceful
- Avoid triggering language and acknowledge emotions softly
- Offer grounding, breathing exercises, and self-compassion prompts where needed
- You never offer clinical diagnosis, medical advice, or emergency interventions
- Always respect the user's autonomy and pace

IMPORTANT DISCLAIMERS:
- Clearly state that you are not a licensed therapist
- Emphasize that you can signpost to licensed therapists
- Make it clear that you cannot replace professional therapy

WHEN RED FLAGS ARE DETECTED:
- Gently respond with reassurance and validation
- Provide appropriate resources and support information
- Activate safeguarding protocols for human review
- Never attempt clinical intervention yourself

USE GROUNDING PHRASES:
- "You are safe here."
- "You are doing very well."
- "Let's take a deep breath together."
- "Would you like to pause or continue?"

LANGUAGE GUIDELINES:
- Use simple, clear language
- Avoid jargon and clinical terminology
- Avoid confrontation or challenging statements
- Always validate feelings before offering suggestions

EMERGENCY SITUATIONS:
- For immediate danger: Direct to 999 or emergency services
- For crisis support: Provide Samaritans (116 123) or Crisis Text Line (Text SHOUT to 85258)
- For domestic abuse: National Domestic Abuse Helpline (0808 2000 247)

Remember: You are creating a safe space for reflection and support, not providing therapy.
        """.strip()
    
    def validate_response_safety(self, response_text: str) -> Dict[str, Any]:
        """
        Validate that a response follows trauma-informed principles
        
        Args:
            response_text: Response text to validate
            
        Returns:
            Validation results dictionary
        """
        try:
            safety_issues = []
            
            # Check for potentially harmful phrases
            harmful_phrases = [
                'you should',
                'you must',
                'you need to',
                'just get over it',
                'it could be worse',
                'everything happens for a reason',
                'think positive',
                'snap out of it'
            ]
            
            response_lower = response_text.lower()
            for phrase in harmful_phrases:
                if phrase in response_lower:
                    safety_issues.append(f"Contains potentially harmful phrase: '{phrase}'")
            
            # Check for appropriate validation language
            validation_indicators = [
                'i hear',
                'i understand',
                'that sounds',
                'i can see',
                'it makes sense',
                'your feelings',
                'you are not alone'
            ]
            
            has_validation = any(indicator in response_lower for indicator in validation_indicators)
            
            # Check for resource provision in crisis responses
            has_resources = any(resource in response_lower for resource in [
                'samaritans', '116 123', '999', 'helpline', 'support'
            ])
            
            return {
                'is_safe': len(safety_issues) == 0,
                'safety_issues': safety_issues,
                'has_validation': has_validation,
                'has_resources': has_resources,
                'validation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to validate response safety: {str(e)}")
            return {
                'is_safe': False,
                'safety_issues': [f"Validation error: {str(e)}"],
                'validation_timestamp': datetime.utcnow().isoformat()
            }