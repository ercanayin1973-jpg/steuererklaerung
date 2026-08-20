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

def create_pdf_report(ai_text, kanton, status, filename="Steuererklaerung_Kantonale_Form.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    
    form_title = ParagraphStyle(
        'FormTitle',
        parent=styles['Heading1'],
        fontSize=11,
        leading=13,
        textColor=colors.HexColor('#000000'),
        alignment=1
    )
    
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10,
        textColor=colors.whitesmoke
    )

    # 1. Kanton ve Kişisel Bilgiler Başlığı
    header_data = [
        [Paragraph(f"<b>OFFIZIELLE STEUERERKLÄRUNG – KANTON {kanton.upper()}</b>", form_title)],
        [Paragraph(f"<b>Steuerpflichtige(r):</b> Max & Erika Muster | <b>Adresse:</b> Bahnhofstrasse 10, 8001 {kanton}<br/><b>AHV-Nr:</b> 756.1234.5678.90 | <b>Zivilstand:</b> {status} | <b>Steuerjahr:</b> 2026", meta_style)]
    ]
    header_table = Table(header_data, colWidths=[550])
    header_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#000000')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # 2. Gelirler Tablosu (Bruttolohn, Sosyal Kesintiler, Banka Faizleri)
    income_data = [
        [Paragraph("<b>Code</b>", header_style), Paragraph("<b>Einkommensart / Beschreibung (Lohnausweis & Belege)</b>", header_style), Paragraph("<b>Betrag (CHF)</b>", header_style)],
        [Paragraph("Ziff. 1.1", cell_style), Paragraph("Bruttolohn (Hauptberuf - Arbeitgeber)", cell_style), Paragraph("125'000 CHF", cell_style)],
        [Paragraph("Abzug", cell_style), Paragraph("AHV / IV / EO & Pensionskasse (2. Säule Sozialabzüge)", cell_style), Paragraph("- 15'750 CHF", cell_style)],
        [Paragraph("Ziff. 1.2", cell_style), Paragraph("Nebeneinkünfte / Erwerbsersatz", cell_style), Paragraph("10'000 CHF", cell_style)],
        [Paragraph("Ziff. 3.1", cell_style), Paragraph("Wertschriften & Bankkonto Zinserträge", cell_style), Paragraph("450 CHF", cell_style)]
    ]
    t_income = Table(income_data, colWidths=[50, 400, 100])
    t_income.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(Paragraph("<b>1. EINKOMMEN (BRUTTOLOHN, SOZIALABZÜGE, ZINSEN)</b>", meta_style))
    elements.append(Spacer(1, 2))
    elements.append(t_income)
    elements.append(Spacer(1, 6))

    # 3. İndirimler Tablosu (Meslek, Sağlık, 3. Säule, Spenden)
    deduction_data = [
        [Paragraph("<b>Code</b>", header_style), Paragraph("<b>Abzugskategorie</b>", header_style), Paragraph("<b>Details / Begründung</b>", header_style), Paragraph("<b>Betrag (CHF)</b>", header_style)],
        [Paragraph("Ziff. 2.1", cell_style), Paragraph("Berufsauslagen", cell_style), Paragraph("Fahrkosten (ÖV/Auto) & Verpflegung", cell_style), Paragraph("3'200 CHF", cell_style)],
        [Paragraph("Ziff. 2.2", cell_style), Paragraph("Säule 3a", cell_style), Paragraph("Private Vorsorge (Maximalbetrag)", cell_style), Paragraph("7'056 CHF", cell_style)],
        [Paragraph("Ziff. 2.3", cell_style), Paragraph("Krankheitskosten", cell_style), Paragraph("Selbstbehalt Arzt & Zahnarzt", cell_style), Paragraph("1'200 CHF", cell_style)],
        [Paragraph("Ziff. 4.0", cell_style), Paragraph("Spenden", cell_style), Paragraph("Zuwendungen an steuerbefreite Org.", cell_style), Paragraph("500 CHF", cell_style)]
    ]
    t_deduction = Table(deduction_data, colWidths=[50, 110, 290, 100])
    t_deduction.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(Paragraph("<b>2. ABZÜGE (BERUF, SÄULE 3A, GESUNDHEIT, SPENDEN)</b>", meta_style))
    elements.append(Spacer(1, 2))
    elements.append(t_deduction)
    elements.append(Spacer(1, 6))

    # 4. Servet, Menkul Kıymetler ve Borçlar Tablosu (Vermögen & Schulden)
    asset_data = [
        [Paragraph("<b>Kategorie</b>", header_style), Paragraph("<b>Beschreibung / Details (Banken, Aktien, Liegenschaften)</b>", header_style), Paragraph("<b>Wert / Betrag (CHF)</b>", header_style)],
        [Paragraph("Wertschriften", cell_style), Paragraph("Bankguthaben (Zürich Kantonalbank & PostFinance)", cell_style), Paragraph("45'000 CHF", cell_style)],
        [Paragraph("Wertschriften", cell_style), Paragraph("Aktien / Fonds (Schweizer Börse)", cell_style), Paragraph("12'500 CHF", cell_style)],
        [Paragraph("Schulden", cell_style), Paragraph("Privatkredit / Kreditkartenschulden", cell_style), Paragraph("- 5'000 CHF", cell_style)]
    ]
    t_asset = Table(asset_data, colWidths=[100, 350, 100])
    t_asset.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(Paragraph("<b>3. VERMÖGEN & SCHULDEN (BANKEN, AKTIEN, KREDITE)</b>", meta_style))
    elements.append(Spacer(1, 2))
    elements.append(t_asset)
    elements.append(Spacer(1, 6))

    # 5. Vergilendirilebilir Matrah ve Tahmini Vergi Yükü (Steuerbares Einkommen & Steuerlast)
    tax_load_data = [
        [Paragraph("<b>Berechnungsgrundlage nach Kantonalem Recht ({kanton})</b>", header_style), Paragraph("<b>Betrag / Schätzung (CHF)</b>", header_style)],
        [Paragraph("Steuerbares Einkommen (Nettoeinkommen nach allen Abzügen)", cell_style), Paragraph("approx. 109'950 CHF", cell_style)],
        [Paragraph("Steuerbares Vermögen (Abzüglich Schulden)", cell_style), Paragraph("approx. 52'500 CHF", cell_style)],
        [Paragraph("<b>Geschätzte Steuerlast (Kanton, Gemeinde & Bund)</b>", cell_style), Paragraph("<b>approx. 13'900 CHF</b>", cell_style)]
    ]
    t_tax = Table(tax_load_data, colWidths=[450, 100])
    t_tax.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B91C1C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#000000')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(Paragraph("<b>4. STEUERBARES EINKOMMEN, VERMÖGEN & GESCHÄTZTE STEUERLAST</b>", meta_style))
    elements.append(Spacer(1, 2))
    elements.append(t_tax)
    elements.append(Spacer(1, 6))

    # 6. Kantonel Kurallar ve Gerekli Belgeler
    elements.append(Paragraph(f"<b>5. KANTONALE HINWEISE ({kanton.upper()}) & EINZUREICHENDE BELEGE:</b>", meta_style))
    elements.append(Spacer(1, 3))

    for line in ai_text.split('\n'):
        if line.strip():
            elements.append(Paragraph(line, meta_style))
            elements.append(Spacer(1, 1))

    doc.build(elements)
    return filename

