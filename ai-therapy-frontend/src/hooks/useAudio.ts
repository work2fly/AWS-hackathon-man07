// Audio hook for microphone and playback management
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useEffect, useCallback, useRef } from 'react';
import { audioService, AudioEventHandler, AudioService } from '@/services/audio';
import type { AudioStream } from '@/types';

export interface AudioState {
  isInitialized: boolean;
  isRecording: boolean;
  isPlaying: boolean;
  volumeLevel: number;
  error: string | null;
  microphoneAvailable: boolean;
  permissionGranted: boolean;
}

export interface AudioData {
  data: ArrayBuffer;
  format: string;
  timestamp: number;
}

export function useAudio() {
  const [state, setState] = useState<AudioState>({
    isInitialized: false,
    isRecording: false,
    isPlaying: false,
    volumeLevel: 0,
    error: null,
    microphoneAvailable: false,
    permissionGranted: false,
  });

  const handlersRef = useRef<Map<string, AudioEventHandler>>(new Map());
  const onAudioDataRef = useRef<((data: AudioData) => void) | null>(null);

  // Initialize audio service
  const initialize = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, error: null }));
      
      const success = await audioService.initialize();
      
      if (success) {
        setState(prev => ({ 
          ...prev, 
          isInitialized: true,
          permissionGranted: true,
          microphoneAvailable: true,
          error: null 
        }));
        return true;
      } else {
        setState(prev => ({ 
          ...prev, 
          error: 'Failed to initialize audio service' 
        }));
        return false;
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Audio initialization failed' 
      }));
      return false;
    }
  }, []);

  // Start recording
  const startRecording = useCallback(async () => {
    if (!state.isInitialized) {
      const initialized = await initialize();
      if (!initialized) return false;
    }

    try {
      const success = await audioService.startRecording();
      if (success) {
        setState(prev => ({ ...prev, isRecording: true, error: null }));
      }
      return success;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to start recording' 
      }));
      return false;
    }
  }, [state.isInitialized, initialize]);

  // Stop recording
  const stopRecording = useCallback(() => {
    audioService.stopRecording();
    setState(prev => ({ ...prev, isRecording: false }));
  }, []);

  // Play audio
  const playAudio = useCallback(async (audioData: ArrayBuffer, format: string = 'webm') => {
    try {
      setState(prev => ({ ...prev, isPlaying: true, error: null }));
      
      const success = await audioService.playAudio(audioData, format);
      
      if (!success) {
        setState(prev => ({ 
          ...prev, 
          isPlaying: false,
          error: 'Failed to play audio' 
        }));
      }
      
      return success;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isPlaying: false,
        error: error instanceof Error ? error.message : 'Audio playback failed' 
      }));
      return false;
    }
  }, []);

  // Check microphone availability
  const checkMicrophoneAvailability = useCallback(async () => {
    const available = await AudioService.checkMicrophoneAvailability();
    setState(prev => ({ ...prev, microphoneAvailable: available }));
    return available;
  }, []);

  // Request microphone permission
  const requestMicrophonePermission = useCallback(async () => {
    const granted = await AudioService.requestMicrophonePermission();
    setState(prev => ({ ...prev, permissionGranted: granted }));
    return granted;
  }, []);

  // Set audio data callback
  const setOnAudioData = useCallback((callback: (data: AudioData) => void) => {
    onAudioDataRef.current = callback;
  }, []);

  // Get current stream state
  const getStreamState = useCallback((): AudioStream => {
    return audioService.getStreamState();
  }, []);

  // Cleanup
  const cleanup = useCallback(() => {
    audioService.cleanup();
    setState({
      isInitialized: false,
      isRecording: false,
      isPlaying: false,
      volumeLevel: 0,
      error: null,
      microphoneAvailable: false,
      permissionGranted: false,
    });
  }, []);

  // Setup event listeners
  useEffect(() => {
    const handleAudioData = (data: AudioData) => {
      if (onAudioDataRef.current) {
        onAudioDataRef.current(data);
      }
    };

    const handleVolumeLevel = (volume: number) => {
      setState(prev => ({ ...prev, volumeLevel: volume }));
    };

    const handleError = (error: any) => {
      setState(prev => ({ 
        ...prev, 
        error: error?.message || 'Audio error',
        isRecording: false,
        isPlaying: false 
      }));
    };

    const handleRecordingStart = () => {
      setState(prev => ({ ...prev, isRecording: true }));
    };

    const handleRecordingStop = () => {
      setState(prev => ({ ...prev, isRecording: false }));
    };

    // Register event handlers
    audioService.on('audioData', handleAudioData);
    audioService.on('volumeLevel', handleVolumeLevel);
    audioService.on('error', handleError);
    audioService.on('recordingStart', handleRecordingStart);
    audioService.on('recordingStop', handleRecordingStop);

    // Store handlers for cleanup
    handlersRef.current.set('audioData', handleAudioData);
    handlersRef.current.set('volumeLevel', handleVolumeLevel);
    handlersRef.current.set('error', handleError);
    handlersRef.current.set('recordingStart', handleRecordingStart);
    handlersRef.current.set('recordingStop', handleRecordingStop);

    // Cleanup on unmount
    return () => {
      handlersRef.current.forEach((handler, event) => {
        audioService.off(event, handler);
      });
      handlersRef.current.clear();
    };
  }, []);

  // Check microphone availability on mount
  useEffect(() => {
    checkMicrophoneAvailability();
  }, [checkMicrophoneAvailability]);

  return {
    // State
    ...state,
    
    // Methods
    initialize,
    startRecording,
    stopRecording,
    playAudio,
    checkMicrophoneAvailability,
    requestMicrophonePermission,
    setOnAudioData,
    getStreamState,
    cleanup,
    
    // Computed properties
    canRecord: state.isInitialized && state.permissionGranted && !state.isRecording,
    isReady: state.isInitialized && state.permissionGranted && state.microphoneAvailable,
  };
}