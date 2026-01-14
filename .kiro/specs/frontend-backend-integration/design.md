# Design Document: Frontend-Backend Integration Fixes

## Overview

This design addresses critical backend integration issues blocking the AI Therapy Platform frontend from switching to real AWS services. The frontend team has completed all UI components with real integration code ready but commented out. This design provides solutions for:

1. Creating a public Cognito client without client secret for secure browser-based authentication
2. Implementing JWT-based WebSocket authentication
3. Creating missing REST API endpoints for frontend integration
4. Optimizing DynamoDB queries for efficient data retrieval

The design follows AWS Breaking Barriers UK 2026 constraints and security best practices.

## Architecture

### High-Level Architecture

```
Frontend (Browser)
    ↓ HTTPS
API Gateway (REST)
    ↓ Lambda Proxy
Lambda Functions (Python)
    ↓ boto3
AWS Services (Cognito, DynamoDB)

Frontend (Browser)
    ↓ WSS (WebSocket Secure)
API Gateway (WebSocket)
    ↓ Lambda Proxy
WebSocket Handlers (Python)
    ↓ boto3
DynamoDB (Connection Management)
```

### Authentication Flow

```
1. User Registration/Login → Frontend
2. Frontend → API Gateway → auth_handlers.py
3. auth_handlers.py → Cognito (SRP Auth)
4. Cognito → JWT Tokens → Frontend
5. Frontend stores tokens in memory/sessionStorage
6. Subsequent requests include: Authorization: Bearer <token>
```

### WebSocket Authentication Flow

```
1. Frontend obtains JWT token from Cognito
2. Frontend connects: wss://endpoint?token=<jwt>
3. WebSocket Handler extracts token from query params
4. Handler validates token with Cognito
5. Handler stores connection in DynamoDB
6. Connection established with user context
```

## Components and Interfaces

### 1. Cognito Client Configuration Script

**Purpose**: Create a public Cognito User Pool Client for frontend applications

**Location**: `backend/scripts/create_public_cognito_client.py`

**Interface**:
```python
def create_public_client(
    user_pool_id: str,
    client_name: str = "ai-therapy-platform-frontend-client"
) -> Dict[str, Any]:
    """
    Create public Cognito client without secret
    
    Returns:
        {
            'client_id': str,
            'client_name': str,
            'user_pool_id': str
        }
    """
```


**Configuration Parameters**:
- No client secret (`generate_secret=False`)
- SRP authentication flow (`ALLOW_USER_SRP_AUTH`)
- Refresh token flow (`ALLOW_REFRESH_TOKEN_AUTH`)
- OAuth flows: authorization code and implicit
- OAuth scopes: email, openid, profile
- Token validity: 1 hour (access/ID), 30 days (refresh)
- Custom attributes: email, role, language_preference

### 2. WebSocket Authentication Module

**Purpose**: Validate JWT tokens for WebSocket connections

**Location**: `backend/src/utils/websocket_auth.py`

**Interface**:
```python
def validate_websocket_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate JWT token for WebSocket connection
    
    Args:
        token: JWT token from query parameters
        
    Returns:
        (is_valid, user_info) where user_info contains:
        {
            'user_id': str,
            'email': str,
            'role': str,
            'username': str
        }
    """

def extract_token_from_event(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract JWT token from WebSocket event
    
    Args:
        event: Lambda event from API Gateway WebSocket
        
    Returns:
        JWT token string or None
    """
```

### 3. REST API Endpoint Handlers

**Purpose**: Provide missing REST API endpoints for frontend integration

**Locations**:
- `backend/src/lambda_functions/user_handlers.py` (new)
- `backend/src/lambda_functions/session_handlers.py` (existing, extend)
- `backend/src/lambda_functions/red_flag_handlers.py` (new)
- `backend/src/lambda_functions/notification_handlers.py` (new)
- `backend/src/lambda_functions/admin_handlers.py` (new)

**Interfaces**:

