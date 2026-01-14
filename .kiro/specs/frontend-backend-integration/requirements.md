# Requirements Document: Frontend-Backend Integration Fixes

## Introduction

This specification addresses critical backend integration issues identified by the frontend team that are blocking the AI Therapy Platform from switching from mock authentication to real AWS services. The frontend team has completed all UI components and has real integration code ready but commented out, waiting for these backend fixes.

## Glossary

- **Cognito_User_Pool_Client**: AWS Cognito configuration that defines how applications authenticate users
- **Public_Client**: A Cognito client without a client secret, suitable for frontend applications
- **SRP_Authentication**: Secure Remote Password protocol, secure authentication method for public clients
- **JWT_Token**: JSON Web Token used for authentication and authorization
- **WebSocket_Handler**: Lambda function that processes WebSocket connection events
- **REST_API_Endpoint**: HTTP endpoint that provides data or functionality to the frontend
- **DynamoDB_Query**: Database operation to retrieve specific data from DynamoDB tables
- **Connection_Manager**: System that tracks active WebSocket connections

## Requirements

### Requirement 1: Public Cognito Client Configuration

**User Story:** As a frontend developer, I want a Cognito client without a client secret, so that I can securely authenticate users from the browser application.

#### Acceptance Criteria

1. WHEN creating a new Cognito User Pool Client, THE System SHALL configure it without a client secret
2. WHEN configuring authentication flows, THE System SHALL enable SRP authentication (ALLOW_USER_SRP_AUTH)
3. WHEN configuring authentication flows, THE System SHALL enable refresh token authentication (ALLOW_REFRESH_TOKEN_AUTH)
4. WHEN configuring authentication flows, THE System SHALL NOT enable password authentication (ALLOW_USER_PASSWORD_AUTH)
5. WHERE OAuth flows are configured, THE System SHALL enable authorization code and implicit flows
6. WHERE OAuth scopes are configured, THE System SHALL include email, openid, and profile scopes
7. WHEN configuring token validity, THE System SHALL set access tokens to 1 hour validity
8. WHEN configuring token validity, THE System SHALL set ID tokens to 1 hour validity
9. WHEN configuring token validity, THE System SHALL set refresh tokens to 30 days validity
10. WHEN configuring custom attributes, THE System SHALL allow reading email, email_verified, role, and language_preference
11. WHEN configuring custom attributes, THE System SHALL allow writing email, role, and language_preference

### Requirement 2: WebSocket Authentication

**User Story:** As a client user, I want my WebSocket connections to be authenticated, so that only authorized users can establish real-time communication sessions.

#### Acceptance Criteria

1. WHEN a WebSocket connection is initiated, THE WebSocket_Handler SHALL extract the JWT token from query parameters
2. IF no JWT token is provided, THEN THE WebSocket_Handler SHALL reject the connection with 401 Unauthorized
3. WHEN a JWT token is provided, THE WebSocket_Handler SHALL validate it against Cognito
4. IF the JWT token is invalid or expired, THEN THE WebSocket_Handler SHALL reject the connection with 401 Unauthorized
5. WHEN a JWT token is valid, THE WebSocket_Handler SHALL extract the user ID from the token
6. WHEN a connection is authenticated, THE Connection_Manager SHALL store the connection ID with user information in DynamoDB
7. WHEN storing connection information, THE System SHALL include connectionId, userId, and connectedAt timestamp
8. WHEN a connection is established, THE WebSocket_Handler SHALL return 200 status with "Connected" message
9. WHEN a connection is disconnected, THE WebSocket_Handler SHALL remove the connection record from DynamoDB

### Requirement 3: REST API Endpoints for Authentication

**User Story:** As a frontend developer, I want REST API endpoints for authentication operations, so that users can register, login, and manage their accounts.

#### Acceptance Criteria

1. WHEN implementing POST /auth/register, THE System SHALL create new user accounts in Cognito
2. WHEN implementing POST /auth/login, THE System SHALL authenticate users and return JWT tokens
3. WHEN implementing POST /auth/logout, THE System SHALL invalidate user sessions
4. WHEN implementing POST /auth/refresh, THE System SHALL refresh expired access tokens
5. WHEN implementing GET /auth/profile, THE System SHALL return the authenticated user's profile information
6. WHEN implementing PUT /auth/profile, THE System SHALL update user profile attributes
7. WHEN implementing POST /auth/enable-mfa, THE System SHALL enable multi-factor authentication for users
8. WHEN implementing POST /auth/reset-password, THE System SHALL initiate password reset flow

### Requirement 4: REST API Endpoints for User Management

**User Story:** As a frontend developer, I want REST API endpoints for user management, so that the application can retrieve and update user information.

#### Acceptance Criteria

1. WHEN implementing GET /users/{userId}, THE System SHALL return user details from DynamoDB
2. WHEN implementing PUT /users/{userId}, THE System SHALL update user information in DynamoDB
3. WHEN implementing GET /users/{userId}/sessions, THE System SHALL return all sessions for the specified user
4. WHEN retrieving user data, THE System SHALL validate that the requesting user has permission to access the data
5. WHEN updating user data, THE System SHALL validate that the requesting user has permission to modify the data

### Requirement 5: REST API Endpoints for Session Management

**User Story:** As a frontend developer, I want REST API endpoints for session management, so that the application can create, retrieve, and manage therapy sessions.

#### Acceptance Criteria

