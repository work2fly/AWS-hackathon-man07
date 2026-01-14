// Authentication hook
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useEffect, useCallback } from 'react';
import { AuthService, SignUpParams, SignInParams } from '@/services/auth';
import type { User, AuthState } from '@/types';

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    loading: true,
    error: null,
  });

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = useCallback(async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const isAuthenticated = await AuthService.isAuthenticated();
      
      if (isAuthenticated) {
        const user = await AuthService.getCurrentUser();
        setAuthState({
          isAuthenticated: true,
          user,
          token: null, // Token is managed by Amplify internally
          loading: false,
          error: null,
        });
      } else {
        setAuthState({
          isAuthenticated: false,
          user: null,
          token: null,
          loading: false,
          error: null,
        });
      }
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        user: null,
        token: null,
        loading: false,
        error: error instanceof Error ? error.message : 'Authentication check failed',
      });
    }
  }, []);

  const signUp = useCallback(async (params: SignUpParams) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await AuthService.signUp(params);
      
      if (result.success) {
        setAuthState(prev => ({ ...prev, loading: false }));
        return result;
      } else {
        setAuthState(prev => ({ 
          ...prev, 
          loading: false, 
          error: result.error || 'Sign up failed' 
        }));
        return result;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign up failed';
      setAuthState(prev => ({ ...prev, loading: false, error: errorMessage }));
      return { success: false, error: errorMessage };
    }
  }, []);

  const confirmSignUp = useCallback(async (email: string, confirmationCode: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await AuthService.confirmSignUp(email, confirmationCode);
      
      if (result.success) {
        setAuthState(prev => ({ ...prev, loading: false }));
        return result;
      } else {
        setAuthState(prev => ({ 
          ...prev, 
          loading: false, 
          error: result.error || 'Confirmation failed' 
        }));
        return result;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Confirmation failed';
      setAuthState(prev => ({ ...prev, loading: false, error: errorMessage }));
      return { success: false, error: errorMessage };
    }
  }, []);

  const resendConfirmationCode = useCallback(async (email: string) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await AuthService.resendConfirmationCode(email);
      
      setAuthState(prev => ({ 
        ...prev, 
        loading: false, 
        error: result.success ? null : (result.error || 'Resend failed')
      }));
      
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Resend failed';
      setAuthState(prev => ({ ...prev, loading: false, error: errorMessage }));
      return { success: false, error: errorMessage };
    }
  }, []);

  const signIn = useCallback(async (params: SignInParams) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await AuthService.signIn(params);
      
      if (result.success && 'isSignedIn' in result && result.isSignedIn && result.user) {
        setAuthState({
          isAuthenticated: true,
          user: result.user,
          token: null, // Managed by Amplify
          loading: false,
          error: null,
        });
        return result;
      } else if (result.success && 'nextStep' in result && result.nextStep) {
        // Handle MFA or other next steps
        setAuthState(prev => ({ ...prev, loading: false }));
        return result;
      } else {
        setAuthState(prev => ({ 
          ...prev, 
          loading: false, 
          error: ('error' in result ? result.error : 'Sign in failed') || null
        }));
        return result;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign in failed';
      setAuthState(prev => ({ ...prev, loading: false, error: errorMessage }));
      return { success: false, error: errorMessage };
    }
  }, []);

  const signOut = useCallback(async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await AuthService.signOut();
      
      if (result.success) {
        setAuthState({
          isAuthenticated: false,
          user: null,
          token: null,
          loading: false,
          error: null,
        });
      } else {
        setAuthState(prev => ({ 
          ...prev, 
          loading: false, 
          error: result.error || 'Sign out failed' 
        }));
      }
      
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign out failed';
      setAuthState(prev => ({ ...prev, loading: false, error: errorMessage }));
      return { success: false, error: errorMessage };
    }
  }, []);

  const clearError = useCallback(() => {
    setAuthState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    // State
    ...authState,
    
    // Actions
    signUp,
    confirmSignUp,
    resendConfirmationCode,
    signIn,
    signOut,
    checkAuthStatus,
    clearError,
    
    // Computed properties
    isClient: authState.user?.role === 'client',
    isTherapist: authState.user?.role === 'therapist',
    isAdmin: authState.user?.role === 'admin',
  };
}