'use client';

// Sign up form component
// 🏆 Breaking Barriers UK 2026 compliant

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Mail, Lock, User, ArrowLeft, Heart } from 'lucide-react';

interface SignUpFormProps {
  onBackToLogin: () => void;
}

export function SignUpForm({ onBackToLogin }: SignUpFormProps) {
  const { signUp, confirmSignUp, resendConfirmationCode, loading, error, clearError } = useAuth();
  const [step, setStep] = useState<'signup' | 'confirm'>('signup');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    role: 'client' as 'client' | 'therapist' | 'admin',
  });
  const [confirmationCode, setConfirmationCode] = useState('');

  const handleSignUpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (!formData.email || !formData.password || !formData.firstName || !formData.lastName) {
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      // Handle password mismatch
      return;
    }

    const result = await signUp({
      email: formData.email,
      password: formData.password,
      firstName: formData.firstName,
      lastName: formData.lastName,
      role: formData.role,
    });

    if (result.success) {
      setStep('confirm');
    }
  };

  const handleConfirmSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (!confirmationCode) {
      return;
    }

    const result = await confirmSignUp(formData.email, confirmationCode);
    
    if (result.success) {
      // Confirmation successful, user can now login
      onBackToLogin();
    }
  };

  const handleResendCode = async () => {
    await resendConfirmationCode(formData.email);
  };

  const handleInputChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value,
    }));
    if (error) clearError();
  };

  if (step === 'confirm') {
    return (
      <Card className="w-full max-w-md mx-auto border-0 shadow-xl">
        <CardHeader className="space-y-1 text-center pb-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Mail className="h-8 w-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">Check Your Email</CardTitle>
          <CardDescription className="text-gray-600">
            We sent a verification code to<br />
            <span className="font-medium text-gray-900">{formData.email}</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleConfirmSubmit} className="space-y-6">
            {error && (
              <Alert variant="destructive" className="border-red-200 bg-red-50">
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="confirmationCode" className="text-gray-700 font-medium">Verification Code</Label>
              <Input
                id="confirmationCode"
                type="text"
                placeholder="Enter 6-digit code"
                value={confirmationCode}
                onChange={(e) => setConfirmationCode(e.target.value)}
                maxLength={6}
                className="text-center text-2xl font-mono h-14 border-gray-200 focus:border-green-500 focus:ring-green-500"
                required
                disabled={loading}
              />
              <p className="text-sm text-gray-600 text-center">
                Check your email and enter the 6-digit code
              </p>
            </div>
            
            <Button 
              type="submit" 
              className="w-full h-12 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg" 
              disabled={loading || !confirmationCode}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Verifying...
                </>
              ) : (
                'Verify & Complete Registration'
              )}
            </Button>
            
            <div className="text-center space-y-4">
              <Button
                type="button"
                variant="ghost"
                onClick={handleResendCode}
                disabled={loading}
                className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
              >
                Didn't receive the code? Resend
              </Button>
              
              <div>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={onBackToLogin}
                  className="text-gray-600 hover:text-gray-900"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Sign In
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto border-0 shadow-xl">
      <CardHeader className="space-y-1 text-center pb-8">
        <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Heart className="h-8 w-8 text-purple-600" />
        </div>
        <CardTitle className="text-2xl font-bold text-gray-900">Join UKind AI Therapy</CardTitle>
        <CardDescription className="text-gray-600">
          Start your healing journey with innovative AI therapy
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSignUpSubmit} className="space-y-6">
          {error && (
            <Alert variant="destructive" className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="firstName" className="text-gray-700 font-medium">First Name</Label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <Input
                  id="firstName"
                  type="text"
                  placeholder="First name"
                  value={formData.firstName}
                  onChange={handleInputChange('firstName')}
                  className="pl-10 h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                  required
                  disabled={loading}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="lastName" className="text-gray-700 font-medium">Last Name</Label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <Input
                  id="lastName"
                  type="text"
                  placeholder="Last name"
                  value={formData.lastName}
                  onChange={handleInputChange('lastName')}
                  className="pl-10 h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                  required
                  disabled={loading}
                />
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="email" className="text-gray-700 font-medium">Email Address</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleInputChange('email')}
                className="pl-10 h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                required
                disabled={loading}
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="role" className="text-gray-700 font-medium">I am a...</Label>
            <select
              id="role"
              value={formData.role}
              onChange={handleInputChange('role')}
              className="w-full h-12 px-3 border border-gray-200 bg-white rounded-md text-gray-900 focus:border-purple-500 focus:ring-purple-500"
              disabled={loading}
            >
              <option value="client">Client - Seeking Therapy Support</option>
              <option value="therapist">Therapist - Mental Health Professional</option>
              <option value="admin">Admin - System Administrator</option>
            </select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password" className="text-gray-700 font-medium">Password</Label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <Input
                id="password"
                type="password"
                placeholder="Create a secure password"
                value={formData.password}
                onChange={handleInputChange('password')}
                className="pl-10 h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                required
                disabled={loading}
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-gray-700 font-medium">Confirm Password</Label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleInputChange('confirmPassword')}
                className="pl-10 h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                required
                disabled={loading}
              />
            </div>
          </div>
          
          {formData.password !== formData.confirmPassword && formData.confirmPassword && (
            <Alert variant="destructive" className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">Passwords do not match</AlertDescription>
            </Alert>
          )}
          
          <div className="bg-purple-50 rounded-lg p-4">
            <Badge variant="secondary" className="bg-purple-100 text-purple-800 w-full justify-center py-2">
              🏆 Breaking Barriers UK 2026 - Secure & Private
            </Badge>
          </div>
          
          <Button 
            type="submit" 
            className="w-full h-12 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg" 
            disabled={loading || !formData.email || !formData.password || !formData.firstName || !formData.lastName || formData.password !== formData.confirmPassword}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Creating Your Account...
              </>
            ) : (
              'Start Your Healing Journey'
            )}
          </Button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <button 
              type="button"
              className="text-purple-600 hover:text-purple-700 font-medium hover:underline"
              onClick={onBackToLogin}
            >
              Sign in here
            </button>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}