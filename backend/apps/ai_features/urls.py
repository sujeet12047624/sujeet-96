"""AI features URL routes."""

from django.urls import path

from . import views

app_name = "ai_features"

urlpatterns = [
    path("evaluate/", views.AnswerEvaluatorView.as_view(), name="evaluate-answer"),
    path("search/", views.SemanticSearchView.as_view(), name="semantic-search"),
    path("health/", views.HealthCheckView.as_view(), name="health"),
]
