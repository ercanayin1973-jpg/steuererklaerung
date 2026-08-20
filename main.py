from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

def create_dynamic_tax_pdf():
    # BURADAN KANTONU DEĞİŞTİREBİLİRSİN: "Zuerich", "Aargau", "Basel"
    kanton = "Aargau"  # Seçenekler: "Zuerich", "Aargau", "Basel"
    
    # Kanton bazlı özel oranlar, portallar ve indirim limitleri
    kanton_verileri = {
        "Zuerich": {
            "ad": "Kanton Zürich", 
            "portal": "ZHprivateTax",
            "kinderabzug": "9'300",
            "steuerfuss_info": "Kantonales Form 300 / 2025"
        },
        "Aargau": {
            "ad": "Kanton Aargau", 
            "portal": "Steuerportal AG",
            "kinderabzug": "8'500", # Aargau kantonu için örnek güncel limit
            "steuerfuss_info": "Steuererklärung AG / 2025"
        },
        "Basel": {
            "ad": "Kanton Basel-Stadt", 
            "portal": "TaxMe BS",
            "kinderabzug": "9'000", # Basel-Stadt kantonu için örnek güncel limit
            "steuerfuss_info": "Steuererklärung BS / 2025"
        }
    }
    
    info = kanton_verileri.get(kanton, kanton_verileri["Zuerich"])
    file_path = f"Steuererklaerung_2025_{kanton}.pdf"
    
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=10
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )

    # --- SAYFA 1: TABLO FORMATINDA VERGİ ÖZETİ ---
    story.append(Paragraph(f"STEUERERKLÄRUNG 2025 - {info['ad'].upper()}", title_style))
    story.append(Paragraph(f"Offizielle Deklaration | Portal: {info['portal']} | {info['steuerfuss_info']}", styles['Normal']))
    story.append(Spacer(1, 10))
    
    raw_data = [
        ["Ziff.", "Beschreibung", "CHF"],
        ["1.1", "Haupterwerb Person 1 & 2 (Lohnausweis)", "170'000"],
        ["4.1", "Wertschriftenertrag (Zinsen / Dividenden)", "450"],
        ["7", "Total der Einkünfte", "170'450"],
        ["11.1/2", "Berufsauslagen P1 + P2", "-6'400"],
        ["12", "Schuldzinsen (Privatkredit)", "-150"],
        ["14.1/2", "Säule 3a (Maximalbeitrag P1 + P2)", "-14'516"],
        ["15", "Versicherungsprämien / Krankenkasse", "-5'800"],
        ["16.2", "Berufsorientierte Weiterbildungskosten", "-500"],
        ["16.3", "Wertschriftenverwaltung (Depotgebühren)", "-150"],
        ["16.6", "Fremdbetreuung Kinder (Kita Noah)", "-12'000"],
        ["17", "Sonderabzug Erwerbstätigkeit (Zweiverdiener)", "-6'100"],
        ["18", "Total der Abzüge", "-45'616"],
        ["21", "Nettoeinkommen", "124'834"],
        ["22.1", "Krankheits- und Unfallkosten", "-1'200"],
        ["22.2", "Gemeinnützige Zuwendungen (Spenden)", "-500"],
        ["23", "Reineinkommen", "123'134"],
        ["24.1", f"Kinderabzug Noah (Kanton: {info['kinderabzug']} / Bund: 6'800)", f"{info['kinderabzug']} / 6'800"],
        ["24.3", "Ehegattenabzug (Direkte Bundessteuer)", "2'800"],
        ["25", f"STEUERBARES EINKOMMEN ({kanton})", "113'834"],
        ["25", "STEUERBARES EINKOMMEN (Bund)", "113'534"],
        ["33", "Total der Vermögenswerte", "57'500"],
        ["34", "Schulden (Privatkredit)", "-5'000"],
        ["35", "STEUERBARES VERMÖGEN", "52'500"]
    ]
    
    table_data = []
    table_data.append([
        Paragraph(raw_data[0][0], header_style),
        Paragraph(raw_data[0][1], header_style),
        Paragraph(raw_data[0][2], header_style)
    ])
    
    for row in raw_data[1:]:
        table_data.append([
            Paragraph(row[0], cell_style),
            Paragraph(row[1], cell_style),
            Paragraph(row[2], cell_style)
        ])
        
    t = Table(table_data, colWidths=[40, 400, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    story.append(t)
    story.append(PageBreak())
    
    # --- SAYFA 2: EK FORMLAR VE KANTONAL BİLGİLER ---
    story.append(Paragraph(f"BEILAGEN & KANTONALE HINWEISE ({info['ad'].upper()})", title_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>1. Wertschriften- und Guthabenverzeichnis</b>", styles['Heading3']))
    story.append(Paragraph("• Bankguthaben & Wertschriften (Steuerwert Total): 57'500 CHF -> Ziff. 33", styles['Normal']))
    story.append(Paragraph("• Bruttoerträge (Zinsen / Dividenden): 450 CHF -> Ziff. 4.1", styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>2. Schuldenverzeichnis</b>", styles['Heading3']))
    story.append(Paragraph("• Privatkredit Restschuld per 31.12.2025: 5'000 CHF -> Ziff. 34", styles['Normal']))
    story.append(Paragraph("• Abzugsfähige Schuldzinsen: 150 CHF -> Ziff. 12", styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>3. Spezifische Bestimmungen für {info['ad']}</b>", styles['Heading3']))
    story.append(Paragraph(f"• Die offizielle Einreichung erfolgt über das Online-Portal: {info['portal']}.", styles['Normal']))
    story.append(Paragraph(f"• Kantonales Kinderabzugslimit wurde mit {info['kinderabzug']} CHF angerechnet.", styles['Normal']))

    doc.build(story)
    return file_path, kanton

def send_email():
    file_path, secilen_kanton = create_dynamic_tax_pdf()
    
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("MY_EMAIL")
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = f"OFFIZIELLE STEUERERKLÄRUNG 2025 - {secilen_kanton.upper()}"
    msg.attach(MIMEText(f"Seçilen kanton ({secilen_kanton}) kurallarına göre hazırlanan çizgili tablo formatındaki vergi taslağı ektedir.", 'plain', 'utf-8'))
    
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
