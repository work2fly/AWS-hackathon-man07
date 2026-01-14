# Frontend Cognito Client Setup Guide

🏆 Breaking Barriers UK 2026 compliant

## Quick Start

A public Cognito client has been created for the frontend application. This client is configured without a client secret, making it suitable for browser-based applications.

## Running the Setup Script

### Prerequisites
- AWS credentials configured
- Cognito User Pool deployed via Terraform

### Execute the Script

```bash
cd backend

# Option 1: Automatic discovery (if pool name contains "ai-therapy-platform")
python scripts/create_public_cognito_client.py

# Option 2: Specify User Pool ID
export USER_POOL_ID=$(cd ../terraform && terraform output -raw cognito_user_pool_id)
python scripts/create_public_cognito_client.py
```

### Expected Output

```
🏆 Breaking Barriers UK 2026 - Public Cognito Client Setup
============================================================
User Pool ID: us-west-2_YourPoolId
Client ID: 1234567890abcdefghijklmnop
Region: us-west-2

🔍 Verifying client configuration...
  ✅ No client secret
  ✅ SRP auth enabled
  ✅ Refresh token auth enabled
  ✅ Password auth disabled
  ✅ OAuth code flow enabled
  ✅ OAuth implicit flow enabled
  ✅ Email scope enabled
  ✅ OpenID scope enabled
  ✅ Profile scope enabled
  ✅ Access token validity = 1 hour
  ✅ ID token validity = 1 hour
  ✅ Refresh token validity = 30 days
  ✅ Can read email
  ✅ Can read email_verified
  ✅ Can read role
  ✅ Can read language_preference
  ✅ Can write email
  ✅ Can write role
  ✅ Can write language_preference

✅ All configuration checks passed!

============================================================
📋 FRONTEND CONFIGURATION
============================================================
User Pool ID: us-west-2_YourPoolId
Client ID: 1234567890abcdefghijklmnop
Region: us-west-2

Add these to your frontend configuration:

NEXT_PUBLIC_USER_POOL_ID=us-west-2_YourPoolId
NEXT_PUBLIC_CLIENT_ID=1234567890abcdefghijklmnop
NEXT_PUBLIC_AWS_REGION=us-west-2
============================================================

💾 Configuration saved to: cognito-client-config.json
```

## Frontend Integration Steps

### Step 1: Update Environment Variables

Create or update `ai-therapy-frontend/.env.local`:

```env
# Cognito Configuration
NEXT_PUBLIC_USER_POOL_ID=us-west-2_YourPoolId
NEXT_PUBLIC_CLIENT_ID=1234567890abcdefghijklmnop
NEXT_PUBLIC_AWS_REGION=us-west-2

# Switch from mock to real authentication
USE_MOCK_AUTH=false
```

### Step 2: Update AWS Config

Update `ai-therapy-frontend/src/config/aws-config.ts`:

```typescript
export const awsConfig = {
  Auth: {
    Cognito: {
      userPoolId: process.env.NEXT_PUBLIC_USER_POOL_ID!,
      userPoolClientId: process.env.NEXT_PUBLIC_CLIENT_ID!,
      region: process.env.NEXT_PUBLIC_AWS_REGION!,
      
      // Authentication flow configuration
      authenticationFlowType: 'USER_SRP_AUTH',
      
      // OAuth configuration
      oauth: {
        domain: `${process.env.NEXT_PUBLIC_COGNITO_DOMAIN}`,
        scope: ['email', 'openid', 'profile'],
        redirectSignIn: 'http://localhost:3000/callback',
        redirectSignOut: 'http://localhost:3000/logout',
        responseType: 'code'
      }
    }
  }
};
```

### Step 3: Uncomment Real Authentication Code

In your authentication service files, uncomment the real AWS Cognito integration code and comment out the mock authentication:

```typescript
// Before
// import { mockAuth } from './mock-auth';
// export const auth = mockAuth;

// After
import { Amplify } from 'aws-amplify';
import { awsConfig } from '../config/aws-config';

Amplify.configure(awsConfig);

export const auth = {
  signUp: async (email, password, attributes) => {
    // Real Cognito sign up
  },
  signIn: async (email, password) => {
    // Real Cognito sign in
  },
  // ... other methods
};
```

### Step 4: Test Authentication Flow

