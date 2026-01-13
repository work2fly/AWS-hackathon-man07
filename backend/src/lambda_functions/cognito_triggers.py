"""
Cognito Lambda Triggers for AI Therapy Platform
Handles user lifecycle events and custom authentication flows
Breaking Barriers UK 2026 compliant
"""

import json
import logging
from typing import Dict, Any

from ..utils.logger import get_logger
from ..utils.validation import validate_email
from ..data.user_repository import user_repository

logger = get_logger(__name__)

def pre_sign_up_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Pre Sign-up Lambda trigger
    Validates user registration and sets custom attributes
    
    Args:
        event: Cognito trigger event
        context: Lambda context
        
    Returns:
        Modified event with validation results
    """
    try:
        logger.info(f"Pre sign-up trigger for user: {event['userName']}")
        
        # Get user attributes
        user_attributes = event['request']['userAttributes']
        email = user_attributes.get('email')
        role = user_attributes.get('custom:role', 'client')
        
        # Validate email format
        if not validate_email(email):
            raise Exception("Invalid email format")
        
        # Validate role
        if role not in ['client', 'therapist', 'admin']:
            raise Exception("Invalid role specified")
        
        # Auto-confirm email for hackathon (in production, use proper verification)
        event['response']['autoConfirmUser'] = True
        event['response']['autoVerifyEmail'] = True
        
        logger.info(f"Pre sign-up validation passed for: {email}")
        
    except Exception as e:
        logger.error(f"Pre sign-up validation failed: {str(e)}")
        raise Exception(f"Registration validation failed: {str(e)}")
    
    return event

def post_confirmation_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Post Confirmation Lambda trigger
    Creates user record in DynamoDB after successful confirmation
    
    Args:
        event: Cognito trigger event
        context: Lambda context
        
    Returns:
        Event (unchanged)
    """
    try:
        logger.info(f"Post confirmation trigger for user: {event['userName']}")
        
        # Get user attributes
        user_attributes = event['request']['userAttributes']
        
        # Create user record in DynamoDB
        user_data = {
            'user_id': event['userName'],
            'email': user_attributes.get('email'),
            'role': user_attributes.get('custom:role', 'client'),
            'language_preference': user_attributes.get('custom:language_preference', 'en'),
            'profile': {
                'first_name': '',
                'last_name': '',
                'timezone': 'UTC',
                'phone_number': '',
                'emergency_contact': {}
            },
            'preferences': {
                'language': user_attributes.get('custom:language_preference', 'en'),
                'voice_settings': {
                    'speed': 1.0,
                    'pitch': 1.0,
                    'voice_id': 'default'
                },
                'notification_settings': {
                    'email_notifications': True,
                    'sms_notifications': False,
                    'push_notifications': True
                },
                'privacy_settings': {
                    'data_sharing': False,
                    'analytics': True,
                    'marketing': False
                }
            },
            'is_active': True,
            'mfa_enabled': False
        }
        
        # Save to DynamoDB
        result = user_repository.create_user(user_data)
        
        if result['success']:
            logger.info(f"User record created in DynamoDB for: {user_data['email']}")
        else:
            logger.error(f"Failed to create user record: {result.get('error')}")
        
    except Exception as e:
        logger.error(f"Post confirmation handler error: {str(e)}")
        # Don't raise exception here as it would prevent user confirmation
    
    return event

def pre_authentication_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Pre Authentication Lambda trigger
    Validates user before authentication
    
    Args:
        event: Cognito trigger event
        context: Lambda context
        
    Returns:
        Event (unchanged or with validation results)
    """
    try:
        logger.info(f"Pre authentication trigger for user: {event['userName']}")
        
        # Check if user is active in our system
        user_info = user_repository.get_user_by_email(event['userName'])
        
        if not user_info or not user_info.get('is_active', True):
            raise Exception("User account is inactive")
        
        logger.info(f"Pre authentication validation passed for: {event['userName']}")
        
    except Exception as e:
        logger.error(f"Pre authentication validation failed: {str(e)}")
        raise Exception(f"Authentication validation failed: {str(e)}")
    
    return event

def post_authentication_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Post Authentication Lambda trigger
    Updates user last login and audit logs
    
    Args:
        event: Cognito trigger event
        context: Lambda context
        
    Returns:
        Event (unchanged)
    """
    try:
        logger.info(f"Post authentication trigger for user: {event['userName']}")
        
        # Update last login timestamp
        user_repository.update_user_last_login(event['userName'])
        
        # Log authentication event for audit
        logger.info(f"User authenticated successfully: {event['userName']}")
        
    except Exception as e:
        logger.error(f"Post authentication handler error: {str(e)}")
        # Don't raise exception as authentication already succeeded
    
    return event

def custom_message_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Custom Message Lambda trigger
    Customizes email messages sent by Cognito
    
    Args:
        event: Cognito trigger event
        context: Lambda context
        
    Returns:
        Event with custom message
    """
    try:
        trigger_source = event['triggerSource']
        
        if trigger_source == 'CustomMessage_SignUp':
            # Customize signup verification email
            event['response']['emailSubject'] = 'Welcome to AI Therapy Platform - Verify Your Email'
            event['response']['emailMessage'] = f"""
            <html>
            <body>
                <h2>Welcome to AI Therapy Platform</h2>
                <p>Thank you for joining our secure therapy platform.</p>
                <p>Your verification code is: <strong>{event['request']['codeParameter']}</strong></p>
                <p>Please enter this code to complete your registration.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>AI Therapy Platform Team</p>
            </body>
            </html>
            """
        
        elif trigger_source == 'CustomMessage_ForgotPassword':
            # Customize password reset email
            event['response']['emailSubject'] = 'AI Therapy Platform - Password Reset'
            event['response']['emailMessage'] = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested a password reset for your AI Therapy Platform account.</p>
                <p>Your verification code is: <strong>{event['request']['codeParameter']}</strong></p>
                <p>Use this code to reset your password.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>AI Therapy Platform Team</p>
            </body>
            </html>
            """
        
        logger.info(f"Custom message generated for trigger: {trigger_source}")
        
    except Exception as e:
        logger.error(f"Custom message handler error: {str(e)}")
        # Use default message if custom message fails
    
    return event

# Lambda handler mapping for different triggers
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler that routes to appropriate trigger handler
    
    Args:
        event: Cognito trigger event
        context: Lambda context
        
    Returns:
        Event processed by appropriate handler
    """
    try:
        trigger_source = event.get('triggerSource')
        
        logger.info(f"Cognito trigger received: {trigger_source}")
        
        if trigger_source == 'PreSignUp_SignUp':
            return pre_sign_up_handler(event, context)
        elif trigger_source == 'PostConfirmation_ConfirmSignUp':
            return post_confirmation_handler(event, context)
        elif trigger_source == 'PreAuthentication_Authentication':
            return pre_authentication_handler(event, context)
        elif trigger_source == 'PostAuthentication_Authentication':
            return post_authentication_handler(event, context)
        elif trigger_source in ['CustomMessage_SignUp', 'CustomMessage_ForgotPassword']:
            return custom_message_handler(event, context)
        else:
            logger.warning(f"Unhandled trigger source: {trigger_source}")
            return event
    
    except Exception as e:
        logger.error(f"Cognito trigger handler error: {str(e)}")
        raise e