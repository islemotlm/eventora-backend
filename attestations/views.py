from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from participants.models import Registration
from .utils import generate_attestation_pdf


class AttestationDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, registration_id):
        reg = get_object_or_404(Registration, pk=registration_id)
        user = request.user
        if user.role not in ('admin', 'client') and reg.participant != user:
            return Response({'detail': 'Forbidden.'}, status=403)
        if not reg.is_present:
            return Response({'detail': 'Attestation only available for participants who attended.'}, status=400)

        pdf_buf = generate_attestation_pdf(reg)

        # Send attestation notification email (fire-and-forget)
        try:
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:3000')
            download_url = f"{base_url}/api/attestations/{registration_id}/"
            html_body = render_to_string('emails/attestation_email.html', {
                'participant': reg.participant,
                'event': reg.event,
                'download_url': download_url,
                'year': timezone.now().year,
            })
            plain_body = (
                f"Hello {reg.participant.first_name},\n\n"
                f"Your attestation of participation for '{reg.event.title}' is ready.\n\n"
                f"Download: {download_url}\n\nEventora"
            )
            msg = EmailMultiAlternatives(
                subject=f"Your attestation for {reg.event.title} is ready",
                body=plain_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[reg.participant.email],
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=True)
        except Exception:
            pass

        response = HttpResponse(pdf_buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="attestation_{registration_id}.pdf"'
        return response
