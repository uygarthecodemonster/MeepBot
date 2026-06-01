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

setup_economy_database()