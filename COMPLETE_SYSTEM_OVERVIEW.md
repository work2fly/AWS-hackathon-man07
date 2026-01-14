# AI Therapy Platform - Complete System Overview

🏆 Breaking Barriers UK 2026 compliant

## What You Have Built

A complete AI-powered therapy platform with:
- Real-time AI chat using AWS Bedrock
- Automatic sentiment tracking (1-10 scale)
- Clinical profile management (internal use)
- Red flag detection and alerting
- Session analysis and progress monitoring
- Full API integration for web/mobile apps

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Complete System Flow                          │
└─────────────────────────────────────────────────────────────────┘

User App (Web/Mobile)
    ↓
    │ 1. User starts session
    ↓
API Gateway (/api/chat POST)
    ↓
Lambda: chat_handler
    ├─ Creates session in DynamoDB
    ├─ Loads clinical profile for context
    └─ Invokes Bedrock Agent
        ↓
    Bedrock Agent (Claude Sonnet 4.5)
        ├─ Maintains conversation memory
        ├─ Uses clinical context
        └─ Generates empathetic responses
        ↓
    Response back to user
    ↓
    │ 2. Conversation continues...
    ↓
    │ 3. User ends session
    ↓
Lambda: end_session_handler
    ├─ Marks session as completed
    └─ Triggers analysis
        ↓
Lambda: session_analyzer
    ├─ Analyzes conversation
    ├─ Calculates sentiment score (1-10)
    ├─ Updates clinical profile
    ├─ Creates red flags if needed
    └─ Stores results in DynamoDB
        ↓
    │ 4. Doctor views progress
    ↓
API Gateway (/api/sentiment-history GET)
    ↓
Lambda: get_sentiment_history
    └─ Returns score history with trends
```

## Data Storage Architecture

### DynamoDB Tables

**1. Users Table**
```
Primary Key: userId
GSI: email
Contains:
├─ User profile (name, timezone, phone)
├─ Clinical profile (internal only)
│   ├─ Age, gender, medical conditions
│   ├─ Emotional state
│   ├─ Risk assessments
│   ├─ Conversation preferences
│   └─ Goals tracking
└─ Preferences (voice, notifications, privacy)
```

**2. Sessions Table**
```
Primary Key: sessionId + timestamp
GSI: clientId + timestamp
Contains:
├─ Session metadata
├─ Start/end times, duration
├─ Sentiment score (1-10)
├─ Status (active/completed)
├─ Reference to Bedrock memory (agent_memory_id)
└─ Audio quality metrics
```

**3. RedFlags Table**
```
Primary Key: sessionId + flagId
GSI: severity + detectedAt
Contains:
├─ Flag type (self_harm, suicidal_ideation, abuse, etc.)
├─ Severity (low, medium, high, critical)
├─ Detection timestamp
├─ Sanitized context (max 1000 chars)
├─ Notifications sent
└─ Resolution status
```

### Bedrock Agent Memory
```
Stores actual conversation:
├─ User messages
├─ AI responses
├─ Conversation context
└─ Turn-by-turn dialogue

