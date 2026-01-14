// WebSocket service for real-time audio communication
// 🏆 Breaking Barriers UK 2026 compliant - API Gateway WebSocket integration

import { getWebSocketUrl } from '@/config/aws-config';
import type { WebSocketMessage, AudioMessage, TextMessage, ControlMessage } from '@/types';

export type WebSocketEventType = 'connect' | 'disconnect' | 'message' | 'error' | 'audio' | 'text' | 'control';

export interface WebSocketEventHandler {
  (data?: any): void;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private eventHandlers: Map<WebSocketEventType, WebSocketEventHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private isConnecting = false;
  private sessionId: string | null = null;

  constructor() {
    // Initialize event handler arrays
    this.eventHandlers.set('connect', []);
    this.eventHandlers.set('disconnect', []);
    this.eventHandlers.set('message', []);
    this.eventHandlers.set('error', []);
    this.eventHandlers.set('audio', []);
    this.eventHandlers.set('text', []);
    this.eventHandlers.set('control', []);
  }

  /**
   * Connect to WebSocket server
   */
  async connect(token?: string): Promise<boolean> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connecting or connected');
      return true;
    }

    this.isConnecting = true;

    try {
      const wsUrl = getWebSocketUrl();
      const urlWithAuth = token ? `${wsUrl}?token=${encodeURIComponent(token)}` : wsUrl;
      
      console.log('Attempting WebSocket connection to:', wsUrl);
      console.log('Full URL:', urlWithAuth);
      
      this.ws = new WebSocket(urlWithAuth);

      return new Promise((resolve, reject) => {
        if (!this.ws) {
          reject(new Error('Failed to create WebSocket'));
          return;
        }

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected successfully');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          this.emit('connect');
          resolve(true);
        };

        this.ws.onclose = (event) => {
          console.log('❌ WebSocket disconnected:', event.code, event.reason);
          
          // If we were still connecting, reject the promise
          if (this.isConnecting) {
            this.isConnecting = false;
            reject(new Error(`Connection closed during handshake: ${event.code} ${event.reason}`));
            return;
          }
          
          this.isConnecting = false;
          this.emit('disconnect', { code: event.code, reason: event.reason });
          
          // Attempt reconnection if not a normal closure
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect(token);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.isConnecting = false;
          this.emit('error', error);
          reject(error);
        };

        this.ws.onmessage = (event) => {
          console.log('📨 WebSocket message received:', event.data);
          this.handleMessage(event);
        };

        // Timeout for connection
        setTimeout(() => {
          if (this.isConnecting) {
            console.error('⏱️ WebSocket connection timeout after 10 seconds');
            this.isConnecting = false;
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);
      });
    } catch (error) {
      this.isConnecting = false;
      console.error('WebSocket connection error:', error);
      return false;
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.sessionId = null;
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Send message through WebSocket
   */
  send(message: WebSocketMessage): boolean {
    if (!this.isConnected()) {
      console.error('WebSocket not connected');
      return false;
    }

    try {
      this.ws!.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
      return false;
    }
  }

  /**
   * Send audio data
   */
  sendAudio(audioData: ArrayBuffer, format: 'webm' | 'wav' | 'mp3' = 'webm', sampleRate: number = 44100): boolean {
    const message: AudioMessage = {
      type: 'audio',
      payload: {
        audioData,
        format,
        sampleRate,
      },
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId || undefined,
    };

    return this.send(message);
  }

  /**
   * Send text message
   */
  sendText(text: string, language?: string): boolean {
    const message: TextMessage = {
      type: 'text',
      payload: {
        text,
        language,
        isFromAI: false,
      },
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId || undefined,
    };

    return this.send(message);
  }

  /**
   * Send control message
   */
  sendControl(action: 'start_session' | 'end_session' | 'pause' | 'resume', sessionId?: string): boolean {
    const message: ControlMessage = {
      type: 'control',
      payload: {
        action,
        sessionId,
      },
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId || sessionId,
    };

    if (action === 'start_session' && sessionId) {
      this.sessionId = sessionId;
    } else if (action === 'end_session') {
      this.sessionId = null;
    }

    return this.send(message);
  }

  /**
   * Add event listener
   */
  on(event: WebSocketEventType, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(event) || [];
    handlers.push(handler);
    this.eventHandlers.set(event, handlers);
  }

  /**
   * Remove event listener
   */
  off(event: WebSocketEventType, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(event) || [];
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
    }
  }

  /**
   * Emit event to all listeners
   */
  private emit(event: WebSocketEventType, data?: any): void {
    const handlers = this.eventHandlers.get(event) || [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error(`Error in WebSocket event handler for ${event}:`, error);
      }
    });
  }

  /**
   * Handle incoming WebSocket message
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Emit general message event
      this.emit('message', message);
      
      // Emit specific event based on message type
      switch (message.type) {
        case 'audio':
          this.emit('audio', message as AudioMessage);
          break;
        case 'text':
          this.emit('text', message as TextMessage);
          break;
        case 'control':
          this.emit('control', message as ControlMessage);
          break;
        case 'error':
          this.emit('error', message.payload);
          break;
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
      this.emit('error', { message: 'Failed to parse message', error });
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(token?: string): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${this.reconnectDelay}ms`);

    setTimeout(() => {
      this.connect(token).catch(error => {
        console.error('Reconnection failed:', error);
        // Exponential backoff
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000); // Max 30 seconds
      });
    }, this.reconnectDelay);
  }
}

// Singleton instance
export const webSocketService = new WebSocketService();