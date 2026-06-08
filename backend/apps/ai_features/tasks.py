"""Celery tasks for async AI operations."""

import json
import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def auto_tag_blog_post(self, post_id: int):
    """Asynchronously analyze and tag a blog post with UPSC syllabus mapping."""
    try:
        from services.ai.syllabus_tagger import SyllabusMapper

        from apps.blog.models import BlogPost

        post = BlogPost.objects.get(id=post_id)
        mapper = SyllabusMapper()
        result = mapper.map_to_syllabus(post.title, post.content)

        if result.get("gs_paper"):
            post.gs_paper = result["gs_paper"]
        if result.get("micro_topics"):
            post.micro_topics = result["micro_topics"]
        post.save(update_fields=["gs_paper", "micro_topics"])

        logger.info("Auto-tagged post %d: GS=%s, topics=%s", post_id, post.gs_paper, post.micro_topics)
    except Exception as exc:
        logger.exception("Auto-tag failed for post %d", post_id)
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def generate_daily_mcq_quiz(self):
    """Generate 5 UPSC-style MCQs from recent current affairs posts."""
    try:
        from services.ai.mcq_generator import MCQGenerator

        from apps.blog.models import BlogPost, MCQQuestion

        today = date.today()

        existing = MCQQuestion.objects.filter(quiz_date=today).count()
        if existing >= 5:
            logger.info("Daily MCQ quiz already generated for %s", today)
            return

        recent_posts = BlogPost.objects.filter(
            category="current_affairs",
            is_published=True,
        ).order_by("-published_at")[:5]

        if not recent_posts:
            logger.warning("No current affairs posts found for MCQ generation.")
            return

        combined_content = "\n\n".join(
            f"Title: {p.title}\n{p.content[:2000]}" for p in recent_posts
        )

        generator = MCQGenerator()
        questions = generator.generate_mcqs(combined_content, count=5)

        for q in questions:
            MCQQuestion.objects.create(
                question=q["question"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                option_c=q["option_c"],
                option_d=q["option_d"],
                correct_option=q["correct_option"],
                explanation=q["explanation"],
                difficulty=q.get("difficulty", "medium"),
                quiz_date=today,
                blog_post=recent_posts.first(),
            )

        logger.info("Generated %d MCQs for %s", len(questions), today)
    except Exception as exc:
        logger.exception("Daily MCQ generation failed")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def ingest_document_to_vector_store(self, document_text: str, metadata: dict):
    """Chunk, embed, and upsert document into Qdrant vector store."""
    try:
        from services.ai.rag_engine import RAGEngine

        engine = RAGEngine()
        engine.ingest_text(document_text, metadata)
        logger.info("Document ingested to vector store: %s", metadata.get("title", "unknown"))
    except Exception as exc:
        logger.exception("Document ingestion failed")
        self.retry(exc=exc)


def evaluate_answer_sync(question: str, answer: str, gs_paper: str = ""):
    """Synchronous streaming wrapper for answer evaluation (called from view)."""
    from services.ai.answer_evaluator import AnswerEvaluator

    evaluator = AnswerEvaluator()
    return evaluator.evaluate_streaming(question, answer, gs_paper)


def semantic_search_sync(query: str, top_k: int = 5):
    """Synchronous wrapper for semantic search (called from view)."""
    from services.ai.rag_engine import RAGEngine

    engine = RAGEngine()
    return engine.search(query, top_k)
