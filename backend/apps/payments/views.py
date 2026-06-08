"""Payment views: order creation and webhook handlers."""

import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from services.payments.razorpay_service import RazorpayService
from services.payments.stripe_service import StripeService

logger = logging.getLogger(__name__)


class CreateRazorpayOrderView(APIView):
    """Create a Razorpay order for subscription payment."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        service = RazorpayService()
        result = service.create_order(request.user)
        if result.get("error"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_201_CREATED)


class CreateStripeSessionView(APIView):
    """Create a Stripe Checkout session for international payments."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        service = StripeService()
        result = service.create_checkout_session(
            user=request.user,
            success_url=request.data.get("success_url", "http://localhost:3000/pricing?success=true"),
            cancel_url=request.data.get("cancel_url", "http://localhost:3000/pricing?cancelled=true"),
        )
        if result.get("error"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_201_CREATED)


class RazorpayWebhookView(APIView):
    """
    Idempotent webhook handler for Razorpay payment events.
    Verifies cryptographic signature before processing.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        service = RazorpayService()
        result = service.handle_webhook(
            payload=request.body,
            signature=request.headers.get("X-Razorpay-Signature", ""),
        )
        if result.get("error"):
            logger.error("Razorpay webhook error: %s", result["error"])
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class StripeWebhookView(APIView):
    """
    Idempotent webhook handler for Stripe payment events.
    Verifies webhook signature before processing.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        service = StripeService()
        result = service.handle_webhook(
            payload=request.body,
            sig_header=request.headers.get("Stripe-Signature", ""),
        )
        if result.get("error"):
            logger.error("Stripe webhook error: %s", result["error"])
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)
