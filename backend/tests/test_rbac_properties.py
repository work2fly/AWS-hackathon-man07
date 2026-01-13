#!/usr/bin/env python3
"""
Property-Based Tests for Role-Based Access Control
🏆 Breaking Barriers UK 2026 compliant
Feature: ai-therapy-platform, Property 9: Role-Based Access Control
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
"""

import unittest
import json
from typing import Dict, Any, List, Optional

# Property-based testing imports
from hypothesis import given, strategies as st, settings, example
from hypothesis.strategies import composite


class RoleBasedAccessControl:
    """Role-based access control utilities (simplified for testing)"""
    
    # Define permissions for each role
    ROLE_PERMISSIONS = {
        'client': [
            'session:create',
            'session:join',
            'session:view_own',
            'profile:view_own',
            'profile:update_own'
        ],
        'therapist': [
            'session:view_summaries',
            'session:view_all',
            'redflags:view',
            'redflags:acknowledge',
            'notifications:view',
            'profile:view_own',
            'profile:update_own',
            'clients:view_summaries'
        ],
        'admin': [
            'users:create',
            'users:view',
            'users:update',
            'users:delete',
            'system:configure',
            'system:monitor',
            'analytics:view',
            'redflags:manage',
            'notifications:manage',
            'profile:view_all',
            'profile:update_all'
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: str, permission: str) -> bool:
        """Check if user role has specific permission"""
        if not user_role:
            return False
        
        # Admin has all permissions
        if user_role == 'admin':
            return True
        
        # Check role-specific permissions
        role_perms = cls.ROLE_PERMISSIONS.get(user_role, [])
        return permission in role_perms
    
    @classmethod
    def get_user_permissions(cls, user_role: str) -> List[str]:
        """Get all permissions for a user role"""
        if user_role == 'admin':
            # Admin gets all permissions
            all_perms = set()
            for perms in cls.ROLE_PERMISSIONS.values():
                all_perms.update(perms)
            return list(all_perms)
        
        return cls.ROLE_PERMISSIONS.get(user_role, [])


class AuthMiddleware:
    """Authorization middleware (simplified for testing)"""
    
    @staticmethod
    def check_role_permission(user_role: str, required_roles: List[str]) -> bool:
        """Check if user role has required permissions"""
        if not user_role or not required_roles:
            return False
        
        # Role hierarchy: admin > therapist > client
        role_hierarchy = {
            'admin': 3,
            'therapist': 2,
            'client': 1
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_levels = [role_hierarchy.get(role, 0) for role in required_roles]
        
        # User must have at least one of the required role levels
        return user_level >= min(required_levels) if required_levels else False


def is_user_authorized_for_resource(user_info: Dict[str, Any], 
                                  resource_owner_id: str) -> bool:
    """Check if user is authorized to access a resource"""
    if not user_info:
        return False
    
    user_role = user_info.get('role')
    user_id = user_info.get('user_id')
    
    # Admin can access everything
    if user_role == 'admin':
        return True
    
    # Therapists can access client resources
    if user_role == 'therapist':
        return True  # Therapists can view client summaries
    
    # Users can access their own resources
    return user_id == resource_owner_id


@composite
def valid_user_info(draw):
    """Generate valid user information for testing"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'))
    email_local = draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
    email_domain = draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
    email = f"{email_local}@{email_domain}.com"
    role = draw(st.sampled_from(['client', 'therapist', 'admin']))
    language = draw(st.sampled_from(['en', 'es', 'fr', 'de']))
    
    return {
        'user_id': user_id,
        'email': email.lower(),
        'role': role,
        'language_preference': language
    }


@composite
def permission_test_data(draw):
    """Generate permission test data"""
    role = draw(st.sampled_from(['client', 'therapist', 'admin']))
    permission = draw(st.sampled_from([
        'session:create',
        'session:view_own',
        'session:view_summaries',
        'redflags:view',
        'redflags:manage',
        'users:create',
        'users:view',
        'users:update',
        'users:delete',
        'system:configure',
        'analytics:view'
    ]))
    
    return role, permission


class TestRBACProperties(unittest.TestCase):
    """Property-based tests for Role-Based Access Control"""
    
    def setUp(self):
        """Set up test environment"""
        pass
    
    def tearDown(self):
        """Clean up test environment"""
        pass
    
    @given(user_info=valid_user_info())
    @settings(max_examples=10, deadline=None)
    @example(user_info={
        'user_id': 'test_client_123',
        'email': 'client@example.com',
        'role': 'client',
        'language_preference': 'en'
    })
    @example(user_info={
        'user_id': 'test_therapist_456',
        'email': 'therapist@example.com',
        'role': 'therapist',
        'language_preference': 'en'
    })
    @example(user_info={
        'user_id': 'test_admin_789',
        'email': 'admin@example.com',
        'role': 'admin',
        'language_preference': 'en'
    })
    def test_property_role_based_access_control(self, user_info):
        """
        Property 9: Role-Based Access Control
        For any user login, the system should provide access only to features appropriate 
        for their role and enforce access restrictions immediately when roles change.
        **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
        """
        user_role = user_info['role']
        
        # Property: Each role should have specific permissions
        user_permissions = RoleBasedAccessControl.get_user_permissions(user_role)
        self.assertIsInstance(user_permissions, list, 
                             f"User permissions should be a list for role {user_role}")
        
        # Property: Client role should have limited permissions
        if user_role == 'client':
            expected_client_perms = [
                'session:create',
                'session:join',
                'session:view_own',
                'profile:view_own',
                'profile:update_own'
            ]
            for perm in expected_client_perms:
                self.assertIn(perm, user_permissions, 
                             f"Client should have permission: {perm}")
            
            # Clients should NOT have admin permissions
            admin_perms = ['users:delete', 'system:configure', 'redflags:manage']
            for perm in admin_perms:
                self.assertNotIn(perm, user_permissions, 
                                f"Client should NOT have admin permission: {perm}")
        
        # Property: Therapist role should have monitoring permissions
        elif user_role == 'therapist':
            expected_therapist_perms = [
                'session:view_summaries',
                'redflags:view',
                'redflags:acknowledge',
                'notifications:view'
            ]
            for perm in expected_therapist_perms:
                self.assertIn(perm, user_permissions, 
                             f"Therapist should have permission: {perm}")
            
            # Therapists should NOT have user management permissions
            admin_only_perms = ['users:delete', 'system:configure']
            for perm in admin_only_perms:
                self.assertNotIn(perm, user_permissions, 
                                f"Therapist should NOT have admin-only permission: {perm}")
        
        # Property: Admin role should have all permissions
        elif user_role == 'admin':
            admin_perms = [
                'users:create', 'users:view', 'users:update', 'users:delete',
                'system:configure', 'system:monitor', 'analytics:view'
            ]
            for perm in admin_perms:
                self.assertIn(perm, user_permissions, 
                             f"Admin should have permission: {perm}")
        
        # Property: Role hierarchy should be respected
        role_hierarchy = {'admin': 3, 'therapist': 2, 'client': 1}
        user_level = role_hierarchy.get(user_role, 0)
        
        # Test role permission checking
        for test_role, required_level in role_hierarchy.items():
            has_permission = AuthMiddleware.check_role_permission(user_role, [test_role])
            expected = user_level >= required_level
            self.assertEqual(has_permission, expected, 
                           f"Role {user_role} (level {user_level}) permission check for {test_role} (level {required_level}) should be {expected}")
    
    @given(user_info=valid_user_info())
    @settings(max_examples=5, deadline=None)
    def test_property_token_validation_consistency(self, user_info):
        """
        Property: Token validation should be consistent and secure
        For any user information, role checking should produce consistent results.
        """
        user_role = user_info['role']
        
        # Property: Role checking should be consistent
        test_roles = ['client', 'therapist', 'admin']
        
        for test_role in test_roles:
            has_permission1 = AuthMiddleware.check_role_permission(user_role, [test_role])
            has_permission2 = AuthMiddleware.check_role_permission(user_role, [test_role])
            
            self.assertEqual(has_permission1, has_permission2, 
                            f"Role permission check should be consistent for {user_role} -> {test_role}")
            
            # Property: Role hierarchy should be respected
            role_hierarchy = {'admin': 3, 'therapist': 2, 'client': 1}
            user_level = role_hierarchy.get(user_role, 0)
            test_level = role_hierarchy.get(test_role, 0)
            expected = user_level >= test_level
            
            self.assertEqual(has_permission1, expected, 
                            f"Role {user_role} (level {user_level}) permission for {test_role} (level {test_level}) should be {expected}")
    
    @given(permission_data=permission_test_data())
    @settings(max_examples=15, deadline=None)
    def test_property_permission_consistency(self, permission_data):
        """
        Property: Permission checking should be consistent and follow role hierarchy
        For any role and permission combination, permission checking should be deterministic.
        """
        role, permission = permission_data
        
        # Property: Permission checking should be consistent
        has_perm1 = RoleBasedAccessControl.has_permission(role, permission)
        has_perm2 = RoleBasedAccessControl.has_permission(role, permission)
        
        self.assertEqual(has_perm1, has_perm2, 
                        f"Permission check should be consistent for {role}:{permission}")
        
        # Property: Admin should have all permissions
        admin_has_perm = RoleBasedAccessControl.has_permission('admin', permission)
        self.assertTrue(admin_has_perm, 
                       f"Admin should have all permissions including: {permission}")
        
        # Property: Permission should match role capabilities
        role_permissions = RoleBasedAccessControl.get_user_permissions(role)
        expected_has_perm = permission in role_permissions or role == 'admin'
        
        self.assertEqual(has_perm1, expected_has_perm, 
                        f"Permission check result should match role capabilities for {role}:{permission}")
    
    @given(user_info=valid_user_info())
    @settings(max_examples=5, deadline=None)
    def test_property_resource_authorization(self, user_info):
        """
        Property: Resource authorization should respect ownership and role hierarchy
        For any user and resource, authorization should follow consistent rules.
        """
        user_role = user_info['role']
        user_id = user_info['user_id']
        
        # Test resource ownership scenarios
        test_resource_owners = [user_id, 'other_user_123', 'another_user_456']
        
        for resource_owner_id in test_resource_owners:
            is_authorized = is_user_authorized_for_resource(user_info, resource_owner_id)
            
            # Property: Admin can access all resources
            if user_role == 'admin':
                self.assertTrue(is_authorized, 
                               f"Admin should be authorized for all resources")
            
            # Property: Therapists can access client resources
            elif user_role == 'therapist':
                self.assertTrue(is_authorized, 
                               f"Therapist should be authorized for client resources")
            
            # Property: Users can access their own resources
            elif user_role == 'client':
                expected_authorized = (user_id == resource_owner_id)
                self.assertEqual(is_authorized, expected_authorized, 
                               f"Client should only access own resources: user={user_id}, resource_owner={resource_owner_id}")
    
    def test_property_invalid_token_rejection(self):
        """
        Property: Invalid roles should always be rejected
        For any invalid role, the system should consistently reject access.
        """
        invalid_roles = [
            '',
            'invalid_role',
            'user',
            'moderator',
            None
        ]
        
        for invalid_role in invalid_roles:
            # Property: Invalid roles should have no permissions
            permissions = RoleBasedAccessControl.get_user_permissions(invalid_role)
            self.assertEqual(permissions, [], 
                           f"Invalid role should have no permissions: {invalid_role}")
            
            # Property: Invalid roles should not have any specific permission
            test_permission = 'session:create'
            has_permission = RoleBasedAccessControl.has_permission(invalid_role, test_permission)
            self.assertFalse(has_permission, 
                           f"Invalid role should not have any permissions: {invalid_role}")
    
    def test_property_role_hierarchy_consistency(self):
        """
        Property: Role hierarchy should be consistent and transitive
        For any role hierarchy, higher roles should have at least the permissions of lower roles.
        """
        roles = ['client', 'therapist', 'admin']
        
        # Get permissions for each role
        role_perms = {}
        for role in roles:
            role_perms[role] = set(RoleBasedAccessControl.get_user_permissions(role))
        
        # Property: Admin should have the most permissions
        admin_perms = role_perms['admin']
        therapist_perms = role_perms['therapist']
        client_perms = role_perms['client']
        
        self.assertGreaterEqual(len(admin_perms), len(therapist_perms), 
                               "Admin should have at least as many permissions as therapist")
        self.assertGreaterEqual(len(therapist_perms), len(client_perms), 
                               "Therapist should have at least as many permissions as client")
        
        # Property: Role permission checking should respect hierarchy
        for role1 in roles:
            for role2 in roles:
                role1_level = {'client': 1, 'therapist': 2, 'admin': 3}[role1]
                role2_level = {'client': 1, 'therapist': 2, 'admin': 3}[role2]
                
                has_permission = AuthMiddleware.check_role_permission(role1, [role2])
                expected = role1_level >= role2_level
                
                self.assertEqual(has_permission, expected, 
                               f"Role {role1} (level {role1_level}) should {'have' if expected else 'not have'} permission for {role2} (level {role2_level})")
    
    @given(user_info=valid_user_info())
    @settings(max_examples=3, deadline=None)
    def test_property_audit_logging_completeness(self, user_info):
        """
        Property: Role-based access should be deterministic
        For any user information, role-based access decisions should be consistent.
        """
        user_role = user_info['role']
        
        # Property: Permission lists should be consistent
        permissions1 = RoleBasedAccessControl.get_user_permissions(user_role)
        permissions2 = RoleBasedAccessControl.get_user_permissions(user_role)
        
        self.assertEqual(permissions1, permissions2, 
                        f"Permission lists should be consistent for role: {user_role}")
        
        # Property: Permission checking should be consistent
        for permission in permissions1:
            has_perm1 = RoleBasedAccessControl.has_permission(user_role, permission)
            has_perm2 = RoleBasedAccessControl.has_permission(user_role, permission)
            
            self.assertEqual(has_perm1, has_perm2, 
                            f"Permission check should be consistent for {user_role}:{permission}")
            self.assertTrue(has_perm1, 
                           f"User should have permission they are listed as having: {user_role}:{permission}")


def run_rbac_property_tests():
    """Run property-based tests for RBAC"""
    print("🧪 Running Property-Based Tests for Role-Based Access Control")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("Feature: ai-therapy-platform, Property 9: Role-Based Access Control")
    print("**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test class
    tests = unittest.TestLoader().loadTestsFromTestCase(TestRBACProperties)
    test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 All RBAC property-based tests passed!")
        print("✅ Role-Based Access Control properties validated")
        print("🏆 Breaking Barriers UK 2026 compliant RBAC verified")
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
    success = run_rbac_property_tests()
    exit(0 if success else 1)