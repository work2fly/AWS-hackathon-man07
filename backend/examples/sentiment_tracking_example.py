"""
Example: Sentiment Score Tracking Usage
🏆 Breaking Barriers UK 2026 compliant
"""

from datetime import datetime
from backend.src.services.session_analyzer import SessionAnalyzer
from backend.src.data.session_repository import SessionRepository
from backend.src.data.user_repository import UserRepository


def example_1_analyze_session_with_score():
    """Example 1: Analyze a session and get sentiment score"""
    
    print("=" * 60)
    print("Example 1: Analyze Session and Calculate Sentiment Score")
    print("=" * 60)
    
    # Sample conversation from a therapy session
    messages = [
        {"role": "user", "content": "I've been feeling really anxious this week"},
        {"role": "assistant", "content": "I hear you. Can you tell me more about what's been making you anxious?"},
        {"role": "user", "content": "Work has been overwhelming, but I tried those breathing exercises you taught me"},
        {"role": "assistant", "content": "That's great that you're using the coping tools! How did they help?"},
        {"role": "user", "content": "They actually helped calm me down. I feel more in control now"}
    ]
    
    # Analyze the session
    analyzer = SessionAnalyzer()
    result = analyzer.analyze_session(
        user_id="user123",
        session_id="session456",
        messages=messages
    )
    
    print(f"\nAnalysis Results:")
    print(f"  Success: {result['success']}")
    print(f"  Sentiment Score: {result['sentiment_score']}/10")
    print(f"  Emotional State: {result['updates_applied'].get('emotional_state')}")
    print(f"  User Risk: {result['updates_applied'].get('user_risk')}")
    print(f"  Red Flags Created: {len(result['red_flags_created'])}")
    
    # Interpret the score
    score = result['sentiment_score']
    if score >= 8:
        interpretation = "Positive - Good progress"
    elif score >= 6:
        interpretation = "Stable - Continuing therapy"
    elif score >= 4:
        interpretation = "Concerning - Needs attention"
    else:
        interpretation = "Critical - Immediate intervention"
    
    print(f"  Interpretation: {interpretation}")
    print()


def example_2_get_patient_progress():
    """Example 2: Get patient's sentiment score history"""
    
    print("=" * 60)
    print("Example 2: Retrieve Patient Progress Over Time")
    print("=" * 60)
    
    # Get sentiment history for a patient
    repo = SessionRepository()
    history = repo.get_sentiment_score_history("user123", limit=10)
    
    print(f"\nSentiment Score History (Last {len(history)} sessions):")
    print(f"{'Date':<20} {'Score':<10} {'Status':<15}")
    print("-" * 45)
    
    for item in history:
        date = datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M')
        score = item['sentiment_score']
        status = item['status']
        
        # Visual indicator
        if score >= 8:
            indicator = "✓"
        elif score >= 6:
            indicator = "○"
        elif score >= 4:
            indicator = "⚠"
        else:
            indicator = "⚠⚠"
        
        print(f"{date:<20} {score:<10} {indicator} {status}")
    
    # Calculate statistics
    if history:
        scores = [item['sentiment_score'] for item in history]
        avg = sum(scores) / len(scores)
        print(f"\nStatistics:")
        print(f"  Average Score: {avg:.2f}")
        print(f"  Latest Score: {scores[-1]}")
        print(f"  Highest Score: {max(scores)}")
        print(f"  Lowest Score: {min(scores)}")
        
        # Trend analysis
        if len(scores) >= 4:
            mid = len(scores) // 2
            first_half = sum(scores[:mid]) / mid
            second_half = sum(scores[mid:]) / (len(scores) - mid)
            
            if second_half > first_half + 0.5:
                trend = "↗ Improving"
            elif second_half < first_half - 0.5:
                trend = "↘ Declining"
            else:
                trend = "→ Stable"
            
            print(f"  Trend: {trend}")
    print()


def example_3_crisis_detection():
    """Example 3: Detect crisis situations from low scores"""
    
    print("=" * 60)
    print("Example 3: Crisis Detection Based on Sentiment Scores")
    print("=" * 60)
    
    # Simulate analyzing a concerning session
    crisis_messages = [
        {"role": "user", "content": "I don't see the point anymore"},
        {"role": "assistant", "content": "I'm concerned about what you're saying. Can you tell me more?"},
        {"role": "user", "content": "Everything feels hopeless. I just want it to end"},
        {"role": "assistant", "content": "I hear that you're in a lot of pain right now. Are you thinking about hurting yourself?"},
        {"role": "user", "content": "Yes, I've been thinking about it a lot"}
    ]
    
    analyzer = SessionAnalyzer()
    result = analyzer.analyze_session(
        user_id="user789",
        session_id="session999",
        messages=crisis_messages
    )
    
    print(f"\nCrisis Analysis:")
    print(f"  Sentiment Score: {result['sentiment_score']}/10 ⚠⚠ CRITICAL")
    print(f"  Self-Harm Risk: {result['updates_applied'].get('self_harm_risk_signal')}")
    print(f"  User Risk: {result['updates_applied'].get('user_risk')}")
    print(f"  Red Flags Created: {len(result['red_flags_created'])}")
    
    if result['sentiment_score'] <= 3:
        print(f"\n  🚨 ALERT: Critical sentiment score detected!")
        print(f"  Action Required: Immediate therapist notification")
        print(f"  Red flags have been created and notifications sent")
    
    print()


