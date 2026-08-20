import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MY_EMAIL = os.environ.get("MY_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def create_pdf_report(report_text, filename="tax_report.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "İsviçre Vergi Beyannamesi Raporu")
    c.setFont("Helvetica", 12)
    
    text_object = c.beginText(100, 750)
    for line in report_text.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()
    return filename

def process_tax_documents():
    raw_expenses = "- 15.03.2026: Tren aboneliği - 1'200 CHF\n- 10.05.2026: Dişçi - 450 CHF"
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=f"Bu harcamaları İsviçre vergi standartlarına göre kategorize et: {raw_expenses}"
    )
    return response.text

def send_email_with_pdf(report_text):
    pdf_path = create_pdf_report(report_text)
    
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = "🧾 Profesyonel İsviçre Vergi Raporunuz"
    msg.attach(MIMEText("Ekli dosyada vergi beyannamesi taslağınızı bulabilirsiniz.", 'plain'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=Vergi_Raporu.pdf")
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(MY_EMAIL, EMAIL_PASSWORD)
    server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
    server.quit()

if __name__ == "__main__":
    report = process_tax_documents()
    send_email_with_pdf(report)
