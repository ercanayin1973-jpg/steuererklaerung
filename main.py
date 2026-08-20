from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def create_official_pdf():
    file_path = "Steuererklaerung_2025_Zuerich_Final.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 820, "STEUERERKLÄRUNG 2025 - KANTON ZÜRICH (FORM 300)")
    
    # 2025 Resmi Ziffer Hesaplama Zinciri
    z7_total_einkunfte = 170450
    z18_total_abzuge = 44816
    z21_netto = z7_total_einkunfte - z18_total_abzuge
    z23_rein = z21_netto - 1700 
    z25_steuerbar_eink = z23_rein - 9300 - 2800 
    
    data = [
        ("Ziff.", "Beschreibung", "CHF"),
        ("1.1", "Haupterwerb Person 1+2", "170'000"),
        ("4.1", "Wertschriftenertrag", "450"),
        ("7", "Total der Einkünfte", str(z7_total_einkunfte)),
        ("18", "Total der Abzüge", str(z18_total_abzuge)),
        ("21", "Nettoeinkommen", str(z21_netto)),
        ("23", "Reineinkommen", str(z23_rein)),
        ("24.1", "Kinderabzug (Noah)", "9'300"),
        ("24.3", "Ehegattenabzug (Bund)", "2'800"),
        ("25", "Steuerbares Einkommen", str(z25_steuerbar_eink)),
        ("33", "Total Vermögenswerte", "57'500"),
        ("34", "Schulden (Privatkredit)", "-5'000"),
        ("35", "Steuerbares Vermögen", "52'500")
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
    msg.attach(MIMEText("Resmi Zürih 2025 standartlarına uygun vergi beyannamesi ektedir.", 'plain', 'utf-8'))
    
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
