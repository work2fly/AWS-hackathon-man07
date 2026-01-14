'use client';

/**
 * Simple Voice-to-Voice with HTTP Polling (No WebSocket)
 * 🏆 Breaking Barriers UK 2026 compliant
 * 
 * Uses REST API instead of WebSocket for maximum compatibility
 */

import { useState, useRef } from 'react';

export default function VoiceSimplePage() {
  const [status, setStatus] = useState('Ready');
  const [messages, setMessages] = useState<string[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const API_URL = 'https://xi8ekw0fj6.execute-api.us-west-2.amazonaws.com/dev';
  const SILENCE_THRESHOLD = 2000; // 2 seconds
  const VOLUME_THRESHOLD = 15;

  const addMessage = (msg: string) => {
    setMessages(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
    console.log(msg);
  };

  // Initialize audio
  const initAudio = async () => {
    try {
      addMessage('🎤 Requesting microphone access...');
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000, // Lower sample rate for better compatibility
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      
      addMessage('✅ Microphone access granted');
      
      // Create audio context for volume monitoring
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      // Start volume monitoring
      monitorVolume();
      
      // Create media recorder - use WAV for better compatibility
      const options: MediaRecorderOptions = {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 32000, // Lower bitrate
      };
      
      if (!MediaRecorder.isTypeSupported(options.mimeType!)) {
        options.mimeType = 'audio/wav';
        addMessage('⚠️ Using WAV format (WebM not supported)');
      }
      
      mediaRecorderRef.current = new MediaRecorder(stream, options);
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstart = () => {
        setIsRecording(true);
        audioChunksRef.current = [];
        addMessage('🎤 Recording started - speak now!');
      };
      
      mediaRecorderRef.current.onstop = () => {
        setIsRecording(false);
        addMessage('🎤 Recording stopped');
      };
      
      return true;
    } catch (error) {
      addMessage(`❌ Microphone error: ${error}`);
      setStatus('❌ Microphone Error');
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
              addMessage('🤫 Silence detected - processing...');
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

  // Process audio and send to backend
  const processAudio = async () => {
    if (audioChunksRef.current.length === 0) {
      addMessage('⚠️ No audio to process');
      return;
    }
    
    try {
      // Combine all audio chunks
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      addMessage(`📦 Audio recorded: ${(audioBlob.size / 1024).toFixed(2)} KB`);
      
      // Clear chunks
      audioChunksRef.current = [];
      
      // Convert to base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      const binaryString = Array.from(uint8Array)
        .map(byte => String.fromCharCode(byte))
        .join('');
      const base64Audio = btoa(binaryString);
      
      addMessage('📤 Sending to AI...');
      setStatus('🤖 AI Processing...');
      
      // Send to backend via REST API
      const response = await fetch(`${API_URL}/process-audio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId: sessionId,
          audioData: base64Audio,
          format: 'webm',
          sampleRate: 16000
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      addMessage('✅ AI response received');
      
      // Play AI response
      if (result.audioData) {
        await playAudio(result.audioData, result.format || 'wav');
      }
      
      if (result.text) {
        addMessage(`💬 AI: ${result.text}`);
      }
      
      setStatus('✅ Ready for next input');
      
    } catch (error) {
      addMessage(`❌ Processing error: ${error}`);
      setStatus('❌ Error');
    }
  };

  // Play audio response
  const playAudio = async (base64Audio: string, format: string) => {
    try {
      addMessage(`🔊 Playing AI response...`);
      setStatus('🔊 Playing response...');
      
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
        addMessage('✅ Playback finished');
        setStatus('✅ Ready');
      };
      
      audio.onerror = (error) => {
        addMessage(`❌ Playback error: ${error}`);
        setStatus('❌ Playback Error');
      };
      
      await audio.play();
    } catch (error) {
      addMessage(`❌ Play error: ${error}`);
      setStatus('❌ Error');
    }
  };

  // Start session
  const startSession = async () => {
    addMessage('🚀 Starting session...');
    setStatus('🚀 Starting...');
    
    // Generate session ID
    const newSessionId = `session_${Date.now()}`;
    setSessionId(newSessionId);
    addMessage(`📝 Session ID: ${newSessionId}`);
    
    // Initialize audio
    const audioReady = await initAudio();
    if (!audioReady) {
      return;
    }
    
    // Start recording
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.start(500); // 500ms chunks
      setStatus('🎤 Listening...');
      addMessage('✅ Session started - speak now!');
    }
  };

  // Stop session
  const stopSession = () => {
    addMessage('🛑 Stopping session...');
    
    // Stop recording
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
    
    // Clear timers
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    
    setStatus('🛑 Stopped');
    setSessionId(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-purple-900">
          🎤 Ally Voice Therapy
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Simple & Reliable Voice-to-Voice AI
        </p>
        
        {/* Status */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="text-center">
            <div className="text-3xl font-bold mb-2">{status}</div>
            <div className="text-sm text-gray-600">
              {sessionId ? `Session: ${sessionId.slice(-8)}` : 'No active session'}
            </div>
          </div>
        </div>
        
        {/* Controls */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-center space-x-4 mb-6">
            <button
              onClick={startSession}
              disabled={isRecording}
              className="px-12 py-6 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl font-bold text-xl hover:from-green-600 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed shadow-lg transform transition hover:scale-105"
            >
              🚀 Start Session
            </button>
            
            <button
              onClick={stopSession}
              disabled={!isRecording}
              className="px-12 py-6 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-bold text-xl hover:from-red-600 hover:to-red-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed shadow-lg transform transition hover:scale-105"
            >
              🛑 Stop Session
            </button>
          </div>
          
          {/* Volume indicator */}
          {isRecording && (
            <div className="space-y-3">
              <div className="text-center text-lg font-semibold text-gray-700">
                {volumeLevel > VOLUME_THRESHOLD ? '🎤 Listening to you...' : '🤫 Waiting for speech...'}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6">
                <div 
                  className={`h-6 rounded-full transition-all duration-150 ${
                    volumeLevel > VOLUME_THRESHOLD 
                      ? 'bg-gradient-to-r from-green-400 to-green-600' 
                      : 'bg-gradient-to-r from-gray-300 to-gray-400'
                  }`}
                  style={{ width: `${Math.min(volumeLevel, 100)}%` }}
                />
              </div>
              <div className="text-center text-sm text-gray-600">
                Volume: {volumeLevel.toFixed(0)}% | Threshold: {VOLUME_THRESHOLD}%
              </div>
            </div>
          )}
        </div>
        
        {/* Messages log */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <span className="mr-2">📋</span>
            Activity Log
          </h2>
          <div className="bg-gray-900 text-green-400 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
            {messages.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                No activity yet. Click "Start Session" to begin.
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className="mb-1 hover:bg-gray-800 px-2 py-1 rounded">
                  {msg}
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* Instructions */}
        <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-xl p-6">
          <h3 className="font-bold text-blue-900 mb-3 text-lg">📖 How to Use:</h3>
          <ol className="list-decimal list-inside space-y-2 text-blue-800">
            <li className="font-medium">Click <strong>"Start Session"</strong> to begin</li>
            <li className="font-medium">Speak clearly into your microphone</li>
            <li className="font-medium">Stop speaking for <strong>2 seconds</strong></li>
            <li className="font-medium">AI will process and respond with voice</li>
            <li className="font-medium">Continue the conversation naturally</li>
          </ol>
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>💡 Tip:</strong> Speak naturally and pause between sentences. 
              The AI needs 2 seconds of silence to know you're done speaking.
            </p>
          </div>
        </div>
        
        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          🏆 Breaking Barriers UK 2026 | Powered by AWS & Amazon Bedrock Nova Sonic 2
        </div>
      </div>
    </div>
  );
}
