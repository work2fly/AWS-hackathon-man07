"""
WebSocket Lambda Functions for AI Therapy Platform
Handles WebSocket connections, disconnections, and message routing
Breaking Barriers UK 2026 compliant
"""

import json
import logging
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError

from ..data.session_repository import session_repository
from ..data.user_repository import user_repository
from ..data.websocket_connection_repository import websocket_connection_repository
from ..services.cognito_service import cognito_service
from ..utils.logger import get_logger
from ..utils.validation import validate_json_message
from ..utils.websocket_security import websocket_security_manager

logger = get_logger(__name__)

# AWS clients
dynamodb = boto3.resource('dynamodb')
apigateway_management = None  # Will be initialized per request

# Environment variables
CONNECTIONS_TABLE_NAME = os.environ.get('CONNECTIONS_TABLE_NAME')
SESSIONS_TABLE_NAME = os.environ.get('SESSIONS_TABLE_NAME')
WEBSOCKET_API_ENDPOINT = os.environ.get('WEBSOCKET_API_ENDPOINT')

def get_apigateway_management_client(domain_name: str, stage: str):
    """Initialize API Gateway Management client for WebSocket operations"""
    global apigateway_management
    if not apigateway_management:
        apigateway_management = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url=f'https://{domain_name}/{stage}'
        )
    return apigateway_management

