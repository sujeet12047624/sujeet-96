"""Stripe payment service – session creation and webhook processing."""

import json
import logging
from datetime import timedelta

import stripe
from django.conf import settings
from django.utils import timezone

from apps.subscriptions.models import Subscription, Transaction

logger = logging.getLogger(__name__)


class StripeService:
    """Handles Stripe Checkout lifecycle: session creation and webhook processing."""

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    def create_checkout_session(self, user, success_url: str, cancel_url: str):
        """Create a Stripe Checkout session for international card payments."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": "UPSC Premium Access Tier",
                                "description": "90-day premium access with AI features",
                            },
                            "unit_amount": int(settings.SUBSCRIPTION_PRICE_INR * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user.id),
                customer_email=user.email,
                metadata={
                    "user_id": str(user.id),
                    "plan": "Premium Access Tier",
                },
            )

            Transaction.objects.create(
                user=user,
                provider=Transaction.Provider.STRIPE,
                provider_order_id=session.id,
                amount_inr=settings.SUBSCRIPTION_PRICE_INR,
                status=Transaction.Status.PENDING,
                metadata={"stripe_session_id": session.id},
            )

            return {
                "session_id": session.id,
                "url": session.url,
            }
        except Exception as e:
            logger.exception("Stripe session creation failed")
            return {"error": str(e)}

    def handle_webhook(self, payload: bytes, sig_header: str):
        """Process Stripe webhook events with signature verification."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
        except stripe.error.SignatureVerificationError:
            return {"error": "Invalid webhook signature."}
        except Exception as e:
            return {"error": str(e)}

        if event["type"] == "checkout.session.completed":
            return self._handle_checkout_completed(event["data"]["object"])
        elif event["type"] == "payment_intent.payment_failed":
            return self._handle_payment_failed(event["data"]["object"])

        return {"status": "ignored", "event_type": event["type"]}

    def _handle_checkout_completed(self, session):
        """Activate subscription on successful Stripe checkout."""
        session_id = session["id"]
        user_id = session.get("client_reference_id") or session["metadata"].get("user_id")

        try:
            transaction = Transaction.objects.get(provider_order_id=session_id)
        except Transaction.DoesNotExist:
            logger.warning("Transaction not found for session %s", session_id)
            return {"error": "Transaction not found."}

        # Idempotency
        if transaction.status == Transaction.Status.SUCCESS:
            return {"status": "already_processed"}

        transaction.provider_payment_id = session.get("payment_intent", "")
        transaction.status = Transaction.Status.SUCCESS
        transaction.metadata["session_completed"] = True
        transaction.save()

        self._activate_subscription(transaction.user, transaction)
        return {"status": "success", "session_id": session_id}

    def _handle_payment_failed(self, payment_intent):
        """Mark transaction as failed on Stripe payment failure."""
        session_id = payment_intent.get("id", "")
        try:
            transaction = Transaction.objects.filter(
                provider=Transaction.Provider.STRIPE,
                provider_payment_id=session_id,
            ).first()
            if transaction:
                transaction.status = Transaction.Status.FAILED
                transaction.save()
        except Exception:
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
            base = subscription.end_date if subscription.is_active else now
            subscription.start_date = now if not subscription.is_active else subscription.start_date
            subscription.end_date = base + duration
            subscription.status = Subscription.Status.ACTIVE
            subscription.save()

        transaction.subscription = subscription
        transaction.save()

        user.is_premium = True
        user.save(update_fields=["is_premium"])

        logger.info("Stripe subscription activated for %s until %s", user.email, subscription.end_date)
