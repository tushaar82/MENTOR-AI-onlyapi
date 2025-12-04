"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  LineChart, 
  PieChart, 
  Target,
  Users,
  Clock,
  Award,
  AlertTriangle,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';

interface EffectivenessMetric {
  name: string;
  value: number;
  percentile: number;
  trend: 'improving' | 'stable' | 'declining';
  status: 'excellent' | 'good' | 'average' | 'below_average' | 'poor';
}

interface CorrelationData {
  involvementMetric: string;
  outcomeMetric: string;
  correlation: number;
  strength: 'strong' | 'moderate' | 'weak' | 'very_weak';
  insights: string[];
}

interface ComparativeData {
  benchmarkType: string;
  metrics: {
    [key: string]: {
      current: number;
      benchmark: number;
      percentile: number;
    };
  };
  strengths: string[];
  improvementAreas: string[];
}

interface PredictiveInsight {
  type: string;
  timeframe: string;
  confidence: number;
  prediction: {
    value: number;
    interpretation: string;
  };
  riskLevel: 'low' | 'moderate' | 'high';
  recommendations: string[];
}

interface VisualizationData {
  chartType: 'line' | 'bar' | 'pie' | 'radar' | 'heatmap';
  title: string;
  data: any[];
  metadata: any;
}

interface AdvancedAnalyticsDashboardProps {
  parentId: string;
  childId: string;
  subscriptionTier: 'basic' | 'standard' | 'premium_plus';
}

