"use client";

import React, { useEffect, useState } from 'react';
import VidhyaChat from '@/components/vidhya/VidhyaChat';
import { DashboardNav } from '@/components/dashboard/DashboardNav';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageCircle, Globe, BookOpen, Users } from 'lucide-react';

export default function VidhyaPage() {
  const [userToken, setUserToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Get user token from localStorage or context
    const token = localStorage.getItem('userToken');
    if (token) {
      setUserToken(token);
    }
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!userToken) {
    return (
      <div className="min-h-screen bg-gray-50">
        <DashboardNav />
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-md mx-auto">
            <Card>
              <CardHeader className="text-center">
                <CardTitle className="flex items-center justify-center gap-2">
                  <MessageCircle className="h-6 w-6 text-blue-600" />
                  Authentication Required
                </CardTitle>
              </CardHeader>
              <CardContent className="text-center space-y-4">
                <p className="text-gray-600">
                  Please log in to access Vidhya AI Assistant.
                </p>
                <Button
                  onClick={() => window.location.href = '/auth'}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  Go to Login
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardNav />
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Vidhya AI Assistant</h1>
              <p className="text-gray-600 mt-2">
                Your multilingual AI learning companion - ask questions in your preferred language
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <BookOpen className="h-4 w-4 mr-2" />
                Help Guide
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
          {/* Feature Cards */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Globe className="h-5 w-5 text-blue-600" />
                Multilingual
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Chat in English, Hindi, Bengali, Telugu, Tamil, and more languages
              </p>
            </CardContent>
          </Card>

          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <MessageCircle className="h-5 w-5 text-green-600" />
                Simple Answers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Get easy-to-understand explanations for complex topics
              </p>
            </CardContent>
          </Card>

          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <BookOpen className="h-5 w-5 text-purple-600" />
                24/7 Available
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Get help with homework and studies anytime, anywhere
              </p>
            </CardContent>
          </Card>

          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Users className="h-5 w-5 text-orange-600" />
                Personalized
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Context-aware conversations that remember your learning journey
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Tips */}
        <Card className="mb-6 bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-900">💡 Quick Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h4 className="font-medium text-blue-900">Getting Started</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Click "New Chat" to start a conversation</li>
                  <li>• Select your preferred language from the dropdown</li>
                  <li>• Ask questions in simple, clear language</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-blue-900">Best Practices</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Be specific in your questions</li>
                  <li>• Provide context about your subject</li>
                  <li>• Ask follow-up questions for clarity</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Chat Interface */}
        <div className="h-[600px]">
          <VidhyaChat userToken={userToken} />
        </div>
      </div>
    </div>
  );
}