import api from "@/lib/api";
import type { Subscription, SubscriptionPlan } from "@/types";

export const subscriptionService = {
  async getPlans(): Promise<{ plans: SubscriptionPlan[] }> {
    const response = await api.get("/api/subscriptions/plans/");
    return response.data;
  },

  async getMySubscription(): Promise<Subscription> {
    const response = await api.get("/api/subscriptions/me/");
    return response.data;
  },

  async createRazorpayOrder() {
    const response = await api.post("/api/payments/razorpay/create-order/");
    return response.data;
  },

  async createStripeSession(successUrl: string, cancelUrl: string) {
    const response = await api.post("/api/payments/stripe/create-session/", {
      success_url: successUrl,
      cancel_url: cancelUrl,
    });
    return response.data;
  },

  async getTransactions() {
    const response = await api.get("/api/subscriptions/transactions/");
    return response.data;
  },
};
