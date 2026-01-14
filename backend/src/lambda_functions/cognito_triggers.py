"""
Cognito Lambda Triggers for AI Therapy Platform
Simplified version - No external dependencies for reliable deployment
🏆 Breaking Barriers UK 2026 compliant
"""

import json
import logging
import re
from typing import Dict, Any

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def validate_email(email: str) -> bool:
    """Simple email validation"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def pre_sign_up_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Pre Sign-up Lambda trigger - Auto-confirm users"""
    try:
        logger.info(f"Pre sign-up trigger for user: {event['userName']}")
        
        # Get user attributes
        user_attributes = event['request']['userAttributes']
        email = user_attributes.get('email')
        
        # Validate email format
        if not validate_email(email):
            raise Exception("Invalid email format")
        
        # Auto-confirm user and email for hackathon (skip email verification)
        event['response']['autoConfirmUser'] = True
        event['response']['autoVerifyEmail'] = True
        
        logger.info(f"Pre sign-up validation passed and auto-confirmed for: {email}")
        
    except Exception as e:
        logger.error(f"Pre sign-up validation failed: {str(e)}")
        raise Exception(f"Registration validation failed: {str(e)}")
    
    return event

def post_confirmation_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Post Confirmation Lambda trigger - Log user confirmation"""
    try:
        logger.info(f"Post confirmation trigger for user: {event['userName']}")
        
        # Get user attributes
        user_attributes = event['request']['userAttributes']
        email = user_attributes.get('email')
        
        logger.info(f"User confirmed successfully: {email}")
        
    except Exception as e:
        logger.error(f"Post confirmation handler error: {str(e)}")
        # Don't raise exception here as it would prevent user confirmation
    
    return event

def pre_authentication_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Pre Authentication Lambda trigger - Allow all authenticated users"""
    try:
        logger.info(f"Pre authentication trigger for user: {event['userName']}")
        
        # For hackathon: allow all users to authenticate
        # In production: add additional checks here
        
        logger.info(f"Pre authentication validation passed for: {event['userName']}")
        
    except Exception as e:
        logger.error(f"Pre authentication validation failed: {str(e)}")
        # Don't block authentication for hackathon
        # raise Exception(f"Authentication validation failed: {str(e)}")
    
    return event

def post_authentication_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Post Authentication Lambda trigger - Log successful authentication"""
    try:
        logger.info(f"Post authentication trigger for user: {event['userName']}")
        
        # Log authentication event for audit
        logger.info(f"User authenticated successfully: {event['userName']}")
        
    except Exception as e:
        logger.error(f"Post authentication handler error: {str(e)}")
        # Don't raise exception as authentication already succeeded
    
    return event

def custom_message_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Custom Message Lambda trigger - Customize Cognito emails"""
    try:
        trigger_source = event['triggerSource']
        
        if trigger_source == 'CustomMessage_SignUp':
            # Customize signup verification email
            event['response']['emailSubject'] = 'Welcome to Ally - Verify Your Email'
            event['response']['emailMessage'] = f"""
            <html>
            <body>
                <h2>Welcome to Ally</h2>
                <p>Thank you for joining our secure therapy platform.</p>
                <p>Your verification code is: <strong>{event['request']['codeParameter']}</strong></p>
                <p>Please enter this code to complete your registration.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Ally Team</p>
            </body>
            </html>
            """
        
        elif trigger_source == 'CustomMessage_ForgotPassword':
            # Customize password reset email
            event['response']['emailSubject'] = 'Ally - Password Reset'
            event['response']['emailMessage'] = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested a password reset for your Ally account.</p>
                <p>Your verification code is: <strong>{event['request']['codeParameter']}</strong></p>
                <p>Use this code to reset your password.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Ally Team</p>
            </body>
            </html>
            """
        
        logger.info(f"Custom message generated for trigger: {trigger_source}")
        
    except Exception as e:
        logger.error(f"Custom message handler error: {str(e)}")
        # Use default message if custom message fails
    
    return event

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler that routes to appropriate trigger handler
    """
    try:
        trigger_source = event.get('triggerSource')
        
        logger.info(f"Cognito trigger received: {trigger_source}")
        logger.info(f"Event: {json.dumps(event, default=str)}")
        
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
        logger.error(f"Event: {json.dumps(event, default=str)}")
        raise e
