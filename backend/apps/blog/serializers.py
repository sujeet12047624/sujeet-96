"""Blog serializers for API responses."""

from rest_framework import serializers

from .models import BlogPost, MCQQuestion


class BlogPostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = BlogPost
        fields = (
            "id",
            "title",
            "slug",
            "author_name",
            "excerpt",
            "featured_image",
            "category",
            "gs_paper",
            "micro_topics",
            "is_premium",
            "views_count",
            "published_at",
            "created_at",
        )


class BlogPostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = BlogPost
        fields = (
            "id",
            "title",
            "slug",
            "author_name",
            "content",
            "excerpt",
            "featured_image",
            "category",
            "gs_paper",
            "micro_topics",
            "is_premium",
            "views_count",
            "published_at",
            "created_at",
            "updated_at",
        )


class BlogPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = (
            "title",
            "content",
            "excerpt",
            "featured_image",
            "category",
            "gs_paper",
            "is_published",
            "is_premium",
        )


class MCQQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQQuestion
        fields = (
            "id",
            "question",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
            "explanation",
            "difficulty",
            "quiz_date",
        )
