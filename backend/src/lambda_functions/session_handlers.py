"""
Session Management Lambda Handlers for AI Therapy Platform
Handles session lifecycle, state tracking, and metadata collection
🏆 Breaking Barriers UK 2026 compliant
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..services.session_service import SessionService
from ..services.session_security_service import SessionSecurityService
from ..models.session import AudioQualityMetrics, ConnectionMetrics
from ..middleware.auth_middleware import (
    require_role, therapist_or_admin, authenticated_user, get_user_from_event, admin_only
)
from ..utils.logger import get_logger
from ..utils.validation import validate_required_fields
from ..utils.response_formatter import success_response, error_response

logger = get_logger(__name__)
session_service = SessionService()
security_service = SessionSecurityService()


@require_role('client')
def create_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Create a new therapy session
    
    POST /sessions
    Body: {
        "agent_id": "string",
        "language": "string" (optional, defaults to "en")
    }
    """
    try:
        user_info = get_user_from_event(event)
        client_id = user_info['user_id']
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate required fields
        required_fields = ['agent_id']
        if not validate_required_fields(body, required_fields):
            return error_response(
                'Missing required fields',
                400,
                {'required': required_fields}
            )
        
        agent_id = body['agent_id']
        language = body.get('language', 'en')
        
        # Create session
        session = session_service.create_session(
            client_id=client_id,
            agent_id=agent_id,
            language=language
        )
        
        if session:
            response_data = {
                'session_id': session.session_id,
                'timestamp': session.timestamp.isoformat(),
                'client_id': session.client_id,
                'agent_id': session.agent_id,
                'status': session.status.value,
                'start_time': session.start_time.isoformat(),
                'language': session.language,
                'agent_memory_id': session.agent_memory_id
            }
            
            logger.info(f"Session {session.session_id} created for client {client_id}")
            return success_response(response_data, 201, 'Session created successfully')
        else:
            logger.error(f"Failed to create session for client {client_id}")
            return error_response('Failed to create session', 500)
    
    except json.JSONDecodeError:
        return error_response('Invalid JSON in request body', 400)
    except Exception as e:
        logger.error(f"Create session handler error: {str(e)}")
        return error_response('Internal server error', 500)


@require_role('client')
def update_session_state_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Update session state and metadata
    
    PUT /sessions/{session_id}/state
    Query params: timestamp (required)
    Body: {
        "audio_quality": {...} (optional),
        "connection_metrics": {...} (optional),
        "therapeutic_milestones": [...] (optional),
        "exercises_completed": [...] (optional)
    }
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get path parameters
        path_params = event.get('pathParameters', {})
        session_id = path_params.get('session_id')
        
        if not session_id:
            return create_response(400, {'error': 'Missing session_id parameter'})
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        timestamp = query_params.get('timestamp')
        
        if not timestamp:
            return create_response(400, {'error': 'Missing timestamp parameter'})
        
        # Verify session ownership
        session = session_service.get_session(session_id, timestamp)
        if not session:
            return create_response(404, {'error': 'Session not found'})
        
        if session.client_id != user_info['user_id']:
            return create_response(403, {'error': 'Access denied'})
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Collect metadata update
        success = session_service.collect_session_metadata(
            session_id=session_id,
            timestamp=timestamp,
            metadata_update=body
        )
        
        if success:
            return create_response(200, {'message': 'Session state updated successfully'})
        else:
            return create_response(500, {'error': 'Failed to update session state'})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Update session state handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@require_role('client')
def complete_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Complete a therapy session
    
    POST /sessions/{session_id}/complete
    Query params: timestamp (required)
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get path parameters
        path_params = event.get('pathParameters', {})
        session_id = path_params.get('session_id')
        
        if not session_id:
            return error_response('Missing session_id parameter', 400)
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        timestamp = query_params.get('timestamp')
        
        if not timestamp:
            return error_response('Missing timestamp parameter', 400)
        
        # Verify session ownership
        session = session_service.get_session(session_id, timestamp)
        if not session:
            return error_response('Session not found', 404)
        
        if session.client_id != user_info['user_id']:
            return error_response('Access denied', 403)
        
        # Complete session
        success = session_service.complete_session(session_id, timestamp)
        
        if success:
            return success_response({}, 200, 'Session completed successfully')
        else:
            return error_response('Failed to complete session', 500)
    
    except Exception as e:
        logger.error(f"Complete session handler error: {str(e)}")
        return error_response('Internal server error', 500)


