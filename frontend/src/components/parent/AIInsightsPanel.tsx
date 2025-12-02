/**
 * AI Insights Panel Component for Parents
 * 
 * This component displays AI-generated insights about student performance,
 * engagement, and areas needing attention. It provides actionable recommendations
 * and allows parents to track and respond to insights.
 * 
 * Author: Mentor AI Team
 * Version: 1.0.0
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { aiFeaturesAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface Insight {
  insight_id: string;
  student_id: string;
  insight_type: 'performance' | 'engagement' | 'weak_areas' | 'progress' | 'recommendation';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  data: Record<string, any>;
  action_required: boolean;
  action_taken?: string;
  status: 'new' | 'acknowledged' | 'in_progress' | 'resolved';
  created_at: string;
  resolved_at?: string;
  metadata: Record<string, any>;
}

interface Alert {
  alert_id: string;
  student_id: string;
  alert_type: 'performance_drop' | 'low_engagement' | 'missed_goals' | 'weak_performance' | 'critical_issue';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  data: Record<string, any>;
  recommended_actions: string[];
  status: 'new' | 'acknowledged' | 'in_progress' | 'resolved';
  created_at: string;
}

interface DashboardData {
  recent_insights: Insight[];
  active_alerts: Alert[];
  insights_count: number;
  alerts_count: number;
}

const AIInsightsPanel: React.FC = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<string>('');
  const [activeTab, setActiveTab] = useState('insights');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [generatingInsights, setGeneratingInsights] = useState(false);

  // Load dashboard data on component mount
  useEffect(() => {
    loadDashboardData();
  }, [selectedStudent]);

  // Load insights when filters change
  useEffect(() => {
    if (activeTab === 'insights') {
      loadInsights();
    }
  }, [selectedStudent, filterType, filterStatus, activeTab]);

  // Load alerts when alerts tab is active
  useEffect(() => {
    if (activeTab === 'alerts') {
      loadAlerts();
    }
  }, [selectedStudent, activeTab]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await aiFeaturesAPI.getDashboard(selectedStudent || undefined);
      setDashboardData(response.data);
      
      // Set initial insights and alerts from dashboard
      setInsights(response.data.recent_insights || []);
      setAlerts(response.data.active_alerts || []);
      
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError(err.response?.data?.error?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = {};
      if (selectedStudent) params.student_id = selectedStudent;
      if (filterType !== 'all') params.insight_type = filterType;
      if (filterStatus !== 'all') params.status = filterStatus;
      
      const response = await aiFeaturesAPI.getInsights(params);
      setInsights(response.data);
      
    } catch (err: any) {
      console.error('Failed to load insights:', err);
      setError(err.response?.data?.error?.message || 'Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = {};
      if (selectedStudent) params.student_id = selectedStudent;
      
      const response = await aiFeaturesAPI.getAlerts(params);
      setAlerts(response.data);
      
    } catch (err: any) {
      console.error('Failed to load alerts:', err);
      setError(err.response?.data?.error?.message || 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const generateNewInsights = async () => {
    if (!selectedStudent) {
      setError('Please select a student to generate insights');
      return;
    }

    try {
      setGeneratingInsights(true);
      setError(null);
      
      const response = await aiFeaturesAPI.generateInsights(selectedStudent);
      
      // Add new insights to the existing list
      const newInsights = response.data.insights || [];
      setInsights(prev => [...newInsights, ...prev]);
      
      // Refresh dashboard data
      await loadDashboardData();
      
    } catch (err: any) {
      console.error('Failed to generate insights:', err);
      setError(err.response?.data?.error?.message || 'Failed to generate insights');
    } finally {
      setGeneratingInsights(false);
    }
  };

  const updateInsightStatus = async (insightId: string, status: string, actionTaken?: string) => {
    try {
      await aiFeaturesAPI.updateInsightStatus(insightId, { status, action_taken: actionTaken });
      
      // Update local state
      setInsights(prev => prev.map(insight => 
        insight.insight_id === insightId 
          ? { ...insight, status: status as any, action_taken: actionTaken }
          : insight
      ));
      
      // Refresh dashboard data
      await loadDashboardData();
      
    } catch (err: any) {
      console.error('Failed to update insight status:', err);
      setError(err.response?.data?.error?.message || 'Failed to update insight status');
    }
  };

  const updateAlertStatus = async (alertId: string, status: string, resolutionNotes?: string) => {
    try {
      await aiFeaturesAPI.updateAlertStatus(alertId, { status, resolution_notes: resolutionNotes });
      
      // Update local state
      setAlerts(prev => prev.map(alert => 
        alert.alert_id === alertId 
          ? { ...alert, status: status as any }
          : alert
      ));
      
      // Refresh dashboard data
      await loadDashboardData();
      
    } catch (err: any) {
      console.error('Failed to update alert status:', err);
      setError(err.response?.data?.error?.message || 'Failed to update alert status');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'destructive';
      case 'acknowledged': return 'default';
      case 'in_progress': return 'default';
      case 'resolved': return 'secondary';
      default: return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="mb-4">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">AI Insights</h2>
          <p className="text-gray-600">AI-powered insights about your child's learning journey</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Student Selector */}
          <Select value={selectedStudent} onValueChange={setSelectedStudent}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select student" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="student1">Student 1</SelectItem>
              <SelectItem value="student2">Student 2</SelectItem>
              {/* Add more students as needed */}
            </SelectContent>
          </Select>
          
          {/* Generate Insights Button */}
          <Button 
            onClick={generateNewInsights}
            disabled={!selectedStudent || generatingInsights}
          >
            {generatingInsights ? 'Generating...' : 'Generate Insights'}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.insights_count || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{dashboardData?.alerts_count || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">New Items</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {insights.filter(i => i.status === 'new').length + alerts.filter(a => a.status === 'new').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>
        
        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          {/* Filters */}
          <div className="flex items-center space-x-4">
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="performance">Performance</SelectItem>
                <SelectItem value="engagement">Engagement</SelectItem>
                <SelectItem value="weak_areas">Weak Areas</SelectItem>
                <SelectItem value="progress">Progress</SelectItem>
                <SelectItem value="recommendation">Recommendations</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="new">New</SelectItem>
                <SelectItem value="acknowledged">Acknowledged</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* Insights List */}
          <div className="space-y-4">
            {insights.map((insight) => (
              <Card key={insight.insight_id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <CardTitle className="text-lg">{insight.title}</CardTitle>
                      <Badge variant={getSeverityColor(insight.severity)}>
                        {insight.severity}
                      </Badge>
                      <Badge variant={getStatusColor(insight.status)}>
                        {insight.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-500">
                      {formatDate(insight.created_at)}
                    </div>
                  </div>
                  <CardDescription>{insight.description}</CardDescription>
                </CardHeader>
                
                <CardContent>
                  {insight.action_required && (
                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Recommended Actions:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {insight.data.recommended_actions?.map((action: string, index: number) => (
                          <li key={index}>{action}</li>
                        )) || <li>No specific actions recommended</li>}
                      </ul>
                    </div>
                  )}
                  
                  {insight.action_taken && (
                    <div className="mb-4 p-3 bg-green-50 rounded-lg">
                      <h4 className="font-medium text-green-800 mb-1">Action Taken:</h4>
                      <p className="text-green-700 text-sm">{insight.action_taken}</p>
                    </div>
                  )}
                  
                  <div className="flex items-center space-x-2">
                    {insight.status === 'new' && (
                      <Button 
                        size="sm" 
                        onClick={() => updateInsightStatus(insight.insight_id, 'acknowledged')}
                      >
                        Acknowledge
                      </Button>
                    )}
                    
                    {insight.status === 'acknowledged' && (
                      <Button 
                        size="sm" 
                        onClick={() => updateInsightStatus(insight.insight_id, 'in_progress')}
                      >
                        Start Working
                      </Button>
                    )}
                    
                    {insight.status === 'in_progress' && (
                      <Button 
                        size="sm" 
                        onClick={() => updateInsightStatus(insight.insight_id, 'resolved', 'Completed the recommended actions')}
                      >
                        Mark Resolved
                      </Button>
                    )}
                    
                    <Badge variant="outline">{insight.insight_type}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {insights.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No insights found. Try generating new insights or adjusting filters.
              </div>
            )}
          </div>
        </TabsContent>
        
        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-4">
          {/* Alerts List */}
          <div className="space-y-4">
            {alerts.map((alert) => (
              <Card key={alert.alert_id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <CardTitle className="text-lg">{alert.title}</CardTitle>
                      <Badge variant={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                      <Badge variant={getStatusColor(alert.status)}>
                        {alert.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-500">
                      {formatDate(alert.created_at)}
                    </div>
                  </div>
                  <CardDescription>{alert.description}</CardDescription>
                </CardHeader>
                
                <CardContent>
                  <div className="mb-4">
                    <h4 className="font-medium mb-2">Recommended Actions:</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {alert.recommended_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {alert.status === 'new' && (
                      <Button 
                        size="sm" 
                        onClick={() => updateAlertStatus(alert.alert_id, 'acknowledged')}
                      >
                        Acknowledge
                      </Button>
                    )}
                    
                    {alert.status === 'acknowledged' && (
                      <Button 
                        size="sm" 
                        onClick={() => updateAlertStatus(alert.alert_id, 'in_progress')}
                      >
                        Start Working
                      </Button>
                    )}
                    
                    {alert.status === 'in_progress' && (
                      <Button 
                        size="sm" 
                        onClick={() => updateAlertStatus(alert.alert_id, 'resolved', 'Successfully addressed the alert')}
                      >
                        Mark Resolved
                      </Button>
                    )}
                    
                    <Badge variant="outline">{alert.alert_type}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {alerts.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No active alerts found.
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AIInsightsPanel;