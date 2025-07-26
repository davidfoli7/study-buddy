// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  fullName: string;
  isActive: boolean;
  isVerified: boolean;
  bio?: string;
  avatarUrl?: string;
  gradeLevel?: string;
  subjectsOfInterest?: string[];
  preferredDifficulty: 'easy' | 'medium' | 'hard';
  dailyStudyGoalMinutes: number;
  preferredStudyTime?: 'morning' | 'afternoon' | 'evening';
  totalStudyTimeMinutes: number;
  totalAssessmentsCompleted: number;
  averageScore: number;
  streakDays: number;
  lastActivity: string;
  createdAt: string;
  updatedAt: string;
}

// Learning Session Types
export interface LearningSession {
  id: number;
  userId: number;
  subject: string;
  topic?: string;
  sessionType: 'study' | 'assessment' | 'review' | 'practice';
  difficultyLevel: 'easy' | 'medium' | 'hard';
  startTime: string;
  endTime?: string;
  durationMinutes?: number;
  plannedDurationMinutes: number;
  completionPercentage: number;
  focusScore?: number;
  comprehensionScore?: number;
  activitiesCompleted: number;
  totalActivities: number;
  notes?: string;
  aiInsights?: string;
  isCompleted: boolean;
  isInterrupted: boolean;
  interruptionReason?: string;
  createdAt: string;
  updatedAt: string;
}

