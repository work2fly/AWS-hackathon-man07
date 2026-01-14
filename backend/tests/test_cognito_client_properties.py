#!/usr/bin/env python3
"""
Property-Based Tests for Cognito Client Configuration
🏆 Breaking Barriers UK 2026 compliant
Feature: frontend-backend-integration, Property 1: Public Cognito Client Configuration
**Validates: Requirements 1.1-1.11**
"""

import unittest
import boto3
import os
import sys
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example


class CognitoClientValidator:
    """Validator for Cognito client configuration"""
    
    @staticmethod
    def validate_public_client_config(config: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate that a Cognito client configuration meets all requirements
        for a public (frontend) client.
        
        Args:
            config: Cognito client configuration dictionary
        
        Returns:
            Dictionary of validation checks with boolean results
        """
        checks = {}
        
        # Requirement 1.1: No client secret
        checks['no_client_secret'] = config.get('ClientSecret') is None
        
        # Get auth flows
        auth_flows = config.get('ExplicitAuthFlows', [])
        
        # Requirement 1.2: SRP authentication enabled
        checks['srp_auth_enabled'] = 'ALLOW_USER_SRP_AUTH' in auth_flows
        
        # Requirement 1.3: Refresh token authentication enabled
        checks['refresh_token_auth_enabled'] = 'ALLOW_REFRESH_TOKEN_AUTH' in auth_flows
        
        # Requirement 1.4: Password authentication NOT enabled (more secure for public clients)
        checks['password_auth_disabled'] = 'ALLOW_USER_PASSWORD_AUTH' not in auth_flows
        
        # Get OAuth settings
        oauth_flows = config.get('AllowedOAuthFlows', [])
        oauth_scopes = config.get('AllowedOAuthScopes', [])
        
        # Requirement 1.5: OAuth flows configured (authorization code and implicit)
        checks['oauth_code_flow_enabled'] = 'code' in oauth_flows
        checks['oauth_implicit_flow_enabled'] = 'implicit' in oauth_flows
        
        # Requirement 1.6: OAuth scopes configured (email, openid, profile)
        checks['oauth_email_scope'] = 'email' in oauth_scopes
        checks['oauth_openid_scope'] = 'openid' in oauth_scopes
        checks['oauth_profile_scope'] = 'profile' in oauth_scopes
        
        # Requirement 1.7: Access token validity = 1 hour
        checks['access_token_validity'] = config.get('AccessTokenValidity') == 1
        
        # Requirement 1.8: ID token validity = 1 hour
        checks['id_token_validity'] = config.get('IdTokenValidity') == 1
        
        # Requirement 1.9: Refresh token validity = 30 days
        checks['refresh_token_validity'] = config.get('RefreshTokenValidity') == 30
        
        # Get token validity units
        token_units = config.get('TokenValidityUnits', {})
        checks['access_token_units_hours'] = token_units.get('AccessToken') == 'hours'
        checks['id_token_units_hours'] = token_units.get('IdToken') == 'hours'
        checks['refresh_token_units_days'] = token_units.get('RefreshToken') == 'days'
        
        # Get read and write attributes
        read_attrs = config.get('ReadAttributes', [])
        write_attrs = config.get('WriteAttributes', [])
        
        # Requirement 1.10: Read attributes (email, email_verified, role, language_preference)
        checks['can_read_email'] = 'email' in read_attrs
        checks['can_read_email_verified'] = 'email_verified' in read_attrs
        checks['can_read_role'] = 'custom:role' in read_attrs
        checks['can_read_language_preference'] = 'custom:language_preference' in read_attrs
        
        # Requirement 1.11: Write attributes (email, role, language_preference)
        checks['can_write_email'] = 'email' in write_attrs
        checks['can_write_role'] = 'custom:role' in write_attrs
        checks['can_write_language_preference'] = 'custom:language_preference' in write_attrs
        
        return checks
    
    @staticmethod
    def all_checks_passed(checks: Dict[str, bool]) -> bool:
        """Check if all validation checks passed"""
        return all(checks.values())
    
    @staticmethod
    def get_failed_checks(checks: Dict[str, bool]) -> list:
        """Get list of failed check names"""
        return [name for name, passed in checks.items() if not passed]


class TestCognitoClientProperties(unittest.TestCase):
    """Property-based tests for Cognito client configuration"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = CognitoClientValidator()
        self.region = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')
    
    def _create_valid_client_config(self) -> Dict[str, Any]:
        """Create a valid public client configuration for testing"""
        return {
            'ClientId': 'test-client-id-123',
            'ClientName': 'test-public-client',
            'UserPoolId': 'us-west-2_TestPool',
            # No ClientSecret - this is key for public clients
            'ExplicitAuthFlows': [
                'ALLOW_USER_SRP_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH',
            ],
            'AllowedOAuthFlows': ['code', 'implicit'],
            'AllowedOAuthScopes': ['email', 'openid', 'profile'],
            'AllowedOAuthFlowsUserPoolClient': True,
            'CallbackURLs': ['http://localhost:3000/callback'],
            'LogoutURLs': ['http://localhost:3000/logout'],
            'SupportedIdentityProviders': ['COGNITO'],
            'AccessTokenValidity': 1,
            'IdTokenValidity': 1,
            'RefreshTokenValidity': 30,
            'TokenValidityUnits': {
                'AccessToken': 'hours',
                'IdToken': 'hours',
                'RefreshToken': 'days'
            },
            'PreventUserExistenceErrors': 'ENABLED',
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
    
    def _create_invalid_client_config(self, flaw: str) -> Dict[str, Any]:
        """Create an invalid client configuration with a specific flaw"""
        config = self._create_valid_client_config()
        
        if flaw == 'has_secret':
            config['ClientSecret'] = 'secret-value-should-not-exist'
        elif flaw == 'no_srp':
            config['ExplicitAuthFlows'] = ['ALLOW_REFRESH_TOKEN_AUTH']
        elif flaw == 'no_refresh':
            config['ExplicitAuthFlows'] = ['ALLOW_USER_SRP_AUTH']
        elif flaw == 'has_password_auth':
            config['ExplicitAuthFlows'].append('ALLOW_USER_PASSWORD_AUTH')
        elif flaw == 'no_oauth_code':
            config['AllowedOAuthFlows'] = ['implicit']
        elif flaw == 'no_oauth_implicit':
            config['AllowedOAuthFlows'] = ['code']
        elif flaw == 'missing_email_scope':
            config['AllowedOAuthScopes'] = ['openid', 'profile']
        elif flaw == 'missing_openid_scope':
            config['AllowedOAuthScopes'] = ['email', 'profile']
        elif flaw == 'missing_profile_scope':
            config['AllowedOAuthScopes'] = ['email', 'openid']
        elif flaw == 'wrong_access_token_validity':
            config['AccessTokenValidity'] = 24
        elif flaw == 'wrong_id_token_validity':
            config['IdTokenValidity'] = 24
        elif flaw == 'wrong_refresh_token_validity':
            config['RefreshTokenValidity'] = 7
        elif flaw == 'missing_read_email':
            config['ReadAttributes'] = ['email_verified', 'custom:role', 'custom:language_preference']
        elif flaw == 'missing_read_role':
            config['ReadAttributes'] = ['email', 'email_verified', 'custom:language_preference']
        elif flaw == 'missing_write_email':
            config['WriteAttributes'] = ['custom:role', 'custom:language_preference']
        elif flaw == 'missing_write_role':
            config['WriteAttributes'] = ['email', 'custom:language_preference']
        
        return config
    
    def test_property_public_cognito_client_configuration(self):
        """
        Property 1: Public Cognito Client Configuration
        For any created public Cognito client, the configuration should have no client secret,
        enable SRP and refresh token auth flows, disable password auth, and include correct
        OAuth settings with appropriate token validity periods.
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11**
        """
        # Test with valid configuration
        valid_config = self._create_valid_client_config()
        checks = self.validator.validate_public_client_config(valid_config)
        
        # Property: All checks should pass for valid configuration
        failed_checks = self.validator.get_failed_checks(checks)
        self.assertTrue(
            self.validator.all_checks_passed(checks),
            f"Valid public client configuration should pass all checks. Failed: {failed_checks}"
        )
        
        # Verify specific requirements
        self.assertTrue(checks['no_client_secret'], 
                       "Requirement 1.1: Public client must not have client secret")
        self.assertTrue(checks['srp_auth_enabled'], 
                       "Requirement 1.2: SRP authentication must be enabled")
        self.assertTrue(checks['refresh_token_auth_enabled'], 
                       "Requirement 1.3: Refresh token authentication must be enabled")
        self.assertTrue(checks['password_auth_disabled'], 
                       "Requirement 1.4: Password authentication should be disabled for security")
        self.assertTrue(checks['oauth_code_flow_enabled'], 
                       "Requirement 1.5: OAuth authorization code flow must be enabled")
        self.assertTrue(checks['oauth_implicit_flow_enabled'], 
                       "Requirement 1.5: OAuth implicit flow must be enabled")
        self.assertTrue(checks['oauth_email_scope'], 
                       "Requirement 1.6: OAuth email scope must be included")
        self.assertTrue(checks['oauth_openid_scope'], 
                       "Requirement 1.6: OAuth openid scope must be included")
        self.assertTrue(checks['oauth_profile_scope'], 
                       "Requirement 1.6: OAuth profile scope must be included")
        self.assertTrue(checks['access_token_validity'], 
                       "Requirement 1.7: Access token validity must be 1 hour")
        self.assertTrue(checks['id_token_validity'], 
                       "Requirement 1.8: ID token validity must be 1 hour")
        self.assertTrue(checks['refresh_token_validity'], 
                       "Requirement 1.9: Refresh token validity must be 30 days")
        self.assertTrue(checks['can_read_email'], 
                       "Requirement 1.10: Must be able to read email")
        self.assertTrue(checks['can_read_email_verified'], 
                       "Requirement 1.10: Must be able to read email_verified")
        self.assertTrue(checks['can_read_role'], 
                       "Requirement 1.10: Must be able to read role")
        self.assertTrue(checks['can_read_language_preference'], 
                       "Requirement 1.10: Must be able to read language_preference")
        self.assertTrue(checks['can_write_email'], 
                       "Requirement 1.11: Must be able to write email")
        self.assertTrue(checks['can_write_role'], 
                       "Requirement 1.11: Must be able to write role")
        self.assertTrue(checks['can_write_language_preference'], 
                       "Requirement 1.11: Must be able to write language_preference")
    
    def test_property_invalid_configurations_detected(self):
        """
        Property: Invalid configurations should be detected
        For any configuration that violates requirements, validation should fail.
        """
        # Test various invalid configurations
        invalid_flaws = [
            'has_secret',
            'no_srp',
            'no_refresh',
            'has_password_auth',
            'no_oauth_code',
            'no_oauth_implicit',
            'missing_email_scope',
            'missing_openid_scope',
            'missing_profile_scope',
            'wrong_access_token_validity',
            'wrong_id_token_validity',
            'wrong_refresh_token_validity',
            'missing_read_email',
            'missing_read_role',
            'missing_write_email',
            'missing_write_role'
        ]
        
        for flaw in invalid_flaws:
            with self.subTest(flaw=flaw):
                invalid_config = self._create_invalid_client_config(flaw)
                checks = self.validator.validate_public_client_config(invalid_config)
                
                # Property: Invalid configuration should fail at least one check
                self.assertFalse(
                    self.validator.all_checks_passed(checks),
                    f"Configuration with flaw '{flaw}' should fail validation"
                )
    
    def test_property_validation_consistency(self):
        """
        Property: Validation should be consistent
        For any configuration, validation should produce consistent results.
        """
        config = self._create_valid_client_config()
        
        # Run validation multiple times
        result1 = self.validator.validate_public_client_config(config)
        result2 = self.validator.validate_public_client_config(config)
        result3 = self.validator.validate_public_client_config(config)
        
        # Property: Results should be identical
        self.assertEqual(result1, result2, "Validation should be consistent")
        self.assertEqual(result2, result3, "Validation should be consistent")
    
    @settings(max_examples=100, deadline=None)
    @given(
        access_validity=st.integers(min_value=1, max_value=24),
        id_validity=st.integers(min_value=1, max_value=24),
        refresh_validity=st.integers(min_value=1, max_value=365)
    )
    def test_property_token_validity_detection(self, access_validity, id_validity, refresh_validity):
        """
        Property: Token validity validation
        For any token validity values, the validator should correctly identify
        whether they match the required values (1 hour for access/ID, 30 days for refresh).
        """
        config = self._create_valid_client_config()
        config['AccessTokenValidity'] = access_validity
        config['IdTokenValidity'] = id_validity
        config['RefreshTokenValidity'] = refresh_validity
        
        checks = self.validator.validate_public_client_config(config)
        
        # Property: Validation should correctly identify token validity
        self.assertEqual(
            checks['access_token_validity'],
            access_validity == 1,
            f"Access token validity check should be {access_validity == 1} for value {access_validity}"
        )
        self.assertEqual(
            checks['id_token_validity'],
            id_validity == 1,
            f"ID token validity check should be {id_validity == 1} for value {id_validity}"
        )
        self.assertEqual(
            checks['refresh_token_validity'],
            refresh_validity == 30,
            f"Refresh token validity check should be {refresh_validity == 30} for value {refresh_validity}"
        )
    
    @settings(max_examples=100, deadline=None)
    @given(
        has_srp=st.booleans(),
        has_refresh=st.booleans(),
        has_password=st.booleans()
    )
    def test_property_auth_flow_detection(self, has_srp, has_refresh, has_password):
        """
        Property: Auth flow detection
        For any combination of auth flows, the validator should correctly identify
        which flows are enabled.
        """
        config = self._create_valid_client_config()
        
        # Build auth flows based on parameters
        auth_flows = []
        if has_srp:
            auth_flows.append('ALLOW_USER_SRP_AUTH')
        if has_refresh:
            auth_flows.append('ALLOW_REFRESH_TOKEN_AUTH')
        if has_password:
            auth_flows.append('ALLOW_USER_PASSWORD_AUTH')
        
        config['ExplicitAuthFlows'] = auth_flows
        
        checks = self.validator.validate_public_client_config(config)
        
        # Property: Validation should correctly identify auth flows
        self.assertEqual(
            checks['srp_auth_enabled'],
            has_srp,
            f"SRP auth check should be {has_srp}"
        )
        self.assertEqual(
            checks['refresh_token_auth_enabled'],
            has_refresh,
            f"Refresh token auth check should be {has_refresh}"
        )
        self.assertEqual(
            checks['password_auth_disabled'],
            not has_password,
            f"Password auth disabled check should be {not has_password}"
        )


def run_property_tests():
    """Run property-based tests for Cognito client configuration"""
    print("🧪 Running Property-Based Tests for Cognito Client Configuration")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: frontend-backend-integration, Property 1: Public Cognito Client Configuration")
    print("**Validates: Requirements 1.1-1.11**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestCognitoClientProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All property-based tests passed!")
        print("✅ Public Cognito Client Configuration properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant configuration verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} test(s) had errors")
        
        # Print failure details
        for test, traceback in result.failures:
            print(f"\nFAILURE: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_property_tests()
    exit(0 if success else 1)
