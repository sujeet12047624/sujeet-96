"""Payment URL routes."""

from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("razorpay/create-order/", views.CreateRazorpayOrderView.as_view(), name="razorpay-create"),
    path("stripe/create-session/", views.CreateStripeSessionView.as_view(), name="stripe-create"),
    path("webhook/razorpay/", views.RazorpayWebhookView.as_view(), name="razorpay-webhook"),
    path("webhook/stripe/", views.StripeWebhookView.as_view(), name="stripe-webhook"),
]
