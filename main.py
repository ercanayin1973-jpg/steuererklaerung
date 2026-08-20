from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_professional_tax_pdf():
    kanton = "Zuerich" # Kanton seçimini buradan yapabilirsin
    kanton_bilgileri = {"Zuerich": {"ad": "Kanton Zürich", "portal": "ZHprivateTax"}}
    info = kanton_bilgileri.get(kanton)
    
    file_path = "Steuererklaerung_2025_Formal.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    # Stil tanımlamaları
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor("#1E293B"))
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=8, textColor=colors.white, fontName="Helvetica-Bold")
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8)

    story.append(Paragraph(f"STEUERERKLÄRUNG 2025 - {info['ad'].upper()}", title_style))
    story.append(Spacer(1, 10))
    
    data = [
        ["Ziff.", "Beschreibung", "CHF"],
        ["1.1", "Haupterwerb Person 1 & 2", "170'000"],
        ["4.1", "Wertschriftenertrag", "450"],
        ["7", "Total der Einkünfte", "170'450"], # GRİ
        ["11.1/2", "Berufsauslagen P1 + P2", "-6'400"],
        ["12", "Schuldzinsen", "-150"],
        ["14.1/2", "Säule 3a", "-14'516"],
        ["15", "Versicherungsprämien", "-5'800"],
        ["16.2", "Weiterbildung", "-500"],
        ["16.3", "Wertschriftenverwaltung", "-150"],
        ["16.6", "Fremdbetreuung Kinder", "-12'000"],
        ["17", "Sonderabzug Erwerbstätigkeit", "-6'100"],
        ["18", "Total der Abzüge", "-45'616"], # GRİ
        ["21", "Nettoeinkommen", "124'834"], # GRİ
        ["22.1/2", "Krankheitskosten / Spenden", "-1'700"],
        ["23", "Reineinkommen", "123'134"], # GRİ
        ["24.1", "Kinderabzug Noah", "9'300"],
        ["24.3", "Ehegattenabzug (Bund)", "2'800"],
        ["25", "STEUERBARES EINKOMMEN", "113'834"], # GRİ
        ["33", "Total Vermögenswerte", "57'500"], # GRİ
        ["34", "Schulden", "-5'000"],
        ["35", "STEUERBARES VERMÖGEN", "52'500"] # GRİ
    ]
    
    # Gri olması gereken satır indeksleri (0'dan başlıyor)
    gri_satirlar = [3, 12, 13, 15, 18, 19, 21] 
    
    table_data = [[Paragraph(x, header_style) for x in data[0]]]
    for i, row in enumerate(data[1:], 1):
        table_data.append([Paragraph(x, cell_style) for x in row])
        
    t = Table(table_data, colWidths=[40, 400, 80])
    ts = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]
    # Gri satırları tablo stiline ekle
    for satır_idx in gri_satirlar:
        ts.append(('BACKGROUND', (0, satır_idx), (-1, satır_idx), colors.HexColor("#F1F5F9")))
        
    t.setStyle(TableStyle(ts))
    story.append(t)
    doc.build(story)
    return file_path

# send_email fonksiyonu aynı kalıyor...
def send_email():
    file_path = create_professional_tax_pdf()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "STEUERERKLÄRUNG 2025 - OFFİZIELLE BERECHNUNG"
    msg.attach(MIMEText("Ara toplamların gri ile vurgulandığı güncel vergi özeti ektedir.", 'plain', 'utf-8'))
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025_V2.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
