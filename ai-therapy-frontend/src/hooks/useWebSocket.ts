// WebSocket hook for real-time communication
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useEffect, useCallback, useRef } from 'react';
import { webSocketService, WebSocketEventType } from '@/services/websocket';
import type { WebSocketMessage, AudioMessage, TextMessage, ControlMessage } from '@/types';

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: WebSocketMessage | null;
}

export function useWebSocket(token?: string) {
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastMessage: null,
  });

  const handlersRef = useRef<Map<WebSocketEventType, (data?: any) => void>>(new Map());

  // Initialize WebSocket connection
  const connect = useCallback(async (): Promise<boolean> => {
    if (state.isConnected) {
      console.log('Already connected');
      return true;
    }
    
    if (state.isConnecting) {
      console.log('Already connecting');
      return false;
    }

    setState(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      const success = await webSocketService.connect(token);
      if (success) {
        setState(prev => ({ 
          ...prev, 
          isConnected: true, 
          isConnecting: false,
          error: null 
        }));
        return true;
      } else {
        setState(prev => ({ 
          ...prev, 
          isConnecting: false,
          error: 'Failed to connect to WebSocket' 
        }));
        return false;
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isConnecting: false,
        error: error instanceof Error ? error.message : 'Connection failed' 
      }));
      return false;
    }
  }, [token, state.isConnecting, state.isConnected]);

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    webSocketService.disconnect();
    setState(prev => ({ 
      ...prev, 
      isConnected: false, 
      isConnecting: false,
      error: null 
    }));
  }, []);

  // Send audio data
  const sendAudio = useCallback((
    audioData: ArrayBuffer, 
    format: 'webm' | 'wav' | 'mp3' = 'webm', 
    sampleRate: number = 44100
  ) => {
    return webSocketService.sendAudio(audioData, format, sampleRate);
  }, []);

  // Send text message
  const sendText = useCallback((text: string, language?: string) => {
    return webSocketService.sendText(text, language);
  }, []);

  // Send control message
  const sendControl = useCallback((
    action: 'start_session' | 'end_session' | 'pause' | 'resume', 
    sessionId?: string
  ) => {
    return webSocketService.sendControl(action, sessionId);
  }, []);

  // Send generic message
  const sendMessage = useCallback((message: WebSocketMessage) => {
    return webSocketService.send(message);
  }, []);

  // Add event listener
  const addEventListener = useCallback((
    event: WebSocketEventType, 
    handler: (data?: any) => void
  ) => {
    webSocketService.on(event, handler);
    handlersRef.current.set(event, handler);
  }, []);

  // Remove event listener
  const removeEventListener = useCallback((
    event: WebSocketEventType, 
    handler: (data?: any) => void
  ) => {
    webSocketService.off(event, handler);
    handlersRef.current.delete(event);
  }, []);

  // Setup event listeners
  useEffect(() => {
    const handleConnect = () => {
      setState(prev => ({ 
        ...prev, 
        isConnected: true, 
        isConnecting: false,
        error: null 
      }));
    };

    const handleDisconnect = (data: any) => {
      setState(prev => ({ 
        ...prev, 
        isConnected: false, 
        isConnecting: false,
        error: data?.reason || 'Disconnected' 
      }));
    };

    const handleError = (error: any) => {
      setState(prev => ({ 
        ...prev, 
        isConnecting: false,
        error: error?.message || 'WebSocket error' 
      }));
    };

    const handleMessage = (message: WebSocketMessage) => {
      setState(prev => ({ ...prev, lastMessage: message }));
    };

    // Register event handlers
    webSocketService.on('connect', handleConnect);
    webSocketService.on('disconnect', handleDisconnect);
    webSocketService.on('error', handleError);
    webSocketService.on('message', handleMessage);

    // Cleanup on unmount
    return () => {
      webSocketService.off('connect', handleConnect);
      webSocketService.off('disconnect', handleDisconnect);
      webSocketService.off('error', handleError);
      webSocketService.off('message', handleMessage);
      
      // Clean up custom handlers
      handlersRef.current.forEach((handler, event) => {
        webSocketService.off(event, handler);
      });
      handlersRef.current.clear();
    };
  }, []);

  // Auto-connect when token is available
  useEffect(() => {
    if (token && !state.isConnected && !state.isConnecting) {
      connect();
    }
  }, [token, connect, state.isConnected, state.isConnecting]);

  return {
    // State
    ...state,
    
    // Connection methods
    connect,
    disconnect,
    
    // Messaging methods
    sendAudio,
    sendText,
    sendControl,
    sendMessage,
    
    // Event handling
    addEventListener,
    removeEventListener,
    
    // Utility
    isReady: state.isConnected && !state.isConnecting,
  };
}