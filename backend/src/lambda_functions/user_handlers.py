"""
User Management Lambda Handlers
Provides REST API endpoints for user operations
🏆 Breaking Barriers UK 2026 compliant
"""

import json
from typing import Dict, Any
from datetime import datetime

from data.user_repository import UserRepository
from data.session_repository import SessionRepository
from utils.response_formatter import success_response, error_response
from middleware.auth_middleware import require_auth, is_user_authorized_for_resource, get_user_from_event
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize repositories
user_repository = UserRepository()
session_repository = SessionRepository()


@require_auth()
def get_user_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /users/{userId}
    Get user details from DynamoDB
    
    Requirements: 4.1, 4.4
    """
    try:
        # Extract user ID from path parameters
        path_params = event.get('pathParameters', {})
        user_id = path_params.get('userId')
        
        if not user_id:
            logger.warning("Missing userId in path parameters")
            return error_response("Missing userId parameter", 400)
        
        # Get authenticated user info
        auth_user = get_user_from_event(event)
        
        # Authorization check: users can only access their own data unless admin/therapist
        if not is_user_authorized_for_resource(auth_user, user_id):
            logger.warning(f"User {auth_user.get('user_id')} attempted to access user {user_id}")
            return error_response("Access denied", 403)
        
        # Retrieve user from DynamoDB
        user_item = user_repository.get_item({'userId': user_id})
        
        if not user_item:
            logger.info(f"User not found: {user_id}")
            return error_response("User not found", 404)
        
        # Format user data for response
        user_data = {
            'userId': user_item.get('userId'),
            'email': user_item.get('email'),
            'role': user_item.get('role'),
            'profile': user_item.get('profile', {}),
            'preferences': user_item.get('preferences', {}),
            'isActive': user_item.get('isActive', True),
            'mfaEnabled': user_item.get('mfaEnabled', False),
            'languagePreference': user_item.get('languagePreference', 'en'),
            'createdAt': user_item.get('createdAt'),
            'updatedAt': user_item.get('updatedAt'),
            'lastLoginAt': user_item.get('lastLoginAt')
        }
        
        logger.info(f"Successfully retrieved user: {user_id}")
        return success_response(user_data)
    
    except Exception as e:
        logger.error(f"Error in get_user_handler: {str(e)}")
        return error_response("Internal server error", 500)


@require_auth()
def update_user_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    PUT /users/{userId}
    Update user information in DynamoDB
    
    Requirements: 4.2, 4.5
    """
    try:
        # Extract user ID from path parameters
        path_params = event.get('pathParameters', {})
        user_id = path_params.get('userId')
        
        if not user_id:
            logger.warning("Missing userId in path parameters")
            return error_response("Missing userId parameter", 400)
        
        # Get authenticated user info
        auth_user = get_user_from_event(event)
        
        # Authorization check: users can only update their own data unless admin
        if not is_user_authorized_for_resource(auth_user, user_id):
            logger.warning(f"User {auth_user.get('user_id')} attempted to update user {user_id}")
            return error_response("Access denied", 403)
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in request body")
            return error_response("Invalid JSON in request body", 400)
        
        # Validate that user exists
        existing_user = user_repository.get_item({'userId': user_id})
        if not existing_user:
            logger.info(f"User not found: {user_id}")
            return error_response("User not found", 404)
        
        # Build update expression dynamically based on provided fields
        update_parts = []
        expression_values = {}
        expression_names = {}
        
        # Always update the updatedAt timestamp
        update_parts.append("#updatedAt = :updatedAt")
        expression_names["#updatedAt"] = "updatedAt"
        expression_values[":updatedAt"] = datetime.utcnow().isoformat()
        
        # Update profile if provided
        if 'profile' in body:
            update_parts.append("#profile = :profile")
            expression_names["#profile"] = "profile"
            expression_values[":profile"] = body['profile']
        
        # Update preferences if provided
        if 'preferences' in body:
            update_parts.append("preferences = :preferences")
            expression_values[":preferences"] = body['preferences']
        
        # Update language preference if provided
        if 'languagePreference' in body:
            update_parts.append("languagePreference = :languagePreference")
            expression_values[":languagePreference"] = body['languagePreference']
        
        # Admin-only fields
        if auth_user.get('role') == 'admin':
            if 'isActive' in body:
                update_parts.append("isActive = :isActive")
                expression_values[":isActive"] = body['isActive']
            
            if 'mfaEnabled' in body:
                update_parts.append("mfaEnabled = :mfaEnabled")
                expression_values[":mfaEnabled"] = body['mfaEnabled']
        
        # Perform update
        update_expression = "SET " + ", ".join(update_parts)
        
        success = user_repository.update_item(
            key={'userId': user_id},
            update_expression=update_expression,
            expression_attribute_values=expression_values,
            expression_attribute_names=expression_names if expression_names else None,
            condition_expression="attribute_exists(userId)"
        )
        
        if not success:
            logger.error(f"Failed to update user: {user_id}")
            return error_response("Failed to update user", 500)
        
        # Retrieve updated user data
        updated_user = user_repository.get_item({'userId': user_id})
        
        user_data = {
            'userId': updated_user.get('userId'),
            'email': updated_user.get('email'),
            'role': updated_user.get('role'),
            'profile': updated_user.get('profile', {}),
            'preferences': updated_user.get('preferences', {}),
            'isActive': updated_user.get('isActive', True),
            'mfaEnabled': updated_user.get('mfaEnabled', False),
            'languagePreference': updated_user.get('languagePreference', 'en'),
            'updatedAt': updated_user.get('updatedAt')
        }
        
        logger.info(f"Successfully updated user: {user_id}")
        return success_response(user_data, message="User updated successfully")
    
    except Exception as e:
        logger.error(f"Error in update_user_handler: {str(e)}")
        return error_response("Internal server error", 500)


