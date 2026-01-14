# Sentiment Score Tracking System

🏆 Breaking Barriers UK 2026 compliant

## Overview

The sentiment score system tracks user emotional wellbeing across therapy sessions using a 1-10 scale. This allows doctors and therapists to monitor patient progress over time and identify trends.

## Sentiment Score Scale (1-10)

### Score Interpretation

**1-3: Very Negative (Critical)**
- High risk indicators present
- Severe emotional distress
- Acute self-harm risk
- Immediate intervention needed
- Example: Active suicidal ideation, severe hopelessness

**4-5: Negative (Concerning)**
- Concerning patterns detected
- Moderate emotional distress
- Passive self-harm thoughts
- Close monitoring required
- Example: Persistent sadness, anxiety, low self-esteem

**6-7: Neutral to Slightly Positive (Stable)**
- Stable emotional state
- Some challenges present
- Managing with support
- Continued therapy beneficial
- Example: Mild anxiety, working on coping strategies

**8-9: Positive (Improving)**
- Good progress evident
- Effective coping mechanisms
- Reduced distress
- Positive engagement
- Example: Seeking coping tools, self-compassion work

**10: Very Positive (Excellent)**
- Excellent progress
- Strong emotional wellbeing
- Effective self-management
- Therapeutic goals achieved
- Example: Confident, hopeful, resilient

## How Scores Are Calculated

The system analyzes each session and calculates a score based on:

### Emotional State Impact
```
Hopelessness: -3
Sadness, Fear, Shame, Numbness, Low Self-Esteem: -2
Anxiety, Anger, Guilt, Confusion: -1
```

### Self-Harm Risk Impact
```
Acute: -4
Concerning: -3
Passive: -2
None: +1
```

### Overall Risk Impact
```
High: -2
Medium: -1
Low: +1
```

### Conversation Preference Impact
```
Coping Tools: +1 (actively seeking help)
Self-Compassion: +1 (positive self-work)
Check-in: +1 (monitoring progress)
Venting, Just Listening: 0 (neutral)
```

### Red Flags Impact
```
Each red flag: -2
```

**Formula**: Start at 5 (neutral), apply all adjustments, clamp to 1-10 range

## Usage Examples

### 1. Automatic Score Calculation After Session

```python
from backend.src.services.session_analyzer import SessionAnalyzer

messages = [
    {"role": "user", "content": "I've been practicing the breathing exercises"},
    {"role": "assistant", "content": "That's wonderful progress!"},
    {"role": "user", "content": "I feel more in control of my anxiety now"}
]

analyzer = SessionAnalyzer()
result = analyzer.analyze_session("user123", "session456", messages)

# Result includes:
# {
#     'success': True,
#     'sentiment_score': 8,  # Positive - seeking coping tools, reduced anxiety
#     'updates_applied': {...},
#     'red_flags_created': [],
#     'analysis_summary': {...}
# }
```

### 2. Retrieve Sentiment History for a Patient

```python
from backend.src.data.session_repository import SessionRepository

repo = SessionRepository()
history = repo.get_sentiment_score_history("user123", limit=50)

# Returns:
# [
#     {
#         'session_id': 'session1',
#         'timestamp': '2026-01-01T10:00:00Z',
#         'sentiment_score': 4,
#         'status': 'completed',
#         'duration': 1800
#     },
#     {
#         'session_id': 'session2',
#         'timestamp': '2026-01-08T10:00:00Z',
#         'sentiment_score': 6,
#         'status': 'completed',
#         'duration': 1920
#     },
#     {
#         'session_id': 'session3',
#         'timestamp': '2026-01-14T10:00:00Z',
#         'sentiment_score': 8,
#         'status': 'completed',
#         'duration': 1740
#     }
# ]
```

### 3. API Call to Get Progress Report

