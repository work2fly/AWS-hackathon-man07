'use client';

// Client session interface with avatar and audio
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAudio } from '@/hooks/useAudio';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { BabylonAvatar } from '@/components/client/BabylonAvatar';
import { 
  Mic, 
  MicOff, 
  Phone, 
  PhoneOff, 
  Volume2, 
  VolumeX,
  Activity,
  Heart,
  MessageCircle,
  Send
} from 'lucide-react';

interface SessionState {
  isActive: boolean;
  sessionId: string | null;
  startTime: Date | null;
  duration: number;
  messageCount: number;
}

interface ChatMessage {
  id: string;
  text: string;
  isFromAI: boolean;
  timestamp: Date;
}

export function SessionInterface() {
  const { user } = useAuth();
  const { 
    isConnected, 
    connect, 
    disconnect, 
    sendAudio,
    sendText,
    sendMessage,
    sendControl, 
    addEventListener, 
    removeEventListener 
  } = useWebSocket();
  
  const {
    isInitialized,
    isRecording,
    volumeLevel,
    error: audioError,
    initialize: initializeAudio,
    startRecording,
    stopRecording,
    playAudio,
    setOnAudioData,
    canRecord,
    isReady: audioReady,
    cleanup
  } = useAudio();
  
  const {
    isListening: isSpeechListening,
    transcript: speechTranscript,
    interimTranscript,
    isSupported: speechSupported,
    error: speechError,
    startListening: startSpeechListening,
    stopListening: stopSpeechListening,
    resetTranscript,
    setOnTranscript
  } = useSpeechRecognition();

  const [session, setSession] = useState<SessionState>({
    isActive: false,
    sessionId: null,
    startTime: null,
    duration: 0,
    messageCount: 0,
  });

  const [isMuted, setIsMuted] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [messageInput, setMessageInput] = useState('');
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isAIPlaying, setIsAIPlaying] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Initialize audio and WebSocket
  useEffect(() => {
    // Don't initialize audio until session starts
    // Audio will be initialized when user clicks "Start Session"
  }, []);

  // Setup audio data streaming only when session is active
  useEffect(() => {
    if (session.isActive && isInitialized) {
      setOnAudioData((audioData) => {
        if (isConnected && !isMuted) {
          const format = audioData.format as 'webm' | 'wav' | 'mp3';
          sendAudio(audioData.data, format);
        }
      });
    } else {
      // Clear audio data handler when session is not active
      setOnAudioData(() => {});
    }
  }, [session.isActive, isInitialized, isConnected, isMuted, setOnAudioData, sendAudio]);

  // Setup WebSocket event listeners
  useEffect(() => {
    const handleAudioMessage = (message: any) => {
      if (message.payload?.audioData) {
        console.log('🔊 Audio message received, setting AI as speaking');
        
        // Decode base64 audio data to ArrayBuffer
        const audioData = message.payload.audioData;
        let arrayBuffer: ArrayBuffer;
        
        if (typeof audioData === 'string') {
          // Base64 string from backend - decode it
          const binaryString = atob(audioData);
          const bytes = new Uint8Array(binaryString.length);
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
          }
          arrayBuffer = bytes.buffer;
        } else {
          // Already an ArrayBuffer
          arrayBuffer = audioData;
        }
        
        // Set AI as speaking BEFORE playing
        setIsAIPlaying(true);
        console.log('✅ isAIPlaying set to TRUE');
        
        // Play received audio from AI
        playAudio(arrayBuffer, message.payload.format || 'mp3').then(() => {
          console.log('🎵 Audio finished playing');
          // Audio finished playing - wait a bit before stopping animation
          setTimeout(() => {
            setIsAIPlaying(false);
            console.log('✅ isAIPlaying set to FALSE');
          }, 500);
        }).catch((error) => {
          console.error('❌ Audio playback error:', error);
          setIsAIPlaying(false);
        });
        
        setSession(prev => ({ ...prev, messageCount: prev.messageCount + 1 }));
      }
    };

    const handleTextMessage = (message: any) => {
      if (message.payload?.text) {
        // Add AI message to chat
        const newMessage: ChatMessage = {
          id: `msg_${Date.now()}_${Math.random()}`,
          text: message.payload.text,
          isFromAI: message.payload.isFromAI || false,
          timestamp: new Date()
        };
        
        setChatMessages(prev => [...prev, newMessage]);
        
        if (message.payload.isFromAI) {
          setSession(prev => ({ ...prev, messageCount: prev.messageCount + 1 }));
        }
      }
    };

    addEventListener('audio', handleAudioMessage);
    addEventListener('text', handleTextMessage);

    return () => {
      removeEventListener('audio', handleAudioMessage);
      removeEventListener('text', handleTextMessage);
    };
  }, [addEventListener, removeEventListener, playAudio]);
  
  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);
  
  // Handle speech recognition transcript
  useEffect(() => {
    setOnTranscript((transcript) => {
      if (transcript && session.isActive) {
        // Auto-send when user finishes speaking
        setMessageInput(transcript);
        // Auto-send after a brief pause
        setTimeout(() => {
          if (transcript === messageInput) {
            sendTextMessage();
          }
        }, 1500);
      }
    });
  }, [setOnTranscript, session.isActive, messageInput]);

  // Update connection status
  useEffect(() => {
    if (isConnected) {
      setConnectionStatus('connected');
    } else {
      setConnectionStatus('disconnected');
    }
  }, [isConnected]);

  // Session timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (session.isActive && session.startTime) {
      interval = setInterval(() => {
        setSession(prev => ({
          ...prev,
          duration: Math.floor((Date.now() - prev.startTime!.getTime()) / 1000)
        }));
      }, 1000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [session.isActive, session.startTime]);

  const startSession = useCallback(async () => {
    try {
      setConnectionStatus('connecting');
      
      // Try to initialize audio, but don't fail if it doesn't work (for demo)
      if (!isInitialized) {
        console.log('Initializing audio...');
        try {
          const audioInitialized = await initializeAudio();
          if (audioInitialized) {
            console.log('Audio initialized successfully');
          } else {
            console.warn('Audio initialization failed - continuing without audio for demo');
          }
        } catch (audioError) {
          console.warn('Audio initialization error - continuing without audio for demo:', audioError);
        }
      }
      
      // Connect to WebSocket if not connected
      if (!isConnected) {
        console.log('Connecting to WebSocket...');
        
        const connected = await connect();
        
        if (!connected) {
          console.error('WebSocket connection failed');
          setConnectionStatus('disconnected');
          return;
        }
        
        console.log('✅ WebSocket connected successfully');
      }
      
      console.log('Proceeding to create session...');
      
      // Generate session ID
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      console.log('Starting session:', sessionId);
      
      // Wait a moment to ensure WebSocket is ready
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Send join_session message
      const joinMessage = {
        type: 'join_session',
        session_id: sessionId,
        timestamp: new Date().toISOString()
      };
      
      console.log('Sending join_session message:', joinMessage);
      const success = sendMessage(joinMessage);
      
      if (!success) {
        console.error('Failed to send join session message');
        setConnectionStatus('disconnected');
        return;
      }
      
      console.log('Join session message sent successfully');
      
      // Set session as active
      setSession({
        isActive: true,
        sessionId,
        startTime: new Date(),
        duration: 0,
        messageCount: 0,
      });
      
      console.log('✅ Session started successfully!');
      
      // Try to start recording if audio is available
      if (canRecord && isInitialized) {
        setTimeout(async () => {
          console.log('Starting audio recording...');
          try {
            const recordingStarted = await startRecording();
            if (recordingStarted) {
              console.log('Audio recording started');
            } else {
              console.warn('Failed to start audio recording - demo will work without audio');
            }
          } catch (recordError) {
            console.warn('Audio recording error - demo will work without audio:', recordError);
          }
        }, 500);
      } else {
        console.log('Audio not available - demo running in text-only mode');
      }
      
    } catch (error) {
      console.error('Failed to start session:', error);
      setConnectionStatus('disconnected');
    }
  }, [isConnected, connect, sendMessage, isInitialized, initializeAudio, canRecord, startRecording]);

  const endSession = useCallback(() => {
    if (session.sessionId) {
      sendControl('end_session', session.sessionId);
    }
    
    // Stop recording and cleanup audio
    stopRecording();
    cleanup(); // This will stop audio monitoring
    
    setSession({
      isActive: false,
      sessionId: null,
      startTime: null,
      duration: 0,
      messageCount: 0,
    });
    
    // Clear chat messages
    setChatMessages([]);
    setMessageInput('');
    
    disconnect();
    setConnectionStatus('disconnected');
  }, [session.sessionId, sendControl, stopRecording, cleanup, disconnect]);

  const sendTextMessage = useCallback(async () => {
    if (!messageInput.trim() || !session.isActive || isSendingMessage) {
      return;
    }
    
    setIsSendingMessage(true);
    
    try {
      // Add user message to chat immediately
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}_${Math.random()}`,
        text: messageInput.trim(),
        isFromAI: false,
        timestamp: new Date()
      };
      
      setChatMessages(prev => [...prev, userMessage]);
      
      // Send to backend
      const success = sendText(messageInput.trim());
      
      if (!success) {
        console.error('Failed to send text message');
      }
      
      // Clear input and reset speech
      setMessageInput('');
      resetTranscript();
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsSendingMessage(false);
    }
  }, [messageInput, session.isActive, isSendingMessage, sendText, resetTranscript]);
  
  const toggleVoiceInput = useCallback(() => {
    if (!speechSupported) {
      alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    
    if (isSpeechListening) {
      stopSpeechListening();
      setIsVoiceMode(false);
    } else {
      const started = startSpeechListening();
      if (started) {
        setIsVoiceMode(true);
      }
    }
  }, [speechSupported, isSpeechListening, startSpeechListening, stopSpeechListening]);
  
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendTextMessage();
    }
  }, [sendTextMessage]);

  const toggleMute = useCallback(() => {
    setIsMuted(prev => !prev);
    if (!isMuted) {
      stopRecording();
    } else if (session.isActive && audioReady) {
      startRecording();
    }
  }, [isMuted, session.isActive, audioReady, stopRecording, startRecording]);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      default: return 'bg-red-500';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Your AI Therapy Session
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Welcome, {user?.profile.firstName || '[firstName]'}. Ready to continue your healing journey with our AI therapist?
        </p>
      </section>

      {/* Connection Status */}
      <Card className="mb-8 border-0 shadow-lg">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full ${getConnectionStatusColor()}`} />
              <div>
                <span className="font-semibold text-gray-900">
                  {connectionStatus === 'connected' ? 'Connected to AI Therapist' : 
                   connectionStatus === 'connecting' ? 'Connecting...' : 'Ready to Connect'}
                </span>
                <p className="text-sm text-gray-600">
                  {connectionStatus === 'connected' ? 'Your session is active and secure' : 
                   connectionStatus === 'connecting' ? 'Establishing secure connection' : 'Click "Start Session" when ready'}
                </p>
              </div>
            </div>
            
            {session.isActive && (
              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{formatDuration(session.duration)}</div>
                  <div className="text-sm text-gray-600">Session Time</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{session.messageCount}</div>
                  <div className="text-sm text-gray-600">Exchanges</div>
                </div>
                <Badge variant="secondary" className="bg-green-100 text-green-800 flex items-center space-x-1">
                  <Activity className="w-3 h-3" />
                  <span>Active Session</span>
                </Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Session Controls */}
      <Card className="mb-8 border-0 shadow-lg">
        <CardContent className="pt-8">
          <div className="flex flex-col items-center space-y-6">
            {!session.isActive ? (
              <div className="text-center space-y-4">
                <Button
                  onClick={startSession}
                  size="lg"
                  className="bg-purple-600 hover:bg-purple-700 text-white px-12 py-4 text-lg rounded-full shadow-lg hover:shadow-xl transition-all"
                  disabled={connectionStatus === 'connecting'}
                >
                  {connectionStatus === 'connecting' ? (
                    <>
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Heart className="mr-3 h-6 w-6" />
                      Start Your Session
                    </>
                  )}
                </Button>
                <p className="text-sm text-gray-600">
                  Your conversation will be private and secure
                </p>
                {audioError && (
                  <p className="text-sm text-red-600">
                    ⚠️ {audioError}
                  </p>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Button
                  onClick={endSession}
                  variant="outline"
                  size="lg"
                  className="rounded-full px-8 py-4 border-red-300 text-red-600 hover:bg-red-50"
                >
                  <PhoneOff className="mr-2 h-5 w-5" />
                  End Session
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* AI Therapist Section - Side by Side Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Left: Avatar */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-gray-900">Your AI Therapist</CardTitle>
            <CardDescription className="text-gray-600">
              Powered by Amazon Bedrock for natural, empathetic conversations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center space-y-6">
              {/* 3D AI Avatar - Babylon.js */}
              <div className="relative w-full h-96">
                <BabylonAvatar
                  isActive={session.isActive}
                  isSpeaking={isAIPlaying}
                  isListening={session.isActive && (isRecording || isSpeechListening)}
                  volumeLevel={isAIPlaying ? 80 : volumeLevel}
                  modelUrl="https://models.readyplayer.me/692c94887b7a88e1f63f3d82.glb?pose=A"
                />
                
                {/* Volume indicator overlay */}
                {(isRecording || isSpeechListening) && (
                  <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 z-10">
                    <div className="bg-white rounded-full px-4 py-2 shadow-lg">
                      <div className="flex items-center space-x-1">
                        {[...Array(5)].map((_, i) => (
                          <div
                            key={i}
                            className={`w-1 h-6 rounded-full transition-all duration-150 ${
                              volumeLevel > (i * 20) ? 'bg-green-500' : 'bg-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Dr. AI Assistant</h3>
                <div className="flex items-center justify-center space-x-2 mb-2">
                  {isAIPlaying && (
                    <Badge className="bg-green-500 text-white animate-pulse">
                      🔊 Speaking
                    </Badge>
                  )}
                  {(isRecording || isSpeechListening) && (
                    <Badge className="bg-blue-500 text-white animate-pulse">
                      👂 Listening
                    </Badge>
                  )}
                  {!isAIPlaying && !isRecording && !isSpeechListening && session.isActive && (
                    <Badge className="bg-gray-400 text-white">
                      💭 Ready
                    </Badge>
                  )}
                </div>
                <p className="text-gray-600 max-w-md">
                  {session.isActive 
                    ? isAIPlaying 
                      ? 'Speaking to you now...'
                      : (isRecording || isSpeechListening)
                        ? 'Listening to you...'
                        : 'Ready to help'
                    : 'Ready to start a compassionate conversation whenever you are'
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Right: Chat Interface - Only show when session is active */}
        {session.isActive && (
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center text-xl text-gray-900">
                <MessageCircle className="mr-2 h-5 w-5 text-purple-600" />
                Chat with Your AI Therapist
              </CardTitle>
              <CardDescription>
                Type or speak your thoughts - your AI therapist is here to listen
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Chat Messages */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4 h-80 overflow-y-auto">
                {chatMessages.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-gray-500">
                    <div className="text-center">
                      <MessageCircle className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                      <p>Start the conversation by typing or speaking</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {chatMessages.map((msg) => (
                      <div
                        key={msg.id}
                        className={`flex ${msg.isFromAI ? 'justify-start' : 'justify-end'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg px-4 py-3 ${
                            msg.isFromAI
                              ? 'bg-white border border-purple-200 text-gray-900'
                              : 'bg-purple-600 text-white'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                          <p className={`text-xs mt-1 ${msg.isFromAI ? 'text-gray-500' : 'text-purple-200'}`}>
                            {msg.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                    <div ref={chatEndRef} />
                  </div>
                )}
              </div>

              {/* Message Input */}
              <div className="flex space-x-2">
                <Button
                  onClick={toggleVoiceInput}
                  disabled={!session.isActive}
                  variant={isVoiceMode ? "default" : "outline"}
                  className={isVoiceMode ? "bg-red-600 hover:bg-red-700 text-white animate-pulse" : ""}
                  title={speechSupported ? "Click to speak" : "Speech not supported in this browser"}
                >
                  {isSpeechListening ? (
                    <MicOff className="h-5 w-5" />
                  ) : (
                    <Mic className="h-5 w-5" />
                  )}
                </Button>
                <Input
                  type="text"
                  placeholder={isSpeechListening ? "Listening... speak now" : (interimTranscript || "Type your message or click mic to speak...")}
                  value={messageInput || interimTranscript}
                  onChange={(e) => setMessageInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={!session.isActive || isSendingMessage || isSpeechListening}
                  className="flex-1"
                />
                <Button
                  onClick={sendTextMessage}
                  disabled={!messageInput.trim() || !session.isActive || isSendingMessage}
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                >
                  {isSendingMessage ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </Button>
              </div>
              
              {speechError && (
                <p className="text-sm text-red-600 mt-2">
                  ⚠️ {speechError}
                </p>
              )}
              
              {!speechSupported && (
                <p className="text-sm text-yellow-600 mt-2">
                  💡 Voice input works best in Chrome, Edge, or Safari
                </p>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* System Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card className="border-0 shadow-md">
          <CardContent className="pt-6 text-center">
            <div className="text-3xl mb-2">
              {audioReady ? '✅' : '❌'}
            </div>
            <div className="text-sm font-medium text-gray-900">Audio System</div>
            <div className="text-xs text-gray-600">
              {audioReady ? 'Ready' : 'Checking...'}
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-0 shadow-md">
          <CardContent className="pt-6 text-center">
            <div className="text-3xl mb-2">
              {isRecording ? '🎤' : '🔇'}
            </div>
            <div className="text-sm font-medium text-gray-900">Microphone</div>
            <div className="text-xs text-gray-600">
              {isRecording ? 'Recording' : 'Standby'}
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-0 shadow-md">
          <CardContent className="pt-6 text-center">
            <div className="text-sm font-medium text-gray-900 mb-2">Voice Level</div>
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-150"
                style={{ width: `${Math.min(volumeLevel, 100)}%` }}
              />
            </div>
            <div className="text-xs text-gray-600">
              {session.isActive && isRecording ? 'Listening' : 'Silent'}
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-0 shadow-md">
          <CardContent className="pt-6 text-center">
            <div className="text-3xl mb-2">
              {isConnected ? '🔗' : '📡'}
            </div>
            <div className="text-sm font-medium text-gray-900">Connection</div>
            <div className="text-xs text-gray-600">
              {isConnected ? 'Secure' : 'Standby'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Error Display */}
      {audioError && (
        <Alert variant="destructive" className="mb-8">
          <AlertDescription>
            <strong>Audio System:</strong> {audioError}
          </AlertDescription>
        </Alert>
      )}

      {/* UKind Branding Footer */}
      <div className="text-center py-8 border-t border-gray-200">
        <div className="flex items-center justify-center mb-4">
          <Heart className="h-5 w-5 text-purple-600 mr-2" />
          <span className="text-gray-600">Powered by UKind Therapy & AWS Innovation</span>
        </div>
        <Badge variant="secondary" className="bg-purple-100 text-purple-800">
          🏆 Breaking Barriers UK 2026 - Empowering Healing Through Technology
        </Badge>
      </div>
    </div>
  );
}