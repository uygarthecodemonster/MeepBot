# Standard Python imports
import os
from email.utils import parsedate_to_datetime

# Telegram/UI imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

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

ASKING_USERS, ASKING_MESSAGE = range(2)

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

    query = update.callback_query
    if query:
        await query.answer()
        status_msg = await query.edit_message_text("Checking your emails, Boss! Just give me a sec...")
    else:
        status_msg = await update.message.reply_text("Checking your emails, Boss! Just give me a sec...")

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
            await status_msg.edit_text("Broo, you don't even have your Google credentials set up yet! Go set that up and then try again.")
            return
        
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=5).execute()
        messages = results.get('messages', [])

        if not messages:
            await status_msg.edit_text("No unread emails, Boss! Time to fap more!")
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

        await status_msg.edit_text(reply_text, parse_mode='Markdown')

    except Exception as error:
        await status_msg.edit_text(f"⚠️ Failed to fetch emails: {error}")

async def start_sending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("Who do you want to send this to?\n\n(Type usernames like `@steve @boss` or type `@all`)")
    return ASKING_USERS

async def ask_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_input = update.message.text
    context.user_data['targets'] = users_input
    await update.message.reply_text("What do you want to say to them? 🤔")
    return ASKING_MESSAGE

async def send_engine(targets: list, message_text: str, is_all: bool, update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    users_to_send = []

    with sqlite3.connect('meepbot.db') as conn:
        cursor = conn.cursor()
        if is_all:
            cursor.execute("SELECT username, chat_id FROM users")
            users_to_send = cursor.fetchall()
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
            await context.bot.send_message(chat_id=chat_id, text=f"📢 **Message from {username}:**\n{message_text}", parse_mode='Markdown')
            usernames_success.append(username)
        except Exception as e:
            print(f"I failed to send message to {username} because of {e}")
        
    await update.message.reply_text(f"✅ Your voice is heard by {', '.join(usernames_success)}.")

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("⚠️Usage: /send @username1 @username2 Your message here\nOr: /send @all Your message here")
        return

    targets = []
    message_words = []
    is_broadcast_all = False

    if context.args[0].lower() == '@all' or context.args[0].lower() == 'all':
        is_broadcast_all = True
        message_words = " ".join(context.args[1:])
    else:
        parsing_targets = True
        for arg in context.args:
            if arg.startswith('@') and parsing_targets:
                targets.append(arg)
            else:
                parsing_targets = False
                message_words.append(arg)
        message_words = " ".join(message_words)

    if not message_words:
        await update.message.reply_text("⚠️ You forgot to include the message, dummass!")
        return

    await send_engine(targets, message_text, is_all, update, context)

async def execute_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    target_string = context.user_data['targets']

    targets = []
    is_broadcast_all = False

    if target_string.lower() == '@all' or target_string.lower() == 'all':
        is_broadcast_all = True
    else:
        targets = target_string.split()
    
    await send_engine(targets, message_text, is_broadcast_all, update, context)

    return ConversationHandler.END

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        InlineKeyboardButton("📚 Check Schedule", callback_data="btn_schedule"),
        InlineKeyboardButton("📩 Check Emails", callback_data="btn_emails"),
        InlineKeyboardButton("📢 Broadcast", callback_data="btn_send")
    ],[
        InlineKeyboardButton("🚫 Cancel", callback_data="btn_cancel")
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('🥶 I am the Iceman. I am a pretty nice man. 🧊', reply_markup=reply_markup)

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    clicked_button = query.data

    if clicked_button == "btn_schedule":
        await query.edit_message_text("Checking your schedule, Boss! Just give me a sec...")
    if clicked_button == "btn_emails":
        await query.edit_message_text("Checking your emails, Boss! Just give me a sec...")
    if clicked_button == "btn_send":
        await query.edit_message_text("To send a message to everyone, use: /send @all Your message here\n\nTo send a message to specific users, use: /send @username1 @username2 Your message here")
    if clicked_button == "btn_cancel":
        await query.edit_message_text("Menu cancelled. I'm just a bot, I don't have feelings, but if I did, I would shot you in the head. 😵🔫")


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Alright, cancelled. I'm just a bot, I don't have feelings, but if I did, I would shot you in the head. 😵🔫")
    return ConversationHandler.END


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
    app.add_handler(CallbackQueryHandler(emails, pattern='^btn_emails$'))

    send_handler = CommandHandler('send', send)
    app.add_handler(send_handler)

    menu_handler = CommandHandler('menu', show_menu)
    app.add_handler(menu_handler)
  

    broadcast_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_sending, pattern='^btn_send$')],
        states={
            ASKING_USERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_message)],
            ASKING_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, execute_send)]
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)]
    )
    app.add_handler(broadcast_handler)

    app.add_handler(CallbackQueryHandler(handle_button_click))

    print("Meep Bot is up and running!")
    app.run_polling()