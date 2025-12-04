"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
// import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  BookOpen, 
  Users, 
  MessageSquare, 
  Target, 
  Clock,
  PlayCircle,
  Pause,
  Square,
  CheckCircle,
  Award,
  Brain,
  Lightbulb,
  Send
} from 'lucide-react';

interface StudySession {
  id: string;
  title: string;
  subject: string;
  topic: string;
  duration: number;
  status: 'planned' | 'active' | 'paused' | 'completed';
  progress: number;
  participants: {
    parent: {
      id: string;
      name: string;
    };
    child: {
      id: string;
      name: string;
    };
  };
  activities: StudyActivity[];
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
}

interface StudyActivity {
  id: string;
  type: 'teaching_prompt' | 'exercise' | 'discussion' | 'quiz';
  title: string;
  content: string;
  duration: number;
  completed: boolean;
  responses?: {
    [key: string]: any;
  };
}

interface TeachingPrompt {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  subject: string;
  topic: string;
  instructions: string[];
  materials: string[];
  estimatedTime: number;
  objectives: string[];
}

interface InteractiveExercise {
  id: string;
  title: string;
  description: string;
  type: 'collaborative' | 'guided' | 'independent';
  subject: string;
  difficulty: 'easy' | 'medium' | 'hard';
  instructions: string;
  materials: string[];
  estimatedTime: number;
  questions: Array<{
    id: string;
    text: string;
    type: 'open_ended' | 'multiple_choice' | 'true_false';
    options?: string[];
    correctAnswer?: string;
  }>;
}

interface InteractiveStudyToolsProps {
  parentId: string;
  childId: string;
  subscriptionTier: 'basic' | 'standard' | 'premium_plus';
}

