"""AI feature views: answer evaluation (premium), RAG search (premium), MCQ generation."""

import logging

from django.http import StreamingHttpResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscriptions.permissions import IsActiveSubscriber

from .serializers import AnswerEvaluationSerializer, RAGSearchSerializer
from .tasks import evaluate_answer_sync, semantic_search_sync

logger = logging.getLogger(__name__)


class AnswerEvaluatorView(APIView):
    """
    PREMIUM: Evaluate UPSC Mains answer using Claude 3.5 Sonnet.
    Returns streaming JSON with score, rubric breakdown, and model draft.
    """

    permission_classes = [permissions.IsAuthenticated, IsActiveSubscriber]

    def post(self, request):
        serializer = AnswerEvaluationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        answer = serializer.validated_data["answer"]
        gs_paper = serializer.validated_data.get("gs_paper", "")

        def event_stream():
            try:
                for chunk in evaluate_answer_sync(question, answer, gs_paper):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.exception("Answer evaluation streaming error")
                yield f'data: {{"error": "{str(e)}"}}\n\n'

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class SemanticSearchView(APIView):
    """
    PREMIUM: RAG-powered semantic search across UPSC blog corpus.
    Returns ranked results with relevance scores and source citations.
    """

    permission_classes = [permissions.IsAuthenticated, IsActiveSubscriber]

    def post(self, request):
        serializer = RAGSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]
        top_k = serializer.validated_data.get("top_k", 5)

        results = semantic_search_sync(query, top_k)
        return Response(results, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    """Public: AI service health check."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "ai_features"})
