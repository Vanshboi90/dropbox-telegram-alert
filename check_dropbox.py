import os
import requests
import smtplib
from email.mime.text import MIMEText

# Env vars
DROPBOX_TOKEN = os.environ['DROPBOX_TOKEN']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
EMAIL_USER = os.environ['EMAIL_USER']
EMAIL_PASS = os.environ['EMAIL_PASS']
EMAIL_TO = os.environ['EMAIL_TO']

def get_mp4_count():
    url = "https://api.dropboxapi.com/2/files/list_folder"
    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Content-Type": "application/json"
    }
    data = { "path": "/instaclipper/To_upload" }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    entries = response.json().get('entries', [])
    return len([e for e in entries if e['name'].endswith('.mp4')])

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = { "chat_id": TELEGRAM_CHAT_ID, "text": message }
    response = requests.post(url, json=payload)
    response.raise_for_status()

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

def main():
    count = get_mp4_count()
    if count == 16:
        message = "⚠️ 16 videos remaining. 2 days until deletion."
    elif count == 8:
        message = "⚠️ 8 videos remaining. 1 day until deletion."
    else:
        return

    # Send alerts
    send_telegram_message(message)
    send_email("Dropbox Alert", message)

if __name__ == "__main__":
    main()
