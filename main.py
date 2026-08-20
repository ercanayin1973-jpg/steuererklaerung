from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def create_pdf():
    file_path = "Steuererklaerung_2025_Zuerich.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # Başlık
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH")
    
    # Veri Listesi
    c.setFont("Helvetica", 10)
    data = [
        ("Ziffer", "Beschreibung", "Betrag (CHF)"),
        ("11.1", "Bruttolohn Person 1", "125'000"),
        ("11.2", "Bruttolohn Person 2", "45'000"),
        ("17", "Sonderabzug Erwerbstätigkeit", "6'100"),
        ("21", "Berufsauslagen", "-6'400"),
        ("22.1", "Säule 3a", "-14'516"),
        ("16.6", "Kita-Abzug", "-12'000"),
        ("30.1", "Bankguthaben", "45'000"),
        ("35", "Schulden", "-5'000")
    ]
    
    y = 750
    for row in data:
        c.drawString(50, y, row[0])
        c.drawString(150, y, row[1])
        c.drawString(400, y, row[2])
        y -= 25
        
    c.save()
    return file_path

def send_email():
    file_path = create_pdf()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025"
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