@require_role('client')
def end_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    End a therapy session (alias for complete_session_handler)
    
    POST /sessions/{session_id}/end
    Query params: timestamp (required)
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get path parameters
        path_params = event.get('pathParameters', {})
        session_id = path_params.get('session_id')
        
        if not session_id:
            return error_response('Missing session_id parameter', 400)
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        timestamp = query_params.get('timestamp')
        
        if not timestamp:
            return error_response('Missing timestamp parameter', 400)
        
        # Verify session ownership
        session = session_service.get_session(session_id, timestamp)
        if not session:
            return error_response('Session not found', 404)
        
        if session.client_id != user_info['user_id']:
            return error_response('Access denied', 403)
        
        # Complete session
        success = session_service.complete_session(session_id, timestamp)
        
        if success:
            return success_response({}, 200, 'Session ended successfully')
        else:
            return error_response('Failed to end session', 500)
    
    except Exception as e:
        logger.error(f"End session handler error: {str(e)}")
        return error_response('Internal server error', 500)


@authenticated_user
def terminate_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Terminate a therapy session (emergency or user-initiated)
    
    POST /sessions/{session_id}/terminate
    Query params: timestamp (required)
    Body: {
        "reason": "string" (optional)
    }
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get path parameters
        path_params = event.get('pathParameters', {})
        session_id = path_params.get('session_id')
        
        if not session_id:
            return create_response(400, {'error': 'Missing session_id parameter'})
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        timestamp = query_params.get('timestamp')
        
        if not timestamp:
            return create_response(400, {'error': 'Missing timestamp parameter'})
        
        # Verify session access
        session = session_service.get_session(session_id, timestamp)
        if not session:
            return create_response(404, {'error': 'Session not found'})
        
        # Clients can only terminate their own sessions, therapists/admins can terminate any
        if user_info['role'] == 'client' and session.client_id != user_info['user_id']:
            return create_response(403, {'error': 'Access denied'})
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        reason = body.get('reason', 'user_terminated')
        
        # Terminate session
        success = session_service.terminate_session(session_id, timestamp, reason)
        
        if success:
            return create_response(200, {'message': 'Session terminated successfully'})
        else:
            return create_response(500, {'error': 'Failed to terminate session'})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Terminate session handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@authenticated_user
