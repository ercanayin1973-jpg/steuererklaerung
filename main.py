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

def create_pdf_report(ai_text, status, filename="Steuererklaerung_Standart.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    elements = []
    styles = getSampleStyleSheet()
    
    form_title = ParagraphStyle(
        'FormTitle',
        parent=styles['Heading1'],
        fontSize=12,
        leading=14,
        textColor=colors.HexColor('#000000'),
        alignment=1
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

    # 1. Kişisel Bilgiler
    header_data = [
        [Paragraph("<b>EIDGENÖSSISCHE & KANTONALE STEUERERKLÄRUNG (SCHWEIZ)</b>", form_title)],
        [Paragraph("<b>Steuerpflichtige(r):</b> Max & Erika Muster &nbsp;&nbsp;|&nbsp;&nbsp; <b>Adresse:</b> Bahnhofstrasse 10, 8001 Zürich<br/><b>AHV-Nr:</b> 756.1234.5678.90 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Zivilstand:</b> " + status + " &nbsp;&nbsp;|&nbsp;&nbsp; <b>Steuerjahr:</b> 2026", meta_style)]
    ]
    header_table = Table(header_data, colWidths=[540])
    header_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#000000')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 8))

    # 2. Gelirler Tablosu (Bruttolohn ve Sosyal Kesintiler Dahil)
    income_data = [
        [Paragraph("<b>Ziffer / Code</b>", header_style), Paragraph("<b>Einkommensart / Beschreibung (Lohnausweis)</b>", header_style), Paragraph("<b>Betrag (CHF)</b>", header_style)],
        [Paragraph("Ziff. 1.1", cell_style), Paragraph("Bruttolohn (Hauptberuf - Arbeitgeber AG)", cell_style), Paragraph("125'000 CHF", cell_style)],
        [Paragraph("Abzug", cell_style), Paragraph("AHV / IV / EO Beiträge (Sozialabzüge vom Brutto)", cell_style), Paragraph("- 6'250 CHF", cell_style)],
        [Paragraph("Abzug", cell_style), Paragraph("Pensionskasse / BVG 2. Säule (Arbeitnehmerbeitrag)", cell_style), Paragraph("- 9'500 CHF", cell_style)],
        [Paragraph("Ziff. 1.2", cell_style), Paragraph("Nebeneinkünfte (Zweiteingang)", cell_style), Paragraph("15'000 CHF", cell_style)]
    ]
    t_income = Table(income_data, colWidths=[60, 380, 100])
    t_income.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(Paragraph("<b>1. EINKOMMEN & SOZIALE ABZÜGE (LOHNAUSWEIS)</b>", meta_style))
    elements.append(Spacer(1, 3))
    elements.append(t_income)
    elements.append(Spacer(1, 8))

    # 3. Diğer İndirimler Tablosu (Berufsauslagen, Krankheitskosten vb.)
    deduction_data = [
        [Paragraph("<b>Ziffer / Code</b>", header_style), Paragraph("<b>Abzugskategorie</b>", header_style), Paragraph("<b>Details / Begründung</b>", header_style), Paragraph("<b>Betrag (CHF)</b>", header_style)],
        [Paragraph("Ziff. 2.1", cell_style), Paragraph("Berufsauslagen", cell_style), Paragraph("Fahrkosten (ÖV/Auto) & Verpflegung", cell_style), Paragraph("3'200 CHF", cell_style)],
        [Paragraph("Ziff. 2.3", cell_style), Paragraph("Krankheitskosten", cell_style), Paragraph("Selbstbehalt Arzt & Zahnarzt", cell_style), Paragraph("1'200 CHF", cell_style)],
        [Paragraph("Ziff. 4.0", cell_style), Paragraph("Zuwendungen", cell_style), Paragraph("Spenden an steuerbefreite Organisationen", cell_style), Paragraph("500 CHF", cell_style)]
    ]
    t_deduction = Table(deduction_data, colWidths=[60, 120, 260, 100])
    t_deduction.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(Paragraph("<b>2. WEITERE ABZÜGE (BERUFSAUSLAGEN, GESUNDHEIT, SPENDEN)</b>", meta_style))
    elements.append(Spacer(1, 3))
    elements.append(t_deduction)
    elements.append(Spacer(1, 8))

    # 4. Ödenecek Vergi / Tahmini Vergi Yükü Tablosu
    tax_load_data = [
        [Paragraph("<b>Berechnungsgrundlage / Steuerlast</b>", header_style), Paragraph("<b>Betrag / Schätzung (CHF)</b>", header_style)],
        [Paragraph("Steuerbares Einkommen (Bereinigt nach Abzügen & Sozialbeiträgen)", cell_style), Paragraph("approx. 114'250 CHF", cell_style)],
        [Paragraph("<b>Geschätzte Steuerlast (Einfache Steuer & Kantons-/Gemeindesteuern)</b>", cell_style), Paragraph("<b>approx. 14'800 CHF</b>", cell_style)]
    ]
    t_tax = Table(tax_load_data, colWidths=[440, 100])
    t_tax.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B91C1C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(Paragraph("<b>3. BERECHNUNG DER STEUERLAST (ZU ZAHLENDE STEUERN)</b>", meta_style))
    elements.append(Spacer(1, 3))
    elements.append(t_tax)
    elements.append(Spacer(1, 8))

    # 5. Detaylı Açıklamalar
    elements.append(Paragraph("<b>4. EINZUREICHENDE BELEGE & RECHTLICHE HINWEISE:</b>", meta_style))
    elements.append(Spacer(1, 4))

    for line in ai_text.split('\n'):
        if line.strip():
            elements.append(Paragraph(line, meta_style))
            elements.append(Spacer(1, 2))

    doc.build(elements)
    return filename

def process_tax_documents():
    medeni_durum = "Verheiratet"  # "Verheiratet" veya "Ledig" (OR Mantığı)
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    if medeni_durum == "Verheiratet":
        tarif_bilgisi = "Musteri EVLI bir cifttir. Isvicre ortak vergi tarifesine (Verheiratetentarif) gore hesapla."
    else:
        tarif_bilgisi = "Musteri BEKARDIR (Ledig). Isvicre bekar vergi tarifesine (Alleinstehenden-Tarif) gore hesapla."

    prompt = f"""
    Du bist ein Experte für das Schweizer Steuerrecht.
    Status: {tarif_bilgisi}
    Erstelle eine formelle Zusammenfassung auf HOCHDEUTSCH (Schweizer Standard).
    Erläutere kurz den Übergang vom Bruttolohn über die Sozialabzüge (AHV/Pensionskasse) zum steuerbaren Einkommen und der geschätzten Steuerlast.
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
    msg['Subject'] = f"Steuererklaerung_Brutto_Sozial_{durum}.pdf"
    msg.attach(MIMEText(f"Im Anhang finden Sie die formgerechte Steuererklärung mit Bruttolohn, Sozialabzügen ve Steuerlast ({durum}).", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=Steuererklaerung_Brutto.pdf")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("Güncel form başarıyla gönderildi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    send_email_with_pdf()
