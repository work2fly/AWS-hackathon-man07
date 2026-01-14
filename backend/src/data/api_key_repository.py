"""
API Key repository for DynamoDB operations
🏆 Breaking Barriers UK 2026 compliant
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .base import BaseRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


class APIKeyRepository(BaseRepository):
    """Repository for API Key operations"""
    
    def __init__(self):
        super().__init__("api_keys")
    
    def create_api_key(self, key_info: Dict[str, Any]) -> bool:
        """
        Store API key information
        
        Args:
            key_info: {
                'key_hash': 'hashed_value',
                'user_id': 'user123',
                'description': 'Mobile app key',
                'created_at': '2026-01-14T...',
                'is_active': True
            }
        """
        try:
            item = {
                'keyHash': {'S': key_info['key_hash']},
                'userId': {'S': key_info['user_id']},
                'description': {'S': key_info.get('description', '')},
                'createdAt': {'S': key_info['created_at']},
                'isActive': {'BOOL': key_info.get('is_active', True)},
                'lastUsed': {'S': ''} if not key_info.get('last_used') else {'S': key_info['last_used']},
                'GSI1PK': {'S': key_info['user_id']},  # For user-based queries
                'GSI1SK': {'S': key_info['created_at']}
            }
            
            condition = "attribute_not_exists(keyHash)"
            return self.put_item(item, condition)
            
        except Exception as e:
            logger.error(f"Failed to create API key: {str(e)}")
            return False
    
    def get_api_key(self, key_hash: str) -> Optional[Dict[str, Any]]:
        """Get API key by hash"""
        try:
            key = {'keyHash': key_hash}
            item = self.get_item(key)
            
            if item:
                return {
                    'key_hash': item['keyHash']['S'],
                    'user_id': item['userId']['S'],
                    'description': item.get('description', {}).get('S', ''),
                    'created_at': item['createdAt']['S'],
                    'is_active': item['isActive']['BOOL'],
                    'last_used': item.get('lastUsed', {}).get('S')
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get API key: {str(e)}")
            return None
    
    def get_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        try:
            response = self.query(
                key_condition_expression="GSI1PK = :user_id",
                expression_attribute_values={":user_id": user_id},
                index_name="UserIndex"
            )
            
            keys = []
            for item in response.get('Items', []):
                keys.append({
                    'key_hash': item['keyHash']['S'],
                    'user_id': item['userId']['S'],
                    'description': item.get('description', {}).get('S', ''),
                    'created_at': item['createdAt']['S'],
                    'is_active': item['isActive']['BOOL'],
                    'last_used': item.get('lastUsed', {}).get('S')
                })
            
            return keys
            
        except Exception as e:
            logger.error(f"Failed to get user API keys: {str(e)}")
            return []
    
    def update_last_used(self, key_hash: str) -> bool:
        """Update last used timestamp for API key"""
        try:
            key = {'keyHash': key_hash}
            update_expression = "SET lastUsed = :last_used"
            expression_attribute_values = {
                ":last_used": datetime.utcnow().isoformat()
            }
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values
            )
            
        except Exception as e:
            logger.error(f"Failed to update last used: {str(e)}")
            return False
    
    def deactivate_api_key(self, key_hash: str) -> bool:
        """Deactivate an API key"""
        try:
            key = {'keyHash': key_hash}
            update_expression = "SET isActive = :active"
            expression_attribute_values = {":active": False}
            condition = "attribute_exists(keyHash)"
            
            return self.update_item(
                key=key,
                update_expression=update_expression,
                expression_attribute_values=expression_attribute_values,
                condition_expression=condition
            )
            
        except Exception as e:
            logger.error(f"Failed to deactivate API key: {str(e)}")
            return False
    
    def delete_api_key(self, key_hash: str) -> bool:
        """Delete an API key"""
        try:
            key = {'keyHash': key_hash}
            condition = "attribute_exists(keyHash)"
            
            return self.delete_item(key, condition)
            
        except Exception as e:
            logger.error(f"Failed to delete API key: {str(e)}")
            return False
    
    def cleanup_old_keys(self, days: int = 90) -> int:
        """
        Cleanup inactive API keys older than specified days
        
        Returns number of keys deleted
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = self.scan(
                filter_expression="isActive = :active AND createdAt < :cutoff",
                expression_attribute_values={
                    ":active": False,
                    ":cutoff": cutoff_date
                }
            )
            
            deleted_count = 0
            for item in response.get('Items', []):
                key_hash = item['keyHash']['S']
                if self.delete_api_key(key_hash):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old API keys")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old keys: {str(e)}")
            return 0
