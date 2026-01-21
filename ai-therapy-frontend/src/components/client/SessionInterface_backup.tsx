'use client';

// Client session interface with avatar and REAL voice therapy
// 🏆 Breaking Barriers UK 2026 compliant
// Integrated with Web Speech API + Claude + Polly

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { VideoAvatar } from '@/components/client/VideoAvatar';
// import { FramerAvatar } from '@/components/client/FramerAvatar'; // Animated - not realistic
// import { SimpleAnimatedAvatar } from '@/components/client/SimpleAnimatedAvatar'; // CSS only
// import { ThreeFiberAvatar } from '@/components/client/ThreeFiberAvatar'; // 3D - too slow
// import { BabylonAvatar } from '@/components/client/BabylonAvatar'; // OLD - commented out
import { 
  Mic, 
  MicOff, 
  Phone, 
  PhoneOff,
  Activity,
  Heart,
  MessageCircle
} from 'lucide-react';

// Extend Window interface for webkitSpeechRecognition
declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }
}

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
  
  // Voice therapy state
  const [session, setSession] = useState<SessionState>({
    isActive: false,
    sessionId: null,
    startTime: null,
    duration: 0,
    messageCount: 0,
  });
  
  const [status, setStatus] = useState('Ready');
  const [messages, setMessages] = useState<string[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [pollyVoice, setPollyVoice] = useState<'Joanna' | 'Matthew'>('Joanna');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [audioError, setAudioError] = useState<string | null>(null);
  const [showVoiceSelector, setShowVoiceSelector] = useState(false);
  
  const recognitionRef = useRef<any>(null);
  const API_URL = 'https://xi8ekw0fj6.execute-api.us-west-2.amazonaws.com/dev';

  const addMessage = (msg: string) => {
    setMessages(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
    console.log(msg);
  };

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';
        
        recognitionRef.current.onresult = (event: any) => {
          let interimTranscript = '';
          let finalTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript + ' ';
            } else {
              interimTranscript += transcript;
            }
          }
          
          if (finalTranscript) {
            setTranscript(finalTranscript.trim());
            addMessage(`📝 You: ${finalTranscript.trim()}`);
            processText(finalTranscript.trim());
          } else if (interimTranscript) {
            setStatus(`🎤 Listening: "${interimTranscript}"`);
            setTranscript(interimTranscript);
            // Simulate volume level for avatar
            setVolumeLevel(50 + Math.random() * 50);
          }
        };
        
        recognitionRef.current.onerror = (event: any) => {
          addMessage(`❌ Recognition error: ${event.error}`);
          setAudioError(`Recognition error: ${event.error}`);
          setIsListening(false);
          setStatus('❌ Error');
          setVolumeLevel(0);
        };
        
        recognitionRef.current.onend = () => {
          setIsListening(false);
          setVolumeLevel(0);
          if (status.includes('Listening')) {
            setStatus('✅ Ready');
          }
        };
      } else {
        addMessage('❌ Speech Recognition not supported');
        setAudioError('Speech Recognition not supported in this browser');
        setStatus('❌ Not Supported');
      }
    }
  }, []);

  // Process text with Claude + Polly
  const processText = async (text: string) => {
    try {
      addMessage('📤 Sending to AI...');
      setStatus('🤖 AI Processing...');
      setIsSpeaking(false);
      setVolumeLevel(0);
      
      console.log('🔊 FRONTEND: Current pollyVoice state:', pollyVoice);
      console.log('🔊 FRONTEND: Sending request with voice:', pollyVoice);
      
      const requestBody = {
        sessionId: session.sessionId,
        audioData: btoa(text),
        format: 'text',
        sampleRate: 16000,
        userText: text,
        pollyVoice: pollyVoice
      };
      
      console.log('🔊 FRONTEND: Request body:', JSON.stringify(requestBody, null, 2));
      
      const response = await fetch(`${API_URL}/process-audio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', errorText);
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      addMessage('✅ AI response received');
      
      if (result.text) {
        addMessage(`💬 AI: ${result.text}`);
        setSession(prev => ({ ...prev, messageCount: prev.messageCount + 1 }));
        
        if (result.audioData && result.voiceEngine === 'polly-neural') {
          addMessage('🔊 Playing response...');
          await playPollyAudio(result.audioData, result.format || 'mp3');
        }
      }
      
      setStatus('✅ Ready - Click "Start Talking"');
      
    } catch (error) {
      addMessage(`❌ Error: ${error}`);
      setAudioError(`Processing error: ${error}`);
      setStatus('❌ Error');
      setIsSpeaking(false);
    }
  };

  // Play Polly audio
  const playPollyAudio = async (base64Audio: string, format: string) => {
    return new Promise<void>((resolve, reject) => {
      try {
        setStatus('🔊 AI Speaking...');
        setIsSpeaking(true);
        
        const binaryString = atob(base64Audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        
        const blob = new Blob([bytes], { type: `audio/${format}` });
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          addMessage('✅ Response finished');
          setStatus('✅ Ready - Click "Start Talking"');
          setIsSpeaking(false);
          resolve();
        };
        
        audio.onerror = (error) => {
          addMessage(`❌ Playback error`);
          setStatus('❌ Error');
          setIsSpeaking(false);
          reject(error);
        };
        
        audio.play();
      } catch (error) {
        addMessage(`❌ Play error`);
        setStatus('❌ Error');
        setIsSpeaking(false);
        reject(error);
      }
    });
  };

  // Start listening
  const startListening = () => {
    if (recognitionRef.current && !isListening && session.isActive) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        setStatus('🎤 Listening...');
        addMessage('🎤 Listening - speak now!');
        setTranscript('');
      } catch (error) {
        addMessage(`❌ Error: ${error}`);
        setAudioError(`Recognition error: ${error}`);
      }
    }
  };

  // Stop listening
  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      setStatus('🛑 Stopped');
      addMessage('🛑 Stopped listening');
      setVolumeLevel(0);
    }
  };

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

  // Start session with voice selection
  const startSession = useCallback(() => {
    if (!session.isActive) {
      setShowVoiceSelector(true);
    }
  }, [session.isActive]);

  // Confirm voice and start
  const confirmVoiceAndStart = useCallback(() => {
    const sessionId = `session_${Date.now()}`;
    console.log('✅ CONFIRM: Current pollyVoice state:', pollyVoice);
    console.log('✅ Starting session with voice:', pollyVoice); // DEBUG
    setSession({
      isActive: true,
      sessionId,
      startTime: new Date(),
      duration: 0,
      messageCount: 0,
    });
    setShowVoiceSelector(false);
    setStatus('✅ Ready - Click "Start Talking"');
    addMessage(`🚀 Session started: ${sessionId}`);
    addMessage(`🎤 Voice: ${pollyVoice} (${pollyVoice === 'Joanna' ? 'Female' : 'Male'})`);
  }, [pollyVoice]);

  // End session
  const endSession = useCallback(() => {
    if (isListening) {
      stopListening();
    }
    
    addMessage('🛑 Session ended');
    
    setSession({
      isActive: false,
      sessionId: null,
      startTime: null,
      duration: 0,
      messageCount: 0,
    });
    
    setStatus('Ready');
    setTranscript('');
    setMessages([]);
    setVolumeLevel(0);
    setIsSpeaking(false);
  }, [isListening]);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getConnectionStatusColor = () => {
    if (session.isActive) return 'bg-green-500';
    return 'bg-gray-400';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          {t('session.title')}
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          {t('session.welcome').replace('{name}', user?.profile.firstName || user?.email || 'there')}
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
                  {session.isActive ? 'Connected to AI Therapist' : 'Ready to Connect'}
                </span>
                <p className="text-sm text-gray-600">
                  {session.isActive ? 'Your session is active and secure' : 'Click "Start Session" when ready'}
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
            {/* Video Avatar - REALISTIC & PROFESSIONAL! */}
            <div className="relative w-full max-w-md h-96 overflow-visible">
              <VideoAvatar
                isActive={session.isActive}
                isSpeaking={isSpeaking}
                isListening={isListening}
                volumeLevel={volumeLevel}
              />
              
              {/* Volume indicator overlay */}
              {isListening && (
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
                  ? (isListening ? 'Listening to you...' : isSpeaking ? 'Speaking to you...' : 'Ready to listen')
                  : t('session.therapist.ready')
                }
              </p>
              {transcript && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg max-w-md">
                  <div className="text-sm text-gray-600">You're saying:</div>
                  <div className="text-lg font-medium text-blue-900">{transcript}</div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Session Controls */}
      <Card className="mb-8 border-0 shadow-lg">
        <CardContent className="pt-8">
          <div className="flex flex-col items-center space-y-6">
            {!session.isActive ? (
              <div className="text-center space-y-6 w-full max-w-2xl">
                <Button
                  onClick={startSession}
                  size="lg"
                  className="bg-purple-600 hover:bg-purple-700 text-white px-12 py-4 text-lg rounded-full shadow-lg hover:shadow-xl transition-all"
                >
                  <Heart className="mr-3 h-6 w-6" />
                  {t('session.start')}
                </Button>
                
                {/* Voice Selection - appears after clicking Start */}
                {showVoiceSelector && (
                  <div className="border-2 border-purple-300 rounded-xl p-6 bg-purple-50">
                    <h3 className="text-xl font-bold text-purple-900 mb-2">Choose Your Therapist's Voice</h3>
                    <p className="text-sm text-gray-600 mb-4">Select the voice that feels most comfortable for you</p>
                    
                    <div className="flex justify-center space-x-4 mb-6">
                      <button
                        onClick={() => {
                          console.log('🟣 Setting voice to Joanna');
                          setPollyVoice('Joanna');
                          console.log('🟣 Voice state after set:', 'Joanna');
                        }}
                        className={`px-8 py-6 rounded-xl font-bold text-lg transition transform hover:scale-105 ${
                          pollyVoice === 'Joanna'
                            ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        👩 Female Voice
                        <div className="text-sm font-normal mt-1">Joanna - Warm & Caring</div>
                      </button>
                      
                      <button
                        onClick={() => {
                          console.log('🔵 Setting voice to Matthew');
                          setPollyVoice('Matthew');
                          console.log('🔵 Voice state after set:', 'Matthew');
                        }}
                        className={`px-8 py-6 rounded-xl font-bold text-lg transition transform hover:scale-105 ${
                          pollyVoice === 'Matthew'
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        👨 Male Voice
                        <div className="text-sm font-normal mt-1">Matthew - Calm & Supportive</div>
                      </button>
                    </div>
                    
                    <div className="flex justify-center space-x-4">
                      <Button
                        onClick={confirmVoiceAndStart}
                        size="lg"
                        className="bg-purple-600 hover:bg-purple-700 text-white px-12 py-4"
                      >
                        Start Session with {pollyVoice}
                      </Button>
                      <Button
                        onClick={() => setShowVoiceSelector(false)}
                        variant="outline"
                        size="lg"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}
                
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
                  onClick={startListening}
                  disabled={isListening || isSpeaking}
                  size="lg"
                  className="bg-green-600 hover:bg-green-700 text-white rounded-full px-8 py-4 disabled:bg-gray-400"
                >
                  <Mic className="mr-2 h-5 w-5" />
                  Start Talking
                </Button>
                
                <Button
                  onClick={stopListening}
                  disabled={!isListening}
                  size="lg"
                  variant="outline"
                  className="rounded-full px-8 py-4 border-red-300 text-red-600 hover:bg-red-50 disabled:opacity-50"
                >
                  <MicOff className="mr-2 h-5 w-5" />
                  Stop
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

      {/* Activity Log - REMOVED */}

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
