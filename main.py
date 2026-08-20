from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_official_pdf():
    file_path = "Steuererklaerung_2025_Zuerich_Detail.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 820, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH (FORM 300)")
    
    # Resmi Hesaplama Zinciri
    einkunfte = 170450
    # İndirimlerin detaylı dökümü (Senin analizine göre)
    abzuge = {
        "11.1": 3200, "11.2": 3200, "14.1": 7258, "14.2": 7258,
        "15": 5800, "16.6": 12000, "17": 6100
    }
    z18_total = sum(abzuge.values())
    z21_netto = einkunfte - z18_total
    z23_rein = z21_netto - 1700 # Krankheits/Spenden
    z25_steuerbar_eink = z23_rein - 9300 - 2800
    
    data = [
        ("Ziff.", "Beschreibung", "Betrag (CHF)"),
        ("1.1", "Haupterwerb Person 1+2", "170'000"),
        ("4.1", "Wertschriftenertrag", "450"),
        ("7", "Total der Einkünfte", str(einkunfte)),
        ("11.1/2", "Berufsauslagen P1+P2", str(abzuge["11.1"]+abzuge["11.2"])),
        ("14.1/2", "Säule 3a P1+P2", str(abzuge["14.1"]+abzuge["14.2"])),
        ("15", "Versicherungsprämien", str(abzuge["15"])),
        ("16.6", "Kinderbetreuung (Kita)", str(abzuge["16.6"])),
        ("17", "Sonderabzug", str(abzuge["17"])),
        ("18", "Total der Abzüge", str(z18_total)),
        ("21", "Nettoeinkommen", str(z21_netto)),
        ("23", "Reineinkommen", str(z23_rein)),
        ("24.1", "Kinderabzug", "9'300"),
        ("24.3", "Ehegattenabzug (Bund)", "2'800"),
        ("25", "STEUERBARES EINKOMMEN", str(z25_steuerbar_eink)),
        ("34", "Schulden (Privatkredit)", "-5'000"),
        ("35", "STEUERBARES VERMÖGEN", "52'500")
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
    msg['Subject'] = "OFFIZIELLE STEUERERKLÄRUNG 2025 - DETAILLIERT"
    msg.attach(MIMEText("İsteğin üzerine Zürih 2025 resmi Ziffer yapısına göre detaylandırılmış beyanname verileri ektedir.", 'plain', 'utf-8'))
    
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
