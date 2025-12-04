"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Search, 
  Filter, 
  Heart, 
  Share2, 
  Download, 
  Star, 
  TrendingUp,
  Users,
  BookOpen,
  Plus,
  Eye
} from 'lucide-react';

interface Resource {
  id: string;
  title: string;
  description: string;
  type: 'article' | 'video' | 'worksheet' | 'guide' | 'template';
  category: string;
  subject: string;
  grade: string;
  language: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
    role: 'parent' | 'expert' | 'teacher';
  };
  stats: {
    views: number;
    likes: number;
    downloads: number;
    rating: number;
    reviews: number;
  };
  tags: string[];
  isLiked: boolean;
  isBookmarked: boolean;
  createdAt: string;
  content: {
    url?: string;
    text?: string;
    attachments?: Array<{
      name: string;
      url: string;
      type: string;
      size: string;
    }>;
  };
}

interface CommunityChallenge {
  id: string;
  title: string;
  description: string;
  type: 'contribution' | 'engagement' | 'quality';
  points: number;
  endDate: string;
  participants: number;
  isCompleted: boolean;
  progress: {
    current: number;
    target: number;
  };
}

interface LeaderboardEntry {
  rank: number;
  parentId: string;
  parentName: string;
  avatar?: string;
  points: number;
  badges: string[];
}

interface CommunityResourceLibraryProps {
  parentId: string;
  childId: string;
  subscriptionTier: 'basic' | 'standard' | 'premium_plus';
}