```python
# User Management
def get_user_handler(event, context) -> Dict:
    """GET /users/{userId}"""

def update_user_handler(event, context) -> Dict:
    """PUT /users/{userId}"""

def get_user_sessions_handler(event, context) -> Dict:
    """GET /users/{userId}/sessions"""

# Session Management
def create_session_handler(event, context) -> Dict:
    """POST /sessions"""

def get_session_handler(event, context) -> Dict:
    """GET /sessions/{sessionId}"""

def end_session_handler(event, context) -> Dict:
    """POST /sessions/{sessionId}/end"""

def list_sessions_handler(event, context) -> Dict:
    """GET /sessions (admin only)"""

# Red Flag Management
def get_therapist_red_flags_handler(event, context) -> Dict:
    """GET /therapists/{therapistId}/red-flags"""

def acknowledge_red_flag_handler(event, context) -> Dict:
    """POST /red-flags/{flagId}/acknowledge"""

def resolve_red_flag_handler(event, context) -> Dict:
    """POST /red-flags/{flagId}/resolve"""

# Notifications
def get_user_notifications_handler(event, context) -> Dict:
    """GET /users/{userId}/notifications"""

def mark_notification_read_handler(event, context) -> Dict:
    """POST /notifications/{notificationId}/read"""

# Admin Operations
def get_admin_stats_handler(event, context) -> Dict:
    """GET /admin/stats"""

def list_all_users_handler(event, context) -> Dict:
    """GET /admin/users"""

def list_all_sessions_handler(event, context) -> Dict:
    """GET /admin/sessions"""

def list_all_red_flags_handler(event, context) -> Dict:
    """GET /admin/red-flags"""
```


### 4. DynamoDB Query Optimization Module

**Purpose**: Provide efficient query operations for API endpoints

**Location**: `backend/src/data/query_optimizer.py` (new)

**Interface**:
```python
def get_user_count() -> int:
    """Get total user count efficiently"""

def get_active_user_count(hours: int = 24) -> int:
    """Get count of users active within specified hours"""

def get_active_session_count() -> int:
    """Get count of currently active sessions"""

def get_unresolved_red_flag_count() -> int:
    """Get count of unresolved red flags"""

def get_therapist_red_flags(
    therapist_id: str,
    resolved: bool = False,
    limit: int = 100
) -> List[Dict]:
    """Get red flags for specific therapist with filtering"""

def get_user_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50
) -> List[Dict]:
    """Get notifications for user with filtering"""
```

### 5. Response Formatter Module

**Purpose**: Standardize API responses across all endpoints

**Location**: `backend/src/utils/response_formatter.py` (new)

**Interface**:
```python
def success_response(
    data: Any,
    status_code: int = 200,
    message: Optional[str] = None
) -> Dict:
    """
    Create standardized success response
    
    Returns:
        {
            'statusCode': int,
            'headers': {...},
            'body': json.dumps({
                'success': True,
                'data': data,
                'message': message
            })
        }
    """

def error_response(
    error: str,
    status_code: int = 400,
    details: Optional[Dict] = None
) -> Dict:
    """
    Create standardized error response
    
    Returns:
        {
            'statusCode': int,
            'headers': {...},
            'body': json.dumps({
                'success': False,
                'error': error,
                'details': details
            })
        }
    """

def get_cors_headers(origin: str = '*') -> Dict[str, str]:
    """Get CORS headers for API responses"""
```

## Data Models

### WebSocket Connection Model

```python
{
    'connectionId': str,      # Primary key
    'userId': str,            # GSI partition key
    'sessionId': str,         # GSI partition key (optional)
    'connectedAt': str,       # ISO 8601 timestamp
    'lastActivityAt': str,    # ISO 8601 timestamp
    'ttl': int                # Unix timestamp for auto-cleanup
}
```

### Admin Statistics Model

```python
{
    'totalUsers': int,
    'activeUsers': int,       # Active in last 24 hours
    'totalSessions': int,
    'activeSessions': int,    # Currently active
    'redFlags': int,          # Unresolved
    'notifications': int      # Unread
}
```

### Red Flag Response Model

