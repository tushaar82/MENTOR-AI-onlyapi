import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  // Parent login
  login: (email: string, password: string) =>
    api.post('/api/auth/login/email', { email, password }),
  
  // Student login
  studentLogin: (username: string, password: string) =>
    api.post('/api/auth/login/student', { username, password }),
  
  register: (data: {
    name: string;
    mobile_number: string;
    email_address: string;
    password: string;
    repeat_password: string;
  }) => api.post('/api/auth/register/simple', null, { params: data }),
  
  verifyEmail: (token: string) =>
    api.post('/api/auth/verify/email/confirm', { token }),
  
  resendVerification: (email: string) =>
    api.post('/api/auth/verify/email/send', { email }),
};

// Onboarding API
export const onboardingAPI = {
  // Parent Preferences
  createPreferences: (parent_id: string, data: {
    language: 'en' | 'hi' | 'mr';
    email_notifications: boolean;
    sms_notifications: boolean;
    push_notifications: boolean;
    teaching_involvement: 'high' | 'medium' | 'low';
  }) => api.post('/api/onboarding/preferences', data, { params: { parent_id } }),
  
  getPreferences: (parent_id: string) =>
    api.get('/api/onboarding/preferences', { params: { parent_id } }),
  
  updatePreferences: (parent_id: string, data: {
    language?: 'en' | 'hi' | 'mr';
    email_notifications?: boolean;
    sms_notifications?: boolean;
    push_notifications?: boolean;
    teaching_involvement?: 'high' | 'medium' | 'low';
  }) => api.put('/api/onboarding/preferences', data, { params: { parent_id } }),
  
  // Child Profile
  createChildProfile: (parent_id: string, data: {
    name: string;
    age: number;
    grade: number;
    current_level: 'beginner' | 'intermediate' | 'advanced';
    username: string;
    password: string;
  }) => api.post('/api/onboarding/child', data, { params: { parent_id } }),
  
  getChildProfile: (parent_id: string) =>
    api.get('/api/onboarding/child', { params: { parent_id } }),
  
  updateChildProfile: (parent_id: string, child_id: string, data: {
    name?: string;
    age?: number;
    grade?: number;
    current_level?: 'beginner' | 'intermediate' | 'advanced';
    username?: string;
    password?: string;
  }) => api.put(`/api/onboarding/child/${child_id}`, data, { params: { parent_id } }),
};

// Exam Selection API
export const examAPI = {
  getAvailableExams: () =>
    api.get('/api/onboarding/exams/available'),
  
  selectExam: (parent_id: string, child_id: string, data: {
    exam_type: 'JEE_MAIN' | 'JEE_ADVANCED' | 'JEE_COMBO' | 'NEET';
    exam_date: string;
    subject_preferences: Record<string, number>;
  }) => api.post('/api/onboarding/exam/select', data, { params: { parent_id, child_id } }),
  
  getExamSelection: (child_id: string) =>
    api.get('/api/onboarding/exam/preferences', { params: { child_id } }),
  
  updateSubjectPreferences: (parent_id: string, child_id: string, preferences: Record<string, number>) =>
    api.put('/api/onboarding/exam/preferences', preferences, { params: { parent_id, child_id } }),
  
  getOnboardingStatus: (parent_id: string) =>
    api.get('/api/onboarding/status', { params: { parent_id } }),
  
  getDiagnosticTest: (test_id: string) =>
    api.get(`/api/diagnostic-test/${test_id}`),
  
  scheduleDiagnosticTest: (data: {
    child_id: string;
    exam_type: string;
    scheduled_date: string;
    test_id: string;
  }) => api.post('/api/diagnostic-test/schedule', data),
  
  getScheduledTests: (child_id: string) =>
    api.get('/api/diagnostic-test/student/' + child_id),
};

