from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Event, Plan, ClientPayment
from .serializers import EventSerializer, EventCreateSerializer, PlanSerializer, ClientPaymentSerializer
from .permissions import IsAdminUser, IsClientUser, IsEventOwner
from speakers.serializers import SpeakerSerializer
from sponsors.serializers import SponsorSerializer


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class EventListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'admin':
                return Event.objects.all()
            elif user.role == 'client':
                return Event.objects.filter(client=user)
        return Event.objects.filter(status='approved')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventCreateSerializer
        return EventSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsClientUser()]

    def perform_create(self, serializer):
        user = self.request.user
        payment = ClientPayment.objects.filter(client=user, status='approved', is_used=False).first()
        if not payment:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'You must have an approved payment to create an event.'})
        event = serializer.save(client=user, plan=payment.plan)
        payment.is_used = True
        payment.save()


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'

    def get_queryset(self):
        return Event.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EventCreateSerializer
        return EventSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsEventOwner()]


class EventDetailByIdView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EventCreateSerializer
        return EventSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class ApproveEventView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.status = 'approved'
        event.save()
        return Response(EventSerializer(event, context={'request': request}).data)


class RejectEventView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.status = 'rejected'
        event.save()
        return Response(EventSerializer(event, context={'request': request}).data)


class EventPublicDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        user = request.user
        if event.status != 'approved':
            if not user.is_authenticated:
                return Response({'detail': 'Not found.'}, status=404)
            if user.role not in ('admin',) and event.client_id != user.id:
                return Response({'detail': 'Not found.'}, status=404)
        data = EventSerializer(event, context={'request': request}).data
        data['speakers'] = SpeakerSerializer(event.speakers.all(), many=True, context={'request': request}).data
        data['sponsors'] = SponsorSerializer(event.sponsors.all(), many=True, context={'request': request}).data
        return Response(data)


class ClientPaymentCreateView(generics.CreateAPIView):
    queryset = ClientPayment.objects.all()
    serializer_class = ClientPaymentSerializer
    permission_classes = [IsClientUser]
    parser_classes = [MultiPartParser, FormParser]  # Required for file uploads

    def perform_create(self, serializer):
        serializer.save(client=self.request.user, status='pending', is_used=False)


class ClientPaymentStatusView(APIView):
    permission_classes = [IsClientUser]

    def get(self, request):
        # Priority 1: Return an approved, unused payment — this is what grants event creation.
        # This handles the case where a client submitted multiple payments; the approved
        # one may not be the most recent.
        payment = (
            ClientPayment.objects.filter(client=request.user, status='approved', is_used=False)
            .order_by('-created_at')
            .first()
        )

        # Priority 2: Fall back to the most recent payment for status display
        # (covers pending / rejected / already-used states)
        if not payment:
            payment = (
                ClientPayment.objects.filter(client=request.user)
                .order_by('-created_at')
                .first()
            )

        if payment:
            data = ClientPaymentSerializer(payment, context={'request': request}).data
            # Explicit permission flag — frontend checks this to allow event creation
            data['can_create_event'] = (payment.status == 'approved' and not payment.is_used)
            return Response(data)
        return Response({'detail': 'No payment found.'}, status=404)


class AdminPaymentListView(generics.ListAPIView):
    queryset = ClientPayment.objects.all().order_by('-created_at')
    serializer_class = ClientPaymentSerializer
    permission_classes = [IsAdminUser]
    # Note: generic views automatically pass request in context, so receipt_image URL is absolute


class AdminApprovePaymentView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        payment = get_object_or_404(ClientPayment, pk=pk)
        payment.status = 'approved'
        payment.save()
        # Pass request in context so receipt_image returns a full absolute URL
        return Response(ClientPaymentSerializer(payment, context={'request': request}).data)


class AdminRejectPaymentView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        payment = get_object_or_404(ClientPayment, pk=pk)
        payment.status = 'rejected'
        payment.save()
        # Pass request in context so receipt_image returns a full absolute URL
        return Response(ClientPaymentSerializer(payment, context={'request': request}).data)
