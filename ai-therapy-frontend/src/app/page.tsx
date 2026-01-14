'use client';

// AI Therapy Platform - Main Page
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useRef, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
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
  const { t } = useLanguage();
  const { isAuthenticated, loading, user } = useAuth();
  const [authMode, setAuthMode] = useState<'login' | 'signup' | 'demo'>('login');
  const [demoUser, setDemoUser] = useState<User | null>(null);
  
  // Refs for smooth scrolling
  const homeRef = useRef<HTMLDivElement>(null);
  const servicesRef = useRef<HTMLDivElement>(null);
  const aboutRef = useRef<HTMLDivElement>(null);
  const contactRef = useRef<HTMLDivElement>(null);
  const authRef = useRef<HTMLDivElement>(null);

  // Scroll to home when user logs out
  useEffect(() => {
    if (!isAuthenticated && !demoUser && !loading) {
      homeRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isAuthenticated, demoUser, loading]);

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

  // Force re-render when auth state changes
  const authKey = `${isAuthenticated}-${!!demoUser}-${user?.userId || 'none'}`;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  if (!isUserAuthenticated) {
    return (
      <div key={authKey} className="min-h-screen bg-white">
        {/* Navigation */}
        <Navbar onNavigate={handleNavigation} />

        {/* Hero Section */}
        <section ref={homeRef} id="home" className="bg-gradient-to-br from-purple-50 to-blue-50 py-20">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              {t('hero.title')}
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              {t('hero.subtitle')}
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
                {t('hero.cta')}
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
                {t('hero.tryDemo')}
              </Button>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section ref={servicesRef} id="services" className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                {t('features.title')}
              </h2>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Zap className="h-8 w-8 text-purple-600" />
                  </div>
                  <CardTitle className="text-xl text-gray-900">{t('features.ai.title')}</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    {t('features.ai.description')}
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Shield className="h-8 w-8 text-green-600" />
                  </div>
                  <CardTitle className="text-xl text-gray-900">{t('features.secure.title')}</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    {t('features.secure.description')}
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Globe className="h-8 w-8 text-blue-600" />
                  </div>
                  <CardTitle className="text-xl text-gray-900">{t('features.multilingual.title')}</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    {t('features.multilingual.description')}
                  </CardDescription>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Heart className="h-8 w-8 text-orange-600" />
                  </div>
                  <CardTitle className="text-xl text-gray-900">{t('features.available.title')}</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    {t('features.available.description')}
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
              <h2 className="text-4xl font-bold text-gray-900 mb-6">{t('about.title')}</h2>
              <p className="text-xl text-gray-600 mb-8">
                {t('about.description')}
              </p>
            </div>
          </div>
        </section>

        {/* Auth Section */}
        <section ref={authRef} className="py-20 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                {t('auth.section.title')}
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                {t('auth.section.subtitle')}
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
                  {t('auth.section.joinNow')}
                </Button>
                <Button
                  variant={authMode === 'login' ? 'default' : 'ghost'}
                  onClick={() => setAuthMode('login')}
                  className={authMode === 'login' ? 'bg-purple-600 text-white' : 'text-gray-600'}
                >
                  {t('auth.section.signIn')}
                </Button>
                <Button
                  variant={authMode === 'demo' ? 'default' : 'ghost'}
                  onClick={() => setAuthMode('demo')}
                  className={authMode === 'demo' ? 'bg-purple-600 text-white' : 'text-gray-600'}
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  {t('auth.section.tryDemo')}
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
                <h2 className="text-4xl font-bold text-gray-900 mb-4">{t('contact.title')}</h2>
                <p className="text-xl text-gray-600">
                  {t('contact.description')}
                </p>
              </div>
              
              <div className="grid md:grid-cols-3 gap-8">
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <Mail className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                    <h3 className="font-semibold text-gray-900 mb-2">{t('contact.email')}</h3>
                    <p className="text-sm text-gray-600">support@ally.io</p>
                  </CardContent>
                </Card>
                
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <Phone className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                    <h3 className="font-semibold text-gray-900 mb-2">{t('contact.phone')}</h3>
                    <p className="text-sm text-gray-600">{t('contact.available247')}</p>
                  </CardContent>
                </Card>
                
                <Card className="border-0 shadow-lg">
                  <CardContent className="pt-6 text-center">
                    <MapPin className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                    <h3 className="font-semibold text-gray-900 mb-2">{t('contact.location')}</h3>
                    <p className="text-sm text-gray-600">{t('contact.uk')}</p>
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
              <span className="text-xl font-semibold">Ally</span>
            </div>
            <p className="text-gray-400 mb-4">
              Powered by AWS • Built for Ally • Breaking Barriers UK 2026
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
    <div key={authKey} className="min-h-screen bg-white">
      <Navbar onNavigate={handleNavigation} />
      
      {demoUser && (
        <div className="bg-purple-100 border-b border-purple-200 py-2">
          <div className="container mx-auto px-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Badge variant="secondary" className="bg-purple-600 text-white">
                {t('demo.mode')}
              </Badge>
              <span className="text-sm text-purple-900">
                {t('demo.testing')} {currentUser?.role}
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDemoLogout}
              className="text-purple-900 hover:text-purple-700"
            >
              {t('demo.exit')}
            </Button>
          </div>
        </div>
      )}

      <main className="bg-gray-50 min-h-screen">
        {currentUser?.role === 'client' && (
          <>
            {typeof window !== 'undefined' && window.location.pathname !== '/voice-real' && (
              window.location.href = '/voice-real'
            )}
            <SessionInterface />
          </>
        )}
        
        {currentUser?.role === 'therapist' && <TherapistDashboard />}
        
        {currentUser?.role === 'admin' && <AdminDashboard />}
      </main>
    </div>
  );
}