// Assessment Types
export interface Assessment {
  id: number;
  userId: number;
  title: string;
  subject: string;
  topic?: string;
  assessmentType: 'diagnostic' | 'formative' | 'summative' | 'adaptive';
  difficultyLevel: 'easy' | 'medium' | 'hard';
  startTime?: string;
  endTime?: string;
  timeLimitMinutes?: number;
  timeTakenMinutes?: number;
  totalQuestions: number;
  questionsAnswered: number;
  correctAnswers: number;
  scorePercentage?: number;
  maxPossibleScore: number;
  strengths?: string[];
  weaknesses?: string[];
  recommendations?: string[];
  status: 'not_started' | 'in_progress' | 'completed' | 'abandoned';
  isCompleted: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Question {
  id: number;
  assessmentId: number;
  questionText: string;
  questionType: 'multiple_choice' | 'true_false' | 'short_answer' | 'essay' | 'fill_blank';
  difficultyLevel: 'easy' | 'medium' | 'hard';
  subject: string;
  topic?: string;
  options?: string[];
  correctAnswer?: string;
  explanation?: string;
  pointsPossible: number;
  bloomTaxonomyLevel?: string;
  learningObjective?: string;
  tags?: string[];
  estimatedTimeSeconds?: number;
  difficultyScore?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Answer {
  id: number;
  assessmentId: number;
  questionId: number;
  userId: number;
  answerText?: string;
  selectedOption?: string;
  isCorrect?: boolean;
  pointsEarned: number;
  pointsPossible: number;
  timeTakenSeconds?: number;
  answeredAt: string;
  confidenceLevel?: number;
  reasoningQuality?: number;
  aiFeedback?: string;
  hesitationTime?: number;
  revisionCount: number;
  createdAt: string;
  updatedAt: string;
}

// Content Types
export interface Content {
  id: number;
  title: string;
  description?: string;
  contentType: 'video' | 'article' | 'interactive' | 'quiz' | 'document' | 'audio';
  format?: string;
  subject: string;
  topic?: string;
  subtopic?: string;
  difficultyLevel: 'easy' | 'medium' | 'hard' | 'expert';
  gradeLevel?: string;
  learningObjectives?: string[];
  url?: string;
  filePath?: string;
  externalSource?: string;
  estimatedDurationMinutes?: number;
  complexityScore?: number;
  readabilityScore?: number;
  keyConcepts?: string[];
  prerequisites?: string[];
  visualScore: number;
  auditoryScore: number;
  kinestheticScore: number;
  readingScore: number;
  accuracyScore?: number;
  engagementScore?: number;
  averageRating?: number;
  totalRatings: number;
  viewCount: number;
  completionCount: number;
  averageCompletionRate?: number;
  averageTimeSpent?: number;
  isActive: boolean;
  isVerified: boolean;
  author?: string;
  sourceAttribution?: string;
  createdAt: string;
  updatedAt: string;
}

// Learning Style Types
export interface LearningStyle {
  id: number;
  userId: number;
  visualScore: number;
  auditoryScore: number;
  readingScore: number;
  kinestheticScore: number;
  socialVsSolitary: number;
  sequentialVsGlobal: number;
  activeVsReflective: number;
  sensingVsIntuitive: number;
  dominantStyle?: 'visual' | 'auditory' | 'reading' | 'kinesthetic' | 'multimodal';
  preferredPace: 'slow' | 'medium' | 'fast' | 'self_paced';
  preferredComplexity: 'immediate' | 'gradual' | 'complex';
  preferredFeedbackFrequency: 'immediate' | 'moderate' | 'delayed';
  attentionSpanMinutes: number;
  breakFrequencyMinutes: number;
  optimalSessionLength: number;
  confidenceScore: number;
  accuracyConfidence: number;
  assessmentMethod: 'survey' | 'behavioral' | 'hybrid';
  dataPointsCount: number;
  lastUpdatedMethod?: string;
  createdAt: string;
  updatedAt: string;
}

// Recommendation Types
export interface Recommendation {
  id: number;
  userId: number;
  recommendationType: 'content' | 'study_plan' | 'assessment' | 'break';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: string;
  targetContentId?: number;
  targetAssessmentId?: number;
  estimatedTimeMinutes?: number;
  difficultyLevel?: 'easy' | 'medium' | 'hard';
  reasoning: string;
  confidenceScore: number;
  isViewed: boolean;
  isAccepted?: boolean;
  viewedAt?: string;
  respondedAt?: string;
  expiresAt?: string;
  createdAt: string;
  updatedAt: string;
}

// Progress Types
export interface Progress {
  id: number;
  userId: number;
  subject: string;
  topic?: string;
  skillLevel: number; // 0-100
  masteryScore: number; // 0-100
  timeSpentMinutes: number;
  lastStudiedAt?: string;
  streakDays: number;
  totalSessions: number;
  averageSessionScore: number;
  improvementRate: number;
  predictedMasteryDate?: string;
  isCompleted: boolean;
  createdAt: string;
  updatedAt: string;
}

// Navigation Types
export type RootStackParamList = {
  Splash: undefined;
  Auth: undefined;
  Main: undefined;
  Onboarding: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
  ResetPassword: { token: string };
};

export type MainTabParamList = {
  Dashboard: undefined;
  Learn: undefined;
  Assess: undefined;
  Progress: undefined;
  Profile: undefined;
};

export type LearnStackParamList = {
  LearnHome: undefined;
  SubjectSelect: undefined;
  ContentList: { subject: string; topic?: string };
  ContentViewer: { contentId: number };
  LearningSession: { sessionId: number };
};

export type AssessStackParamList = {
  AssessHome: undefined;
  AssessmentList: { subject?: string };
  Assessment: { assessmentId: number };
  AssessmentResults: { assessmentId: number };
};

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// State Types
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface LearningState {
  currentSession: LearningSession | null;
  recentSessions: LearningSession[];
  recommendations: Recommendation[];
  isLoading: boolean;
  error: string | null;
}

export interface AssessmentState {
  currentAssessment: Assessment | null;
  currentQuestion: Question | null;
  currentQuestionIndex: number;
  answers: Answer[];
  timeRemaining?: number;
  isLoading: boolean;
  error: string | null;
}

export interface ContentState {
  contents: Content[];
  currentContent: Content | null;
  bookmarkedContents: Content[];
  recentContents: Content[];
  isLoading: boolean;
  error: string | null;
}

export interface ProgressState {
  overallProgress: Progress[];
  subjectProgress: { [subject: string]: Progress[] };
  learningStyle: LearningStyle | null;
  achievements: any[];
  isLoading: boolean;
  error: string | null;
}