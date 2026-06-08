"""Custom DRF permission: gates premium endpoints to active subscribers."""

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsActiveSubscriber(BasePermission):
    """
    Allow access only to users with a currently active subscription.
    Dynamically checks timezone.now() <= subscription.end_date.
    Returns 403 with a payload pointing to the subscription route.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            raise PermissionDenied(
                detail={
                    "error": "Authentication required for premium features.",
                    "subscription_url": "/api/subscriptions/plans/",
                    "pricing_page": "/pricing",
                }
            )

        subscription = getattr(user, "subscription", None)
        if subscription is None or not subscription.is_active:
            raise PermissionDenied(
                detail={
                    "error": "Active subscription required. Your subscription is expired or not found.",
                    "subscription_url": "/api/subscriptions/plans/",
                    "pricing_page": "/pricing",
                    "plan": "Premium Access Tier – ₹500 for 90 days",
                }
            )

        return True
