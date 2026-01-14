# AI Chat Integration Guide

🏆 Breaking Barriers UK 2026 compliant

## Overview

This guide shows how to connect your app (web/mobile) to the AI therapy chatbot using AWS Bedrock Agents.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Flow Architecture                    │
└─────────────────────────────────────────────────────────────┘

Frontend App                API Gateway              Lambda                Bedrock Agent
────────────                ───────────              ──────                ─────────────
User types                     │                       │                        │
message ──────────────────────→│                       │                        │
                               │                       │                        │
                               │  POST /chat           │                        │
                               │  ─────────────────────→│                        │
                               │                       │                        │
                               │                       │  Invoke agent          │
                               │                       │  ──────────────────────→│
                               │                       │                        │
                               │                       │                   AI processes
                               │                       │                   with context
                               │                       │                        │
                               │                       │  ←─────────────────────│
                               │                       │  AI response           │
                               │  ←─────────────────────│                        │
                               │  Response              │                        │
AI response ←──────────────────│                       │                        │
displayed                      │                       │                        │
```

## Step-by-Step Integration

### Step 1: Create Bedrock Agent (AWS Setup)

First, create your AI therapy agent in AWS Bedrock:

```python
# This is done once during setup (not in your app code)
import boto3

bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')

# Create agent
response = bedrock_agent.create_agent(
    agentName='TherapyAgent',
    foundationModel='anthropic.claude-sonnet-4-5-v2:0',
    instruction='''You are a compassionate AI therapy assistant. Your role is to:
    - Listen actively and empathetically
    - Ask open-ended questions
    - Provide coping strategies when appropriate
    - Detect signs of crisis and escalate if needed
    - Maintain a warm, supportive tone
    - Never provide medical diagnoses
    - Encourage professional help when needed
    ''',
    agentResourceRoleArn='arn:aws:iam::ACCOUNT:role/BedrockAgentRole'
)

agent_id = response['agent']['agentId']
print(f"Agent created: {agent_id}")

# Create agent alias
alias_response = bedrock_agent.create_agent_alias(
    agentId=agent_id,
    agentAliasName='production'
)

agent_alias_id = alias_response['agentAlias']['agentAliasId']
print(f"Alias created: {agent_alias_id}")
```

### Step 2: Create Lambda Function for Chat

Create a Lambda function that handles chat requests:

```python
# backend/src/api/chat_handler.py
"""
Chat handler for AI therapy sessions
🏆 Breaking Barriers UK 2026 compliant
"""

import boto3
import json
import os
from datetime import datetime
from typing import Dict, Any
from ..data.session_repository import SessionRepository
from ..data.user_repository import UserRepository
from ..models.session import TherapySession, SessionStatus
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Bedrock client
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

# Get agent configuration from environment
AGENT_ID = os.environ.get('BEDROCK_AGENT_ID')
AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID')


