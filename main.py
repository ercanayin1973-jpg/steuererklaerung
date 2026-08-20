from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_complete_steuererklaerung():
    file_path = "Steuererklaerung_2025_Form300_Eksiksiz.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # --- SAYFA 1: FORM 300 (Tüm Detaylarıyla Eksiksiz Ziffer Zinciri) ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 810, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH (FORM 300)")
    
    main_data = [
        ("Ziff.", "Beschreibung (Form 300)", "CHF"),
        ("1.1", "Haupterwerb Person 1 & 2", "170'000"),
        ("4.1", "Wertschriftenertrag (Form 340)", "450"),
        ("7", "Total der Einkünfte", "170'450"),
        ("11.1/2", "Berufsauslagen P1 + P2", "-6'400"),
        ("12", "Schuldzinsen (Privatkredit)", "-150"),
        ("14.1/2", "Säule 3a (P1 + P2)", "-14'516"),
        ("15", "Versicherungsprämien / Krankenkasse", "-5'800"),
        ("16.2", "Weiterbildungskosten", "-500"),
        ("16.3", "Wertschriftenverwaltung", "-150"),
        ("16.6", "Fremdbetreuung Kinder (Kita Noah)", "-12'000"),
        ("17", "Sonderabzug Erwerbstätigkeit", "-6'100"),
        ("18", "Total der Abzüge", "-45'616"),
        ("21", "Nettoeinkommen", "124'834"),
        ("22.1", "Krankheits- und Unfallkosten", "-1'200"),
        ("22.2", "Gemeinnützige Zuwendungen (Spenden)", "-500"),
        ("23", "Reineinkommen", "123'134"),
        ("24.1", "Kinderabzug Noah (Kanton: 9'300 / Bund: 6'800)", "9'300 / 6'800"),
        ("24.3", "Ehegattenabzug (Nur Bundessteuer)", "2'800"),
        ("25", "STEUERBARES EINKOMMEN (Kanton Zürich)", "113'834"),
        ("25", "STEUERBARES EINKOMMEN (Direkte Bundessteuer)", "113'534"),
        ("33", "Total der Vermögenswerte (Form 340)", "57'500"),
        ("34", "Schulden (Form 355 - Privatkredit)", "-5'000"),
        ("35", "STEUERBARES VERMÖGEN", "52'500")
    ]
    
    y = 785
    c.setFont("Helvetica-Bold", 8)
    c.drawString(50, y, main_data[0][0]); c.drawString(120, y, main_data[0][1]); c.drawString(420, y, main_data[0][2])
    y -= 15
    c.setFont("Helvetica", 8)
    for row in main_data[1:]:
        c.drawString(50, y, row[0]); c.drawString(120, y, row[1]); c.drawString(420, y, row[2])
        y -= 13
        
    # --- SAYFA 2: EK AÇIKLAMALAR VE KONTROL LİSTESİ ---
    c.showPage()
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, 800, "ZUSÄTZLICHE HINWEISE ZUR STEUERERKLÄRUNG")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 760, "1. Form 340 (Wertschriftenverzeichnis)")
    c.setFont("Helvetica", 8)
    c.drawString(50, 742, "• ZKB Bankguthaben & Aktien/Fonds Total Vergi Değeri: 57'500 CHF (Ziff. 33)")
    c.drawString(50, 728, "• Elde Edilen Brüt Faiz ve Temettü Geliri: 450 CHF (Ziff. 4.1)")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 690, "2. Form 355 (Schuldenverzeichnis)")
    c.setFont("Helvetica", 8)
    c.drawString(50, 672, "• Privatkredit Restschuld per 31.12.2025: 5'000 CHF (Ziff. 34)")
    c.drawString(50, 658, "• Yıllık Ödenen Faiz Miktarı: 150 CHF (Ziff. 12)")

    c.save()
    return file_path

def send_email():
    file_path = create_complete_steuererklaerung()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025 - KOMPLETT & UNGEKÜRZT"
    msg.attach(MIMEText("Zürih 2025 Form 300 hiçbir kalem eksiltilmeden ve Kanton/Bund ayrımıyla ekte sunulmuştur.", 'plain', 'utf-8'))
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025_Eksiksiz.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