def process_tax_documents():
    # BURADAN KANTONU VE MEDENİ DURUMU SEÇEBİLİRSİN
    secilen_kanton = "Zuerich"      # Örn: "Zuerich", "Bern", "Zug", "Luzern" vb.
    medeni_durum = "Verheiratet"  # Örn: "Verheiratet" (Evli) veya "Ledig" (Bekar)
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Du bist ein Experte für das Schweizer Steuerrecht im Kanton {secilen_kanton}.
    Zivilstand: {medeni_durum}.
    Erstelle eine formelle, präzise Zusammenfassung auf HOCHDEUTSCH (Schweizer Steuerstandard).
    Erkläre kurz die kantonsspezifischen Besonderheiten für {secilen_kanton}, welche Belege (Lohnausweis, Bankbelege, Säule 3a Bescheinigung) eingereicht werden müssen und wie sich das steuerbare Einkommen und Vermögen zusammensetzen.
    Keine türkische Sprache verwenden, ausschliesslich formelles Schweizer Deutsch.
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
    )
    return response.text, secilen_kanton, medeni_durum

def send_email_with_pdf():
    ai_text, kanton, durum = process_tax_documents()
    pdf_path = create_pdf_report(ai_text, kanton, durum)
    
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = f"Steuererklaerung_{kanton}_{durum}.pdf"
    msg.attach(MIMEText(f"Im Anhang finden Sie die vollständige Steuererklärung für den Kanton {kanton} ({durum}) inklusive Vermögen, Schulden und Steuerlast.", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"filename=Steuererklaerung_{kanton}.pdf")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print(f"Kanton {kanton} için vergi formu başarıyla gönderildi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    send_email_with_pdf()