// AI Features API
export const aiFeaturesAPI = {
  // AI Interactions
  getInteractions: (params?: {
    student_id?: string;
    interaction_type?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    skip?: number;
  }) => api.get('/api/ai-features/interactions', { params }),
  
  getInteractionsSummary: (days?: number) =>
    api.get('/api/ai-features/interactions/summary', { params: { days } }),
  
  // Parent Insights
  getInsights: (params?: {
    student_id?: string;
    insight_type?: string;
    severity?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    skip?: number;
  }) => api.get('/api/ai-features/insights', { params }),
  
  generateInsights: (student_id: string, insight_type?: string) =>
    api.get('/api/ai-features/insights/generate', { params: { student_id, insight_type } }),
  
  updateInsightStatus: (insight_id: string, data: {
    status: string;
    action_taken?: string;
  }) => api.post(`/api/ai-features/insights/${insight_id}/status`, data),
  
  // Engagement Metrics
  getEngagementMetrics: (student_id: string, params?: {
    metric_type?: string;
    period?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    skip?: number;
  }) => api.get('/api/ai-features/engagement-metrics', { params: { student_id, ...params } }),
  
  trackEngagementMetric: (data: {
    student_id: string;
    metric_type: string;
    metric_name: string;
    value: number;
    unit: string;
    period: string;
    date: string;
    context?: Record<string, any>;
  }) => api.post('/api/ai-features/engagement-metrics/track', data),
  
  // Communication History
  getCommunicationHistory: (params?: {
    student_id?: string;
    communication_type?: string;
    channel?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    skip?: number;
  }) => api.get('/api/ai-features/communications', { params }),
  
  // Intervention Alerts
  getAlerts: (params?: {
    student_id?: string;
    alert_type?: string;
    severity?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    skip?: number;
  }) => api.get('/api/ai-features/alerts', { params }),
  
  updateAlertStatus: (alert_id: string, data: {
    status: string;
    resolution_notes?: string;
  }) => api.post(`/api/ai-features/alerts/${alert_id}/status`, data),
  
  // Dashboard
  getDashboard: (student_id?: string) =>
    api.get('/api/ai-features/dashboard', { params: { student_id } }),
  
  getDashboardConfig: () =>
    api.get('/api/ai-features/dashboard/config'),
  
  updateDashboardConfig: (data: {
    notification_preferences?: Record<string, boolean>;
    insight_preferences?: Record<string, boolean>;
    privacy_settings?: Record<string, boolean>;
  }) => api.post('/api/ai-features/dashboard/config', data),
  
  // Health Check
  healthCheck: () =>
    api.get('/api/ai-features/health'),
};

// Study Center API
export const studyCenterAPI = {
  getStudyMaterials: (params?: {
    subject?: string;
    topic?: string;
    difficulty?: string;
    limit?: number;
  }) => api.get('/api/study-center/materials', { params }),
  
  getStudyPlan: (student_id: string) =>
    api.get('/api/study-center/plan', { params: { student_id } }),
  
  updateStudyProgress: (data: {
    student_id: string;
    material_id: string;
    progress: number;
    time_spent: number;
  }) => api.post('/api/study-center/progress', data),
  
  getRecommendations: (student_id: string) =>
    api.get('/api/study-center/recommendations', { params: { student_id } }),
};

// Parent Dashboard API
export const parentDashboardAPI = {
  getOverview: (student_id?: string) =>
    api.get('/api/parent/dashboard', { params: { student_id } }),
  
  getWeeklyReport: (student_id: string) =>
    api.get('/api/parent/reports/weekly', { params: { student_id } }),
  
  getMonthlyReport: (student_id: string) =>
    api.get('/api/parent/reports/monthly', { params: { student_id } }),
  
  setGoals: (student_id: string, data: {
    goals: Array<{
      title: string;
      description: string;
      target_date: string;
      metrics: Record<string, number>;
    }>;
  }) => api.post('/api/parent/goals', data, { params: { student_id } }),
  
  getGoals: (student_id: string) =>
    api.get('/api/parent/goals', { params: { student_id } }),
  
  updateGoal: (goal_id: string, data: {
    title?: string;
    description?: string;
    target_date?: string;
    metrics?: Record<string, number>;
    status?: string;
  }) => api.put(`/api/parent/goals/${goal_id}`, data),
};

