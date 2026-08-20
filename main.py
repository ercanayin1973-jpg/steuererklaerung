from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_comprehensive_tax_pdf():
    file_path = "Steuererklaerung_2025_Komplett.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # --- SAYFA 1: ANA FORM (Form 300 Özet Verileri) ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH (FORM 300)")
    
    einkunfte = 170450
    abzuge = {
        "11.1": 3200, "11.2": 3200, "14.1": 7258, "14.2": 7258,
        "15": 5800, "16.6": 12000, "17": 6100
    }
    z18_total = sum(abzuge.values())
    z21_netto = einkunfte - z18_total
    z23_rein = z21_netto - 1700 # Krankheits/Spenden
    z25_steuerbar_eink = z23_rein - 9300 - 2800
    
    main_data = [
        ("Ziff.", "Beschreibung", "Betrag (CHF)"),
        ("1.1", "Haupterwerb Person 1+2", "170'000"),
        ("4.1", "Wertschriftenertrag (Form 340)", "450"),
        ("7", "Total der Einkünfte", str(einkunfte)),
        ("18", "Total der Abzüge (Detail unten)", str(z18_total)),
        ("21", "Nettoeinkommen", str(z21_netto)),
        ("23", "Reineinkommen", str(z23_rein)),
        ("24.1", "Kinderabzug (Noah)", "9'300"),
        ("24.3", "Ehegattenabzug (Bund)", "2'800"),
        ("25", "STEUERBARES EINKOMMEN", str(z25_steuerbar_eink)),
        ("33", "Total Vermögenswerte", "57'500"),
        ("34", "Schulden (Form 355)", "-5'000"),
        ("35", "STEUERBARES VERMÖGEN", "52'500")
    ]
    
    y = 750
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, main_data[0][0]); c.drawString(150, y, main_data[0][1]); c.drawString(450, y, main_data[0][2])
    y -= 25
    c.setFont("Helvetica", 10)
    for row in main_data[1:]:
        c.drawString(50, y, row[0]); c.drawString(150, y, row[1]); c.drawString(450, y, row[2])
        y -= 18
        
    # --- YENİ SAYFA: EK FORMVE DÖKÜMLER (Beilagen) ---
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "BEILAGEN ZUR STEUERERKLÄRUNG 2025")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 760, "1. Wertschriften- und Guthabenverzeichnis (Form 340)")
    c.setFont("Helvetica", 10)
    c.drawString(50, 740, "• ZKB Bankguthaben (Konto-Nr: ...): 45'000 CHF | Ertrag: 250 CHF")
    c.drawString(50, 725, "• Aktien / Fonds (Portfolio): 12'500 CHF | Ertrag (Dividende): 200 CHF")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 680, "2. Schuldenverzeichnis (Form 355)")
    c.setFont("Helvetica", 10)
    c.drawString(50, 660, "• Privatkredit (Bank): Restschuld per 31.12.2025 = 5'000 CHF")
    c.drawString(50, 645, "• Davon abzugsfähiger Schuldzinsen (Ziff. 12): [Kontrol Edilecek]")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 600, "3. Abzüge Detaildökümanı (Ziff. 18 Detayı)")
    c.setFont("Helvetica", 10)
    c.drawString(50, 580, "• Berufsauslagen P1+P2 (Ziff. 11.1/2): 6'400 CHF")
    c.drawString(50, 565, "• Säule 3a P1+P2 (Ziff. 14.1/2): 14'516 CHF")
    c.drawString(50, 550, "• Versicherungsprämien / Krankenkasse (Ziff. 15): 5'800 CHF")
    c.drawString(50, 535, "• Kinderbetreuung / Kita (Ziff. 16.6): 12'000 CHF")
    c.drawString(50, 520, "• Sonderabzug bei Erwerbstätigkeit (Ziff. 17): 6'100 CHF")

    c.save()
    return file_path

def send_email():
    file_path = create_comprehensive_tax_pdf()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025 - KOMPLETT PAKET"
    msg.attach(MIMEText("Zürih 2025 Form 300 ve ek formları (Wertschriften/Schulden dökümleri) içeren kapsamlı PDF ektedir.", 'plain', 'utf-8'))
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025_Komplett.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
