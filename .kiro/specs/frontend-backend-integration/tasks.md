# Implementation Plan: Frontend-Backend Integration Fixes

## Overview

This implementation plan addresses critical backend integration issues blocking the AI Therapy Platform frontend. The frontend team has all UI components ready with real integration code commented out. Once these backend fixes are complete, the frontend can switch from mock to real AWS services in minutes.

## Tasks

- [x] 1. Create public Cognito client for frontend
  - Create Python script to configure public client without secret
  - Configure SRP authentication and OAuth flows
  - Set token validity periods
  - Test client creation and verify configuration
  - Provide client ID to frontend team
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11_

- [x] 1.1 Write property test for Cognito client configuration
  - **Property 1: Public Cognito Client Configuration**
  - **Validates: Requirements 1.1-1.11**

- [ ] 2. Implement WebSocket authentication
  - [ ] 2.1 Create WebSocket authentication utility module
    - Implement JWT token extraction from query parameters
    - Implement token validation against Cognito
    - Implement user information extraction from token
    - Add error handling for invalid/missing tokens
    - _Requirements: 2.1, 2.3, 2.5_

  - [ ] 2.2 Update WebSocket connect handler
    - Integrate authentication utility
    - Store authenticated connections in DynamoDB
    - Return appropriate status codes
    - Add connection logging
    - _Requirements: 2.6, 2.7, 2.8_

  - [ ] 2.3 Update WebSocket disconnect handler
    - Remove connection records from DynamoDB
    - Add graceful cleanup
    - Add disconnection logging
    - _Requirements: 2.9_

  - [ ] 2.4 Write property test for WebSocket token validation
    - **Property 2: WebSocket Token Validation**
    - **Validates: Requirements 2.1, 2.3, 2.5**

  - [ ] 2.5 Write property test for WebSocket connection lifecycle
    - **Property 3: WebSocket Connection Lifecycle**
    - **Validates: Requirements 2.6, 2.7, 2.8, 2.9**

- [ ] 3. Create response formatter utility
  - Implement success_response function
  - Implement error_response function
  - Implement get_cors_headers function
  - Add response format validation
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 11.1, 11.2_

- [ ] 3.1 Write property test for CORS headers consistency
  - **Property 10: CORS Headers Consistency**
  - **Validates: Requirements 10.1-10.6**

- [ ] 3.2 Write property test for response format consistency
  - **Property 11: Response Format Consistency**
  - **Validates: Requirements 11.1, 11.2**

- [ ] 4. Implement user management endpoints
  - [ ] 4.1 Create user_handlers.py module
    - Implement get_user_handler (GET /users/{userId})
    - Implement update_user_handler (PUT /users/{userId})
    - Implement get_user_sessions_handler (GET /users/{userId}/sessions)
    - Add authorization checks
    - Use response formatter for consistent responses
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 4.2 Write property test for user management endpoints
    - **Property 5: User Management Endpoints Availability**
    - **Validates: Requirements 4.1-4.5**

- [ ] 5. Extend session management endpoints
  - [ ] 5.1 Update session_handlers.py module
    - Implement create_session_handler (POST /sessions)
    - Implement get_session_handler (GET /sessions/{sessionId})
    - Implement end_session_handler (POST /sessions/{sessionId}/end)
    - Implement list_sessions_handler (GET /sessions) for admin
    - Add authorization checks
    - Use response formatter
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ] 5.2 Write property test for session management endpoints
    - **Property 6: Session Management Endpoints Availability**
    - **Validates: Requirements 5.1-5.6**

- [ ] 6. Implement red flag management endpoints
  - [ ] 6.1 Create red_flag_handlers.py module
    - Implement get_therapist_red_flags_handler (GET /therapists/{therapistId}/red-flags)
    - Implement acknowledge_red_flag_handler (POST /red-flags/{flagId}/acknowledge)
    - Implement resolve_red_flag_handler (POST /red-flags/{flagId}/resolve)
    - Add therapist/admin authorization checks
    - Use response formatter
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ] 6.2 Write property test for red flag management endpoints
    - **Property 7: Red Flag Management Endpoints Availability**
    - **Validates: Requirements 6.1-6.6**

- [ ] 7. Implement notification endpoints
  - [ ] 7.1 Create notification_handlers.py module
    - Implement get_user_notifications_handler (GET /users/{userId}/notifications)
    - Implement mark_notification_read_handler (POST /notifications/{notificationId}/read)
    - Add authorization checks
    - Use response formatter
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 7.2 Write property test for notification endpoints
    - **Property 8: Notification Endpoints Availability**
    - **Validates: Requirements 7.1-7.5**

- [ ] 8. Implement admin endpoints
  - [ ] 8.1 Create admin_handlers.py module
    - Implement get_admin_stats_handler (GET /admin/stats)
    - Implement list_all_users_handler (GET /admin/users)
    - Implement list_all_sessions_handler (GET /admin/sessions)
    - Implement list_all_red_flags_handler (GET /admin/red-flags)
    - Add admin-only authorization checks
    - Use response formatter
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [ ] 8.2 Create DynamoDB query optimizer module
    - Implement get_user_count function
    - Implement get_active_user_count function
    - Implement get_active_session_count function
    - Implement get_unresolved_red_flag_count function
    - Implement get_therapist_red_flags function
    - Implement get_user_notifications function
    - Add error handling and logging
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [ ] 8.3 Write property test for admin endpoints
    - **Property 9: Admin Endpoints Availability**
    - **Validates: Requirements 8.1-8.8**

- [ ] 9. Update auth_handlers.py for consistency
  - Update all handlers to use response formatter
  - Ensure CORS headers on all responses
  - Verify error handling consistency
  - Add comprehensive logging
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [ ] 9.1 Write property test for authentication endpoints
  - **Property 4: Authentication Endpoints Availability**
  - **Validates: Requirements 3.1-3.8**

- [ ] 9.2 Write property test for HTTP status code correctness
  - **Property 12: HTTP Status Code Correctness**
  - **Validates: Requirements 11.3-11.8**

- [ ] 10. Checkpoint - Ensure all tests pass
  - Run all unit tests
  - Run all property-based tests
  - Fix any failing tests
  - Verify test coverage
  - Ask the user if questions arise

- [ ] 11. Update Terraform configuration
  - Add new Lambda functions to Terraform
  - Configure API Gateway routes for new endpoints
  - Set up environment variables
  - Configure IAM permissions
  - Deploy infrastructure changes
  - _Requirements: 8.1, 8.2_

- [ ] 12. Integration testing
  - Test complete authentication flow
  - Test WebSocket connection with JWT
  - Test all REST API endpoints
  - Test admin statistics accuracy
  - Test error handling
  - Verify CORS headers
  - _Requirements: All_

- [ ] 13. Frontend integration coordination
  - Provide new Cognito client ID to frontend team
  - Provide API endpoint documentation
  - Provide WebSocket connection instructions
  - Assist with frontend code uncomment
  - Test end-to-end integration
  - _Requirements: All_

- [ ] 14. Final checkpoint - Production readiness
  - All tests passing
  - All endpoints documented
  - Frontend integration complete
  - Performance verified (< 1 RPS Breaking Barriers constraint)
  - Security verified
  - Monitoring configured
  - Ask the user if ready for demo

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Focus on getting frontend unblocked quickly
- Coordinate closely with frontend team throughout implementation
