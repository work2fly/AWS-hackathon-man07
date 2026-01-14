'use client';

// Therapist Dashboard Component
// 🏆 Breaking Barriers UK 2026 compliant

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { ApiService } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  AlertTriangle, 
  CheckCircle,
  Clock,
  Users,
  Activity,
  TrendingUp,
  Bell,
  Eye,
  MessageCircle
} from 'lucide-react';
import type { RedFlag, TherapySession, Notification } from '@/types';

export function TherapistDashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'redflags' | 'sessions' | 'clients'>('overview');
  const [redFlags, setRedFlags] = useState<RedFlag[]>([]);
  const [sessions, setSessions] = useState<TherapySession[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  // MOCK DATA - Replace with real API calls when backend is ready
  const mockRedFlags: RedFlag[] = [
    {
      sessionId: 'session_001',
      flagId: 'flag_001',
      type: 'suicidal_ideation',
      severity: 'critical',
      detectedAt: new Date(Date.now() - 3600000).toISOString(),
      context: 'Client expressed thoughts about self-harm during session',
      notificationsSent: [
        {
          recipientId: user?.userId || '',
          method: 'email',
          sentAt: new Date(Date.now() - 3500000).toISOString(),
          acknowledged: false,
        }
      ],
      resolved: false,
    },
    {
      sessionId: 'session_002',
      flagId: 'flag_002',
      type: 'crisis',
      severity: 'high',
      detectedAt: new Date(Date.now() - 7200000).toISOString(),
      context: 'Client mentioned experiencing severe anxiety and panic attacks',
      notificationsSent: [
        {
          recipientId: user?.userId || '',
          method: 'push',
          sentAt: new Date(Date.now() - 7100000).toISOString(),
          acknowledged: true,
          acknowledgedAt: new Date(Date.now() - 7000000).toISOString(),
        }
      ],
      resolved: false,
    },
    {
      sessionId: 'session_003',
      flagId: 'flag_003',
      type: 'abuse',
      severity: 'medium',
      detectedAt: new Date(Date.now() - 86400000).toISOString(),
      context: 'Client discussed ongoing domestic situation requiring attention',
      notificationsSent: [
        {
          recipientId: user?.userId || '',
          method: 'in_app',
          sentAt: new Date(Date.now() - 86300000).toISOString(),
          acknowledged: true,
          acknowledgedAt: new Date(Date.now() - 86200000).toISOString(),
        }
      ],
      resolved: true,
      resolvedBy: user?.userId,
      resolvedAt: new Date(Date.now() - 43200000).toISOString(),
    },
  ];

  const stats = {
    activeClients: 24,
    totalSessions: 156,
    pendingRedFlags: mockRedFlags.filter(f => !f.resolved).length,
    unreadNotifications: 5,
  };

  // REAL API INTEGRATION (COMMENTED OUT - WAITING FOR BACKEND)
  /*
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch red flags
        const redFlagsResponse = await ApiService.getRedFlags(user?.userId || '');
        if (redFlagsResponse.success && redFlagsResponse.data) {
          setRedFlags(redFlagsResponse.data);
        }

        // Fetch notifications
        const notificationsResponse = await ApiService.getNotifications(user?.userId || '');
        if (notificationsResponse.success && notificationsResponse.data) {
          setNotifications(notificationsResponse.data);
        }

        // Fetch sessions (therapist's clients)
        const sessionsResponse = await ApiService.getUserSessions(user?.userId || '');
        if (sessionsResponse.success && sessionsResponse.data) {
          setSessions(sessionsResponse.data);
        }
      } catch (error) {
        console.error('Failed to fetch therapist data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchData, 30000);
    
    return () => clearInterval(interval);
  }, [user?.userId]);
  */

  // MOCK DATA LOADING (REMOVE WHEN REAL API IS READY)
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setRedFlags(mockRedFlags);
      setLoading(false);
    }, 1000);
  }, []);

  const handleAcknowledgeRedFlag = async (flagId: string) => {
    // REAL API CALL (COMMENTED OUT - WAITING FOR BACKEND)
    /*
    const result = await ApiService.acknowledgeRedFlag(flagId);
    if (result.success) {
      // Refresh red flags
      const response = await ApiService.getRedFlags(user?.userId || '');
      if (response.success && response.data) {
        setRedFlags(response.data);
      }
    }
    */
    
    // MOCK IMPLEMENTATION
    setRedFlags(prev => prev.map(flag => 
      flag.flagId === flagId 
        ? {
            ...flag,
            notificationsSent: flag.notificationsSent.map(n => ({
              ...n,
              acknowledged: true,
              acknowledgedAt: new Date().toISOString(),
            }))
          }
        : flag
    ));
  };

  const handleResolveRedFlag = async (flagId: string) => {
    // REAL API CALL (COMMENTED OUT - WAITING FOR BACKEND)
    /*
    const result = await ApiService.resolveRedFlag(flagId, user?.userId || '');
    if (result.success) {
      const response = await ApiService.getRedFlags(user?.userId || '');
      if (response.success && response.data) {
        setRedFlags(response.data);
      }
    }
    */
    
    // MOCK IMPLEMENTATION
    setRedFlags(prev => prev.map(flag => 
      flag.flagId === flagId 
        ? {
            ...flag,
            resolved: true,
            resolvedBy: user?.userId,
            resolvedAt: new Date().toISOString(),
          }
        : flag
    ));
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'suicidal_ideation': return 'Suicidal Ideation';
      case 'self_harm': return 'Self Harm';
      case 'abuse': return 'Abuse';
      case 'violence': return 'Violence';
      case 'crisis': return 'Crisis';
      default: return type;
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: TrendingUp },
    { id: 'redflags', name: 'Red Flags', icon: AlertTriangle, badge: stats.pendingRedFlags },
    { id: 'sessions', name: 'Sessions', icon: Activity },
    { id: 'clients', name: 'Clients', icon: Users },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Therapist Dashboard</h1>
            <p className="text-gray-600">Monitor client sessions and red flags</p>
          </div>
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            🏆 Professional Oversight
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
                className={`flex items-center space-x-2 pb-4 border-b-2 transition-colors relative ${
                  activeTab === tab.id
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="font-medium">{tab.name}</span>
                {tab.badge && tab.badge > 0 && (
                  <Badge variant="destructive" className="ml-2">
                    {tab.badge}
                  </Badge>
                )}
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
                    <p className="text-sm text-gray-600 mb-1">Active Clients</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.activeClients}</p>
                  </div>
                  <Users className="h-12 w-12 text-purple-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Sessions</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.totalSessions}</p>
                  </div>
                  <Activity className="h-12 w-12 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Pending Red Flags</p>
                    <p className="text-3xl font-bold text-gray-900">{stats.pendingRedFlags}</p>
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
                    <p className="text-3xl font-bold text-gray-900">{stats.unreadNotifications}</p>
                  </div>
                  <Bell className="h-12 w-12 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Red Flags */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <span>Recent Red Flags</span>
              </CardTitle>
              <CardDescription>Requires immediate attention</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                  <p className="text-gray-600 mt-4">Loading red flags...</p>
                </div>
              ) : redFlags.filter(f => !f.resolved).length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
                  <p className="text-gray-600">No pending red flags</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {redFlags.filter(f => !f.resolved).slice(0, 3).map((flag) => (
                    <Alert key={flag.flagId} className={`${getSeverityColor(flag.severity)} border`}>
                      <AlertDescription>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <Badge variant="outline" className="border-current">
                                {getTypeLabel(flag.type)}
                              </Badge>
                              <Badge variant="outline" className="border-current">
                                {flag.severity.toUpperCase()}
                              </Badge>
                              <span className="text-xs text-gray-600">
                                {formatTimeAgo(flag.detectedAt)}
                              </span>
                            </div>
                            <p className="text-sm mb-2">{flag.context}</p>
                            <p className="text-xs text-gray-600">Session: {flag.sessionId}</p>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setActiveTab('redflags')}
                            className="ml-4"
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                        </div>
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Red Flags Tab */}
      {activeTab === 'redflags' && (
        <div className="space-y-6">
          <Alert className="bg-purple-50 border-purple-200">
            <AlertTriangle className="h-4 w-4 text-purple-600" />
            <AlertDescription className="text-purple-900">
              Red flags are automatically detected during therapy sessions and require professional review.
              Please acknowledge and resolve each flag appropriately.
            </AlertDescription>
          </Alert>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading red flags...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {redFlags.map((flag) => (
                <Card key={flag.flagId} className={`border-0 shadow-lg ${flag.resolved ? 'opacity-60' : ''}`}>
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-3">
                          <Badge className={getSeverityColor(flag.severity)}>
                            {flag.severity.toUpperCase()}
                          </Badge>
                          <Badge variant="outline">
                            {getTypeLabel(flag.type)}
                          </Badge>
                          {flag.resolved && (
                            <Badge variant="secondary" className="bg-green-100 text-green-800">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Resolved
                            </Badge>
                          )}
                        </div>
                        
                        <h3 className="font-semibold text-gray-900 mb-2">
                          {getTypeLabel(flag.type)} - {flag.severity} Severity
                        </h3>
                        
                        <p className="text-gray-700 mb-3">{flag.context}</p>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Session ID:</span> {flag.sessionId}
                          </div>
                          <div>
                            <span className="font-medium">Detected:</span> {formatTimeAgo(flag.detectedAt)}
                          </div>
                          {flag.resolved && (
                            <>
                              <div>
                                <span className="font-medium">Resolved:</span> {formatTimeAgo(flag.resolvedAt!)}
                              </div>
                              <div>
                                <span className="font-medium">Resolved By:</span> {flag.resolvedBy}
                              </div>
                            </>
                          )}
                        </div>

                        {/* Notifications */}
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <p className="text-sm font-medium text-gray-700 mb-2">Notifications:</p>
                          <div className="space-y-2">
                            {flag.notificationsSent.map((notif, idx) => (
                              <div key={idx} className="flex items-center space-x-2 text-sm">
                                {notif.acknowledged ? (
                                  <CheckCircle className="h-4 w-4 text-green-600" />
                                ) : (
                                  <Clock className="h-4 w-4 text-orange-600" />
                                )}
                                <span className="text-gray-600">
                                  {notif.method.toUpperCase()} - Sent {formatTimeAgo(notif.sentAt)}
                                  {notif.acknowledged && ` - Acknowledged ${formatTimeAgo(notif.acknowledgedAt!)}`}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {!flag.resolved && (
                        <div className="flex flex-col space-y-2 ml-4">
                          {!flag.notificationsSent[0]?.acknowledged && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleAcknowledgeRedFlag(flag.flagId)}
                              className="whitespace-nowrap"
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Acknowledge
                            </Button>
                          )}
                          <Button
                            size="sm"
                            onClick={() => handleResolveRedFlag(flag.flagId)}
                            className="bg-green-600 hover:bg-green-700 text-white whitespace-nowrap"
                          >
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Mark Resolved
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Other Tabs - Placeholder */}
      {(activeTab === 'sessions' || activeTab === 'clients') && (
        <Card className="border-0 shadow-lg">
          <CardContent className="pt-8 text-center">
            <div className="max-w-md mx-auto">
              <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <MessageCircle className="h-10 w-10 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {activeTab === 'sessions' ? 'Sessions Management' : 'Clients Management'}
              </h3>
              <p className="text-gray-600 mb-6">
                This section will display detailed {activeTab} information with real-time data from DynamoDB.
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