def example_4_progress_report():
    """Example 4: Generate progress report for doctor"""
    
    print("=" * 60)
    print("Example 4: Generate Progress Report for Clinical Review")
    print("=" * 60)
    
    # Simulate patient data
    patient_data = {
        'user_id': 'user123',
        'name': '[Patient Name]',
        'sessions': [
            {'date': '2025-12-01', 'score': 3},
            {'date': '2025-12-08', 'score': 4},
            {'date': '2025-12-15', 'score': 5},
            {'date': '2025-12-22', 'score': 6},
            {'date': '2025-12-29', 'score': 6},
            {'date': '2026-01-05', 'score': 7},
            {'date': '2026-01-12', 'score': 8},
        ]
    }
    
    scores = [s['score'] for s in patient_data['sessions']]
    
    print(f"\nProgress Report")
    print(f"Patient: {patient_data['name']}")
    print(f"Period: {patient_data['sessions'][0]['date']} to {patient_data['sessions'][-1]['date']}")
    print(f"Total Sessions: {len(scores)}")
    print()
    
    # Score progression
    print("Score Progression:")
    for session in patient_data['sessions']:
        bar = "█" * session['score']
        print(f"  {session['date']}: {bar} {session['score']}")
    
    print()
    
    # Statistics
    avg = sum(scores) / len(scores)
    improvement = scores[-1] - scores[0]
    
    print(f"Summary:")
    print(f"  Starting Score: {scores[0]}/10")
    print(f"  Current Score: {scores[-1]}/10")
    print(f"  Average Score: {avg:.1f}/10")
    print(f"  Improvement: +{improvement} points")
    
    # Clinical interpretation
    print(f"\nClinical Interpretation:")
    if improvement >= 3:
        print(f"  ✓ Significant improvement observed")
        print(f"  ✓ Patient responding well to therapy")
        print(f"  ✓ Continue current treatment plan")
    elif improvement >= 1:
        print(f"  ○ Moderate improvement observed")
        print(f"  ○ Patient making progress")
        print(f"  ○ Monitor and adjust as needed")
    else:
        print(f"  ⚠ Limited improvement")
        print(f"  ⚠ Consider treatment adjustment")
        print(f"  ⚠ Increase session frequency")
    
    print()


def example_5_api_integration():
    """Example 5: API integration for frontend dashboard"""
    
    print("=" * 60)
    print("Example 5: API Integration Example")
    print("=" * 60)
    
    print("\nFrontend Dashboard API Calls:")
    print()
    
    # Example 1: Get sentiment history
    print("1. Get Patient Sentiment History:")
    print("   GET /api/sentiment-history/user123?limit=50")
    print()
    print("   Response:")
    print("   {")
    print('     "client_id": "user123",')
    print('     "history": [')
    print('       {"session_id": "s1", "timestamp": "2026-01-01T10:00:00Z", "sentiment_score": 4},')
    print('       {"session_id": "s2", "timestamp": "2026-01-08T10:00:00Z", "sentiment_score": 6},')
    print('       {"session_id": "s3", "timestamp": "2026-01-14T10:00:00Z", "sentiment_score": 8}')
    print('     ],')
    print('     "statistics": {')
    print('       "average_score": 6.0,')
    print('       "latest_score": 8,')
    print('       "trend": "improving"')
    print('     }')
    print("   }")
    print()
    
    # Example 2: Analyze session
    print("2. Analyze Completed Session:")
    print("   POST /api/analyze-session")
    print("   Body: {")
    print('     "user_id": "user123",')
    print('     "session_id": "session456",')
    print('     "messages": [...]')
    print("   }")
    print()
    print("   Response:")
    print("   {")
    print('     "message": "Session analyzed successfully",')
    print('     "sentiment_score": 7,')
    print('     "updates_applied": {...},')
    print('     "red_flags_created": []')
    print("   }")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Sentiment Score Tracking System - Examples            ║")
    print("║     🏆 Breaking Barriers UK 2026 compliant                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Run examples
    example_1_analyze_session_with_score()
    example_2_get_patient_progress()
    example_3_crisis_detection()
    example_4_progress_report()
    example_5_api_integration()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)
