import os
import requests
from bs4 import BeautifulSoup
import feedparser
import datetime
import smtplib
from email.message import EmailMessage
from transformers import pipeline

# AYARLAR
KEYWORDS = ["artificial intelligence", "LLM", "machine learning"]
MAX_HABER = 3 
MAIL_ADRESI = os.getenv("MAIL_ADRESI")
MAIL_SIFRESI = os.getenv("MAIL_SIFRESI")


summarizer = pipeline("summarization", model="google/pegasus-xsum")

def get_smart_summary(text):
    
    if not text or len(text.split()) < 100:
        return "Inhalt is too short."
    
    input_text = text[:3500]
    
    summary = summarizer(
        input_text, 
        max_length=250,   
        min_length=150,   
        do_sample=True,   
        temperature=0.8   
    )
    
    return summary[0]['summary_text'].strip()

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
                # 1. URL'ye git ve makaleyi çek
                r = requests.get(entry.link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")
                
                # Sadece asıl metni al (reklamları ele)
                paragraphs = [p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 60]
                full_text = " ".join(paragraphs)

                # 2. Eğer teknoloji içeriyorsa özetle
                if any(k in full_text.lower() for k in KEYWORDS):
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
        msg['Subject'] = f"🚀 Günlük Akıllı Haber Makale Analizleri - {datetime.date.today()}"
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
