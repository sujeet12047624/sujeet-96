"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { aiService } from "@/services/ai";
import type { SearchResult } from "@/types";

export default function SemanticSearchPage() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error("Please enter a search query.");
      return;
    }
    setLoading(true);
    try {
      const data = await aiService.semanticSearch(query, topK);
      setResults(data.results);
      if (data.results.length === 0) {
        toast("No results found. Try a different query.");
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail?.error || "Search failed. Check subscription.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Semantic RAG Search</h1>
        <p className="text-gray-600">
          Search across the entire UPSC corpus using AI-powered semantic understanding.
          Find relevant content from blogs, NCERTs, and official syllabi.
        </p>
        <span className="badge-premium mt-2 inline-block">Premium Feature</span>
      </div>

      <div className="card mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            className="input-field flex-grow"
            placeholder="Ask any UPSC-related question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <select
            className="input-field w-24"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
          >
            {[3, 5, 10, 15, 20].map((n) => (
              <option key={n} value={n}>
                Top {n}
              </option>
            ))}
          </select>
          <button onClick={handleSearch} className="btn-primary" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">
            {results.length} Result{results.length !== 1 ? "s" : ""} Found
          </h2>
          {results.map((result, index) => (
            <div key={index} className="card">
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm font-medium text-primary-600">
                  Result #{index + 1}
                </span>
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                  Relevance: {(result.score * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-gray-800 leading-relaxed">{result.text}</p>
              {Object.keys(result.metadata).length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {Object.entries(result.metadata).map(([key, value]) => (
                    <span
                      key={key}
                      className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                    >
                      {key}: {String(value)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
