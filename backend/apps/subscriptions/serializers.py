"""Subscription serializers."""

from rest_framework import serializers

from .models import Subscription, Transaction


class SubscriptionSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "plan_name",
            "price_inr",
            "start_date",
            "end_date",
            "status",
            "is_active",
            "days_remaining",
            "created_at",
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id",
            "provider",
            "provider_order_id",
            "provider_payment_id",
            "amount_inr",
            "currency",
            "status",
            "created_at",
        )


class SubscriptionPlanSerializer(serializers.Serializer):
    """Static plan info for display."""

    name = serializers.CharField(default="Premium Access Tier")
    price_inr = serializers.IntegerField(default=500)
    duration_days = serializers.IntegerField(default=90)
    features = serializers.ListField(
        child=serializers.CharField(),
        default=[
            "AI Mains Answer Evaluator (Claude 3.5 Sonnet)",
            "Semantic RAG Search across UPSC corpus",
            "Personalized study recommendations",
            "Priority support",
        ],
    )
