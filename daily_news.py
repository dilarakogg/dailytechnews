import os
import requests
from bs4 import BeautifulSoup
import feedparser
import datetime
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from transformers import pipeline

# .env yükle
load_dotenv()

# AYARLAR
KEYWORDS = ["yapay zeka", "teknoloji"] # Burayı istediğin gibi değiştir
MAX_HABER = 5
G_MAIL = os.getenv("MAIL_ADRESI")
G_SIFRE = os.getenv("MAIL_SIFRESI")

# MODELLER (Senin ilk kodundaki modeller)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def mail_at(liste):
    msg = EmailMessage()
    msg['Subject'] = f"Günlük Bülten - {datetime.date.today()}"
    msg['From'] = G_MAIL
    msg['To'] = G_MAIL
    icerik = "Seçtiğim Haberler:\n\n"
    for h in liste:
        icerik += f"Başlık: {h['title']}\nLink: {h['link']}\nÖzet: {h['summary']}\n\n---\n"
    msg.set_content(icerik)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(G_MAIL, G_SIFRE)
        smtp.send_message(msg)

# AKIŞ
feeds = ["https://medium.com/feed/topic/technology", "https://www.technologyreview.com/feed/"]
haberler = []

for url in feeds:
    f = feedparser.parse(url)
    for entry in f.entries:
        if len(haberler) >= MAX_HABER: break
        
        try:
            # SİTEYE GİRİŞ YAPARKEN KENDİMİZİ TANITIYORUZ (Engel yememek için)
            headers = {'User-Agent': 'Mozilla/5.0'} 
            r = requests.get(entry.link, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Makale metnini bul (p etiketlerini topla)
            metin = " ".join([p.get_text() for p in soup.find_all('p')])

            # EĞER SİTE BİZİ ENGELLEDİYSE (Just a moment dediyse) RSS ÖZETİNİ AL
            if "just a moment" in metin.lower() or len(metin) < 200:
                metin = entry.summary if 'summary' in entry else entry.title

            # SENİN İLK KODUNDAKİ AI KONTROLÜ
            res = classifier(metin[:1000], candidate_labels=KEYWORDS, multi_label=True)
            if any(s > 0.3 for s in res['scores']):
                # ÖZETLEME
                ozet = summarizer(metin[:2000], max_length=150, min_length=40, do_sample=False)[0]['summary_text']
                haberler.append({"title": entry.title, "link": entry.link, "summary": ozet})
                print(f"Haber Hazır: {entry.title}")
        except:
            continue

mail_at(haberler)