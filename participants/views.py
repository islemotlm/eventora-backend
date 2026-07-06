from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from events.models import Event
from events.permissions import IsClientUser, IsOrganizerUser, IsAdminUser
from .models import Registration, ExhibitorStand
from .serializers import RegistrationSerializer, RegistrationCreateSerializer, ExhibitorStandSerializer
from .utils import generate_ticket_pdf


class RegisterForEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id, status='approved')
        if Registration.objects.filter(event=event, participant=request.user).exists():
            return Response({'detail': 'Already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        if event.registrations.count() >= event.max_capacity:
            return Response({'detail': 'Event is full.'}, status=status.HTTP_400_BAD_REQUEST)

        payment_receipt = request.FILES.get('payment_receipt')
        # For free events, auto-approve; for paid events, set pending
        initial_payment_status = 'pending'
        if event.ticket_type == 'free':
            initial_payment_status = 'approved'

        reg = Registration.objects.create(
            event=event,
            participant=request.user,
            payment_receipt=payment_receipt,
            payment_status=initial_payment_status,
        )

        # Send ticket PDF + HTML email
        try:
            pdf_buf = generate_ticket_pdf(reg)
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            html_body = render_to_string('emails/ticket_email.html', {
                'event': event,
                'participant': request.user,
                'registration': reg,
                'base_url': base_url,
                'year': timezone.now().year,
            })
            plain_body = (
                f"Hello {request.user.first_name},\n\n"
                f"Your ticket for {event.title} is attached.\n\n"
                f"Date: {event.date.strftime('%B %d, %Y')}\n"
                f"Location: {event.location}\n\n"
                f"See you there!\n\nEventora"
            )
            msg = EmailMultiAlternatives(
                subject=f"Your ticket for {event.title}",
                body=plain_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[request.user.email],
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.attach(f"ticket_{event.slug}.pdf", pdf_buf.read(), 'application/pdf')
            msg.send(fail_silently=True)
            reg.ticket_sent = True
            reg.save(update_fields=['ticket_sent'])
        except Exception:
            pass

        return Response(RegistrationSerializer(reg).data, status=status.HTTP_201_CREATED)


class EventRegistrationsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsClientUser]

    def get_queryset(self):
        return Registration.objects.filter(event_id=self.kwargs['event_id']).select_related('participant', 'event')


class MyRegistrationsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(participant=self.request.user).select_related('event')


class MyRegistrationDetailView(generics.RetrieveAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(participant=self.request.user).select_related('event')


class ValidateRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        reg = get_object_or_404(Registration, pk=pk)
        if request.user.role not in ('organizer', 'admin', 'client'):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        reg.is_present = True
        reg.save(update_fields=['is_present'])
        return Response(RegistrationSerializer(reg).data)


class ValidateByTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'detail': 'Token required.'}, status=status.HTTP_400_BAD_REQUEST)
        reg = get_object_or_404(Registration, token=token)

        # Only admins, the event owner, or an organizer assigned to this event
        # can check in participants.
        user = request.user
        allowed = False
        if user.role == 'admin':
            allowed = True
        elif user.role == 'client' and reg.event.client_id == user.id:
            allowed = True
        elif user.role == 'organizer':
            from organizers.models import Organizer
            allowed = Organizer.objects.filter(event=reg.event, user=user).exists()

        if not allowed:
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        if reg.payment_status != 'approved':
            return Response(
                {'detail': 'Payment not approved yet. Participant cannot be checked in.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if reg.is_present:
            return Response({'detail': 'Already checked in.'}, status=status.HTTP_400_BAD_REQUEST)
        reg.is_present = True
        reg.save(update_fields=['is_present'])
        return Response({
            'detail': 'Validated successfully.',
            'participant': reg.participant.get_full_name(),
            'event': reg.event.title,
        })


# ── Admin-only registration management ───────────────────────────────────────

class AdminRegistrationsView(generics.ListAPIView):
    """Admin can list all registrations, optionally filtered by event."""
    serializer_class = RegistrationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = Registration.objects.select_related('participant', 'event').order_by('-registered_at')
        event_id = self.request.query_params.get('event_id')
        payment_status = self.request.query_params.get('payment_status')
        if event_id:
            qs = qs.filter(event_id=event_id)
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        return qs


class ApprovePaymentView(APIView):
    """Admin approves a participant's payment/registration."""
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        reg = get_object_or_404(Registration, pk=pk)
        reg.payment_status = 'approved'
        reg.save(update_fields=['payment_status'])
        return Response(RegistrationSerializer(reg).data)


class RejectPaymentView(APIView):
    """Admin rejects a participant's payment/registration."""
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        reg = get_object_or_404(Registration, pk=pk)
        reg.payment_status = 'rejected'
        reg.save(update_fields=['payment_status'])
        return Response(RegistrationSerializer(reg).data)


# ── Exhibitor stand registration ─────────────────────────────────────────────

class RegisterExhibitorStandView(APIView):
    """Authenticated users register for an exhibitor stand at an event."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id, status='approved')
        if ExhibitorStand.objects.filter(event=event, exhibitor=request.user).exists():
            return Response({'detail': 'Already registered as exhibitor.'}, status=status.HTTP_400_BAD_REQUEST)

        stand_type = request.data.get('stand_type')
        if stand_type not in ('minimum', 'standard', 'premium'):
            return Response({'detail': 'Invalid stand type.'}, status=status.HTTP_400_BAD_REQUEST)

        company_name = request.data.get('company_name', '').strip()
        if not company_name:
            return Response({'detail': 'Company name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        payment_receipt = request.FILES.get('payment_receipt')
        if not payment_receipt:
            return Response({'detail': 'Payment receipt is required.'}, status=status.HTTP_400_BAD_REQUEST)

        stand = ExhibitorStand.objects.create(
            event=event,
            exhibitor=request.user,
            stand_type=stand_type,
            company_name=company_name,
            payment_receipt=payment_receipt,
        )
        return Response(ExhibitorStandSerializer(stand).data, status=status.HTTP_201_CREATED)


class AdminExhibitorStandsView(generics.ListAPIView):
    """Admin lists all exhibitor stand registrations, optionally filtered by event."""
    serializer_class = ExhibitorStandSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = ExhibitorStand.objects.select_related('exhibitor', 'event').order_by('-registered_at')
        event_id = self.request.query_params.get('event_id')
        payment_status = self.request.query_params.get('payment_status')
        if event_id:
            qs = qs.filter(event_id=event_id)
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        return qs


class ApproveExhibitorPaymentView(APIView):
    """Admin approves an exhibitor stand payment."""
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        stand = get_object_or_404(ExhibitorStand, pk=pk)
        stand.payment_status = 'approved'
        stand.save(update_fields=['payment_status'])
        return Response(ExhibitorStandSerializer(stand).data)


class RejectExhibitorPaymentView(APIView):
    """Admin rejects an exhibitor stand payment."""
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        stand = get_object_or_404(ExhibitorStand, pk=pk)
        stand.payment_status = 'rejected'
        stand.save(update_fields=['payment_status'])
        return Response(ExhibitorStandSerializer(stand).data)


class MyExhibitorStandsView(generics.ListAPIView):
    """Authenticated user views their own exhibitor stand registrations."""
    serializer_class = ExhibitorStandSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExhibitorStand.objects.filter(exhibitor=self.request.user).select_related('event')


# ── Client payment management (own events only) ───────────────────────────────

class ClientEventRegistrationsView(generics.ListAPIView):
    """Client lists registrations for one of their own events."""
    serializer_class = RegistrationSerializer
    permission_classes = [IsClientUser]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'], client=self.request.user)
        qs = Registration.objects.filter(event=event).select_related('participant', 'event').order_by('-registered_at')
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        return qs


class ClientApprovePaymentView(APIView):
    permission_classes = [IsClientUser]

    def patch(self, request, pk):
        reg = get_object_or_404(Registration, pk=pk, event__client=request.user)
        reg.payment_status = 'approved'
        reg.save(update_fields=['payment_status'])
        return Response(RegistrationSerializer(reg).data)


class ClientRejectPaymentView(APIView):
    permission_classes = [IsClientUser]

    def patch(self, request, pk):
        reg = get_object_or_404(Registration, pk=pk, event__client=request.user)
        reg.payment_status = 'rejected'
        reg.save(update_fields=['payment_status'])
        return Response(RegistrationSerializer(reg).data)


class ClientEventExhibitorStandsView(generics.ListAPIView):
    """Client lists exhibitor stands for one of their own events."""
    serializer_class = ExhibitorStandSerializer
    permission_classes = [IsClientUser]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'], client=self.request.user)
        qs = ExhibitorStand.objects.filter(event=event).select_related('exhibitor', 'event').order_by('-registered_at')
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        return qs


class ClientApproveExhibitorPaymentView(APIView):
    permission_classes = [IsClientUser]

    def patch(self, request, pk):
        stand = get_object_or_404(ExhibitorStand, pk=pk, event__client=request.user)
        stand.payment_status = 'approved'
        stand.save(update_fields=['payment_status'])
        return Response(ExhibitorStandSerializer(stand).data)


class ClientRejectExhibitorPaymentView(APIView):
    permission_classes = [IsClientUser]

    def patch(self, request, pk):
        stand = get_object_or_404(ExhibitorStand, pk=pk, event__client=request.user)
        stand.payment_status = 'rejected'
        stand.save(update_fields=['payment_status'])
        return Response(ExhibitorStandSerializer(stand).data)
