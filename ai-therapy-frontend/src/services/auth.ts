// Authentication service using AWS Cognito
// 🏆 Breaking Barriers UK 2026 compliant

import { Amplify } from 'aws-amplify';
// import { signIn, signUp, signOut, getCurrentUser, confirmSignUp, resendSignUpCode } from 'aws-amplify/auth';
import { awsConfig } from '@/config/aws-config';
import type { User } from '@/types';
import { MockAuthService } from './mock-auth';

// TEMPORARY: Use mock auth until backend team fixes Cognito client secret issue
const USE_MOCK_AUTH = false;

// Configure Amplify with Cognito settings (ready for when backend is fixed)
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: awsConfig.cognito.userPoolId,
      userPoolClientId: awsConfig.cognito.userPoolWebClientId,
      loginWith: {
        email: true,
      },
      signUpVerificationMethod: 'code',
      userAttributes: {
        email: {
          required: true,
        },
        given_name: {
          required: true,
        },
        family_name: {
          required: true,
        },
        // 'custom:role': {
        //   required: true,
        // },
      },
      passwordFormat: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireNumbers: true,
        requireSpecialCharacters: true,
      },
    },
  },
}, {
  ssr: false // Disable SSR for client-side only
});

export interface SignUpParams {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: 'client' | 'therapist' | 'admin';
}

export interface SignInParams {
  email: string;
  password: string;
}

export class AuthService {
  /**
   * Sign up a new user
   */
  static async signUp({ email, password, firstName, lastName, role }: SignUpParams) {
    if (USE_MOCK_AUTH) {
      return MockAuthService.signUp({ email, password, firstName, lastName, role });
    }

    // REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
    /*
    try {
      const { isSignUpComplete, userId, nextStep } = await signUp({
        username: email,
        password,
        options: {
          userAttributes: {
            email,
            given_name: firstName,
            family_name: lastName,
            'custom:role': role,
          },
        },
      });

      return {
        success: true,
        userId,
        isSignUpComplete,
        nextStep,
      };
    } catch (error) {
      console.error('Sign up error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Sign up failed',
      };
    }
    */
    
    return {
      success: false,
      error: 'Real Cognito integration not available yet',
    };
  }

  /**
   * Confirm sign up with verification code
   */
  static async confirmSignUp(email: string, confirmationCode: string) {
    if (USE_MOCK_AUTH) {
      return MockAuthService.confirmSignUp(email, confirmationCode);
    }

    // REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
    /*
    try {
      const { isSignUpComplete, nextStep } = await confirmSignUp({
        username: email,
        confirmationCode,
      });

      return {
        success: true,
        isSignUpComplete,
        nextStep,
      };
    } catch (error) {
      console.error('Confirm sign up error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Confirmation failed',
      };
    }
    */
    
    return {
      success: false,
      error: 'Real Cognito integration not available yet',
    };
  }

  /**
   * Resend confirmation code
   */
  static async resendConfirmationCode(email: string) {
    if (USE_MOCK_AUTH) {
      return MockAuthService.resendConfirmationCode(email);
    }

    // REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
    /*
    try {
      await resendSignUpCode({ username: email });
      return { success: true };
    } catch (error) {
      console.error('Resend confirmation code error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Resend failed',
      };
    }
    */
    
    return {
      success: false,
      error: 'Real Cognito integration not available yet',
    };
  }

  /**
   * Sign in user
   */
  static async signIn({ email, password }: SignInParams) {
    if (USE_MOCK_AUTH) {
      const result = await MockAuthService.signIn({ email, password });
      
      // Store user in session if sign in successful
      if (result.success && result.user) {
        MockAuthService.setCurrentUser(result.user);
      }
      
      return result;
    }

    // REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
    /*
    try {
      const { isSignedIn, nextStep } = await signIn({
        username: email,
        password,
      });

      if (isSignedIn) {
        const user = await this.getCurrentUser();
        return {
          success: true,
          user,
          isSignedIn,
        };
      }

      return {
        success: true,
        isSignedIn,
        nextStep,
      };
    } catch (error) {
      console.error('Sign in error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Sign in failed',
      };
    }
    */
    
    return {
      success: false,
      error: 'Real Cognito integration not available yet',
    };
  }

  /**
   * Sign out user
   */
  static async signOut() {
    if (USE_MOCK_AUTH) {
      MockAuthService.setCurrentUser(null);
      return MockAuthService.signOut();
    }

    // REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
    /*
    try {
      await signOut();
      return { success: true };
    } catch (error) {
      console.error('Sign out error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Sign out failed',
      };
    }
    */
    
    return {
      success: false,
      error: 'Real Cognito integration not available yet',
    };
  }

  /**
   * Get current authenticated user
   */
  static async getCurrentUser(): Promise<User | null> {
    if (USE_MOCK_AUTH) {
      return MockAuthService.getCurrentUser();
    }

    // REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
    /*
    try {
      const { username, userId, signInDetails } = await getCurrentUser();
      
      // Get user attributes from Cognito
      const userAttributes = signInDetails?.loginId ? {
        email: signInDetails.loginId,
        // Note: In a real implementation, you'd fetch full user profile from your API
        // For hackathon, we'll use mock data structure
      } : null;

      if (!userAttributes) return null;

      // Mock user object - in production, fetch from your API
      const user: User = {
        userId: userId || username,
        email: userAttributes.email,
        role: 'client', // This would come from custom attributes or your API
        profile: {
          firstName: '[firstName]', // Placeholder for compliance
          lastName: '[lastName]',   // Placeholder for compliance
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

      return user;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
    */
    
    return null;
  }

  /**
   * Check if user is authenticated
   */
  static async isAuthenticated(): Promise<boolean> {
    if (USE_MOCK_AUTH) {
      return MockAuthService.isAuthenticated();
    }

    // REAL COGNITO CODE (COMMENTED OUT - BACKEND TEAM NEEDS TO FIX CLIENT SECRET ISSUE)
    /*
    try {
      await getCurrentUser();
      return true;
    } catch {
      return false;
    }
    */
    
    return false;
  }
}