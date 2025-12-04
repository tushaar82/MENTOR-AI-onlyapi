"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BookOpen, Clock, Award, PlayCircle, CheckCircle, Lock } from 'lucide-react';

interface Module {
  id: string;
  title: string;
  description: string;
  duration: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: string;
  isLocked: boolean;
  progress: number;
  isCompleted: boolean;
  topics: string[];
}

interface LearningPath {
  id: string;
  title: string;
  description: string;
  modules: string[];
  estimatedTime: string;
  progress: number;
}

interface ParentTrainingAcademyProps {
  parentId: string;
  childId: string;
  subscriptionTier: 'basic' | 'standard' | 'premium_plus';
}

export default function ParentTrainingAcademy({ 
  parentId, 
  childId, 
  subscriptionTier 
}: ParentTrainingAcademyProps) {
  const [modules, setModules] = useState<Module[]>([]);
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('modules');

  useEffect(() => {
    fetchTrainingData();
  }, [parentId, subscriptionTier]);

  const fetchTrainingData = async () => {
    try {
      setLoading(true);
      
      // Fetch modules
      const modulesResponse = await fetch(`/api/parent/training/modules?parent_id=${parentId}`);
      if (modulesResponse.ok) {
        const modulesData = await modulesResponse.json();
        setModules(modulesData.modules || []);
      }

      // Fetch learning paths
      const pathsResponse = await fetch(`/api/parent/training/learning-paths?parent_id=${parentId}&child_id=${childId}`);
      if (pathsResponse.ok) {
        const pathsData = await pathsResponse.json();
        setLearningPaths(pathsData.learning_paths || []);
      }
    } catch (error) {
      console.error('Error fetching training data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startModule = async (moduleId: string) => {
    try {
      const response = await fetch('/api/parent/training/start-module', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_id: parentId,
          module_id: moduleId,
          child_id: childId
        })
      });

      if (response.ok) {
        // Update module progress
        setModules(prev => prev.map(module => 
          module.id === moduleId 
            ? { ...module, progress: 0, isLocked: false }
            : module
        ));
      }
    } catch (error) {
      console.error('Error starting module:', error);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const canAccessFeature = (feature: string) => {
    const featureAccess = {
      basic: ['basic_modules'],
      standard: ['basic_modules', 'intermediate_modules', 'learning_paths'],
      premium_plus: ['basic_modules', 'intermediate_modules', 'advanced_modules', 'learning_paths', 'personalized_paths']
    };
    
    return featureAccess[subscriptionTier]?.includes(feature) || false;
  };

  const filteredModules = selectedCategory === 'all' 
    ? modules 
    : modules.filter(module => module.category === selectedCategory);

  const categories = ['all', ...new Set(modules.map(module => module.category))];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Parent Training Academy</h1>
          <p className="text-gray-600 mt-2">
            Enhance your teaching skills with our expert-designed modules
          </p>
        </div>
        
        {subscriptionTier === 'basic' && (
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4">
              <p className="text-sm text-blue-800">
                Upgrade to Standard or Premium Plus for access to more modules and personalized learning paths
              </p>
              <Button className="mt-2 bg-blue-600 hover:bg-blue-700">
                Upgrade Plan
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="modules">Training Modules</TabsTrigger>
          <TabsTrigger value="paths">Learning Paths</TabsTrigger>
        </TabsList>

        <TabsContent value="modules" className="space-y-6">
          {/* Category Filter */}
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <Button
                key={category}
                variant={selectedCategory === category ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category)}
                className="capitalize"
              >
                {category.replace('_', ' ')}
              </Button>
            ))}
          </div>

          {/* Modules Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredModules.map(module => (
              <Card key={module.id} className="relative">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{module.title}</CardTitle>
                      <CardDescription className="mt-2">
                        {module.description}
                      </CardDescription>
                    </div>
                    {module.isLocked && (
                      <Lock className="h-5 w-5 text-gray-400" />
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 mt-3">
                    <Badge className={getDifficultyColor(module.difficulty)}>
                      {module.difficulty}
                    </Badge>
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {module.duration}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Topics */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-700 mb-2">Topics Covered:</h4>
                    <div className="flex flex-wrap gap-1">
                      {module.topics.slice(0, 3).map((topic, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {topic}
                        </Badge>
                      ))}
                      {module.topics.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{module.topics.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Progress */}
                  {module.progress > 0 && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Progress</span>
                        <span className="text-sm text-gray-600">{module.progress}%</span>
                      </div>
                      <Progress value={module.progress} className="h-2" />
                    </div>
                  )}

                  {/* Action Button */}
                  <Button 
                    className="w-full"
                    disabled={module.isLocked || (!canAccessFeature('intermediate_modules') && module.difficulty !== 'beginner')}
                    onClick={() => startModule(module.id)}
                  >
                    {module.isCompleted ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Review Module
                      </>
                    ) : module.progress > 0 ? (
                      <>
                        <PlayCircle className="h-4 w-4 mr-2" />
                        Continue
                      </>
                    ) : (
                      <>
                        <BookOpen className="h-4 w-4 mr-2" />
                        {module.isLocked ? 'Locked' : 'Start Module'}
                      </>
                    )}
                  </Button>

                  {/* Upgrade Prompt */}
                  {module.isLocked && !canAccessFeature('intermediate_modules') && (
                    <p className="text-xs text-orange-600 mt-2 text-center">
                      Upgrade to Standard to access this module
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Empty State */}
          {filteredModules.length === 0 && (
            <Card>
              <CardContent className="text-center py-12">
                <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No modules found
                </h3>
                <p className="text-gray-600">
                  Try selecting a different category or upgrade your plan for more content.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="paths" className="space-y-6">
          {/* Learning Paths */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {learningPaths.map(path => (
              <Card key={path.id}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5 text-yellow-600" />
                    {path.title}
                  </CardTitle>
                  <CardDescription>
                    {path.description}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      {path.modules.length} modules
                    </span>
                    <span className="text-gray-600">
                      <Clock className="h-4 w-4 inline mr-1" />
                      {path.estimatedTime}
                    </span>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Path Progress</span>
                      <span className="text-sm text-gray-600">{path.progress}%</span>
                    </div>
                    <Progress value={path.progress} className="h-2" />
                  </div>

                  <Button 
                    className="w-full"
                    disabled={!canAccessFeature('learning_paths')}
                  >
                    {canAccessFeature('learning_paths') ? (
                      <>
                        <PlayCircle className="h-4 w-4 mr-2" />
                        Continue Path
                      </>
                    ) : (
                      <>
                        <Lock className="h-4 w-4 mr-2" />
                        Upgrade to Access
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Empty State */}
          {learningPaths.length === 0 && (
            <Card>
              <CardContent className="text-center py-12">
                <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No learning paths available
                </h3>
                <p className="text-gray-600">
                  {canAccessFeature('learning_paths') 
                    ? 'Complete some modules to generate personalized learning paths.'
                    : 'Upgrade to Standard or Premium Plus to access personalized learning paths.'
                  }
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}