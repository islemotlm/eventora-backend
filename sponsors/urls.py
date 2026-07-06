from django.urls import path
from .views import SponsorListCreateView, SponsorDetailView

urlpatterns = [
    path('events/<int:event_id>/sponsors/', SponsorListCreateView.as_view(), name='sponsor-list-create'),
    path('sponsors/<int:pk>/', SponsorDetailView.as_view(), name='sponsor-detail'),
]
