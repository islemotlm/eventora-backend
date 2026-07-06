from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from events.models import Event
from events.permissions import IsClientUser
from .models import Sponsor
from .serializers import SponsorSerializer


class SponsorListCreateView(generics.ListCreateAPIView):
    serializer_class = SponsorSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsClientUser()]

    def get_queryset(self):
        return Sponsor.objects.filter(event_id=self.kwargs['event_id'])

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'])
        serializer.save(event=event)


class SponsorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SponsorSerializer
    queryset = Sponsor.objects.all()
    permission_classes = [IsClientUser]