@require_auth()
def get_user_sessions_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    GET /users/{userId}/sessions
    Get all sessions for a specific user
    
    Requirements: 4.3, 4.4
    """
    try:
        # Extract user ID from path parameters
        path_params = event.get('pathParameters', {})
        user_id = path_params.get('userId')
        
        if not user_id:
            logger.warning("Missing userId in path parameters")
            return error_response("Missing userId parameter", 400)
        
        # Get authenticated user info
        auth_user = get_user_from_event(event)
        
        # Authorization check: users can only access their own sessions unless admin/therapist
        if not is_user_authorized_for_resource(auth_user, user_id):
            logger.warning(f"User {auth_user.get('user_id')} attempted to access sessions for user {user_id}")
            return error_response("Access denied", 403)
        
        # Get query parameters for pagination
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        
        # Query sessions using ClientIndex GSI
        response = session_repository.query(
            key_condition_expression="GSI1PK = :userId",
            expression_attribute_values={":userId": user_id},
            index_name="ClientIndex",
            limit=limit,
            scan_index_forward=False  # Most recent first
        )
        
        # Format session data
        sessions = []
        for item in response.get('Items', []):
            session_data = {
                'sessionId': item.get('sessionId'),
                'userId': item.get('userId'),
                'therapistId': item.get('therapistId'),
                'status': item.get('status'),
                'startTime': item.get('startTime'),
                'endTime': item.get('endTime'),
                'duration': item.get('duration'),
                'timestamp': item.get('timestamp'),
                'metadata': item.get('metadata', {})
            }
            
            # Include sentiment summary if available (therapist/admin only)
            if auth_user.get('role') in ['therapist', 'admin']:
                if 'sentimentSummary' in item:
                    session_data['sentimentSummary'] = item['sentimentSummary']
            
            sessions.append(session_data)
        
        result = {
            'sessions': sessions,
            'count': len(sessions),
            'lastEvaluatedKey': response.get('LastEvaluatedKey')
        }
        
        logger.info(f"Successfully retrieved {len(sessions)} sessions for user: {user_id}")
        return success_response(result)
    
    except Exception as e:
        logger.error(f"Error in get_user_sessions_handler: {str(e)}")
        return error_response("Internal server error", 500)
