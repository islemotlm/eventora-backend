from django.urls import path
from .views import (
    RegisterForEventView, EventRegistrationsView,
    MyRegistrationsView, MyRegistrationDetailView,
    ValidateRegistrationView, ValidateByTokenView,
    AdminRegistrationsView, ApprovePaymentView, RejectPaymentView,
    RegisterExhibitorStandView, AdminExhibitorStandsView,
    ApproveExhibitorPaymentView, RejectExhibitorPaymentView, MyExhibitorStandsView,
    ClientEventRegistrationsView, ClientApprovePaymentView, ClientRejectPaymentView,
    ClientEventExhibitorStandsView, ClientApproveExhibitorPaymentView, ClientRejectExhibitorPaymentView,
)

urlpatterns = [
    path('events/<int:event_id>/register/', RegisterForEventView.as_view(), name='event-register'),
    path('events/<int:event_id>/registrations/', EventRegistrationsView.as_view(), name='event-registrations'),
    path('my-registrations/', MyRegistrationsView.as_view(), name='my-registrations'),
    path('my-registrations/<int:pk>/', MyRegistrationDetailView.as_view(), name='my-registration-detail'),
    path('registrations/<int:pk>/validate/', ValidateRegistrationView.as_view(), name='validate-registration'),
    path('registrations/validate-token/', ValidateByTokenView.as_view(), name='validate-by-token'),
    # Admin – participants
    path('admin/registrations/', AdminRegistrationsView.as_view(), name='admin-registrations'),
    path('admin/registrations/<int:pk>/approve/', ApprovePaymentView.as_view(), name='approve-payment'),
    path('admin/registrations/<int:pk>/reject/', RejectPaymentView.as_view(), name='reject-payment'),
    # Exhibitor stands
    path('events/<int:event_id>/exhibitor/register/', RegisterExhibitorStandView.as_view(), name='exhibitor-register'),
    path('my-exhibitor-stands/', MyExhibitorStandsView.as_view(), name='my-exhibitor-stands'),
    # Admin – exhibitor stands
    path('admin/exhibitor-stands/', AdminExhibitorStandsView.as_view(), name='admin-exhibitor-stands'),
    path('admin/exhibitor-stands/<int:pk>/approve/', ApproveExhibitorPaymentView.as_view(), name='approve-exhibitor-payment'),
    path('admin/exhibitor-stands/<int:pk>/reject/', RejectExhibitorPaymentView.as_view(), name='reject-exhibitor-payment'),
    # Client – own event registrations & payment approval
    path('client/events/<int:event_id>/registrations/', ClientEventRegistrationsView.as_view(), name='client-event-registrations'),
    path('client/registrations/<int:pk>/approve/', ClientApprovePaymentView.as_view(), name='client-approve-payment'),
    path('client/registrations/<int:pk>/reject/', ClientRejectPaymentView.as_view(), name='client-reject-payment'),
    path('client/events/<int:event_id>/exhibitor-stands/', ClientEventExhibitorStandsView.as_view(), name='client-event-exhibitor-stands'),
    path('client/exhibitor-stands/<int:pk>/approve/', ClientApproveExhibitorPaymentView.as_view(), name='client-approve-exhibitor'),
    path('client/exhibitor-stands/<int:pk>/reject/', ClientRejectExhibitorPaymentView.as_view(), name='client-reject-exhibitor'),
]
