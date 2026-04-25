from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency']
    readonly_fields = ['stripe_session_id', 'stripe_payment_intent']
