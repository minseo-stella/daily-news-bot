import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser
from google import genai

# 1. WSJ 및 BBC RSS 뉴스 수집
def get_rss_news():
    wsj_url = "https://feeds.a1.wsj.net/xml/rss/3_7085.xml"
    bbc_url = "http://feeds.bbci.co.uk/news/rss.xml"
    
    wsj_feed = feedparser.parse(wsj_url).entries[:10]
    bbc_feed = feedparser.parse(bbc_url).entries[:10]
    
    wsj_text = "\n".join([f"- {entry.title}: {entry.get('summary', '')}" for entry in wsj_feed])
    bbc_text = "\n".join([f"- {entry.title}: {entry.get('summary', '')}" for entry in bbc_feed])
    
    return wsj_text, bbc_text

# 2. 최신 google-genai SDK로 요약 생성
def generate_news_summary(wsj_news, bbc_news):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_api_key)
    
    prompt = f"""
    You are a professional news analyst and English teacher.
    Based on the provided news articles, create a daily summary strictly following the exact structure below.

    [Exact Output Structure]
    제목: <매일 아침 10분! 영어 뉴스로 세계 읽기>

    - 월스트리트 저널 (WSJ) Top 5
    1) [English Title]
    EN summary: [3-line English summary]
    KO summary: [3-line Korean summary]
    key point: [Insight / Implications / What to notice in Korean]
    (Repeat for 5 WSJ articles)

    - BBC Top 5
    1) [English Title]
    EN summary: [3-line English summary]
    KO summary: [3-line Korean summary]
    key point: [Insight / Implications / What to notice in Korean]
    (Repeat for 5 BBC articles)

    => WSJ과 BBC 겹치는 토픽: [Topic Name or Summary]
    - 세계적으로 주목하고 있는 점
    - 꼭 알아야 할 세계 이슈

    <Expression>
    - Extract AT LEAST 10 useful English expressions, phrases, idioms, or vocabulary words used across the news articles with English-Korean explanations.

    [Raw News Articles]
    WSJ News:
    {wsj_news}

    BBC News:
    {bbc_news}
    """
    
    # 모델명을 gemini-3.8-flash로 지정
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )
    return response.text

# 3. 내 Gmail로 이메일 발송
def send_email(content):
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "<매일 아침 10분! 영어 뉴스로 세계 읽기>"
    
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)
    
    print("이메일 발송 완료!")

if __name__ == "__main__":
    wsj, bbc = get_rss_news()
    summary_content = generate_news_summary(wsj, bbc)
    send_email(summary_content)
