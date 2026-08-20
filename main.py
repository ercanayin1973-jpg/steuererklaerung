from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_final_tax_pdf():
    file_path = "Steuererklaerung_2025_Komplett.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor("#1E293B"))
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=7, textColor=colors.white, fontName="Helvetica-Bold")
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=7)

    story.append(Paragraph("STEUERERKLÄRUNG 2025 - OFFIZIELLE FORM 300", title_style))
    story.append(Spacer(1, 10))
    
    # Form 300 Detaylı Tablo
    data = [
        ["Ziff.", "Beschreibung (Form 300)", "Kanton (CHF)", "Bund (CHF)"],
        ["1.1", "Haupterwerb Person 1+2", "170'000", "170'000"],
        ["1.2/3", "Nebenerwerb / Rente / EO / Taggeld", "0", "0"],
        ["4.1", "Wertschriftenertrag (Form 340)", "450", "450"],
        ["6", "Liegenschaften (Eigenmietwert)", "0", "0"],
        ["7", "Total der Einkünfte", "170'450", "170'450"],
        ["11.1/2", "Berufsauslagen", "-6'400", "-6'400"],
        ["12", "Schuldzinsen (Ziff. 34)", "-150", "-150"],
        ["14.1/2", "Säule 3a", "-14'516", "-14'516"],
        ["15", "Versicherungsprämien", "-5'800", "-5'800"],
        ["16.1-6", "Weitere Abzüge (Kita, Weiterb., etc.)", "-12'650", "-12'650"],
        ["17", "Sonderabzug", "-6'100", "-6'100"],
        ["18", "Total der Abzüge", "-45'616", "-45'616"],
        ["21", "Nettoeinkommen", "124'834", "124'834"],
        ["22.1", "Krankheitskosten", "-1'200", "-1'200"],
        ["22.2", "Spenden", "-500", "-500"],
        ["23", "Reineinkommen", "123'134", "123'134"],
        ["24.1", "Kinderabzug Noah", "-9'300", "-6'800"],
        ["24.3", "Ehegattenabzug", "0", "-2'800"],
        ["25", "STEUERBARES EINKOMMEN", "113'834", "113'534"],
        ["33", "Total Vermögenswerte (Form 340)", "57'500", "-"],
        ["34", "Schulden (Form 355)", "-5'000", "-"],
        ["35", "STEUERBARES VERMÖGEN", "52'500", "-"]
    ]
    
    # Tablo Oluşturma
    table_data = [[Paragraph(x, header_style) for x in data[0]]]
    for row in data[1:]:
        table_data.append([Paragraph(x, cell_style) for x in row])
        
    t = Table(table_data, colWidths=[30, 250, 80, 80])
    ts = [('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
          ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
          ('BACKGROUND', (0,5), (-1,5), colors.HexColor("#F1F5F9")), # Total Einkunfte
          ('BACKGROUND', (0,12), (-1,12), colors.HexColor("#F1F5F9")), # Total Abzuge
          ('BACKGROUND', (0,13), (-1,13), colors.HexColor("#F1F5F9")), # Netto
          ('BACKGROUND', (0,16), (-1,16), colors.HexColor("#F1F5F9")), # Rein
          ('BACKGROUND', (0,19), (-1,19), colors.HexColor("#E2E8F0"))] # Steuerbar
    t.setStyle(TableStyle(ts))
    story.append(t)
    
    doc.build(story)
    return file_path

def send_email():
    file_path = create_final_tax_pdf()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025 - FORM 300 VOLLSTÄNDIG"
    msg.attach(MIMEText("Tüm Ziffer kalemlerinin (boşlar dahil) Kanton/Bund ayrımıyla listelendiği resmi beyanname ektedir.", 'plain', 'utf-8'))
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025_Vollstaendig.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
