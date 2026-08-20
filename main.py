import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google import genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MY_EMAIL = os.environ.get("MY_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def create_pdf_report(report_text, filename="tax_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=15,
        spaceAfter=12
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    elements.append(Paragraph("Isvicre Vergi Beyannamesi Otomatik Raporu", title_style))
    elements.append(Spacer(1, 10))

    for line in report_text.split('\n'):
        if line.strip():
            clean_line = line.replace('|', '-').replace('**', '')
            elements.append(Paragraph(clean_line, body_style))

    doc.build(elements)
    return filename

def process_tax_documents():
    # Buradan müşterinin durumunu "Verheiratet" (Evli) veya "Ledig" (Bekar) yapabilirsin
    medeni_durum = "Verheiratet"  
    
    raw_expenses = """
    - Yol/Ulasim Masrafi (Berufsauslagen): 1'500 CHF
    - Saglik Masraflari (Krankheitskosten): 800 CHF
    - Bagislar (Spenden): 250 CHF
    """
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    if medeni_durum == "Verheiratet":
        tarif_aciklamasi = "Musteri EVLI bir cifttir. Isvicre evli ciftler ortak vergi tarifesine (Verheiratetentarif) gore hesapla."
    else:
        tarif_aciklamasi = "Musteri BEKARDIR (Ledig). Isvicre bekar vergi tarifesine (Alleinstehenden-Tarif) gore hesapla."

    prompt = f"""
    Sen Isvicre vergi mevzuatina hakim uzman bir vergi asistanisin.
    Durum: {tarif_aciklamasi}
    Asagidaki harcamalari Isvicre vergi standartlarina gore kategorize et ve duzenli bir ozet rapor hazirla.
    Turkce karakter sorununa yol acmayacak duz metin formatinda yaz.

    Harcama Listesi:
    {raw_expenses}
    """
    
    # Güncel ve resmi model adı
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text, medeni_durum

def send_email_with_pdf():
    report_text, durum = process_tax_documents()
    pdf_path = create_pdf_report(report_text)
    
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = f"🧾 Isvicre Vergi Raporu ({durum})"
    msg.attach(MIMEText(f"Musterinin medeni durumuna ({durum}) gore hazirlanan vergi taslagi ektedir.", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=Vergi_Raporu_{durum}.pdf")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("Ortak vergi raporu basariyla gonderildi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    send_email_with_pdf()
