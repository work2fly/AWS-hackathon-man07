'use client';

// Demo login for testing without backend
// 🏆 Breaking Barriers UK 2026 compliant

import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { User, UserCheck, Shield } from 'lucide-react';

interface DemoLoginProps {
  onDemoLogin: (role: 'client' | 'therapist' | 'admin') => void;
}

export function DemoLogin({ onDemoLogin }: DemoLoginProps) {
  const { t } = useLanguage();
  const [selectedRole, setSelectedRole] = useState<'client' | 'therapist' | 'admin'>('client');

  const roles = [
    {
      id: 'client' as const,
      title: t('demo.roles.client.title'),
      description: t('demo.roles.client.description'),
      icon: User,
      color: 'text-blue-500',
    },
    {
      id: 'therapist' as const,
      title: t('demo.roles.therapist.title'),
      description: t('demo.roles.therapist.description'),
      icon: UserCheck,
      color: 'text-green-500',
    },
    {
      id: 'admin' as const,
      title: t('demo.roles.admin.title'),
      description: t('demo.roles.admin.description'),
      icon: Shield,
      color: 'text-purple-500',
    },
  ];

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">{t('demo.title')}</CardTitle>
        <CardDescription className="text-center">
          {t('demo.subtitle')}
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
          {t('demo.enterAs')} {roles.find(r => r.id === selectedRole)?.title}
        </Button>

        <div className="text-center text-xs text-muted-foreground">
          <p>{t('demo.info1')}</p>
          <p>{t('demo.info2')}</p>
        </div>
      </CardContent>
    </Card>
  );
}