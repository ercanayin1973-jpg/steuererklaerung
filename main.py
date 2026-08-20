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
    # Profesyonel PDF şablonu (Türkçe karakter uyumlu Paragraph yapısı)
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    # Başlık stili
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=15,
        textColor=colors_HexColor = '#1A365D'
    )
    
    # Normal metin stili
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )

    elements.append(Paragraph("Isvicre Vergi Beyannamesi Raporu", title_style))
    elements.append(Spacer(1, 10))

    # Metni satır satır güvenli paragraflara bölüyoruz
    for line in report_text.split('\n'):
        if line.strip():
            # Bozuk karakter ihtimaline karşı temizleme
            clean_line = line.replace('|', '-').replace('**', '')
            elements.append(Paragraph(clean_line, body_style))

    doc.build(elements)
    return filename

def process_tax_documents():
    raw_expenses = """
    - Es 1 (Ahmet): Berufsauslagen (Yol/Tren) - 1'500 CHF
    - Es 2 (Ayse): Weiterbildung (Mesleki Kurs) - 1'200 CHF
    - Ortak: Krankheitskosten (Saglik masraflari) - 800 CHF
    - Ortak: Spenden (Bagislar) - 250 CHF
    """
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Sen Isvicre vergi mevzuatina hakim uzman bir vergi asistanisin.
    Musterimiz evli bir cifttir. Isvicre'nin evli ciftler icin gecerli ortak vergi tarifesine gore asagidaki harcamalari kategorize et.
    Raporu hazirlarken Turkce karakter kullaniminda sikinti cikarmayacak duz metin ve liste formatinda yaz (ozel simgeler kullanma).

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
    msg['Subject'] = "🧾 Isvicre Ortak Vergi Beyannamesi (Evli Ciftler)"
    msg.attach(MIMEText("Ekli dosyada evli ciftler icin hazirlanan vergi taslagini bulabilirsiniz.", 'plain', 'utf-8'))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=Vergi_Raporu.pdf")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("PDF raporu basariyla gonderildi!")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    report = process_tax_documents()
    send_email_with_pdf(report)
