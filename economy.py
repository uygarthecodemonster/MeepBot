import sqlite3
import os
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv

load_dotenv()

def setup_economy_database():
    conn = sqlite3.connect('meepbot.db')
    c = conn.cursor()
    try:
        c.execute('''
                ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0
                ''')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('''
                ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 0
                ''')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('''
                ALTER TABLE users ADD COLUMN total_xp INTEGER DEFAULT 0
                ''')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('''
                ALTER TABLE users ADD COLUMN salary REAL DEFAULT 0
                ''')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('''
                ALTER TABLE users ADD COLUMN hours_worked INTEGER DEFAULT 0
                ''')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('''
                    ALTER TABLE users ADD COLUMN current_job TEXT DEFAULT "Street Cleaner"
                ''')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    with sqlite3.connect('meepbot.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT balance FROM users WHERE username = ?
        ''', (f"@{username}",))
        balance = c.fetchone()
        if balance is not None:
            await update.message.reply_text(f"💰 Your current balance is: €{balance[0]:.2f}, Boss!")
        else:
            await update.message.reply_text("⚠️ You don't have an account yet, Boss! Use /start to sign yourself up!")

setup_economy_database()