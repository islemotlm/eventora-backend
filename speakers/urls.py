from django.urls import path
from .views import SpeakerListCreateView, SpeakerDetailView

urlpatterns = [
    path('events/<int:event_id>/speakers/', SpeakerListCreateView.as_view(), name='speaker-list-create'),
    path('speakers/<int:pk>/', SpeakerDetailView.as_view(), name='speaker-detail'),
]