```python
{
    'sessionId': str,
    'flagId': str,
    'type': str,              # 'suicidal_ideation', 'self_harm', etc.
    'severity': str,          # 'low', 'medium', 'high', 'critical'
    'detectedAt': str,        # ISO 8601 timestamp
    'context': str,           # Brief context
    'notificationsSent': List[Dict],
    'resolved': bool,
    'resolvedAt': Optional[str],
    'resolvedBy': Optional[str],
    'acknowledgedAt': Optional[str],
    'acknowledgedBy': Optional[str]
}
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Public Cognito Client Configuration

*For any* created public Cognito client, the configuration should have no client secret, enable SRP and refresh token auth flows, disable password auth, and include correct OAuth settings with appropriate token validity periods.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11**

### Property 2: WebSocket Token Validation

*For any* WebSocket connection attempt with a JWT token, the system should correctly extract the token from query parameters, validate it against Cognito, extract user information, and either establish the connection (valid token) or reject with 401 (invalid/missing token).

**Validates: Requirements 2.1, 2.3, 2.5**

### Property 3: WebSocket Connection Lifecycle

*For any* authenticated WebSocket connection, the system should store the connection with all required fields (connectionId, userId, connectedAt) in DynamoDB, return 200 status on establishment, and remove the connection record on disconnection.

**Validates: Requirements 2.6, 2.7, 2.8, 2.9**

### Property 4: Authentication Endpoints Availability

*For any* authentication operation (register, login, logout, refresh, profile get/update, MFA enable, password reset), the corresponding REST API endpoint should exist, accept the correct request format, and return the expected response structure.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8**

### Property 5: User Management Endpoints Availability

*For any* user management operation (get user, update user, get user sessions), the corresponding REST API endpoint should exist, enforce proper authorization, and return the expected data format.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

### Property 6: Session Management Endpoints Availability

*For any* session management operation (create, get, end, list), the corresponding REST API endpoint should exist, enforce proper authorization, and return the expected data format with all required session fields.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**

### Property 7: Red Flag Management Endpoints Availability

*For any* red flag management operation (get therapist flags, acknowledge, resolve), the corresponding REST API endpoint should exist, enforce therapist/admin authorization, and return the expected data format with all red flag details.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**

### Property 8: Notification Endpoints Availability

*For any* notification operation (get user notifications, mark as read), the corresponding REST API endpoint should exist, enforce proper authorization, and return the expected data format with notification details.

**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

### Property 9: Admin Endpoints Availability

*For any* admin operation (get stats, list users, list sessions, list red flags), the corresponding REST API endpoint should exist, enforce admin-only authorization, and return the expected data format with accurate statistics and pagination.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8**

### Property 10: CORS Headers Consistency

*For any* API response from any endpoint, the response should include all required CORS headers (Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Allow-Headers) with appropriate values.

**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6**

### Property 11: Response Format Consistency

*For any* API operation, successful responses should include success: true and data fields, while failed responses should include success: false and error fields, maintaining consistent structure across all endpoints.

**Validates: Requirements 11.1, 11.2**

### Property 12: HTTP Status Code Correctness

*For any* API error condition, the system should return the correct HTTP status code: 401 for authentication failures, 403 for authorization failures, 404 for not found, 400 for validation errors, and 500 for server errors.

**Validates: Requirements 11.3, 11.4, 11.5, 11.6, 11.7, 11.8**


## Error Handling

### WebSocket Connection Errors

**Missing Token**:
- Status: 401 Unauthorized
- Response: `{'error': 'Authentication failed'}`
- Action: Close connection immediately

**Invalid Token**:
- Status: 401 Unauthorized
- Response: `{'error': 'Authentication failed'}`
- Action: Close connection immediately

**Expired Token**:
- Status: 401 Unauthorized
- Response: `{'error': 'Authentication failed'}`
- Action: Client should refresh token and reconnect

**Connection Storage Failure**:
- Status: 500 Internal Server Error
- Response: `{'error': 'Failed to store connection'}`
- Action: Close connection, log error, alert monitoring

### REST API Errors

**Authentication Errors (401)**:
- Missing Authorization header
- Invalid JWT token
- Expired JWT token
- Response: `{'success': false, 'error': 'Unauthorized'}`

**Authorization Errors (403)**:
- User lacks required role
- User lacks required permission
- Accessing another user's resources
- Response: `{'success': false, 'error': 'Access denied'}`

**Validation Errors (400)**:
- Missing required fields
- Invalid field formats
- Invalid parameter values
- Response: `{'success': false, 'error': 'Validation failed', 'details': {...}}`

**Not Found Errors (404)**:
- Resource does not exist
- Endpoint does not exist
- Response: `{'success': false, 'error': 'Not found'}`

**Server Errors (500)**:
- DynamoDB operation failures
- Cognito service errors
- Unexpected exceptions
- Response: `{'success': false, 'error': 'Internal server error'}`
- Action: Log error with full context, alert monitoring

### DynamoDB Error Handling

**Throttling**:
- Implement exponential backoff with jitter
- Maximum 3 retry attempts
- Log throttling events for capacity planning

**Item Not Found**:
- Return 404 to client
- Log if unexpected (e.g., referential integrity issue)

**Conditional Check Failed**:
- Return 409 Conflict
- Include details about the conflict

**Service Unavailable**:
- Return 503 Service Unavailable
- Implement circuit breaker pattern
- Alert monitoring immediately

### Cognito Error Handling

**User Not Found**:
- Return 404 for GET operations
- Return 401 for authentication operations

**Invalid Credentials**:
- Return 401 with generic message
- Implement rate limiting to prevent brute force
- Log failed attempts for security monitoring

**User Not Confirmed**:
- Return 403 with specific message
- Provide resend confirmation option

**MFA Required**:
- Return 403 with MFA challenge
- Include challenge parameters in response

## Testing Strategy

### Unit Tests

Unit tests will verify specific examples, edge cases, and error conditions for each component:

**Cognito Client Creation**:
- Test successful client creation with correct configuration
- Test error handling for invalid parameters
- Test idempotency (running script multiple times)

**WebSocket Authentication**:
- Test token extraction from various query string formats
- Test validation with valid Cognito tokens
- Test rejection of invalid/expired tokens
- Test connection storage in DynamoDB
- Test connection cleanup on disconnect

**REST API Endpoints**:
- Test each endpoint with valid requests
- Test authentication enforcement
- Test authorization enforcement (role-based)
- Test input validation
- Test error responses
- Test CORS headers presence

**DynamoDB Queries**:
- Test count queries return correct values
- Test filtering works correctly
- Test pagination works correctly
- Test GSI queries work correctly

**Response Formatting**:
- Test success response format
- Test error response format
- Test CORS headers inclusion

### Property-Based Tests

Property-based tests will verify universal properties across all inputs using Python's Hypothesis library:

**Configuration**: Each property test will run minimum 100 iterations with randomized inputs.

**Test Tags**: Each test will include a comment referencing the design property:
```python
# Feature: frontend-backend-integration, Property 2: WebSocket Token Validation
```

**Property Test 1: Public Cognito Client Configuration**
- Generate: N/A (single configuration check)
- Verify: Client has all required settings
- Tag: Property 1

**Property Test 2: WebSocket Token Validation**
- Generate: Random JWT tokens (valid and invalid)
- Verify: Correct extraction, validation, and response
- Tag: Property 2

**Property Test 3: WebSocket Connection Lifecycle**
- Generate: Random connection IDs and user IDs
- Verify: Storage, retrieval, and cleanup work correctly
- Tag: Property 3

**Property Test 4-9: Endpoint Availability**
- Generate: Random valid request payloads
- Verify: Endpoints exist and return correct format
- Tag: Properties 4-9

**Property Test 10: CORS Headers Consistency**
- Generate: Random requests to all endpoints
- Verify: All responses include CORS headers
- Tag: Property 10

**Property Test 11: Response Format Consistency**
- Generate: Random requests (success and failure cases)
- Verify: Response format matches specification
- Tag: Property 11

**Property Test 12: HTTP Status Code Correctness**
- Generate: Random error conditions
- Verify: Correct status codes returned
- Tag: Property 12

### Integration Tests

Integration tests will verify end-to-end flows:

**Authentication Flow**:
1. Create public Cognito client
2. Register new user
3. Login with credentials
4. Verify JWT token received
5. Use token to access protected endpoint
6. Refresh token
7. Logout

**WebSocket Flow**:
1. Obtain JWT token
2. Connect to WebSocket with token
3. Verify connection stored in DynamoDB
4. Send message
5. Disconnect
6. Verify connection removed from DynamoDB

**Admin Statistics Flow**:
1. Create test data (users, sessions, red flags)
2. Call admin stats endpoint
3. Verify counts are accurate
4. Clean up test data

### Manual Testing Checklist

**Frontend Integration**:
- [ ] Update frontend config with new Cognito client ID
- [ ] Enable real authentication (USE_MOCK_AUTH = false)
- [ ] Uncomment real API integration code
- [ ] Test user registration flow
- [ ] Test user login flow
- [ ] Test WebSocket connection
- [ ] Test session creation
- [ ] Test therapist dashboard
- [ ] Test admin dashboard
- [ ] Verify all API calls work
- [ ] Verify real-time updates work

**Performance Testing**:
- [ ] Test API response times < 200ms
- [ ] Test WebSocket latency < 100ms
- [ ] Test concurrent connections (10+ users)
- [ ] Verify rate limiting works (< 1 RPS per Breaking Barriers constraint)
- [ ] Test DynamoDB query performance

**Security Testing**:
- [ ] Verify JWT tokens expire correctly
- [ ] Verify refresh tokens work
- [ ] Verify unauthorized access is blocked
- [ ] Verify role-based access control works
- [ ] Verify CORS headers prevent unauthorized origins
- [ ] Verify input validation prevents injection attacks