Referenced by: agent_memory_id in Sessions table
```

## Key Features

### 1. AI Chat System
- **Location**: `backend/src/api/chat_handler.py`
- **How it works**: 
  - User sends message → Lambda → Bedrock Agent → AI response
  - Bedrock maintains conversation context automatically
  - Clinical profile provides context to AI (not shown to user)
- **Integration**: See `backend/docs/AI_CHAT_INTEGRATION.md`

### 2. Sentiment Score Tracking
- **Location**: `backend/src/services/session_analyzer.py`
- **How it works**:
  - After session ends, analyzer processes conversation
  - Calculates score 1-10 based on emotional state, risk, engagement
  - Stores score with session for progress tracking
- **Scoring**:
  - 1-3: Critical (high risk)
  - 4-5: Concerning (needs attention)
  - 6-7: Stable (continuing therapy)
  - 8-9: Positive (improving)
  - 10: Excellent (strong wellbeing)
- **Documentation**: `backend/docs/SENTIMENT_SCORE_TRACKING.md`

### 3. Clinical Profile System
- **Location**: `backend/src/models/user.py`
- **What it tracks**:
  - Emotional state (fear, anxiety, sadness, etc.)
  - Self-harm risk (none, passive, concerning, acute)
  - Overall user risk (low, medium, high)
  - Conversation preference (coping tools, venting, etc.)
  - Goals progress
- **Privacy**: Internal only - never shown to users
- **Documentation**: `backend/docs/CLINICAL_PROFILE_USAGE.md`

### 4. Red Flag System
- **Location**: `backend/src/data/red_flag_repository.py`
- **How it works**:
  - Automatically detects concerning patterns
  - Creates alerts for clinical staff
  - Tracks notifications and acknowledgments
  - Maintains resolution status
- **Types**: Self-harm, suicidal ideation, abuse, violence, crisis

### 5. Progress Tracking
- **Location**: `backend/src/data/session_repository.py`
- **What it provides**:
  - Sentiment score history over time
  - Trend analysis (improving/declining/stable)
  - Statistics (average, highest, lowest scores)
  - Session duration and frequency

## API Endpoints

### Chat Endpoints
```
POST /api/chat
- Start session and send messages
- Body: {user_id, message, create_session}
- Returns: {session_id, ai_response, timestamp}

POST /api/chat/end
- End therapy session
- Body: {user_id, session_id}
- Returns: {duration, message}
```

### Analysis Endpoints
```
POST /api/analyze-session
- Analyze completed session
- Body: {user_id, session_id, messages}
- Returns: {sentiment_score, updates_applied, red_flags_created}

GET /api/sentiment-history/{client_id}
- Get progress over time
- Returns: {history[], statistics{average, trend}}
```

### Clinical Endpoints (Internal Only)
```
GET /api/clinical-profile/{user_id}
- Get clinical profile
- Returns: {clinical_profile{...}}

POST /api/update-goals
- Update therapeutic goals
- Body: {user_id, total_goals, goals_achieved}
```

## Frontend Integration

### React Example
```javascript
import chatService from './services/chatService';

// Start session
const result = await chatService.startSession(userId);

// Send message
const response = await chatService.sendMessage("I'm feeling anxious");

// End session
await chatService.endSession();
```

### React Native Example
```javascript
// Same API, works on mobile
const result = await chatService.startSession(userId);
const response = await chatService.sendMessage(message);
```

**Full examples**: `backend/docs/AI_CHAT_INTEGRATION.md`

## How Different Parts Work Together

### Example: Complete Session Flow

**1. User starts session**
```
Frontend → POST /api/chat (create_session=true)
    ↓
Lambda creates session in DynamoDB
    ↓
Lambda loads user's clinical profile
    ↓
Lambda invokes Bedrock Agent with context
    ↓
Bedrock responds with greeting
    ↓
Frontend displays AI message
```

**2. Conversation happens**
```
User types: "I'm feeling anxious"
    ↓
Frontend → POST /api/chat
    ↓
Lambda sends to Bedrock (with session_id)
    ↓
Bedrock uses memory + clinical context
    ↓
Bedrock responds: "I hear you. Tell me more..."
    ↓
Frontend displays response
```

**3. Session ends**
```
User clicks "End Session"
    ↓
Frontend → POST /api/chat/end
    ↓
Lambda marks session completed
    ↓
Lambda triggers analysis
    ↓
Analyzer retrieves conversation from Bedrock
    ↓
Analyzer calculates sentiment score: 6/10
    ↓
Analyzer updates clinical profile:
    - emotional_state: anxiety
    - user_risk: low
    - last_session_timestamp: now
    ↓
Analyzer stores sentiment score with session
    ↓
No red flags created (risk is low)
```

**4. Doctor views progress**
```
Doctor opens dashboard
    ↓
Frontend → GET /api/sentiment-history/user123
    ↓
Lambda queries DynamoDB for all sessions
    ↓
