from django.contrib import admin
from .models import Event, Plan, ClientPayment

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'status', 'date', 'theme', 'plan']
    list_filter = ['status', 'theme']
    search_fields = ['title', 'client__username']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']

@admin.register(ClientPayment)
class ClientPaymentAdmin(admin.ModelAdmin):
    list_display = ['client', 'plan', 'status', 'is_used', 'created_at']
    list_filter = ['status', 'is_used', 'plan']
    search_fields = ['client__username']
