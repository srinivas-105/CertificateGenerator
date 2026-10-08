from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)


def _fit_font_size(text: str, font_name: str, max_size: int, max_width: float) -> int:
    size = max_size
    while size > 12 and stringWidth(text, font_name, size) > max_width:
        size -= 1
    return size


def draw_certificate(
    output_path: Path,
    organization_name: str,
    course_name: str,
    recipient_name: str,
    issue_date: date,
) -> None:
    canvas_obj = canvas.Canvas(str(output_path), pagesize=landscape(A4))

    margin = 28
    canvas_obj.setStrokeColor(colors.HexColor("#263238"))
    canvas_obj.setLineWidth(2)
    canvas_obj.rect(margin, margin, PAGE_WIDTH - 2 * margin, PAGE_HEIGHT - 2 * margin)

    canvas_obj.setStrokeColor(colors.HexColor("#9E9E9E"))
    canvas_obj.setLineWidth(0.7)
    canvas_obj.rect(margin + 10, margin + 10, PAGE_WIDTH - 2 * (margin + 10), PAGE_HEIGHT - 2 * (margin + 10))

    center_x = PAGE_WIDTH / 2

    canvas_obj.setFillColor(colors.HexColor("#263238"))
    organization_size = _fit_font_size(organization_name.upper(), "Helvetica-Bold", 22, PAGE_WIDTH - 180)
    canvas_obj.setFont("Helvetica-Bold", organization_size)
    canvas_obj.drawCentredString(center_x, PAGE_HEIGHT - 90, organization_name.upper())

    canvas_obj.setFillColor(colors.HexColor("#455A64"))
    canvas_obj.setFont("Helvetica-Bold", 25)
    canvas_obj.drawCentredString(center_x, PAGE_HEIGHT - 140, "CERTIFICATE OF COMPLETION")

    canvas_obj.setFillColor(colors.black)
    canvas_obj.setFont("Helvetica", 13)
    canvas_obj.drawCentredString(center_x, PAGE_HEIGHT - 185, "This certificate is presented to")

    recipient_size = _fit_font_size(recipient_name, "Helvetica-Bold", 30, PAGE_WIDTH - 180)
    canvas_obj.setFillColor(colors.HexColor("#111111"))
    canvas_obj.setFont("Helvetica-Bold", recipient_size)
    canvas_obj.drawCentredString(center_x, PAGE_HEIGHT - 235, recipient_name)

    canvas_obj.setFillColor(colors.black)
    canvas_obj.setFont("Helvetica", 12)
    canvas_obj.drawCentredString(center_x, PAGE_HEIGHT - 275, "for successfully completing the course")

    course_size = _fit_font_size(course_name.upper(), "Helvetica-Bold", 18, PAGE_WIDTH - 180)
    canvas_obj.setFillColor(colors.HexColor("#455A64"))
    canvas_obj.setFont("Helvetica-Bold", course_size)
    canvas_obj.drawCentredString(center_x, PAGE_HEIGHT - 315, course_name.upper())

    canvas_obj.setFillColor(colors.black)
    canvas_obj.setFont("Helvetica", 11)
    canvas_obj.drawCentredString(center_x, PAGE_HEIGHT - 350, issue_date.strftime("%d %B %Y"))

    signature_y = 78
    left_x = PAGE_WIDTH * 0.30
    right_x = PAGE_WIDTH * 0.70
    canvas_obj.setStrokeColor(colors.HexColor("#555555"))
    canvas_obj.line(left_x - 75, signature_y, left_x + 75, signature_y)
    canvas_obj.line(right_x - 75, signature_y, right_x + 75, signature_y)

    canvas_obj.setFillColor(colors.black)
    canvas_obj.setFont("Helvetica", 10)
    canvas_obj.drawCentredString(left_x, signature_y - 17, "Instructor")
    canvas_obj.drawCentredString(right_x, signature_y - 17, "Director")

    canvas_obj.save()
