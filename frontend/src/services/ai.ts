import api from "@/lib/api";
import type { SearchResult } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const aiService = {
  async evaluateAnswer(
    question: string,
    answer: string,
    gsPaper?: string,
    onChunk?: (chunk: string) => void
  ): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/api/ai/evaluate/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ question, answer, gs_paper: gsPaper }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.error || "Evaluation failed");
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullText = "";

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") break;
            fullText += data;
            onChunk?.(data);
          }
        }
      }
    }

    return fullText;
  },

  async semanticSearch(
    query: string,
    topK: number = 5
  ): Promise<{ query: string; results: SearchResult[]; total: number }> {
    const response = await api.post("/api/ai/search/", {
      query,
      top_k: topK,
    });
    return response.data;
  },
};
