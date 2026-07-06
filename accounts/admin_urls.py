from django.urls import path
from .views import (
    AdminUsersView,
    AdminUserDetailView,
    AdminPendingUsersView,
    AdminApproveUserView,
)

urlpatterns = [
    path('admin/users/', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/pending/', AdminPendingUsersView.as_view(), name='admin-users-pending'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<int:pk>/approve/', AdminApproveUserView.as_view(), name='admin-user-approve'),
]
