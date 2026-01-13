"""
Middleware package for AI Therapy Platform
Breaking Barriers UK 2026 compliant
"""

from .auth_middleware import (
    AuthMiddleware,
    RoleBasedAccessControl,
    require_auth,
    require_role,
    require_permission,
    admin_only,
    therapist_or_admin,
    authenticated_user,
    get_user_from_event,
    is_user_authorized_for_resource
)

__all__ = [
    'AuthMiddleware',
    'RoleBasedAccessControl',
    'require_auth',
    'require_role',
    'require_permission',
    'admin_only',
    'therapist_or_admin',
    'authenticated_user',
    'get_user_from_event',
    'is_user_authorized_for_resource'
]