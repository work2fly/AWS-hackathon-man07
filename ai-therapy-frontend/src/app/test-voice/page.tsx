'use client';

/**
 * Simple Voice-to-Voice Test Page
 * 🏆 Breaking Barriers UK 2026 compliant
 * 
 * Direct WebSocket connection - no complex hooks or state management
 */

import { useState, useEffect, useRef } from 'react';

export default function TestVoicePage() {
  const [status, setStatus] = useState('Not connected');
  const [messages, setMessages] = useState<string[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioChunksRef = useRef<string[]>([]);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const WEBSOCKET_URL = 'wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev';
  const SILENCE_THRESHOLD = 1500; // 1.5 seconds
  const VOLUME_THRESHOLD = 15;

  const addMessage = (msg: string) => {
    setMessages(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
    console.log(msg);
  };

  // Connect to WebSocket
  const connectWebSocket = () => {
    try {
      addMessage('🔗 Connecting to WebSocket...');
      const ws = new WebSocket(WEBSOCKET_URL);
      
      ws.onopen = () => {
        setStatus('✅ Connected');
        addMessage('✅ WebSocket connected!');
        wsRef.current = ws;
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          addMessage(`📨 Received: ${message.type}`);
          
          if (message.type === 'audio' && message.payload?.audioData) {
            // Play received audio
            playAudio(message.payload.audioData, message.payload.format || 'wav');
          } else if (message.type === 'text') {
            addMessage(`💬 AI: ${message.payload.text}`);
          }
        } catch (error) {
          addMessage(`❌ Parse error: ${error}`);
        }
      };
      
      ws.onerror = (error) => {
        setStatus('❌ Error');
        addMessage(`❌ WebSocket error: ${JSON.stringify(error)}`);
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = (event) => {
        setStatus('🔌 Disconnected');
        addMessage(`🔌 Disconnected: ${event.code} - ${event.reason}`);
        wsRef.current = null;
      };
      
    } catch (error) {
      addMessage(`❌ Connection failed: ${error}`);
    }
  };

  // Initialize audio
  const initAudio = async () => {
    try {
      addMessage('🎤 Requesting microphone access...');
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 44100,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      
      addMessage('✅ Microphone access granted');
      
      // Create audio context for volume monitoring
      audioContextRef.current = new AudioContext({ sampleRate: 44100 });
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      // Start volume monitoring
      monitorVolume();
      
      // Create media recorder
      const options: MediaRecorderOptions = {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 64000,
      };
      
      if (!MediaRecorder.isTypeSupported(options.mimeType!)) {
        options.mimeType = 'audio/wav';
      }
      
      mediaRecorderRef.current = new MediaRecorder(stream, options);
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          // Convert to base64 and store
          event.data.arrayBuffer().then(arrayBuffer => {
            const uint8Array = new Uint8Array(arrayBuffer);
            const binaryString = Array.from(uint8Array)
              .map(byte => String.fromCharCode(byte))
              .join('');
            const base64Audio = btoa(binaryString);
            audioChunksRef.current.push(base64Audio);
          });
        }
      };
      
      mediaRecorderRef.current.onstart = () => {
        setIsRecording(true);
        audioChunksRef.current = [];
        addMessage('🎤 Recording started');
      };
      
      mediaRecorderRef.current.onstop = () => {
        setIsRecording(false);
        addMessage('🎤 Recording stopped');
      };
      
      return true;
    } catch (error) {
      addMessage(`❌ Microphone error: ${error}`);
      return false;
    }
  };

  // Monitor volume for voice activity detection
  const monitorVolume = () => {
    if (!analyserRef.current) return;
    
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const updateVolume = () => {
      if (!analyserRef.current) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) {
        sum += dataArray[i] * dataArray[i];
      }
      
      const rms = Math.sqrt(sum / bufferLength);
      const volume = Math.min(100, (rms / 255) * 100);
      setVolumeLevel(volume);
      
      // Voice activity detection
      if (isRecording) {
        if (volume > VOLUME_THRESHOLD) {
          // User is speaking - clear silence timer
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        } else {
          // Silence detected - start timer if not already started
          if (!silenceTimerRef.current && audioChunksRef.current.length > 0) {
            silenceTimerRef.current = setTimeout(() => {
              addMessage('🤫 Silence detected - processing audio...');
              processAudio();
              silenceTimerRef.current = null;
            }, SILENCE_THRESHOLD);
          }
        }
      }
      
      requestAnimationFrame(updateVolume);
    };
    
    updateVolume();
  };

  // Process accumulated audio
  const processAudio = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      addMessage('❌ WebSocket not connected');
      return;
    }
    
    if (audioChunksRef.current.length === 0) {
      addMessage('⚠️ No audio to process');
      return;
    }
    
    // Combine all chunks
    const combinedAudio = audioChunksRef.current.join('');
    addMessage(`📤 Sending ${audioChunksRef.current.length} audio chunks (${combinedAudio.length} bytes)`);
    
    // Clear chunks
    audioChunksRef.current = [];
    
    // Send pause signal to backend
    const message = {
      type: 'control',
      payload: {
        action: 'pause'
      },
      timestamp: new Date().toISOString()
    };
    
    wsRef.current.send(JSON.stringify(message));
    addMessage('📤 Sent pause signal');
  };

  // Play audio response
  const playAudio = async (base64Audio: string, format: string) => {
    try {
      addMessage(`🔊 Playing AI response (${format})...`);
      
      // Decode base64
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create blob and play
      const blob = new Blob([bytes], { type: `audio/${format}` });
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        addMessage('✅ Audio playback finished');
      };
      
      audio.onerror = (error) => {
        addMessage(`❌ Audio playback error: ${error}`);
      };
      
      await audio.play();
    } catch (error) {
      addMessage(`❌ Play audio error: ${error}`);
    }
  };

  // Start session
  const startSession = async () => {
    addMessage('🚀 Starting session...');
    
    // Connect WebSocket
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      connectWebSocket();
      
      // Wait for connection
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Initialize audio
    const audioReady = await initAudio();
    if (!audioReady) {
      addMessage('❌ Failed to initialize audio');
      return;
    }
    
    // Send start session message
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = {
        type: 'control',
        payload: {
          action: 'start_session',
          sessionId: `session_${Date.now()}`
        },
        timestamp: new Date().toISOString()
      };
      
      wsRef.current.send(JSON.stringify(message));
      addMessage('📤 Sent start_session');
      
      // Start recording
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.start(100); // 100ms chunks
        addMessage('🎤 Continuous listening started');
      }
    } else {
      addMessage('❌ WebSocket not ready');
    }
  };

  // Stop session
  const stopSession = () => {
    addMessage('🛑 Stopping session...');
    
    // Stop recording
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
    
    // Send end session
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = {
        type: 'control',
        payload: {
          action: 'end_session'
        },
        timestamp: new Date().toISOString()
      };
      
      wsRef.current.send(JSON.stringify(message));
      addMessage('📤 Sent end_session');
    }
    
    // Clear timers
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-purple-900">
          🎤 Voice-to-Voice Test
        </h1>
        
        {/* Status */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold mb-2">{status}</div>
            <div className="text-sm text-gray-600">
              WebSocket: {WEBSOCKET_URL}
            </div>
          </div>
        </div>
        
        {/* Controls */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-center space-x-4">
            <button
              onClick={startSession}
              disabled={isRecording}
              className="px-8 py-4 bg-green-600 text-white rounded-lg font-bold text-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              🚀 Start Session
            </button>
            
            <button
              onClick={stopSession}
              disabled={!isRecording}
              className="px-8 py-4 bg-red-600 text-white rounded-lg font-bold text-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              🛑 Stop Session
            </button>
          </div>
          
          {/* Volume indicator */}
          {isRecording && (
            <div className="mt-6">
              <div className="text-center text-sm text-gray-600 mb-2">
                Voice Level: {volumeLevel.toFixed(0)}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div 
                  className="bg-gradient-to-r from-green-400 to-green-600 h-4 rounded-full transition-all duration-150"
                  style={{ width: `${Math.min(volumeLevel, 100)}%` }}
                />
              </div>
              <div className="text-center text-xs text-gray-500 mt-2">
                {volumeLevel > VOLUME_THRESHOLD ? '🎤 Speaking...' : '🤫 Silence...'}
              </div>
            </div>
          )}
        </div>
        
        {/* Messages log */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">📋 Activity Log</h2>
          <div className="bg-gray-50 rounded p-4 h-96 overflow-y-auto font-mono text-sm">
            {messages.length === 0 ? (
              <div className="text-gray-400 text-center">No messages yet...</div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className="mb-1">
                  {msg}
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-bold text-blue-900 mb-2">📖 Instructions:</h3>
          <ol className="list-decimal list-inside space-y-1 text-blue-800 text-sm">
            <li>Click "Start Session" to begin</li>
            <li>Speak into your microphone</li>
            <li>Stop speaking for 1.5 seconds</li>
            <li>AI will process and respond with audio</li>
            <li>Repeat the conversation</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
