import os
from dotenv import load_dotenv
import requests
import feedparser
import datetime
import smtplib
from bs4 import BeautifulSoup
from email.message import EmailMessage
from openai import OpenAI

load_dotenv()
KEYWORDS = ["artificial intelligence", "large language models", "machine learning","AI", "deep learning", "neural networks", "computer vision", "natural language processing", "Digitalisierung", "AI applications"]
MAX_ARTICLES = 3
MAIL_SENDER = os.getenv("MAIL_ADRESI")
MAIL_PASSWORD = os.getenv("MAIL_SIFRESI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_FILE = "sent_articles.txt"

client = OpenAI(api_key=OPENAI_API_KEY)

# --- MEMORY FUNCTIONS ---
def get_sent_articles():
    """Reads the history file to avoid sending same news twice."""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def save_sent_article(title):
    """Saves the title of the sent article to the history file."""
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")

def get_ai_summary(title, text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes tech news in a concise, professional English."},
                {"role": "user", "content": f"Title: {title}\n\nContent: {text[:4000]}\n\nSummarize the key points in 3 sentences.Write in a proffessional and interesting style."}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary could not be generated: {e}"

def fetch_tech_news():
  
    rss_urls = [
    
    "https://news.mit.edu/rss/topic/artificial-intelligence2", # MIT AI
    "https://news.mit.edu/rss/topic/computer-science",          # MIT CS
    "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml", # Science Daily AI
    "https://news.stanford.edu/rss-feed/topic/1057/",           


    "https://medium.com/feed/topic/artificial-intelligence",     # Medium AI Topic
    "https://medium.com/feed/topic/machine-learning",           # Medium ML Topic

    
    "https://news.google.com/rss/search?q=artificial+intelligence+when:7d&hl=en-US&gl=US&ceid=US:en", # Google News 7tage
    "https://news.google.com/rss/search?q=LLM+models+when:7d&hl=en-US&gl=US&ceid=US:en"              # Google News LLM
]

    
    
    selected_news = []
    seen_titles = set()
    sent_history = get_sent_articles() # to load previous history

    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if len(selected_news) >= MAX_ARTICLES:
                break
            # Check if article was already sent
            if entry.title in sent_history:
                continue

            # Key Word Control
            content_to_check = (entry.title + " " + getattr(entry, 'summary', '')).lower()
            if any(k in content_to_check for k in KEYWORDS) and entry.title not in seen_titles:
                
                # Full text 
                try:
                    r = requests.get(entry.link, timeout=10)
                    soup = BeautifulSoup(r.text, "html.parser")
                    paragraphs = [p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 50]
                    full_text = " ".join(paragraphs)
                    
                    summary = get_ai_summary(entry.title, full_text)
                    
                    selected_news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": summary
                    })
                    seen_titles.add(entry.title)
                    print(f"Found: {entry.title}")
                except:
                    continue
                    
    return selected_news

def send_email(news_list):
    msg = EmailMessage()
    msg['Subject'] = f"🚀 Daily AI & Tech NEWS - {datetime.date.today()}"
    msg['From'] = MAIL_SENDER
    msg['To'] = MAIL_SENDER

    email_body = "Here are the relevant latest news based on your interests:\n\n"
    
    for i, item in enumerate(news_list, 1):
        email_body += f"{i}. {item['title'].upper()}\n"
        email_body += f"🔗 Link: {item['link']}\n"
        email_body += f"📝 SUMMARY: {item['summary']}\n\n"
        email_body += "-"*50 + "\n\n"
        
        save_sent_article(item['title']) 

    msg.set_content(email_body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(MAIL_SENDER, MAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    print("Fetching news...")
    news = fetch_tech_news()
    if news:
        send_email(news)
        print("Newsletter sent successfully!")
    else:
        print("No matching news found today.")

