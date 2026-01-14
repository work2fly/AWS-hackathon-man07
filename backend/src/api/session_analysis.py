"""
Session Analysis API endpoints
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Dict, Any, List
from datetime import datetime
from ..services.session_analyzer import SessionAnalyzer
from ..utils.logger import get_logger

logger = get_logger(__name__)


def analyze_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for analyzing completed therapy sessions
    
    Expected event structure:
    {
        "user_id": "user123",
        "session_id": "session456",
        "messages": [
            {"role": "user", "content": "I'm feeling really anxious today..."},
            {"role": "assistant", "content": "I hear you..."},
            ...
        ]
    }
    """
    try:
        # Extract request data
        body = event.get('body', {})
        if isinstance(body, str):
            import json
            body = json.loads(body)
        
        user_id = body.get('user_id')
        session_id = body.get('session_id')
        messages = body.get('messages', [])
        
        # Validate input
        if not user_id or not session_id:
            return {
                'statusCode': 400,
                'body': {'error': 'user_id and session_id are required'}
            }
        
        if not messages:
            return {
                'statusCode': 400,
                'body': {'error': 'messages array is required'}
            }
        
        # Analyze session
        analyzer = SessionAnalyzer()
        result = analyzer.analyze_session(user_id, session_id, messages)
        
        if result['success']:
            logger.info(f"Session {session_id} analyzed successfully")
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Session analyzed successfully',
                    'updates_applied': result['updates_applied'],
                    'red_flags_created': result['red_flags_created'],
                    'analysis_summary': result['analysis_summary']
                }
            }
        else:
            logger.error(f"Session analysis failed: {result.get('error')}")
            return {
                'statusCode': 500,
                'body': {'error': result.get('error', 'Analysis failed')}
            }
    
    except Exception as e:
        logger.error(f"Session analysis handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }


def get_clinical_profile_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for retrieving user clinical profile (internal use only)
    
    Expected event structure:
    {
        "user_id": "user123"
    }
    """
    try:
        from ..data.user_repository import UserRepository
        
        # Extract user_id from path parameters or query string
        user_id = event.get('pathParameters', {}).get('user_id')
        if not user_id:
            user_id = event.get('queryStringParameters', {}).get('user_id')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': {'error': 'user_id is required'}
            }
        
        # Get user with clinical profile
        user_repo = UserRepository()
        user = user_repo.get_user(user_id)
        
        if not user:
            return {
                'statusCode': 404,
                'body': {'error': 'User not found'}
            }
        
        if not user.clinical_profile:
            return {
                'statusCode': 404,
                'body': {'error': 'Clinical profile not found'}
            }
        
        # Return clinical profile (internal use only - not exposed to user)
        return {
            'statusCode': 200,
            'body': {
                'user_id': user.user_id,
                'clinical_profile': {
                    'age': user.clinical_profile.age,
                    'gender': user.clinical_profile.gender,
                    'note_on_user': user.clinical_profile.note_on_user,
                    'medical_conditions': user.clinical_profile.medical_conditions,
                    'domestic_abuse_type': user.clinical_profile.domestic_abuse_type,
                    'emotional_state': user.clinical_profile.emotional_state,
                    'conversation_preference': user.clinical_profile.conversation_preference,
                    'self_harm_risk_signal': user.clinical_profile.self_harm_risk_signal,
                    'user_risk': user.clinical_profile.user_risk,
                    'last_session_timestamp': user.clinical_profile.last_session_timestamp.isoformat() if user.clinical_profile.last_session_timestamp else None,
                    'total_goals': user.clinical_profile.total_goals,
                    'goals_achieved': user.clinical_profile.goals_achieved
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Get clinical profile handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }


def update_goals_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for updating user goals
    
    Expected event structure:
    {
        "user_id": "user123",
        "total_goals": 5,
        "goals_achieved": 2
    }
    """
    try:
        from ..data.user_repository import UserRepository
        
        # Extract request data
        body = event.get('body', {})
        if isinstance(body, str):
            import json
            body = json.loads(body)
        
        user_id = body.get('user_id')
        total_goals = body.get('total_goals')
        goals_achieved = body.get('goals_achieved')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': {'error': 'user_id is required'}
            }
        
        # Build updates
        updates = {}
        if total_goals is not None:
            updates['total_goals'] = total_goals
        if goals_achieved is not None:
            updates['goals_achieved'] = goals_achieved
        
        if not updates:
            return {
                'statusCode': 400,
                'body': {'error': 'No updates provided'}
            }
        
        # Update clinical profile
        user_repo = UserRepository()
        success = user_repo.update_clinical_profile(user_id, updates)
        
        if success:
            return {
                'statusCode': 200,
                'body': {'message': 'Goals updated successfully'}
            }
        else:
            return {
                'statusCode': 500,
                'body': {'error': 'Failed to update goals'}
            }
    
    except Exception as e:
        logger.error(f"Update goals handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }


def get_sentiment_history_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for retrieving user sentiment score history
    Shows progress over time for doctors/therapists
    
    Expected event structure:
    {
        "client_id": "user123",
        "limit": 50  # optional
    }
    """
    try:
        from ..data.session_repository import SessionRepository
        
        # Extract client_id from path parameters or query string
        client_id = event.get('pathParameters', {}).get('client_id')
        if not client_id:
            client_id = event.get('queryStringParameters', {}).get('client_id')
        
        if not client_id:
            return {
                'statusCode': 400,
                'body': {'error': 'client_id is required'}
            }
        
        # Get optional limit
        limit = None
        query_params = event.get('queryStringParameters', {})
        if query_params and 'limit' in query_params:
            try:
                limit = int(query_params['limit'])
            except ValueError:
                pass
        
        # Get sentiment score history
        session_repo = SessionRepository()
        history = session_repo.get_sentiment_score_history(client_id, limit)
        
        if not history:
            return {
                'statusCode': 200,
                'body': {
                    'client_id': client_id,
                    'history': [],
                    'count': 0,
                    'message': 'No sentiment scores recorded yet'
                }
            }
        
        # Calculate statistics
        scores = [item['sentiment_score'] for item in history]
        avg_score = sum(scores) / len(scores)
        
        # Determine trend (comparing first half vs second half)
        if len(scores) >= 4:
            mid = len(scores) // 2
            first_half_avg = sum(scores[:mid]) / mid
            second_half_avg = sum(scores[mid:]) / (len(scores) - mid)
            
            if second_half_avg > first_half_avg + 0.5:
                trend = "improving"
            elif second_half_avg < first_half_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            'statusCode': 200,
            'body': {
                'client_id': client_id,
                'history': history,
                'count': len(history),
                'statistics': {
                    'average_score': round(avg_score, 2),
                    'latest_score': scores[-1] if scores else None,
                    'highest_score': max(scores) if scores else None,
                    'lowest_score': min(scores) if scores else None,
                    'trend': trend
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Get sentiment history handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }
