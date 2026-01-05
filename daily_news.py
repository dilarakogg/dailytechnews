import os
import requests
from bs4 import BeautifulSoup
import feedparser
import datetime
import smtplib
from email.message import EmailMessage

# AYARLAR
KEYWORDS = ["artificial intelligence", "llm", "machine learning"]
MAX_HABER = 3 
MAIL_ADRESI = os.getenv("MAIL_ADRESI")
MAIL_SIFRESI = os.getenv("MAIL_SIFRESI")
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def get_smart_summary(text):
    if not text or len(text.split()) < 50:
        return "Inhalt is too short."
    
    # Pegasus-XSUM API Kullanımı (pipeline yerine bulut çağrısı)
    API_URL = "https://api-inference.huggingface.co/models/google/pegasus-xsum"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Metni çok uzunsa keselim (API sınırı için)
    input_text = text[:3000]
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": input_text}, timeout=20)
        output = response.json()
        
        if isinstance(output, list) and len(output) > 0:
            return output[0].get('summary_text', 'Summary not available.').strip()
        else:
            return "Özet oluşturulamadı (Model yükleniyor olabilir)."
    except Exception as e:
        return f"API Hatası: {e}"

def main():
    feeds = [
        "https://www.technologyreview.com/feed/",
        "https://medium.com/feed/topic/technology"
    ]
    
    secilenler = []

    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if len(secilenler) >= MAX_HABER: break
            
            try:
                r = requests.get(entry.link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")
                
                paragraphs = [p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 60]
                full_text = " ".join(paragraphs)

                # Anahtar kelime kontrolü
                if any(k.lower() in full_text.lower() for k in KEYWORDS):
                    print(f"Özetleniyor: {entry.title}")
                    ozet = get_smart_summary(full_text)
                    
                    secilenler.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": ozet
                    })
            except Exception as e:
                print(f"Hata: {e}")

    if secilenler:
        msg = EmailMessage()
        msg['Subject'] = f"🚀 Günlük Akıllı Haber Analizleri - {datetime.date.today()}"
        msg['From'] = MAIL_ADRESI
        msg['To'] = MAIL_ADRESI
        
        icerik = "Bugünün öne çıkan haberlerinden senin için derlediğim derin analizler:\n\n"
        for i, h in enumerate(secilenler, 1):
            icerik += f"{i}. {h['title']}\n🔗 {h['link']}\n📝 ANALİZ: {h['summary']}\n\n" + "-"*40 + "\n\n"
        
        msg.set_content(icerik)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MAIL_ADRESI, MAIL_SIFRESI)
            smtp.send_message(msg)
        print("Bülten başarıyla gönderildi!")

if __name__ == "__main__":
    main()
