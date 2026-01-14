# Frontend-Backend Integration Guide
🏆 Breaking Barriers UK 2026 compliant

## Quick Start - Get Everything Working in 15 Minutes

This guide will help you connect the frontend and backend to create a fully functional AI Therapy Platform.

## Prerequisites

- ✅ Backend code committed
- ✅ Frontend code committed
- ✅ AWS account with Breaking Barriers UK 2026 credentials
- ✅ Terraform infrastructure deployed

## Step 1: Setup Cognito Frontend Client (5 minutes)

The current Cognito client has a secret which cannot be used in browsers. We need to create a frontend-compatible client.

```bash
# Navigate to backend directory
cd backend

# Make script executable
chmod +x scripts/setup_cognito_frontend_client.sh

# Run the setup script
./scripts/setup_cognito_frontend_client.sh
```

**Expected Output:**
```
✅ Frontend client created successfully!

Client ID: abc123xyz456...
User Pool ID: us-west-2_ASOPUuOOV
Region: us-west-2
```

**Save the Client ID** - you'll need it in the next step!

## Step 2: Update Frontend Configuration (2 minutes)

### 2.1 Update AWS Config

Edit `ai-therapy-frontend/src/config/aws-config.ts`:

```typescript
export const awsConfig = {
  cognito: {
    region: 'us-west-2',
    userPoolId: 'us-west-2_ASOPUuOOV',
    userPoolWebClientId: 'YOUR_NEW_CLIENT_ID_HERE',  // ← Paste Client ID from Step 1
  },
  apiGateway: {
    region: 'us-west-2',
    restApiUrl: 'https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev',
    websocketUrl: 'wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev'
  }
};
```

### 2.2 Enable Real Authentication

Edit `ai-therapy-frontend/src/services/auth.ts`:

```typescript
// Change this line from true to false:
const USE_MOCK_AUTH = false;  // ← Change to false
```

### 2.3 Uncomment Real Code

Search for these comments in the frontend and uncomment the code:

```typescript
// REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
// REAL API INTEGRATION (COMMENTED OUT - WAITING FOR BACKEND)
// REAL WEBSOCKET CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO SETUP WEBSOCKET AUTH)
```

**Files to update:**
- `src/services/auth.ts` - Uncomment Cognito authentication
- `src/services/api.ts` - Uncomment REST API calls
- `src/services/websocket.ts` - Uncomment WebSocket connection
- `src/components/TherapistDashboard.tsx` - Uncomment real data fetching
- `src/components/AdminDashboard.tsx` - Uncomment real data fetching

## Step 3: Deploy Backend API Endpoints (5 minutes)

### 3.1 Update Terraform for API Endpoints

The new API handlers need to be deployed. Update `terraform/api_gateway.tf`:

```hcl
# Add new Lambda functions for API handlers
resource "aws_lambda_function" "api_handlers" {
  filename         = "${path.module}/../backend/lambda_packages/api_handlers.zip"
  function_name    = "${var.project_name}-${var.environment}-api-handlers"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_functions.api_handlers.handler"
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 512

  environment {
    variables = {
      ENVIRONMENT = var.environment
      USERS_TABLE_NAME = aws_dynamodb_table.users.name
      SESSIONS_TABLE_NAME = aws_dynamodb_table.sessions.name
      RED_FLAGS_TABLE_NAME = aws_dynamodb_table.red_flags.name
      NOTIFICATIONS_TABLE_NAME = aws_dynamodb_table.notifications.name
    }
  }
}

# Add API Gateway routes
resource "aws_apigatewayv2_route" "get_profile" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /auth/profile"
  target    = "integrations/${aws_apigatewayv2_integration.api_handlers.id}"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.cognito.id
}

# Add more routes for all endpoints...
```

### 3.2 Package and Deploy

```bash
cd backend

# Package Lambda functions
python scripts/package_lambdas.py

# Deploy with Terraform
cd ../terraform
terraform apply
```

## Step 4: Test the Integration (3 minutes)

### 4.1 Start Frontend

```bash
cd ai-therapy-frontend
npm install
npm run dev
```

Open http://localhost:3000

### 4.2 Test User Registration

1. Click "Sign Up"
2. Enter email and password
3. Verify email (check console for verification code in dev)
4. Login with credentials

### 4.3 Test Client Session

1. Login as client
2. Click "Start Session"
3. Verify WebSocket connection (check browser console)
4. Test audio controls

### 4.4 Test Therapist Dashboard

1. Create therapist user (or use admin to change role)
2. Login as therapist
3. View red flags dashboard
4. Test acknowledge/resolve functionality

### 4.5 Test Admin Dashboard

1. Login as admin
2. View system statistics
3. Check DynamoDB tables display
4. Verify real-time updates

## Troubleshooting

### Issue: "NotAuthorizedException: Client is configured with secret"

**Solution:** You're still using the old client ID. Make sure you:
1. Ran the setup script in Step 1
2. Updated the Client ID in `aws-config.ts`
3. Restarted the frontend dev server

### Issue: "WebSocket connection failed"

**Solution:** Check that:
1. WebSocket URL is correct in `aws-config.ts`
2. JWT token is being sent in query parameter
3. WebSocket Lambda has JWT verification enabled
4. Check CloudWatch logs for WebSocket Lambda

### Issue: "API returns 401 Unauthorized"

**Solution:**
1. Verify JWT token is in Authorization header
2. Check Cognito authorizer is configured in API Gateway
3. Verify user has correct role for endpoint
4. Check CloudWatch logs for API Lambda

### Issue: "CORS errors in browser"

