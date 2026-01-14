// API service for backend integration
// 🏆 Breaking Barriers UK 2026 compliant

import { getApiUrl } from '@/config/aws-config';
import type { User, TherapySession, RedFlag, Notification } from '@/types';

export class ApiService {
  private static async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<{ success: boolean; data?: T; error?: string }> {
    try {
      const url = getApiUrl(endpoint);
      
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Request failed',
      };
    }
  }

  // User management
  static async getUserProfile(userId: string): Promise<{ success: boolean; data?: User; error?: string }> {
    return this.makeRequest<User>(`/users/${userId}`);
  }

  static async updateUserProfile(userId: string, profile: Partial<User>): Promise<{ success: boolean; error?: string }> {
    return this.makeRequest(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  }

  // Session management
  static async createSession(clientId: string): Promise<{ success: boolean; data?: TherapySession; error?: string }> {
    return this.makeRequest<TherapySession>('/sessions', {
      method: 'POST',
      body: JSON.stringify({ clientId }),
    });
  }

  static async getSession(sessionId: string): Promise<{ success: boolean; data?: TherapySession; error?: string }> {
    return this.makeRequest<TherapySession>(`/sessions/${sessionId}`);
  }

  static async endSession(sessionId: string): Promise<{ success: boolean; error?: string }> {
    return this.makeRequest(`/sessions/${sessionId}/end`, {
      method: 'POST',
    });
  }

  static async getUserSessions(userId: string): Promise<{ success: boolean; data?: TherapySession[]; error?: string }> {
    return this.makeRequest<TherapySession[]>(`/users/${userId}/sessions`);
  }

  // Red flags and notifications
  static async getRedFlags(therapistId: string): Promise<{ success: boolean; data?: RedFlag[]; error?: string }> {
    return this.makeRequest<RedFlag[]>(`/therapists/${therapistId}/red-flags`);
  }

  static async acknowledgeRedFlag(flagId: string): Promise<{ success: boolean; error?: string }> {
    return this.makeRequest(`/red-flags/${flagId}/acknowledge`, {
      method: 'POST',
    });
  }

  static async resolveRedFlag(flagId: string, resolvedBy: string): Promise<{ success: boolean; error?: string }> {
    return this.makeRequest(`/red-flags/${flagId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolvedBy }),
    });
  }

  static async getNotifications(userId: string): Promise<{ success: boolean; data?: Notification[]; error?: string }> {
    return this.makeRequest<Notification[]>(`/users/${userId}/notifications`);
  }

  static async markNotificationRead(notificationId: string): Promise<{ success: boolean; error?: string }> {
    return this.makeRequest(`/notifications/${notificationId}/read`, {
      method: 'POST',
    });
  }

  // Admin endpoints
  static async getAdminStats(): Promise<{ success: boolean; data?: any; error?: string }> {
    return this.makeRequest('/admin/stats');
  }

  static async getAllUsers(): Promise<{ success: boolean; data?: User[]; error?: string }> {
    return this.makeRequest<User[]>('/admin/users');
  }

  static async getAllSessions(): Promise<{ success: boolean; data?: TherapySession[]; error?: string }> {
    return this.makeRequest<TherapySession[]>('/admin/sessions');
  }

  static async getAllRedFlags(): Promise<{ success: boolean; data?: RedFlag[]; error?: string }> {
    return this.makeRequest<RedFlag[]>('/admin/red-flags');
  }

  // Health check
  static async healthCheck(): Promise<{ success: boolean; data?: { status: string; timestamp: string }; error?: string }> {
    return this.makeRequest<{ status: string; timestamp: string }>('/health');
  }
}