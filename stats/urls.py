from django.urls import path
from .views import EventStatsView, ClientDashboardStatsView, AdminDashboardStatsView

urlpatterns = [
    path('events/<int:event_id>/stats/', EventStatsView.as_view(), name='event-stats'),
    path('client/stats/', ClientDashboardStatsView.as_view(), name='client-stats'),
    path('admin/dashboard/', AdminDashboardStatsView.as_view(), name='admin-dashboard'),
]
