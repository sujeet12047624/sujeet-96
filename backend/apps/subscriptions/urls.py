"""Subscription URL routes."""

from django.urls import path

from . import views

app_name = "subscriptions"

urlpatterns = [
    path("plans/", views.SubscriptionPlanView.as_view(), name="plans"),
    path("me/", views.UserSubscriptionView.as_view(), name="user-subscription"),
    path("transactions/", views.TransactionHistoryView.as_view(), name="transactions"),
]
