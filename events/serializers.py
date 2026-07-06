from rest_framework import serializers
from .models import Event, Plan, ClientPayment
from accounts.serializers import UserSerializer

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price', 'features']

class ClientPaymentSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    plan_details = PlanSerializer(source='plan', read_only=True)

    class Meta:
        model = ClientPayment
        fields = ['id', 'client', 'plan', 'plan_details', 'receipt_image', 'status', 'is_used', 'created_at']
        read_only_fields = ['id', 'client', 'status', 'is_used', 'created_at']

class EventSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    registrations_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location', 'max_capacity',
            'logo', 'theme', 'status', 'slug', 'client', 'plan', 'created_at', 'updated_at',
            'registrations_count', 'ticket_type', 'price', 'ccp_number',
        ]
        read_only_fields = ['id', 'slug', 'client', 'plan', 'status', 'created_at', 'updated_at']

    def get_registrations_count(self, obj):
        return obj.registrations.count()


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'location', 'max_capacity', 'logo', 'theme', 'slug', 'status', 'ticket_type', 'price', 'ccp_number', 'plan']
        read_only_fields = ['id', 'slug', 'status', 'plan']
