"""
Amazon Nova Sonic 2 Configuration for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant

Handles Nova Sonic 2 client setup, authentication, session management,
and error handling with retry logic for real-time audio therapy sessions.

Requirements: 2.3, 2.4
"""

import boto3
import os
import time
import logging
from typing import Optional, Dict, Any, Tuple
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class NovaSessionStatus(Enum):
    """Nova Sonic 2 session status states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATED = "terminated"
    ERROR = "error"


class NovaRetryStrategy:
    """Retry strategy configuration for Nova Sonic 2 operations"""
    
    # Retry configuration
    MAX_RETRIES = 3
    BASE_DELAY = 1.0  # seconds
    MAX_DELAY = 10.0  # seconds
    EXPONENTIAL_BASE = 2
    
    # Retryable error codes
    RETRYABLE_ERRORS = {
        'ThrottlingException',
        'ServiceUnavailable',
        'InternalServerError',
        'RequestTimeout',
        'TooManyRequestsException',
    }
    
    @classmethod
    def should_retry(cls, error: Exception, attempt: int) -> bool:
        """
        Determine if an error should trigger a retry
        
        Args:
            error: The exception that occurred
            attempt: Current retry attempt number (0-indexed)
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= cls.MAX_RETRIES:
            return False
        
        if isinstance(error, ClientError):
            error_code = error.response.get('Error', {}).get('Code', '')
            return error_code in cls.RETRYABLE_ERRORS
        
        # Retry on network-related boto errors
        if isinstance(error, BotoCoreError):
            return True
        
        return False
    
    @classmethod
    def get_delay(cls, attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter
        
        Args:
            attempt: Current retry attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        import random
        
        delay = min(
            cls.BASE_DELAY * (cls.EXPONENTIAL_BASE ** attempt),
            cls.MAX_DELAY
        )
        
        # Add jitter (±25%)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        return max(0.1, delay + jitter)


class NovaSonicConfig:
    """
    Configuration manager for Amazon Nova Sonic 2 client
    
    Handles authentication, session management, and connection configuration
    for real-time audio therapy sessions.
    """
    
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    
    # Nova Sonic 2 Configuration
    MODEL_ID = "amazon.nova-sonic-2"  # Latest Nova Sonic 2 model
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE = 16000  # 16kHz for speech
    AUDIO_CHANNELS = 1  # Mono audio
    AUDIO_FORMAT = "pcm"  # PCM format for real-time streaming
    
    # Session Configuration
    SESSION_TIMEOUT = 3600  # 1 hour max session duration
    IDLE_TIMEOUT = 300  # 5 minutes idle timeout
    
    # Performance Configuration
    MAX_LATENCY_MS = 200  # Target latency for real-time conversation
    BUFFER_SIZE = 4096  # Audio buffer size in bytes
    
    # Rate Limiting (Breaking Barriers UK 2026 constraint)
    MAX_REQUESTS_PER_SECOND = 0.9  # Stay below 1 RPS limit
    
    def __init__(self):
        """Initialize Nova Sonic 2 configuration"""
        self._validate_environment()
        self._bedrock_client = None
        self._bedrock_runtime_client = None
    
    def _validate_environment(self):
        """Validate required environment variables and configuration"""
        if not self.AWS_REGION:
            raise ValueError("AWS_DEFAULT_REGION environment variable not set")
        
        # Validate region is permitted for hackathon
        if self.AWS_REGION not in ['us-west-2', 'us-east-1']:
            logger.warning(
                f"Region {self.AWS_REGION} may not be permitted. "
                "Use us-west-2 or us-east-1 for Breaking Barriers UK 2026"
            )
    
    @property
    def bedrock_client(self):
        """
        Get or create Bedrock client for model management
        
        Returns:
            boto3 Bedrock client
        """
        if self._bedrock_client is None:
            retry_config = Config(
                region_name=self.AWS_REGION,
                retries={
                    'max_attempts': NovaRetryStrategy.MAX_RETRIES,
                    'mode': 'adaptive'
                },
                connect_timeout=5,
                read_timeout=60
            )
            
            self._bedrock_client = boto3.client(
                'bedrock',
                config=retry_config
            )
            
            logger.info(f"Initialized Bedrock client in region {self.AWS_REGION}")
        
        return self._bedrock_client
    
    @property
    def bedrock_runtime_client(self):
        """
        Get or create Bedrock Runtime client for inference
        
        Returns:
            boto3 Bedrock Runtime client
        """
        if self._bedrock_runtime_client is None:
            retry_config = Config(
                region_name=self.AWS_REGION,
                retries={
                    'max_attempts': NovaRetryStrategy.MAX_RETRIES,
                    'mode': 'adaptive'
                },
                connect_timeout=5,
                read_timeout=60
            )
            
            self._bedrock_runtime_client = boto3.client(
                'bedrock-runtime',
                config=retry_config
            )
            
            logger.info(
                f"Initialized Bedrock Runtime client in region {self.AWS_REGION}"
            )
        
        return self._bedrock_runtime_client
    
    def get_therapeutic_system_prompt(
        self,
        language: str = "en",
        approach: Optional[str] = None,
        context: Optional[str] = None,
        cultural_context: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Get therapeutic system prompt for Nova Sonic 2 using the prompt service
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
            approach: Optional therapeutic approach
            context: Optional conversation context
            cultural_context: Optional cultural context
            client_id: Optional client ID for A/B testing
            
        Returns:
            Tuple of (prompt text, selection metadata)
        """
        try:
            from ..services.therapeutic_prompt_service import (
                therapeutic_prompt_service,
                PromptSelectionCriteria,
                TherapeuticApproach,
                ConversationContext,
                CulturalContext
            )
            
            # Parse enums from strings
            therapeutic_approach = (
                TherapeuticApproach(approach) if approach
                else TherapeuticApproach.PERSON_CENTERED
            )
            
            conversation_context = (
                ConversationContext(context) if context
                else ConversationContext.ONGOING_SESSION
            )
            
            cultural_ctx = (
                CulturalContext(cultural_context) if cultural_context
                else CulturalContext.NEUTRAL
            )
            
            # Create selection criteria
            criteria = PromptSelectionCriteria(
                approach=therapeutic_approach,
                context=conversation_context,
                language=language,
                cultural_context=cultural_ctx
            )
            
            # Select prompt
            prompt_version, metadata = therapeutic_prompt_service.select_prompt(
                criteria=criteria,
                client_id=client_id,
                enable_ab_testing=True
            )
            
            return prompt_version.prompt_text, metadata
            
        except Exception as e:
            logger.error(f"Failed to get prompt from service: {str(e)}, using fallback")
            # Fallback to simple prompt
            return self._get_fallback_prompt(language), {'error': str(e)}
    
    def _get_fallback_prompt(self, language: str = "en") -> str:
        """Fallback prompt if service unavailable"""
        base_prompt = """You are a compassionate, qualified AI therapist providing mental health support. 
Your role is to:
- Listen actively and empathetically to clients
- Provide evidence-based therapeutic guidance
- Maintain professional boundaries
- Recognize and respond to emotional distress
- Encourage healthy coping mechanisms
- Never provide medical diagnoses or prescriptions
- Escalate serious concerns (self-harm, suicidal ideation) appropriately

Communication style:
- Use warm, supportive language
- Ask open-ended questions
- Validate emotions and experiences
- Provide psychoeducation when appropriate
- Maintain cultural sensitivity
- Adapt to the client's communication style

Safety guidelines:
- Never encourage harmful behaviors
- Recognize red flags (self-harm, suicide, abuse)
- Maintain confidentiality within legal limits
- Provide crisis resources when needed"""
        
        # Language-specific adaptations
        language_notes = {
            "es": "\n\nCommunicate in Spanish with culturally appropriate expressions and therapeutic approaches for Spanish-speaking clients.",
            "fr": "\n\nCommunicate in French with culturally appropriate expressions and therapeutic approaches for French-speaking clients.",
            "de": "\n\nCommunicate in German with culturally appropriate expressions and therapeutic approaches for German-speaking clients.",
        }
        
        if language in language_notes:
            base_prompt += language_notes[language]
        
        return base_prompt
    
    def create_session_config(
        self,
        session_id: str,
        client_id: str,
        language: str = "en",
        custom_prompt: Optional[str] = None,
        approach: Optional[str] = None,
        context: Optional[str] = None,
        cultural_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create session configuration for Nova Sonic 2
        
        Args:
            session_id: Unique session identifier
            client_id: Client user ID
            language: Preferred language code
            custom_prompt: Optional custom system prompt override
            approach: Optional therapeutic approach
            context: Optional conversation context
            cultural_context: Optional cultural context
            
        Returns:
            Session configuration dictionary
        """
        # Get therapeutic prompt
        if custom_prompt:
            system_prompt = custom_prompt
            prompt_metadata = {'custom': True}
        else:
            system_prompt, prompt_metadata = self.get_therapeutic_system_prompt(
                language=language,
                approach=approach,
                context=context,
                cultural_context=cultural_context,
                client_id=client_id
            )
        
        return {
            "session_id": session_id,
            "client_id": client_id,
            "model_id": self.MODEL_ID,
            "language": language,
            "system_prompt": system_prompt,
            "prompt_metadata": prompt_metadata,
            "audio_config": {
                "sample_rate": self.AUDIO_SAMPLE_RATE,
                "channels": self.AUDIO_CHANNELS,
                "format": self.AUDIO_FORMAT,
                "buffer_size": self.BUFFER_SIZE
            },
            "performance_config": {
                "max_latency_ms": self.MAX_LATENCY_MS,
                "max_requests_per_second": self.MAX_REQUESTS_PER_SECOND
            },
            "timeout_config": {
                "session_timeout": self.SESSION_TIMEOUT,
                "idle_timeout": self.IDLE_TIMEOUT
            },
            "status": NovaSessionStatus.INITIALIZING.value,
            "created_at": time.time()
        }


class NovaSonicClient:
    """
    Client for Amazon Nova Sonic 2 speech-to-speech AI model
    
    Handles authentication, session management, error handling,
    and retry logic for real-time audio therapy sessions.
    """
    
    def __init__(self, config: Optional[NovaSonicConfig] = None):
        """
        Initialize Nova Sonic 2 client
        
        Args:
            config: Optional NovaSonicConfig instance
        """
        self.config = config or NovaSonicConfig()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._last_request_time = 0.0
        
        logger.info("Nova Sonic 2 client initialized")
    
    def _enforce_rate_limit(self):
        """
        Enforce rate limiting to stay below 1 RPS
        (Breaking Barriers UK 2026 constraint)
        """
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        min_interval = 1.0 / self.config.MAX_REQUESTS_PER_SECOND
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping {sleep_time:.3f}s")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _execute_with_retry(
        self,
        operation: callable,
        operation_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute an operation with retry logic
        
        Args:
            operation: Callable to execute
            operation_name: Name for logging
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Operation result
            
        Raises:
            Exception: If all retries exhausted
        """
        last_error = None
        
        for attempt in range(NovaRetryStrategy.MAX_RETRIES + 1):
            try:
                # Enforce rate limiting before each attempt
                self._enforce_rate_limit()
                
                # Execute operation
                result = operation(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(
                        f"{operation_name} succeeded on attempt {attempt + 1}"
                    )
                
                return result
                
            except Exception as error:
                last_error = error
                
                if not NovaRetryStrategy.should_retry(error, attempt):
                    logger.error(
                        f"{operation_name} failed after {attempt + 1} attempts: {error}"
                    )
                    raise
                
                delay = NovaRetryStrategy.get_delay(attempt)
                logger.warning(
                    f"{operation_name} failed (attempt {attempt + 1}), "
                    f"retrying in {delay:.2f}s: {error}"
                )
                time.sleep(delay)
        
        # Should not reach here, but just in case
        raise last_error
    
    def create_session(
        self,
        session_id: str,
        client_id: str,
        language: str = "en",
        custom_prompt: Optional[str] = None,
        approach: Optional[str] = None,
        context: Optional[str] = None,
        cultural_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Nova Sonic 2 therapy session
        
        Args:
            session_id: Unique session identifier
            client_id: Client user ID
            language: Preferred language code
            custom_prompt: Optional custom system prompt
            approach: Optional therapeutic approach
            context: Optional conversation context
            cultural_context: Optional cultural context
            
        Returns:
            Session configuration dictionary
            
        Raises:
            ValueError: If session already exists
            ClientError: If AWS API call fails
        """
        if session_id in self._active_sessions:
            raise ValueError(f"Session {session_id} already exists")
        
        def _create():
            # Create session configuration
            session_config = self.config.create_session_config(
                session_id=session_id,
                client_id=client_id,
                language=language,
                custom_prompt=custom_prompt,
                approach=approach,
                context=context,
                cultural_context=cultural_context
            )
            
            # Verify model access (this validates authentication)
            try:
                self.config.bedrock_client.get_foundation_model(
                    modelIdentifier=self.config.MODEL_ID
                )
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code == 'ResourceNotFoundException':
                    logger.warning(
                        f"Model {self.config.MODEL_ID} not found. "
                        "This may be expected if Nova Sonic 2 is not yet available."
                    )
                else:
                    raise
            
            # Store session
            session_config["status"] = NovaSessionStatus.ACTIVE.value
            self._active_sessions[session_id] = session_config
            
            logger.info(
                f"Created Nova Sonic 2 session {session_id} "
                f"for client {client_id} in language {language}"
            )
            
            return session_config
        
        return self._execute_with_retry(
            _create,
            f"create_session({session_id})"
        )
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session configuration
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session configuration or None if not found
        """
        return self._active_sessions.get(session_id)
    
    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate a Nova Sonic 2 session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was terminated, False if not found
        """
        session = self._active_sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found for termination")
            return False
        
        session["status"] = NovaSessionStatus.TERMINATED.value
        session["terminated_at"] = time.time()
        
        # Remove from active sessions
        del self._active_sessions[session_id]
        
        logger.info(f"Terminated Nova Sonic 2 session {session_id}")
        return True
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active sessions
        
        Returns:
            Dictionary of active sessions
        """
        return self._active_sessions.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Nova Sonic 2 client
        
        Returns:
            Health status dictionary
        """
        try:
            # Test Bedrock connectivity
            self.config.bedrock_client.list_foundation_models(
                byProvider="Amazon"
            )
            
            return {
                "status": "healthy",
                "region": self.config.AWS_REGION,
                "model_id": self.config.MODEL_ID,
                "active_sessions": len(self._active_sessions),
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }


# Global Nova Sonic 2 client instance
nova_sonic_client = NovaSonicClient()
