# Session Analysis System - Quick Summary

## What Was Built

### 1. Enhanced User Model (`backend/src/models/user.py`)
Added `ClinicalProfile` with internal tracking fields:
- Demographics: age, gender, medical conditions
- Risk assessment: domestic abuse type, emotional state, self-harm risk, overall risk
- Preferences: conversation preference
- Progress: goals tracking, last session timestamp

### 2. Session Model with Sentiment Score (`backend/src/models/session.py`)
Added `sentiment_score` field (1-10) to track user wellbeing per session

### 3. Session Analyzer Service (`backend/src/services/session_analyzer.py`)
Analyzes completed therapy sessions and automatically:
- Detects emotional states from conversation
- Identifies conversation preferences
- Assesses self-harm and overall risk levels
- **Calculates sentiment score (1-10)** based on multiple factors
- Creates red flags for critical situations
- Updates user clinical profile in real-time

### 4. User Repository Updates (`backend/src/data/user_repository.py`)
Added `update_clinical_profile()` method to update internal clinical data

### 5. Session Repository Updates (`backend/src/data/session_repository.py`)
Added methods:
- `update_session_sentiment_score()`: Store sentiment score for session
- `get_sentiment_score_history()`: Retrieve score history for progress tracking

### 6. API Endpoints (`backend/src/api/session_analysis.py`)
- `analyze_session_handler`: Analyzes session and updates profile + score
- `get_clinical_profile_handler`: Retrieves clinical data (internal only)
- `update_goals_handler`: Updates therapeutic goals
- `get_sentiment_history_handler`: **NEW** - Retrieves sentiment score history with statistics

### 7. Documentation
- `CLINICAL_PROFILE_USAGE.md`: Complete usage guide
- `SENTIMENT_SCORE_TRACKING.md`: **NEW** - Sentiment score system documentation
- `SESSION_ANALYSIS_SUMMARY.md`: Quick reference

### 8. Examples
- `sentiment_tracking_example.py`: **NEW** - Practical examples of sentiment tracking

## How It Works

```
Session Ends → Analyze Messages → Calculate Sentiment Score (1-10) → Update Clinical Profile → Store Score → Create Red Flags (if needed)
```

### Sentiment Score Calculation (1-10)

**Score Ranges:**
- **1-3**: Very negative (critical, high risk)
- **4-5**: Negative (concerning, needs attention)
- **6-7**: Neutral to positive (stable)
- **8-9**: Positive (improving, good progress)
- **10**: Very positive (excellent wellbeing)

**Factors Considered:**
- Emotional state (hopelessness -3, anxiety -1, etc.)
- Self-harm risk (acute -4, concerning -3, passive -2, none +1)
- Overall user risk (high -2, medium -1, low +1)
- Conversation preference (seeking coping tools +1)
- Red flags (each -2)

### Automatic Detection

**Emotional States**: Fear, Shame, Guilt, Confusion, Anger, Sadness, Hopelessness, Anxiety, Numbness, Low Self-Esteem

**Risk Levels**:
- NONE → No concerns detected
- PASSIVE → Passive ideation ("wish I wasn't here")
- CONCERNING → Self-harm indicators
- ACUTE → Active suicidal ideation → Creates CRITICAL red flag

**Conversation Preferences**: Just Listening, Coping Tools, Check-in, Venting, Self-Compassion

## Key Features

✅ **Automatic Analysis**: Runs after each session
✅ **Sentiment Score Tracking**: 1-10 scale for progress monitoring
✅ **Progress History**: View score trends over time
✅ **Trend Analysis**: Automatically detects improving/declining/stable patterns
✅ **Red Flag Integration**: Creates alerts for critical situations
✅ **Internal Only**: Clinical data never exposed to users
✅ **Real-time Updates**: Profile and scores updated immediately
✅ **Statistics**: Average, latest, highest, lowest scores with trends
✅ **Bedrock Ready**: Can upgrade to AI-powered analysis

## Usage Example

```python
from backend.src.services.session_analyzer import SessionAnalyzer
from backend.src.data.session_repository import SessionRepository

# Analyze session and get sentiment score
messages = [
    {"role": "user", "content": "I'm feeling anxious and overwhelmed"},
    {"role": "assistant", "content": "I hear you..."}
]

analyzer = SessionAnalyzer()
result = analyzer.analyze_session("user123", "session456", messages)

# Result includes sentiment score
# {
#     'success': True,
#     'sentiment_score': 5,  # Out of 10
#     'updates_applied': {
#         'emotional_state': 'anxiety',
#         'user_risk': 'medium',
#         'last_session_timestamp': '2026-01-14T...'
#     },
#     'red_flags_created': [],
#     'analysis_summary': {...}
# }

# Get sentiment score history for progress tracking
repo = SessionRepository()
history = repo.get_sentiment_score_history("user123", limit=50)

# Returns chronological list of scores
# [
#     {'session_id': 's1', 'timestamp': '...', 'sentiment_score': 4},
#     {'session_id': 's2', 'timestamp': '...', 'sentiment_score': 6},
#     {'session_id': 's3', 'timestamp': '...', 'sentiment_score': 8}
# ]
```

## API Endpoints

### Analyze Session (POST)
```
POST /api/analyze-session
Body: {
    "user_id": "user123",
    "session_id": "session456",
    "messages": [...]
}

Response: {
    "sentiment_score": 7,
    "updates_applied": {...},
    "red_flags_created": []
}
```

### Get Sentiment History (GET) - **NEW**
```
GET /api/sentiment-history/{client_id}?limit=50

Response: {
    "client_id": "user123",
    "history": [...],
    "count": 10,
    "statistics": {
        "average_score": 6.5,
        "latest_score": 8,
        "highest_score": 9,
        "lowest_score": 3,
        "trend": "improving"
    }
}
```

### Get Clinical Profile (GET - Internal Only)
```
GET /api/clinical-profile/{user_id}
```

### Update Goals (POST)
```
POST /api/update-goals
Body: {
    "user_id": "user123",
    "total_goals": 5,
    "goals_achieved": 2
}
```

## Integration Points

1. **After Session Completion**: Call `analyze_session()` automatically
2. **Before New Session**: Retrieve clinical profile to inform AI context
3. **Dashboard Display**: Show sentiment score history with trend graphs
4. **Red Flag Alerts**: Automatically notifies staff of critical situations
5. **Progress Reports**: Generate reports showing score trends over time
6. **Progress Tracking**: Update goals as user achieves them

## Clinical Dashboard Example

```
Patient: [Name]
Total Sessions: 12
Average Score: 6.5/10
Trend: ↗ Improving

Recent Sessions:
┌────────────┬───────┬──────────────────────┐
│ Date       │ Score │ Status               │
├────────────┼───────┼──────────────────────┤
│ 2026-01-14 │   8   │ ✓ Positive progress  │
│ 2026-01-07 │   6   │ ○ Stable             │
│ 2025-12-31 │   4   │ ⚠ Needs attention    │
│ 2025-12-24 │   3   │ ⚠ High risk          │
└────────────┴───────┴──────────────────────┘
```

🏆 Breaking Barriers UK 2026 compliant - uses DynamoDB, Lambda, and can integrate with Bedrock.
