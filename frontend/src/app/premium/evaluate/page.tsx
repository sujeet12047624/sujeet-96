"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { aiService } from "@/services/ai";

export default function AnswerEvaluatorPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [gsPaper, setGsPaper] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");

  const handleEvaluate = async () => {
    if (!question.trim() || !answer.trim()) {
      toast.error("Please provide both the question and your answer.");
      return;
    }
    setLoading(true);
    setResult("");
    try {
      await aiService.evaluateAnswer(question, answer, gsPaper, (chunk) => {
        setResult((prev) => prev + chunk);
      });
    } catch (err: any) {
      toast.error(err.message || "Evaluation failed. Please check your subscription.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">AI Mains Answer Evaluator</h1>
        <p className="text-gray-600">
          Get your UPSC Mains answers evaluated by Claude AI with detailed rubric
          feedback, score breakdown, and a model answer draft.
        </p>
        <span className="badge-premium mt-2 inline-block">Premium Feature</span>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              GS Paper (Optional)
            </label>
            <select
              className="input-field"
              value={gsPaper}
              onChange={(e) => setGsPaper(e.target.value)}
            >
              <option value="">Select GS Paper</option>
              <option value="gs1">GS Paper 1</option>
              <option value="gs2">GS Paper 2</option>
              <option value="gs3">GS Paper 3</option>
              <option value="gs4">GS Paper 4 (Ethics)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              UPSC Question
            </label>
            <textarea
              className="input-field h-32"
              placeholder="Paste the UPSC Mains question here..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Answer
            </label>
            <textarea
              className="input-field h-64"
              placeholder="Type or paste your answer here..."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
            />
          </div>
          <button
            onClick={handleEvaluate}
            className="btn-primary w-full"
            disabled={loading}
          >
            {loading ? "Evaluating..." : "Evaluate Answer"}
          </button>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-3">Evaluation Result</h2>
          <div className="card min-h-[400px] bg-gray-50">
            {result ? (
              <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800">
                {result}
              </pre>
            ) : (
              <p className="text-gray-400 text-center py-20">
                Your evaluation results will appear here...
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
