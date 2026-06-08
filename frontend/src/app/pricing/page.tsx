"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { subscriptionService } from "@/services/subscription";

declare global {
  interface Window {
    Razorpay: any;
  }
}

export default function PricingPage() {
  const [loading, setLoading] = useState(false);

  const handleRazorpayPayment = async () => {
    setLoading(true);
    try {
      const order = await subscriptionService.createRazorpayOrder();
      const options = {
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "UPSC Blog Premium",
        description: "Premium Access Tier – 90 Days",
        order_id: order.order_id,
        handler: () => {
          toast.success("Payment successful! Premium access activated.");
          window.location.reload();
        },
        theme: { color: "#2563eb" },
      };
      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (detail?.pricing_page) {
        toast.error("Please log in to subscribe.");
      } else {
        toast.error("Failed to initiate payment. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStripePayment = async () => {
    setLoading(true);
    try {
      const session = await subscriptionService.createStripeSession(
        `${window.location.origin}/pricing?success=true`,
        `${window.location.origin}/pricing?cancelled=true`
      );
      window.location.href = session.url;
    } catch (err: any) {
      toast.error("Failed to initiate Stripe payment.");
    } finally {
      setLoading(false);
    }
  };

  const features = [
    "AI Mains Answer Evaluator (Claude 3.5 Sonnet)",
    "Semantic RAG Search across UPSC corpus",
    "Personalized study recommendations",
    "Priority support",
    "Access to premium articles",
    "Detailed rubric feedback on answers",
  ];

  const freeFeatures = [
    "All Prelims & Mains articles",
    "Daily MCQ quizzes (5 questions)",
    "Current affairs coverage",
    "GS Paper categorization",
    "Auto-tagged syllabus topics",
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
        <p className="text-xl text-gray-600">
          Unlock AI-powered features for your UPSC preparation
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        {/* Free Plan */}
        <div className="card border-2 border-gray-200">
          <h2 className="text-2xl font-bold mb-2">Free</h2>
          <p className="text-4xl font-bold mb-1">
            ₹0<span className="text-lg font-normal text-gray-500">/forever</span>
          </p>
          <p className="text-gray-600 mb-6">Essential UPSC preparation</p>
          <ul className="space-y-3 mb-8">
            {freeFeatures.map((f) => (
              <li key={f} className="flex items-start gap-2">
                <svg className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-gray-700">{f}</span>
              </li>
            ))}
          </ul>
          <button className="btn-secondary w-full" disabled>
            Current Plan
          </button>
        </div>

        {/* Premium Plan */}
        <div className="card border-2 border-primary-500 relative">
          <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
            Recommended
          </span>
          <h2 className="text-2xl font-bold mb-2">Premium Access Tier</h2>
          <p className="text-4xl font-bold mb-1">
            ₹500<span className="text-lg font-normal text-gray-500">/90 days</span>
          </p>
          <p className="text-gray-600 mb-6">Advanced AI-powered features</p>
          <ul className="space-y-3 mb-8">
            {features.map((f) => (
              <li key={f} className="flex items-start gap-2">
                <svg className="w-5 h-5 text-primary-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-gray-700">{f}</span>
              </li>
            ))}
          </ul>
          <div className="space-y-3">
            <button
              onClick={handleRazorpayPayment}
              className="btn-primary w-full"
              disabled={loading}
            >
              {loading ? "Processing..." : "Pay with Razorpay (UPI/Cards)"}
            </button>
            <button
              onClick={handleStripePayment}
              className="btn-secondary w-full"
              disabled={loading}
            >
              Pay with Stripe (International)
            </button>
          </div>
        </div>
      </div>

      {/* Razorpay script */}
      <script src="https://checkout.razorpay.com/v1/checkout.js" async />
    </div>
  );
}
