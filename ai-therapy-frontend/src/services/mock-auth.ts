// Mock authentication service for demo mode
// 🏆 Breaking Barriers UK 2026 compliant

import type { User } from '@/types';

export interface MockSignUpParams {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: 'client' | 'therapist' | 'admin';
}

export interface MockSignInParams {
  email: string;
  password: string;
}

// Simple in-memory storage for demo
const mockUsers = new Map<string, {
  user: User;
  password: string;
  verified: boolean;
  verificationCode?: string;
}>();

export class MockAuthService {
  /**
   * Mock sign up - stores user in memory
   */
  static async signUp({ email, password, firstName, lastName, role }: MockSignUpParams) {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check if user already exists
      if (mockUsers.has(email)) {
        return {
          success: false,
          error: 'User already exists',
        };
      }

      // Create mock user
      const user: User = {
        userId: `mock_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        email,
        role,
        profile: {
          firstName,
          lastName,
          timezone: 'UTC',
        },
        preferences: {
          language: 'en',
          voiceSettings: {
            preferredVoice: 'neural',
            speechRate: 1.0,
            volume: 0.8,
          },
          notificationSettings: {
            email: true,
            sms: false,
            push: true,
            redFlags: true,
          },
          privacySettings: {
            shareProgressWithTherapist: true,
            allowRecording: false,
            dataRetentionDays: 90,
          },
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        isActive: true,
        mfaEnabled: false,
        languagePreference: 'en',
      };

      // Generate mock verification code
      const verificationCode = Math.floor(100000 + Math.random() * 900000).toString();

      // Store user
      mockUsers.set(email, {
        user,
        password,
        verified: false,
        verificationCode,
      });

      console.log(`Mock verification code for ${email}: ${verificationCode}`);

      return {
        success: true,
        userId: user.userId,
        isSignUpComplete: false,
        nextStep: {
          signUpStep: 'CONFIRM_SIGN_UP',
          codeDeliveryDetails: {
            destination: email,
            deliveryMedium: 'EMAIL',
          },
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Sign up failed',
      };
    }
  }

  /**
   * Mock confirm sign up
   */
  static async confirmSignUp(email: string, confirmationCode: string) {
    try {
      await new Promise(resolve => setTimeout(resolve, 500));

      const userData = mockUsers.get(email);
      if (!userData) {
        return {
          success: false,
          error: 'User not found',
        };
      }

      if (userData.verificationCode !== confirmationCode) {
        return {
          success: false,
          error: 'Invalid verification code',
        };
      }

      // Mark as verified
      userData.verified = true;
      mockUsers.set(email, userData);

      return {
        success: true,
        isSignUpComplete: true,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Confirmation failed',
      };
    }
  }

  /**
   * Mock resend confirmation code
   */
  static async resendConfirmationCode(email: string) {
    try {
      await new Promise(resolve => setTimeout(resolve, 500));

      const userData = mockUsers.get(email);
      if (!userData) {
        return {
          success: false,
          error: 'User not found',
        };
      }

      // Generate new code
      const verificationCode = Math.floor(100000 + Math.random() * 900000).toString();
      userData.verificationCode = verificationCode;
      mockUsers.set(email, userData);

      console.log(`New mock verification code for ${email}: ${verificationCode}`);

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Resend failed',
      };
    }
  }

  /**
   * Mock sign in
   */
  static async signIn({ email, password }: MockSignInParams) {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      const userData = mockUsers.get(email);
      if (!userData) {
        return {
          success: false,
          error: 'User not found',
        };
      }

      if (userData.password !== password) {
        return {
          success: false,
          error: 'Invalid password',
        };
      }

      if (!userData.verified) {
        return {
          success: false,
          error: 'Please verify your email first',
        };
      }

      return {
        success: true,
        user: userData.user,
        isSignedIn: true,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Sign in failed',
      };
    }
  }

  /**
   * Mock sign out
   */
  static async signOut() {
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Sign out failed',
      };
    }
  }

  /**
   * Mock get current user (from session storage)
   */
  static async getCurrentUser(): Promise<User | null> {
    try {
      const userJson = sessionStorage.getItem('mockCurrentUser');
      if (!userJson) return null;
      
      return JSON.parse(userJson) as User;
    } catch {
      return null;
    }
  }

  /**
   * Mock set current user (to session storage)
   */
  static setCurrentUser(user: User | null): void {
    if (user) {
      sessionStorage.setItem('mockCurrentUser', JSON.stringify(user));
    } else {
      sessionStorage.removeItem('mockCurrentUser');
    }
  }

  /**
   * Mock check if authenticated
   */
  static async isAuthenticated(): Promise<boolean> {
    try {
      const user = await this.getCurrentUser();
      return !!user;
    } catch {
      return false;
    }
  }
}