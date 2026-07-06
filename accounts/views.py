from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from events.permissions import IsAdminUser


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminUsersView(generics.ListAPIView):
    """Admin: list all users with optional search and status filter."""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = User.objects.all().order_by('-date_joined')
        params = self.request.query_params

        status_filter = params.get('status', '')
        if status_filter == 'pending':
            qs = qs.filter(is_active=False)
        elif status_filter == 'active':
            qs = qs.filter(is_active=True)

        role_filter = params.get('role', '')
        if role_filter:
            qs = qs.filter(role=role_filter)

        search = params.get('search', '')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search) |
                Q(role__icontains=search)
            )
        return qs


class AdminUserDetailView(APIView):
    """Admin: update (activate, change role) or delete a user."""
    permission_classes = [IsAdminUser]

    ALLOWED_ROLES = {'admin', 'client', 'organizer', 'participant'}

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        updated_fields = []

        if 'is_active' in request.data:
            user.is_active = bool(request.data.get('is_active'))
            updated_fields.append('is_active')

        if 'role' in request.data:
            role = request.data.get('role')
            if role not in self.ALLOWED_ROLES:
                return Response({'role': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)
            user.role = role
            updated_fields.append('role')

        for field in ('first_name', 'last_name', 'email', 'phone'):
            if field in request.data:
                setattr(user, field, request.data.get(field) or '')
                updated_fields.append(field)

        if updated_fields:
            user.save(update_fields=updated_fields)
        return Response(UserSerializer(user).data)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.pk == request.user.pk:
            return Response(
                {'detail': "You can't delete your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminPendingUsersView(generics.ListAPIView):
    """Admin: list accounts awaiting approval (is_active=False)."""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(is_active=False).order_by('-date_joined')


class AdminApproveUserView(APIView):
    """Admin: approve a pending user in one action."""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response(UserSerializer(user).data)


class AvailableOrganizersView(generics.ListAPIView):
    """Client: list active users with role=organizer to pick from when assigning."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(role='organizer', is_active=True).order_by('first_name', 'last_name')
