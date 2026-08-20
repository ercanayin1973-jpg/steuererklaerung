import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email():
    # 1. Zürih 2025 Detaylı Veri Hazırlığı
    data = [
        ["Ziffer", "Beschreibung", "Betrag (CHF)"],
        ["11.1", "Bruttolohn Person 1", 125000],
        ["11.2", "Bruttolohn Person 2", 45000],
        ["17", "Sonderabzug Erwerbstätigkeit (Beide)", 6100],
        ["21", "Berufsauslagen (Total)", -6400],
        ["22.1", "Säule 3a (Max. Total)", -14516],
        ["22.2", "Krankenkassen-Sozialabzug", -5800],
        ["16.6", "Kita-Abzug (Fremdbetreuung)", -12000],
        ["30.1", "Bankkonten (ZKB)", 45000],
        ["35", "Schulden (Privatkredit)", -5000]
    ]
    
    file_name = "Steuererklaerung_Zuerich_2025_Final.csv"
    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    # 2. Maili Hazırla
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025 - ZÜRICH"
    msg.attach(MIMEText("Ekli dosya, Zürih Kantonu 2025 resmî standartlarına göre hazırlanan detaylı vergi beyannamesi verileridir.", 'plain', 'utf-8'))

    # 3. Dosyayı Ekle
    with open(file_name, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=file_name)
        msg.attach(part)

    # 4. Gönder
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