**Solution:**
1. Verify CORS headers in Lambda responses
2. Check API Gateway CORS configuration
3. Ensure OPTIONS method is configured

## API Endpoints Reference

### Authentication
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile

### Sessions
- `POST /sessions` - Create session
- `GET /sessions/{sessionId}` - Get session
- `POST /sessions/{sessionId}/end` - End session
- `GET /users/{userId}/sessions` - Get user sessions

### Red Flags (Therapist)
- `GET /therapists/{therapistId}/red-flags` - Get red flags
- `POST /red-flags/{flagId}/acknowledge` - Acknowledge flag
- `POST /red-flags/{flagId}/resolve` - Resolve flag

### Notifications
- `GET /users/{userId}/notifications` - Get notifications
- `POST /notifications/{notificationId}/read` - Mark as read

### Admin
- `GET /admin/stats` - System statistics
- `GET /admin/users` - All users
- `GET /admin/sessions` - All sessions
- `GET /admin/red-flags` - All red flags

## WebSocket Messages

### Client → Server

```json
{
  "action": "audio",
  "data": {
    "sessionId": "session_123",
    "audioData": "base64_encoded_audio",
    "timestamp": "2026-01-14T10:30:00Z"
  }
}
```

### Server → Client

```json
{
  "type": "audio_response",
  "data": {
    "sessionId": "session_123",
    "audioData": "base64_encoded_audio",
    "transcript": "I understand how you're feeling...",
    "timestamp": "2026-01-14T10:30:01Z"
  }
}
```

### Red Flag Notification

```json
{
  "type": "red_flag",
  "data": {
    "sessionId": "session_123",
    "flagId": "flag_456",
    "severity": "critical",
    "type": "suicidal_ideation",
    "timestamp": "2026-01-14T10:30:00Z"
  }
}
```

## Environment Variables

### Backend (.env)

```bash
AWS_DEFAULT_REGION=us-west-2
COGNITO_USER_POOL_ID=us-west-2_ASOPUuOOV
COGNITO_CLIENT_ID=your_frontend_client_id
USERS_TABLE_NAME=ai-therapy-platform-dev-users
SESSIONS_TABLE_NAME=ai-therapy-platform-dev-sessions
RED_FLAGS_TABLE_NAME=ai-therapy-platform-dev-redflags
NOTIFICATIONS_TABLE_NAME=ai-therapy-platform-dev-notifications
WEBSOCKET_API_ENDPOINT=wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_AWS_REGION=us-west-2
NEXT_PUBLIC_COGNITO_USER_POOL_ID=us-west-2_ASOPUuOOV
NEXT_PUBLIC_COGNITO_CLIENT_ID=your_frontend_client_id
NEXT_PUBLIC_API_URL=https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
NEXT_PUBLIC_WEBSOCKET_URL=wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
```

## Testing Checklist

- [ ] User registration works
- [ ] User login works
- [ ] JWT tokens are issued
- [ ] API calls include Authorization header
- [ ] WebSocket connects with token
- [ ] Client can start session
- [ ] Audio streaming works
- [ ] Red flags are detected
- [ ] Therapist receives notifications
- [ ] Therapist can acknowledge/resolve flags
- [ ] Admin sees system statistics
- [ ] Admin can view all data
- [ ] CORS works correctly
- [ ] Error handling works
- [ ] Loading states display correctly

## Performance Considerations

### Breaking Barriers UK 2026 Constraints

- ✅ **Rate Limiting**: Stay below 1 RPS for Bedrock
- ✅ **Region**: Use us-west-2 only
- ✅ **Instance Types**: Avoid prohibited instance types
- ✅ **Cost Optimization**: Use serverless where possible

### Optimization Tips

1. **API Caching**: Enable API Gateway caching for GET requests
2. **Connection Pooling**: Reuse DynamoDB connections
3. **Lazy Loading**: Load data on demand in frontend
4. **Debouncing**: Debounce API calls in frontend
5. **WebSocket Batching**: Batch audio chunks for efficiency

## Security Best Practices

1. **Never expose secrets**: Use environment variables
2. **Validate all inputs**: Server-side validation required
3. **Use HTTPS/WSS**: Always use secure connections
4. **Rotate credentials**: Regular credential rotation
5. **Monitor logs**: Check CloudWatch for suspicious activity
6. **Rate limiting**: Implement per-user rate limits
7. **CORS**: Configure strict CORS policies for production

## Next Steps

Once integration is working:

1. **Add LiveKit**: Integrate LiveKit for better audio quality
2. **Add Nova Sonic**: Enable real AI responses
3. **Add AgentCore**: Enable memory persistence
4. **Performance Testing**: Test with multiple concurrent users
5. **Security Audit**: Review all security configurations
6. **Documentation**: Document any custom configurations
7. **Demo Preparation**: Prepare demo scenarios

## Support

If you encounter issues:

1. Check CloudWatch logs for Lambda functions
2. Check browser console for frontend errors
3. Verify all environment variables are set
4. Test API endpoints with Postman/curl
5. Check DynamoDB tables have correct data

## Success Criteria

✅ Users can register and login
✅ WebSocket connections work
✅ API endpoints return data
✅ Red flags are detected and displayed
✅ Therapist dashboard shows real data
✅ Admin dashboard shows system stats
✅ No CORS errors
✅ No authentication errors
✅ Performance meets requirements

---

**🏆 Breaking Barriers UK 2026 Compliant**

This integration follows all hackathon constraints and security requirements.

**Last Updated:** January 14, 2026
**Status:** Ready for Integration
