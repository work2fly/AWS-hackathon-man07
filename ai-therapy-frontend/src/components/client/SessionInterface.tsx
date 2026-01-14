'use client';

// Client session interface with avatar and audio
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useLanguage } from '@/contexts/LanguageContext';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAudio } from '@/hooks/useAudio';
import { Button } from '@/components/ui/button';
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
  MessageCircle
} from 'lucide-react';

interface SessionState {
  isActive: boolean;
  sessionId: string | null;
  startTime: Date | null;
  duration: number;
  messageCount: number;
}

export function SessionInterface() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { 
    isConnected, 
    connect, 
    disconnect, 
    sendAudio, 
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

  const [session, setSession] = useState<SessionState>({
    isActive: false,
    sessionId: null,
    startTime: null,
    duration: 0,
    messageCount: 0,
  });

  const [isMuted, setIsMuted] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  
  // Manual control states for when audio doesn't work
  const [manualSpeaking, setManualSpeaking] = useState(false);
  const [manualListening, setManualListening] = useState(false);

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
        // Play received audio from AI
        playAudio(message.payload.audioData, message.payload.format || 'webm');
        setSession(prev => ({ ...prev, messageCount: prev.messageCount + 1 }));
      }
    };

    const handleTextMessage = (message: any) => {
      if (message.payload?.isFromAI) {
        setSession(prev => ({ ...prev, messageCount: prev.messageCount + 1 }));
      }
    };

    addEventListener('audio', handleAudioMessage);
    addEventListener('text', handleTextMessage);

    return () => {
      removeEventListener('audio', handleAudioMessage);
      removeEventListener('text', handleTextMessage);
    };
  }, [addEventListener, removeEventListener, playAudio]);

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
      
      // Initialize audio first when starting session
      if (!isInitialized) {
        console.log('Initializing audio...');
        const audioInitialized = await initializeAudio();
        if (!audioInitialized) {
          console.error('Audio initialization failed');
          setConnectionStatus('disconnected');
          return;
        }
        console.log('Audio initialized successfully');
      }
      
      // Connect to WebSocket if not connected
      if (!isConnected) {
        console.log('Connecting to WebSocket...');
        await connect();
        console.log('WebSocket connected');
      }
      
      // Generate session ID
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      console.log('Starting session:', sessionId);
      
      // Send start session control message
      const success = sendControl('start_session', sessionId);
      
      if (success) {
        setSession({
          isActive: true,
          sessionId,
          startTime: new Date(),
          duration: 0,
          messageCount: 0,
        });
        
        console.log('Session started successfully');
        
        // Start recording after a small delay to ensure everything is ready
        setTimeout(async () => {
          if (canRecord) {
            console.log('Starting audio recording...');
            const recordingStarted = await startRecording();
            if (recordingStarted) {
              console.log('Audio recording started');
            } else {
              console.error('Failed to start audio recording');
            }
          } else {
            console.warn('Cannot record - audio not ready');
          }
        }, 500);
      } else {
        console.error('Failed to send start session control');
        setConnectionStatus('disconnected');
      }
    } catch (error) {
      console.error('Failed to start session:', error);
      setConnectionStatus('disconnected');
    }
  }, [isConnected, connect, sendControl, isInitialized, initializeAudio, canRecord, startRecording]);

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
    
    disconnect();
    setConnectionStatus('disconnected');
  }, [session.sessionId, sendControl, stopRecording, cleanup, disconnect]);

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
          {t('session.title')}
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          {t('session.welcome').replace('{name}', user?.profile.firstName || '[firstName]')}
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

      {/* AI Therapist Section */}
      <Card className="mb-8 border-0 shadow-lg overflow-visible">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl text-gray-900">{t('session.therapist.title')}</CardTitle>
          <CardDescription className="text-gray-600">
            {t('session.therapist.subtitle')}
          </CardDescription>
        </CardHeader>
        <CardContent className="overflow-visible">
          <div className="flex flex-col items-center space-y-6">
            {/* 3D AI Avatar - Babylon.js */}
            <div className="relative w-full max-w-md h-96 overflow-visible">
              <BabylonAvatar
                isActive={session.isActive}
                isSpeaking={manualSpeaking || (session.isActive && !isRecording && session.messageCount > 0)}
                isListening={manualListening || (session.isActive && isRecording)}
                volumeLevel={volumeLevel}
                modelUrl="https://models.readyplayer.me/692c94887b7a88e1f63f3d82.glb?pose=A&morphTargets=ARKit"
              />
              
              {/* Volume indicator overlay */}
              {isRecording && (
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
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{t('session.therapist.name')}</h3>
              <p className="text-gray-600 max-w-md">
                {session.isActive 
                  ? t('session.therapist.listening')
                  : t('session.therapist.ready')
                }
              </p>
            </div>
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
                      {t('session.start')}
                    </>
                  )}
                </Button>
                <p className="text-sm text-gray-600">
                  {t('session.privacy')}
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
                  onClick={toggleMute}
                  variant={isMuted ? "destructive" : "secondary"}
                  size="lg"
                  className="rounded-full px-8 py-4"
                >
                  {isMuted ? (
                    <>
                      <MicOff className="mr-2 h-5 w-5" />
                      Unmute
                    </>
                  ) : (
                    <>
                      <Mic className="mr-2 h-5 w-5" />
                      Mute
                    </>
                  )}
                </Button>
                
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

      {/* Manual Avatar Controls (for when audio doesn't work) */}
      <Card className="mb-8 border-0 shadow-lg bg-blue-50">
        <CardHeader className="text-center pb-4">
          <CardTitle className="text-lg text-gray-900">🎭 Avatar Controls</CardTitle>
          <CardDescription className="text-sm text-gray-600">
            Simulate talking and listening when audio isn't working
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center space-x-4">
            <Button
              onClick={() => setManualListening(!manualListening)}
              variant={manualListening ? "default" : "outline"}
              size="lg"
              className={`rounded-full px-8 py-4 ${
                manualListening 
                  ? 'bg-green-600 hover:bg-green-700 text-white' 
                  : 'border-green-300 text-green-600 hover:bg-green-50'
              }`}
            >
              <Mic className="mr-2 h-5 w-5" />
              {manualListening ? 'Stop Listening' : 'Start Listening'}
            </Button>
            
            <Button
              onClick={() => setManualSpeaking(!manualSpeaking)}
              variant={manualSpeaking ? "default" : "outline"}
              size="lg"
              className={`rounded-full px-8 py-4 ${
                manualSpeaking 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                  : 'border-blue-300 text-blue-600 hover:bg-blue-50'
              }`}
            >
              <MessageCircle className="mr-2 h-5 w-5" />
              {manualSpeaking ? 'Stop Talking' : 'Start Talking'}
            </Button>
          </div>
          
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              {manualListening && manualSpeaking && '🎭 Both states active - Avatar is listening and talking'}
              {manualListening && !manualSpeaking && '👂 Avatar is listening to you'}
              {!manualListening && manualSpeaking && '💬 Avatar is talking to you'}
              {!manualListening && !manualSpeaking && '😌 Avatar is in idle state'}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* System Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card className="border-0 shadow-md">
          <CardContent className="pt-6 text-center">
            <div className="text-3xl mb-2">
              {audioReady ? '✅' : '❌'}
            </div>
            <div className="text-sm font-medium text-gray-900">{t('session.audio.system')}</div>
            <div className="text-xs text-gray-600">
              {audioReady ? t('session.audio.ready') : t('session.audio.checking')}
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-0 shadow-md">
          <CardContent className="pt-6 text-center">
            <div className="text-3xl mb-2">
              {isRecording ? '🎤' : '🔇'}
            </div>
            <div className="text-sm font-medium text-gray-900">{t('session.audio.microphone')}</div>
            <div className="text-xs text-gray-600">
              {isRecording ? t('session.recording') : t('session.audio.standby')}
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-0 shadow-md">
          <CardContent className="pt-6 text-center">
            <div className="text-sm font-medium text-gray-900 mb-2">{t('session.audio.voiceLevel')}</div>
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-150"
                style={{ width: `${Math.min(volumeLevel, 100)}%` }}
              />
            </div>
            <div className="text-xs text-gray-600">
              {session.isActive && isRecording ? t('session.audio.listening') : t('session.audio.silent')}
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-0 shadow-md">
          <CardContent className="pt-6 text-center">
            <div className="text-3xl mb-2">
              {isConnected ? '🔗' : '📡'}
            </div>
            <div className="text-sm font-medium text-gray-900">{t('session.audio.connection')}</div>
            <div className="text-xs text-gray-600">
              {isConnected ? t('session.audio.secure') : t('session.audio.standby')}
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

      {/* Ally Branding Footer */}
      <div className="text-center py-8 border-t border-gray-200">
        <div className="flex items-center justify-center mb-4">
          <Heart className="h-5 w-5 text-purple-600 mr-2" />
          <span className="text-gray-600">Powered by Ally & AWS Innovation</span>
        </div>
        <Badge variant="secondary" className="bg-purple-100 text-purple-800">
          🏆 Breaking Barriers UK 2026 - Empowering Healing Through Technology
        </Badge>
      </div>
    </div>
  );
}