from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def create_official_pdf():
    file_path = "Steuererklaerung_2025_Zuerich_Offiziell.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 820, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH")
    
    # Resmi Ziffer Yapısı
    data = [
        ("Ziffer", "Beschreibung", "Betrag (CHF)"),
        ("1.1", "Haupterwerb Person 1", "125'000"),
        ("1.1", "Haupterwerb Person 2", "45'000"),
        ("11.1", "Berufsauslagen Person 1", "-3'200"),
        ("11.2", "Berufsauslagen Person 2", "-3'200"),
        ("14.1", "Säule 3a Person 1", "-7'258"),
        ("14.2", "Säule 3a Person 2", "-7'258"),
        ("15", "Versicherungsprämien (Krankenkasse)", "-5'800"),
        ("16.6", "Fremdbetreuung Kinder (Kita)", "-12'000"),
        ("17", "Sonderabzug Erwerbstätigkeit", "6'100"),
        ("22.1", "Krankheits- und Unfallkosten", "-1'200"),
        ("22.2", "Gemeinnützige Zuwendungen", "-500"),
        ("24.1", "Kinderabzug (Staatssteuer)", "-9'300"),
        ("30.1", "Bankguthaben & Wertschriften", "57'500"),
        ("34", "Schulden (Privatkredit)", "-5'000"),
        ("35", "STEUERBARES VERMÖGEN GESAMT", "52'500")
    ]
    
    y = 770
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, data[0][0]); c.drawString(150, y, data[0][1]); c.drawString(450, y, data[0][2])
    y -= 30
    c.setFont("Helvetica", 10)
    for row in data[1:]:
        c.drawString(50, y, row[0]); c.drawString(150, y, row[1]); c.drawString(450, y, row[2])
        y -= 20
    c.save()
    return file_path

def send_email():
    file_path = create_official_pdf()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025"
    
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
