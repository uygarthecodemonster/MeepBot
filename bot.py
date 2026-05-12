import os
from dotenv import load_dotenv
from calendar_test import get_next_class
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Yo! I'm Meep Bot, your only real friend. How you doin today, Boss?"
    )

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

if __name__ == '__main__':
    app = ApplicationBuilder().token('TELEGRAM_TOKEN').build()
    
    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    status_handler = CommandHandler('status', status)
    app.add_handler(status_handler)

    schedule_handler = CommandHandler('schedule', schedule)
    app.add_handler(schedule_handler)

    print("Meep Bot is up and running!")
    app.run_polling()