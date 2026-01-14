"""
User repository for DynamoDB operations
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseRepository, DynamoDBError
from ..models.user import User, UserRole
from ..utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository):
    """Repository for User operations"""
    
    def __init__(self):
        super().__init__("users")
    
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            # Convert to DynamoDB format
            item = user.to_dynamodb_item()
            
            # Use condition to prevent overwriting existing users
            condition = "attribute_not_exists(userId)"
            
            return self.put_item(item, condition)
            
        except Exception as e:
            logger.error(f"Failed to create user {user.user_id}: {str(e)}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            key = {'userId': user_id}
            item = self.get_item(key)
            
            if item:
                return User.from_dynamodb_item(item)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email using GSI"""
        try:
            response = self.query(
                key_condition_expression="GSI1PK = :email",
                expression_attribute_values={":email": email},
                index_name="EmailIndex",
                limit=1
            )
            
            items = response.get('Items', [])
            if items:
                return User.from_dynamodb_item(items[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {str(e)}")
            return None
    
    def update_user(self, user: User) -> bool:
        """Update existing user"""
        try:
            user.updated_at = datetime.utcnow()
            
            # Build update expression
            update_expression = """
                SET profile = :profile,
                    preferences = :preferences,
                    updatedAt = :updated_at,
                    isActive = :is_active,
                    mfaEnabled = :mfa_enabled,
                    languagePreference = :language_preference
            """
            
            expression_attribute_values = {
                ":profile": user.profile.dict(),
                ":preferences": user.preferences.dict(),
                ":updated_at": user.updated_at.isoformat(),
                ":is_active": user.is_active,
                ":mfa_enabled": user.mfa_enabled,
                ":language_preference": user.language_preference
            }
            
            key = {'userId': user.user_id}
            condition = "attribute_exists(userId)"  # Ensure user exists
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to update user {user.user_id}: {str(e)}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user (GDPR compliance)"""
        try:
            key = {'userId': user_id}
            condition = "attribute_exists(userId)"  # Ensure user exists
            
            return self.delete_item(key, condition)
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {str(e)}")
            return False
    
    def list_users_by_role(self, role: UserRole, limit: Optional[int] = None, 
                          exclusive_start_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List users by role"""
        try:
            response = self.scan(
                filter_expression="#role = :role",
                expression_attribute_names={"#role": "role"},
                expression_attribute_values={":role": role.value},
                limit=limit,
                exclusive_start_key=exclusive_start_key
            )
            
            # Convert items to User objects
            users = []
            for item in response.get('Items', []):
                try:
                    user = User.from_dynamodb_item(item)
                    users.append(user)
                except Exception as e:
                    logger.warning(f"Failed to parse user item: {str(e)}")
                    continue
            
            return {
                'users': users,
                'count': len(users),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
        except Exception as e:
            logger.error(f"Failed to list users by role {role}: {str(e)}")
            return {'users': [], 'count': 0, 'last_evaluated_key': None}
    
    def list_active_users(self, limit: Optional[int] = None,
                         exclusive_start_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List active users"""
        try:
            response = self.scan(
                filter_expression="isActive = :active",
                expression_attribute_values={":active": True},
                limit=limit,
                exclusive_start_key=exclusive_start_key
            )
            
            # Convert items to User objects
            users = []
            for item in response.get('Items', []):
                try:
                    user = User.from_dynamodb_item(item)
                    users.append(user)
                except Exception as e:
                    logger.warning(f"Failed to parse user item: {str(e)}")
                    continue
            
            return {
                'users': users,
                'count': len(users),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
        except Exception as e:
            logger.error(f"Failed to list active users: {str(e)}")
            return {'users': [], 'count': 0, 'last_evaluated_key': None}
    
    def update_user_status(self, user_id: str, is_active: bool) -> bool:
        """Update user active status"""
        try:
            key = {'userId': user_id}
            update_expression = "SET isActive = :active, updatedAt = :updated_at"
            expression_attribute_values = {
                ":active": is_active,
                ":updated_at": datetime.utcnow().isoformat()
            }
            condition = "attribute_exists(userId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to update user status {user_id}: {str(e)}")
            return False
    
    def enable_mfa(self, user_id: str) -> bool:
        """Enable MFA for user"""
        try:
            key = {'userId': user_id}
            update_expression = "SET mfaEnabled = :mfa, updatedAt = :updated_at"
            expression_attribute_values = {
                ":mfa": True,
                ":updated_at": datetime.utcnow().isoformat()
            }
            condition = "attribute_exists(userId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to enable MFA for user {user_id}: {str(e)}")
            return False
    
    def update_language_preference(self, user_id: str, language: str) -> bool:
        """Update user language preference"""
        try:
            key = {'userId': user_id}
            update_expression = "SET languagePreference = :lang, updatedAt = :updated_at"
            expression_attribute_values = {
                ":lang": language,
                ":updated_at": datetime.utcnow().isoformat()
            }
            condition = "attribute_exists(userId)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to update language preference for user {user_id}: {str(e)}")
            return False
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user from dictionary data (for Cognito triggers)"""
        try:
            # Add timestamps
            now = datetime.utcnow().isoformat()
            user_data['created_at'] = now
            user_data['updated_at'] = now
            
            # Convert to DynamoDB format
            item = {
                'userId': user_data['user_id'],
                'email': user_data['email'],
                'role': user_data['role'],
                'profile': user_data['profile'],
                'preferences': user_data['preferences'],
                'createdAt': user_data['created_at'],
                'updatedAt': user_data['updated_at'],
                'isActive': user_data['is_active'],
                'mfaEnabled': user_data['mfa_enabled'],
                'languagePreference': user_data['language_preference'],
                'GSI1PK': user_data['email']  # For email-based queries
            }
            
            # Use condition to prevent overwriting existing users
            condition = "attribute_not_exists(userId)"
            
            success = self.put_item(item, condition)
            
            if success:
                return {'success': True, 'user_id': user_data['user_id']}
            else:
                return {'success': False, 'error': 'Failed to create user'}
            
        except Exception as e:
            logger.error(f"Failed to create user {user_data.get('user_id')}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email using GSI (returns dict for Cognito triggers)"""
        try:
            response = self.query(
                key_condition_expression="GSI1PK = :email",
                expression_attribute_values={":email": email},
                index_name="EmailIndex",
                limit=1
            )
            
            items = response.get('Items', [])
            if items:
                return items[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {str(e)}")
            return None
    
    def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            key = {'userId': user_id}
            update_expression = "SET lastLoginAt = :login_time, updatedAt = :updated_at"
            expression_attribute_values = {
                ":login_time": datetime.utcnow().isoformat(),
                ":updated_at": datetime.utcnow().isoformat()
            }
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values
            )
            
        except Exception as e:
            logger.error(f"Failed to update last login for user {user_id}: {str(e)}")
            return False
    
    def update_clinical_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update clinical profile fields (internal use only)
        
        Args:
            user_id: User identifier
            updates: Dict of clinical profile fields to update
                    (emotional_state, conversation_preference, self_harm_risk_signal, 
                     user_risk, last_session_timestamp, etc.)
        """
        try:
            key = {'userId': user_id}
            
            # Build update expression for clinical profile fields
            update_parts = []
            expression_values = {":updated_at": datetime.utcnow().isoformat()}
            
            for field, value in updates.items():
                # Convert field names to DynamoDB format
                db_field = ''.join(word.capitalize() for word in field.split('_'))
                db_field = db_field[0].lower() + db_field[1:]  # camelCase
                
                update_parts.append(f"clinicalProfile.{db_field} = :{field}")
                
                # Handle datetime objects
                if isinstance(value, datetime):
                    expression_values[f":{field}"] = value.isoformat()
                # Handle enum values
                elif hasattr(value, 'value'):
                    expression_values[f":{field}"] = value.value
                else:
                    expression_values[f":{field}"] = value
            
            update_expression = f"SET {', '.join(update_parts)}, updatedAt = :updated_at"
            condition = "attribute_exists(userId) AND attribute_exists(clinicalProfile)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to update clinical profile for user {user_id}: {str(e)}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Alias for get_user_by_id for consistency"""
        return self.get_user_by_id(user_id)


# Global user repository instance
user_repository = UserRepository()