1. WHEN implementing POST /sessions, THE System SHALL create new therapy sessions in DynamoDB
2. WHEN implementing GET /sessions/{sessionId}, THE System SHALL return session details from DynamoDB
3. WHEN implementing POST /sessions/{sessionId}/end, THE System SHALL mark sessions as ended and update end timestamp
4. WHERE admin access is granted, WHEN implementing GET /sessions, THE System SHALL return all sessions with pagination
5. WHEN creating sessions, THE System SHALL include sessionId, userId, therapistId, status, startTime, and metadata
6. WHEN retrieving sessions, THE System SHALL include all session attributes and related data

### Requirement 6: REST API Endpoints for Red Flag Management

**User Story:** As a therapist, I want REST API endpoints for red flag management, so that I can view, acknowledge, and resolve safety concerns.

#### Acceptance Criteria

1. WHEN implementing GET /therapists/{therapistId}/red-flags, THE System SHALL return all red flags assigned to the therapist
2. WHEN implementing POST /red-flags/{flagId}/acknowledge, THE System SHALL mark red flags as acknowledged by the therapist
3. WHEN implementing POST /red-flags/{flagId}/resolve, THE System SHALL mark red flags as resolved and update resolution timestamp
4. WHEN retrieving red flags, THE System SHALL include sessionId, flagId, type, severity, detectedAt, context, and resolution status
5. WHEN retrieving red flags, THE System SHALL filter to only show unresolved flags by default
6. WHEN acknowledging red flags, THE System SHALL record the therapist ID and acknowledgment timestamp

### Requirement 7: REST API Endpoints for Notifications

**User Story:** As a user, I want REST API endpoints for notifications, so that I can view and manage my notifications.

#### Acceptance Criteria

1. WHEN implementing GET /users/{userId}/notifications, THE System SHALL return all notifications for the user
2. WHEN implementing POST /notifications/{notificationId}/read, THE System SHALL mark notifications as read
3. WHEN retrieving notifications, THE System SHALL include notificationId, userId, type, message, createdAt, and read status
4. WHEN retrieving notifications, THE System SHALL order by createdAt descending (newest first)
5. WHEN marking notifications as read, THE System SHALL update the read status and record the read timestamp

### Requirement 8: REST API Endpoints for Admin Operations

**User Story:** As an administrator, I want REST API endpoints for admin operations, so that I can monitor system health and manage users.

#### Acceptance Criteria

1. WHEN implementing GET /admin/stats, THE System SHALL return system statistics including user counts, session counts, and red flag counts
2. WHEN implementing GET /admin/users, THE System SHALL return all users with pagination
3. WHEN implementing GET /admin/sessions, THE System SHALL return all sessions with pagination
4. WHEN implementing GET /admin/red-flags, THE System SHALL return all red flags with pagination
5. WHEN calculating statistics, THE System SHALL query DynamoDB for total counts
6. WHEN calculating active user statistics, THE System SHALL filter users by lastActiveAt within 24 hours
7. WHEN calculating active session statistics, THE System SHALL filter sessions by status equals "active"
8. WHEN calculating red flag statistics, THE System SHALL filter red flags by resolved equals false

### Requirement 9: DynamoDB Query Operations

**User Story:** As a backend developer, I want optimized DynamoDB query operations, so that API endpoints can efficiently retrieve data.

#### Acceptance Criteria

1. WHEN querying the Users table for counts, THE System SHALL use scan with Select='COUNT' for efficiency
2. WHEN querying the Users table for active users, THE System SHALL use FilterExpression with lastActiveAt comparison
3. WHEN querying the Sessions table for active sessions, THE System SHALL use FilterExpression with status comparison
4. WHEN querying the RedFlags table for therapist red flags, THE System SHALL use query with therapist-index GSI
5. WHEN querying the RedFlags table for unresolved flags, THE System SHALL use FilterExpression with resolved equals false
6. WHEN implementing pagination, THE System SHALL use LastEvaluatedKey and Limit parameters
7. WHEN querying fails, THE System SHALL return appropriate error messages and status codes

### Requirement 10: CORS Configuration

**User Story:** As a frontend developer, I want proper CORS headers on all API responses, so that the browser allows cross-origin requests.

#### Acceptance Criteria

1. WHEN responding to API requests, THE System SHALL include Access-Control-Allow-Origin header
2. WHEN responding to API requests, THE System SHALL include Access-Control-Allow-Methods header with allowed HTTP methods
3. WHEN responding to API requests, THE System SHALL include Access-Control-Allow-Headers header with allowed request headers
4. WHEN responding to preflight OPTIONS requests, THE System SHALL return 200 status with CORS headers
5. WHERE development environment is active, THE System SHALL allow localhost origins
6. WHERE production environment is active, THE System SHALL allow only configured production origins

### Requirement 11: Error Handling and Response Format

**User Story:** As a frontend developer, I want consistent error handling and response formats, so that I can reliably handle API responses.

#### Acceptance Criteria

1. WHEN API operations succeed, THE System SHALL return responses with success: true and data fields
2. WHEN API operations fail, THE System SHALL return responses with success: false and error fields
3. WHEN authentication fails, THE System SHALL return 401 status code
4. WHEN authorization fails, THE System SHALL return 403 status code
5. WHEN resources are not found, THE System SHALL return 404 status code
6. WHEN validation fails, THE System SHALL return 400 status code with validation error details
7. WHEN server errors occur, THE System SHALL return 500 status code with error message
8. WHEN returning errors, THE System SHALL include descriptive error messages for debugging
