import api from "@/lib/api";
import type { User } from "@/types";

export const authService = {
  async signup(data: {
    email: string;
    username: string;
    password: string;
    password_confirm: string;
  }) {
    const response = await api.post("/api/auth/signup/", data);
    return response.data;
  },

  async login(data: { email: string; password: string }) {
    const response = await api.post("/api/auth/login/", data);
    return response.data;
  },

  async logout() {
    const response = await api.post("/api/auth/logout/");
    return response.data;
  },

  async refreshToken() {
    const response = await api.post("/api/auth/token/refresh/");
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await api.get("/api/auth/profile/");
    return response.data;
  },

  async updateProfile(data: Partial<User>) {
    const response = await api.patch("/api/auth/profile/", data);
    return response.data;
  },
};
