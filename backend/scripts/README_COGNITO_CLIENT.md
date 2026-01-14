# Public Cognito Client Setup

🏆 Breaking Barriers UK 2026 compliant

## Overview

This script creates a public Cognito User Pool Client without a client secret, suitable for browser-based frontend applications. The client is configured with secure authentication flows (SRP) and appropriate OAuth settings.

## Prerequisites

1. AWS credentials configured (via AWS CLI or environment variables)
2. Cognito User Pool already deployed (via Terraform)
3. Python 3.8+ with boto3 installed

## Usage

### Option 1: Automatic Discovery

If your user pool name contains "ai-therapy-platform", the script will find it automatically:

```bash
cd backend
python scripts/create_public_cognito_client.py
```

### Option 2: Specify User Pool ID

Set the `USER_POOL_ID` environment variable:

```bash
export USER_POOL_ID=us-west-2_YourPoolId
python scripts/create_public_cognito_client.py
```

### Option 3: Get User Pool ID from Terraform

After deploying with Terraform:

```bash
cd terraform
export USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
cd ../backend
python scripts/create_public_cognito_client.py
```

## What the Script Does

1. **Creates Public Client**: Configures a Cognito client without a client secret
2. **Configures Auth Flows**: Enables SRP and refresh token authentication
3. **Sets OAuth**: Configures authorization code and implicit flows
4. **Sets Token Validity**: 1 hour for access/ID tokens, 30 days for refresh tokens
5. **Configures Attributes**: Sets read/write permissions for user attributes
6. **Verifies Configuration**: Runs comprehensive checks to ensure all requirements are met
7. **Outputs Configuration**: Provides frontend configuration values

## Output

The script will output:

```
User Pool ID: us-west-2_YourPoolId
Client ID: 1234567890abcdefghijklmnop
Region: us-west-2

Add these to your frontend configuration:

NEXT_PUBLIC_USER_POOL_ID=us-west-2_YourPoolId
NEXT_PUBLIC_CLIENT_ID=1234567890abcdefghijklmnop
NEXT_PUBLIC_AWS_REGION=us-west-2
```

The configuration is also saved to `cognito-client-config.json`.

## Configuration Details

The created client has the following configuration:

### Authentication Flows
- ✅ SRP Authentication (ALLOW_USER_SRP_AUTH) - Secure for public clients
- ✅ Refresh Token Authentication (ALLOW_REFRESH_TOKEN_AUTH)
- ❌ Password Authentication (ALLOW_USER_PASSWORD_AUTH) - Disabled for security

### OAuth Configuration
- **Flows**: Authorization Code, Implicit
- **Scopes**: email, openid, profile
- **Callback URLs**: http://localhost:3000/callback, http://localhost:3000/
- **Logout URLs**: http://localhost:3000/logout, http://localhost:3000/

### Token Validity
- **Access Token**: 1 hour
- **ID Token**: 1 hour
- **Refresh Token**: 30 days

### User Attributes
- **Read**: email, email_verified, custom:role, custom:language_preference
- **Write**: email, custom:role, custom:language_preference

## Frontend Integration

After running the script, update your frontend configuration:

### Next.js (.env.local)

```env
NEXT_PUBLIC_USER_POOL_ID=us-west-2_YourPoolId
NEXT_PUBLIC_CLIENT_ID=1234567890abcdefghijklmnop
NEXT_PUBLIC_AWS_REGION=us-west-2
```

### React/Vue/Angular

Update your AWS Amplify or Cognito configuration:

```javascript
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'us-west-2_YourPoolId',
      userPoolClientId: '1234567890abcdefghijklmnop',
      region: 'us-west-2'
    }
  }
});
```

## Verification

The script automatically verifies the configuration against all requirements:

- ✅ No client secret
- ✅ SRP auth enabled
- ✅ Refresh token auth enabled
- ✅ Password auth disabled
- ✅ OAuth code flow enabled
- ✅ OAuth implicit flow enabled
- ✅ Email scope enabled
- ✅ OpenID scope enabled
- ✅ Profile scope enabled
- ✅ Access token validity = 1 hour
- ✅ ID token validity = 1 hour
- ✅ Refresh token validity = 30 days
- ✅ Can read email
- ✅ Can read email_verified
- ✅ Can read role
- ✅ Can read language_preference
- ✅ Can write email
- ✅ Can write role
- ✅ Can write language_preference

## Idempotency

The script is idempotent - if a client with the same name already exists, it will:
1. Detect the existing client
2. Retrieve its configuration
3. Verify the configuration
4. Output the existing client ID

This means you can safely run the script multiple times.

## Troubleshooting

### Error: Could not find User Pool ID

**Solution**: Ensure your Cognito User Pool is deployed and either:
- Set the `USER_POOL_ID` environment variable
- Ensure the pool name contains "ai-therapy-platform"

### Error: Unable to locate credentials

**Solution**: Configure AWS credentials:

```bash
aws configure
# OR
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

### Error: Client limit exceeded

**Solution**: Delete unused clients from the Cognito User Pool:

```bash
aws cognito-idp list-user-pool-clients --user-pool-id us-west-2_YourPoolId
aws cognito-idp delete-user-pool-client --user-pool-id us-west-2_YourPoolId --client-id ClientIdToDelete
```

## Security Notes

🔒 **No Client Secret**: Public clients (browser-based apps) should never have a client secret, as it cannot be kept secure in client-side code.

🔒 **SRP Authentication**: Secure Remote Password (SRP) protocol provides secure authentication without transmitting passwords.

🔒 **Token Expiry**: Short-lived access tokens (1 hour) minimize the impact of token theft. Refresh tokens (30 days) allow users to stay logged in.

🔒 **CORS**: Remember to configure CORS on your API Gateway to allow requests from your frontend domain.

## Breaking Barriers UK 2026 Compliance

✅ Uses us-west-2 region (Oregon)
✅ No PII in configuration
✅ Follows AWS security best practices
✅ Documented for team collaboration

## Related Files

- **Script**: `backend/scripts/create_public_cognito_client.py`
- **Tests**: `backend/tests/test_cognito_client_properties.py`
- **Terraform**: `terraform/cognito.tf`
- **Design**: `.kiro/specs/frontend-backend-integration/design.md`
- **Requirements**: `.kiro/specs/frontend-backend-integration/requirements.md`
