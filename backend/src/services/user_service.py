"""
User service with validation and business logic
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from ..data.user_repository import UserRepository
from ..models.user import User, UserRole, UserProfile, UserPreferences
from ..utils.validation import DataValidator, ValidationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user operations with validation and business logic"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.validator = DataValidator()
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user with validation"""
        try:
            # Sanitize input data
            sanitized_data = self.validator.sanitize_user_input(user_data)
            
            # Validate data
            validation_errors = self.validator.validate_user_data(sanitized_data)
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors,
                    'user': None
                }
            
            # Check if user already exists
            existing_user = self.user_repository.get_user_by_email(sanitized_data['email'])
            if existing_user:
                return {
                    'success': False,
                    'errors': {'email': ['User with this email already exists']},
                    'user': None
                }
            
            # Generate user ID if not provided
            if 'user_id' not in sanitized_data or not sanitized_data['user_id']:
                sanitized_data['user_id'] = str(uuid.uuid4())
            
            # Create User object
            user = User(
                user_id=sanitized_data['user_id'],
                email=sanitized_data['email'],
                role=UserRole(sanitized_data['role']),
                profile=UserProfile(**sanitized_data.get('profile', {})),
                preferences=UserPreferences(**sanitized_data.get('preferences', {})),
                language_preference=sanitized_data.get('language_preference', 'en')
            )
            
            # Save to database
            success = self.user_repository.create_user(user)
            
            if success:
                logger.info(f"Successfully created user {user.user_id}")
                return {
                    'success': True,
                    'errors': {},
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'errors': {'general': ['Failed to create user']},
                    'user': None
                }
                
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {
                'success': False,
                'errors': {'general': [f'Internal error: {str(e)}']},
                'user': None
            }
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID with validation"""
        try:
            if not self.validator.validate_user_id(user_id):
                logger.warning(f"Invalid user ID format: {user_id}")
                return None
            
            return self.user_repository.get_user_by_id(user_id)
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email with validation"""
        try:
            if not self.validator.validate_email(email):
                logger.warning(f"Invalid email format: {email}")
                return None
            
            return self.user_repository.get_user_by_email(email.lower().strip())
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user with validation"""
        try:
            # Get existing user
            user = self.get_user(user_id)
            if not user:
                return {
                    'success': False,
                    'errors': {'user_id': ['User not found']},
                    'user': None
                }
            
            # Sanitize input data
            sanitized_data = self.validator.sanitize_user_input(update_data)
            
            # Validate update data
            validation_errors = {}
            
            # Validate profile updates
            if 'profile' in sanitized_data:
                profile_data = sanitized_data['profile']
                for field, value in profile_data.items():
                    if field in ['first_name', 'last_name'] and value:
                        if not self.validator.validate_string_length(value, 1, 50):
                            validation_errors.setdefault(f'profile.{field}', []).append(f"{field} must be 1-50 characters")
                    elif field == 'phone_number' and value:
                        if not self.validator.validate_phone_number(value):
                            validation_errors.setdefault('profile.phone_number', []).append("Invalid phone number format")
            
            # Validate language preference
            if 'language_preference' in sanitized_data and sanitized_data['language_preference']:
                if not self.validator.validate_language_code(sanitized_data['language_preference']):
                    validation_errors.setdefault('language_preference', []).append("Invalid language code format")
            
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors,
                    'user': None
                }
            
            # Update user object
            if 'profile' in sanitized_data:
                for field, value in sanitized_data['profile'].items():
                    if hasattr(user.profile, field):
                        setattr(user.profile, field, value)
            
            if 'preferences' in sanitized_data:
                for field, value in sanitized_data['preferences'].items():
                    if hasattr(user.preferences, field):
                        setattr(user.preferences, field, value)
            
            if 'language_preference' in sanitized_data:
                user.language_preference = sanitized_data['language_preference']
            
            if 'is_active' in sanitized_data:
                user.is_active = bool(sanitized_data['is_active'])
            
            if 'mfa_enabled' in sanitized_data:
                user.mfa_enabled = bool(sanitized_data['mfa_enabled'])
            
            # Save updates
            success = self.user_repository.update_user(user)
            
            if success:
                logger.info(f"Successfully updated user {user_id}")
                return {
                    'success': True,
                    'errors': {},
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'errors': {'general': ['Failed to update user']},
                    'user': None
                }
                
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return {
                'success': False,
                'errors': {'general': [f'Internal error: {str(e)}']},
                'user': None
            }
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete user (GDPR compliance)"""
        try:
            if not self.validator.validate_user_id(user_id):
                return {
                    'success': False,
                    'errors': {'user_id': ['Invalid user ID format']},
                    'deleted': False
                }
            
            # Check if user exists
            user = self.get_user(user_id)
            if not user:
                return {
                    'success': False,
                    'errors': {'user_id': ['User not found']},
                    'deleted': False
                }
            
            # Delete user
            success = self.user_repository.delete_user(user_id)
            
            if success:
                logger.info(f"Successfully deleted user {user_id}")
                return {
                    'success': True,
                    'errors': {},
                    'deleted': True
                }
            else:
                return {
                    'success': False,
                    'errors': {'general': ['Failed to delete user']},
                    'deleted': False
                }
                
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            return {
                'success': False,
                'errors': {'general': [f'Internal error: {str(e)}']},
                'deleted': False
            }
    
    def list_users_by_role(self, role: str, limit: Optional[int] = None, 
                          page_token: Optional[str] = None) -> Dict[str, Any]:
        """List users by role with pagination"""
        try:
            # Validate role
            valid_roles = ['client', 'therapist', 'admin']
            if role not in valid_roles:
                return {
                    'success': False,
                    'errors': {'role': [f'Role must be one of: {", ".join(valid_roles)}']},
                    'users': [],
                    'next_page_token': None
                }
            
            # Parse page token (base64 encoded last_evaluated_key)
            exclusive_start_key = None
            if page_token:
                try:
                    import base64
                    import json
                    exclusive_start_key = json.loads(base64.b64decode(page_token).decode())
                except Exception:
                    logger.warning(f"Invalid page token: {page_token}")
            
            # Get users
            result = self.user_repository.list_users_by_role(
                role=UserRole(role),
                limit=limit,
                exclusive_start_key=exclusive_start_key
            )
            
            # Generate next page token
            next_page_token = None
            if result['last_evaluated_key']:
                import base64
                import json
                next_page_token = base64.b64encode(
                    json.dumps(result['last_evaluated_key']).encode()
                ).decode()
            
            return {
                'success': True,
                'errors': {},
                'users': result['users'],
                'count': result['count'],
                'next_page_token': next_page_token
            }
            
        except Exception as e:
            logger.error(f"Error listing users by role {role}: {str(e)}")
            return {
                'success': False,
                'errors': {'general': [f'Internal error: {str(e)}']},
                'users': [],
                'next_page_token': None
            }
    
    def activate_user(self, user_id: str) -> Dict[str, Any]:
        """Activate user account"""
        try:
            success = self.user_repository.update_user_status(user_id, True)
            
            if success:
                logger.info(f"Successfully activated user {user_id}")
                return {
                    'success': True,
                    'errors': {},
                    'activated': True
                }
            else:
                return {
                    'success': False,
                    'errors': {'general': ['Failed to activate user']},
                    'activated': False
                }
                
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {str(e)}")
            return {
                'success': False,
                'errors': {'general': [f'Internal error: {str(e)}']},
                'activated': False
            }
    
    def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Deactivate user account"""
        try:
            success = self.user_repository.update_user_status(user_id, False)
            
            if success:
                logger.info(f"Successfully deactivated user {user_id}")
                return {
                    'success': True,
                    'errors': {},
                    'deactivated': True
                }
            else:
                return {
                    'success': False,
                    'errors': {'general': ['Failed to deactivate user']},
                    'deactivated': False
                }
                
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {str(e)}")
            return {
                'success': False,
                'errors': {'general': [f'Internal error: {str(e)}']},
                'deactivated': False
            }
    
    def enable_mfa(self, user_id: str) -> Dict[str, Any]:
        """Enable MFA for user"""
        try:
            success = self.user_repository.enable_mfa(user_id)
            
            if success:
                logger.info(f"Successfully enabled MFA for user {user_id}")
                return {
                    'success': True,
                    'errors': {},
                    'mfa_enabled': True
                }
            else:
                return {
                    'success': False,
                    'errors': {'general': ['Failed to enable MFA']},
                    'mfa_enabled': False
                }
                
        except Exception as e:
            logger.error(f"Error enabling MFA for user {user_id}: {str(e)}")
            return {
                'success': False,
                'errors': {'general': [f'Internal error: {str(e)}']},
                'mfa_enabled': False
            }
    
    def update_language_preference(self, user_id: str, language: str) -> Dict[str, Any]:
        """Update user language preference"""
        try:
            # Validate language code
            if not self.validator.validate_language_code(language):
                return {
                    'success': False,
                    'errors': {'language': ['Invalid language code format']},
                    'updated': False
                }
            
            success = self.user_repository.update_language_preference(user_id, language)
            
            if success:
                logger.info(f"Successfully updated language preference for user {user_id}")
                return {
                    'success': True,
                    'errors': {},
                    'updated': True
                }
            else:
                return {
                    'success': False,
                    'errors': {'general': ['Failed to update language preference']},
                    'updated': False
                }
                
        except Exception as e:
            logger.error(f"Error updating language preference for user {user_id}: {str(e)}")
            return {
                'success': False,
                'errors': {'general': [f'Internal error: {str(e)}']},
                'updated': False
            }