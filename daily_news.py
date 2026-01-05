
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
def basit_ozetle(text):
    """Eğer AI çalışmazsa devreye girecek olan garantili özetleyici."""
    sentences = text.split('.')
    summary = ". ".join(sentences[:2]) + "."
    return f"(Hızlı Özet): {summary}"

def get_smart_summary(text):
    if not text or len(text.split()) < 80:
        return "İçerik analiz için çok kısa."
    
    API_URL = "https://api-inference.huggingface.co/models/slauw87/bart_summarisation"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    input_text = text[:3000]
    
    # "wait_for_model": True -> Model uykudaysa uyandırana kadar bekle
    payload = {
        "inputs": input_text,
        "options": {"wait_for_model": True}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        output = response.json()
        
        if isinstance(output, list) and len(output) > 0:
            return output[0].get('summary_text', 'Özet hazır değil.').strip()
        return "Şu an analiz yapılamadı, model yükleniyor olabilir."
    except Exception as e:
        return f"Bağlantı hatası: {e}"

def main():
    feeds = [ "https://medium.com/feed/topic/technology"]
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

                if any(k.lower() in full_text.lower() for k in KEYWORDS):
                    print(f"Eşleşme Bulundu: {entry.title}")
                    ozet = get_smart_summary(full_text)
                    secilenler.append({"title": entry.title, "link": entry.link, "summary": ozet})
            except Exception as e:
                print(f"Haber çekme hatası: {e}")

    if secilenler:
        msg = EmailMessage()
        msg['Subject'] = f"🚀 Günlük Akıllı Haber Analizleri - {datetime.date.today()}"
        msg['From'] = MAIL_ADRESI
        msg['To'] = MAIL_ADRESI
        
        icerik = "Seçtiğin anahtar kelimelere göre hazırlanan bugünkü analizler:\n\n"
        for i, h in enumerate(secilenler, 1):
            icerik += f"{i}. {h['title']}\n🔗 {h['link']}\n📝 ANALİZ: {h['summary']}\n\n" + "-"*40 + "\n\n"
        
        msg.set_content(icerik)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MAIL_ADRESI, MAIL_SIFRESI)
            smtp.send_message(msg)
        print("Bülten başarıyla gönderildi!")
    else:
        print("Anahtar kelimelerle eşleşen yeni haber bulunamadı.")

if __name__ == "__main__":
    main()



