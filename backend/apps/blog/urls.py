"""Blog URL routes."""

from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("posts/", views.BlogPostListView.as_view(), name="post-list"),
    path("posts/create/", views.BlogPostCreateView.as_view(), name="post-create"),
    path("posts/<slug:slug>/", views.BlogPostDetailView.as_view(), name="post-detail"),
    path("quiz/", views.DailyQuizView.as_view(), name="daily-quiz"),
    path("categories/", views.CategoryListView.as_view(), name="categories"),
]