export default function InteractiveStudyTools({ 
  parentId, 
  childId, 
  subscriptionTier 
}: InteractiveStudyToolsProps) {
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [prompts, setPrompts] = useState<TeachingPrompt[]>([]);
  const [exercises, setExercises] = useState<InteractiveExercise[]>([]);
  const [activeSession, setActiveSession] = useState<StudySession | null>(null);
  const [currentActivity, setCurrentActivity] = useState<StudyActivity | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('sessions');
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');

  useEffect(() => {
    fetchStudyData();
  }, [parentId, childId]);

  const fetchStudyData = async () => {
    try {
      setLoading(true);
      
      // Fetch study sessions
      const sessionsResponse = await fetch(
        `/api/parent/study-tools/sessions?parent_id=${parentId}&child_id=${childId}`
      );
      if (sessionsResponse.ok) {
        const sessionsData = await sessionsResponse.json();
        setSessions(sessionsData.sessions || []);
      }

      // Fetch teaching prompts
      const promptsResponse = await fetch(
        `/api/parent/study-tools/prompts?parent_id=${parentId}&subject=${selectedSubject}&difficulty=${selectedDifficulty}`
      );
      if (promptsResponse.ok) {
        const promptsData = await promptsResponse.json();
        setPrompts(promptsData.prompts || []);
      }

      // Fetch exercises
      const exercisesResponse = await fetch(
        `/api/parent/study-tools/exercises?parent_id=${parentId}&subject=${selectedSubject}&difficulty=${selectedDifficulty}`
      );
      if (exercisesResponse.ok) {
        const exercisesData = await exercisesResponse.json();
        setExercises(exercisesData.exercises || []);
      }
    } catch (error) {
      console.error('Error fetching study data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startStudySession = async (promptId?: string, exerciseId?: string) => {
    try {
      const response = await fetch('/api/parent/study-tools/start-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_id: parentId,
          child_id: childId,
          prompt_id: promptId,
          exercise_id: exerciseId
        })
      });

      if (response.ok) {
        const sessionData = await response.json();
        setActiveSession(sessionData.session);
        setActiveTab('active');
      }
    } catch (error) {
      console.error('Error starting study session:', error);
    }
  };

  const pauseSession = async () => {
    if (!activeSession) return;
    
    try {
      const response = await fetch('/api/parent/study-tools/pause-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: activeSession.id,
          parent_id: parentId
        })
      });

      if (response.ok) {
        setActiveSession(prev => prev ? { ...prev, status: 'paused' } : null);
      }
    } catch (error) {
      console.error('Error pausing session:', error);
    }
  };

  const resumeSession = async () => {
    if (!activeSession) return;
    
    try {
      const response = await fetch('/api/parent/study-tools/resume-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: activeSession.id,
          parent_id: parentId
        })
      });

      if (response.ok) {
        setActiveSession(prev => prev ? { ...prev, status: 'active' } : null);
      }
    } catch (error) {
      console.error('Error resuming session:', error);
    }
  };

  const completeSession = async () => {
    if (!activeSession) return;
    
    try {
      const response = await fetch('/api/parent/study-tools/complete-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: activeSession.id,
          parent_id: parentId,
          feedback: {
            rating: 0, // Would be collected from UI
            comments: ''
          }
        })
      });

      if (response.ok) {
        setActiveSession(null);
        setCurrentActivity(null);
        fetchStudyData(); // Refresh sessions list
      }
    } catch (error) {
      console.error('Error completing session:', error);
    }
  };

  const submitActivityResponse = async (activityId: string, response: any) => {
    try {
      const result = await fetch('/api/parent/study-tools/submit-activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          activity_id: activityId,
          parent_id: parentId,
          response: response
        })
      });

      if (result.ok) {
        // Update activity completion status
        if (currentActivity && currentActivity.id === activityId) {
          setCurrentActivity({ ...currentActivity, completed: true, responses: response });
        }
      }
    } catch (error) {
      console.error('Error submitting activity response:', error);
    }
  };

  const canAccessFeature = (feature: string) => {
    const featureAccess = {
      basic: ['basic_sessions'],
      standard: ['basic_sessions', 'teaching_prompts', 'basic_exercises'],
      premium_plus: ['basic_sessions', 'teaching_prompts', 'basic_exercises', 'advanced_exercises', 'real_time_collaboration']
    };
    
    return featureAccess[subscriptionTier]?.includes(feature) || false;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'teaching_prompt': return <Lightbulb className="h-4 w-4" />;
      case 'exercise': return <Target className="h-4 w-4" />;
      case 'discussion': return <MessageSquare className="h-4 w-4" />;
      case 'quiz': return <Brain className="h-4 w-4" />;
      default: return <BookOpen className="h-4 w-4" />;
    }
  };

  const subjects = ['all', 'mathematics', 'science', 'english', 'history', 'geography'];
  const difficulties = ['all', 'easy', 'medium', 'hard'];

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
          <h1 className="text-3xl font-bold text-gray-900">Interactive Study Tools</h1>
          <p className="text-gray-600 mt-2">
            Engage in collaborative learning activities with your child
          </p>
        </div>

        {subscriptionTier === 'basic' && (
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4">
              <p className="text-sm text-blue-800">
                Upgrade to Standard or Premium Plus for access to teaching prompts and interactive exercises
              </p>
              <Button className="mt-2 bg-blue-600 hover:bg-blue-700">
                Upgrade Plan
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Active Session Banner */}
      {activeSession && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <PlayCircle className="h-5 w-5 text-green-600" />
                  <span className="font-medium text-green-900">
                    Active Study Session: {activeSession.title}
                  </span>
                </div>
                <Badge className="bg-green-100 text-green-800">
                  {activeSession.status}
                </Badge>
              </div>
              
              <div className="flex gap-2">
                {activeSession.status === 'active' ? (
                  <Button size="sm" variant="outline" onClick={pauseSession}>
                    <Pause className="h-4 w-4 mr-1" />
                    Pause
                  </Button>
                ) : (
                  <Button size="sm" variant="outline" onClick={resumeSession}>
                    <PlayCircle className="h-4 w-4 mr-1" />
                    Resume
                  </Button>
                )}
                <Button size="sm" onClick={completeSession}>
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Complete
                </Button>
              </div>
            </div>
            
            {activeSession.progress > 0 && (
              <div className="mt-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Session Progress</span>
                  <span className="text-sm text-gray-600">{activeSession.progress}%</span>
                </div>
                <Progress value={activeSession.progress} className="h-2" />
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="sessions">Sessions</TabsTrigger>
          <TabsTrigger value="prompts">Teaching Prompts</TabsTrigger>
          <TabsTrigger value="exercises">Exercises</TabsTrigger>
          <TabsTrigger value="active">Active Session</TabsTrigger>
        </TabsList>

        <TabsContent value="sessions" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session) => (
              <Card key={session.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">{session.title}</CardTitle>
                  <CardDescription>
                    {session.subject} - {session.topic}
                  </CardDescription>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge className={
                      session.status === 'completed' ? 'bg-green-100 text-green-800' :
                      session.status === 'active' ? 'bg-blue-100 text-blue-800' :
                      session.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }>
                      {session.status}
                    </Badge>
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {session.duration} min
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      {session.participants.parent.name} + {session.participants.child.name}
                    </span>
                    <span className="text-gray-600">
                      {new Date(session.createdAt).toLocaleDateString()}
                    </span>
                  </div>

                  {session.progress > 0 && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Progress</span>
                        <span className="text-sm text-gray-600">{session.progress}%</span>
                      </div>
                      <Progress value={session.progress} className="h-2" />
                    </div>
                  )}

                  <Button 
                    className="w-full"
                    disabled={session.status === 'completed'}
                    onClick={() => setActiveSession(session)}
                  >
                    {session.status === 'completed' ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        View Summary
                      </>
                    ) : (
                      <>
                        <PlayCircle className="h-4 w-4 mr-2" />
                        {session.status === 'active' ? 'Continue' : 'Start'}
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {sessions.length === 0 && (
            <Card>
              <CardContent className="text-center py-12">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No study sessions yet
                </h3>
                <p className="text-gray-600">
                  Start your first interactive study session with your child.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="prompts" className="space-y-6">
          {/* Filters */}
          <div className="flex gap-4">
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              {subjects.map(subject => (
                <option key={subject} value={subject}>
                  {subject === 'all' ? 'All Subjects' : subject.charAt(0).toUpperCase() + subject.slice(1)}
                </option>
              ))}
            </select>
            
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              {difficulties.map(difficulty => (
                <option key={difficulty} value={difficulty}>
                  {difficulty === 'all' ? 'All Levels' : difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Upgrade Prompt */}
          {!canAccessFeature('teaching_prompts') && (
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="text-center py-8">
                <Lightbulb className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-blue-900 mb-2">
                  Teaching Prompts
                </h3>
                <p className="text-blue-800 mb-4">
                  Upgrade to Standard or Premium Plus to access AI-powered teaching prompts
                </p>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  Upgrade Plan
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Prompts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {prompts.map((prompt) => (
              <Card key={prompt.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">{prompt.title}</CardTitle>
                  <CardDescription>
                    {prompt.description}
                  </CardDescription>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge className={getDifficultyColor(prompt.difficulty)}>
                      {prompt.difficulty}
                    </Badge>
                    <Badge variant="outline">
                      {prompt.subject}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-medium text-sm mb-2">Learning Objectives:</h4>
                    <ul className="space-y-1">
                      {prompt.objectives.slice(0, 3).map((objective, index) => (
                        <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                          <span className="text-blue-600">•</span>
                          {objective}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      <Clock className="h-3 w-3 inline mr-1" />
                      {prompt.estimatedTime} min
                    </span>
                  </div>

                  <Button 
                    className="w-full"
                    onClick={() => startStudySession(prompt.id)}
                  >
                    <PlayCircle className="h-4 w-4 mr-2" />
                    Start Session
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="exercises" className="space-y-6">
          {/* Same filters as prompts */}
          <div className="flex gap-4">
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              {subjects.map(subject => (
                <option key={subject} value={subject}>
                  {subject === 'all' ? 'All Subjects' : subject.charAt(0).toUpperCase() + subject.slice(1)}
                </option>
              ))}
            </select>
            
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              {difficulties.map(difficulty => (
                <option key={difficulty} value={difficulty}>
                  {difficulty === 'all' ? 'All Levels' : difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Exercises Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {exercises.map((exercise) => (
              <Card key={exercise.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">{exercise.title}</CardTitle>
                  <CardDescription>
                    {exercise.description}
                  </CardDescription>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge className={getDifficultyColor(exercise.difficulty)}>
                      {exercise.difficulty}
                    </Badge>
                    <Badge variant="outline">
                      {exercise.type}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      <Clock className="h-3 w-3 inline mr-1" />
                      {exercise.estimatedTime} min
                    </span>
                    <span className="text-gray-600">
                      {exercise.questions.length} questions
                    </span>
                  </div>

                  <Button 
                    className="w-full"
                    onClick={() => startStudySession(undefined, exercise.id)}
                  >
                    <Target className="h-4 w-4 mr-2" />
                    Start Exercise
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="active" className="space-y-6">
          {activeSession ? (
            <div className="space-y-6">
              {/* Session Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-blue-600" />
                    {activeSession.title}
                  </CardTitle>
                  <CardDescription>
                    {activeSession.subject} - {activeSession.topic}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-gray-600" />
                      <span>
                        {activeSession.participants.parent.name} + {activeSession.participants.child.name}
                      </span>
                    </div>
                    <Badge className={
                      activeSession.status === 'active' ? 'bg-blue-100 text-blue-800' :
                      activeSession.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }>
                      {activeSession.status}
                    </Badge>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Session Progress</span>
                      <span className="text-sm text-gray-600">{activeSession.progress}%</span>
                    </div>
                    <Progress value={activeSession.progress} className="h-3" />
                  </div>
                </CardContent>
              </Card>

              {/* Activities */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Session Activities</h3>
                {activeSession.activities.map((activity) => (
                  <Card key={activity.id}>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        {getActivityIcon(activity.type)}
                        {activity.title}
                      </CardTitle>
                      {activity.completed && (
                        <Badge className="bg-green-100 text-green-800">
                          Completed
                        </Badge>
                      )}
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-gray-700">{activity.content}</p>
                      
                      {!activity.completed && (
                        <div>
                          <h4 className="font-medium text-sm mb-2">Your Response:</h4>
                          {activity.type === 'open_ended' && (
                            <textarea
                              placeholder="Enter your response..."
                              className="w-full p-2 border rounded-md"
                              rows={3}
                            />
                          )}
                          
                          <Button
                            className="mt-2"
                            onClick={() => {
                              // Handle response submission based on activity type
                              const response = activity.type === 'open_ended'
                                ? { text: 'Sample response' }
                                : { answer: 'Sample answer' };
                              
                              submitActivityResponse(activity.id, response);
                            }}
                          >
                            <Send className="h-4 w-4 mr-2" />
                            Submit Response
                          </Button>
                        </div>
                      )}
                      
                      {activity.completed && activity.responses && (
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <h4 className="font-medium text-sm mb-2">Your Response:</h4>
                          <p className="text-sm text-gray-700">
                            {activity.responses.text || activity.responses.answer}
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <PlayCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Active Session
                </h3>
                <p className="text-gray-600">
                  Start a new study session from the Teaching Prompts or Exercises tabs.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}