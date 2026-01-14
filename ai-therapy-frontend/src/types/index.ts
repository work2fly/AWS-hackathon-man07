// Type definitions for AI Therapy Platform

export interface User {
  userId: string;
  email: string;
  role: 'client' | 'therapist' | 'admin';
  profile: UserProfile;
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
  mfaEnabled: boolean;
  languagePreference: string;
}

export interface UserProfile {
  firstName: string;
  lastName: string;
  timezone: string;
  phoneNumber?: string;
  emergencyContact?: EmergencyContact;
}

export interface UserPreferences {
  language: string;
  voiceSettings: VoiceSettings;
  notificationSettings: NotificationSettings;
  privacySettings: PrivacySettings;
}

export interface EmergencyContact {
  name: string;
  phone: string;
  relationship: string;
}

export interface VoiceSettings {
  preferredVoice: string;
  speechRate: number;
  volume: number;
}

export interface NotificationSettings {
  email: boolean;
  sms: boolean;
  push: boolean;
  redFlags: boolean;
}

export interface PrivacySettings {
  shareProgressWithTherapist: boolean;
  allowRecording: boolean;
  dataRetentionDays: number;
}

export interface TherapySession {
  sessionId: string;
  timestamp: string;
  clientId: string;
  agentId: string;
  status: 'active' | 'completed' | 'terminated';
  startTime: string;
  endTime?: string;
  duration?: number;
  language: string;
  metadata: SessionMetadata;
  sentimentSummary?: SentimentSummary;
  agentMemoryId: string;
}

export interface SessionMetadata {
  audioQuality: AudioQualityMetrics;
  connectionMetrics: ConnectionMetrics;
  therapeuticMilestones: string[];
  exercisesCompleted: string[];
}

export interface AudioQualityMetrics {
  averageLatency: number;
  packetLoss: number;
  audioClarity: number;
}

export interface ConnectionMetrics {
  connectionTime: number;
  reconnections: number;
  totalUptime: number;
}

export interface SentimentSummary {
  overallSentiment: 'positive' | 'neutral' | 'negative';
  emotionalState: string[];
  progressIndicators: ProgressIndicator[];
  keyTopics: string[];
  riskLevel: 'low' | 'medium' | 'high';
  generatedAt: string;
}

export interface ProgressIndicator {
  metric: string;
  value: number;
  trend: 'improving' | 'stable' | 'declining';
  description: string;
}

export interface RedFlag {
  sessionId: string;
  flagId: string;
  type: 'self_harm' | 'suicidal_ideation' | 'abuse' | 'violence' | 'crisis';
  severity: 'low' | 'medium' | 'high' | 'critical';
  detectedAt: string;
  context: string;
  notificationsSent: NotificationRecord[];
  resolved: boolean;
  resolvedBy?: string;
  resolvedAt?: string;
}

export interface NotificationRecord {
  recipientId: string;
  method: 'email' | 'sms' | 'push' | 'in_app';
  sentAt: string;
  acknowledged: boolean;
  acknowledgedAt?: string;
}

export interface Notification {
  recipientId: string;
  timestamp: string;
  type: 'red_flag' | 'session_complete' | 'system_alert';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  title: string;
  message: string;
  relatedSessionId?: string;
  relatedFlagId?: string;
  read: boolean;
  readAt?: string;
  actionRequired: boolean;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'audio' | 'text' | 'control' | 'error';
  payload: any;
  timestamp: string;
  sessionId?: string;
}

export interface AudioMessage extends WebSocketMessage {
  type: 'audio';
  payload: {
    audioData: ArrayBuffer;
    format: 'webm' | 'wav' | 'mp3';
    sampleRate: number;
  };
}

export interface TextMessage extends WebSocketMessage {
  type: 'text';
  payload: {
    text: string;
    language?: string;
    isFromAI: boolean;
  };
}

export interface ControlMessage extends WebSocketMessage {
  type: 'control';
  payload: {
    action: 'start_session' | 'end_session' | 'pause' | 'resume';
    sessionId?: string;
  };
}

// Authentication types
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

// Audio processing types
export interface AudioConfig {
  sampleRate: number;
  channels: number;
  bitDepth: number;
  bufferSize: number;
}

export interface AudioStream {
  stream: MediaStream | null;
  recorder: MediaRecorder | null;
  isRecording: boolean;
  isPlaying: boolean;
}