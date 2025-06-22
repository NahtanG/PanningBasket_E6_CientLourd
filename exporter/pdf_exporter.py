from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def export_trainings_to_pdf(trainings, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    # Bandeau titre coloré
    c.setFillColorRGB(0.18, 0.32, 0.52)  # Bleu basket pro
    c.roundRect(margin-10, y-20, width-2*margin+20, 40, 10, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y, "Planning des Entraînements")
    y -= 40

    # Encadré d'infos (mois, nombre de séances)
    c.setFillColorRGB(0.95, 0.95, 0.98)
    c.roundRect(margin-5, y-35, width-2*margin+10, 32, 8, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    if trainings:
        mois = trainings[0].date.strftime("%B %Y").capitalize()
    else:
        mois = ""
    c.drawString(margin, y-18, f"Mois : {mois}")
    c.drawRightString(width-margin, y-18, f"Nombre de séances : {len(trainings)}")
    y -= 45

    # En-tête de tableau stylisé
    c.setFillColorRGB(0.85, 0.89, 0.98)
    c.roundRect(margin-2, y-18, width-2*margin+4, 22, 5, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#2d3a4a"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y-5, "Date")
    c.drawString(margin + 80, y-5, "Heure")
    c.drawString(margin + 170, y-5, "Catégorie")
    c.drawString(margin + 300, y-5, "Description")
    y -= 25

    # Corps du tableau
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    row_height = 14
    for t in trainings:
        date_str = t.date.strftime('%d/%m/%Y')
        hour_str = f"{t.start_time.strftime('%H:%M')} – {t.end_time.strftime('%H:%M')}"
        desc_lines = t.description.splitlines() if t.description else [""]
        nb_lines = max(1, len(desc_lines))
        total_height = nb_lines * row_height + 2 + (nb_lines-1)*0  # +2 pour marge haute, pas d'espacement entre lignes

        # Saut de page si besoin
        if y - total_height < margin + 40:
            c.showPage()
            y = height - margin - 60

        # Encadrement sur toute la hauteur de l'événement
        c.setFillColor(colors.HexColor("#f7f7f9"))
        c.roundRect(margin-2, y-total_height+row_height, width-2*margin+4, total_height, 3, fill=1, stroke=0)
        c.setFillColor(colors.black)

        # Texte
        y_line = y + 2
        c.drawString(margin, y_line, date_str)
        c.drawString(margin + 80, y_line, hour_str)
        c.drawString(margin + 170, y_line, t.category)
        first = True
        for line in desc_lines:
            c.drawString(margin + 300, y_line, line)
            if first:
                first = False
            else:
                c.drawString(margin, y_line, "")
                c.drawString(margin + 80, y_line, "")
                c.drawString(margin + 170, y_line, "")
            y_line -= row_height

        y -= total_height + 2  # Espace entre les séances

    c.save()