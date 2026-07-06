from rest_framework import serializers
from .models import Speaker


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ['id', 'event', 'first_name', 'last_name', 'title', 'cv_image', 'photo', 'schedule_time']
        read_only_fields = ['id', 'event']
