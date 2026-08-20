from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_complete_steuererklaerung():
    file_path = "Steuererklaerung_2025_Form300_Komplett.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # --- SAYFA 1: FORM 300 (Ana Vergi Özeti ve Ziffer Zinciri) ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH (FORM 300)")
    
    einkunfte = 170450  # Ziff. 7
    abzuge = {
        "11.1/2": 6400,   # Berufsauslagen P1+P2
        "12": 150,        # Schuldzinsen (Privatkredit faizi)
        "14.1/2": 14516,  # Säule 3a P1+P2
        "15": 5800,       # Versicherungsprämien / Krankenkasse
        "16.2": 500,      # Weiterbildung
        "16.3": 150,      # Wertschriftenverwaltung
        "16.6": 12000,    # Fremdbetreuung Kinder (Kita Noah)
        "17": 6100        # Sonderabzug Erwerbstätigkeit
    }
    z18_total = sum(abzuge.values()) 
    z21_netto = einkunfte - z18_total
    
    z22_total = 1700 # Krankheitskosten / Spenden
    z23_rein = z21_netto - z22_total
    z25_steuerbar_eink = z23_rein - 9300 - 2800 
    
    main_data = [
        ("Ziff.", "Beschreibung (Form 300)", "CHF"),
        ("1.1", "Haupterwerb Person 1 & 2", "170'000"),
        ("4.1", "Wertschriftenertrag (Form 340)", "450"),
        ("7", "Total der Einkünfte", str(einkunfte)),
        ("11.1/2", "Berufsauslagen P1+P2", str(abzuge["11.1/2"])),
        ("12", "Schuldzinsen (Privatkredit)", str(abzuge["12"])),
        ("14.1/2", "Säule 3a P1+P2", str(abzuge["14.1/2"])),
        ("15", "Versicherungsprämien", str(abzuge["15"])),
        ("16.2", "Weiterbildungskosten", str(abzuge["16.2"])),
        ("16.3", "Wertschriftenverwaltung", str(abzuge["16.3"])),
        ("16.6", "Kinderbetreuung (Kita Noah)", str(abzuge["16.6"])),
        ("17", "Sonderabzug Erwerbstätigkeit", str(abzuge["17"])),
        ("18", "Total der Abzüge", str(z18_total)),
        ("21", "Nettoeinkommen", str(z21_netto)),
        ("22.1/2", "Krankheitskosten / Spenden", str(z22_total)),
        ("23", "Reineinkommen", str(z23_rein)),
        ("24.1", "Kinderabzug (Noah - Kanton)", "9'300"),
        ("24.3", "Ehegattenabzug (Bund)", "2'800"),
        ("25", "STEUERBARES EINKOMMEN", str(z25_steuerbar_eink)),
        ("33", "Total der Vermögenswerte", "57'500"),
        ("34", "Schulden (Form 355 - Privatkredit)", "-5'000"),
        ("35", "STEUERBARES VERMÖGEN", "52'500")
    ]
    
    y = 750
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, main_data[0][0]); c.drawString(120, y, main_data[0][1]); c.drawString(450, y, main_data[0][2])
    y -= 20
    c.setFont("Helvetica", 9)
    for row in main_data[1:]:
        c.drawString(50, y, row[0]); c.drawString(120, y, row[1]); c.drawString(450, y, row[2])
        y -= 16
        
    # --- SAYFA 2: EK FORMLAR (Form 340 Wertschriften ve Form 355 Schulden) ---
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "ERFORDERLICHE BEILAGEN ZUR STEUERERKLÄRUNG")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 760, "1. Wertschriften- und Guthabenverzeichnis (Form 340)")
    c.setFont("Helvetica", 9)
    c.drawString(50, 740, "• ZKB Bankguthaben: 45'000 CHF | Ertrag (Ziff. 4.1): 250 CHF")
    c.drawString(50, 725, "• Aktien / Fonds (Portfolio): 12'500 CHF | Ertrag (Dividende): 200 CHF")
    c.drawString(50, 710, "-> Total Wertschriften / Guthaben (Ziff. 33): 57'500 CHF")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 670, "2. Schuldenverzeichnis (Form 355)")
    c.setFont("Helvetica", 9)
    c.drawString(50, 650, "• Privatkredit (Restschuld per 31.12.2025): 5'000 CHF -> Ziff. 34")
    c.drawString(50, 635, "• Schuldzinsen (2025 Ödemesi): 150 CHF -> Ziff. 12")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 595, "3. Kontrol Edilmesi Gereken Ek Noktalar")
    c.setFont("Helvetica", 9)
    c.drawString(50, 575, "• Krankheits- / Unfallkosten (Ziff. 22.1): 1'700 CHF")
    c.drawString(50, 560, "• Kinderbetreuung (Ziff. 16.6): Kita masrafı için resmi onaylı fatura gereklidir.")

    c.save()
    return file_path

def send_email():
    file_path = create_complete_steuererklaerung()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025 - FORM 300 KOMPLETT"
    msg.attach(MIMEText("Zürih 2025 Form 300 ve ek form dökümleri (Wertschriften/Schulden) içeren tam liste ektedir.", 'plain', 'utf-8'))
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025_Form300_Komplett.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
