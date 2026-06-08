"""Daily MCQ Quiz Generator using OpenAI Structured Outputs."""

import json
import logging

import openai
from django.conf import settings

logger = logging.getLogger(__name__)

MCQ_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "option_a": {"type": "string"},
                    "option_b": {"type": "string"},
                    "option_c": {"type": "string"},
                    "option_d": {"type": "string"},
                    "correct_option": {"type": "string", "enum": ["A", "B", "C", "D"]},
                    "explanation": {"type": "string"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                },
                "required": [
                    "question",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_option",
                    "explanation",
                    "difficulty",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["questions"],
    "additionalProperties": False,
}


class MCQGenerator:
    """Generates UPSC Prelims-style MCQs from current affairs content."""

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_mcqs(self, content: str, count: int = 5) -> list[dict]:
        """Generate MCQs using OpenAI Structured Outputs (response_format)."""
        prompt = f"""You are a UPSC Prelims question setter. Based on the following current affairs content,
generate exactly {count} high-quality MCQ questions suitable for UPSC Civil Services Preliminary Examination.

Requirements:
- Questions should test conceptual understanding, not mere recall
- Options should be plausible and well-crafted
- Include a mix of difficulty levels (easy, medium, hard)
- Explanations should cite specific facts from the content
- Follow UPSC pattern: statement-based, assertion-reason, or matching type

Content:
{content[:4000]}

Generate exactly {count} questions."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "mcq_questions",
                        "strict": True,
                        "schema": MCQ_SCHEMA,
                    },
                },
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("questions", [])
        except Exception as e:
            logger.exception("MCQ generation failed")
            return []
