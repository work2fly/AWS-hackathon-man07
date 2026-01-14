// Audio service for real-time audio processing
// 🏆 Breaking Barriers UK 2026 compliant

import type { AudioConfig, AudioStream } from '@/types';

export interface AudioEventHandler {
  (data: any): void;
}

export class AudioService {
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private isRecording = false;
  private isPlaying = false;
  private eventHandlers: Map<string, AudioEventHandler[]> = new Map();
  
  private config: AudioConfig = {
    sampleRate: 44100,
    channels: 1, // Mono for therapy sessions
    bitDepth: 16,
    bufferSize: 4096,
  };

  constructor(config?: Partial<AudioConfig>) {
    if (config) {
      this.config = { ...this.config, ...config };
    }
    
    // Initialize event handler arrays
    this.eventHandlers.set('audioData', []);
    this.eventHandlers.set('volumeLevel', []);
    this.eventHandlers.set('error', []);
    this.eventHandlers.set('recordingStart', []);
    this.eventHandlers.set('recordingStop', []);
  }

  /**
   * Initialize audio context and get microphone access
   */
  async initialize(): Promise<boolean> {
    try {
      // Request microphone access
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channels,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      // Create audio context
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: this.config.sampleRate,
      });

      // Create analyser for volume monitoring
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      
      const source = this.audioContext.createMediaStreamSource(this.mediaStream);
      source.connect(this.analyser);

      // Start volume monitoring
      this.startVolumeMonitoring();

      console.log('Audio service initialized successfully');
      return true;
    } catch (error) {
      console.error('Failed to initialize audio service:', error);
      this.emit('error', { message: 'Failed to initialize audio', error });
      return false;
    }
  }

  /**
   * Start recording audio
   */
  async startRecording(): Promise<boolean> {
    if (!this.mediaStream) {
      console.error('Audio not initialized');
      return false;
    }

    if (this.isRecording) {
      console.warn('Already recording');
      return true;
    }

    try {
      // Create MediaRecorder with WebM format for better compression
      const options: MediaRecorderOptions = {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 64000, // 64kbps for good quality with low bandwidth
      };

      // Fallback to other formats if WebM not supported
      if (!MediaRecorder.isTypeSupported(options.mimeType!)) {
        options.mimeType = 'audio/wav';
      }

      this.mediaRecorder = new MediaRecorder(this.mediaStream, options);
      
      // Handle audio data chunks
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          // Convert blob to ArrayBuffer for WebSocket transmission
          event.data.arrayBuffer().then(arrayBuffer => {
            this.emit('audioData', {
              data: arrayBuffer,
              format: options.mimeType?.includes('webm') ? 'webm' : 'wav',
              timestamp: Date.now(),
            });
          });
        }
      };

      this.mediaRecorder.onstart = () => {
        this.isRecording = true;
        this.emit('recordingStart');
        console.log('Recording started');
      };

      this.mediaRecorder.onstop = () => {
        this.isRecording = false;
        this.emit('recordingStop');
        console.log('Recording stopped');
      };

      this.mediaRecorder.onerror = (error) => {
        console.error('MediaRecorder error:', error);
        this.emit('error', { message: 'Recording error', error });
      };

      // Start recording with small time slices for real-time streaming
      this.mediaRecorder.start(100); // 100ms chunks for low latency
      
      return true;
    } catch (error) {
      console.error('Failed to start recording:', error);
      this.emit('error', { message: 'Failed to start recording', error });
      return false;
    }
  }

  /**
   * Stop recording audio
   */
  stopRecording(): void {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
    }
  }

  /**
   * Play audio from ArrayBuffer
   */
  async playAudio(audioData: ArrayBuffer, format: string = 'webm'): Promise<boolean> {
    if (!this.audioContext) {
      console.error('Audio context not initialized');
      return false;
    }

    try {
      this.isPlaying = true;
      
      // Create blob from ArrayBuffer
      const blob = new Blob([audioData], { type: `audio/${format}` });
      const audioUrl = URL.createObjectURL(blob);
      
      // Create audio element for playback
      const audio = new Audio(audioUrl);
      audio.volume = 0.8; // Comfortable volume level
      
      // Handle playback events
      audio.onended = () => {
        this.isPlaying = false;
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = (error) => {
        this.isPlaying = false;
        URL.revokeObjectURL(audioUrl);
        console.error('Audio playback error:', error);
        this.emit('error', { message: 'Audio playback failed', error });
      };

      await audio.play();
      return true;
    } catch (error) {
      this.isPlaying = false;
      console.error('Failed to play audio:', error);
      this.emit('error', { message: 'Failed to play audio', error });
      return false;
    }
  }

  /**
   * Get current volume level (0-100)
   */
  getVolumeLevel(): number {
    if (!this.analyser) return 0;

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);

    // Calculate RMS (Root Mean Square) for volume level
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i] * dataArray[i];
    }
    
    const rms = Math.sqrt(sum / bufferLength);
    return Math.min(100, (rms / 255) * 100);
  }

  /**
   * Start monitoring volume levels
   */
  private startVolumeMonitoring(): void {
    const updateVolume = () => {
      if (this.analyser) {
        const volume = this.getVolumeLevel();
        this.emit('volumeLevel', volume);
      }
      
      // Continue monitoring if audio context is running
      if (this.audioContext && this.audioContext.state === 'running') {
        requestAnimationFrame(updateVolume);
      }
    };
    
    updateVolume();
  }

  /**
   * Get current audio stream state
   */
  getStreamState(): AudioStream {
    return {
      stream: this.mediaStream,
      recorder: this.mediaRecorder,
      isRecording: this.isRecording,
      isPlaying: this.isPlaying,
    };
  }

  /**
   * Check if microphone is available
   */
  static async checkMicrophoneAvailability(): Promise<boolean> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.some(device => device.kind === 'audioinput');
    } catch {
      return false;
    }
  }

  /**
   * Request microphone permissions
   */
  static async requestMicrophonePermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop()); // Stop immediately after permission check
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Add event listener
   */
  on(event: string, handler: AudioEventHandler): void {
    const handlers = this.eventHandlers.get(event) || [];
    handlers.push(handler);
    this.eventHandlers.set(event, handlers);
  }

  /**
   * Remove event listener
   */
  off(event: string, handler: AudioEventHandler): void {
    const handlers = this.eventHandlers.get(event) || [];
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
    }
  }

  /**
   * Emit event to all listeners
   */
  private emit(event: string, data?: any): void {
    const handlers = this.eventHandlers.get(event) || [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error(`Error in audio event handler for ${event}:`, error);
      }
    });
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    this.stopRecording();
    
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.mediaRecorder = null;
    this.analyser = null;
    this.isRecording = false;
    this.isPlaying = false;
  }
}

// Singleton instance
export const audioService = new AudioService();