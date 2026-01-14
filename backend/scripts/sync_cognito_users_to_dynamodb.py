#!/usr/bin/env python3
"""
Sync Cognito users to DynamoDB users table
🏆 Breaking Barriers UK 2026 compliant
"""

import boto3
import sys
from datetime import datetime
from decimal import Decimal

# Configuration
USER_POOL_ID = 'us-west-2_ASOPUuOOV'
USERS_TABLE_NAME = 'ai-therapy-platform-dev-users'
REGION = 'us-west-2'

# Initialize AWS clients
cognito = boto3.client('cognito-idp', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)
users_table = dynamodb.Table(USERS_TABLE_NAME)

def get_role_from_email(email):
    """Determine role from email address"""
    email_lower = email.lower()
    if 'admin' in email_lower:
        return 'admin'
    elif 'therapist' in email_lower or 'dr.' in email_lower:
        return 'therapist'
    else:
        return 'client'

def sync_users():
    """Sync all Cognito users to DynamoDB"""
    try:
        print(f"Fetching users from Cognito User Pool: {USER_POOL_ID}")
        
        # List all users in Cognito
        response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Limit=60
        )
        
        users = response.get('Users', [])
        print(f"Found {len(users)} users in Cognito")
        
        synced_count = 0
        
        for user in users:
            username = user['Username']
            
            # Extract attributes
            attributes = {attr['Name']: attr['Value'] for attr in user.get('Attributes', [])}
            email = attributes.get('email', '')
            given_name = attributes.get('given_name', '')
            family_name = attributes.get('family_name', '')
            sub = attributes.get('sub', username)
            
            # Determine role
            role = get_role_from_email(email)
            
            # Create DynamoDB user item
            timestamp = datetime.now().isoformat()
            
            user_item = {
                'userId': sub,
                'email': email,
                'role': role,
                'profile': {
                    'firstName': given_name or email.split('@')[0],
                    'lastName': family_name or '',
                    'timezone': 'UTC'
                },
                'preferences': {
                    'language': 'en',
                    'voiceSettings': {
                        'preferredVoice': 'neural',
                        'speechRate': Decimal('1.0'),
                        'volume': Decimal('0.8')
                    },
                    'notificationSettings': {
                        'email': True,
                        'sms': False,
                        'push': True,
                        'redFlags': True
                    },
                    'privacySettings': {
                        'shareProgressWithTherapist': True,
                        'allowRecording': False,
                        'dataRetentionDays': 90
                    }
                },
                'createdAt': timestamp,
                'updatedAt': timestamp,
                'isActive': True,
                'mfaEnabled': False,
                'languagePreference': 'en'
            }
            
            # Put item in DynamoDB
            users_table.put_item(Item=user_item)
            
            print(f"✅ Synced user: {email} (role: {role}, userId: {sub})")
            synced_count += 1
        
        print(f"\n🎉 Successfully synced {synced_count} users to DynamoDB")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing users: {str(e)}")
        return False

if __name__ == '__main__':
    success = sync_users()
    sys.exit(0 if success else 1)
