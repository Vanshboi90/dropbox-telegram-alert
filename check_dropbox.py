import os
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
DROPBOX_REFRESH = os.environ['DROPBOX_REFRESH']
DROPBOX_APP_KEY = os.environ['DROPBOX_APP_KEY']
DROPBOX_APP_SECRET = os.environ['DROPBOX_APP_SECRET']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
EMAIL_USER = os.environ['EMAIL_USER']
EMAIL_PASS = os.environ['EMAIL_PASS']
EMAIL_TO = os.environ['EMAIL_TO']

def get_dropbox_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    auth = (DROPBOX_APP_KEY, DROPBOX_APP_SECRET)
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH
    }
    response = requests.post(url, auth=auth, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def get_mp4_count():
    access_token = get_dropbox_access_token()
    url = "https://api.dropboxapi.com/2/files/list_folder"
    headers = {
        "Authorization": f"Bearer {access_token}",
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
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

def main():
    try:
        count = get_mp4_count()
    except Exception as e:
        error_msg = f"❌ Failed to check Dropbox files: {str(e)}"
        send_telegram_message(error_msg)
        send_email("Dropbox Alert Error", error_msg)
        return

    message = ""
    if count == 16:
        message = "⚠️ 16 videos remaining. 2 days until you run out of content."
    elif count == 8:
        message = "⚠️ 8 videos remaining. 1 day until you run out of content."

    if message:
        send_telegram_message(message)
        send_email("Dropbox Alert", message)

if __name__ == "__main__":
    main()
