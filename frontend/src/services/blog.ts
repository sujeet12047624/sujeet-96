import api from "@/lib/api";
import type { BlogPost, MCQQuestion, PaginatedResponse } from "@/types";

export const blogService = {
  async getPosts(params?: {
    category?: string;
    gs_paper?: string;
    search?: string;
    ordering?: string;
    page?: number;
  }): Promise<PaginatedResponse<BlogPost>> {
    const response = await api.get("/api/blog/posts/", { params });
    return response.data;
  },

  async getPost(slug: string): Promise<BlogPost> {
    const response = await api.get(`/api/blog/posts/${slug}/`);
    return response.data;
  },

  async getDailyQuiz(date?: string): Promise<{ date: string; questions: MCQQuestion[] }> {
    const response = await api.get("/api/blog/quiz/", {
      params: date ? { date } : {},
    });
    return response.data;
  },

  async getCategories() {
    const response = await api.get("/api/blog/categories/");
    return response.data;
  },
};
