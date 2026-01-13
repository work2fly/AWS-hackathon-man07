"""
WebSocket Connection Repository for AI Therapy Platform
Manages WebSocket connection data in DynamoDB
Breaking Barriers UK 2026 compliant
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import BaseRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)

class WebSocketConnectionRepository(BaseRepository):
    """Repository for managing WebSocket connections"""
    
    def __init__(self, table_name: str = None):
        super().__init__(table_name or 'websocket-connections')
    
    def create_connection(self, connection_id: str, user_id: str, 
                         session_id: Optional[str] = None) -> bool:
        """Create a new WebSocket connection record"""
        try:
            # TTL for 2 hours (7200 seconds)
            ttl = int(time.time()) + 7200
            
            item = {
                'connectionId': connection_id,
                'userId': user_id,
                'connectedAt': datetime.utcnow().isoformat(),
                'ttl': ttl,
                'status': 'connected',
                'lastActivity': datetime.utcnow().isoformat()
            }
            
            if session_id:
                item['sessionId'] = session_id
            
            success = self.put_item(item)
            
            if success:
                logger.info(f"Created connection record: {connection_id} for user: {user_id}")
            else:
                logger.error(f"Failed to create connection record: {connection_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating connection {connection_id}: {str(e)}")
            return False
    
    def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection details by connection ID"""
        try:
            return self.get_item({'connectionId': connection_id})
        except Exception as e:
            logger.error(f"Error getting connection {connection_id}: {str(e)}")
            return None
    
    def update_connection_session(self, connection_id: str, session_id: str) -> bool:
        """Update connection with session ID"""
        try:
            return self.update_item(
                key={'connectionId': connection_id},
                update_expression="SET sessionId = :session_id, lastActivity = :activity",
                expression_attribute_values={
                    ':session_id': session_id,
                    ':activity': datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error updating connection {connection_id}: {str(e)}")
            return False
    
    def update_connection_activity(self, connection_id: str) -> bool:
        """Update last activity timestamp for connection"""
        try:
            return self.update_item(
                key={'connectionId': connection_id},
                update_expression="SET lastActivity = :activity",
                expression_attribute_values={
                    ':activity': datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error updating activity for connection {connection_id}: {str(e)}")
            return False
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove connection record"""
        try:
            success = self.delete_item({'connectionId': connection_id})
            
            if success:
                logger.info(f"Removed connection record: {connection_id}")
            else:
                logger.error(f"Failed to remove connection record: {connection_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error removing connection {connection_id}: {str(e)}")
            return False
    
    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active connections for a user"""
        try:
            response = self.query(
                index_name='UserIndex',
                key_condition_expression='userId = :user_id',
                expression_attribute_values={':user_id': user_id}
            )
            
            connections = response.get('Items', [])
            logger.info(f"Found {len(connections)} connections for user: {user_id}")
            return connections
            
        except Exception as e:
            logger.error(f"Error getting connections for user {user_id}: {str(e)}")
            return []
    
    def get_session_connections(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all connections for a session"""
        try:
            response = self.query(
                index_name='SessionIndex',
                key_condition_expression='sessionId = :session_id',
                expression_attribute_values={':session_id': session_id}
            )
            
            connections = response.get('Items', [])
            logger.info(f"Found {len(connections)} connections for session: {session_id}")
            return connections
            
        except Exception as e:
            logger.error(f"Error getting connections for session {session_id}: {str(e)}")
            return []
    
    def get_active_connections(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all active connections (for monitoring/cleanup)"""
        try:
            response = self.scan(
                filter_expression='#status = :status',
                expression_attribute_names={'#status': 'status'},
                expression_attribute_values={':status': 'connected'},
                limit=limit
            )
            
            connections = response.get('Items', [])
            logger.info(f"Found {len(connections)} active connections")
            return connections
            
        except Exception as e:
            logger.error(f"Error getting active connections: {str(e)}")
            return []
    
    def cleanup_stale_connections(self, max_age_hours: int = 2) -> int:
        """Clean up stale connections older than max_age_hours"""
        try:
            cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
            
            # Get all connections
            active_connections = self.get_active_connections(limit=1000)
            
            stale_count = 0
            for connection in active_connections:
                connected_at = connection.get('connectedAt')
                if connected_at:
                    try:
                        connected_timestamp = datetime.fromisoformat(connected_at.replace('Z', '+00:00')).timestamp()
                        if connected_timestamp < cutoff_time:
                            # Connection is stale, remove it
                            if self.remove_connection(connection['connectionId']):
                                stale_count += 1
                    except ValueError:
                        # Invalid timestamp format, consider it stale
                        if self.remove_connection(connection['connectionId']):
                            stale_count += 1
            
            logger.info(f"Cleaned up {stale_count} stale connections")
            return stale_count
            
        except Exception as e:
            logger.error(f"Error cleaning up stale connections: {str(e)}")
            return 0
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        try:
            active_connections = self.get_active_connections(limit=1000)
            
            stats = {
                'total_active_connections': len(active_connections),
                'connections_by_status': {},
                'connections_with_sessions': 0,
                'unique_users': set(),
                'unique_sessions': set()
            }
            
            for connection in active_connections:
                # Count by status
                status = connection.get('status', 'unknown')
                stats['connections_by_status'][status] = stats['connections_by_status'].get(status, 0) + 1
                
                # Count connections with sessions
                if connection.get('sessionId'):
                    stats['connections_with_sessions'] += 1
                    stats['unique_sessions'].add(connection['sessionId'])
                
                # Count unique users
                if connection.get('userId'):
                    stats['unique_users'].add(connection['userId'])
            
            # Convert sets to counts
            stats['unique_users'] = len(stats['unique_users'])
            stats['unique_sessions'] = len(stats['unique_sessions'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting connection stats: {str(e)}")
            return {
                'total_active_connections': 0,
                'connections_by_status': {},
                'connections_with_sessions': 0,
                'unique_users': 0,
                'unique_sessions': 0
            }

# Global repository instance
websocket_connection_repository = WebSocketConnectionRepository()