# AI Therapy Platform Frontend

🏆 **Breaking Barriers UK 2026 - AWS Hackathon Project**

A modern, secure AI-powered therapy platform built with Next.js 14, TypeScript, and AWS services.

## Features

### 🎯 Core Functionality
- **Real-time Audio Therapy Sessions** - Natural voice conversations with AI therapist
- **Multi-language Support** - Automatic language detection and culturally sensitive responses
- **Role-based Access Control** - Client, Therapist, and Admin interfaces
- **Privacy-first Design** - End-to-end encryption and GDPR compliance
- **Professional Oversight** - Therapist monitoring without compromising client privacy

### 🔧 Technical Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Authentication**: AWS Cognito with MFA support
- **Real-time Communication**: API Gateway WebSockets
- **Audio Processing**: Web Audio API + Amazon Nova Sonic 2
- **State Management**: React hooks with custom services
- **UI Components**: shadcn/ui with Lucide icons

### 🏗️ AWS Architecture
- **API Gateway**: REST API + WebSocket for real-time communication
- **Lambda Functions**: Serverless backend processing
- **DynamoDB**: User profiles, sessions, and metadata
- **Cognito**: User authentication and management
- **AgentCore**: AI agent memory and conversation context
- **Nova Sonic 2**: Speech-to-speech AI processing

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- AWS account with Breaking Barriers UK 2026 credentials

### Installation

1. **Clone and install dependencies**
   ```bash
   cd ai-therapy-frontend
   npm install
   ```

2. **Configure AWS credentials**
   The app is pre-configured for the hackathon AWS environment:
   - Region: `us-west-2` (Breaking Barriers constraint)
   - API Gateway: `https://xi8ekw0fj6.execute-api.us-west-2.amazonaws.com/dev`
   - WebSocket: `wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com`
   - Cognito User Pool: `us-west-2_ASOPUuOOV`

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open browser**
   Navigate to `http://localhost:3000`

### Build for Production
```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                    # Next.js 14 app router
│   └── page.tsx           # Main application page
├── components/            # React components
│   ├── auth/             # Authentication components
│   ├── client/           # Client session interface
│   └── ui/               # shadcn/ui components
├── hooks/                # Custom React hooks
│   ├── useAuth.ts        # Authentication management
│   ├── useWebSocket.ts   # Real-time communication
│   └── useAudio.ts       # Audio capture/playback
├── services/             # Business logic services
│   ├── auth.ts           # AWS Cognito integration
│   ├── websocket.ts      # WebSocket management
│   ├── audio.ts          # Audio processing
│   └── api.ts            # REST API client
├── config/               # Configuration
│   └── aws-config.ts     # AWS service endpoints
└── types/                # TypeScript definitions
    └── index.ts          # Application types
```

## Key Components

### Authentication (`useAuth` hook)
- AWS Cognito integration with Amplify
- Role-based access control (client/therapist/admin)
- MFA support and secure session management

### Real-time Communication (`useWebSocket` hook)
- API Gateway WebSocket connections
- Audio streaming to Nova Sonic 2
- Automatic reconnection with exponential backoff
- Message routing and error handling

### Audio Processing (`useAudio` hook)
- Web Audio API for microphone access
- Real-time audio streaming (100ms chunks)
- Volume level monitoring
- Cross-browser audio format support

### Session Interface
- Professional therapy session UI
- Real-time audio controls and status
- Session timing and message counting
- Connection status monitoring

## Security & Compliance

### 🏆 Breaking Barriers UK 2026 Compliance
- **Region Restriction**: us-west-2 only
- **Data Security**: No PII in code (uses placeholders like `[firstName]`)
- **Rate Limiting**: Designed for <1 RPS to avoid Bedrock throttling
- **Permitted Services**: Only uses approved AWS services list
- **Account Termination**: All code saved locally (terminates 23:00 on 15th January 2026)

### Privacy & Security Features
- End-to-end encryption (TLS 1.3)
- Data at rest encryption (AES-256)
- No full transcript access for therapists
- GDPR-compliant data handling
- Secure WebSocket connections
- JWT token management

## Development Notes

### Audio Configuration
- **Sample Rate**: 44.1kHz for high quality
- **Channels**: Mono (optimized for speech)
- **Chunk Size**: 100ms for low latency
- **Formats**: WebM (preferred), WAV (fallback)

### WebSocket Events
- `connect/disconnect` - Connection management
- `audio` - Real-time audio streaming
- `text` - Text message exchange
- `control` - Session control (start/end/pause)
- `error` - Error handling and recovery

### Backend Integration
The frontend is designed to work with the existing AWS backend:
- **REST API**: User management, session metadata
- **WebSocket**: Real-time audio streaming to Nova Sonic 2
- **AgentCore**: Conversation memory and context
- **DynamoDB**: Session storage and user profiles

## Testing

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Microphone permission and audio capture
- [ ] WebSocket connection establishment
- [ ] Session start/end functionality
- [ ] Audio streaming and playback
- [ ] Role-based interface switching
- [ ] Error handling and recovery
- [ ] Responsive design (desktop/mobile)

### Browser Compatibility
- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

## Deployment

### Production Deployment
1. **Build the application**
   ```bash
   npm run build
   ```

2. **Deploy to AWS Amplify or S3 + CloudFront**
   - Configure environment variables
   - Set up custom domain (if needed)
   - Enable HTTPS and security headers

3. **Environment Configuration**
   - Update API endpoints for production
   - Configure Cognito for production domain
   - Set up monitoring and logging

## Troubleshooting

### Common Issues

**Audio not working**
- Check microphone permissions in browser
- Verify HTTPS connection (required for audio)
- Test with different audio formats

**WebSocket connection fails**
- Verify AWS credentials and region
- Check API Gateway WebSocket endpoint
- Ensure proper CORS configuration

**Authentication issues**
- Verify Cognito configuration
- Check user pool and client ID
- Ensure MFA settings match backend

### Debug Mode
Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'true');
```

## Contributing

This is a hackathon project for Breaking Barriers UK 2026. The codebase is designed to be:
- **Self-contained**: Works with or without backend for testing
- **Professional**: Clean, documented, and maintainable code
- **Scalable**: Ready for production deployment
- **Compliant**: Follows all hackathon constraints and security requirements

## License

Built for AWS Breaking Barriers UK 2026 Hackathon
© 2026 - UKind Therapy Charity

---

**Remember**: AWS accounts terminate at 23:00 on 15th January 2026 - ensure all code is saved locally before this deadline! 🏆