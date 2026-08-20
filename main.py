from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_complete_steuererklaerung():
    file_path = "Steuererklaerung_2025_Form300_Resmi.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # --- SAYFA 1: FORM 300 (Ana Vergi Özeti ve Ziffer Zinciri) ---
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, 800, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH (FORM 300)")
    
    einkunfte = 170450  # Ziff. 7
    abzuge = {
        "11.1/2": 6400,   # Berufsauslagen P1+P2
        "12": 150,        # Schuldzinsen (Privatkredit)
        "14.1/2": 14516,  # Säule 3a P1+P2
        "15": 5800,       # Versicherungsprämien
        "16.2": 500,      # Weiterbildung
        "16.3": 150,      # Wertschriftenverwaltung
        "16.6": 12000,    # Fremdbetreuung Kinder (Kita)
        "17": 6100        # Sonderabzug Erwerbstätigkeit
    }
    z18_total = sum(abzuge.values()) # 45'616 CHF
    z21_netto = einkunfte - z18_total # 124'834 CHF
    
    z22_1 = 1200 # Krankheitskosten
    z22_2 = 500  # Spenden
    z23_rein = z21_netto - (z22_1 + z22_2) # 123'134 CHF
    
    # Ziff. 25 Ayrımı (Kanton vs. Bund)
    z25_kanton = z23_rein - 9300        # Kanton Zürich (Sadece Kinderabzug 9'300) -> 113'834 CHF
    z25_bund = z23_rein - 6800 - 2800   # Bundessteuer (Kinderabzug 6'800 + Ehegattenabzug 2'800) -> 113'534 CHF
    
    main_data = [
        ("Ziff.", "Beschreibung (Form 300)", "CHF"),
        ("1.1", "Haupterwerb Person 1 & 2", "170'000"),
        ("4.1", "Wertschriftenertrag (Form 340)", "450"),
        ("7", "Total der Einkünfte", str(einkunfte)),
        ("18", "Total der Abzüge (Detail)", str(z18_total)),
        ("21", "Nettoeinkommen", str(z21_netto)),
        ("22.1", "Krankheits- und Unfallkosten", str(z22_1)),
        ("22.2", "Gemeinnützige Zuwendungen (Spenden)", str(z22_2)),
        ("23", "Reineinkommen", str(z23_rein)),
        ("24.1", "Kinderabzug Noah (Kanton: 9'300 / Bund: 6'800)", "9'300 / 6'800"),
        ("24.3", "Ehegattenabzug (Nur Bund)", "2'800"),
        ("25", "STEUERBARES EINKOMMEN (Kanton Zürich)", str(z25_kanton)),
        ("25", "STEUERBARES EINKOMMEN (Direkte Bundessteuer)", str(z25_bund)),
        ("33", "Total der Vermögenswerte", "57'500"),
        ("34", "Schulden (Form 355 - Privatkredit)", "-5'000"),
        ("35", "STEUERBARES VERMÖGEN", "52'500")
    ]
    
    y = 750
    c.setFont("Helvetica-Bold", 8)
    c.drawString(50, y, main_data[0][0]); c.drawString(120, y, main_data[0][1]); c.drawString(420, y, main_data[0][2])
    y -= 18
    c.setFont("Helvetica", 8)
    for row in main_data[1:]:
        c.drawString(50, y, row[0]); c.drawString(120, y, row[1]); c.drawString(420, y, row[2])
        y -= 15
        
    # --- SAYFA 2: EK FORMLAR VE DETAYLAR ---
    c.showPage()
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, 800, "DETAILANALYSE UND BEILAGEN ZUR STEUERERKLÄRUNG")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 760, "1. Abzüge Detail (Ziff. 18 Total: 45'616 CHF)")
    c.setFont("Helvetica", 8)
    c.drawString(50, 742, "• Berufsauslagen P1+P2 (Ziff. 11.1/2): 6'400 CHF")
    c.drawString(50, 728, "• Schuldzinsen Privatkredit (Ziff. 12): 150 CHF")
    c.drawString(50, 714, "• Säule 3a P1+P2 (Ziff. 14.1/2): 14'516 CHF")
    c.drawString(50, 700, "• Versicherungsprämien (Ziff. 15): 5'800 CHF")
    c.drawString(50, 686, "• Weiterbildung (Ziff. 16.2) & Depotgebühr (Ziff. 16.3): 650 CHF")
    c.drawString(50, 672, "• Kita / Fremdbetreuung (Ziff. 16.6): 12'000 CHF")
    c.drawString(50, 658, "• Sonderabzug Erwerbstätigkeit (Ziff. 17): 6'100 CHF")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 620, "2. Wertschriften (Form 340) & Schulden (Form 355)")
    c.setFont("Helvetica", 8)
    c.drawString(50, 602, "• ZKB Konto & Aktien (Vergi Değeri): 57'500 CHF -> Ziff. 33")
    c.drawString(50, 588, "• Privatkredit Restschuld (Vergi Değeri): -5'000 CHF -> Ziff. 34")

    c.save()
    return file_path

def send_email():
    file_path = create_complete_steuererklaerung()
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025 - KANTON & BUND SEperat"
    msg.attach(MIMEText("Zürih 2025 Form 300, Kanton/Bund Ziffer 25 ayrımları ve ek formlar dahil güncel paket ektedir.", 'plain', 'utf-8'))
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="Steuererklaerung_2025_Kanton_Bund.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