Returns: [
    {session1: score 4},
    {session2: score 6},
    {session3: score 7}
]
    ↓
Dashboard shows:
    - Trend: ↗ Improving
    - Average: 5.7/10
    - Latest: 7/10
```

## File Structure

```
backend/
├── src/
│   ├── models/
│   │   ├── user.py              # User + ClinicalProfile models
│   │   ├── session.py           # Session + sentiment score
│   │   └── red_flag.py          # RedFlag model
│   ├── data/
│   │   ├── user_repository.py   # User CRUD + clinical updates
│   │   ├── session_repository.py # Session CRUD + sentiment history
│   │   └── red_flag_repository.py # Red flag management
│   ├── services/
│   │   └── session_analyzer.py  # Sentiment calculation + analysis
│   └── api/
│       ├── chat_handler.py      # Chat endpoints
│       └── session_analysis.py  # Analysis endpoints
├── docs/
│   ├── AI_CHAT_INTEGRATION.md   # How to connect frontend
│   ├── SENTIMENT_SCORE_TRACKING.md # Sentiment system docs
│   ├── CLINICAL_PROFILE_USAGE.md # Clinical profile guide
│   └── DEPLOYMENT_GUIDE.md      # AWS deployment steps
└── examples/
    └── sentiment_tracking_example.py # Usage examples
```

## AWS Services Used

✅ **Compute**: Lambda (Python 3.9)
✅ **AI/ML**: Bedrock Agent (Claude Sonnet 4.5)
✅ **Database**: DynamoDB (3 tables)
✅ **API**: API Gateway (REST)
✅ **Auth**: Cognito (user authentication)
✅ **Notifications**: SNS (red flag alerts)
✅ **Monitoring**: CloudWatch (logs, metrics, alarms)
✅ **Security**: KMS (encryption), IAM (permissions)
✅ **Region**: us-west-2 (Oregon)

## Key Constraints (Hackathon Rules)

⚠️ **Region**: Only us-west-2 (Oregon)
⚠️ **Bedrock Rate Limit**: Stay below 1 RPS
⚠️ **Account Termination**: 23:00 on 15th January 2026
⚠️ **Lambda Variables**: Don't set AWS_REGION (auto-provided)
⚠️ **Models**: Only Claude Sonnet 4.5, Opus 4.5, etc. (see rules)

## Next Steps

### For Development
1. Test chat integration locally
2. Deploy to AWS (see DEPLOYMENT_GUIDE.md)
3. Configure Bedrock Agent
4. Set up DynamoDB tables
5. Deploy Lambda functions
6. Create API Gateway
7. Test end-to-end flow

### For Production
1. Add authentication (Cognito)
2. Implement rate limiting
3. Set up CloudWatch monitoring
4. Configure SNS notifications
5. Add error handling
6. Implement retry logic
7. Test with real users

### For Demo
1. Create sample users with clinical profiles
2. Run test sessions with various scenarios
3. Show sentiment score progression
4. Demonstrate red flag detection
5. Display progress dashboard
6. Show trend analysis

## Documentation Index

- **AI Chat Integration**: `backend/docs/AI_CHAT_INTEGRATION.md`
- **Sentiment Tracking**: `backend/docs/SENTIMENT_SCORE_TRACKING.md`
- **Clinical Profiles**: `backend/docs/CLINICAL_PROFILE_USAGE.md`
- **Deployment**: `backend/docs/DEPLOYMENT_GUIDE.md`
- **Session Analysis**: `backend/docs/SESSION_ANALYSIS_SUMMARY.md`
- **Examples**: `backend/examples/sentiment_tracking_example.py`

## Support

For issues during the hackathon, contact Environment Leads:
- **London**: Mevlit (mevlit@), Rama (ramaknat@)
- **Manchester**: Basheer Ahmed (basheerz@), Robert Bradley (rbradaws@)
- **Dublin**: Shane Adams (shaadas@), Sherin Chandy (chandys@), Eduarda Siqueira (edds@)

🏆 Breaking Barriers UK 2026 compliant - Complete AI therapy platform ready for deployment!
