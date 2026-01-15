# Speech-to-Speech Ready! 🎤🔊

## ✅ What's Working

Your AI therapy chatbot now has **full speech-to-speech** capability:

### 🎤 Speech Input (Speech-to-Text)
- Uses browser's **Web Speech API** (Chrome, Edge, Safari)
- Click the microphone button to start speaking
- Your speech is converted to text in real-time
- Text is automatically sent to the AI after you finish speaking

### 🤖 AI Processing
- **Bedrock Claude Sonnet 4.5** generates culturally-aware therapy responses
- Maintains conversation context
- Stays under 1 RPS for Breaking Barriers compliance

### 🔊 Speech Output (Text-to-Speech)
- **Amazon Polly** converts AI responses to natural speech
- Uses "Joanna" neural voice (warm, empathetic)
- Audio plays automatically when AI responds
- MP3 format for broad compatibility

## 🎯 How to Use for Demo

### 1. Start a Session
- Click "Start Your Session"
- Wait for WebSocket to connect

### 2. Talk to the AI
**Option A: Voice Input**
- Click the microphone button (it will turn red and pulse)
- Speak your message clearly
- The AI will transcribe, process, and respond with voice

**Option B: Text Input**
- Type your message in the chat box
- Press Enter or click Send
- The AI will respond with text + voice

### 3. Demo Flow Example
```
You: [Click mic] "I've been feeling stressed about work lately"
AI: [Speaks] "I hear that work stress is affecting you. That's a common challenge..."
You: [Click mic] "Yes, especially with deadlines"
AI: [Speaks] "Deadlines can create a lot of pressure. Can you tell me more..."
```

## 🌍 Cultural Awareness

The AI is now culturally sensitive and will:
- Respect diverse backgrounds and beliefs
- Adapt to collectivist vs individualist values
- Be mindful of mental health stigma across cultures
- Acknowledge religious/spiritual perspectives
- Understand migration and identity challenges

**Test with:**
- "In my culture, we don't talk about feelings openly"
- "My family expects me to always be strong"
- "I'm caught between two cultures"

## 🔧 Technical Details

### Architecture
```
User speaks
    ↓
Browser Web Speech API (speech-to-text)
    ↓
WebSocket → Lambda
    ↓
Bedrock Claude Sonnet 4.5 (AI response)
    ↓
Amazon Polly (text-to-speech)
    ↓
WebSocket → Browser
    ↓
Audio plays automatically
```

### Browser Compatibility
- ✅ **Chrome** - Full support
- ✅ **Edge** - Full support  
- ✅ **Safari** - Full support
- ⚠️ **Firefox** - Limited support (may need text input)

### What Happens Behind the Scenes
1. **Microphone button clicked** → Web Speech API starts listening
2. **User speaks** → Browser converts speech to text in real-time
3. **User pauses** → Text is sent to backend via WebSocket
4. **Lambda receives text** → Calls Bedrock for AI response
5. **Bedrock responds** → Lambda calls Polly for speech synthesis
6. **Polly generates audio** → Sent back via WebSocket as base64 MP3
7. **Frontend receives** → Decodes and plays audio automatically

## 🎬 Demo Tips

### For Best Results:
1. **Use Chrome or Edge** for most reliable speech recognition
2. **Speak clearly** and pause between sentences
3. **Allow microphone permission** when prompted
4. **Use headphones** to avoid audio feedback
5. **Test in quiet environment** for better recognition

### Demo Script:
```
1. "Hi, I'm feeling anxious about my presentation tomorrow"
   → AI responds with empathy and asks follow-up

2. "I'm worried people will judge me"
   → AI explores the fear and offers perspective

3. "In my culture, showing weakness is not acceptable"
   → AI acknowledges cultural context and adapts approach

4. "Thank you, this helps"
   → AI provides encouragement and closing
```

### Fallback Options:
- If voice input doesn't work → Use text chat (still gets voice responses)
- If audio doesn't play → Check browser console, refresh page
- If WebSocket disconnects → Click "End Session" then "Start Session"

## 🏆 Breaking Barriers UK 2026 Compliant

- ✅ **Region**: us-west-2
- ✅ **Services**: Bedrock (Claude Sonnet 4.5), Polly, Lambda, API Gateway, DynamoDB
- ✅ **Rate Limiting**: < 1 RPS
- ✅ **No prohibited data**: Generic placeholders only
- ✅ **Browser-based speech**: No AWS Transcribe needed (cost-effective!)

## 🚀 Quick Start

1. **Hard refresh** your browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
2. Click **"Start Your Session"**
3. Click the **microphone button** 🎤
4. **Speak** your message
5. **Listen** to the AI's voice response 🔊

## 🐛 Troubleshooting

### Microphone not working?
- Check browser permissions (click lock icon in address bar)
- Try Chrome or Edge instead
- Use text input as fallback

### No audio response?
- Check volume is up
- Look for audio playback errors in console (F12)
- Hard refresh the page

### WebSocket errors?
- End session and start again
- Check CloudWatch logs for backend errors
- Verify Lambda has Polly permissions

## 📊 What to Show Judges

1. **Voice interaction** - Speak naturally, get voice responses
2. **Cultural awareness** - Mention cultural context, see AI adapt
3. **Conversation flow** - Multiple exchanges with context retention
4. **3D Avatar** - Visual representation that reacts to conversation
5. **Real-time processing** - Fast response times

---

**You're ready for your demo!** 🎉

The speech-to-speech is working using:
- Browser's built-in speech recognition (free, fast, reliable)
- Bedrock AI for intelligent responses
- Polly for natural voice output

This is a production-ready solution that works reliably for demos!
