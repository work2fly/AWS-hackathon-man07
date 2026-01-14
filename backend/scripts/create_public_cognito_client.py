#!/usr/bin/env python3
"""
Create Public Cognito Client for Frontend
Breaking Barriers UK 2026 compliant

This script creates a public Cognito User Pool Client without a client secret,
suitable for browser-based frontend applications.
"""

import boto3
import json
import sys
import os
from typing import Dict, Any, Optional


def get_user_pool_id() -> Optional[str]:
    """
    Get the User Pool ID from environment or AWS resources.
    
    Returns:
        User Pool ID or None if not found
    """
    # Try environment variable first
    user_pool_id = os.environ.get('USER_POOL_ID')
    if user_pool_id:
        return user_pool_id
    
    # Try to find it from Cognito
    client = boto3.client('cognito-idp', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-west-2'))
    try:
        response = client.list_user_pools(MaxResults=60)
        for pool in response.get('UserPools', []):
            if 'ai-therapy-platform' in pool['Name']:
                return pool['Id']
    except Exception as e:
        print(f"Error finding user pool: {e}", file=sys.stderr)
    
    return None


def create_public_client(
    user_pool_id: str,
    client_name: str = "ai-therapy-platform-frontend-client",
    region: str = 'us-west-2'
) -> Dict[str, Any]:
    """
    Create public Cognito client without secret.
    
    Args:
        user_pool_id: The Cognito User Pool ID
        client_name: Name for the client
        region: AWS region (default: us-west-2 for Breaking Barriers UK 2026)
    
    Returns:
        Dictionary containing client_id, client_name, and user_pool_id
    """
    client = boto3.client('cognito-idp', region_name=region)
    
    try:
        # Check if client already exists
        existing_clients = client.list_user_pool_clients(
            UserPoolId=user_pool_id,
            MaxResults=60
        )
        
        for existing_client in existing_clients.get('UserPoolClients', []):
            if existing_client['ClientName'] == client_name:
                print(f"Client '{client_name}' already exists with ID: {existing_client['ClientId']}")
                
                # Get full client details
                client_details = client.describe_user_pool_client(
                    UserPoolId=user_pool_id,
                    ClientId=existing_client['ClientId']
                )
                
                return {
                    'client_id': existing_client['ClientId'],
                    'client_name': client_name,
                    'user_pool_id': user_pool_id,
                    'existing': True,
                    'details': client_details['UserPoolClient']
                }
        
        # Create new public client
        print(f"Creating new public client: {client_name}")
        
        response = client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=client_name,
            
            # CRITICAL: No client secret for public clients
            GenerateSecret=False,
            
            # Authentication flows - SRP for secure public client auth
            ExplicitAuthFlows=[
                'ALLOW_USER_SRP_AUTH',        # Secure Remote Password
                'ALLOW_REFRESH_TOKEN_AUTH',   # Refresh tokens
            ],
            
            # OAuth configuration
            AllowedOAuthFlows=['code', 'implicit'],
            AllowedOAuthScopes=['email', 'openid', 'profile'],
            AllowedOAuthFlowsUserPoolClient=True,
            
            # Callback and logout URLs
            CallbackURLs=[
                'http://localhost:3000/callback',
                'http://localhost:3000/',
            ],
            LogoutURLs=[
                'http://localhost:3000/logout',
                'http://localhost:3000/',
            ],
            
            # Supported identity providers
            SupportedIdentityProviders=['COGNITO'],
            
            # Token validity periods
            AccessTokenValidity=1,   # 1 hour
            IdTokenValidity=1,       # 1 hour
            RefreshTokenValidity=30, # 30 days
            TokenValidityUnits={
                'AccessToken': 'hours',
                'IdToken': 'hours',
                'RefreshToken': 'days'
            },
            
            # Prevent user existence errors for security
            PreventUserExistenceErrors='ENABLED',
            
            # Read attributes
            ReadAttributes=[
                'email',
                'email_verified',
                'custom:role',
                'custom:language_preference'
            ],
            
            # Write attributes
            WriteAttributes=[
                'email',
                'custom:role',
                'custom:language_preference'
            ]
        )
        
        client_id = response['UserPoolClient']['ClientId']
        
        print(f"✅ Successfully created public client!")
        print(f"Client ID: {client_id}")
        
        return {
            'client_id': client_id,
            'client_name': client_name,
            'user_pool_id': user_pool_id,
            'existing': False,
            'details': response['UserPoolClient']
        }
        
    except client.exceptions.ResourceNotFoundException:
        print(f"❌ Error: User Pool {user_pool_id} not found", file=sys.stderr)
        sys.exit(1)
    except client.exceptions.LimitExceededException:
        print(f"❌ Error: Client limit exceeded for User Pool", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating client: {e}", file=sys.stderr)
        sys.exit(1)


def verify_client_configuration(user_pool_id: str, client_id: str, region: str = 'us-west-2') -> bool:
    """
    Verify the client configuration meets all requirements.
    
    Args:
        user_pool_id: The Cognito User Pool ID
        client_id: The client ID to verify
        region: AWS region
    
    Returns:
        True if configuration is correct, False otherwise
    """
    client = boto3.client('cognito-idp', region_name=region)
    
    try:
        response = client.describe_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id
        )
        
        config = response['UserPoolClient']
        
        print("\n🔍 Verifying client configuration...")
        
        checks = []
        
        # Check 1: No client secret
        has_secret = config.get('ClientSecret') is not None
        checks.append(('No client secret', not has_secret))
        
        # Check 2: SRP auth enabled
        auth_flows = config.get('ExplicitAuthFlows', [])
        checks.append(('SRP auth enabled', 'ALLOW_USER_SRP_AUTH' in auth_flows))
        
        # Check 3: Refresh token auth enabled
        checks.append(('Refresh token auth enabled', 'ALLOW_REFRESH_TOKEN_AUTH' in auth_flows))
        
        # Check 4: Password auth NOT enabled (more secure)
        checks.append(('Password auth disabled', 'ALLOW_USER_PASSWORD_AUTH' not in auth_flows))
        
        # Check 5: OAuth flows configured
        oauth_flows = config.get('AllowedOAuthFlows', [])
        checks.append(('OAuth code flow enabled', 'code' in oauth_flows))
        checks.append(('OAuth implicit flow enabled', 'implicit' in oauth_flows))
        
        # Check 6: OAuth scopes configured
        oauth_scopes = config.get('AllowedOAuthScopes', [])
        checks.append(('Email scope enabled', 'email' in oauth_scopes))
        checks.append(('OpenID scope enabled', 'openid' in oauth_scopes))
        checks.append(('Profile scope enabled', 'profile' in oauth_scopes))
        
        # Check 7: Token validity
        checks.append(('Access token validity = 1 hour', config.get('AccessTokenValidity') == 1))
        checks.append(('ID token validity = 1 hour', config.get('IdTokenValidity') == 1))
        checks.append(('Refresh token validity = 30 days', config.get('RefreshTokenValidity') == 30))
        
        # Check 8: Read attributes
        read_attrs = config.get('ReadAttributes', [])
        checks.append(('Can read email', 'email' in read_attrs))
        checks.append(('Can read email_verified', 'email_verified' in read_attrs))
        checks.append(('Can read role', 'custom:role' in read_attrs))
        checks.append(('Can read language_preference', 'custom:language_preference' in read_attrs))
        
        # Check 9: Write attributes
        write_attrs = config.get('WriteAttributes', [])
        checks.append(('Can write email', 'email' in write_attrs))
        checks.append(('Can write role', 'custom:role' in write_attrs))
        checks.append(('Can write language_preference', 'custom:language_preference' in write_attrs))
        
        # Print results
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✅ All configuration checks passed!")
        else:
            print("\n⚠️  Some configuration checks failed")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error verifying configuration: {e}", file=sys.stderr)
        return False


