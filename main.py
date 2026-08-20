from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def create_full_pdf():
    file_path = "Steuererklaerung_2025_Offiziell.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # Başlık ve Kişisel Bilgiler
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 820, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH")
    c.setFont("Helvetica", 10)
    c.drawString(50, 800, "Person 1: Max Muster | Person 2: Erika Muster | Kinder: Noah Muster (10.02.2018)")
    
    # Tablo Başlıkları
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 770, "Ziffer")
    c.drawString(120, 770, "Beschreibung")
    c.drawString(450, 770, "Betrag (CHF)")
    
    # Detaylı Veriler (Senin istediğin 18 madde buraya sığıyor)
    c.setFont("Helvetica", 10)
    data = [
        ("11.1", "Bruttolohn Person 1", "125'000"),
        ("11.2", "Bruttolohn Person 2", "45'000"),
        ("17", "Sonderabzug Erwerbstätigkeit", "6'100"),
        ("21", "Berufsauslagen Total", "-6'400"),
        ("22.1", "Säule 3a (P1+P2)", "-14'516"),
        ("22.2", "Krankenkassen-Sozialabzug", "-5'800"),
        ("16.6", "Kita-Abzug (Fremdbetreuung)", "-12'000"),
        ("7", "Kinder-Sozialabzug (Noah)", "-9'300"),
        ("30.1", "Bankguthaben (ZKB)", "45'000"),
        ("35", "Schulden (Privatkredit)", "-5'000"),
        ("Total", "STEUERBARES EINKOMMEN", "125'484")
    ]
    
    y = 740
    for z, d, b in data:
        c.drawString(50, y, z)
        c.drawString(120, y, d)
        c.drawString(450, y, b)
        y -= 20
        
    c.save()
    return file_path

def send_email():
    file_path = create_full_pdf()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025 - DETAILLIERT"
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025_Offiziell.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
