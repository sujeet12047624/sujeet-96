"""Blog models: posts, categories, tags, and quiz questions."""

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.TextChoices):
    PRELIMS = "prelims", "Prelims"
    MAINS = "mains", "Mains"
    CURRENT_AFFAIRS = "current_affairs", "Current Affairs"
    EDITORIAL = "editorial", "Editorial Analysis"


class GSPaper(models.TextChoices):
    GS1 = "gs1", "GS Paper 1"
    GS2 = "gs2", "GS Paper 2"
    GS3 = "gs3", "GS Paper 3"
    GS4 = "gs4", "GS Paper 4 (Ethics)"
    ESSAY = "essay", "Essay"


class BlogPost(models.Model):
    """Core blog post with UPSC-specific categorization."""

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    featured_image = models.ImageField(upload_to="blog/images/", blank=True)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.MAINS,
        db_index=True,
    )
    gs_paper = models.CharField(
        max_length=10,
        choices=GSPaper.choices,
        blank=True,
        db_index=True,
    )
    micro_topics = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-generated micro-topic tags from UPSC syllabus.",
    )
    is_published = models.BooleanField(default=False, db_index=True)
    is_premium = models.BooleanField(
        default=False,
        help_text="If True, content is restricted to active subscribers.",
    )
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "blog_posts"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["category", "is_published"]),
            models.Index(fields=["gs_paper", "is_published"]),
            models.Index(fields=["-published_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            base_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        if not self.excerpt and self.content:
            self.excerpt = self.content[:497] + "..."
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class MCQQuestion(models.Model):
    """UPSC-style MCQ auto-generated from blog content."""

    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="mcq_questions",
        null=True,
        blank=True,
    )
    question = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
    )
    explanation = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        default="medium",
    )
    quiz_date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mcq_questions"
        ordering = ["-quiz_date", "-created_at"]

    def __str__(self):
        return self.question[:80]