def main():
    """Main execution function."""
    print("🏆 Breaking Barriers UK 2026 - Public Cognito Client Setup")
    print("=" * 60)
    
    # Get user pool ID
    user_pool_id = get_user_pool_id()
    
    if not user_pool_id:
        print("❌ Error: Could not find User Pool ID", file=sys.stderr)
        print("Please set USER_POOL_ID environment variable or ensure user pool exists", file=sys.stderr)
        sys.exit(1)
    
    print(f"User Pool ID: {user_pool_id}")
    
    # Get region from environment or use default
    region = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')
    print(f"Region: {region}")
    print()
    
    # Create public client
    result = create_public_client(user_pool_id, region=region)
    
    # Verify configuration
    print()
    verification_passed = verify_client_configuration(
        user_pool_id,
        result['client_id'],
        region=region
    )
    
    # Output results
    print("\n" + "=" * 60)
    print("📋 FRONTEND CONFIGURATION")
    print("=" * 60)
    print(f"User Pool ID: {user_pool_id}")
    print(f"Client ID: {result['client_id']}")
    print(f"Region: {region}")
    print()
    print("Add these to your frontend configuration:")
    print()
    print(f"NEXT_PUBLIC_USER_POOL_ID={user_pool_id}")
    print(f"NEXT_PUBLIC_CLIENT_ID={result['client_id']}")
    print(f"NEXT_PUBLIC_AWS_REGION={region}")
    print("=" * 60)
    
    # Save to file
    output_file = 'cognito-client-config.json'
    with open(output_file, 'w') as f:
        json.dump({
            'user_pool_id': user_pool_id,
            'client_id': result['client_id'],
            'region': region,
            'client_name': result['client_name'],
            'verification_passed': verification_passed
        }, f, indent=2)
    
    print(f"\n💾 Configuration saved to: {output_file}")
    
    if not verification_passed:
        sys.exit(1)


if __name__ == '__main__':
    main()
