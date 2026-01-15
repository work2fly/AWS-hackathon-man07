// Speech recognition hook using Web Speech API
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useEffect, useCallback, useRef } from 'react';

export interface SpeechRecognitionState {
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  isSupported: boolean;
  error: string | null;
}

export function useSpeechRecognition() {
  const [state, setState] = useState<SpeechRecognitionState>({
    isListening: false,
    transcript: '',
    interimTranscript: '',
    isSupported: false,
    error: null,
  });

  const recognitionRef = useRef<any>(null);
  const onTranscriptRef = useRef<((transcript: string) => void) | null>(null);

  // Check if Web Speech API is supported
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const isSupported = !!SpeechRecognition;
    
    setState(prev => ({ ...prev, isSupported }));

    if (isSupported && !recognitionRef.current) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
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

        setState(prev => ({
          ...prev,
          transcript: prev.transcript + finalTranscript,
          interimTranscript,
        }));

        // Call callback with final transcript
        if (finalTranscript && onTranscriptRef.current) {
          onTranscriptRef.current(finalTranscript.trim());
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setState(prev => ({
          ...prev,
          isListening: false,
          error: `Speech recognition error: ${event.error}`,
        }));
      };

      recognition.onend = () => {
        setState(prev => ({ ...prev, isListening: false }));
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) {
      setState(prev => ({ ...prev, error: 'Speech recognition not supported' }));
      return false;
    }

    try {
      recognitionRef.current.start();
      setState(prev => ({
        ...prev,
        isListening: true,
        error: null,
        transcript: '',
        interimTranscript: '',
      }));
      return true;
    } catch (error) {
      console.error('Failed to start speech recognition:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to start listening',
      }));
      return false;
    }
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setState(prev => ({ ...prev, isListening: false }));
    }
  }, []);

  const resetTranscript = useCallback(() => {
    setState(prev => ({
      ...prev,
      transcript: '',
      interimTranscript: '',
    }));
  }, []);

  const setOnTranscript = useCallback((callback: (transcript: string) => void) => {
    onTranscriptRef.current = callback;
  }, []);

  return {
    ...state,
    startListening,
    stopListening,
    resetTranscript,
    setOnTranscript,
  };
}
