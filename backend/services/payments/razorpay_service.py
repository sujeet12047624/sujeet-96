"""Razorpay payment service – order creation and webhook processing."""

import hashlib
import hmac
import json
import logging
from datetime import timedelta

import razorpay
from django.conf import settings
from django.utils import timezone

from apps.subscriptions.models import Subscription, Transaction

logger = logging.getLogger(__name__)


class RazorpayService:
    """Handles Razorpay order lifecycle: creation, verification, subscription activation."""

    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET

    def create_order(self, user):
        """Create a Razorpay order for the Premium Access Tier."""
        try:
            order_data = {
                "amount": int(settings.SUBSCRIPTION_PRICE_INR * 100),  # paise
                "currency": "INR",
                "receipt": f"sub_{user.id}_{int(timezone.now().timestamp())}",
                "notes": {
                    "user_id": str(user.id),
                    "email": user.email,
                    "plan": "Premium Access Tier",
                },
            }
            order = self.client.order.create(data=order_data)

            Transaction.objects.create(
                user=user,
                provider=Transaction.Provider.RAZORPAY,
                provider_order_id=order["id"],
                amount_inr=settings.SUBSCRIPTION_PRICE_INR,
                status=Transaction.Status.PENDING,
                metadata={"razorpay_order": order},
            )

            return {
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "key_id": settings.RAZORPAY_KEY_ID,
            }
        except Exception as e:
            logger.exception("Razorpay order creation failed")
            return {"error": str(e)}

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Cryptographic signature verification using HMAC-SHA256."""
        expected = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def handle_webhook(self, payload: bytes, signature: str):
        """Process Razorpay webhook events idempotently."""
        if not self._verify_signature(payload, signature):
            return {"error": "Invalid webhook signature."}

        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON payload."}

        event_type = event.get("event")

        if event_type == "order.paid":
            return self._handle_order_paid(event)
        elif event_type == "payment.failed":
            return self._handle_payment_failed(event)

        return {"status": "ignored", "event": event_type}

    def _handle_order_paid(self, event):
        """Activate or extend subscription on successful payment."""
        payment_entity = event["payload"]["payment"]["entity"]
        order_id = payment_entity.get("order_id")
        payment_id = payment_entity.get("id")

        try:
            transaction = Transaction.objects.get(provider_order_id=order_id)
        except Transaction.DoesNotExist:
            logger.warning("Transaction not found for order %s", order_id)
            return {"error": "Transaction not found."}

        # Idempotency check
        if transaction.status == Transaction.Status.SUCCESS:
            return {"status": "already_processed"}

        transaction.provider_payment_id = payment_id
        transaction.status = Transaction.Status.SUCCESS
        transaction.metadata["payment_entity"] = payment_entity
        transaction.save()

        self._activate_subscription(transaction.user, transaction)
        return {"status": "success", "order_id": order_id}

    def _handle_payment_failed(self, event):
        """Mark transaction as failed."""
        payment_entity = event["payload"]["payment"]["entity"]
        order_id = payment_entity.get("order_id")

        try:
            transaction = Transaction.objects.get(provider_order_id=order_id)
            transaction.status = Transaction.Status.FAILED
            transaction.metadata["failure_reason"] = payment_entity.get("error_description")
            transaction.save()
        except Transaction.DoesNotExist:
            pass

        return {"status": "payment_failed"}

    def _activate_subscription(self, user, transaction):
        """Create or extend subscription for exactly 90 days."""
        now = timezone.now()
        duration = timedelta(days=settings.SUBSCRIPTION_DURATION_DAYS)

        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                "start_date": now,
                "end_date": now + duration,
                "status": Subscription.Status.ACTIVE,
                "price_inr": settings.SUBSCRIPTION_PRICE_INR,
            },
        )

        if not created:
            # Extend from current end_date if still active, otherwise from now
            base = subscription.end_date if subscription.is_active else now
            subscription.start_date = now if not subscription.is_active else subscription.start_date
            subscription.end_date = base + duration
            subscription.status = Subscription.Status.ACTIVE
            subscription.save()

        transaction.subscription = subscription
        transaction.save()

        # Update user premium flag
        user.is_premium = True
        user.save(update_fields=["is_premium"])

        logger.info("Subscription activated for %s until %s", user.email, subscription.end_date)
