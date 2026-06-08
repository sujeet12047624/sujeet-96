"""Subscription model with precise time-bound tracking."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Subscription(models.Model):
    """Tracks premium subscription with explicit start/end dates."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan_name = models.CharField(max_length=100, default="Premium Access Tier")
    price_inr = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"

    @property
    def is_active(self):
        """Dynamically compute whether the subscription is still valid."""
        return self.status == self.Status.ACTIVE and timezone.now() <= self.end_date

    @property
    def days_remaining(self):
        if not self.is_active:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)

    def __str__(self):
        return f"{self.user.email} – {self.plan_name} ({self.status})"


class Transaction(models.Model):
    """Payment transaction ledger for audit trail."""

    class Provider(models.TextChoices):
        RAZORPAY = "razorpay", "Razorpay"
        STRIPE = "stripe", "Stripe"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions",
    )
    provider = models.CharField(max_length=20, choices=Provider.choices)
    provider_order_id = models.CharField(max_length=255, unique=True, db_index=True)
    provider_payment_id = models.CharField(max_length=255, blank=True)
    amount_inr = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider} – {self.provider_order_id} – {self.status}"