def create_response(status_code: int, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized WebSocket response"""
    response = {
        'statusCode': status_code
    }
    
    if body:
        response['body'] = json.dumps(body)
    
    return response

class WebSocketConnectionManager:
    """Manages WebSocket connections and session state"""
    
    def __init__(self):
        self.repository = websocket_connection_repository
    
    def store_connection(self, connection_id: str, user_id: str, 
                        session_id: Optional[str] = None) -> bool:
        """Store WebSocket connection in DynamoDB"""
        return self.repository.create_connection(connection_id, user_id, session_id)
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove WebSocket connection from DynamoDB"""
        return self.repository.remove_connection(connection_id)
    
    def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection details from DynamoDB"""
        return self.repository.get_connection(connection_id)
    
    def get_user_connections(self, user_id: str) -> list:
        """Get all connections for a user"""
        return self.repository.get_user_connections(user_id)
    
    def get_session_connections(self, session_id: str) -> list:
        """Get all connections for a session"""
        return self.repository.get_session_connections(session_id)
    
    def update_connection_session(self, connection_id: str, session_id: str) -> bool:
        """Update connection with session ID"""
        return self.repository.update_connection_session(connection_id, session_id)

# Global connection manager instance
connection_manager = WebSocketConnectionManager()

def authenticate_websocket_connection(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Authenticate WebSocket connection using security manager"""
    return websocket_security_manager.authenticate_connection(event)

def send_message_to_connection(connection_id: str, message: Dict[str, Any], 
                              domain_name: str, stage: str) -> bool:
    """Send message to specific WebSocket connection"""
    try:
        client = get_apigateway_management_client(domain_name, stage)
        
        client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message)
        )
        
        logger.info(f"Message sent to connection: {connection_id}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'GoneException':
            # Connection is stale, remove it
            logger.info(f"Removing stale connection: {connection_id}")
            connection_manager.remove_connection(connection_id)
        else:
            logger.error(f"Failed to send message to {connection_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending message to {connection_id}: {str(e)}")
        return False

def broadcast_to_session(session_id: str, message: Dict[str, Any], 
                        domain_name: str, stage: str, 
                        exclude_connection: Optional[str] = None) -> int:
    """Broadcast message to all connections in a session"""
    connections = connection_manager.get_session_connections(session_id)
    sent_count = 0
    
    for connection in connections:
        connection_id = connection['connectionId']
        
        # Skip excluded connection (e.g., sender)
        if exclude_connection and connection_id == exclude_connection:
            continue
        
        if send_message_to_connection(connection_id, message, domain_name, stage):
            sent_count += 1
    
    logger.info(f"Broadcast message to {sent_count} connections in session {session_id}")
    return sent_count

def connect_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle WebSocket $connect route
    Authenticates user and stores connection
    """
    try:
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        logger.info(f"WebSocket connection attempt: {connection_id}")
        
        # Authenticate the connection
        user_info = authenticate_websocket_connection(event)
        
        if not user_info:
            logger.warning(f"Authentication failed for connection: {connection_id}")
            return create_response(401, {'error': 'Authentication failed'})
        
        # Store the connection
        success = connection_manager.store_connection(
            connection_id=connection_id,
            user_id=user_info['user_id']
        )
        
        if not success:
            logger.error(f"Failed to store connection: {connection_id}")
            return create_response(500, {'error': 'Failed to store connection'})
        
        # Send welcome message
        welcome_message = {
            'type': 'connection_established',
            'message': 'WebSocket connection established successfully',
            'user_id': user_info['user_id'],
            'role': user_info['role'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        send_message_to_connection(connection_id, welcome_message, domain_name, stage)
        
        logger.info(f"WebSocket connection established for user: {user_info['user_id']}")
        return create_response(200)
        
    except Exception as e:
        logger.error(f"Connect handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def disconnect_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle WebSocket $disconnect route
    Cleans up connection and session state with graceful termination
    """
    try:
        connection_id = event['requestContext']['connectionId']
        
        logger.info(f"WebSocket disconnection: {connection_id}")
        
        # Get connection details before removing
        connection_info = connection_manager.get_connection(connection_id)
        
        if connection_info:
            user_id = connection_info.get('userId')
            session_id = connection_info.get('sessionId')
            
            # Log disconnection event
            websocket_security_manager._log_security_event('connection_disconnected', {
                'connection_id': connection_id,
                'user_id': user_id,
                'session_id': session_id
            })
            
            # If connection was part of a session, handle graceful session cleanup
            if session_id:
                # Check if this was the last connection for the session
                session_connections = connection_manager.get_session_connections(session_id)
                
                if len(session_connections) <= 1:  # Only this connection left
                    # Gracefully end the session
                    try:
                        session_repository.update_session_status(session_id, 'completed')
                        
                        # Store session end time
                        session_repository.update_item(
                            key={'sessionId': session_id, 'timestamp': connection_info.get('connectedAt', '')},
                            update_expression="SET endTime = :end_time, #status = :status",
                            expression_attribute_names={'#status': 'status'},
                            expression_attribute_values={
                                ':end_time': datetime.utcnow().isoformat(),
                                ':status': 'completed'
                            }
                        )
                        
                        logger.info(f"Session {session_id} gracefully ended due to last connection disconnect")
                        
                    except Exception as e:
                        logger.error(f"Error ending session {session_id}: {str(e)}")
                
                else:
                    # Notify other participants about disconnection
                    try:
                        domain_name = event['requestContext']['domainName']
                        stage = event['requestContext']['stage']
                        
                        participant_message = {
                            'type': 'participant_disconnected',
                            'session_id': session_id,
                            'user_id': user_id,
                            'timestamp': datetime.utcnow().isoformat(),
                            'message': 'A participant has disconnected'
                        }
                        
                        broadcast_to_session(session_id, participant_message, domain_name, stage, exclude_connection=connection_id)
                        
                    except Exception as e:
                        logger.error(f"Error notifying participants of disconnection: {str(e)}")
        
        # Remove the connection record
        connection_manager.remove_connection(connection_id)
        
        logger.info(f"WebSocket connection gracefully cleaned up: {connection_id}")
        return create_response(200)
        
    except Exception as e:
        logger.error(f"Disconnect handler error: {str(e)}")
        # Still try to clean up the connection even if there was an error
        try:
            connection_id = event['requestContext']['connectionId']
            connection_manager.remove_connection(connection_id)
        except:
            pass
        
        return create_response(500, {'error': 'Internal server error'})

def default_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle WebSocket $default route
    Routes messages based on message type
    """
    try:
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        # Parse message body
        body = event.get('body', '{}')
        if isinstance(body, str):
            message = json.loads(body)
        else:
            message = body
        
        logger.info(f"WebSocket message from {connection_id}: {message.get('type', 'unknown')}")
        
        # Validate message format
        if not validate_json_message(message):
            error_response = {
                'type': 'error',
                'error': 'Invalid message format',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(400, {'error': 'Invalid message format'})
        
        # Get connection info
        connection_info = connection_manager.get_connection(connection_id)
        
        if not connection_info:
            error_response = {
                'type': 'error',
                'error': 'Connection not found',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(404, {'error': 'Connection not found'})
        
        user_id = connection_info.get('userId')
        
        # Validate message security and rate limits
        security_valid, security_message = websocket_security_manager.validate_message_security(
            connection_id, user_id, message
        )
        
        if not security_valid:
            error_response = {
                'type': 'error',
                'error': f'Security validation failed: {security_message}',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(429, {'error': security_message})  # 429 Too Many Requests
        
        # Route message based on type
        message_type = message.get('type', '')
        
        if message_type == 'ping':
            return handle_ping_message(connection_id, message, domain_name, stage)
        elif message_type == 'join_session':
            return handle_join_session(connection_id, connection_info, message, domain_name, stage)
        elif message_type == 'leave_session':
            return handle_leave_session(connection_id, connection_info, message, domain_name, stage)
        elif message_type == 'audio_stream_init':
            return handle_audio_stream_init(connection_id, connection_info, message, domain_name, stage)
        elif message_type == 'audio_chunk':
            return handle_audio_chunk(connection_id, connection_info, message, domain_name, stage)
        elif message_type == 'audio_stream_pause':
            return handle_audio_stream_pause(connection_id, connection_info, message, domain_name, stage)
        elif message_type == 'audio_stream_resume':
            return handle_audio_stream_resume(connection_id, connection_info, message, domain_name, stage)
        elif message_type == 'audio_stream_close':
            return handle_audio_stream_close(connection_id, connection_info, message, domain_name, stage)
        elif message_type == 'session_message':
            return handle_session_message(connection_id, connection_info, message, domain_name, stage)
        else:
            error_response = {
                'type': 'error',
                'error': f'Unknown message type: {message_type}',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(400, {'error': f'Unknown message type: {message_type}'})
        
    except json.JSONDecodeError:
        error_response = {
            'type': 'error',
            'error': 'Invalid JSON in message body',
            'timestamp': datetime.utcnow().isoformat()
        }
        send_message_to_connection(connection_id, error_response, domain_name, stage)
        return create_response(400, {'error': 'Invalid JSON'})
    except Exception as e:
        logger.error(f"Default handler error: {str(e)}")
        error_response = {
            'type': 'error',
            'error': 'Internal server error',
            'timestamp': datetime.utcnow().isoformat()
        }
        send_message_to_connection(connection_id, error_response, domain_name, stage)
        return create_response(500, {'error': 'Internal server error'})

def handle_ping_message(connection_id: str, message: Dict[str, Any], 
                       domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle ping message for connection health monitoring"""
    pong_response = {
        'type': 'pong',
        'timestamp': datetime.utcnow().isoformat(),
        'original_timestamp': message.get('timestamp')
    }
    
    send_message_to_connection(connection_id, pong_response, domain_name, stage)
    return create_response(200)

def handle_join_session(connection_id: str, connection_info: Dict[str, Any], 
                       message: Dict[str, Any], domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle joining a therapy session"""
    try:
        session_id = message.get('session_id')
        user_id = connection_info['userId']
        
        if not session_id:
            error_response = {
                'type': 'error',
                'error': 'Missing session_id',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(400, {'error': 'Missing session_id'})
        
        # Verify session exists and user has access
        session_data = session_repository.get_session(session_id)
        
        if not session_data:
            error_response = {
                'type': 'error',
                'error': 'Session not found',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(404, {'error': 'Session not found'})
        
        # Check if user has access to this session
        if session_data.get('clientId') != user_id:
            # TODO: Add therapist/admin access check
            error_response = {
                'type': 'error',
                'error': 'Access denied to session',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(403, {'error': 'Access denied'})
        
        # Update connection with session ID
        connection_manager.update_connection_session(connection_id, session_id)
        
        # Send confirmation
        join_response = {
            'type': 'session_joined',
            'session_id': session_id,
            'message': 'Successfully joined session',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        send_message_to_connection(connection_id, join_response, domain_name, stage)
        
        # Notify other participants (if any)
        participant_message = {
            'type': 'participant_joined',
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        broadcast_to_session(session_id, participant_message, domain_name, stage, exclude_connection=connection_id)
        
        logger.info(f"User {user_id} joined session {session_id}")
        return create_response(200)
        
    except Exception as e:
        logger.error(f"Join session error: {str(e)}")
        error_response = {
            'type': 'error',
            'error': 'Failed to join session',
            'timestamp': datetime.utcnow().isoformat()
        }
        send_message_to_connection(connection_id, error_response, domain_name, stage)
        return create_response(500, {'error': 'Failed to join session'})

def handle_leave_session(connection_id: str, connection_info: Dict[str, Any], 
                        message: Dict[str, Any], domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle leaving a therapy session"""
    try:
        session_id = connection_info.get('sessionId')
        user_id = connection_info['userId']
        
        if not session_id:
            error_response = {
                'type': 'error',
                'error': 'Not in a session',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(400, {'error': 'Not in a session'})
        
        # Remove session from connection
        connection_manager.update_connection_session(connection_id, '')
        
        # Send confirmation
        leave_response = {
            'type': 'session_left',
            'session_id': session_id,
            'message': 'Successfully left session',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        send_message_to_connection(connection_id, leave_response, domain_name, stage)
        
        # Notify other participants
        participant_message = {
            'type': 'participant_left',
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        broadcast_to_session(session_id, participant_message, domain_name, stage, exclude_connection=connection_id)
        
        logger.info(f"User {user_id} left session {session_id}")
        return create_response(200)
        
    except Exception as e:
        logger.error(f"Leave session error: {str(e)}")
        error_response = {
            'type': 'error',
            'error': 'Failed to leave session',
            'timestamp': datetime.utcnow().isoformat()
        }
        send_message_to_connection(connection_id, error_response, domain_name, stage)
        return create_response(500, {'error': 'Failed to leave session'})

def handle_audio_stream_init(connection_id: str, connection_info: Dict[str, Any],
                           message: Dict[str, Any], domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle audio stream initialization"""
    try:
        from ..services.audio_streaming_service import audio_streaming_service, AudioStreamConfig, AudioQuality
        from ..models.websocket_messages import AudioStreamReadyMessage
        
        session_id = connection_info.get('sessionId')
        
        if not session_id:
            error_response = {
                'type': 'error',
                'error': 'Must join a session before initializing audio stream',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(400, {'error': 'Not in a session'})
        
        # Parse stream configuration
        config_data = message.get('config', {})
        quality = AudioQuality(config_data.get('quality', 'medium'))
        config = AudioStreamConfig.from_quality_preset(quality)
        
        # Initialize stream
        result = audio_streaming_service.initialize_stream(session_id, config)
        
        if result['success']:
            # Send ready confirmation
            ready_message = AudioStreamReadyMessage(
                session_id=session_id,
                config=result['config']
            )
            send_message_to_connection(connection_id, ready_message.dict(), domain_name, stage)
            
            logger.info(f"Audio stream initialized for session {session_id}")
            return create_response(200)
        else:
            error_response = {
                'type': 'error',
                'error': result.get('error', 'Failed to initialize audio stream'),
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(500, {'error': 'Stream initialization failed'})
        
    except Exception as e:
        logger.error(f"Audio stream init error: {str(e)}")
        error_response = {
            'type': 'error',
            'error': 'Failed to initialize audio stream',
            'timestamp': datetime.utcnow().isoformat()
        }
        send_message_to_connection(connection_id, error_response, domain_name, stage)
        return create_response(500, {'error': 'Stream initialization failed'})


def handle_audio_chunk(connection_id: str, connection_info: Dict[str, Any],
                      message: Dict[str, Any], domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle incoming audio chunk"""
    try:
        from ..services.audio_streaming_service import audio_streaming_service
        from ..models.websocket_messages import AudioChunkAckMessage, QualityMetricsMessage
        
        session_id = connection_info.get('sessionId')
        
        if not session_id:
            error_response = {
                'type': 'error',
                'error': 'Must join a session before sending audio',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(400, {'error': 'Not in a session'})
        
        # Process audio chunk
        result = audio_streaming_service.process_audio_chunk(session_id, message)
        
        if result['success']:
            # Send acknowledgment
            ack_message = AudioChunkAckMessage(
                session_id=session_id,
                chunk_id=result['chunk_id'],
                sequence_number=result['sequence_number'],
                buffer_fill=result['buffer_fill'],
                state=result['state']
            )
            send_message_to_connection(connection_id, ack_message.dict(), domain_name, stage)
            
            # Send quality metrics periodically (every 10 chunks)
            if result['sequence_number'] % 10 == 0:
                metrics_message = QualityMetricsMessage(
                    session_id=session_id,
                    metrics=result['metrics']
                )
                send_message_to_connection(connection_id, metrics_message.dict(), domain_name, stage)
            
            return create_response(200)
        else:
            error_response = {
                'type': 'error',
                'error': result.get('error', 'Failed to process audio chunk'),
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(500, {'error': 'Audio processing failed'})
        
    except Exception as e:
        logger.error(f"Audio chunk error: {str(e)}")
        error_response = {
            'type': 'error',
            'error': 'Failed to process audio chunk',
            'timestamp': datetime.utcnow().isoformat()
        }
        send_message_to_connection(connection_id, error_response, domain_name, stage)
        return create_response(500, {'error': 'Audio processing failed'})


def handle_audio_stream_pause(connection_id: str, connection_info: Dict[str, Any],
                             message: Dict[str, Any], domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle audio stream pause"""
    try:
        from ..services.audio_streaming_service import audio_streaming_service
        
        session_id = connection_info.get('sessionId')
        
        if not session_id:
            return create_response(400, {'error': 'Not in a session'})
        
        success = audio_streaming_service.pause_stream(session_id)
        
        if success:
            ack_response = {
                'type': 'ack',
                'message': 'Audio stream paused',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, ack_response, domain_name, stage)
            return create_response(200)
        else:
            return create_response(500, {'error': 'Failed to pause stream'})
        
    except Exception as e:
        logger.error(f"Audio stream pause error: {str(e)}")
        return create_response(500, {'error': 'Failed to pause stream'})


def handle_audio_stream_resume(connection_id: str, connection_info: Dict[str, Any],
                              message: Dict[str, Any], domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle audio stream resume"""
    try:
        from ..services.audio_streaming_service import audio_streaming_service
        
        session_id = connection_info.get('sessionId')
        
        if not session_id:
            return create_response(400, {'error': 'Not in a session'})
        
        success = audio_streaming_service.resume_stream(session_id)
        
        if success:
            ack_response = {
                'type': 'ack',
                'message': 'Audio stream resumed',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, ack_response, domain_name, stage)
            return create_response(200)
        else:
            return create_response(500, {'error': 'Failed to resume stream'})
        
    except Exception as e:
        logger.error(f"Audio stream resume error: {str(e)}")
        return create_response(500, {'error': 'Failed to resume stream'})


def handle_audio_stream_close(connection_id: str, connection_info: Dict[str, Any],
                             message: Dict[str, Any], domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle audio stream close"""
    try:
        from ..services.audio_streaming_service import audio_streaming_service
        
        session_id = connection_info.get('sessionId')
        
        if not session_id:
            return create_response(400, {'error': 'Not in a session'})
        
        success = audio_streaming_service.close_stream(session_id)
        
        if success:
            ack_response = {
                'type': 'ack',
                'message': 'Audio stream closed',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, ack_response, domain_name, stage)
            return create_response(200)
        else:
            return create_response(500, {'error': 'Failed to close stream'})
        
    except Exception as e:
        logger.error(f"Audio stream close error: {str(e)}")
        return create_response(500, {'error': 'Failed to close stream'})

def handle_session_message(connection_id: str, connection_info: Dict[str, Any], 
                          message: Dict[str, Any], domain_name: str, stage: str) -> Dict[str, Any]:
    """Handle general session messages"""
    try:
        session_id = connection_info.get('sessionId')
        user_id = connection_info['userId']
        
        if not session_id:
            error_response = {
                'type': 'error',
                'error': 'Must join a session before sending messages',
                'timestamp': datetime.utcnow().isoformat()
            }
            send_message_to_connection(connection_id, error_response, domain_name, stage)
            return create_response(400, {'error': 'Not in a session'})
        
        # Broadcast message to session participants
        session_message = {
            'type': 'session_message',
            'session_id': session_id,
            'user_id': user_id,
            'content': message.get('content', ''),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        broadcast_to_session(session_id, session_message, domain_name, stage)
        
        logger.info(f"Session message broadcast in {session_id}")
        return create_response(200)
        
    except Exception as e:
        logger.error(f"Session message error: {str(e)}")
        error_response = {
            'type': 'error',
            'error': 'Failed to send session message',
            'timestamp': datetime.utcnow().isoformat()
        }
        send_message_to_connection(connection_id, error_response, domain_name, stage)
        return create_response(500, {'error': 'Failed to send message'})

def monitor_connection_health(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Monitor WebSocket connection health and cleanup stale connections
    This function can be triggered by CloudWatch Events periodically
    """
    try:
        logger.info("Starting WebSocket connection health monitoring")
        
        # Get security statistics
        security_stats = websocket_security_manager.get_security_stats()
        logger.info(f"Security stats: {security_stats}")
        
        # Cleanup stale connections
        stale_count = websocket_connection_repository.cleanup_stale_connections(max_age_hours=2)
        logger.info(f"Cleaned up {stale_count} stale connections")
        
        # Get connection statistics
        connection_stats = websocket_connection_repository.get_connection_stats()
        logger.info(f"Connection stats: {connection_stats}")
        
        # Send metrics to CloudWatch
        import boto3
        cloudwatch = boto3.client('cloudwatch')
        
        metrics = [
            {
                'MetricName': 'ActiveConnections',
                'Value': connection_stats['total_active_connections'],
                'Unit': 'Count'
            },
            {
                'MetricName': 'UniqueUsers',
                'Value': connection_stats['unique_users'],
                'Unit': 'Count'
            },
            {
                'MetricName': 'ActiveSessions',
                'Value': connection_stats['unique_sessions'],
                'Unit': 'Count'
            },
            {
                'MetricName': 'StaleConnectionsCleanedUp',
                'Value': stale_count,
                'Unit': 'Count'
            }
        ]
        
        cloudwatch.put_metric_data(
            Namespace='AITherapyPlatform/WebSocket',
            MetricData=metrics
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Health monitoring completed',
                'security_stats': security_stats,
                'connection_stats': connection_stats,
                'stale_connections_cleaned': stale_count
            })
        }
        
    except Exception as e:
        logger.error(f"Connection health monitoring error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Health monitoring failed'})
        }