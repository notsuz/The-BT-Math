from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "student",
        "course",
        "amount",
        "gateway",
        "status",
        "transaction_uuid",
        "created_at",
    ]
    list_filter = ["gateway", "status", "created_at"]
    search_fields = ["student__email", "course__title", "transaction_uuid", "gateway_reference"]
    readonly_fields = ["transaction_uuid", "created_at", "updated_at"]
