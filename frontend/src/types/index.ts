export interface User {
  id: number;
  email: string;
  username: string;
  phone_number: string;
  is_premium: boolean;
  bio: string;
  preparation_year: number | null;
  optional_subject: string;
  avatar: string;
  created_at: string;
}

export interface BlogPost {
  id: number;
  title: string;
  slug: string;
  author_name: string;
  content?: string;
  excerpt: string;
  featured_image: string;
  category: "prelims" | "mains" | "current_affairs" | "editorial";
  gs_paper: string;
  micro_topics: string[];
  is_premium: boolean;
  views_count: number;
  published_at: string;
  created_at: string;
  updated_at?: string;
}

export interface MCQQuestion {
  id: number;
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_option: "A" | "B" | "C" | "D";
  explanation: string;
  difficulty: "easy" | "medium" | "hard";
  quiz_date: string;
}

export interface Subscription {
  id: number;
  plan_name: string;
  price_inr: number;
  start_date: string;
  end_date: string;
  status: "active" | "expired" | "cancelled";
  is_active: boolean;
  days_remaining: number;
  created_at: string;
}

export interface SubscriptionPlan {
  name: string;
  price_inr: number;
  duration_days: number;
  features: string[];
}

export interface EvaluationResult {
  total_score: number;
  rubric_breakdown: {
    introduction: { score: number; feedback: string };
    analytical_depth: { score: number; feedback: string };
    structure_and_points: { score: number; feedback: string };
    conclusion: { score: number; feedback: string };
    factual_accuracy: { score: number; feedback: string };
  };
  strengths: string[];
  areas_for_improvement: string[];
  model_answer_draft: string;
}

export interface SearchResult {
  text: string;
  score: number;
  metadata: Record<string, string | number>;
}

export interface APIResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
