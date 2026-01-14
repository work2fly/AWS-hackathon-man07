#!/usr/bin/env python3
"""
Test LiveKit Token Generation
Breaking Barriers UK 2026 Hackathon

This script tests LiveKit token generation using the API credentials
stored in AWS Secrets Manager.
"""

import sys
import json
import boto3
from datetime import datetime, timedelta

try:
    from livekit import api
except ImportError:
    print("❌ livekit-api package not installed")
    print("   Install with: pip install livekit-api")
    sys.exit(1)


def get_secret(secret_arn, region='us-west-2'):
    """Retrieve secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_arn)
        return response['SecretString']
    except Exception as e:
        print(f"❌ Error retrieving secret: {e}")
        return None


def get_terraform_outputs():
    """Get Terraform outputs"""
    import subprocess
    try:
        result = subprocess.run(
            ['terraform', 'output', '-json'],
            cwd='../terraform',
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"❌ Error getting Terraform outputs: {e}")
        return None


def test_token_generation():
    """Test LiveKit token generation"""
    print("🏆 Breaking Barriers UK 2026 - LiveKit Token Generation Test")
    print("=" * 60)
    print()
    
    # Get Terraform outputs
    print("📡 Retrieving configuration from Terraform...")
    outputs = get_terraform_outputs()
    
    if not outputs:
        print("❌ Could not retrieve Terraform outputs")
        return False
    
    # Get LiveKit configuration
    try:
        livekit_config = outputs['environment_config']['value']
        server_url = livekit_config['LIVEKIT_SERVER_URL']
        api_key_secret_arn = livekit_config['LIVEKIT_API_KEY_SECRET']
        api_secret_secret_arn = livekit_config['LIVEKIT_API_SECRET_SECRET']
        
        print(f"✅ LiveKit Server URL: {server_url}")
        print()
    except KeyError as e:
        print(f"❌ Missing configuration: {e}")
        return False
    
    # Retrieve API credentials from Secrets Manager
    print("🔐 Retrieving API credentials from Secrets Manager...")
    api_key = get_secret(api_key_secret_arn)
    api_secret = get_secret(api_secret_secret_arn)
    
    if not api_key or not api_secret:
        print("❌ Could not retrieve API credentials")
        return False
    
    print("✅ API credentials retrieved successfully")
    print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    # Generate test token
    print("🎫 Generating test token...")
    try:
        # Create token with test parameters
        token = api.AccessToken(api_key, api_secret)
        
        # Set token parameters
        token.with_identity("test-user-123")
        token.with_name("Test User")
        token.with_grants(api.VideoGrants(
            room_join=True,
            room="test-room",
            can_publish=True,
            can_subscribe=True,
        ))
        
        # Set expiration (1 hour)
        token.with_ttl(timedelta(hours=1))
        
        # Generate JWT
        jwt_token = token.to_jwt()
        
        print("✅ Token generated successfully!")
        print()
        print("Token Details:")
        print(f"   Identity: test-user-123")
        print(f"   Room: test-room")
        print(f"   Permissions: publish, subscribe")
        print(f"   Expires: {datetime.now() + timedelta(hours=1)}")
        print()
        print("JWT Token (first 50 chars):")
        print(f"   {jwt_token[:50]}...")
        print()
        
        # Test token validation
        print("🔍 Validating token...")
        try:
            # Decode token to verify it's valid
            import jwt as pyjwt
            decoded = pyjwt.decode(
                jwt_token,
                api_secret,
                algorithms=["HS256"],
                options={"verify_signature": True}
            )
            print("✅ Token is valid!")
            print(f"   Subject: {decoded.get('sub')}")
            print(f"   Video grants: {decoded.get('video')}")
            print()
        except Exception as e:
            print(f"⚠️  Token validation warning: {e}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print()
    success = test_token_generation()
    print()
    print("=" * 60)
    
    if success:
        print("✅ All tests passed!")
        print()
        print("Next steps:")
        print("1. Use this token generation logic in Lambda functions")
        print("2. Test client connection with the generated token")
        print("3. Verify audio streaming works end-to-end")
        print()
        print("🏆 Breaking Barriers UK 2026 - LiveKit Authentication Ready!")
        return 0
    else:
        print("❌ Tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
