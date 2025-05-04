import os
import dropbox
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Load environment variables
DROPBOX_REFRESH = os.environ['DROPBOX_REFRESH']
DROPBOX_APP_KEY = os.environ['DROPBOX_APP_KEY']
DROPBOX_APP_SECRET = os.environ['DROPBOX_APP_SECRET']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
EMAIL_USER = os.environ['EMAIL_USER']
EMAIL_PASS = os.environ['EMAIL_PASS']
EMAIL_TO = os.environ['EMAIL_TO']

def get_mp4_count():
    dbx = dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET
    )
    folder_path = "/instaclipper/To_upload"
    result = dbx.files_list_folder(folder_path)
    return len([entry for entry in result.entries if entry.name.endswith('.mp4')])

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
    if count == 6:
        message = "⚠️ 6 videos remaining. 3 days until you run out of content."
    elif count == 4:
        message = "⚠️ 4 videos remaining. 2 day until you run out of content."
    elif count == 4:
        message = "⚠️ 2 videos remaining. 1 day until you run out of content."
    
    if message:
        send_telegram_message(message)
        send_email("Dropbox Alert", message)

if __name__ == "__main__":
    main()
