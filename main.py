from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_dynamic_tax_pdf(kanton="Zuerich"):
    file_path = f"Steuererklaerung_2025_{kanton}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # Kanton bazlı başlık ve özel notlar
    kanton_adlari = {
        "Zuerich": "Kanton Zürich (Form 300 / ZHprivateTax)",
        "Aargau": "Kanton Aargau (Steuererklärung AG)",
        "Basel": "Kanton Basel-Stadt (Steuererklärung BS)"
    }
    
    baslik = kanton_adlari.get(kanton, "Kanton Zürich")
    
    # --- SAYFA 1: ANA VERGİ ÖZETİ ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 805, f"STEUERERKLÄRUNG 2025 - {baslik.upper()}")
    c.setFont("Helvetica", 9)
    c.drawString(50, 790, f"Offizielle Deklaration für den Wohnsitzkanton: {kanton}")
    
    main_data = [
        ("Ziff.", "Beschreibung", "CHF"),
        ("1.1", "Haupterwerb Person 1 & 2 (Lohnausweis)", "170'000"),
        ("4.1", "Wertschriftenertrag (Zinsen / Dividenden)", "450"),
        ("7", "Total der Einkünfte", "170'450"),
        ("11.1/2", "Berufsauslagen P1 + P2", "-6'400"),
        ("12", "Schuldzinsen (Privatkredit)", "-150"),
        ("14.1/2", "Säule 3a (Maximalbeitrag P1 + P2)", "-14'516"),
        ("15", "Versicherungsprämien / Krankenkasse", "-5'800"),
        ("16.2", "Berufsorientierte Weiterbildungskosten", "-500"),
        ("16.3", "Wertschriftenverwaltung (Depotgebühren)", "-150"),
        ("16.6", "Fremdbetreuung Kinder (Kita Noah)", "-12'000"),
        ("17", "Sonderabzug Erwerbstätigkeit (Zweiverdiener)", "-6'100"),
        ("18", "Total der Abzüge", "-45'616"),
        ("21", "Nettoeinkommen", "124'834"),
        ("22.1", "Krankheits- und Unfallkosten", "-1'200"),
        ("22.2", "Gemeinnützige Zuwendungen (Spenden)", "-500"),
        ("23", "Reineinkommen", "123'134"),
        ("24.1", "Kinderabzug (Kantonale Regelung)", "9'300"),
        ("24.3", "Ehegattenabzug (Direkte Bundessteuer)", "2'800"),
        ("25", "STEUERBARES EINKOMMEN (Kanton)", "113'834"),
        ("25", "STEUERBARES EINKOMMEN (Bund)", "113'534"),
        ("33", "Total der Vermögenswerte", "57'500"),
        ("34", "Schulden (Privatkredit)", "-5'000"),
        ("35", "STEUERBARES VERMÖGEN", "52'500")
    ]
    
    y = 765
    c.setFont("Helvetica-Bold", 8)
    c.drawString(50, y, main_data[0][0])
    c.drawString(110, y, main_data[0][1])
    c.drawString(440, y, main_data[0][2])
    y -= 14
    
    c.setFont("Helvetica", 8)
    for row in main_data[1:]:
        c.drawString(50, y, row[0])
        c.drawString(110, y, row[1])
        c.drawString(440, y, row[2])
        y -= 13
        
    # --- SAYFA 2: KANTONAL ÖZEL AÇIKLAMALAR ---
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 805, f"KANTONALE HINWEISE & BEILAGEN ({kanton.upper()})")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 765, "1. Wertschriften- und Guthabenverzeichnis")
    c.setFont("Helvetica", 9)
    c.drawString(50, 747, "• Bankguthaben & Wertschriften (Steuerwert Total): 57'500 CHF -> Ziff. 33")
    c.drawString(50, 732, "• Bruttoerträge (Zinsen / Dividenden): 450 CHF -> Ziff. 4.1")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 695, "2. Schuldenverzeichnis")
    c.setFont("Helvetica", 9)
    c.drawString(50, 677, "• Privatkredit Restschuld per 31.12.2025: 5'000 CHF -> Ziff. 34")
    c.drawString(50, 662, "• Abzugsfähige Schuldzinsen: 150 CHF -> Ziff. 12")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 625, f"3. Spezifische Hinweise für {kanton}")
    c.setFont("Helvetica", 9)
    c.drawString(50, 607, f"• Die Steuererklärung 2025 für {kanton} berücksichtigt die kantonalen Abzugslimiten.")
    c.drawString(50, 592, "• Belege für Berufsauslagen, Säule 3a und Kita vollständig digital bereitstellen.")
    c.drawString(50, 577, f"• Offizielles Einrichtungsportal des Kantons ({kanton}) nutzen.")

    c.save()
    return file_path

def send_email():
    # Buradan istediğin kantonu seçebilirsin: "Zuerich", "Aargau", "Basel"
    secilen_kanton = os.environ.get("KANTON", "Zuerich")
    file_path = create_dynamic_tax_pdf(secilen_kanton)
    
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = f"OFFIZIELLE STEUERERKLÄRUNG 2025 - {secilen_kanton.upper()}"
    msg.attach(MIMEText(f"{secilen_kanton} kantonu 2025 vergi beyannamesi taslağı ve ekleri ektedir.", 'plain', 'utf-8'))
    
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=f"Steuererklaerung_2025_{secilen_kanton}.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
