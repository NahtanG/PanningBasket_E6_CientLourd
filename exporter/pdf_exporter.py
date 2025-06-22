from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_trainings_to_pdf(trainings, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    # Titre
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, "Planning des Entraînements")
    y -= 30

    # En-tête de tableau
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Date")
    c.drawString(margin + 100, y, "Heure")
    c.drawString(margin + 200, y, "Catégorie")
    c.drawString(margin + 300, y, "Description")
    y -= 20

    # Corps du tableau
    c.setFont("Helvetica", 11)
    for t in trainings:
        date_str = t.date.strftime('%d/%m/%Y')
        hour_str = f"{t.start_time.strftime('%H:%M')} – {t.end_time.strftime('%H:%M')}"
        c.drawString(margin, y, date_str)
        c.drawString(margin + 100, y, hour_str)
        c.drawString(margin + 200, y, t.category)
        c.drawString(margin + 300, y, t.description)
        y -= 18
        if y < margin:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - margin

    c.save()