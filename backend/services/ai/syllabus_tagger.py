"""Syllabus-Mapping AI Auto-Tagger using OpenAI GPT-4o."""

import json
import logging

import openai
from django.conf import settings

logger = logging.getLogger(__name__)

UPSC_SYLLABUS_MATRIX = {
    "gs1": {
        "label": "GS Paper 1",
        "topics": [
            "Indian Heritage and Culture",
            "History of the World",
            "Modern Indian History",
            "Indian Society",
            "Social Empowerment",
            "Communalism, Regionalism & Secularism",
            "World Geography",
            "Distribution of Key Natural Resources",
            "Geophysical Phenomena",
        ],
    },
    "gs2": {
        "label": "GS Paper 2",
        "topics": [
            "Indian Constitution",
            "Functions and Responsibilities of the Union and the States",
            "Parliament and State Legislatures",
            "Judiciary",
            "Governance",
            "Social Justice",
            "International Relations",
            "Important International Institutions",
            "Bilateral, Regional and Global Groupings",
        ],
    },
    "gs3": {
        "label": "GS Paper 3",
        "topics": [
            "Indian Economy",
            "Planning and Mobilization of Resources",
            "Inclusive Growth",
            "Government Budgeting",
            "Agriculture",
            "Food Processing",
            "Science and Technology",
            "Space Technology",
            "Environment and Ecology",
            "Biodiversity",
            "Internal Security",
            "Disaster Management",
        ],
    },
    "gs4": {
        "label": "GS Paper 4 (Ethics)",
        "topics": [
            "Ethics and Human Interface",
            "Attitude",
            "Aptitude and Foundational Values",
            "Emotional Intelligence",
            "Public/Civil Service Values",
            "Probity in Governance",
            "Case Studies on Ethics",
        ],
    },
}


class SyllabusMapper:
    """Maps blog post content to UPSC GS Papers and micro-topics."""

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def map_to_syllabus(self, title: str, content: str) -> dict:
        """Analyze text and return gs_paper + micro_topics."""
        syllabus_context = json.dumps(UPSC_SYLLABUS_MATRIX, indent=2)
        prompt = f"""You are a UPSC syllabus expert. Analyze the following blog post and map it to:
1. The most relevant GS Paper (gs1, gs2, gs3, or gs4)
2. Up to 5 specific micro-topics from the UPSC syllabus

UPSC Syllabus Reference:
{syllabus_context}

Blog Post Title: {title}
Blog Post Content (first 3000 chars): {content[:3000]}

Respond ONLY with valid JSON in this exact format:
{{"gs_paper": "gs1|gs2|gs3|gs4", "micro_topics": ["topic1", "topic2"]}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            return {
                "gs_paper": result.get("gs_paper", ""),
                "micro_topics": result.get("micro_topics", []),
            }
        except Exception as e:
            logger.exception("Syllabus mapping failed")
            return {"gs_paper": "", "micro_topics": [], "error": str(e)}
