'use client';

// AI Therapy Platform - Main Page
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Navbar } from '@/components/layout/Navbar';
import { LoginForm } from '@/components/auth/LoginForm';
import { SignUpForm } from '@/components/auth/SignUpForm';
import { DemoLogin } from '@/components/auth/DemoLogin';
import { SessionInterface } from '@/components/client/SessionInterface';
import { TherapistDashboard } from '@/components/therapist/TherapistDashboard';
import { AdminDashboard } from '@/components/admin/AdminDashboard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Heart, Shield, Globe, Zap, TestTube, Mail, Phone, MapPin } from 'lucide-react';
import type { User } from '@/types';

export default function Home() {
  const { isAuthenticated, loading, user } = useAuth();
  const [authMode, setAuthMode] = useState<'login' | 'signup' | 'demo'>('login');
  const [demoUser, setDemoUser] = useState<User | null>(null);
  
  // Refs for smooth scrolling
  const homeRef = useRef<HTMLDivElement>(null);
  const servicesRef = useRef<HTMLDivElement>(null);
  const aboutRef = useRef<HTMLDivElement>(null);
  const contactRef = useRef<HTMLDivElement>(null);
  const authRef = useRef<HTMLDivElement>(null);

  const handleNavigation = (section: string) => {
    const refs: { [key: string]: React.RefObject<HTMLDivElement | null> } = {
      home: homeRef,
      services: servicesRef,
      about: aboutRef,
      contact: contactRef,
    };
    
    refs[section]?.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Demo login handler
  const handleDemoLogin = (role: 'client' | 'therapist' | 'admin') => {
    const mockUser: User = {
      userId: `demo_${role}_${Date.now()}`,
      email: `demo-${role}@example.com`,
      role,
      profile: {
        firstName: 'Demo',
        lastName: role === 'client' ? 'Client' : role === 'therapist' ? 'Therapist' : 'Admin',
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
    setDemoUser(mockUser);
  };

  const handleDemoLogout = () => {
    setDemoUser(null);
    setAuthMode('login');
  };

  // Use demo user if available, otherwise use real auth
  const currentUser = demoUser || user;
  const isUserAuthenticated = isAuthenticated || !!demoUser;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading AI Therapy Platform...</p>
        </div>
      </div>
    );
  }

  if (!isUserAuthenticated) {
    return (
      <div className="min-h-screen bg-white">
        {/* Navigation */}
        <Navbar onNavigate={handleNavigation} />

        {/* Hero Section */}
        <section ref={homeRef} id="home" className="bg-gradient-to-br from-purple-50 to-blue-50 py-20">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Kick start your healing journey with{' '}
              <span className="text-purple-600">AI-Powered Therapy</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Discover how UKind Therapy is empowering survivors with innovative AI therapy, 
              featuring cutting-edge real-time audio communication for faster, purpose-driven healing.
            </p>
            <div className="flex justify-center space-x-4 mb-12">
              <Button
                size="lg"
                className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 text-lg"
                onClick={() => {
                  setAuthMode('signup');
                  authRef.current?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                Start Your Journey
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="border-purple-600 text-purple-600 hover:bg-purple-50 px-8 py-4 text-lg"
                onClick={() => {
                  setAuthMode('demo');
                  authRef.current?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                Try Demo
              </Button>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section ref={servicesRef} id="services" className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Experience a new approach to healing
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                With our evidence-based AI methods, experience results up to 40% faster than traditional therapy
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Zap className="h-8 w-8 text-purple-600" />
                  </div>
                  <CardTitle className="text-xl text-gray-900">Real-Time Audio</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    Natural voice conversations with AI therapist using Amazon Nova Sonic 2 for ultra-low latency healing sessions.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Shield className="h-8 w-8 text-green-600" />
                  </div>
                  <CardTitle className="text-xl text-gray-900">Created for survivors</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    Built around real needs with end-to-end encryption, GDPR compliance, and professional oversight.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Globe className="h-8 w-8 text-blue-600" />
                  </div>
                  <CardTitle className="text-xl text-gray-900">Accessible for all</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    Multiple languages with automatic detection and culturally sensitive responses for everyone.
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Heart className="h-8 w-8 text-orange-600" />
                  </div>
                  <CardTitle className="text-xl text-gray-900">Convenient & flexible</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    Therapy on your terms. Connect to AI therapy sessions remotely, wherever and whenever you need support.
                  </CardDescription>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* About Section */}
        <section ref={aboutRef} id="about" className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">About UKind AI Therapy</h2>
              <p className="text-xl text-gray-600 mb-8">
                UKind Therapy CIC is transforming mental health care for survivors of domestic abuse with cutting-edge AI therapy. 
                Our mission is to provide effective, accessible support for lasting recovery.
              </p>
              <div className="grid md:grid-cols-3 gap-8 mt-12">
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <div className="text-4xl mb-4">🎯</div>
                    <h3 className="font-semibold text-gray-900 mb-2">Our Mission</h3>
                    <p className="text-sm text-gray-600">
                      Empowering survivors through innovative AI therapy solutions
                    </p>
                  </CardContent>
                </Card>
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <div className="text-4xl mb-4">💡</div>
                    <h3 className="font-semibold text-gray-900 mb-2">Innovation</h3>
                    <p className="text-sm text-gray-600">
                      Leveraging AWS technology for real-time therapy sessions
                    </p>
                  </CardContent>
                </Card>
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <div className="text-4xl mb-4">❤️</div>
                    <h3 className="font-semibold text-gray-900 mb-2">Compassion</h3>
                    <p className="text-sm text-gray-600">
                      Built with survivors, for survivors, with care and empathy
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Auth Section */}
        <section ref={authRef} className="py-20 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Ready to take control of your healing journey?
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Be among the first to experience innovative AI therapy with powerful tools for recovery
              </p>
            </div>

            {/* Auth Mode Selector */}
            <div className="flex justify-center mb-8">
              <div className="bg-white rounded-lg p-2 shadow-md">
                <Button
                  variant={authMode === 'signup' ? 'default' : 'ghost'}
                  onClick={() => setAuthMode('signup')}
                  className={authMode === 'signup' ? 'bg-purple-600 text-white' : 'text-gray-600'}
                >
                  Join Now
                </Button>
                <Button
                  variant={authMode === 'login' ? 'default' : 'ghost'}
                  onClick={() => setAuthMode('login')}
                  className={authMode === 'login' ? 'bg-purple-600 text-white' : 'text-gray-600'}
                >
                  Sign In
                </Button>
                <Button
                  variant={authMode === 'demo' ? 'default' : 'ghost'}
                  onClick={() => setAuthMode('demo')}
                  className={authMode === 'demo' ? 'bg-purple-600 text-white' : 'text-gray-600'}
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  Try Demo
                </Button>
              </div>
            </div>

            {/* Auth Forms */}
            <div className="flex justify-center">
              {authMode === 'login' ? (
                <LoginForm onGoToSignUp={() => setAuthMode('signup')} />
              ) : authMode === 'signup' ? (
                <SignUpForm onBackToLogin={() => setAuthMode('login')} />
              ) : (
                <DemoLogin onDemoLogin={handleDemoLogin} />
              )}
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section ref={contactRef} id="contact" className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-4xl font-bold text-gray-900 mb-4">Get in Touch</h2>
                <p className="text-xl text-gray-600">
                  Have questions? We're here to help you on your healing journey
                </p>
              </div>
              
              <div className="grid md:grid-cols-3 gap-8">
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <Mail className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                    <h3 className="font-semibold text-gray-900 mb-2">Email</h3>
                    <p className="text-sm text-gray-600">support@ukindtherapy.io</p>
                  </CardContent>
                </Card>
                
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <Phone className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                    <h3 className="font-semibold text-gray-900 mb-2">Phone</h3>
                    <p className="text-sm text-gray-600">Available 24/7</p>
                  </CardContent>
                </Card>
                
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <MapPin className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                    <h3 className="font-semibold text-gray-900 mb-2">Location</h3>
                    <p className="text-sm text-gray-600">United Kingdom</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12">
          <div className="container mx-auto px-4 text-center">
            <div className="flex items-center justify-center mb-6">
              <Heart className="h-6 w-6 text-purple-400 mr-2" />
              <span className="text-xl font-semibold">UKind AI Therapy</span>
            </div>
            <p className="text-gray-400 mb-4">
              Powered by AWS • Built for UKind Therapy Charity • Breaking Barriers UK 2026
            </p>
            <div className="text-sm text-gray-500">
              <p>Using: API Gateway WebSockets • Lambda • DynamoDB • Cognito • AgentCore • Nova Sonic 2</p>
              <p className="mt-2">Empowering survivors through innovative AI therapy solutions</p>
            </div>
          </div>
        </footer>
      </div>
    );
  }

  // Authenticated user - show appropriate interface based on role
  return (
    <div className="min-h-screen bg-white">
      <Navbar onNavigate={handleNavigation} />
      
      {demoUser && (
        <div className="bg-purple-100 border-b border-purple-200 py-2">
          <div className="container mx-auto px-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Badge variant="secondary" className="bg-purple-600 text-white">
                Demo Mode
              </Badge>
              <span className="text-sm text-purple-900">
                You're testing the platform as {currentUser?.role}
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDemoLogout}
              className="text-purple-900 hover:text-purple-700"
            >
              Exit Demo
            </Button>
          </div>
        </div>
      )}

      <main className="bg-gray-50 min-h-screen">
        {currentUser?.role === 'client' && <SessionInterface />}
        
        {currentUser?.role === 'therapist' && <TherapistDashboard />}
        
        {currentUser?.role === 'admin' && <AdminDashboard />}
      </main>
    </div>
  );
}