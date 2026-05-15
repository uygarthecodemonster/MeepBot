# Standard Python imports
import os
from email.utils import parsedate_to_datetime

# Telegram imports
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Environment variables
from dotenv import load_dotenv

# Google Calendar imports
from calendar_test import get_next_class

# Google API Core imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

#SQLite imports
import sqlite3

def setup_database():
    conn = sqlite3.connect('meepbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            chat_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

setup_database()
load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    username = user.username

    if username:
        conn = sqlite3.connect('meepbot.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (username, chat_id) VALUES (?, ?)', (f"@{username}", chat_id))

        conn.commit()
        conn.close()

    await update.message.reply_text(f"Yo, I am Meep Bot, {user.first_name}! I will never forget you, and I will always be here to serve you!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm doing great, Boss! Just hanging out here scratching my balls."
    )

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Let me check your schedule, Boss! Just give me a sec..."
    )
    result = get_next_class()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result
    )

async def emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Checking your emails, Boss! Just give me a sec...")

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        else:
            await update.message.reply_text("Broo, you don't even have your Google credentials set up yet! Go set that up and then try again.")
            return
        
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=5).execute()
        messages = results.get('messages', [])

        if not messages:
            await update.message.reply_text("No unread emails, Boss! Time to fap more!")
            return
        
        reply_text = "📬 **Your Latest Unread Emails:**\n\n"

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders=['Subject', 'From', 'Date']).execute()

            headers = msg['payload']['headers']
            subject = 'No Subject'
            sender = 'Unknown Sender'
            clean_date = 'Unknown Date'

            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                if header['name'] == 'From':
                    sender = header['value'].split('<')[0].strip()
                if header['name'] == 'Date':
                    raw_date = header['value']               
                    dt_object = parsedate_to_datetime(raw_date)
                    local_dt = dt_object.astimezone() 
                    clean_date = local_dt.strftime("%b %d at %H:%M")

            reply_text += f"🔹 **{subject}**\n👤 {sender}\n🕒 {clean_date}\n\n"

        await update.message.reply_text(reply_text, parse_mode='Markdown')

    except Exception as error:
        await update.message.reply_text(f"⚠️ Failed to fetch emails: {error}")

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args)<2:
        await update.message.reply_text("⚠️ Usage: /send @username Your message here")
        return
    
    targets = []
    message_words = []
    is_broadcast_all = False

    if context.args[0].lower() == '@all':
        is_broadcast_all = True
        message_words = " ".join(context.args[1:]) 
    else:
        parsing_usernames = True
        for arg in context.args:
            if arg.startswith('@') and parsing_usernames:
                targets.append(arg)
            else:
                parsing_usernames = False
                message_words.append(arg)
        
        message_words = " ".join(message_words)

    if not message_words:
        await update.message.reply_text("⚠️ You forgot to include a message dumbass!")
        return

    chat_ids_to_send = []

    with sqlite3.connect('meepbot.db') as conn:
        cursor = conn.cursor()
        if is_broadcast_all:
            cursor.execute("SELECT username, chat_id FROM users")
            results = cursor.fetchall()
            users_to_send = results 
        else:
            placeholder = ','.join('?' * len(targets)) 
            query = f"SELECT username, chat_id FROM users WHERE username IN ({placeholder})"
            cursor.execute(query, targets)
            results = cursor.fetchall()

            found_usernames = [row[0] for row in results]
            missing = [user for user in targets if user not in found_usernames]
            if missing:
                await update.message.reply_text(f"⚠️ I couldn't find these motherfuckers: {', '.join(missing)}")

            users_to_send = results 

    if not users_to_send:
        await update.message.reply_text("⚠️ I fucking don't know any of those people you mentioned, moron!")
        return
            
    usernames_success = []

    await update.message.reply_text(f"🚀 Sending message to {len(users_to_send)} user(s)...")

    for username, chat_id in users_to_send:
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"📢 **Message from {update.effective_user.username}:**\n{message_words}", parse_mode='Markdown')
            usernames_success.append(username)
        except Exception as e:
            print(f"I failed to send message to {chat_id} because of {e}")
        
    await update.message.reply_text(f"✅ Your voice is heard by {', '.join(usernames_success)}.")

    


if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    status_handler = CommandHandler('status', status)
    app.add_handler(status_handler)

    schedule_handler = CommandHandler('schedule', schedule)
    app.add_handler(schedule_handler)

    emails_handler = CommandHandler('emails', emails)
    app.add_handler(emails_handler)

    send_handler = CommandHandler('send', send)
    app.add_handler(send_handler)

    print("Meep Bot is up and running!")
    app.run_polling()