def get_client_sessions_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get sessions for a client
    
    GET /clients/{client_id}/sessions
    Query params: limit, start_date, end_date, exclusive_start_key
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get path parameters
        path_params = event.get('pathParameters', {})
        client_id = path_params.get('client_id')
        
        if not client_id:
            return create_response(400, {'error': 'Missing client_id parameter'})
        
        # Check authorization - clients can only see their own sessions
        if user_info['role'] == 'client' and client_id != user_info['user_id']:
            return create_response(403, {'error': 'Access denied'})
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        exclusive_start_key = query_params.get('exclusive_start_key')
        
        # Parse dates if provided
        start_date_obj = datetime.fromisoformat(start_date) if start_date else None
        end_date_obj = datetime.fromisoformat(end_date) if end_date else None
        
        # Parse exclusive start key if provided
        exclusive_start_key_obj = json.loads(exclusive_start_key) if exclusive_start_key else None
        
        # Get sessions
        result = session_service.get_client_sessions(
            client_id=client_id,
            limit=limit,
            start_date=start_date_obj,
            end_date=end_date_obj,
            exclusive_start_key=exclusive_start_key_obj
        )
        
        # Format sessions for response
        sessions_data = []
        for session in result['sessions']:
            session_data = {
                'session_id': session.session_id,
                'timestamp': session.timestamp.isoformat(),
                'status': session.status.value,
                'start_time': session.start_time.isoformat(),
                'language': session.language,
                'duration': session.duration,
                'therapeutic_milestones': session.metadata.therapeutic_milestones,
                'exercises_completed': session.metadata.exercises_completed
            }
            
            if session.end_time:
                session_data['end_time'] = session.end_time.isoformat()
            
            # Add sentiment summary for therapists and admins
            if user_info['role'] in ['therapist', 'admin'] and session.sentiment_summary:
                session_data['sentiment_summary'] = {
                    'overall_sentiment': session.sentiment_summary.overall_sentiment.value,
                    'risk_level': session.sentiment_summary.risk_level.value,
                    'key_topics': session.sentiment_summary.key_topics,
                    'generated_at': session.sentiment_summary.generated_at.isoformat()
                }
            
            sessions_data.append(session_data)
        
        response_data = {
            'sessions': sessions_data,
            'count': result['count'],
            'client_id': client_id
        }
        
        if result['last_evaluated_key']:
            response_data['last_evaluated_key'] = result['last_evaluated_key']
        
        return create_response(200, response_data)
    
    except ValueError as e:
        return create_response(400, {'error': f'Invalid date format: {str(e)}'})
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid exclusive_start_key format'})
    except Exception as e:
        logger.error(f"Get client sessions handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@therapist_or_admin
def get_active_sessions_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get all active sessions (therapists and admins only)
    
    GET /sessions/active
    Query params: limit
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 100)) if query_params.get('limit') else None
        
        # Get active sessions
        sessions = session_service.get_active_sessions(limit=limit)
        
        # Format sessions for response
        sessions_data = []
        for session in sessions:
            session_data = {
                'session_id': session.session_id,
                'timestamp': session.timestamp.isoformat(),
                'client_id': session.client_id,
                'agent_id': session.agent_id,
                'status': session.status.value,
                'start_time': session.start_time.isoformat(),
                'language': session.language,
                'therapeutic_milestones': session.metadata.therapeutic_milestones,
                'exercises_completed': session.metadata.exercises_completed
            }
            sessions_data.append(session_data)
        
        return success_response({
            'active_sessions': sessions_data,
            'count': len(sessions_data)
        })
    
    except Exception as e:
        logger.error(f"Get active sessions handler error: {str(e)}")
        return error_response('Internal server error', 500)