export default function CommunityResourceLibrary({ 
  parentId, 
  childId, 
  subscriptionTier 
}: CommunityResourceLibraryProps) {
  const [resources, setResources] = useState<Resource[]>([]);
  const [challenges, setChallenges] = useState<CommunityChallenge[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [sortBy, setSortBy] = useState('trending');
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('resources');
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);

  useEffect(() => {
    fetchCommunityData();
  }, [parentId, subscriptionTier, searchQuery, selectedCategory, selectedType, sortBy]);

  const fetchCommunityData = async () => {
    try {
      setLoading(true);
      
      // Fetch resources
      const resourcesResponse = await fetch(
        `/api/parent/resources/search?parent_id=${parentId}&query=${searchQuery}&category=${selectedCategory}&type=${selectedType}&sort=${sortBy}`
      );
      if (resourcesResponse.ok) {
        const resourcesData = await resourcesResponse.json();
        setResources(resourcesData.resources || []);
      }

      // Fetch challenges
      const challengesResponse = await fetch(`/api/parent/engagement/challenges?parent_id=${parentId}`);
      if (challengesResponse.ok) {
        const challengesData = await challengesResponse.json();
        setChallenges(challengesData.challenges || []);
      }

      // Fetch leaderboard
      const leaderboardResponse = await fetch('/api/parent/engagement/leaderboard');
      if (leaderboardResponse.ok) {
        const leaderboardData = await leaderboardResponse.json();
        setLeaderboard(leaderboardData.leaderboard || []);
      }
    } catch (error) {
      console.error('Error fetching community data:', error);
    } finally {
      setLoading(false);
    }
  };

  const likeResource = async (resourceId: string) => {
    try {
      const response = await fetch('/api/parent/resources/like', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_id: parentId,
          resource_id: resourceId
        })
      });

      if (response.ok) {
        setResources(prev => prev.map(resource => 
          resource.id === resourceId 
            ? { 
                ...resource, 
                isLiked: !resource.isLiked,
                stats: {
                  ...resource.stats,
                  likes: resource.isLiked ? resource.stats.likes - 1 : resource.stats.likes + 1
                }
              }
            : resource
        ));
      }
    } catch (error) {
      console.error('Error liking resource:', error);
    }
  };

  const bookmarkResource = async (resourceId: string) => {
    try {
      const response = await fetch('/api/parent/resources/bookmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_id: parentId,
          resource_id: resourceId
        })
      });

      if (response.ok) {
        setResources(prev => prev.map(resource => 
          resource.id === resourceId 
            ? { ...resource, isBookmarked: !resource.isBookmarked }
            : resource
        ));
      }
    } catch (error) {
      console.error('Error bookmarking resource:', error);
    }
  };

  const joinChallenge = async (challengeId: string) => {
    try {
      const response = await fetch('/api/parent/engagement/join-challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_id: parentId,
          challenge_id: challengeId
        })
      });

      if (response.ok) {
        setChallenges(prev => prev.map(challenge => 
          challenge.id === challengeId 
            ? { ...challenge, isCompleted: false }
            : challenge
        ));
      }
    } catch (error) {
      console.error('Error joining challenge:', error);
    }
  };

  const canContribute = () => {
    return subscriptionTier === 'standard' || subscriptionTier === 'premium_plus';
  };

  const getResourceTypeIcon = (type: string) => {
    switch (type) {
      case 'article': return '📄';
      case 'video': return '🎥';
      case 'worksheet': return '📋';
      case 'guide': return '📖';
      case 'template': return '📝';
      default: return '📄';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'article': return 'bg-blue-100 text-blue-800';
      case 'video': return 'bg-red-100 text-red-800';
      case 'worksheet': return 'bg-green-100 text-green-800';
      case 'guide': return 'bg-purple-100 text-purple-800';
      case 'template': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const categories = ['all', 'study_techniques', 'subject_help', 'motivation', 'organization', 'communication'];

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
          <h1 className="text-3xl font-bold text-gray-900">Community Resource Library</h1>
          <p className="text-gray-600 mt-2">
            Discover and share resources with fellow parents
          </p>
        </div>

        {canContribute() && (
          <Dialog>
            <Button
              className="bg-blue-600 hover:bg-blue-700"
              onClick={() => {/* Open contribution dialog */}}
            >
              <Plus className="h-4 w-4 mr-2" />
              Contribute Resource
            </Button>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Share Your Resource</DialogTitle>
              </DialogHeader>
              {/* Resource contribution form would go here */}
              <div className="p-4 text-center text-gray-600">
                Resource contribution form coming soon!
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="challenges">Challenges</TabsTrigger>
          <TabsTrigger value="leaderboard">Leaderboard</TabsTrigger>
        </TabsList>

        <TabsContent value="resources" className="space-y-6">
          {/* Search and Filters */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search resources..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <div className="flex gap-2">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 border rounded-md"
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
              
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-3 py-2 border rounded-md"
              >
                <option value="all">All Types</option>
                <option value="article">Articles</option>
                <option value="video">Videos</option>
                <option value="worksheet">Worksheets</option>
                <option value="guide">Guides</option>
                <option value="template">Templates</option>
              </select>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border rounded-md"
              >
                <option value="trending">Trending</option>
                <option value="newest">Newest</option>
                <option value="rating">Highest Rated</option>
                <option value="downloads">Most Downloaded</option>
              </select>
            </div>
          </div>

          {/* Resources Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map(resource => (
              <Card key={resource.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{getResourceTypeIcon(resource.type)}</span>
                      <Badge className={getTypeColor(resource.type)}>
                        {resource.type}
                      </Badge>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => likeResource(resource.id)}
                        className={resource.isLiked ? 'text-red-500' : ''}
                      >
                        <Heart className={`h-4 w-4 ${resource.isLiked ? 'fill-current' : ''}`} />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => bookmarkResource(resource.id)}
                      >
                        <BookOpen className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  
                  <CardTitle className="text-lg mt-2">{resource.title}</CardTitle>
                  <CardDescription className="line-clamp-2">
                    {resource.description}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Author */}
                  <div className="flex items-center gap-2">
                    <Avatar className="h-6 w-6">
                      <AvatarImage src={resource.author.avatar} />
                      <AvatarFallback>
                        {resource.author.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <span className="text-sm text-gray-600">{resource.author.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {resource.author.role}
                    </Badge>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1">
                    {resource.tags.slice(0, 3).map((tag, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {resource.tags.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{resource.tags.length - 3}
                      </Badge>
                    )}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {resource.stats.views}
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="h-3 w-3" />
                        {resource.stats.likes}
                      </span>
                      <span className="flex items-center gap-1">
                        <Download className="h-3 w-3" />
                        {resource.stats.downloads}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="h-3 w-3 text-yellow-500" />
                      {resource.stats.rating.toFixed(1)}
                    </div>
                  </div>

                  {/* Action Button */}
                  <Dialog open={selectedResource?.id === resource.id} onOpenChange={(open) => !open && setSelectedResource(null)}>
                    <Button
                      className="w-full"
                      onClick={() => setSelectedResource(resource)}
                    >
                      View Resource
                    </Button>
                    <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                      {selectedResource?.id === resource.id && (
                        <>
                          <DialogHeader>
                            <DialogTitle>{selectedResource.title}</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                            <p>{selectedResource.description}</p>
                            
                            {selectedResource.content.text && (
                              <div className="bg-gray-50 p-4 rounded-lg">
                                <p>{selectedResource.content.text}</p>
                              </div>
                            )}
                            
                            {selectedResource.content.attachments && (
                              <div>
                                <h4 className="font-medium mb-2">Attachments:</h4>
                                <div className="space-y-2">
                                  {selectedResource.content.attachments.map((attachment, index) => (
                                    <div key={index} className="flex items-center justify-between p-2 border rounded">
                                      <div className="flex items-center gap-2">
                                        <span>{attachment.name}</span>
                                        <Badge variant="outline" className="text-xs">
                                          {attachment.type}
                                        </Badge>
                                        <span className="text-sm text-gray-600">{attachment.size}</span>
                                      </div>
                                      <Button size="sm" variant="outline">
                                        <Download className="h-4 w-4" />
                                      </Button>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </>
                      )}
                    </DialogContent>
                  </Dialog>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Empty State */}
          {resources.length === 0 && (
            <Card>
              <CardContent className="text-center py-12">
                <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No resources found
                </h3>
                <p className="text-gray-600">
                  Try adjusting your search terms or filters.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="challenges" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {challenges.map(challenge => (
              <Card key={challenge.id}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    {challenge.title}
                  </CardTitle>
                  <CardDescription>
                    {challenge.description}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-green-100 text-green-800">
                        {challenge.points} points
                      </Badge>
                      <Badge variant="outline">
                        {challenge.participants} participants
                      </Badge>
                    </div>
                    <span className="text-sm text-gray-600">
                      Ends: {new Date(challenge.endDate).toLocaleDateString()}
                    </span>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Progress</span>
                      <span className="text-sm text-gray-600">
                        {challenge.progress.current} / {challenge.progress.target}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(challenge.progress.current / challenge.progress.target) * 100}%` }}
                      />
                    </div>
                  </div>

                  <Button 
                    className="w-full"
                    disabled={challenge.isCompleted || !canContribute()}
                    onClick={() => joinChallenge(challenge.id)}
                  >
                    {challenge.isCompleted ? (
                      'Completed'
                    ) : canContribute() ? (
                      'Join Challenge'
                    ) : (
                      'Upgrade to Participate'
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="leaderboard" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-yellow-600" />
                Community Leaderboard
              </CardTitle>
              <CardDescription>
                Top contributors this month
              </CardDescription>
            </CardHeader>

            <CardContent>
              <div className="space-y-4">
                {leaderboard.map((entry, index) => (
                  <div key={entry.parentId} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-yellow-100 text-yellow-800 font-bold">
                        {entry.rank}
                      </div>
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={entry.avatar} />
                        <AvatarFallback>
                          {entry.parentName.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-medium">{entry.parentName}</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Badge className="bg-yellow-100 text-yellow-800">
                        {entry.points} points
                      </Badge>
                      <div className="flex gap-1">
                        {entry.badges.slice(0, 2).map((badge, badgeIndex) => (
                          <Badge key={badgeIndex} variant="outline" className="text-xs">
                            {badge}
                          </Badge>
                        ))}
                        {entry.badges.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{entry.badges.length - 2}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}