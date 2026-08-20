import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MY_EMAIL = os.environ.get("MY_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def process_tax_documents():
    raw_expenses = """
    - 15.03.2026: Zürih Tren İstasyonu yıllık abonelik (Berufsauslagen / Yol) - 1'200 CHF
    - 10.05.2026: Dişçi kontrol ve tedavi faturası (Krankheitskosten) - 450 CHF
    - 20.08.2026: İsviçre Kızılayı bağış makbuzu (Spenden) - 100 CHF
    - 12.11.2026: Mesleki Almanca kursu faturası (Weiterbildung) - 800 CHF
    """
    
    # Doğrudan API anahtarı ile istemciyi başlatıyoruz
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Sen İsviçre vergi mevzuatına (Steuererklärung) hakim profesyonel bir dijital vergi asistanısın.
    Aşağıda bir müşterinin yıl boyunca topladığı dağınık harcama listesi bulunmaktadır.
    Bu harcamaları İsviçre vergi dairesinin standart kategorilerine göre (Örn: Berufsauslagen, Krankheitskosten, Spenden, Weiterbildung) ayır.
    Müşterinin vergi beyannamesine doğrudan yazabileceği, net, anlaşılır ve düzenli bir vergi özet raporu hazırla.

    Dağınık Harcama Listesi:
    {raw_expenses}
    """
    
    # Standart Developer API model adı
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

def send_tax_report(report_content):
    if not MY_EMAIL or not EMAIL_PASSWORD:
        print("E-posta veya şifre eksik!")
        return

    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL
    msg['Subject'] = "🧾 İsviçre Vergi Beyannamesi Otomatik Taslak Raporu"

    body = f"""
    İsviçre Vergi Asistanı - Otomatik Sınıflandırma Raporu
    --------------------------------------------------
    {report_content}
    
    --------------------------------------------------
    Bu rapor sistem tarafından otomatik olarak oluşturulmuştur.
    """
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASSWORD)
        server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        server.quit()
        print("Vergi raporu başarıyla e-posta adresinize gönderildi!")
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    print("Vergi belgeleri analiz ediliyor...")
    report = process_tax_documents()
    send_tax_report(report)