// Student Dashboard API
export const studentDashboardAPI = {
  getTodayPlan: (student_id: string) =>
    api.get('/api/student/today', { params: { student_id } }),
  
  getQuickPractice: (student_id: string, params?: {
    subject?: string;
    difficulty?: string;
    count?: number;
  }) => api.get('/api/student/practice/quick', { params: { student_id, ...params } }),
  
  getDoubts: (student_id: string) =>
    api.get('/api/student/doubts', { params: { student_id } }),
  
  submitDoubt: (student_id: string, data: {
    question: string;
    subject: string;
    topic?: string;
    context?: string;
  }) => api.post('/api/student/doubts', data, { params: { student_id } }),
  
  getBookmarks: (student_id: string) =>
    api.get('/api/student/bookmarks', { params: { student_id } }),
  
  addBookmark: (student_id: string, data: {
    title: string;
    type: string;
    content: string;
    url?: string;
  }) => api.post('/api/student/bookmarks', data, { params: { student_id } }),
  
  removeBookmark: (bookmark_id: string) =>
    api.delete(`/api/student/bookmarks/${bookmark_id}`),
};

// Gamification API
export const gamificationAPI = {
  getAchievements: (student_id: string) =>
    api.get('/api/gamification/achievements', { params: { student_id } }),
  
  getDailyChallenge: (student_id: string) =>
    api.get('/api/gamification/challenge/daily', { params: { student_id } }),
  
  submitChallengeResult: (student_id: string, data: {
    challenge_id: string;
    result: any;
    time_taken: number;
  }) => api.post('/api/gamification/challenge/submit', data, { params: { student_id } }),
  
  getLeaderboard: (params?: {
    type?: string;
    period?: string;
    limit?: number;
  }) => api.get('/api/gamification/leaderboard', { params }),
  
  getStreak: (student_id: string) =>
    api.get('/api/gamification/streak', { params: { student_id } }),
  
  getPoints: (student_id: string) =>
    api.get('/api/gamification/points', { params: { student_id } }),
};

// Analytics API
export const analyticsAPI = {
  generateAnalytics: (student_id: string, params?: {
    period?: string;
    metrics?: string[];
  }) => api.get('/api/analytics/generate', { params: { student_id, ...params } }),
  
  getStudentAnalytics: (student_id: string, params?: {
    period?: string;
    type?: string;
  }) => api.get('/api/analytics/student', { params: { student_id, ...params } }),
  
  getPerformanceTrends: (student_id: string, params?: {
    subject?: string;
    period?: string;
  }) => api.get('/api/analytics/trends', { params: { student_id, ...params } }),
  
  getWeakAreas: (student_id: string) =>
    api.get('/api/analytics/weak-areas', { params: { student_id } }),
  
  getProgressReport: (student_id: string, params?: {
    period?: string;
    format?: string;
  }) => api.get('/api/analytics/progress', { params: { student_id, ...params } }),
};

// Syllabus Coverage API
export const syllabusAPI = {
  getCoverage: (student_id: string, params?: {
    subject?: string;
    chapter?: string;
  }) => api.get('/api/syllabus/coverage', { params: { student_id, ...params } }),
  
  updateCoverage: (student_id: string, data: {
    subject: string;
    chapter: string;
    topics: Array<{
      name: string;
      completed: boolean;
      confidence_level: number;
    }>;
  }) => api.post('/api/syllabus/coverage/update', data, { params: { student_id } }),
  
  getRecommendations: (student_id: string) =>
    api.get('/api/syllabus/recommendations', { params: { student_id } }),
};
