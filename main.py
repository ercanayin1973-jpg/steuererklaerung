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

def create_pdf_report(ai_text, status, filename="Steuererklaerung_Formular.pdf"):
    # Resmi Vergi Formu Düzeni (Kenar boşlukları ve yapı)
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    elements = []
    styles = getSampleStyleSheet()
    
    # Form Başlık Stili
    form_title = ParagraphStyle(
        'FormTitle',
        parent=styles['Heading1'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#000000'),
        alignment=1 # Ortalanmış
    )
    
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=11
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=11
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.whitesmoke
    )

    # 1. Resmi Form Başlığı ve Barkod Alanı Simülasgonu (Üst Bilgi Kutusu)
    header_data = [
        [Paragraph("<b>STEUERVERWALTUNG SCHWEIZ - OFFIZIELLES FORMULAR</b>", form_title)],
        [Paragraph("<b>Steuernummer:</b> CH-2026-998877 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Veranlagungsjahr:</b> 2026 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Zivilstand:</b> " + status, meta_style)]
    ]
    header_table = Table(header_data, colWidths=[540])
    header_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#000000')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # 2. Resmi Form Tablosu (Abzüge & Berechnungen)
    table_data = [
        [Paragraph("<b>Ziffer / Code</b>", header_style), Paragraph("<b>Steuerliche Kategorie (Abzüge)</b>", header_style), Paragraph("<b>Erklaerung / Details</b>", header_style), Paragraph("<b>Betrag (CHF)</b>", header_style)],
        [Paragraph("Ziff. 1.1", cell_style), Paragraph("Berufsauslagen", cell_style), Paragraph("Fahrkosten / OeV (Tarifkonform)", cell_style), Paragraph("1'500 CHF", cell_style)],
        [Paragraph("Ziff. 2.3", cell_style), Paragraph("Krankheitskosten", cell_style), Paragraph("Selbstbehalt Arzt/Zahnarzt", cell_style), Paragraph("800 CHF", cell_style)],
        [Paragraph("Ziff. 4.0", cell_style), Paragraph("Zuwendungen", cell_style), Paragraph("Spenden an gemeinnuetzige Org.", cell_style), Paragraph("250 CHF", cell_style)]
    ]
    
    form_table = Table(table_data, colWidths=[60, 130, 270, 80])
    form_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(form_table)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>RECHTLICHE BERECHNUNG UND BEGRÜNDUNG (AMTLICHE DETAILS):</b>", meta_style))
    elements.append(Spacer(1, 4))

    # 3. Yapay Zekadan Gelen OR (Koşullu) Detaylı Analiz Metni
    for line in ai_text.split('\n'):
        if line.strip():
            elements.append(Paragraph(line, meta_style))
            elements.append(Spacer(1, 2))

    doc.build(elements)
    return filename

def process_tax_documents():
    # OR (Koşullu) Mantık: Burayı "Verheiratet" veya "Ledig" yaparak değiştirebilirsin
    medeni_durum = "Verheiratet"  # Örn: Verheiratet (Evli) veya Ledig (Bekar)
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    if medeni_durum == "Verheiratet":
        tarif_bilgisi = "Musteri EVLI bir cifttir. Isvicre ortak vergi tarifesine (Verheiratetentarif) gore hesapla."
    else:
        tarif_bilgisi = "Musteri BEKARDIR (Ledig). Isvicre bekar vergi tarifesine (Alleinstehenden-Tarif) gore hesapla."

    prompt = f"""
    Du bist ein Experte für das Schweizer Steuerrecht.
    Zivilstand-Status: {tarif_bilgisi}
    Erstelle eine formelle steuerrechtliche Analyse auf HOCHDEUTSCH (Schweizer Steueramt Standard).
    Erkläre präzise die gesetzlichen Abzüge (Berufsauslagen, Krankheitskosten, Spenden) gemäss diesem Status.
    Keine türkische Sprache verwenden, ausschliesslich formelles Schweizer Deutsch.
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
    )
    return response.text, medeni_durum

def send_email_with_pdf():
    ai_text, durum = process_tax_documents()
    pdf_path = create_pdf_report(ai_text, durum)
    
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = f"Offizielles_Steuerformular_{durum}.pdf"
    msg.attach(MIMEText(f"Im Anhang finden Sie das offizielle Steuerformular im Formular-Layout ({durum}).", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=Steuerformular_{durum}.pdf")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("Resmi form formatinda PDF basariyla gonderildi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    send_email_with_pdf()
