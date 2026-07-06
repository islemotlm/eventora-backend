from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math

# Register fonts once at module level
try:
    pdfmetrics.registerFont(TTFont('SerifItalic', '/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf'))
    pdfmetrics.registerFont(TTFont('SerifBold', '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf'))
    pdfmetrics.registerFont(TTFont('Serif', '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'))
    HAVE_SERIF = True
except Exception:
    HAVE_SERIF = False


def _draw_floral_corner(c, cx, cy, scale=1.0, flip_x=False, flip_y=False):
    """Draw a decorative floral/leaf corner ornament."""
    PRIMARY = colors.HexColor('#7B5EA7')
    c.saveState()
    c.translate(cx, cy)
    if flip_x:
        c.scale(-1, 1)
    if flip_y:
        c.scale(1, -1)
    c.scale(scale, scale)

    c.setStrokeColor(PRIMARY)
    c.setFillColor(PRIMARY)
    c.setLineWidth(0.6)

    # Main stem
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(8, 8, 18, 16, 28, 28)
    c.drawPath(p, stroke=1, fill=0)

    # Leaves along the stem
    leaf_positions = [
        (5, 5, 10, 14, 2, 10),
        (12, 12, 22, 20, 8, 18),
        (20, 20, 30, 26, 16, 26),
    ]
    for (sx, sy, cpx, cpy, ex, ey) in leaf_positions:
        p = c.beginPath()
        p.moveTo(sx, sy)
        p.curveTo(cpx, cpy + 6, ex + 4, ey, ex, ey)
        p.curveTo(ex - 4, ey, cpx - 4, cpy - 2, sx, sy)
        c.drawPath(p, stroke=0, fill=1)

    # Branch arms
    branches = [
        ((6, 6), (14, 18), (10, 22)),
        ((14, 14), (20, 26), (18, 30)),
        ((22, 22), (26, 34), (24, 38)),
    ]
    for start, cp, end in branches:
        p = c.beginPath()
        p.moveTo(*start)
        p.curveTo(cp[0], cp[1], end[0], end[1], end[0], end[1])
        c.drawPath(p, stroke=1, fill=0)
        # small leaf at end
        p = c.beginPath()
        p.moveTo(end[0], end[1])
        p.curveTo(end[0] + 5, end[1] + 4, end[0] + 6, end[1] + 8, end[0] + 2, end[1] + 10)
        p.curveTo(end[0] - 2, end[1] + 8, end[0] - 3, end[1] + 4, end[0], end[1])
        c.drawPath(p, stroke=0, fill=1)

    # Small dots / berries
    for (bx, by) in [(28, 32), (32, 28), (34, 34)]:
        c.circle(bx, by, 1.5, fill=1, stroke=0)

    c.restoreState()


def _draw_wreath(c, cx, cy, radius=10 * mm):
    """Draw a simple decorative laurel wreath."""
    PRIMARY = colors.HexColor('#7B5EA7')
    c.setStrokeColor(PRIMARY)
    c.setFillColor(PRIMARY)
    c.setLineWidth(0.5)

    leaf_count = 10
    for side in [-1, 1]:
        for i in range(leaf_count):
            angle = math.radians(190 + i * 16 * side)
            lx = cx + side * radius * 0.7 * math.cos(angle)
            ly = cy + radius * 0.7 * math.sin(angle)
            p = c.beginPath()
            p.moveTo(lx, ly)
            end_x = lx + side * 5 * math.cos(angle + math.radians(20))
            end_y = ly + 5 * math.sin(angle + math.radians(20))
            p.curveTo(
                lx + side * 4, ly + 4,
                end_x + side * 2, end_y + 2,
                end_x, end_y
            )
            p.curveTo(
                end_x - side * 2, end_y + 2,
                lx - side * 2, ly + 2,
                lx, ly
            )
            c.drawPath(p, fill=1, stroke=0)

    # small star in center
    c.setFillColor(colors.HexColor('#9B7EC8'))
    for i in range(5):
        a = math.radians(i * 72 - 90)
        px = cx + 3 * math.cos(a)
        py = cy + 3 * math.sin(a)
        c.circle(px, py, 0.8, fill=1, stroke=0)


def _draw_signature_scribble(c, x, y, style='a'):
    """Draw a simple handwriting-style signature scribble."""
    c.setStrokeColor(colors.HexColor('#222222'))
    c.setLineWidth(1.2)
    if style == 'a':
        p = c.beginPath()
        p.moveTo(x, y)
        p.curveTo(x + 5, y + 8, x + 10, y - 4, x + 16, y + 6)
        p.curveTo(x + 20, y + 10, x + 22, y - 2, x + 28, y + 2)
        c.drawPath(p, stroke=1, fill=0)
    else:
        p = c.beginPath()
        p.moveTo(x, y + 4)
        p.curveTo(x + 6, y + 12, x + 14, y - 2, x + 20, y + 8)
        p.curveTo(x + 24, y + 13, x + 26, y + 2, x + 30, y + 5)
        p.curveTo(x + 32, y + 7, x + 31, y + 2, x + 34, y + 4)
        c.drawPath(p, stroke=1, fill=0)
        # small heart
        hx, hy = x + 36, y + 8
        p2 = c.beginPath()
        p2.moveTo(hx, hy)
        p2.curveTo(hx + 3, hy + 4, hx + 6, hy + 2, hx + 3, hy - 1)
        p2.curveTo(hx, hy - 3, hx - 3, hy, hx, hy)
        c.drawPath(p2, stroke=1, fill=0)


