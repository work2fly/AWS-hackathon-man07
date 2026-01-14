# Integration Quick Start
🏆 Breaking Barriers UK 2026 compliant

## Get Everything Working in 5 Minutes

### Option 1: Automated Setup (Recommended)

```bash
# Run the integration script
./integrate.sh
```

This will:
- ✅ Create Cognito frontend client
- ✅ Update frontend configuration
- ✅ Enable real authentication
- ✅ Create environment files
- ✅ Install dependencies

### Option 2: Manual Setup

#### 1. Setup Cognito (2 min)
```bash
cd backend
./scripts/setup_cognito_frontend_client.sh
```

Save the Client ID that's displayed.

#### 2. Update Frontend Config (1 min)

Edit `ai-therapy-frontend/src/config/aws-config.ts`:
```typescript
userPoolWebClientId: 'YOUR_CLIENT_ID_HERE',  // Paste from step 1
```

Edit `ai-therapy-frontend/src/services/auth.ts`:
```typescript
const USE_MOCK_AUTH = false;  // Change to false
```

#### 3. Start Frontend (2 min)
```bash
cd ai-therapy-frontend
npm install
npm run dev
```

Open http://localhost:3000

## Test the Integration

### 1. Register User
- Click "Sign Up"
- Enter email and password
- Verify email (check console for code)

### 2. Login
- Use your credentials
- Should see dashboard

### 3. Test Features
- **Client**: Start session, test audio
- **Therapist**: View red flags, acknowledge/resolve
- **Admin**: View statistics, check tables

## Troubleshooting

### "Client is configured with secret" error
→ Make sure you ran the Cognito setup script and updated the Client ID

### WebSocket connection fails
→ Check that JWT token is being sent in the connection URL

### API returns 401
→ Verify JWT token is in Authorization header

### CORS errors
→ Check API Gateway CORS configuration

## What's Connected

✅ **Authentication**: Cognito with SRP (secure for browsers)
✅ **REST API**: All endpoints ready (need deployment)
✅ **WebSocket**: JWT authentication enabled
✅ **DynamoDB**: All tables configured
✅ **Frontend**: All components ready

## What Needs Deployment

The backend API handlers are created but need to be deployed:

```bash
cd terraform
terraform apply
```

This will deploy:
- REST API endpoints
- WebSocket handlers
- Lambda functions
- API Gateway routes

## Files Created

### Backend
- `backend/src/lambda_functions/api_handlers.py` - REST API endpoints
- `backend/scripts/setup_cognito_frontend_client.sh` - Cognito setup
- `backend/.env` - Environment variables

### Frontend
- `ai-therapy-frontend/.env.local` - Environment variables
- Updated `aws-config.ts` - AWS configuration
- Updated `auth.ts` - Real authentication enabled

### Documentation
- `FRONTEND_BACKEND_INTEGRATION_GUIDE.md` - Detailed guide
- `INTEGRATION_QUICK_START.md` - This file
- `integrate.sh` - Automated setup script

## API Endpoints Available

### Authentication
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update profile

### Sessions
- `POST /sessions` - Create session
- `GET /sessions/{id}` - Get session
- `POST /sessions/{id}/end` - End session

### Red Flags (Therapist)
- `GET /therapists/{id}/red-flags` - Get flags
- `POST /red-flags/{id}/acknowledge` - Acknowledge
- `POST /red-flags/{id}/resolve` - Resolve

### Admin
- `GET /admin/stats` - System statistics
- `GET /admin/users` - All users
- `GET /admin/sessions` - All sessions

## Next Steps

1. ✅ Run integration script
2. ✅ Test user registration/login
3. ⏳ Deploy backend with Terraform
4. ⏳ Uncomment real API code in frontend
5. ⏳ Test end-to-end workflows
6. ⏳ Add LiveKit for better audio
7. ⏳ Enable Nova Sonic AI responses

## Success Criteria

- [ ] Users can register
- [ ] Users can login
- [ ] JWT tokens work
- [ ] API calls succeed
- [ ] WebSocket connects
- [ ] Red flags display
- [ ] Admin stats show
- [ ] No CORS errors

## Support

See `FRONTEND_BACKEND_INTEGRATION_GUIDE.md` for:
- Detailed troubleshooting
- API reference
- WebSocket messages
- Security best practices
- Performance optimization

---

**🏆 Breaking Barriers UK 2026 Compliant**

Last Updated: January 14, 2026
