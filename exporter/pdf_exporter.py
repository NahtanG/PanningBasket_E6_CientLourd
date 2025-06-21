# exporter/pdf_exporter.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_trainings_to_pdf(trainings, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 40
    c.setFont("Helvetica", 12)
    for t in trainings:
        line = f"{t.date.strftime('%d/%m')} - {t.start_time.strftime('%H:%M')}–{t.end_time.strftime('%H:%M')} - {t.description} ({t.category})"
        c.drawString(40, y, line)
        y -= 20
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 40
    c.save()