@admin_only
def list_sessions_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    List all sessions (admin only)
    
    GET /sessions
    Query params: limit, status, start_date, end_date
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50)) if query_params.get('limit') else 50
        status = query_params.get('status')
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        
        # Build search criteria
        search_criteria = {}
        if status:
            search_criteria['status'] = status
        if start_date:
            search_criteria['start_date'] = start_date
        if end_date:
            search_criteria['end_date'] = end_date
        
        # Search sessions
        result = session_service.search_sessions(search_criteria, limit)
        
        # Format sessions for response
        sessions_data = []
        for session in result['sessions']:
            session_data = {
                'session_id': session.session_id,
                'timestamp': session.timestamp.isoformat(),
                'client_id': session.client_id,
                'agent_id': session.agent_id,
                'status': session.status.value,
                'start_time': session.start_time.isoformat(),
                'language': session.language,
                'duration': session.duration,
                'therapeutic_milestones': session.metadata.therapeutic_milestones,
                'exercises_completed': session.metadata.exercises_completed
            }
            
            if session.end_time:
                session_data['end_time'] = session.end_time.isoformat()
            
            # Add sentiment summary for admins
            if session.sentiment_summary:
                session_data['sentiment_summary'] = {
                    'overall_sentiment': session.sentiment_summary.overall_sentiment.value,
                    'risk_level': session.sentiment_summary.risk_level.value,
                    'key_topics': session.sentiment_summary.key_topics,
                    'generated_at': session.sentiment_summary.generated_at.isoformat()
                }
            
            sessions_data.append(session_data)
        
        return success_response({
            'sessions': sessions_data,
            'count': result['count'],
            'total_scanned': result['total_scanned']
        })
    
    except ValueError:
        return error_response('Invalid parameter format', 400)
    except Exception as e:
        logger.error(f"List sessions handler error: {str(e)}")
        return error_response('Internal server error', 500)
        logger.error(f"Get active sessions handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@therapist_or_admin
def search_sessions_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Search sessions based on criteria
    
    POST /sessions/search
    Body: {
        "client_id": "string" (optional),
        "status": "string" (optional),
        "language": "string" (optional),
        "start_date": "string" (optional),
        "end_date": "string" (optional),
        "min_duration": number (optional),
        "max_duration": number (optional),
        "risk_level": "string" (optional),
        "sentiment": "string" (optional),
        "limit": number (optional)
    }
    """
    try:
        user_info = get_user_from_event(event)
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract search criteria
        search_criteria = {
            'client_id': body.get('client_id'),
            'status': body.get('status'),
            'language': body.get('language'),
            'start_date': body.get('start_date'),
            'end_date': body.get('end_date'),
            'min_duration': body.get('min_duration'),
            'max_duration': body.get('max_duration'),
            'risk_level': body.get('risk_level'),
            'sentiment': body.get('sentiment')
        }
        
        # Remove None values
        search_criteria = {k: v for k, v in search_criteria.items() if v is not None}
        
        limit = body.get('limit', 50)
        
        # Perform search
        result = session_service.search_sessions(search_criteria, limit)
        
        # Format sessions for response
        sessions_data = []
        for session in result['sessions']:
            session_data = {
                'session_id': session.session_id,
                'timestamp': session.timestamp.isoformat(),
                'client_id': session.client_id,
                'status': session.status.value,
                'start_time': session.start_time.isoformat(),
                'language': session.language,
                'duration': session.duration,
                'therapeutic_milestones': session.metadata.therapeutic_milestones,
                'exercises_completed': session.metadata.exercises_completed
            }
            
            if session.end_time:
                session_data['end_time'] = session.end_time.isoformat()
            
            # Add sentiment summary for therapists and admins
            if session.sentiment_summary:
                session_data['sentiment_summary'] = {
                    'overall_sentiment': session.sentiment_summary.overall_sentiment.value,
                    'risk_level': session.sentiment_summary.risk_level.value,
                    'key_topics': session.sentiment_summary.key_topics,
                    'generated_at': session.sentiment_summary.generated_at.isoformat()
                }
            
            sessions_data.append(session_data)
        
        return create_response(200, {
            'sessions': sessions_data,
            'count': result['count'],
            'search_criteria': result['search_criteria'],
            'total_scanned': result['total_scanned']
        })
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Search sessions handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@authenticated_user
def export_session_data_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Export session data for a client (GDPR compliance)
    
    POST /clients/{client_id}/sessions/export
    Body: {
        "format": "json" | "csv",
        "include_sentiment": boolean (optional),
        "start_date": "string" (optional),
        "end_date": "string" (optional)
    }
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get path parameters
        path_params = event.get('pathParameters', {})
        client_id = path_params.get('client_id')
        
        if not client_id:
            return create_response(400, {'error': 'Missing client_id parameter'})
        
        # Check authorization - clients can only export their own data
        if user_info['role'] == 'client' and client_id != user_info['user_id']:
            return create_response(403, {'error': 'Access denied'})
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        format_type = body.get('format', 'json')
        include_sentiment = body.get('include_sentiment', True)
        start_date = body.get('start_date')
        end_date = body.get('end_date')
        
        # Parse dates if provided
        start_date_obj = datetime.fromisoformat(start_date) if start_date else None
        end_date_obj = datetime.fromisoformat(end_date) if end_date else None
        
        # Export session data
        result = session_service.export_session_data(
            client_id=client_id,
            format=format_type,
            include_sentiment=include_sentiment,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        if result.get('success'):
            # For JSON format, return the data directly
            if format_type.lower() == 'json':
                return create_response(200, {
                    'export_data': result['data'],
                    'metadata': {
                        'format': result['format'],
                        'size_bytes': result['size_bytes'],
                        'client_id': result['client_id']
                    }
                })
            else:
                # For CSV format, return as downloadable content
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'text/csv',
                        'Content-Disposition': f'attachment; filename="sessions_{client_id}.csv"',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': result['data']
                }
        else:
            return create_response(500, {'error': result.get('error', 'Export failed')})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except ValueError as e:
        return create_response(400, {'error': f'Invalid date format: {str(e)}'})
    except Exception as e:
        logger.error(f"Export session data handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@therapist_or_admin
def get_session_statistics_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get session statistics and analytics
    
    GET /sessions/statistics
    Query params: client_id (optional), days (optional)
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        client_id = query_params.get('client_id')
        days = int(query_params.get('days', 30))
        
        # Check authorization for client-specific statistics
        if client_id and user_info['role'] == 'client' and client_id != user_info['user_id']:
            return create_response(403, {'error': 'Access denied'})
        
        # Get statistics
        stats = session_service.get_session_statistics(client_id=client_id, days=days)
        
        return create_response(200, stats)
    
    except ValueError:
        return create_response(400, {'error': 'Invalid days parameter'})
    except Exception as e:
        logger.error(f"Get session statistics handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@authenticated_user
def delete_user_session_data_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Delete all session data for a user (GDPR right to erasure)
    
    DELETE /clients/{client_id}/sessions
    Body: {
        "reason": "string" (optional)
    }
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get path parameters
        path_params = event.get('pathParameters', {})
        client_id = path_params.get('client_id')
        
        if not client_id:
            return create_response(400, {'error': 'Missing client_id parameter'})
        
        # Check authorization - clients can only delete their own data, admins can delete any
        if user_info['role'] == 'client' and client_id != user_info['user_id']:
            return create_response(403, {'error': 'Access denied'})
        elif user_info['role'] not in ['client', 'admin']:
            return create_response(403, {'error': 'Insufficient permissions'})
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        reason = body.get('reason', 'user_request')
        
        # Audit the deletion request
        security_service.audit_session_access(
            user_id=user_info['user_id'],
            user_role=user_info['role'],
            session_id=f"all_sessions_{client_id}",
            action='delete_user_data'
        )
        
        # Delete user session data
        result = security_service.delete_user_session_data(client_id, reason)
        
        if result.get('success'):
            return create_response(200, {
                'message': 'User session data deleted successfully',
                'sessions_deleted': result['sessions_deleted'],
                'total_sessions': result['total_sessions'],
                'client_id': client_id
            })
        else:
            return create_response(500, {'error': result.get('error', 'Deletion failed')})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Delete user session data handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@therapist_or_admin
def apply_data_retention_policy_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Apply data retention policy to sessions
    
    POST /sessions/retention-policy
    Body: {
        "retention_days": number (optional, default: 2555 = 7 years)
    }
    """
    try:
        user_info = get_user_from_event(event)
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        retention_days = body.get('retention_days', 2555)  # 7 years default
        
        # Audit the retention policy application
        security_service.audit_session_access(
            user_id=user_info['user_id'],
            user_role=user_info['role'],
            session_id='system_wide',
            action='apply_retention_policy'
        )
        
        # Apply retention policy
        result = security_service.apply_data_retention_policy(retention_days)
        
        if result.get('success'):
            return create_response(200, result)
        else:
            return create_response(500, {'error': result.get('error', 'Retention policy failed')})
    
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        logger.error(f"Apply data retention policy handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@therapist_or_admin
def create_privacy_report_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Create privacy compliance report
    
    GET /sessions/privacy-report
    Query params: client_id (optional)
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        client_id = query_params.get('client_id')
        
        # Check authorization for client-specific reports
        if client_id and user_info['role'] == 'client' and client_id != user_info['user_id']:
            return create_response(403, {'error': 'Access denied'})
        
        # Audit the privacy report request
        security_service.audit_session_access(
            user_id=user_info['user_id'],
            user_role=user_info['role'],
            session_id=client_id or 'system_wide',
            action='create_privacy_report'
        )
        
        # Create privacy report
        report = security_service.create_privacy_report(client_id)
        
        return create_response(200, report)
    
    except Exception as e:
        logger.error(f"Create privacy report handler error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


@authenticated_user
def get_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get session details with security filtering
    
    GET /sessions/{session_id}
    Query params: timestamp (required)
    """
    try:
        user_info = get_user_from_event(event)
        
        # Get path parameters
        path_params = event.get('pathParameters', {})
        session_id = path_params.get('session_id')
        
        if not session_id:
            return error_response('Missing session_id parameter', 400)
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        timestamp = query_params.get('timestamp')
        
        if not timestamp:
            return error_response('Missing timestamp parameter', 400)
        
        # Get session
        session = session_service.get_session(session_id, timestamp)
        
        if not session:
            return error_response('Session not found', 404)
        
        # Check access permission
        if not security_service.check_session_access_permission(
            user_info['user_id'], user_info['role'], session
        ):
            return error_response('Access denied', 403)
        
        # Audit session access
        security_service.audit_session_access(
            user_id=user_info['user_id'],
            user_role=user_info['role'],
            session_id=session_id,
            action='view_session'
        )
        
        # Filter session data based on user role
        filtered_data = security_service.filter_session_data_by_role(session, user_info['role'])
        
        return success_response(filtered_data)
    
    except Exception as e:
        logger.error(f"Get session handler error: {str(e)}")
        return error_response('Internal server error', 500)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler that routes to appropriate session endpoint
    """
    try:
        # Get HTTP method and path
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        logger.info(f"Session handler: {http_method} {path}")
        
        # Route to appropriate handler
        if path == '/sessions' and http_method == 'POST':
            return create_session_handler(event, context)
        elif path == '/sessions' and http_method == 'GET':
            return list_sessions_handler(event, context)
        elif path.startswith('/sessions/') and path.endswith('/state') and http_method == 'PUT':
            return update_session_state_handler(event, context)
        elif path.startswith('/sessions/') and path.endswith('/complete') and http_method == 'POST':
            return complete_session_handler(event, context)
        elif path.startswith('/sessions/') and path.endswith('/end') and http_method == 'POST':
            return end_session_handler(event, context)
        elif path.startswith('/sessions/') and path.endswith('/terminate') and http_method == 'POST':
            return terminate_session_handler(event, context)
        elif path.startswith('/sessions/') and http_method == 'GET' and not path.endswith('/sessions'):
            return get_session_handler(event, context)
        elif path.startswith('/clients/') and path.endswith('/sessions') and http_method == 'GET':
            return get_client_sessions_handler(event, context)
        elif path.startswith('/clients/') and path.endswith('/sessions') and http_method == 'DELETE':
            return delete_user_session_data_handler(event, context)
        elif path.startswith('/clients/') and path.endswith('/sessions/export') and http_method == 'POST':
            return export_session_data_handler(event, context)
        elif path == '/sessions/active' and http_method == 'GET':
            return get_active_sessions_handler(event, context)
        elif path == '/sessions/search' and http_method == 'POST':
            return search_sessions_handler(event, context)
        elif path == '/sessions/statistics' and http_method == 'GET':
            return get_session_statistics_handler(event, context)
        elif path == '/sessions/reports' and http_method == 'POST':
            return generate_session_report_handler(event, context)
        elif path == '/sessions/retention-policy' and http_method == 'POST':
            return apply_data_retention_policy_handler(event, context)
        elif path == '/sessions/privacy-report' and http_method == 'GET':
            return create_privacy_report_handler(event, context)
        else:
            return error_response('Endpoint not found', 404)
    
    except Exception as e:
        logger.error(f"Session handler routing error: {str(e)}")
        return error_response('Internal server error', 500)