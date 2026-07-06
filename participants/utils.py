from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.conf import settings
import os


def generate_ticket_pdf(registration):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'EventoraTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor('#6C47FF'),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0F0E17'),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#444444'),
        spaceAfter=4,
        alignment=TA_CENTER,
    )

    story.append(Paragraph("EVENTORA", title_style))
    story.append(Paragraph("Event Ticket", heading_style))
    story.append(Spacer(1, 0.5*cm))

    event = registration.event
    participant = registration.participant

    data = [
        ['Event:', event.title],
        ['Participant:', f"{participant.first_name} {participant.last_name}"],
        ['Date:', event.date.strftime('%B %d, %Y at %H:%M')],
        ['Location:', event.location],
        ['Token:', str(registration.token)],
    ]
    table = Table(data, colWidths=[5*cm, 11*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F7F6FF')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6C47FF')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F7F6FF')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
        ('ROUNDEDCORNERS', [4]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(table)
    story.append(Spacer(1, 1*cm))

    if registration.qr_code:
        qr_path = os.path.join(settings.MEDIA_ROOT, registration.qr_code.name)
        if os.path.exists(qr_path):
            story.append(Paragraph("Scan to validate presence", body_style))
            story.append(Spacer(1, 0.3*cm))
            qr_img = Image(qr_path, width=5*cm, height=5*cm)
            qr_img.hAlign = 'CENTER'
            story.append(qr_img)

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Thank you for participating!", body_style))

    doc.build(story)
    buf.seek(0)
    return buf