```bash
# Get sentiment history with statistics
GET /api/sentiment-history/{client_id}?limit=50

# Response:
{
    "client_id": "user123",
    "history": [
        {
            "session_id": "session1",
            "timestamp": "2026-01-01T10:00:00Z",
            "sentiment_score": 4,
            "status": "completed",
            "duration": 1800
        },
        {
            "session_id": "session2",
            "timestamp": "2026-01-08T10:00:00Z",
            "sentiment_score": 6,
            "status": "completed",
            "duration": 1920
        },
        {
            "session_id": "session3",
            "timestamp": "2026-01-14T10:00:00Z",
            "sentiment_score": 8,
            "status": "completed",
            "duration": 1740
        }
    ],
    "count": 3,
    "statistics": {
        "average_score": 6.0,
        "latest_score": 8,
        "highest_score": 8,
        "lowest_score": 4,
        "trend": "improving"
    }
}
```

## Trend Analysis

The system automatically calculates trends by comparing the first half of sessions to the second half:

- **Improving**: Second half average > first half average + 0.5
- **Declining**: Second half average < first half average - 0.5
- **Stable**: Within 0.5 points
- **Insufficient Data**: Less than 4 sessions

## Integration with Clinical Dashboard

### Example Dashboard Display

```
Patient: [User Name]
Total Sessions: 12
Average Score: 6.5
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

[View Full History] [Generate Report]
```

## Visualization Example (Frontend)

```javascript
// Example chart data for frontend
const chartData = {
    labels: history.map(h => new Date(h.timestamp).toLocaleDateString()),
    datasets: [{
        label: 'Sentiment Score',
        data: history.map(h => h.sentiment_score),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
    }]
};

// Color coding by score range
function getScoreColor(score) {
    if (score <= 3) return '#dc3545'; // Red - Critical
    if (score <= 5) return '#ffc107'; // Yellow - Concerning
    if (score <= 7) return '#17a2b8'; // Blue - Stable
    return '#28a745'; // Green - Positive
}
```

## Clinical Use Cases

### 1. Progress Monitoring
Doctors can see if therapy is effective over time:
- Upward trend = therapy working
- Downward trend = intervention needed
- Stable low scores = treatment adjustment required

### 2. Crisis Detection
Sudden drops in score trigger alerts:
- Score drops by 3+ points = automatic notification
- Score reaches 1-3 = immediate red flag created

### 3. Treatment Effectiveness
Compare scores before/after interventions:
- New medication started at session 5
- Compare average scores session 1-4 vs 6-10
- Measure improvement

### 4. Discharge Planning
Consistent high scores indicate readiness:
- 5+ consecutive sessions with score 8+
- Upward trend maintained
- No red flags in recent sessions

## API Endpoints

### Get Sentiment History
```
GET /api/sentiment-history/{client_id}?limit=50
```

### Analyze Session (Auto-calculates score)
```
POST /api/analyze-session
Body: {
    "user_id": "user123",
    "session_id": "session456",
    "messages": [...]
}
```

## Database Schema

### Session Table
```
sessionId (PK): string
timestamp (SK): string
sentimentScore: number (1-10)
status: string
clientId: string (GSI)
```

### Query Patterns
```sql
-- Get all scores for a client (chronological)
Query on ClientIndex where clientId = "user123"
Sort by timestamp ASC

-- Get recent low scores (alerts)
Scan where sentimentScore <= 3 AND status = "completed"
```

## Monitoring & Alerts

### CloudWatch Metrics
- Average sentiment score per day
- Number of sessions with score <= 3
- Trend changes (improving → declining)

### Automated Alerts
- Score drops below 3 → SNS notification to therapist
- Score drops by 3+ points between sessions → Email alert
- 3 consecutive declining sessions → Dashboard warning

## Privacy & Security

- Sentiment scores are **internal only** - not shown to patients
- Stored encrypted in DynamoDB
- Access restricted to clinical staff
- Audit logging enabled
- GDPR compliant - can be deleted on request

## Future Enhancements

1. **AI-Powered Scoring**: Use Bedrock for more accurate sentiment analysis
2. **Predictive Analytics**: Predict future scores based on trends
3. **Comparative Analysis**: Compare patient progress to anonymized cohorts
4. **Goal Correlation**: Link sentiment scores to goal achievement
5. **Multi-Factor Scoring**: Include session duration, engagement metrics

🏆 Breaking Barriers UK 2026 compliant - uses DynamoDB, Lambda, and can integrate with Bedrock for enhanced analysis.
