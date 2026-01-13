"""
Cognito Service for AI Therapy Platform
Handles user authentication, registration, and management
Breaking Barriers UK 2026 compliant
"""

import boto3
import json
import os
import logging
from typing import Dict, List, Optional, Tuple
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

from ..config.aws_config import aws_clients
from ..utils.logger import get_logger
from ..utils.validation import validate_email, validate_password

logger = get_logger(__name__)

# Environment variables
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
COGNITO_CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET')

class CognitoService:
    """Service for managing Cognito user operations"""
    
    def __init__(self):
        self.client = aws_clients.cognito_idp
        self.user_pool_id = COGNITO_USER_POOL_ID
        self.client_id = COGNITO_CLIENT_ID
        self.client_secret = COGNITO_CLIENT_SECRET
        
        if not all([self.user_pool_id, self.client_id]):
            raise ValueError("Missing required Cognito configuration")
    
    def register_user(self, email: str, password: str, role: str, 
                     language_preference: str = 'en') -> Dict:
        """
        Register a new user with email verification
        
        Args:
            email: User email address
            password: User password
            role: User role (client, therapist, admin)
            language_preference: Preferred language code
            
        Returns:
            Dict containing user registration result
        """
        try:
            # Validate inputs
            if not validate_email(email):
                raise ValueError("Invalid email format")
            
            if not validate_password(password):
                raise ValueError("Password does not meet requirements")
            
            if role not in ['client', 'therapist', 'admin']:
                raise ValueError("Invalid role specified")
            
            # Create user in Cognito
            response = self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'false'},
                    {'Name': 'custom:role', 'Value': role},
                    {'Name': 'custom:language_preference', 'Value': language_preference}
                ],
                TemporaryPassword=password,
                MessageAction='SUPPRESS',  # We'll handle verification ourselves
                DesiredDeliveryMediums=['EMAIL']
            )
            
            # Add user to appropriate group
            self.client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=email,
                GroupName=f"{role}s"  # clients, therapists, admins
            )
            
            # Set permanent password
            self.client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=email,
                Password=password,
                Permanent=True
            )
            
            logger.info(f"User registered successfully: {email} with role {role}")
            
            return {
                'success': True,
                'user_id': response['User']['Username'],
                'email': email,
                'role': role,
                'status': response['User']['UserStatus']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"Cognito registration error: {error_code} - {error_message}")
            
            if error_code == 'UsernameExistsException':
                return {'success': False, 'error': 'User already exists'}
            elif error_code == 'InvalidPasswordException':
                return {'success': False, 'error': 'Password does not meet requirements'}
            else:
                return {'success': False, 'error': f'Registration failed: {error_message}'}
        
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            return {'success': False, 'error': 'Registration failed'}
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """
        Authenticate user and return JWT tokens
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict containing authentication result and tokens
        """
        try:
            # Initiate authentication
            response = self.client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            # Get user attributes
            user_info = self.get_user_info(email)
            
            result = {
                'success': True,
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn'],
                'user_info': user_info
            }
            
            logger.info(f"User authenticated successfully: {email}")
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"Authentication error: {error_code} - {error_message}")
            
            if error_code == 'NotAuthorizedException':
                return {'success': False, 'error': 'Invalid credentials'}
            elif error_code == 'UserNotConfirmedException':
                return {'success': False, 'error': 'User email not verified'}
            elif error_code == 'UserNotFoundException':
                return {'success': False, 'error': 'User not found'}
            else:
                return {'success': False, 'error': f'Authentication failed: {error_message}'}
        
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            return {'success': False, 'error': 'Authentication failed'}
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh JWT tokens using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict containing new tokens
        """
        try:
            response = self.client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            return {
                'success': True,
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn']
            }
            
        except ClientError as e:
            logger.error(f"Token refresh error: {e.response['Error']['Code']}")
            return {'success': False, 'error': 'Token refresh failed'}
    
    def get_user_info(self, username: str) -> Dict:
        """
        Get user information from Cognito
        
        Args:
            username: Username (email)
            
        Returns:
            Dict containing user information
        """
        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            
            # Parse user attributes
            attributes = {}
            for attr in response['UserAttributes']:
                attributes[attr['Name']] = attr['Value']
            
            # Get user groups
            groups_response = self.client.admin_list_groups_for_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            
            groups = [group['GroupName'] for group in groups_response['Groups']]
            
            return {
                'username': response['Username'],
                'email': attributes.get('email'),
                'email_verified': attributes.get('email_verified') == 'true',
                'role': attributes.get('custom:role'),
                'language_preference': attributes.get('custom:language_preference', 'en'),
                'groups': groups,
                'status': response['UserStatus'],
                'enabled': response['Enabled'],
                'created_date': response['UserCreateDate'].isoformat(),
                'last_modified_date': response['UserLastModifiedDate'].isoformat()
            }
            
        except ClientError as e:
            logger.error(f"Error getting user info: {e.response['Error']['Code']}")
            return {}
    
    def update_user_attributes(self, username: str, attributes: Dict) -> bool:
        """
        Update user attributes
        
        Args:
            username: Username (email)
            attributes: Dict of attributes to update
            
        Returns:
            Boolean indicating success
        """
        try:
            # Convert attributes to Cognito format
            user_attributes = []
            for key, value in attributes.items():
                if key in ['role', 'language_preference']:
                    user_attributes.append({
                        'Name': f'custom:{key}',
                        'Value': str(value)
                    })
                else:
                    user_attributes.append({
                        'Name': key,
                        'Value': str(value)
                    })
            
            self.client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=user_attributes
            )
            
            logger.info(f"User attributes updated for: {username}")
            return True
            
        except ClientError as e:
            logger.error(f"Error updating user attributes: {e.response['Error']['Code']}")
            return False
    
    def change_user_group(self, username: str, old_role: str, new_role: str) -> bool:
        """
        Change user's role by updating group membership
        
        Args:
            username: Username (email)
            old_role: Current role
            new_role: New role
            
        Returns:
            Boolean indicating success
        """
        try:
            # Remove from old group
            if old_role:
                self.client.admin_remove_user_from_group(
                    UserPoolId=self.user_pool_id,
                    Username=username,
                    GroupName=f"{old_role}s"
                )
            
            # Add to new group
            self.client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=username,
                GroupName=f"{new_role}s"
            )
            
            # Update role attribute
            self.update_user_attributes(username, {'role': new_role})
            
            logger.info(f"User role changed from {old_role} to {new_role} for: {username}")
            return True
            
        except ClientError as e:
            logger.error(f"Error changing user group: {e.response['Error']['Code']}")
            return False
    
    def reset_password(self, username: str) -> Dict:
        """
        Initiate password reset for user
        
        Args:
            username: Username (email)
            
        Returns:
            Dict containing reset result
        """
        try:
            self.client.admin_reset_user_password(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            
            logger.info(f"Password reset initiated for: {username}")
            return {'success': True, 'message': 'Password reset email sent'}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Password reset error: {error_code}")
            
            if error_code == 'UserNotFoundException':
                return {'success': False, 'error': 'User not found'}
            else:
                return {'success': False, 'error': 'Password reset failed'}
    
    def delete_user(self, username: str) -> bool:
        """
        Delete user account (GDPR compliance)
        
        Args:
            username: Username (email)
            
        Returns:
            Boolean indicating success
        """
        try:
            self.client.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            
            logger.info(f"User deleted: {username}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting user: {e.response['Error']['Code']}")
            return False
    
    def enable_mfa(self, username: str) -> bool:
        """
        Enable MFA for user
        
        Args:
            username: Username (email)
            
        Returns:
            Boolean indicating success
        """
        try:
            self.client.admin_set_user_mfa_preference(
                UserPoolId=self.user_pool_id,
                Username=username,
                SoftwareTokenMfaSettings={
                    'Enabled': True,
                    'PreferredMfa': True
                }
            )
            
            logger.info(f"MFA enabled for: {username}")
            return True
            
        except ClientError as e:
            logger.error(f"Error enabling MFA: {e.response['Error']['Code']}")
            return False
    
    def verify_jwt_token(self, token: str) -> Dict:
        """
        Verify JWT token and extract user information
        
        Args:
            token: JWT access token
            
        Returns:
            Dict containing token verification result
        """
        try:
            response = self.client.get_user(AccessToken=token)
            
            # Parse user attributes
            attributes = {}
            for attr in response['UserAttributes']:
                attributes[attr['Name']] = attr['Value']
            
            return {
                'valid': True,
                'username': response['Username'],
                'email': attributes.get('email'),
                'role': attributes.get('custom:role'),
                'language_preference': attributes.get('custom:language_preference', 'en')
            }
            
        except ClientError as e:
            logger.error(f"Token verification error: {e.response['Error']['Code']}")
            return {'valid': False, 'error': 'Invalid token'}

# Global Cognito service instance
cognito_service = CognitoService()