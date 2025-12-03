"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Loader2, Send, Globe, Trash2, MessageCircle } from 'lucide-react';

interface Message {
  message_id: string;
  role: 'user' | 'assistant';
  content: string;
  language: string;
  timestamp: string;
}

interface Session {
  session_id: string;
  title: string;
  language: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface VidhyaChatProps {
  userToken?: string;
}

const SUPPORTED_LANGUAGES = {
  en: "English",
  hi: "हिन्दी (Hindi)",
  bn: "বাংলা (Bengali)",
  te: "తెలుగు (Telugu)",
  ta: "தமிழ் (Tamil)",
  mr: "मराठी (Marathi)",
  gu: "ગુજરાતી (Gujarati)",
  kn: "ಕನ್ನಡ (Kannada)",
  ml: "മലയാളം (Malayalam)",
  pa: "ਪੰਜਾਬੀ (Punjabi)"
};

export default function VidhyaChat({ userToken }: VidhyaChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [showSessions, setShowSessions] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (userToken) {
      loadSessions();
    }
  }, [userToken]);

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/vidhya/chat/sessions', {
        headers: {
          'Authorization': `Bearer ${userToken}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setSessions(data.data.sessions);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const startNewSession = async () => {
    try {
      const response = await fetch('/api/vidhya/chat/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify({
          language: selectedLanguage,
          title: `Chat - ${new Date().toLocaleDateString()}`
        })
      });
      const data = await response.json();
      if (data.success) {
        const newSession: Session = {
          session_id: data.data.session_id,
          title: data.data.title,
          language: data.data.language,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          message_count: 1
        };
        setCurrentSession(newSession);
        setMessages([{
          message_id: 'welcome',
          role: 'assistant',
          content: data.data.welcome_message,
          language: data.data.language,
          timestamp: new Date().toISOString()
        }]);
        setShowSessions(false);
        await loadSessions();
      }
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  };

  const loadSession = async (sessionId: string) => {
    try {
      const response = await fetch(`/api/vidhya/chat/history/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${userToken}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setCurrentSession({
          session_id: data.data.session_id,
          title: data.data.title,
          language: data.data.language,
          created_at: data.data.created_at,
          updated_at: data.data.updated_at,
          message_count: data.data.message_count
        });
        setMessages(data.data.messages);
        setShowSessions(false);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`/api/vidhya/chat/session/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${userToken}`
        }
      });
      const data = await response.json();
      if (data.success) {
        await loadSessions();
        if (currentSession?.session_id === sessionId) {
          setCurrentSession(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentSession || isLoading) return;

    const userMessage: Message = {
      message_id: `user_${Date.now()}`,
      role: 'user',
      content: inputMessage,
      language: selectedLanguage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await fetch('/api/vidhya/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: currentSession.session_id,
          language: selectedLanguage
        })
      });
      const data = await response.json();
      
      if (data.success) {
        const assistantMessage: Message = {
          message_id: `assistant_${Date.now()}`,
          role: 'assistant',
          content: data.data.response,
          language: data.data.language,
          timestamp: data.data.timestamp
        };
        setMessages(prev => [...prev, assistantMessage]);
        
        // Update session in sessions list
        await loadSessions();
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Add error message
      const errorMessage: Message = {
        message_id: `error_${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        language: selectedLanguage,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getMessageDirection = (language: string) => {
    // RTL languages: Arabic, Hebrew, Urdu, Persian
    const rtlLanguages = ['ar', 'he', 'ur', 'fa'];
    return rtlLanguages.includes(language) ? 'rtl' : 'ltr';
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <MessageCircle className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-semibold">Vidhya AI</h1>
          </div>
          
          <Button 
            onClick={startNewSession}
            className="w-full bg-blue-600 hover:bg-blue-700"
          >
            <MessageCircle className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Recent Chats</h3>
          <div className="space-y-2">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  currentSession?.session_id === session.session_id
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-gray-50 border border-gray-200'
                }`}
                onClick={() => loadSession(session.session_id)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm truncate">{session.title}</h4>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(session.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    <Badge variant="outline" className="text-xs">
                      {SUPPORTED_LANGUAGES[session.language as keyof typeof SUPPORTED_LANGUAGES]?.split(' ')[0] || session.language}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.session_id);
                      }}
                      className="h-6 w-6 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4 text-gray-500" />
            <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
              <SelectTrigger className="flex-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(SUPPORTED_LANGUAGES).map(([code, name]) => (
                  <SelectItem key={code} value={code}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {currentSession ? (
          <>
            {/* Header */}
            <div className="bg-white border-b border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10 bg-blue-600">
                    <AvatarFallback>V</AvatarFallback>
                  </Avatar>
                  <div>
                    <h2 className="font-semibold">{currentSession.title}</h2>
                    <p className="text-sm text-gray-500">
                      {SUPPORTED_LANGUAGES[currentSession.language as keyof typeof SUPPORTED_LANGUAGES]}
                    </p>
                  </div>
                </div>
                <Badge variant="outline">
                  {currentSession.message_count} messages
                </Badge>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.message_id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  dir={getMessageDirection(message.language)}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border border-gray-200 text-gray-800'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {message.role === 'assistant' && (
                        <Avatar className="h-6 w-6 bg-blue-600 flex-shrink-0 mt-1">
                          <AvatarFallback className="text-xs">V</AvatarFallback>
                        </Avatar>
                      )}
                      <div className="flex-1">
                        <p className="text-sm leading-relaxed">{message.content}</p>
                        <p
                          className={`text-xs mt-2 ${
                            message.role === 'user' ? 'text-blue-100' : 'text-gray-400'
                          }`}
                        >
                          {formatTimestamp(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center gap-2">
                      <Avatar className="h-6 w-6 bg-blue-600">
                        <AvatarFallback className="text-xs">V</AvatarFallback>
                      </Avatar>
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white border-t border-gray-200 p-4">
              <div className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask Vidhya anything..."
                  className="flex-1"
                  disabled={isLoading}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </>
        ) : (
          /* Welcome Screen */
          <div className="flex-1 flex items-center justify-center">
            <Card className="w-full max-w-md">
              <CardHeader className="text-center">
                <CardTitle className="flex items-center justify-center gap-2">
                  <MessageCircle className="h-6 w-6 text-blue-600" />
                  Welcome to Vidhya AI
                </CardTitle>
              </CardHeader>
              <CardContent className="text-center space-y-4">
                <p className="text-gray-600">
                  Your AI learning assistant that speaks your language!
                </p>
                <div className="space-y-2">
                  <p className="text-sm text-gray-500">
                    • Get help with homework and studies
                  </p>
                  <p className="text-sm text-gray-500">
                    • Ask questions in simple language
                  </p>
                  <p className="text-sm text-gray-500">
                    • Learn in your preferred language
                  </p>
                </div>
                <Button
                  onClick={startNewSession}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  Start Chatting
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}