def generate_attestation_pdf(registration):
    buf = BytesIO()

    # ── Landscape A4 ──────────────────────────────────────────────────────────
    page_w, page_h = landscape(A4)
    c = pdf_canvas.Canvas(buf, pagesize=landscape(A4))

    PRIMARY = colors.HexColor('#7B5EA7')
    PRIMARY_DARK = colors.HexColor('#5C3D8F')
    LAVENDER_BG = colors.HexColor('#EDE8F5')
    LAVENDER_MID = colors.HexColor('#D8CFF0')
    DARK = colors.HexColor('#1A1A2E')
    GRAY = colors.HexColor('#5A5A7A')
    WHITE = colors.white

    event = registration.event
    participant = registration.participant
    full_name = f"{participant.first_name} {participant.last_name}".strip()
    today = date.today()
    reg_id = f"EVT-{today.year}-{str(registration.id).zfill(5)}-AT"

    margin = 14 * mm

    # ── Lavender background ───────────────────────────────────────────────────
    c.setFillColor(LAVENDER_BG)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # ── Soft inner background panel ───────────────────────────────────────────
    c.setFillColor(colors.HexColor('#F4F0FA'))
    c.roundRect(margin, margin, page_w - 2 * margin, page_h - 2 * margin, 6, fill=1, stroke=0)

    # ── Thin border ───────────────────────────────────────────────────────────
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(1.2)
    c.roundRect(margin, margin, page_w - 2 * margin, page_h - 2 * margin, 6, fill=0, stroke=1)

    # ── Thin inner border ────────────────────────────────────────────────────
    inner_m = margin + 4 * mm
    c.setStrokeColor(colors.HexColor('#C3B0E8'))
    c.setLineWidth(0.5)
    c.roundRect(inner_m, inner_m, page_w - 2 * inner_m, page_h - 2 * inner_m, 4, fill=0, stroke=1)

    # ── Floral corner ornaments ───────────────────────────────────────────────
    corner_offset = margin + 2 * mm
    sc = 1.4
    # bottom-left
    _draw_floral_corner(c, corner_offset + 4, corner_offset + 4, scale=sc, flip_x=False, flip_y=False)
    # bottom-right
    _draw_floral_corner(c, page_w - corner_offset - 4, corner_offset + 4, scale=sc, flip_x=True, flip_y=False)
    # top-left
    _draw_floral_corner(c, corner_offset + 4, page_h - corner_offset - 4, scale=sc, flip_x=False, flip_y=True)
    # top-right
    _draw_floral_corner(c, page_w - corner_offset - 4, page_h - corner_offset - 4, scale=sc, flip_x=True, flip_y=True)

    # ── Watermark hand silhouette (subtle background center) ──────────────────
    c.saveState()
    c.setFillColor(colors.HexColor('#DDD4F0'))
    cx_wm, cy_wm = page_w / 2, page_h / 2 + 5 * mm
    # Simple abstract leaf/hand shapes as watermark
    for offset, rotation in [(-18 * mm, -15), (18 * mm, 15)]:
        c.saveState()
        c.translate(cx_wm + offset, cy_wm)
        c.rotate(rotation)
        p = c.beginPath()
        p.moveTo(0, -25 * mm)
        p.curveTo(-8 * mm, -10 * mm, -10 * mm, 10 * mm, 0, 25 * mm)
        p.curveTo(10 * mm, 10 * mm, 8 * mm, -10 * mm, 0, -25 * mm)
        c.drawPath(p, fill=1, stroke=0)
        c.restoreState()
    c.restoreState()

    # ── ATTESTATION title ─────────────────────────────────────────────────────
    title_y = page_h - margin - 22 * mm
    if HAVE_SERIF:
        c.setFont('SerifBold', 34)
    else:
        c.setFont('Helvetica-Bold', 34)
    c.setFillColor(PRIMARY_DARK)
    c.drawCentredString(page_w / 2, title_y, 'ATTESTATION')

    # ── DE RÉUSSITE subtitle ──────────────────────────────────────────────────
    subtitle_y = title_y - 11 * mm
    if HAVE_SERIF:
        c.setFont('Serif', 20)
    else:
        c.setFont('Helvetica', 20)
    c.setFillColor(PRIMARY)
    c.drawCentredString(page_w / 2, subtitle_y, 'DE PARTICIPATION')

    # ── Thin decorative divider ───────────────────────────────────────────────
    div_y = subtitle_y - 6 * mm
    c.setStrokeColor(LAVENDER_MID)
    c.setLineWidth(0.8)
    c.line(page_w / 2 - 50 * mm, div_y, page_w / 2 + 50 * mm, div_y)
    # small diamond center
    c.setFillColor(PRIMARY)
    c.saveState()
    c.translate(page_w / 2, div_y)
    c.rotate(45)
    c.rect(-2, -2, 4, 4, fill=1, stroke=0)
    c.restoreState()

    # ── "Ce diplôme est fièrement décerné à" ──────────────────────────────────
    awarded_y = div_y - 10 * mm
    if HAVE_SERIF:
        c.setFont('SerifItalic', 12)
    else:
        c.setFont('Helvetica-Oblique', 12)
    c.setFillColor(GRAY)
    c.drawCentredString(page_w / 2, awarded_y, "Ce diplôme est fièrement décerné à")

    # ── Participant name in cursive-style italic ───────────────────────────────
    name_y = awarded_y - 16 * mm
    if HAVE_SERIF:
        c.setFont('SerifItalic', 38)
    else:
        c.setFont('Helvetica-BoldOblique', 38)
    c.setFillColor(PRIMARY_DARK)
    c.drawCentredString(page_w / 2, name_y, full_name)

    # ── Description text ──────────────────────────────────────────────────────
    desc_y = name_y - 12 * mm
    event_date_str = event.date.strftime('%d %B %Y')
    desc_text = (
        f"pour avoir participé à l'événement <b>{event.title}</b>, "
        f"tenu le {event_date_str} à {event.location}."
    )
    desc_style = ParagraphStyle(
        'desc',
        fontName='Helvetica',
        fontSize=10.5,
        textColor=GRAY,
        alignment=TA_CENTER,
        leading=16,
    )
    para = Paragraph(desc_text, desc_style)
    para.wrapOn(c, 150 * mm, 30 * mm)
    para.drawOn(c, (page_w - 150 * mm) / 2, desc_y - 14 * mm)

    # ── "Fait à" / "Le" line ──────────────────────────────────────────────────
    fait_y = desc_y - 28 * mm
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 9)
    # left
    c.drawString(page_w / 2 - 80 * mm, fait_y, 'Fait à')
    c.setStrokeColor(colors.HexColor('#C0B8D8'))
    c.setLineWidth(0.6)
    c.line(page_w / 2 - 68 * mm, fait_y - 1, page_w / 2 - 20 * mm, fait_y - 1)
    # right
    c.drawString(page_w / 2 + 4 * mm, fait_y, 'Le')
    c.line(page_w / 2 + 14 * mm, fait_y - 1, page_w / 2 + 68 * mm, fait_y - 1)

    # ── Signature area ────────────────────────────────────────────────────────
    sig_y = fait_y - 14 * mm
    sig_left_cx = page_w / 2 - 55 * mm
    sig_right_cx = page_w / 2 + 55 * mm

    # Left signature
    _draw_signature_scribble(c, sig_left_cx - 14 * mm, sig_y + 4 * mm, style='a')
    c.setStrokeColor(colors.HexColor('#C0B8D8'))
    c.setLineWidth(0.6)
    c.line(sig_left_cx - 20 * mm, sig_y, sig_left_cx + 20 * mm, sig_y)
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(sig_left_cx, sig_y - 5 * mm, 'DIRECTRICE DE L\'ACADÉMIE')
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 8)
    c.drawCentredString(sig_left_cx, sig_y - 10 * mm, 'Organisatrice')

    # Center wreath
    _draw_wreath(c, page_w / 2, sig_y - 3 * mm, radius=9 * mm)

    # Right signature
    _draw_signature_scribble(c, sig_right_cx - 14 * mm, sig_y + 4 * mm, style='b')
    c.setStrokeColor(colors.HexColor('#C0B8D8'))
    c.setLineWidth(0.6)
    c.line(sig_right_cx - 20 * mm, sig_y, sig_right_cx + 20 * mm, sig_y)
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(sig_right_cx, sig_y - 5 * mm, 'FORMATRICE')
    c.setFillColor(GRAY)
    c.setFont('Helvetica', 8)
    c.drawCentredString(sig_right_cx, sig_y - 10 * mm, 'Responsable Formation')

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_y = margin + 5 * mm
    c.setFillColor(colors.HexColor('#A090C0'))
    c.setFont('Helvetica', 7)
    c.drawString(margin + 8 * mm, footer_y, f"Généré le {today.strftime('%d %B %Y')}   •   ID: {reg_id}")
    c.setFillColor(PRIMARY)
    c.setFont('Helvetica-Bold', 8)
    c.drawRightString(page_w - margin - 8 * mm, footer_y, 'eventora.com')

    c.save()
    buf.seek(0)
    return buf


# ── Demo / test ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    from types import SimpleNamespace
    from datetime import date as dt

    reg = SimpleNamespace(
        id=42,
        participant=SimpleNamespace(first_name='Clara', last_name='Carpentier'),
        event=SimpleNamespace(
            title='Programme Intensif de Prothésie Ongulaire',
            date=dt(2025, 6, 14),
            location='Paris'
        )
    )

    buf = generate_attestation_pdf(reg)
    with open('/mnt/user-data/outputs/attestation_demo.pdf', 'wb') as f:
        f.write(buf.read())
    print('PDF written to /mnt/user-data/outputs/attestation_demo.pdf')
