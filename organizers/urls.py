from django.urls import path
from .views import OrganizerListCreateView, OrganizerDetailView, MyOrganizerView

urlpatterns = [
    path('events/<int:event_id>/organizers/', OrganizerListCreateView.as_view(), name='organizer-list-create'),
    path('organizers/<int:pk>/', OrganizerDetailView.as_view(), name='organizer-detail'),
    path('organizers/me/', MyOrganizerView.as_view(), name='organizer-me'),
]
