"""UPSC Mains Answer Evaluator using Claude 3.5 Sonnet (streaming)."""

import json
import logging

import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

EVALUATION_SYSTEM_PROMPT = """You are an expert UPSC Mains answer evaluator with 20+ years of experience.
Evaluate the candidate's answer against the given UPSC question using these pillars:

1. **Introduction** (10 marks): Relevance, context-setting, clarity
2. **Body - Analytical Depth** (40 marks): Multi-dimensional analysis, use of examples, data, case studies
3. **Body - Structure & Points** (20 marks): Logical flow, sub-headings, point-wise organization
4. **Conclusion** (10 marks): Summary, way forward, balanced view
5. **Core Factual Accuracy** (20 marks): Correctness of facts, dates, constitutional provisions, schemes

Return a structured JSON response with:
{
  "total_score": <0-100>,
  "rubric_breakdown": {
    "introduction": {"score": <0-10>, "feedback": "..."},
    "analytical_depth": {"score": <0-40>, "feedback": "..."},
    "structure_and_points": {"score": <0-20>, "feedback": "..."},
    "conclusion": {"score": <0-10>, "feedback": "..."},
    "factual_accuracy": {"score": <0-20>, "feedback": "..."}
  },
  "strengths": ["..."],
  "areas_for_improvement": ["..."],
  "model_answer_draft": "A concise, well-structured model answer for the same question (250 words max)"
}"""


class AnswerEvaluator:
    """Evaluates UPSC Mains answers using Claude 3.5 Sonnet with streaming."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def evaluate_streaming(self, question: str, answer: str, gs_paper: str = ""):
        """Stream evaluation results chunk by chunk."""
        gs_context = f" (GS Paper: {gs_paper})" if gs_paper else ""
        user_message = f"""UPSC Mains Question{gs_context}:
{question}

Candidate's Answer:
{answer}

Please evaluate this answer thoroughly using the rubric and provide your structured JSON assessment."""

        try:
            with self.client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=EVALUATION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.exception("Claude streaming evaluation failed")
            yield json.dumps({"error": str(e)})

    def evaluate_sync(self, question: str, answer: str, gs_paper: str = "") -> dict:
        """Non-streaming evaluation for Celery task usage."""
        gs_context = f" (GS Paper: {gs_paper})" if gs_paper else ""
        user_message = f"""UPSC Mains Question{gs_context}:
{question}

Candidate's Answer:
{answer}

Please evaluate this answer thoroughly using the rubric and provide your structured JSON assessment."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=EVALUATION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            return json.loads(response.content[0].text)
        except Exception as e:
            logger.exception("Claude evaluation failed")
            return {"error": str(e)}
