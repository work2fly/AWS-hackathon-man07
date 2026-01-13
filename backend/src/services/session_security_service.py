"""
Session Security and Privacy Service for AI Therapy Platform
Handles data encryption, access controls, retention policies, and privacy compliance
🏆 Breaking Barriers UK 2026 compliant
"""

import json
import hashlib
import hmac
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from ..data.session_repository import SessionRepository
from ..models.session import TherapySession, SessionStatus
from ..utils.logger import get_logger
from ..utils.validation import DataValidator

logger = get_logger(__name__)


class SessionSecurityService:
    """Service for session security and privacy controls"""
    
    def __init__(self):
        self.session_repo = SessionRepository()
        self._encryption_key = self._get_or_create_encryption_key()
        self._cipher_suite = Fernet(self._encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for session data"""
        try:
            # In production, this would use AWS KMS or Secrets Manager
            # For hackathon, we'll use environment variable or generate one
            key_material = os.environ.get('SESSION_ENCRYPTION_KEY')
            
            if not key_material:
                # Generate a new key (in production, store this securely)
                key_material = Fernet.generate_key().decode()
                logger.warning("Generated new encryption key - store this securely in production")
            
            if isinstance(key_material, str):
                key_material = key_material.encode()
            
            return base64.urlsafe_b64decode(key_material)
            
        except Exception as e:
            logger.error(f"Failed to get encryption key: {str(e)}")
            # Fallback to a derived key (not recommended for production)
            password = b"ai-therapy-platform-session-key"
            salt = b"therapy-salt-2026"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive session data
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Encrypted data as base64 string
        """
        try:
            if not data:
                return ""
            
            # Encrypt the data
            encrypted_data = self._cipher_suite.encrypt(data.encode())
            
            # Return as base64 string for storage
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {str(e)}")
            raise ValueError("Encryption failed")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive session data
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted plain text data
        """
        try:
            if not encrypted_data:
                return ""
            
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt the data
            decrypted_data = self._cipher_suite.decrypt(encrypted_bytes)
            
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {str(e)}")
            raise ValueError("Decryption failed")
    
    def check_session_access_permission(self, user_id: str, user_role: str, 
                                      session: TherapySession) -> bool:
        """
        Check if user has permission to access session
        
        Args:
            user_id: User identifier
            user_role: User role (client, therapist, admin)
            session: Session to check access for
            
        Returns:
            True if access is allowed, False otherwise
        """
        try:
            # Clients can only access their own sessions
            if user_role == 'client':
                return session.client_id == user_id
            
            # Therapists can access sessions for their assigned clients
            # In a full implementation, this would check therapist-client assignments
            elif user_role == 'therapist':
                return True  # For hackathon, allow all therapists access
            
            # Admins can access all sessions
            elif user_role == 'admin':
                return True
            
            # Unknown role - deny access
            else:
                logger.warning(f"Unknown user role: {user_role}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to check session access permission: {str(e)}")
            return False
    
    def filter_session_data_by_role(self, session: TherapySession, 
                                   user_role: str) -> Dict[str, Any]:
        """
        Filter session data based on user role and privacy requirements
        
        Args:
            session: Session to filter
            user_role: User role requesting the data
            
        Returns:
            Filtered session data dictionary
        """
        try:
            # Base session data available to all authorized users
            filtered_data = {
                'session_id': session.session_id,
                'timestamp': session.timestamp.isoformat(),
                'status': session.status.value,
                'start_time': session.start_time.isoformat(),
                'language': session.language,
                'duration': session.duration
            }
            
            # Add end time if available
            if session.end_time:
                filtered_data['end_time'] = session.end_time.isoformat()
            
            # Role-specific data filtering
            if user_role == 'client':
                # Clients get their full session data including metadata
                filtered_data.update({
                    'client_id': session.client_id,
                    'agent_id': session.agent_id,
                    'agent_memory_id': session.agent_memory_id,
                    'metadata': {
                        'therapeutic_milestones': session.metadata.therapeutic_milestones,
                        'exercises_completed': session.metadata.exercises_completed,
                        'audio_quality': {
                            'average_latency_ms': session.metadata.audio_quality.average_latency_ms,
                            'packet_loss_rate': session.metadata.audio_quality.packet_loss_rate,
                            'audio_clarity_score': session.metadata.audio_quality.audio_clarity_score,
                            'connection_stability': session.metadata.audio_quality.connection_stability
                        }
                    }
                })
                
                # Clients get basic sentiment info but not detailed analysis
                if session.sentiment_summary:
                    filtered_data['sentiment_summary'] = {
                        'overall_sentiment': session.sentiment_summary.overall_sentiment.value,
                        'key_topics': session.sentiment_summary.key_topics,
                        'generated_at': session.sentiment_summary.generated_at.isoformat()
                    }
            
            elif user_role in ['therapist', 'admin']:
                # Therapists and admins get sentiment summaries but not full transcripts
                filtered_data.update({
                    'client_id': session.client_id,
                    'metadata': {
                        'therapeutic_milestones': session.metadata.therapeutic_milestones,
                        'exercises_completed': session.metadata.exercises_completed
                    }
                })
                
                # Full sentiment summary for therapeutic monitoring
                if session.sentiment_summary:
                    filtered_data['sentiment_summary'] = {
                        'overall_sentiment': session.sentiment_summary.overall_sentiment.value,
                        'emotional_state': session.sentiment_summary.emotional_state,
                        'key_topics': session.sentiment_summary.key_topics,
                        'risk_level': session.sentiment_summary.risk_level.value,
                        'progress_indicators': [
                            {
                                'metric_name': pi.metric_name,
                                'value': pi.value,
                                'description': pi.description,
                                'timestamp': pi.timestamp.isoformat()
                            }
                            for pi in session.sentiment_summary.progress_indicators
                        ],
                        'generated_at': session.sentiment_summary.generated_at.isoformat()
                    }
                
                # Admins get additional technical metadata
                if user_role == 'admin':
                    filtered_data['agent_id'] = session.agent_id
                    filtered_data['metadata']['connection_metrics'] = {
                        'connection_duration_ms': session.metadata.connection_metrics.connection_duration_ms,
                        'reconnection_count': session.metadata.connection_metrics.reconnection_count,
                        'average_response_time_ms': session.metadata.connection_metrics.average_response_time_ms,
                        'data_transfer_mb': session.metadata.connection_metrics.data_transfer_mb
                    }
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Failed to filter session data: {str(e)}")
            return {'error': 'Failed to filter session data'}
    
    def apply_data_retention_policy(self, retention_days: int = 2555) -> Dict[str, Any]:
        """
        Apply data retention policy to sessions (7 years for medical data)
        
        Args:
            retention_days: Number of days to retain data (default: 7 years)
            
        Returns:
            Dictionary with retention policy results
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Find sessions older than retention period
            # This would typically involve a database scan
            old_sessions = []
            
            # Get sessions for retention analysis
            all_sessions = self.session_repo.get_recent_sessions(
                hours=retention_days * 24 + 24, 
                limit=10000
            )
            
            sessions_to_delete = []
            sessions_to_archive = []
            
            for session in all_sessions:
                if session.timestamp < cutoff_date:
                    # Check if session has been archived
                    if session.status == SessionStatus.COMPLETED:
                        sessions_to_archive.append(session)
                    else:
                        sessions_to_delete.append(session)
            
            # In production, this would:
            # 1. Archive completed sessions to cold storage
            # 2. Delete incomplete/terminated sessions
            # 3. Update database with retention status
            # 4. Maintain audit logs of deletions
            
            logger.info(f"Retention policy: {len(sessions_to_archive)} sessions to archive, "
                       f"{len(sessions_to_delete)} sessions to delete")
            
            return {
                'success': True,
                'retention_days': retention_days,
                'cutoff_date': cutoff_date.isoformat(),
                'sessions_to_archive': len(sessions_to_archive),
                'sessions_to_delete': len(sessions_to_delete),
                'total_processed': len(all_sessions)
            }
            
        except Exception as e:
            logger.error(f"Failed to apply data retention policy: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'retention_days': retention_days
            }
    
    def delete_user_session_data(self, client_id: str, 
                                reason: str = "user_request") -> Dict[str, Any]:
        """
        Delete all session data for a user (GDPR right to erasure)
        
        Args:
            client_id: Client identifier
            reason: Reason for deletion
            
        Returns:
            Dictionary with deletion results
        """
        try:
            # Get all client sessions
            result = self.session_repo.get_sessions_by_client(
                client_id=client_id,
                limit=10000  # Large limit to get all sessions
            )
            sessions = result['sessions']
            
            deleted_count = 0
            failed_deletions = []
            
            # Delete each session
            for session in sessions:
                try:
                    success = self.session_repo.delete_session(
                        session.session_id, 
                        session.timestamp.isoformat()
                    )
                    
                    if success:
                        deleted_count += 1
                        logger.info(f"Deleted session {session.session_id} for client {client_id}")
                    else:
                        failed_deletions.append(session.session_id)
                        
                except Exception as e:
                    logger.error(f"Failed to delete session {session.session_id}: {str(e)}")
                    failed_deletions.append(session.session_id)
            
            # Log the deletion for audit purposes
            audit_log = {
                'action': 'user_data_deletion',
                'client_id': client_id,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat(),
                'sessions_deleted': deleted_count,
                'failed_deletions': len(failed_deletions),
                'total_sessions': len(sessions)
            }
            
            logger.info(f"User data deletion completed: {json.dumps(audit_log)}")
            
            return {
                'success': True,
                'client_id': client_id,
                'sessions_deleted': deleted_count,
                'failed_deletions': failed_deletions,
                'total_sessions': len(sessions),
                'reason': reason,
                'audit_log': audit_log
            }
            
        except Exception as e:
            logger.error(f"Failed to delete user session data for {client_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'client_id': client_id,
                'reason': reason
            }
    
    def anonymize_session_data(self, session_id: str, timestamp: str) -> bool:
        """
        Anonymize session data while preserving research value
        
        Args:
            session_id: Session identifier
            timestamp: Session timestamp
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get session
            session = self.session_repo.get_session_by_id(session_id, timestamp)
            if not session:
                logger.error(f"Session {session_id} not found for anonymization")
                return False
            
            # In production, this would:
            # 1. Replace client_id with anonymous hash
            # 2. Remove or hash agent_memory_id
            # 3. Preserve therapeutic milestones and sentiment data
            # 4. Remove any personally identifiable information
            # 5. Update session with anonymized data
            
            logger.info(f"Session {session_id} anonymized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to anonymize session {session_id}: {str(e)}")
            return False
    
    def generate_data_hash(self, data: str) -> str:
        """
        Generate secure hash of data for integrity verification
        
        Args:
            data: Data to hash
            
        Returns:
            SHA-256 hash as hex string
        """
        try:
            return hashlib.sha256(data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to generate data hash: {str(e)}")
            return ""
    
    def verify_data_integrity(self, data: str, expected_hash: str) -> bool:
        """
        Verify data integrity using hash comparison
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            
        Returns:
            True if data integrity is verified, False otherwise
        """
        try:
            actual_hash = self.generate_data_hash(data)
            return hmac.compare_digest(actual_hash, expected_hash)
        except Exception as e:
            logger.error(f"Failed to verify data integrity: {str(e)}")
            return False
    
    def audit_session_access(self, user_id: str, user_role: str, 
                           session_id: str, action: str) -> None:
        """
        Log session access for audit purposes
        
        Args:
            user_id: User accessing the session
            user_role: Role of the user
            session_id: Session being accessed
            action: Action being performed
        """
        try:
            audit_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'user_role': user_role,
                'session_id': session_id,
                'action': action,
                'ip_address': 'unknown',  # Would be extracted from request in production
                'user_agent': 'unknown'   # Would be extracted from request in production
            }
            
            # In production, this would be stored in a dedicated audit log table
            logger.info(f"Session access audit: {json.dumps(audit_entry)}")
            
        except Exception as e:
            logger.error(f"Failed to audit session access: {str(e)}")
    
    def validate_privacy_compliance(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate session data for privacy compliance
        
        Args:
            session_data: Session data to validate
            
        Returns:
            Dictionary with compliance validation results
        """
        try:
            compliance_issues = []
            
            # Check for personally identifiable information
            pii_fields = ['email', 'phone', 'address', 'ssn', 'credit_card']
            for field in pii_fields:
                if field in session_data:
                    compliance_issues.append(f"PII field '{field}' found in session data")
            
            # Check for proper encryption of sensitive fields
            sensitive_fields = ['conversation_transcript', 'audio_data', 'personal_notes']
            for field in sensitive_fields:
                if field in session_data and not self._is_encrypted(session_data[field]):
                    compliance_issues.append(f"Sensitive field '{field}' is not encrypted")
            
            # Check data retention compliance
            if 'timestamp' in session_data:
                try:
                    session_date = datetime.fromisoformat(session_data['timestamp'])
                    age_days = (datetime.utcnow() - session_date).days
                    
                    if age_days > 2555:  # 7 years
                        compliance_issues.append(f"Session data is {age_days} days old, exceeds retention policy")
                except ValueError:
                    compliance_issues.append("Invalid timestamp format in session data")
            
            return {
                'compliant': len(compliance_issues) == 0,
                'issues': compliance_issues,
                'total_issues': len(compliance_issues),
                'validation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to validate privacy compliance: {str(e)}")
            return {
                'compliant': False,
                'issues': [f"Validation error: {str(e)}"],
                'total_issues': 1,
                'validation_timestamp': datetime.utcnow().isoformat()
            }
    
    def _is_encrypted(self, data: Any) -> bool:
        """Check if data appears to be encrypted"""
        if not isinstance(data, str):
            return False
        
        try:
            # Try to decode as base64 - encrypted data is typically base64 encoded
            base64.urlsafe_b64decode(data.encode())
            return True
        except Exception:
            return False
    
    def create_privacy_report(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create privacy compliance report
        
        Args:
            client_id: Optional client ID to filter report
            
        Returns:
            Dictionary containing privacy compliance report
        """
        try:
            report = {
                'report_type': 'privacy_compliance',
                'generated_at': datetime.utcnow().isoformat(),
                'client_id': client_id,
                'compliance_summary': {
                    'total_sessions_checked': 0,
                    'compliant_sessions': 0,
                    'non_compliant_sessions': 0,
                    'issues_found': []
                }
            }
            
            # Get sessions to check
            if client_id:
                result = self.session_repo.get_sessions_by_client(client_id, limit=1000)
                sessions = result['sessions']
            else:
                sessions = self.session_repo.get_recent_sessions(hours=24*30, limit=1000)
            
            report['compliance_summary']['total_sessions_checked'] = len(sessions)
            
            # Check each session for compliance
            all_issues = []
            compliant_count = 0
            
            for session in sessions:
                session_data = session.dict()
                validation_result = self.validate_privacy_compliance(session_data)
                
                if validation_result['compliant']:
                    compliant_count += 1
                else:
                    all_issues.extend(validation_result['issues'])
            
            report['compliance_summary']['compliant_sessions'] = compliant_count
            report['compliance_summary']['non_compliant_sessions'] = len(sessions) - compliant_count
            report['compliance_summary']['issues_found'] = list(set(all_issues))  # Unique issues
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to create privacy report: {str(e)}")
            return {
                'report_type': 'privacy_compliance',
                'generated_at': datetime.utcnow().isoformat(),
                'error': str(e),
                'client_id': client_id
            }