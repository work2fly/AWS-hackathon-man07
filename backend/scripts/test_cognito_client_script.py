#!/usr/bin/env python3
"""
Test script for create_public_cognito_client.py
Tests the script logic without requiring AWS credentials
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from tests.test_cognito_client_properties import CognitoClientValidator


def test_validator():
    """Test the CognitoClientValidator class"""
    print("🧪 Testing CognitoClientValidator")
    print("=" * 60)
    
    validator = CognitoClientValidator()
    
    # Test 1: Valid configuration
    print("\n✅ Test 1: Valid public client configuration")
    valid_config = {
        'ClientId': 'test-client-123',
        'ClientName': 'test-public-client',
        'UserPoolId': 'us-west-2_TestPool',
        'ExplicitAuthFlows': [
            'ALLOW_USER_SRP_AUTH',
            'ALLOW_REFRESH_TOKEN_AUTH',
        ],
        'AllowedOAuthFlows': ['code', 'implicit'],
        'AllowedOAuthScopes': ['email', 'openid', 'profile'],
        'AccessTokenValidity': 1,
        'IdTokenValidity': 1,
        'RefreshTokenValidity': 30,
        'TokenValidityUnits': {
            'AccessToken': 'hours',
            'IdToken': 'hours',
            'RefreshToken': 'days'
        },
        'ReadAttributes': [
            'email',
            'email_verified',
            'custom:role',
            'custom:language_preference'
        ],
        'WriteAttributes': [
            'email',
            'custom:role',
            'custom:language_preference'
        ]
    }
    
    checks = validator.validate_public_client_config(valid_config)
    all_passed = validator.all_checks_passed(checks)
    
    print(f"All checks passed: {all_passed}")
    if all_passed:
        print("✅ Valid configuration correctly validated")
    else:
        failed = validator.get_failed_checks(checks)
        print(f"❌ Failed checks: {failed}")
        return False
    
    # Test 2: Invalid configuration (has client secret)
    print("\n❌ Test 2: Invalid configuration (has client secret)")
    invalid_config = valid_config.copy()
    invalid_config['ClientSecret'] = 'should-not-exist'
    
    checks = validator.validate_public_client_config(invalid_config)
    all_passed = validator.all_checks_passed(checks)
    
    print(f"All checks passed: {all_passed}")
    if not all_passed:
        failed = validator.get_failed_checks(checks)
        print(f"✅ Correctly detected invalid configuration: {failed}")
    else:
        print("❌ Failed to detect invalid configuration")
        return False
    
    # Test 3: Invalid configuration (missing SRP auth)
    print("\n❌ Test 3: Invalid configuration (missing SRP auth)")
    invalid_config = valid_config.copy()
    invalid_config['ExplicitAuthFlows'] = ['ALLOW_REFRESH_TOKEN_AUTH']
    
    checks = validator.validate_public_client_config(invalid_config)
    all_passed = validator.all_checks_passed(checks)
    
    print(f"All checks passed: {all_passed}")
    if not all_passed:
        failed = validator.get_failed_checks(checks)
        print(f"✅ Correctly detected missing SRP auth: {failed}")
    else:
        print("❌ Failed to detect missing SRP auth")
        return False
    
    # Test 4: Invalid configuration (wrong token validity)
    print("\n❌ Test 4: Invalid configuration (wrong token validity)")
    invalid_config = valid_config.copy()
    invalid_config['AccessTokenValidity'] = 24  # Should be 1
    
    checks = validator.validate_public_client_config(invalid_config)
    all_passed = validator.all_checks_passed(checks)
    
    print(f"All checks passed: {all_passed}")
    if not all_passed:
        failed = validator.get_failed_checks(checks)
        print(f"✅ Correctly detected wrong token validity: {failed}")
    else:
        print("❌ Failed to detect wrong token validity")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All validator tests passed!")
    return True


if __name__ == '__main__':
    success = test_validator()
    sys.exit(0 if success else 1)
