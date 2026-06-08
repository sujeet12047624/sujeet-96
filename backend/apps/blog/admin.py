from django.contrib import admin

from .models import BlogPost, MCQQuestion


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "gs_paper", "is_published", "is_premium", "published_at")
    list_filter = ("category", "gs_paper", "is_published", "is_premium")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"


@admin.register(MCQQuestion)
class MCQQuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "correct_option", "difficulty", "quiz_date")
    list_filter = ("difficulty", "quiz_date")
