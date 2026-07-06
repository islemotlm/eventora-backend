from django.contrib import admin
from .models import Registration, ExhibitorStand


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['participant', 'event', 'payment_status', 'is_present', 'registered_at']
    list_filter = ['payment_status', 'is_present']
    search_fields = ['participant__username', 'participant__email', 'event__title']
    readonly_fields = ['payment_receipt_link']

    def payment_receipt_link(self, obj):
        if obj.payment_receipt:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank">View Receipt</a>', obj.payment_receipt.url)
        return '—'
    payment_receipt_link.short_description = 'Receipt'

    actions = ['approve_payments', 'reject_payments']

    def approve_payments(self, request, queryset):
        queryset.update(payment_status='approved')
    approve_payments.short_description = 'Approve selected payments'

    def reject_payments(self, request, queryset):
        queryset.update(payment_status='rejected')
    reject_payments.short_description = 'Reject selected payments'


@admin.register(ExhibitorStand)
class ExhibitorStandAdmin(admin.ModelAdmin):
    list_display = ['exhibitor', 'company_name', 'event', 'stand_type', 'price', 'payment_status', 'registered_at']
    list_filter = ['payment_status', 'stand_type']
    search_fields = ['exhibitor__username', 'exhibitor__email', 'company_name', 'event__title']
    readonly_fields = ['price', 'payment_receipt_link']

    def price(self, obj):
        return f"DZD {obj.price:,}"
    price.short_description = 'Price'

    def payment_receipt_link(self, obj):
        if obj.payment_receipt:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank">View Receipt</a>', obj.payment_receipt.url)
        return '—'
    payment_receipt_link.short_description = 'Receipt'

    actions = ['approve_payments', 'reject_payments']

    def approve_payments(self, request, queryset):
        queryset.update(payment_status='approved')
    approve_payments.short_description = 'Approve selected stand payments'

    def reject_payments(self, request, queryset):
        queryset.update(payment_status='rejected')
    reject_payments.short_description = 'Reject selected stand payments'
