from django.urls import path
from .views import (
    EventListCreateView, EventDetailView, EventDetailByIdView,
    ApproveEventView, RejectEventView, EventPublicDetailView,
    PlanListView, ClientPaymentCreateView, ClientPaymentStatusView,
    AdminPaymentListView, AdminApprovePaymentView, AdminRejectPaymentView
)

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('events/<int:pk>/detail/', EventDetailByIdView.as_view(), name='event-detail-by-id'),
    path('events/<int:pk>/approve/', ApproveEventView.as_view(), name='event-approve'),
    path('events/<int:pk>/reject/', RejectEventView.as_view(), name='event-reject'),
    path('public/events/<slug:slug>/', EventPublicDetailView.as_view(), name='event-public-detail'),

    # Plans
    path('plans/', PlanListView.as_view(), name='plan-list'),

    # Client payments — multiple URL aliases to cover all frontend calls
    path('payments/', ClientPaymentCreateView.as_view(), name='payment-create'),
    path('payments/status/', ClientPaymentStatusView.as_view(), name='payment-status'),
    path('client/payment-status/', ClientPaymentStatusView.as_view(), name='client-payment-status'),

    # Admin payment management
    path('admin/payments/', AdminPaymentListView.as_view(), name='admin-payment-list'),
    path('admin/payments/<int:pk>/approve/', AdminApprovePaymentView.as_view(), name='admin-payment-approve'),
    path('admin/payments/<int:pk>/reject/', AdminRejectPaymentView.as_view(), name='admin-payment-reject'),
]
