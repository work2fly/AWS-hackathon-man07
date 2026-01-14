# Setup Without AWS CLI Login
🏆 Breaking Barriers UK 2026 compliant

## Quick Setup Using Environment Variables

If you're not logged in to AWS CLI, you can still set up the integration using environment variables.

### Step 1: Get Your Cognito Client ID

You need a Cognito User Pool Client ID. Get it one of these ways:

#### Option A: AWS Console (Recommended)

1. Go to [AWS Console](https://console.aws.amazon.com/cognito)
2. Navigate to **Cognito > User Pools**
3. Select pool: `us-west-2_ASOPUuOOV`
4. Go to **App integration** tab
5. Click **Create app client**
6. Configure:
   - **App type**: Public client
   - **App client name**: `ai-therapy-platform-frontend-client`
   - **Authentication flows**: 
     - ✅ ALLOW_USER_SRP_AUTH
     - ✅ ALLOW_REFRESH_TOKEN_AUTH
   - **Client secret**: Don't generate (leave unchecked)
   - **Token expiration**:
     - Access token: 1 hour
     - ID token: 1 hour
     - Refresh token: 30 days
7. Click **Create app client**
8. **Copy the Client ID** (looks like: `abc123def456ghi789`)

#### Option B: Use Existing Client

If a client already exists:

1. Go to AWS Console > Cognito > User Pools
2. Select pool: `us-west-2_ASOPUuOOV`
3. Go to **App integration** tab
4. Find an existing app client
5. Copy the **Client ID**

#### Option C: Ask Team Member

If someone on your team already created a client, ask them for the Client ID.

### Step 2: Set Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

Set these values in `.env`:

```bash
# Required
AWS_REGION=us-west-2
COGNITO_USER_POOL_ID=us-west-2_ASOPUuOOV
COGNITO_FRONTEND_CLIENT_ID=your-client-id-here  # Paste from Step 1

# Optional (defaults provided)
API_GATEWAY_URL=https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
WEBSOCKET_URL=wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
```

### Step 3: Load Environment Variables

```bash
# Load the variables
source .env

# Verify they're set
echo $COGNITO_FRONTEND_CLIENT_ID
```

### Step 4: Run Integration Script

```bash
./integrate.sh
```

The script will:
- ✅ Use your environment variables
- ✅ Skip AWS CLI calls
- ✅ Configure frontend and backend
- ✅ Create environment files
- ✅ Install dependencies

### Step 5: Start Frontend

```bash
cd ai-therapy-frontend
npm run dev
```

Open http://localhost:3000

---

## Alternative: Manual Configuration

If you prefer to configure manually without the script:

### 1. Create Backend Config

Create `backend/cognito-frontend-config.json`:

```json
{
  "region": "us-west-2",
  "userPoolId": "us-west-2_ASOPUuOOV",
  "userPoolWebClientId": "YOUR_CLIENT_ID_HERE",
  "clientName": "ai-therapy-platform-frontend-client",
  "createdAt": "2026-01-14T12:00:00Z"
}
```

### 2. Create Backend .env

Create `backend/.env`:

```bash
AWS_REGION=us-west-2
COGNITO_USER_POOL_ID=us-west-2_ASOPUuOOV
COGNITO_CLIENT_ID=YOUR_CLIENT_ID_HERE
USERS_TABLE_NAME=ai-therapy-platform-dev-users
SESSIONS_TABLE_NAME=ai-therapy-platform-dev-sessions
RED_FLAGS_TABLE_NAME=ai-therapy-platform-dev-redflags
NOTIFICATIONS_TABLE_NAME=ai-therapy-platform-dev-notifications
WEBSOCKET_API_ENDPOINT=wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
API_GATEWAY_URL=https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
```

### 3. Create Frontend .env.local

Create `ai-therapy-frontend/.env.local`:

```bash
NEXT_PUBLIC_AWS_REGION=us-west-2
NEXT_PUBLIC_COGNITO_USER_POOL_ID=us-west-2_ASOPUuOOV
NEXT_PUBLIC_COGNITO_CLIENT_ID=YOUR_CLIENT_ID_HERE
NEXT_PUBLIC_API_URL=https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
NEXT_PUBLIC_WEBSOCKET_URL=wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev
```

### 4. Update Frontend Config

Edit `ai-therapy-frontend/src/config/aws-config.ts`:

```typescript
export const awsConfig = {
  region: 'us-west-2',
  cognito: {
    userPoolId: 'us-west-2_ASOPUuOOV',
    userPoolWebClientId: 'YOUR_CLIENT_ID_HERE',  // Update this
  },
  apiGateway: {
    restApiUrl: 'https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev',
    websocketUrl: 'wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev',
  },
};
```

### 5. Enable Real Auth

Edit `ai-therapy-frontend/src/services/auth.ts`:

```typescript
const USE_MOCK_AUTH = false;  // Change to false
```

### 6. Install Dependencies

```bash
cd ai-therapy-frontend
npm install
```

### 7. Start Frontend

```bash
npm run dev
```

---

## Troubleshooting

### "Client is configured with secret"

Your client has a secret, which can't be used in browsers. Create a new client:

1. Go to AWS Console > Cognito
2. Create new app client
3. **Important**: Don't generate a client secret
4. Use the new Client ID

### "Invalid authentication flow"

Your client doesn't have SRP auth enabled:

1. Go to AWS Console > Cognito
2. Edit your app client
3. Enable: ALLOW_USER_SRP_AUTH
4. Enable: ALLOW_REFRESH_TOKEN_AUTH

### "Environment variable not set"

Make sure you loaded the `.env` file:

```bash
source .env
echo $COGNITO_FRONTEND_CLIENT_ID  # Should show your client ID
```

### "Cannot find module"

Install dependencies:

```bash
cd ai-therapy-frontend
npm install
```

---

## Verification Checklist

After setup, verify:

- [ ] `.env` file exists with correct values
- [ ] `backend/.env` file created
- [ ] `ai-therapy-frontend/.env.local` file created
- [ ] `backend/cognito-frontend-config.json` file created
- [ ] Frontend config updated with Client ID
- [ ] `USE_MOCK_AUTH = false` in auth.ts
- [ ] Dependencies installed (`node_modules` exists)
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:3000

---

## Next Steps

1. **Deploy Backend** (if not already done):
   ```bash
   cd backend
   python3 scripts/package_lambdas.py
   cd ../terraform
   terraform apply
   ```

2. **Uncomment Frontend Code**:
   Search for these markers and uncomment:
   - `REAL COGNITO CODE (COMMENTED OUT`
   - `REAL API INTEGRATION (COMMENTED OUT`
   - `REAL WEBSOCKET CODE (COMMENTED OUT`

3. **Test Integration**:
   - Register a user
   - Login
   - Start session
   - Test therapist dashboard
   - Test admin dashboard

---

## Support

For issues:
- Check CloudWatch logs
- Verify Cognito client configuration
- Test with mock auth first
- See `FRONTEND_BACKEND_INTEGRATION_GUIDE.md`

---

**🏆 Breaking Barriers UK 2026 Compliant**

**Created:** January 14, 2026
**Last Updated:** January 14, 2026
