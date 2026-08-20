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
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Isvicre Evli Ciftler Vergi Beyannamesi Raporu")
    c.setFont("Helvetica", 10)
    
    text_object = c.beginText(50, 770)
    for line in report_text.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()
    return filename

def process_tax_documents():
    raw_expenses = """
    - Eş 1 (Ahmet): Berufsauslagen (Yol/Tren) - 1'500 CHF
    - Eş 2 (Ayşe): Weiterbildung (Mesleki Kurs) - 1'200 CHF
    - Ortak: Krankheitskosten (Diş/Sağlık masrafları) - 800 CHF
    - Ortak: Spenden (Bağışlar) - 250 CHF
    """
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Sen İsviçre vergi mevzuatına (Steuererklärung) hakim uzman bir vergi asistanısın.
    Müşterimiz **evli bir çifttir**. İsviçre'nin evli çiftler için geçerli ortak vergi tarifesine (Verheiratetentarif) göre aşağıdaki harcamaları kategorize et.
    Eşlerin masraflarını ve ortak masrafları ayrı ayrı tasnif ederek, vergi dairesine sunulabilecek düzenli bir taslak özet rapor hazirla.

    Harcama Listesi:
    {raw_expenses}
    """
    
    response = client.models.generate_content(
        model='gemini-3.7-flash',
        contents=prompt,
    )
    return response.text

def send_email_with_pdf(report_text):
    pdf_path = create_pdf_report(report_text)
    
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = "🧾 İsviçre Ortak Vergi Beyannamesi (Evli Çiftler)"
    msg.attach(MIMEText("Ekli dosyada evli çiftler için hazırlanan vergi taslağını bulabilirsiniz.", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=Evli_Ciftler_Vergi_Raporu.pdf")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("PDF raporu başarıyla gönderildi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    report = process_tax_documents()
    send_email_with_pdf(report)