1. **Sign Up**: Test user registration
   ```typescript
   await auth.signUp('test@example.com', 'SecurePassword123!', {
     'custom:role': 'client',
     'custom:language_preference': 'en'
   });
   ```

2. **Confirm Sign Up**: Verify email with code
   ```typescript
   await auth.confirmSignUp('test@example.com', '123456');
   ```

3. **Sign In**: Test login
   ```typescript
   const session = await auth.signIn('test@example.com', 'SecurePassword123!');
   ```

4. **Get Current User**: Verify session
   ```typescript
   const user = await auth.getCurrentUser();
   console.log(user);
   ```

## Client Configuration Details

### Authentication Flows
- ✅ **SRP Authentication** (ALLOW_USER_SRP_AUTH) - Secure Remote Password protocol
- ✅ **Refresh Token** (ALLOW_REFRESH_TOKEN_AUTH) - Token refresh capability
- ❌ **Password Auth** (ALLOW_USER_PASSWORD_AUTH) - Disabled for security

### OAuth Configuration
- **Flows**: Authorization Code, Implicit
- **Scopes**: email, openid, profile
- **Callback URLs**: http://localhost:3000/callback, http://localhost:3000/
- **Logout URLs**: http://localhost:3000/logout, http://localhost:3000/

### Token Validity
- **Access Token**: 1 hour (short-lived for security)
- **ID Token**: 1 hour (short-lived for security)
- **Refresh Token**: 30 days (allows persistent sessions)

### User Attributes
- **Readable**: email, email_verified, custom:role, custom:language_preference
- **Writable**: email, custom:role, custom:language_preference

## Security Best Practices

### 1. No Client Secret
✅ Public clients (browser apps) should never have a client secret
- Client secrets cannot be kept secure in client-side code
- SRP authentication provides security without secrets

### 2. Token Storage
⚠️ Store tokens securely:
- Use `sessionStorage` for short-lived sessions
- Use `localStorage` only if persistent login is required
- Never store tokens in cookies without HttpOnly flag

### 3. Token Refresh
✅ Implement automatic token refresh:
```typescript
// Refresh token before expiry
const refreshSession = async () => {
  const session = await Auth.currentSession();
  return session;
};
```

### 4. CORS Configuration
⚠️ Ensure API Gateway has proper CORS headers:
- `Access-Control-Allow-Origin`: Your frontend domain
- `Access-Control-Allow-Methods`: GET, POST, PUT, DELETE, OPTIONS
- `Access-Control-Allow-Headers`: Authorization, Content-Type

## Troubleshooting

### Issue: "User pool client does not exist"
**Solution**: Run the setup script to create the client

### Issue: "Invalid authentication flow"
**Solution**: Ensure you're using SRP authentication, not password authentication

### Issue: "Token expired"
**Solution**: Implement token refresh logic in your frontend

### Issue: "CORS error"
**Solution**: Verify API Gateway CORS configuration matches frontend domain

### Issue: "Cannot read custom attributes"
**Solution**: Ensure attributes are prefixed with `custom:` (e.g., `custom:role`)

## Testing Checklist

- [ ] Environment variables configured
- [ ] AWS config updated
- [ ] Mock authentication disabled
- [ ] Real authentication code uncommented
- [ ] Sign up flow works
- [ ] Email verification works
- [ ] Sign in flow works
- [ ] Token refresh works
- [ ] Sign out works
- [ ] Protected routes work
- [ ] User attributes readable
- [ ] User attributes writable

## Next Steps

1. ✅ Run the setup script to create the public client
2. ✅ Update frontend environment variables
3. ✅ Update AWS configuration
4. ✅ Uncomment real authentication code
5. ✅ Test authentication flows
6. ✅ Test WebSocket connection with JWT token
7. ✅ Test API calls with Authorization header

## Support

For issues or questions:
- Check `backend/scripts/README_COGNITO_CLIENT.md` for detailed documentation
- Review property tests in `backend/tests/test_cognito_client_properties.py`
- Refer to design document in `.kiro/specs/frontend-backend-integration/design.md`

## Breaking Barriers UK 2026 Compliance

✅ Uses us-west-2 region (Oregon)
✅ No PII in configuration
✅ Follows AWS security best practices
✅ Secure authentication flows (SRP)
✅ Appropriate token expiry times
✅ Documented for team collaboration
