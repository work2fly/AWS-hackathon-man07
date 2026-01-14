'use client';

// Admin Dashboard Component
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { ApiService } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  Activity, 
  AlertTriangle, 
  Bell, 
  Database,
  TrendingUp,
  Shield,
  Settings
} from 'lucide-react';

interface AdminStats {
  totalUsers: number;
  activeUsers: number;
  totalSessions: number;
  activeSessions: number;
  redFlags: number;
  notifications: number;
}

export function AdminDashboard() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'sessions' | 'redflags' | 'system'>('overview');
  const [stats, setStats] = useState<AdminStats>({
    totalUsers: 156,
    activeUsers: 42,
    totalSessions: 1247,
    activeSessions: 8,
    redFlags: 3,
    notifications: 12,
  });
  const [loading, setLoading] = useState(false);

  // REAL API INTEGRATION (COMMENTED OUT - WAITING FOR BACKEND)
  /*
  useEffect(() => {
    const fetchAdminStats = async () => {
      setLoading(true);
      try {
        // Fetch admin statistics from backend
        const response = await fetch('/api/admin/stats', {
          headers: {
            'Authorization': `Bearer ${token}`, // Get from auth context
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          setStats({
            totalUsers: data.totalUsers || 0,
            activeUsers: data.activeUsers || 0,
            totalSessions: data.totalSessions || 0,
            activeSessions: data.activeSessions || 0,
            redFlags: data.redFlags || 0,
            notifications: data.notifications || 0,
          });
        }
      } catch (error) {
        console.error('Failed to fetch admin stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAdminStats();
    
    // Refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchAdminStats, 30000);
    
    return () => clearInterval(interval);
  }, []);
  */

  // MOCK DATA (REMOVE WHEN REAL API IS READY)
  useEffect(() => {
    // Simulate loading
    setLoading(true);
    setTimeout(() => setLoading(false), 500);
  }, []);

  const tabs = [
    { id: 'overview', name: 'Overview', icon: TrendingUp },
    { id: 'users', name: 'Users', icon: Users },
    { id: 'sessions', name: 'Sessions', icon: Activity },
    { id: 'redflags', name: 'Red Flags', icon: AlertTriangle },
    { id: 'system', name: 'System', icon: Settings },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600">System management and monitoring</p>
          </div>
          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
            🏆 Breaking Barriers UK 2026
          </Badge>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-8 border-b border-gray-200">
        <div className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 pb-4 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="font-medium">{tab.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Users</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.totalUsers}</p>
                    <p className="text-sm text-green-600 mt-1">↑ 12% from last month</p>
                  </div>
                  <Users className="h-12 w-12 text-purple-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Active Sessions</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.activeSessions}</p>
                    <p className="text-sm text-blue-600 mt-1">{stats.totalSessions} total</p>
                  </div>
                  <Activity className="h-12 w-12 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Red Flags</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.redFlags}</p>
                    <p className="text-sm text-red-600 mt-1">Requires attention</p>
                  </div>
                  <AlertTriangle className="h-12 w-12 text-red-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Notifications</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.notifications}</p>
                    <p className="text-sm text-orange-600 mt-1">Pending review</p>
                  </div>
                  <Bell className="h-12 w-12 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* DynamoDB Tables */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5 text-purple-600" />
                <span>DynamoDB Tables</span>
              </CardTitle>
              <CardDescription>Backend database resources</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-purple-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">Users Table</h3>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">ai-therapy-platform-dev-users</p>
                  <p className="text-xs text-gray-500">{stats.totalUsers} records</p>
                </div>

                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">Sessions Table</h3>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">ai-therapy-platform-dev-sessions</p>
                  <p className="text-xs text-gray-500">{stats.totalSessions} records</p>
                </div>

                <div className="p-4 bg-red-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">Red Flags Table</h3>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">ai-therapy-platform-dev-redflags</p>
                  <p className="text-xs text-gray-500">{stats.redFlags} records</p>
                </div>

                <div className="p-4 bg-orange-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">Notifications Table</h3>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">ai-therapy-platform-dev-notifications</p>
                  <p className="text-xs text-gray-500">{stats.notifications} records</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Health */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-green-600" />
                <span>System Health</span>
              </CardTitle>
              <CardDescription>AWS services status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">API Gateway (REST)</span>
                  </div>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">Operational</Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">API Gateway (WebSocket)</span>
                  </div>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">Operational</Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">Cognito User Pool</span>
                  </div>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">Operational</Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">DynamoDB Tables</span>
                  </div>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">Operational</Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">Lambda Functions</span>
                  </div>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">Operational</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Other Tabs - Placeholder */}
      {activeTab !== 'overview' && (
        <Card className="border-0 shadow-lg">
          <CardContent className="pt-8 text-center">
            <div className="max-w-md mx-auto">
              <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Database className="h-10 w-10 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {tabs.find(t => t.id === activeTab)?.name} Management
              </h3>
              <p className="text-gray-600 mb-6">
                This section will display detailed {activeTab} management interface with data from DynamoDB tables.
              </p>
              <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                Coming Soon - Backend Integration Required
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
