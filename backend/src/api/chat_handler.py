"""
Chat handler for AI therapy sessions
🏆 Breaking Barriers UK 2026 compliant
"""

import boto3
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from ..data.session_repository import SessionRepository
from ..data.user_repository import UserRepository
from ..models.session import TherapySession, SessionStatus
from ..security.api_security import secure_handler, SecurityHeaders
from ..security.rate_limiter import rate_limit_handler, RateLimiter
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Bedrock client (us-west-2 region as per hackathon rules)
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

# Get agent configuration from environment variables
# DO NOT set AWS_REGION manually - it's automatically provided by Lambda
AGENT_ID = os.environ.get('BEDROCK_AGENT_ID')
AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID')


@secure_handler
@rate_limit_handler('chat')
def chat_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for chat messages
    
    Expected event structure:
    {
        "body": {
            "user_id": "user123",
            "session_id": "session456",  # Optional - creates new if not provided
            "message": "I'm feeling anxious today",
            "create_session": true  # Optional - for first message
        }
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {
            "session_id": "session456",
            "user_message": "I'm feeling anxious today",
            "ai_response": "I hear you. Can you tell me more...",
            "timestamp": "2026-01-14T10:30:00Z"
        }
    }
    """
    try:
        # Parse request body
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)
        
        user_id = body.get('user_id')
        session_id = body.get('session_id')
        message = body.get('message')
        create_session = body.get('create_session', False)
        
        # Validate required fields
        if not user_id or not message:
            logger.warning(f"Missing required fields: user_id={user_id}, message={bool(message)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Configure CORS as needed
                },
                'body': json.dumps({'error': 'user_id and message are required'})
            }
        
        # Get user information for context
        user_repo = UserRepository()
        user = user_repo.get_user(user_id)
        
        if not user:
            logger.error(f"User not found: {user_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'User not found'})
            }
        
        # Create new session if needed
        session_repo = SessionRepository()
        if create_session or not session_id:
            session_id = f"session_{user_id}_{int(datetime.utcnow().timestamp())}"
            timestamp = datetime.utcnow()
            
            # Create session record in DynamoDB
            session = TherapySession(
                session_id=session_id,
                timestamp=timestamp,
                client_id=user_id,
                agent_id=AGENT_ID,
                agent_memory_id=f"mem_{session_id}",  # Bedrock will use this
                status=SessionStatus.ACTIVE
            )
            
            success = session_repo.create_session(session)
            if not success:
                logger.error(f"Failed to create session: {session_id}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Failed to create session'})
                }
            
            logger.info(f"Created new session: {session_id} for user: {user_id}")
        
        # Build context from clinical profile (internal use - not shown to user)
        context_info = ""
        if user.clinical_profile:
            context_info = f"""
            Internal context (do not mention directly to user):
            - Current emotional state: {user.clinical_profile.emotional_state}
            - Risk level: {user.clinical_profile.user_risk}
            - Self-harm risk: {user.clinical_profile.self_harm_risk_signal}
            - Conversation preference: {user.clinical_profile.conversation_preference}
            - Goals progress: {user.clinical_profile.goals_achieved}/{user.clinical_profile.total_goals}
            
            Use this context to:
            - Tailor your responses appropriately
            - Watch for concerning patterns
            - Provide relevant coping strategies
            - Escalate if risk increases
            """
        
        # Invoke Bedrock Agent
        # Note: Stay below 1 RPS to avoid throttling (hackathon constraint)
        try:
            response = bedrock_agent_runtime.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId=session_id,  # Bedrock uses this to maintain conversation context
                inputText=message,
                sessionState={
                    'sessionAttributes': {
                        'user_id': user_id,
                        'user_name': user.profile.first_name,
                        'context': context_info
                    }
                }
            )
        except Exception as bedrock_error:
            logger.error(f"Bedrock invocation failed: {str(bedrock_error)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'AI service temporarily unavailable',
                    'details': str(bedrock_error)
                })
            }
        
        # Parse agent response (streaming format)
        ai_response = ""
        for event_chunk in response.get('completion', []):
            if 'chunk' in event_chunk:
                chunk = event_chunk['chunk']
                if 'bytes' in chunk:
                    ai_response += chunk['bytes'].decode('utf-8')
        
        # Log the interaction (for monitoring)
        logger.info(f"Chat interaction - Session: {session_id}, User message length: {len(message)}, AI response length: {len(ai_response)}")
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'session_id': session_id,
                'user_message': message,
                'ai_response': ai_response,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
    
    except Exception as e:
        logger.error(f"Chat handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


@secure_handler
def end_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for ending a therapy session
    
    Expected event structure:
    {
        "body": {
            "user_id": "user123",
            "session_id": "session456"
        }
    }
    
    This will:
    1. Mark session as completed in DynamoDB
    2. Calculate session duration
    3. Trigger session analysis (sentiment score, clinical profile update)
    """
    try:
        # Parse request body
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)
        
        user_id = body.get('user_id')
        session_id = body.get('session_id')
        
        if not user_id or not session_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'user_id and session_id are required'})
            }
        
        # Get session from DynamoDB
        session_repo = SessionRepository()
        sessions_result = session_repo.get_sessions_by_client(user_id, limit=100)
        
        # Find the specific session
        session = None
        for s in sessions_result['sessions']:
            if s.session_id == session_id:
                session = s
                break
        
        if not session:
            logger.error(f"Session not found: {session_id} for user: {user_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Session not found'})
            }
        
        # Calculate session duration
        end_time = datetime.utcnow()
        duration = int((end_time - session.start_time).total_seconds())
        
        # Update session status to completed
        success = session_repo.update_session_status(
            session_id=session_id,
            timestamp=session.timestamp.isoformat(),
            status=SessionStatus.COMPLETED,
            end_time=end_time,
            duration=duration
        )
        
        if not success:
            logger.error(f"Failed to update session status: {session_id}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Failed to end session'})
            }
        
        logger.info(f"Session ended: {session_id}, Duration: {duration}s")
        
        # Trigger session analysis asynchronously
        # In production, this would invoke another Lambda or use EventBridge
        # For now, we'll return success and analysis happens separately
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Session ended successfully',
                'session_id': session_id,
                'duration': duration,
                'duration_formatted': f"{duration // 60}m {duration % 60}s"
            })
        }
    
    except Exception as e:
        logger.error(f"End session handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


@secure_handler
def get_conversation_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for retrieving conversation history from Bedrock
    (Internal use only - for analysis and review)
    
    Expected event structure:
    {
        "pathParameters": {
            "session_id": "session456"
        }
    }
    """
    try:
        # Get session_id from path
        session_id = event.get('pathParameters', {}).get('session_id')
        
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'session_id is required'})
            }
        
        # Retrieve conversation from Bedrock Agent memory
        # Note: This is a simplified example - actual implementation depends on
        # how you're storing conversation history in Bedrock
        
        try:
            # Get agent memory
            response = bedrock_agent_runtime.retrieve_and_generate(
                input={
                    'text': 'Retrieve conversation history'
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': 'your-kb-id',
                        'modelArn': f'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-sonnet-4-5-v2:0'
                    }
                },
                sessionId=session_id
            )
            
            # Parse conversation
            conversation = response.get('output', {}).get('text', '')
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'session_id': session_id,
                    'conversation': conversation
                })
            }
            
        except Exception as bedrock_error:
            logger.error(f"Failed to retrieve conversation: {str(bedrock_error)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Failed to retrieve conversation',
                    'details': str(bedrock_error)
                })
            }
    
    except Exception as e:
        logger.error(f"Get conversation handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
