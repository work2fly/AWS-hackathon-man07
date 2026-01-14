'use client';

// Demo login for testing without backend
// 🏆 Breaking Barriers UK 2026 compliant

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { User, UserCheck, Shield } from 'lucide-react';

interface DemoLoginProps {
  onDemoLogin: (role: 'client' | 'therapist' | 'admin') => void;
}

export function DemoLogin({ onDemoLogin }: DemoLoginProps) {
  const [selectedRole, setSelectedRole] = useState<'client' | 'therapist' | 'admin'>('client');

  const roles = [
    {
      id: 'client' as const,
      title: 'Demo Client',
      description: 'Experience the therapy session interface',
      icon: User,
      color: 'text-blue-500',
    },
    {
      id: 'therapist' as const,
      title: 'Demo Therapist',
      description: 'View therapist dashboard and monitoring',
      icon: UserCheck,
      color: 'text-green-500',
    },
    {
      id: 'admin' as const,
      title: 'Demo Admin',
      description: 'Access system management panel',
      icon: Shield,
      color: 'text-purple-500',
    },
  ];

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">Demo Mode</CardTitle>
        <CardDescription className="text-center">
          Test the platform without backend connection
        </CardDescription>
        <Badge variant="secondary" className="mx-auto">
          🏆 Breaking Barriers UK 2026 - Demo
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          {roles.map((role) => {
            const Icon = role.icon;
            return (
              <div
                key={role.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedRole === role.id
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                }`}
                onClick={() => setSelectedRole(role.id)}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`h-5 w-5 ${role.color}`} />
                  <div className="flex-1">
                    <h3 className="font-medium">{role.title}</h3>
                    <p className="text-sm text-muted-foreground">{role.description}</p>
                  </div>
                  <div className={`w-4 h-4 rounded-full border-2 ${
                    selectedRole === role.id
                      ? 'border-primary bg-primary'
                      : 'border-muted-foreground'
                  }`} />
                </div>
              </div>
            );
          })}
        </div>

        <Button
          onClick={() => onDemoLogin(selectedRole)}
          className="w-full"
          size="lg"
        >
          Enter Demo as {roles.find(r => r.id === selectedRole)?.title}
        </Button>

        <div className="text-center text-xs text-muted-foreground">
          <p>Demo mode simulates authentication without AWS Cognito</p>
          <p>Perfect for testing UI and functionality</p>
        </div>
      </CardContent>
    </Card>
  );
}