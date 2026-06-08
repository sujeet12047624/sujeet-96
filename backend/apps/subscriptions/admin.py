from django.contrib import admin

from .models import Subscription, Transaction


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan_name", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("user__email",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "amount_inr", "status", "created_at")
    list_filter = ("provider", "status")
    search_fields = ("user__email", "provider_order_id")
