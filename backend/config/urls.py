"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/blog/", include("apps.blog.urls")),
    path("api/subscriptions/", include("apps.subscriptions.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/ai/", include("apps.ai_features.urls")),
]
