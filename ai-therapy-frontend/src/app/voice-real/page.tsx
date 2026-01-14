'use client';

/**
 * REAL Voice-to-Voice with Web Speech API
 * 🏆 Breaking Barriers UK 2026 compliant
 * Uses browser's Speech Recognition + Claude + Speech Synthesis
 * FASTEST & MOST RELIABLE SOLUTION!
 */

import { useState, useRef, useEffect } from 'react';

// Extend Window interface for webkitSpeechRecognition
declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }
}

export default function VoiceRealPage() {
  const [status, setStatus] = useState('Ready');
  const [messages, setMessages] = useState<string[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [transcript, setTranscript] = useState('');
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  
  const recognitionRef = useRef<any>(null);

  const API_URL = 'https://xi8ekw0fj6.execute-api.us-west-2.amazonaws.com/dev';

  const addMessage = (msg: string) => {
    setMessages(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
    console.log(msg);
  };

  // Initialize voices when component mounts
  useEffect(() => {
    const loadVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      
      if (voices.length > 0 && !selectedVoice) {
        // Priority list for most natural voices
        const preferredVoices = [
          'Samantha',           // macOS - Very natural female
          'Karen',              // macOS - Natural female
          'Moira',              // macOS - Irish female
          'Tessa',              // macOS - South African female
          'Google US English Female',  // Chrome - Natural
          'Microsoft Zira Desktop - English (United States)', // Windows - Natural
          'Google UK English Female',
          'Microsoft David Desktop - English (United States)'
        ];
        
        // Find the best available voice
        let bestVoice = voices.find(voice => 
          preferredVoices.some(pv => voice.name === pv)
        );
        
        // Fallback: any high-quality English female voice
        if (!bestVoice) {
          bestVoice = voices.find(voice => 
            voice.lang.startsWith('en') && 
            voice.name.toLowerCase().includes('female')
          );
        }
        
        // Fallback: any English voice
        if (!bestVoice) {
          bestVoice = voices.find(voice => voice.lang.startsWith('en'));
        }
        
        if (bestVoice) {
          setSelectedVoice(bestVoice);
          addMessage(`🎤 Selected voice: ${bestVoice.name} (${bestVoice.lang})`);
        }
      }
    };
    
    // Load voices immediately
    loadVoices();
    
    // Also load when voices change (some browsers load async)
    if (window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, []);

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
            addMessage(`📝 You said: ${finalTranscript.trim()}`);
            processText(finalTranscript.trim());
          } else if (interimTranscript) {
            setStatus(`🎤 Listening: "${interimTranscript}"`);
          }
        };
        
        recognitionRef.current.onerror = (event: any) => {
          addMessage(`❌ Recognition error: ${event.error}`);
          setIsListening(false);
          setStatus('❌ Error');
        };
        
        recognitionRef.current.onend = () => {
          setIsListening(false);
          if (status.includes('Listening')) {
            setStatus('✅ Ready');
          }
        };
      } else {
        addMessage('❌ Speech Recognition not supported in this browser');
        setStatus('❌ Not Supported');
      }
    }
  }, []);

  // Process text with Claude
  const processText = async (text: string) => {
    try {
      addMessage('📤 Sending to AI...');
      setStatus('🤖 AI Processing...');
      
      const response = await fetch(`${API_URL}/process-audio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId: sessionId,
          audioData: btoa(text), // Send text as base64
          format: 'text',
          sampleRate: 16000,
          userText: text // Direct text input
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 100)}`);
      }
      
      const result = await response.json();
      addMessage('✅ AI response received');
      
      // Display AI text response
      if (result.text) {
        addMessage(`💬 AI: ${result.text}`);
        
        // Use Web Speech API for text-to-speech
        if ('speechSynthesis' in window) {
          await speakText(result.text);
        }
      }
      
      setStatus('✅ Ready');
      
    } catch (error) {
      addMessage(`❌ Processing error: ${error}`);
      setStatus('❌ Error');
    }
  };

  // Speak text using Web Speech API (Consistent Natural Voice)
  const speakText = async (text: string) => {
    return new Promise<void>((resolve, reject) => {
      try {
        addMessage('🔊 Speaking response...');
        setStatus('🔊 Speaking...');
        
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Use the selected voice (consistent throughout session)
        if (selectedVoice) {
          utterance.voice = selectedVoice;
        } else {
          // Fallback if voice not loaded yet
          const voices = window.speechSynthesis.getVoices();
          const fallbackVoice = voices.find(voice => 
            voice.name === 'Samantha' || 
            voice.name === 'Karen' ||
            voice.name.includes('Google US English Female')
          );
          if (fallbackVoice) {
            utterance.voice = fallbackVoice;
            setSelectedVoice(fallbackVoice);
          }
        }
        
        // Natural speech settings
        utterance.lang = 'en-US';
        utterance.rate = 0.92;      // Slightly slower for warmth
        utterance.pitch = 1.05;     // Slightly higher for friendliness
        utterance.volume = 1.0;
        
        utterance.onend = () => {
          addMessage('✅ Speech finished');
          setStatus('✅ Ready - Click "Start Talking" to continue');
          resolve();
        };
        
        utterance.onerror = (error) => {
          addMessage(`❌ Speech error: ${error}`);
          setStatus('❌ Speech Error');
          reject(error);
        };
        
        // Small delay to ensure everything is ready
        setTimeout(() => {
          window.speechSynthesis.speak(utterance);
        }, 100);
      } catch (error) {
        addMessage(`❌ TTS error: ${error}`);
        setStatus('❌ Error');
        reject(error);
      }
    });
  };

  // Start listening
  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        setStatus('🎤 Listening...');
        addMessage('🎤 Started listening - speak now!');
      } catch (error) {
        addMessage(`❌ Error starting recognition: ${error}`);
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
    }
  };

  // Start session
  const startSession = () => {
    const newSessionId = `session_${Date.now()}`;
    setSessionId(newSessionId);
    addMessage(`🚀 Session started: ${newSessionId}`);
    setStatus('✅ Ready - Click "Start Talking" to speak');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-purple-900">
          🎤 Ally Voice Therapy (REAL)
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Fastest & Most Reliable Voice-to-Voice AI
        </p>
        
        {/* Status */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="text-center">
            <div className="text-3xl font-bold mb-2">{status}</div>
            <div className="text-sm text-gray-600">
              {sessionId ? `Session: ${sessionId.slice(-8)}` : 'No active session'}
            </div>
            {selectedVoice && (
              <div className="mt-2 text-sm text-purple-600 font-medium">
                🎤 Voice: {selectedVoice.name}
              </div>
            )}
            {transcript && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <div className="text-sm text-gray-600">Current transcript:</div>
                <div className="text-lg font-medium text-blue-900">{transcript}</div>
              </div>
            )}
          </div>
        </div>
        
        {/* Controls */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-center space-x-4 mb-6">
            {!sessionId ? (
              <button
                onClick={startSession}
                className="px-12 py-6 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl font-bold text-xl hover:from-green-600 hover:to-green-700 shadow-lg transform transition hover:scale-105"
              >
                🚀 Start Session
              </button>
            ) : (
              <>
                <button
                  onClick={startListening}
                  disabled={isListening}
                  className="px-12 py-6 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-bold text-xl hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed shadow-lg transform transition hover:scale-105"
                >
                  🎤 Start Talking
                </button>
                
                <button
                  onClick={stopListening}
                  disabled={!isListening}
                  className="px-12 py-6 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-bold text-xl hover:from-red-600 hover:to-red-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed shadow-lg transform transition hover:scale-105"
                >
                  🛑 Stop
                </button>
              </>
            )}
          </div>
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
            <li className="font-medium">Click <strong>"Start Session"</strong></li>
            <li className="font-medium">Click <strong>"Start Talking"</strong> and speak clearly</li>
            <li className="font-medium">Your words appear as you speak</li>
            <li className="font-medium">AI processes and responds automatically</li>
            <li className="font-medium">Listen to the natural voice response</li>
          </ol>
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">
              <strong>✨ FASTEST SOLUTION:</strong> Uses browser's built-in speech recognition - no delays!
            </p>
          </div>
        </div>
        
        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          🏆 Breaking Barriers UK 2026 | Powered by Web Speech API + Claude 3.5 Sonnet
        </div>
      </div>
    </div>
  );
}
