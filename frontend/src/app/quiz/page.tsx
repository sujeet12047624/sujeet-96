"use client";

import { useEffect, useState } from "react";
import { blogService } from "@/services/blog";
import type { MCQQuestion } from "@/types";

export default function QuizPage() {
  const [questions, setQuestions] = useState<MCQQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [quizDate, setQuizDate] = useState(new Date().toISOString().split("T")[0]);

  useEffect(() => {
    setLoading(true);
    setShowResults(false);
    setAnswers({});
    blogService
      .getDailyQuiz(quizDate)
      .then((data) => setQuestions(data.questions))
      .catch(() => setQuestions([]))
      .finally(() => setLoading(false));
  }, [quizDate]);

  const handleAnswer = (questionId: number, option: string) => {
    if (showResults) return;
    setAnswers({ ...answers, [questionId]: option });
  };

  const handleSubmit = () => setShowResults(true);

  const score = questions.filter(
    (q) => answers[q.id] === q.correct_option
  ).length;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Daily UPSC Quiz</h1>
          <p className="text-gray-600 mt-1">5 MCQs from current affairs</p>
        </div>
        <input
          type="date"
          value={quizDate}
          onChange={(e) => setQuizDate(e.target.value)}
          className="input-field w-auto"
        />
      </div>

      {loading ? (
        <div className="space-y-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="space-y-2">
                {[1, 2, 3, 4].map((j) => (
                  <div key={j} className="h-4 bg-gray-200 rounded w-1/2"></div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : questions.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 text-lg">No quiz available for this date.</p>
          <p className="text-gray-400 text-sm mt-2">
            Quizzes are generated daily from current affairs content.
          </p>
        </div>
      ) : (
        <>
          <div className="space-y-6">
            {questions.map((q, index) => {
              const options = [
                { key: "A", value: q.option_a },
                { key: "B", value: q.option_b },
                { key: "C", value: q.option_c },
                { key: "D", value: q.option_d },
              ];

              return (
                <div key={q.id} className="card">
                  <div className="flex items-start gap-3 mb-4">
                    <span className="bg-primary-100 text-primary-700 font-bold px-3 py-1 rounded-full text-sm">
                      Q{index + 1}
                    </span>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          q.difficulty === "easy"
                            ? "bg-green-100 text-green-700"
                            : q.difficulty === "hard"
                            ? "bg-red-100 text-red-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {q.difficulty}
                      </span>
                    </div>
                  </div>
                  <p className="text-lg font-medium mb-4">{q.question}</p>
                  <div className="space-y-2">
                    {options.map((opt) => {
                      const isSelected = answers[q.id] === opt.key;
                      const isCorrect = opt.key === q.correct_option;
                      let optionClass =
                        "border border-gray-200 rounded-lg p-3 cursor-pointer transition-colors";

                      if (showResults) {
                        if (isCorrect)
                          optionClass += " bg-green-50 border-green-500 text-green-800";
                        else if (isSelected && !isCorrect)
                          optionClass += " bg-red-50 border-red-500 text-red-800";
                        else optionClass += " opacity-60";
                      } else if (isSelected) {
                        optionClass += " bg-primary-50 border-primary-500";
                      } else {
                        optionClass += " hover:bg-gray-50";
                      }

                      return (
                        <div
                          key={opt.key}
                          className={optionClass}
                          onClick={() => handleAnswer(q.id, opt.key)}
                        >
                          <span className="font-medium mr-2">{opt.key}.</span>
                          {opt.value}
                        </div>
                      );
                    })}
                  </div>
                  {showResults && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                      <p className="text-sm font-medium text-blue-800">Explanation:</p>
                      <p className="text-sm text-blue-700 mt-1">{q.explanation}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="mt-8 text-center">
            {!showResults ? (
              <button
                onClick={handleSubmit}
                className="btn-primary text-lg px-10 py-3"
                disabled={Object.keys(answers).length < questions.length}
              >
                Submit Quiz
              </button>
            ) : (
              <div className="card inline-block">
                <p className="text-2xl font-bold">
                  Score: {score}/{questions.length}
                </p>
                <p className="text-gray-600 mt-1">
                  {score === questions.length
                    ? "Perfect score! Excellent preparation!"
                    : score >= 3
                    ? "Good job! Keep practicing."
                    : "Review the explanations carefully."}
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
