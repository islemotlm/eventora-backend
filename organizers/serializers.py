from rest_framework import serializers
from django.utils import timezone
from accounts.serializers import UserSerializer
from events.serializers import EventSerializer
from .models import Organizer


class OrganizerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    validated_today = serializers.SerializerMethodField()
    validated_total = serializers.SerializerMethodField()
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = Organizer
        fields = [
            'id', 'event', 'user', 'door_number', 'work_schedule',
            'validated_today', 'validated_total',
            'first_name', 'last_name', 'email',
        ]
        read_only_fields = ['id', 'event', 'user', 'validated_today', 'validated_total']

    def get_validated_today(self, obj):
        if not obj.event_id:
            return 0
        from participants.models import Registration
        today = timezone.localdate()
        return Registration.objects.filter(
            event_id=obj.event_id,
            is_present=True,
            registered_at__date=today,
        ).count()

    def get_validated_total(self, obj):
        if not obj.event_id:
            return 0
        from participants.models import Registration
        return Registration.objects.filter(
            event_id=obj.event_id,
            is_present=True,
        ).count()
