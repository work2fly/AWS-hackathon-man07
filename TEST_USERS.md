# Test Users for Ally Platform Demo
**🏆 Breaking Barriers UK 2026 compliant**

---

## Test User Accounts

### 1️⃣ Admin User
**Purpose:** Access admin dashboard, manage users, view analytics

```
Email: admin@ally.io
Password: Admin@2026
First Name: Admin
Last Name: Manager
Role: Admin (auto-detected from email)
```

**What you'll see after login:**
- Admin Dashboard
- User management interface
- System analytics
- Red flag monitoring
- Platform statistics

---

### 2️⃣ Therapist User
**Purpose:** Access therapist dashboard, view client sessions, monitor red flags

```
Email: therapist@ally.io
Password: Therapist@2026
First Name: Dr. Sarah
Last Name: Johnson
Role: Therapist (auto-detected from email)
```

**What you'll see after login:**
- Therapist Dashboard
- Active client sessions
- Red flag alerts
- Session history
- Client progress tracking

---

### 3️⃣ Patient/Client User
**Purpose:** Access therapy sessions, talk to AI therapist

```
Email: patient@ally.io
Password: Patient@2026
First Name: John
Last Name: Doe
Role: Client (default role)
```

**What you'll see after login:**
- AI Therapy Session Interface
- 3D Avatar (Dr. AI Assistant)
- Voice conversation controls
- Session history
- Progress tracking

---

## How to Create These Users

### Step 1: Sign Up Each User
1. Go to http://localhost:3000
2. Click "Create your account"
3. Fill in the details for each user (see above)
4. Click "Join Ally"
5. Account will be auto-confirmed (no email verification needed for hackathon)

### Step 2: Test Login
1. Go to http://localhost:3000
2. Click "Sign In"
3. Enter email and password
4. You'll be redirected to the appropriate dashboard based on role

---

## Role Detection Logic

The system automatically detects user role from email:

```typescript
// Admin: email contains "admin"
admin@ally.io → Admin Dashboard

// Therapist: email contains "therapist" or "dr."
therapist@ally.io → Therapist Dashboard
dr.sarah@ally.io → Therapist Dashboard

// Client: everything else
patient@ally.io → Session Interface
john.doe@ally.io → Session Interface
```

---

## Testing Scenarios

### Scenario 1: Client Session
1. Login as `patient@ally.io`
2. Click "Start Your Session"
3. Test voice conversation
4. Test 3D avatar animations
5. Test language switching

### Scenario 2: Therapist Monitoring
1. Login as `therapist@ally.io`
2. View active sessions
3. Check red flag alerts
4. Review client progress

### Scenario 3: Admin Management
1. Login as `admin@ally.io`
2. View platform statistics
3. Manage users
4. Monitor system health

---

## Current User in Cognito

Check existing users:
```bash
aws cognito-idp list-users \
  --user-pool-id us-west-2_ASOPUuOOV \
  --region us-west-2 \
  --query 'Users[].{Username:Username,Email:Attributes[?Name==`email`].Value|[0],Status:UserStatus}'
```

---

## Notes

- ✅ All passwords follow security requirements (8+ chars, uppercase, lowercase, number, special char)
- ✅ Auto-confirm enabled for hackathon (no email verification needed)
- ✅ Role detection is automatic based on email
- ✅ All users can switch languages (6 languages supported)
- ⚠️ In production, roles should be stored in DynamoDB and fetched via API

---

**Last Updated:** January 14, 2026  
**Status:** Ready for Demo  
**🏆 Breaking Barriers UK 2026 compliant**
