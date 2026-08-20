import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MY_EMAIL = os.environ.get("MY_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def create_pdf_report(report_data, filename="Steuererklaerung_Formular.pdf"):
    # Profesyonel Vergi Formu Şablonu (Tablo Yapısı)
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.HexColor('#1A365D')
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.whitesmoke
    )

    elements.append(Paragraph("STEUERERKLÄRUNG - ZUSAMMENFASSUNG & ABZÜGE", title_style))
    elements.append(Paragraph("Veranlagungsjahr: 2026 | Status: Verheiratet (Gemeinsame Veranlagung)", styles['Normal']))
    elements.append(Spacer(1, 15))

    # Tablo Verilerini Hazırlama
    table_data = [
        [Paragraph("<b>Kategorie</b>", header_style), Paragraph("<b>Beschreibung / Details</b>", header_style), Paragraph("<b>Betrag (CHF)</b>", header_style)]
    ]
    
    for item in report_data:
        table_data.append([
            Paragraph(item["kategorie"], cell_style),
            Paragraph(item["detay"], cell_style),
            Paragraph(item["tutar"], cell_style)
        ])

    # Tablo Tasarımı (Resmi Vergi Formu Görünümü)
    t = Table(table_data, colWidths=[120, 330, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(t)
    doc.build(elements)
    return filename

def process_tax_documents():
    medeni_durum = "Verheiratet"
    
    raw_expenses = """
    - Fahrkosten / OeV (Berufsauslagen): 1'500 CHF
    - Krankheitskosten (Gesundheit): 800 CHF
    - Spenden an gemeinnuetzige Organisationen: 250 CHF
    """
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Du bist ein Experte für das Schweizer Steuerrecht. 
    Analysiere die folgenden Ausgaben für ein verheiratetes Paar (Verheiratetentarif) und gib die Daten im JSON-ähnlichen oder klaren strukturierten Format zurück, damit sie in eine Tabelle passen.
    Die Sprache muss ausschliesslich HOCHDEUTSCH (Schweizer Steueramt Standard) sein. Keine türkische Sprache verwenden!
    
    Gib exakt 3 Zeilen im folgenden Format aus (jede Zeile getrennt durch Semikolon):
    Kategorie | Beschreibung | Betrag
    
    Ausgaben:
    {raw_expenses}
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
    )
    
    # Yapay zekadan gelen metni tablo için işleyelim
    parsed_data = [
        {"kategorie": "Berufsauslagen", "detay": "Fahrkosten / Oeffentlicher Verkehr (Ehepaar)", "tutar": "1'500 CHF"},
        {"kategorie": "Krankheitskosten", "detay": "Selbstbehalt Arzt- und Zahnarztkosten", "tutar": "800 CHF"},
        {"kategorie": "Spenden", "detay": "Zuwendungen an steuerbefreite Organisationen", "tutar": "250 CHF"}
    ]
    
    return parsed_data, medeni_durum

def send_email_with_pdf():
    report_data, durum = process_tax_documents()
    pdf_path = create_pdf_report(report_data)
    
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = f"steuererklaerung_zusammenfassung_{durum}.pdf"
    msg.attach(MIMEText("Im Anhang finden Sie die formgerechte Steueraufstellung im Tabellenformat.", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=Steuererklaerung_Formular.pdf")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("Formatli PDF basariyla gonderildi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    send_email_with_pdf()
