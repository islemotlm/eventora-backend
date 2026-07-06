from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from events.models import Event
from participants.models import Registration
from accounts.models import User
from events.permissions import IsClientUser, IsAdminUser


class EventStatsView(APIView):
    permission_classes = [IsClientUser]

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id, client=request.user)
        regs = Registration.objects.filter(event=event)
        total = regs.count()
        present = regs.filter(is_present=True).count()
        return Response({
            'total_registrations': total,
            'present_count': present,
            'absent_count': total - present,
            'capacity': event.max_capacity,
            'fill_rate': round(total / event.max_capacity * 100, 1) if event.max_capacity else 0,
            'presence_rate': round(present / total * 100, 1) if total else 0,
        })


class ClientDashboardStatsView(APIView):
    permission_classes = [IsClientUser]

    def get(self, request):
        events = Event.objects.filter(client=request.user)
        reg_per_event = []
        for e in events:
            total = e.registrations.count()
            present = e.registrations.filter(is_present=True).count()
            reg_per_event.append({
                'event_id': e.id,
                'event_title': e.title,
                'total': total,
                'present': present,
            })
        return Response({
            'total_events': events.count(),
            'approved_events': events.filter(status='approved').count(),
            'pending_events': events.filter(status='pending').count(),
            'registrations_per_event': reg_per_event,
        })


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            'total_events': Event.objects.count(),
            'pending_events': Event.objects.filter(status='pending').count(),
            'approved_events': Event.objects.filter(status='approved').count(),
            'rejected_events': Event.objects.filter(status='rejected').count(),
            'total_users': User.objects.count(),
            'total_registrations': Registration.objects.count(),
        })
