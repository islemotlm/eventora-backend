from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import secrets

from events.models import Event
from events.permissions import IsClientUser
from accounts.models import User
from .models import Organizer
from .serializers import OrganizerSerializer


class OrganizerListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizerSerializer
    permission_classes = [IsClientUser]

    def get_queryset(self):
        return Organizer.objects.filter(event_id=self.kwargs['event_id'])

    def create(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'])
        data = request.data
        user_id = data.get('user_id')

        if user_id:
            # Assign an existing organizer user to this event
            user = get_object_or_404(User, pk=user_id, role='organizer', is_active=True)
            if Organizer.objects.filter(event=event, user=user).exists():
                return Response(
                    {'detail': 'This organizer is already assigned to this event.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            organizer = Organizer.objects.create(
                event=event,
                user=user,
                door_number=data.get('door_number', ''),
                work_schedule=data.get('work_schedule', ''),
            )
            return Response(OrganizerSerializer(organizer).data, status=status.HTTP_201_CREATED)

        # No user_id: create a brand-new organizer account and send credentials
        password = secrets.token_urlsafe(10)
        username = data.get('email', '').split('@')[0] + secrets.token_hex(3)
        user = User.objects.create_user(
            username=username,
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            password=password,
            role='organizer',
        )
        organizer = Organizer.objects.create(
            event=event,
            user=user,
            door_number=data.get('door_number', ''),
            work_schedule=data.get('work_schedule', ''),
        )
        # Send HTML credentials email
        try:
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:3000')
            login_url = f"{base_url}/login"
            html_body = render_to_string('emails/organizer_credentials_email.html', {
                'organizer_name': user.first_name or user.username,
                'organizer_email': user.email,
                'temp_password': password,
                'event': event,
                'login_url': login_url,
                'base_url': getattr(settings, 'MEDIA_BASE_URL', 'http://localhost:8000'),
                'year': timezone.now().year,
            })
            plain_body = (
                f"Hello {user.first_name},\n\n"
                f"You have been assigned as organizer for '{event.title}'.\n\n"
                f"Email: {user.email}\n"
                f"Temporary Password: {password}\n\n"
                f"Door: {organizer.door_number}\n"
                f"Schedule: {organizer.work_schedule}\n\n"
                f"Login at: {login_url}\n\n"
                f"For security, please change your password upon first login.\n\nEventora"
            )
            msg = EmailMultiAlternatives(
                subject=f"Your Eventora organizer credentials for {event.title}",
                body=plain_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=True)
        except Exception:
            pass
        return Response(OrganizerSerializer(organizer).data, status=status.HTTP_201_CREATED)


class OrganizerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizerSerializer
    queryset = Organizer.objects.all()
    permission_classes = [IsClientUser]


class MyOrganizerView(generics.RetrieveAPIView):
    serializer_class = OrganizerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Organizer, user=self.request.user)
