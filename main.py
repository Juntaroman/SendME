import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# --- 設定情報 ---
GMAIL_USER = "oshiro0307@gmail.com"        # 送信元（ご自身のGmailアドレス）
GMAIL_APP_PASS = "nlnf wijf fhfs tcsp"     # Gmailのアプリパスワード
TO_EMAIL = "oshiro0307@gmail.com"          # 送信先メールアドレス

SERPAPI_KEY = "YOUR_SERPAPI_KEY"           # SerpAPIのAPIキー
DB_FILE = "notified_urls.txt"              # 通知済みURLの保存ファイル

# --- 1. 過去に通知したURLの読み込み ---
def load_notified_urls():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

# --- 2. 新しいURLの保存 ---
def save_notified_urls(urls):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        for url in urls:
            f.write(f"{url}\n")

# --- 3. Upwork勉強会情報の検索 ---
def fetch_upwork_events():
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": "Upwork 勉強会 OR セミナー",
        "location": "Japan",
        "hl": "ja",
        "gl": "jp",
        "api_key": SERPAPI_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    results = []
    if "organic_results" in data:
        for item in data["organic_results"]:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet", "")
            })
    return results

# --- 4. メール送信処理 ---
def send_email(new_events):
    subject = f"【自動通知】Upworkの新しい勉強会・セミナー情報 ({len(new_events)}件)"
    
    body = "Upworkに関する新しい勉強会・セミナー情報が見つかりました：\n\n"
    for event in new_events:
        body += f"■ {event['title']}\n"
        body += f"URL: {event['link']}\n"
        body += f"概要: {event['snippet']}\n\n"
        
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            server.send_message(msg)
        print("メールを送信しました。")
    except Exception as e:
        print(f"メール送信エラー: {e}")

# --- メイン処理 ---
def main():
    notified_urls = load_notified_urls()
    events = fetch_upwork_events()
    
    new_events = []
    for event in events:
        if event['link'] not in notified_urls:
            new_events.append(event)
            
    if new_events:
        print(f"{len(new_events)} 件の新しい情報が見つかりました。")
        send_email(new_events)
        # 通知済みリストを更新
        new_urls = [e['link'] for e in new_events]
        save_notified_urls(new_urls)
    else:
        print("新しい勉強会情報はありませんでした。")

if __name__ == "__main__":
    main():