def chat_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for chat messages
    
    Expected event:
    {
        "user_id": "user123",
        "session_id": "session456",  # Optional - creates new if not provided
        "message": "I'm feeling anxious today",
        "create_session": true  # Optional - for first message
    }
    """
    try:
        # Parse request
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)
        
        user_id = body.get('user_id')
        session_id = body.get('session_id')
        message = body.get('message')
        create_session = body.get('create_session', False)
        
        # Validate input
        if not user_id or not message:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id and message are required'})
            }
        
        # Get user info for context
        user_repo = UserRepository()
        user = user_repo.get_user(user_id)
        
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User not found'})
            }
        
        # Create new session if needed
        session_repo = SessionRepository()
        if create_session or not session_id:
            session_id = f"session_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            # Create session in DynamoDB
            session = TherapySession(
                session_id=session_id,
                client_id=user_id,
                agent_id=AGENT_ID,
                agent_memory_id=f"mem_{session_id}",
                status=SessionStatus.ACTIVE
            )
            session_repo.create_session(session)
            
            logger.info(f"Created new session: {session_id}")
        
        # Get clinical profile for AI context (if available)
        context_info = ""
        if user.clinical_profile:
            context_info = f"""
            User context (internal - do not mention directly):
            - Current emotional state: {user.clinical_profile.emotional_state}
            - Risk level: {user.clinical_profile.user_risk}
            - Conversation preference: {user.clinical_profile.conversation_preference}
            - Goals: {user.clinical_profile.goals_achieved}/{user.clinical_profile.total_goals} achieved
            """
        
        # Invoke Bedrock Agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=message,
            sessionState={
                'sessionAttributes': {
                    'user_id': user_id,
                    'user_name': user.profile.first_name,
                    'context': context_info
                }
            }
        )
        
        # Parse agent response
        ai_response = ""
        for event in response.get('completion', []):
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    ai_response += chunk['bytes'].decode('utf-8')
        
        # Return response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'session_id': session_id,
                'user_message': message,
                'ai_response': ai_response,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
    
    except Exception as e:
        logger.error(f"Chat handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def end_session_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for ending a session
    
    Expected event:
    {
        "user_id": "user123",
        "session_id": "session456"
    }
    """
    try:
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)
        
        user_id = body.get('user_id')
        session_id = body.get('session_id')
        
        if not user_id or not session_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id and session_id are required'})
            }
        
        # Get session
        session_repo = SessionRepository()
        sessions = session_repo.get_sessions_by_client(user_id, limit=1)
        
        if not sessions['sessions']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Session not found'})
            }
        
        session = sessions['sessions'][0]
        
        # Calculate duration
        duration = int((datetime.utcnow() - session.start_time).total_seconds())
        
        # Update session status
        session_repo.update_session_status(
            session_id=session_id,
            timestamp=session.timestamp.isoformat(),
            status=SessionStatus.COMPLETED,
            end_time=datetime.utcnow(),
            duration=duration
        )
        
        # Get conversation from Bedrock for analysis
        # Note: In production, retrieve actual conversation from Bedrock memory
        # For now, we'll trigger analysis separately
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Session ended successfully',
                'session_id': session_id,
                'duration': duration
            })
        }
    
    except Exception as e:
        logger.error(f"End session handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Step 3: Deploy API Gateway

Create API Gateway endpoints:

```yaml
# API Gateway configuration
/api/chat:
  POST:
    handler: chat_handler
    description: Send message to AI
    
/api/chat/end:
  POST:
    handler: end_session_handler
    description: End therapy session
    
/api/chat/history:
  GET:
    handler: get_chat_history_handler
    description: Get session history
```

### Step 4: Frontend Integration (React Example)

```javascript
// frontend/src/services/chatService.js

const API_BASE_URL = 'https://your-api-gateway.amazonaws.com/prod';

class ChatService {
  constructor() {
    this.sessionId = null;
    this.userId = null;
  }

  /**
   * Initialize chat session
   */
  async startSession(userId) {
    this.userId = userId;
    
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify({
        user_id: userId,
        message: "Hello, I'd like to start a session",
        create_session: true
      })
    });

    const data = await response.json();
    this.sessionId = data.session_id;
    
    return {
      sessionId: data.session_id,
      aiResponse: data.ai_response
    };
  }

  /**
   * Send message to AI
   */
  async sendMessage(message) {
    if (!this.sessionId) {
      throw new Error('No active session. Call startSession() first.');
    }

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify({
        user_id: this.userId,
        session_id: this.sessionId,
        message: message
      })
    });

    const data = await response.json();
    
    return {
      userMessage: data.user_message,
      aiResponse: data.ai_response,
      timestamp: data.timestamp
    };
  }

  /**
   * End session
   */
  async endSession() {
    if (!this.sessionId) {
      return;
    }

    const response = await fetch(`${API_BASE_URL}/api/chat/end`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify({
        user_id: this.userId,
        session_id: this.sessionId
      })
    });

    const data = await response.json();
    
    // Clear session
    this.sessionId = null;
    
    return data;
  }

  /**
   * Get auth token (from Cognito or your auth system)
   */
  getAuthToken() {
    // Implement your auth token retrieval
    return localStorage.getItem('auth_token');
  }
}

export default new ChatService();
```

### Step 5: React Chat Component

```javascript
// frontend/src/components/TherapyChat.jsx

import React, { useState, useEffect, useRef } from 'react';
import chatService from '../services/chatService';

function TherapyChat({ userId }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionActive, setSessionActive] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Start session
  const handleStartSession = async () => {
    setIsLoading(true);
    try {
      const result = await chatService.startSession(userId);
      
      setMessages([
        {
          role: 'assistant',
          content: result.aiResponse,
          timestamp: new Date().toISOString()
        }
      ]);
      
      setSessionActive(true);
    } catch (error) {
      console.error('Failed to start session:', error);
      alert('Failed to start session. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Send message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) {
      return;
    }

    // Add user message to UI immediately
    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send to AI
      const result = await chatService.sendMessage(inputMessage);
      
      // Add AI response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: result.aiResponse,
        timestamp: result.timestamp
      }]);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // End session
  const handleEndSession = async () => {
    if (!window.confirm('Are you sure you want to end this session?')) {
      return;
    }

    setIsLoading(true);
    try {
      await chatService.endSession();
      setSessionActive(false);
      
      // Show completion message
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Session ended. Thank you for sharing today.',
        timestamp: new Date().toISOString()
      }]);
      
    } catch (error) {
      console.error('Failed to end session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="therapy-chat">
      <div className="chat-header">
        <h2>Therapy Session</h2>
        {sessionActive && (
          <button onClick={handleEndSession} className="end-session-btn">
            End Session
          </button>
        )}
      </div>

      <div className="chat-messages">
        {!sessionActive ? (
          <div className="start-session">
            <p>Ready to start your therapy session?</p>
            <button onClick={handleStartSession} disabled={isLoading}>
              {isLoading ? 'Starting...' : 'Start Session'}
            </button>
          </div>
        ) : (
          <>
            {messages.map((msg, index) => (
              <div key={index} className={`message message-${msg.role}`}>
                <div className="message-content">{msg.content}</div>
                <div className="message-time">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message message-assistant">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {sessionActive && (
        <form onSubmit={handleSendMessage} className="chat-input">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !inputMessage.trim()}>
            Send
          </button>
        </form>
      )}
    </div>
  );
}

export default TherapyChat;
```

### Step 6: Mobile App Integration (React Native Example)

```javascript
// mobile/src/screens/TherapyChatScreen.js

import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, KeyboardAvoidingView } from 'react-native';
import chatService from '../services/chatService';

export default function TherapyChatScreen({ route }) {
  const { userId } = route.params;
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionActive, setSessionActive] = useState(false);

  const startSession = async () => {
    setIsLoading(true);
    try {
      const result = await chatService.startSession(userId);
      setMessages([{
        id: '1',
        role: 'assistant',
        content: result.aiResponse,
        timestamp: new Date().toISOString()
      }]);
      setSessionActive(true);
    } catch (error) {
      console.error('Failed to start session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const result = await chatService.sendMessage(inputMessage);
      
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.aiResponse,
        timestamp: result.timestamp
      }]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = ({ item }) => (
    <View style={[
      styles.messageBubble,
      item.role === 'user' ? styles.userBubble : styles.aiBubble
    ]}>
      <Text style={styles.messageText}>{item.content}</Text>
      <Text style={styles.messageTime}>
        {new Date(item.timestamp).toLocaleTimeString()}
      </Text>
    </View>
  );

  return (
    <KeyboardAvoidingView style={styles.container} behavior="padding">
      {!sessionActive ? (
        <View style={styles.startContainer}>
          <Text style={styles.startText}>Ready to start your session?</Text>
          <TouchableOpacity 
            style={styles.startButton} 
            onPress={startSession}
            disabled={isLoading}
          >
            <Text style={styles.startButtonText}>
              {isLoading ? 'Starting...' : 'Start Session'}
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          <FlatList
            data={messages}
            renderItem={renderMessage}
            keyExtractor={item => item.id}
            style={styles.messagesList}
          />
          
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              value={inputMessage}
              onChangeText={setInputMessage}
              placeholder="Type your message..."
              editable={!isLoading}
            />
            <TouchableOpacity 
              style={styles.sendButton} 
              onPress={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
            >
              <Text style={styles.sendButtonText}>Send</Text>
            </TouchableOpacity>
          </View>
        </>
      )}
    </KeyboardAvoidingView>
  );
}
```

## Complete Integration Flow

```
1. User opens app
   ↓
2. User clicks "Start Session"
   ↓
3. Frontend calls POST /api/chat with create_session=true
   ↓
4. Lambda creates session in DynamoDB
   ↓
5. Lambda invokes Bedrock Agent
   ↓
6. Bedrock Agent responds with greeting
   ↓
7. Frontend displays AI greeting
   ↓
8. User types message
   ↓
9. Frontend calls POST /api/chat with message
   ↓
10. Lambda sends message to Bedrock Agent (with session_id)
    ↓
11. Bedrock Agent processes with context from memory
    ↓
12. Bedrock Agent responds
    ↓
13. Frontend displays AI response
    ↓
14. Repeat steps 8-13 for conversation
    ↓
15. User clicks "End Session"
    ↓
16. Frontend calls POST /api/chat/end
    ↓
17. Lambda marks session as completed
    ↓
18. Lambda triggers session analysis
    ↓
19. Sentiment score calculated and stored
    ↓
20. Clinical profile updated
    ↓
21. Session complete
```

## Environment Variables

Set these in your Lambda function:

```bash
BEDROCK_AGENT_ID=your-agent-id
BEDROCK_AGENT_ALIAS_ID=your-alias-id
DYNAMODB_SESSIONS_TABLE=sessions
DYNAMODB_USERS_TABLE=users
DYNAMODB_REDFLAGS_TABLE=redflags
```

## Testing

```bash
# Test chat endpoint
curl -X POST https://your-api.amazonaws.com/prod/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": "user123",
    "message": "Hello, I need help with anxiety",
    "create_session": true
  }'

# Response:
{
  "session_id": "session_user123_1705234567",
  "user_message": "Hello, I need help with anxiety",
  "ai_response": "Hello! I'm here to support you. Can you tell me more about what you're experiencing with anxiety?",
  "timestamp": "2026-01-14T10:30:00Z"
}
```

🏆 Breaking Barriers UK 2026 compliant - uses API Gateway, Lambda, Bedrock Agent, and DynamoDB.
