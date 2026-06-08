"""Subscription views: plan info, user subscription status, transaction history."""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription, Transaction
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    TransactionSerializer,
)


class SubscriptionPlanView(APIView):
    """Public: display available subscription plans."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        plan = SubscriptionPlanSerializer({}).data
        return Response({"plans": [plan]})


class UserSubscriptionView(APIView):
    """Authenticated: get current user's subscription status."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            subscription = request.user.subscription
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {"message": "No active subscription found.", "is_active": False},
                status=status.HTTP_200_OK,
            )


class TransactionHistoryView(generics.ListAPIView):
    """Authenticated: list user's payment transaction history."""

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
