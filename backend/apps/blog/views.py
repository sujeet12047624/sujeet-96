"""Blog API views – fully public for free content, gated for premium."""

import logging
from datetime import date

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_features.tasks import auto_tag_blog_post

from .models import BlogPost, MCQQuestion
from .serializers import (
    BlogPostCreateSerializer,
    BlogPostDetailSerializer,
    BlogPostListSerializer,
    MCQQuestionSerializer,
)

logger = logging.getLogger(__name__)


class BlogPostListView(generics.ListAPIView):
    """Public: list published blog posts with filtering, search, ordering."""

    serializer_class = BlogPostListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "gs_paper", "is_premium"]
    search_fields = ["title", "content", "micro_topics"]
    ordering_fields = ["published_at", "views_count", "created_at"]
    ordering = ["-published_at"]

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).select_related("author")


class BlogPostDetailView(generics.RetrieveAPIView):
    """Public: retrieve single blog post by slug (increments view count)."""

    serializer_class = BlogPostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).select_related("author")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        BlogPost.objects.filter(pk=instance.pk).update(views_count=instance.views_count + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BlogPostCreateView(generics.CreateAPIView):
    """Authenticated: create a new blog post (triggers async AI tagging)."""

    serializer_class = BlogPostCreateSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # Fire async AI auto-tagging
        auto_tag_blog_post.delay(post.id)


class DailyQuizView(APIView):
    """Public: return today's MCQ quiz (5 questions)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        quiz_date = request.query_params.get("date", str(date.today()))
        questions = MCQQuestion.objects.filter(quiz_date=quiz_date)[:5]
        serializer = MCQQuestionSerializer(questions, many=True)
        return Response(
            {"date": quiz_date, "questions": serializer.data},
            status=status.HTTP_200_OK,
        )


class CategoryListView(APIView):
    """Public: return available categories and GS papers."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from .models import Category, GSPaper

        return Response(
            {
                "categories": [{"value": c.value, "label": c.label} for c in Category],
                "gs_papers": [{"value": g.value, "label": g.label} for g in GSPaper],
            }
        )
