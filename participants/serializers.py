from rest_framework import serializers
from accounts.serializers import UserSerializer
from events.serializers import EventSerializer
from .models import Registration, ExhibitorStand


class RegistrationSerializer(serializers.ModelSerializer):
    participant = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id', 'event', 'participant', 'token', 'qr_code',
            'is_present', 'registered_at', 'ticket_sent',
            'payment_receipt', 'payment_status',
        ]
        read_only_fields = ['id', 'token', 'qr_code', 'registered_at', 'ticket_sent']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        plan = instance.event.plan
        if plan is not None and plan.name.lower() == 'medium':
            representation['qr_code'] = None  # Ensure QR is hidden for Medium plan
        return representation


class RegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['id', 'event', 'token', 'qr_code', 'is_present', 'registered_at', 'payment_receipt', 'payment_status']
        read_only_fields = ['id', 'token', 'qr_code', 'is_present', 'registered_at', 'payment_status']


class ExhibitorStandSerializer(serializers.ModelSerializer):
    exhibitor = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    price = serializers.ReadOnlyField()

    class Meta:
        model = ExhibitorStand
        fields = [
            'id', 'event', 'exhibitor', 'stand_type', 'company_name',
            'payment_receipt', 'payment_status', 'price', 'registered_at',
        ]
        read_only_fields = ['id', 'payment_status', 'registered_at']
