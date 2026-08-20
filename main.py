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

def create_pdf_report(kanton, status, filename="Steuererklaerung_2025_Zuerich.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    
    # Zürih 2025 Resmî Standartları
    elements.append(Paragraph("<b>STEUERERKLÄRUNG 2025 - KANTON ZÜRICH</b>", ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, alignment=1)))
    elements.append(Spacer(1, 10))
    
    # 1. Personendaten & Kinder (Ziff. 1-9)
    elements.append(Paragraph("<b>1. PERSONALIEN & FAMILIE</b>", styles['Heading2']))
    personal_data = [
        ["Steuerpflichtiger (P1):", "Max Muster (15.05.1985)"],
        ["Ehepartner (P2):", "Erika Muster (20.08.1988)"],
        ["Kinder (Ziff. 7):", "Noah Muster (Geb. 10.02.2018 - Sozialabzug 9'300 CHF berücksichtigt)"]
    ]
    elements.append(Table(personal_data, colWidths=[150, 350]))
    elements.append(Spacer(1, 10))

    # 2. Einkommen (Ziff. 11-19)
    elements.append(Paragraph("<b>2. EINKOMMEN (BRUTTO)</b>", styles['Heading2']))
    income_data = [
        ["Ziff.", "Beschreibung", "P1 (CHF)", "P2 (CHF)"],
        ["11.1", "Bruttolohn", "125'000", "45'000"],
        ["11.2", "AHV/IV/EO/ALV", "-7'800", "-2'800"],
        ["11.3", "Pensionskasse", "-8'500", "-3'050"],
        ["17", "Sonderabzug Erwerbstätigkeit (Beide)", "6'100", "-"],
        ["Total", "Nettoeinkommen", "114'600", "39'150"]
    ]
    elements.append(Table(income_data, colWidths=[50, 250, 100, 100]))
    elements.append(Spacer(1, 10))

    # 3. Abzüge (Ziff. 20-22)
    elements.append(Paragraph("<b>3. ABZÜGE (BERUF, 3A, KRANKENKASSE)</b>", styles['Heading2']))
    deduct_data = [
        ["Ziff.", "Kategorie", "Betrag (CHF)"],
        ["21", "Berufsauslagen (P1 + P2)", "6'400"],
        ["22.1", "Säule 3a (Max. 7'258 x 2)", "14'516"],
        ["22.2", "Krankenkassenprämien (Max. Sozialabzug)", "5'800"],
        ["22.3", "Spenden / Krankheitskosten", "1'700"]
    ]
    elements.append(Table(deduct_data, colWidths=[50, 300, 150]))
    elements.append(Spacer(1, 10))

    # 4. Vermögen & Schulden (Ziff. 30-35)
    elements.append(Paragraph("<b>4. VERMÖGEN & SCHULDEN</b>", styles['Heading2']))
    asset_data = [
        ["Ziff.", "Kategorie", "Betrag (CHF)"],
        ["30.1", "Bankkonten (ZKB, PostFinance)", "45'000"],
        ["30.2", "Wertschriften (Aktien/Fonds)", "12'500"],
        ["35", "Schulden (Privatkredit)", "-5'000"]
    ]
    elements.append(Table(asset_data, colWidths=[50, 300, 150]))
    elements.append(Spacer(1, 10))

    # 5. Steuerberechnung (3-Teilig)
    elements.append(Paragraph("<b>5. STEUERBERECHNUNG (ZÜRICH 2025)</b>", styles['Heading2']))
    tax_data = [
        ["Steuerart", "Berechnungsgrundlage", "Betrag (CHF)"],
        ["Staatssteuer", "Kanton Zürich", "6'200"],
        ["Gemeindesteuer", "Zürich (Stadt)", "7'100"],
        ["Bundessteuer", "Direkte Bundessteuer", "3'100"],
        ["TOTAL", "Geschätzte Steuerlast", "16'400"]
    ]
    elements.append(Table(tax_data, colWidths=[150, 200, 150]))

    doc.build(elements)
    return filename

def send_email_with_pdf():
    pdf_path = create_pdf_report("Zuerich", "Verheiratet")
    
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = "Offizielle_Steuererklaerung_Zuerich_2025.pdf"
    msg.attach(MIMEText("Ekli dosya, Zürih Kantonu 2025 resmî form kurallarına göre düzenlenmiş güncel beyannamedir.", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025_Zuerich.pdf")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("Resmi Zürih 2025 formu başarıyla gönderildi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    send_email_with_pdf()
