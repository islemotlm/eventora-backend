from django.urls import path
from .views import AttestationDownloadView

urlpatterns = [
    path('attestations/<int:registration_id>/', AttestationDownloadView.as_view(), name='attestation-download'),
]
