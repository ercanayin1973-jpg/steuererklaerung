import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email():
    try:
        print("DEBUG: Süreç başlıyor...")
        
        # 1. Veri oluştur
        data = [["Ziffer", "Beschreibung", "Betrag"], ["Test", "Test", 0]]
        with open("test.csv", "w", newline="") as f:
            csv.writer(f).writerows(data)
        print("DEBUG: CSV dosyası oluşturuldu.")

        # 2. Mail hazırla
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("MY_EMAIL")
        msg['To'] = os.environ.get("MY_EMAIL")
        msg['Subject'] = "DEBUG TEST MAIL"
        msg.attach(MIMEText("Bu bir test mailidir.", 'plain'))

        # 3. SMTP Bağlantısı
        print("DEBUG: SMTP sunucusuna bağlanılıyor...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("DEBUG: TLS başlatıldı. Giriş deneniyor...")
        
        server.login(os.environ.get("MY_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
        print("DEBUG: Giriş başarılı!")
        
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        print("DEBUG: Mail gönderildi!")
        server.quit()
        print("DEBUG: İşlem başarıyla tamamlandı.")

    except Exception as e:
        print(f"DEBUG KRİTİK HATA: {e}")

if __name__ == "__main__":
    send_email()