export default function AdvancedAnalyticsDashboard({ 
  parentId, 
  childId, 
  subscriptionTier 
}: AdvancedAnalyticsDashboardProps) {
  const [effectiveness, setEffectiveness] = useState<{
    overall: number;
    percentile: number;
    trend: string;
    metrics: EffectivenessMetric[];
  } | null>(null);
  
  const [correlations, setCorrelations] = useState<CorrelationData[]>([]);
  const [comparative, setComparative] = useState<ComparativeData | null>(null);
  const [predictions, setPredictions] = useState<PredictiveInsight[]>([]);
  const [visualizations, setVisualizations] = useState<VisualizationData[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [timePeriod, setTimePeriod] = useState('monthly');

  useEffect(() => {
    fetchAnalyticsData();
  }, [parentId, childId, timePeriod]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Fetch effectiveness metrics
      const effectivenessResponse = await fetch(
        `/api/parent/analytics/effectiveness?parent_id=${parentId}&child_id=${childId}&period=${timePeriod}`
      );
      if (effectivenessResponse.ok) {
        const effectivenessData = await effectivenessResponse.json();
        setEffectiveness(effectivenessData);
      }

      // Fetch correlation analysis
      const correlationResponse = await fetch(
        `/api/parent/analytics/correlation?parent_id=${parentId}&child_id=${childId}&period=${timePeriod}`
      );
      if (correlationResponse.ok) {
        const correlationData = await correlationResponse.json();
        setCorrelations(correlationData.correlation_results || []);
      }

      // Fetch comparative analytics
      const comparativeResponse = await fetch(
        `/api/parent/analytics/comparative?parent_id=${parentId}&child_id=${childId}&period=${timePeriod}`
      );
      if (comparativeResponse.ok) {
        const comparativeData = await comparativeResponse.json();
        setComparative(comparativeData.comparative_results);
      }

      // Fetch predictive insights
      const predictionResponse = await fetch(
        `/api/parent/analytics/predictive?parent_id=${parentId}&child_id=${childId}`
      );
      if (predictionResponse.ok) {
        const predictionData = await predictionResponse.json();
        setPredictions(predictionData.predictive_results || []);
      }

      // Fetch visualization data
      const vizResponse = await fetch(
        `/api/parent/analytics/visualizations?parent_id=${parentId}&child_id=${childId}`
      );
      if (vizResponse.ok) {
        const vizData = await vizResponse.json();
        setVisualizations(vizData.visualization_data || []);
      }
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'declining': return <TrendingDown className="h-4 w-4 text-red-600" />;
      default: return <Minus className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'bg-green-100 text-green-800';
      case 'good': return 'bg-blue-100 text-blue-800';
      case 'average': return 'bg-yellow-100 text-yellow-800';
      case 'below_average': return 'bg-orange-100 text-orange-800';
      case 'poor': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCorrelationColor = (correlation: number) => {
    const abs = Math.abs(correlation);
    if (abs >= 0.7) return 'text-green-600';
    if (abs >= 0.5) return 'text-blue-600';
    if (abs >= 0.3) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const canAccessFeature = (feature: string) => {
    const featureAccess = {
      basic: ['basic_analytics'],
      standard: ['basic_analytics', 'correlation_analysis', 'comparative_analytics'],
      premium_plus: ['basic_analytics', 'correlation_analysis', 'comparative_analytics', 'predictive_insights', 'advanced_visualizations']
    };
    
    return featureAccess[subscriptionTier]?.includes(feature) || false;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Comprehensive insights into your parenting effectiveness and child's progress
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <select
            value={timePeriod}
            onChange={(e) => setTimePeriod(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="weekly">Last Week</option>
            <option value="monthly">Last Month</option>
            <option value="quarterly">Last Quarter</option>
            <option value="yearly">Last Year</option>
          </select>
        </div>
      </div>

      {/* Upgrade Prompt */}
      {subscriptionTier !== 'premium_plus' && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-blue-900">Upgrade to Premium Plus</h3>
                <p className="text-sm text-blue-800 mt-1">
                  Get predictive insights, advanced visualizations, and comprehensive analytics
                </p>
              </div>
              <Button className="bg-blue-600 hover:bg-blue-700">
                Upgrade Now
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="effectiveness">Effectiveness</TabsTrigger>
          <TabsTrigger value="correlations">Correlations</TabsTrigger>
          <TabsTrigger value="comparative">Comparative</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Overall Effectiveness</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {effectiveness ? `${(effectiveness.overall * 100).toFixed(1)}%` : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {effectiveness ? `${effectiveness.percentile}th percentile` : ''}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Strongest Correlation</CardTitle>
                <BarChart3 className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {correlations.length > 0 ? correlations[0].strength : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {correlations.length > 0 ? `${Math.abs(correlations[0].correlation).toFixed(2)} correlation` : ''}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Benchmark Ranking</CardTitle>
                <Users className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {comparative ? comparative.metrics?.overall?.percentile ? `${comparative.metrics.overall.percentile}th` : 'N/A' : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">
                  Among similar parents
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Risk Level</CardTitle>
                <AlertTriangle className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {predictions.length > 0 ? predictions[0].riskLevel : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">
                  Based on predictive analysis
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Insights */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Key Strengths</CardTitle>
                <CardDescription>Areas where you're excelling</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {comparative?.strengths?.slice(0, 3).map((strength, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm">{strength}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Improvement Areas</CardTitle>
                <CardDescription>Focus areas for growth</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {comparative?.improvementAreas?.slice(0, 3).map((area, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-orange-600" />
                      <span className="text-sm">{area}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="effectiveness" className="space-y-6">
          {effectiveness && (
            <>
              {/* Overall Score */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5 text-yellow-600" />
                    Overall Effectiveness Score
                  </CardTitle>
                  <CardDescription>
                    Your comprehensive parenting effectiveness rating
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-3xl font-bold">
                        {(effectiveness.overall * 100).toFixed(1)}%
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        {getTrendIcon(effectiveness.trend)}
                        <span className="text-sm text-gray-600 capitalize">
                          {effectiveness.trend}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">
                        {effectiveness.percentile}th
                      </div>
                      <div className="text-sm text-gray-600">percentile</div>
                    </div>
                  </div>
                  <Progress value={effectiveness.overall * 100} className="h-3" />
                </CardContent>
              </Card>

              {/* Individual Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {effectiveness.metrics.map((metric, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <CardTitle className="text-lg">{metric.name}</CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(metric.status)}>
                          {metric.status.replace('_', ' ')}
                        </Badge>
                        {getTrendIcon(metric.trend)}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-2xl font-bold">
                          {(metric.value * 100).toFixed(1)}%
                        </span>
                        <div className="text-right">
                          <div className="text-lg font-bold text-blue-600">
                            {metric.percentile}th
                          </div>
                          <div className="text-sm text-gray-600">percentile</div>
                        </div>
                      </div>
                      <Progress value={metric.value * 100} className="h-2" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </TabsContent>

        <TabsContent value="correlations" className="space-y-6">
          {!canAccessFeature('correlation_analysis') ? (
            <Card>
              <CardContent className="text-center py-12">
                <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Correlation Analysis
                </h3>
                <p className="text-gray-600 mb-4">
                  Upgrade to Standard or Premium Plus to access correlation analysis
                </p>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  Upgrade Plan
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {correlations.map((correlation, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>
                        {correlation.involvementMetric} → {correlation.outcomeMetric}
                      </span>
                      <Badge className={getCorrelationColor(correlation.correlation)}>
                        {correlation.strength}
                      </Badge>
                    </CardTitle>
                    <CardDescription>
                      Correlation coefficient: {correlation.correlation.toFixed(3)}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">Strength:</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${getCorrelationColor(correlation.correlation)}`}
                          style={{ width: `${Math.abs(correlation.correlation) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">
                        {Math.abs(correlation.correlation).toFixed(2)}
                      </span>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm mb-2">Key Insights:</h4>
                      <ul className="space-y-1">
                        {correlation.insights.map((insight, insightIndex) => (
                          <li key={insightIndex} className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-blue-600">•</span>
                            {insight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="comparative" className="space-y-6">
          {!canAccessFeature('comparative_analytics') ? (
            <Card>
              <CardContent className="text-center py-12">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Comparative Analytics
                </h3>
                <p className="text-gray-600 mb-4">
                  Upgrade to Standard or Premium Plus to access comparative analytics
                </p>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  Upgrade Plan
                </Button>
              </CardContent>
            </Card>
          ) : comparative && (
            <div className="space-y-6">
              {Object.entries(comparative).map(([benchmarkType, data]: [string, any]) => (
                <Card key={benchmarkType}>
                  <CardHeader>
                    <CardTitle className="capitalize">
                      {benchmarkType.replace('_', ' ')} Benchmark
                    </CardTitle>
                    <CardDescription>
                      How you compare to {benchmarkType.replace('_', ' ')} peers
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-sm mb-3">Strengths</h4>
                        <div className="space-y-2">
                          {(data.strengths as string[]).map((strength: string, index: number) => (
                            <div key={index} className="flex items-center gap-2">
                              <ArrowUp className="h-4 w-4 text-green-600" />
                              <span className="text-sm">{strength}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium text-sm mb-3">Improvement Areas</h4>
                        <div className="space-y-2">
                          {(data.improvementAreas as string[]).map((area: string, index: number) => (
                            <div key={index} className="flex items-center gap-2">
                              <Target className="h-4 w-4 text-orange-600" />
                              <span className="text-sm">{area}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="predictions" className="space-y-6">
          {!canAccessFeature('predictive_insights') ? (
            <Card>
              <CardContent className="text-center py-12">
                <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Predictive Insights
                </h3>
                <p className="text-gray-600 mb-4">
                  Upgrade to Premium Plus to access predictive analytics
                </p>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  Upgrade Plan
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {predictions.map((prediction, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="capitalize">{prediction.type} Prediction</span>
                      <Badge className={getRiskColor(prediction.riskLevel)}>
                        {prediction.riskLevel} risk
                      </Badge>
                    </CardTitle>
                    <CardDescription>
                      {prediction.timeframe} forecast with {prediction.confidence}% confidence
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm mb-2">Predicted Outcome:</h4>
                      <div className="text-lg font-bold text-blue-600">
                        {prediction.prediction.interpretation}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm mb-2">Recommendations:</h4>
                      <ul className="space-y-1">
                        {prediction.recommendations.map((rec, recIndex) => (
                          <li key={recIndex} className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-blue-600">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}