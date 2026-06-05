import sqlite3
import os
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv
import time

load_dotenv()

JOBS = {
    "Street Cleaner": {
        "min_level": 0,
        "workplace": "the streets of your city",
        "promotions": [
            {"hours": 0, "title": "Junior Street Cleaner", "salary": 50},
            {"hours": 100, "title": "Street Cleaner", "salary": 75},
            {"hours": 300, "title": "Senior Street Cleaner", "salary": 125},
            {"hours": 700, "title": "Street Cleaning Supervisor", "salary": 200},
            {"hours": 1500, "title": "Street Cleaning Manager", "salary": 350},
        ]
    },
    "Cashier": {
        "min_level": 4,
        "workplace": "a local supermarket",
        "promotions": [
            {"hours": 0, "title": "Trainee Cashier", "salary": 300},
            {"hours": 100, "title": "Cashier", "salary": 450},
            {"hours": 300, "title": "Senior Cashier", "salary": 650},
            {"hours": 700, "title": "Head Cashier", "salary": 950},
            {"hours": 1500, "title": "Store Supervisor", "salary": 1300},
        ]
    },
    "Police Officer": {
        "min_level": 11,
        "workplace": "the police department",
        "promotions": [
            {"hours": 0, "title": "Cadet", "salary": 125},
            {"hours": 100, "title": "Police Officer", "salary": 350},
            {"hours": 300, "title": "Detective", "salary": 650},
            {"hours": 700, "title": "Sergeant", "salary": 1100},
            {"hours": 1500, "title": "Police Captain", "salary": 1800},
        ]
    },
    "Chef": {
        "min_level": 12,
        "workplace": "the restaurant kitchen",
        "promotions": [
            {"hours": 0, "title": "Kitchen Assistant", "salary": 175},
            {"hours": 100, "title": "Line Cook", "salary": 425},
            {"hours": 300, "title": "Sous Chef", "salary": 800},
            {"hours": 700, "title": "Head Chef", "salary": 1400},
            {"hours": 1500, "title": "Executive Chef", "salary": 2200},
        ]
    },
    "Accountant": {
        "min_level": 22,
        "workplace": "the accounting firm",
        "promotions": [
            {"hours": 0, "title": "Junior Accountant", "salary": 400},
            {"hours": 100, "title": "Accountant", "salary": 900},
            {"hours": 300, "title": "Senior Accountant", "salary": 1800},
            {"hours": 700, "title": "Finance Manager", "salary": 3200},
            {"hours": 1500, "title": "CFO", "salary": 5500},
        ]
    },
    "Pilot": {
        "min_level": 23,
        "workplace": "the cockpit",
        "promotions": [
            {"hours": 0, "title": "Student Pilot", "salary": 500},
            {"hours": 100, "title": "Co-Pilot", "salary": 1100},
            {"hours": 300, "title": "Commercial Pilot", "salary": 2200},
            {"hours": 700, "title": "Senior Pilot", "salary": 3900},
            {"hours": 1500, "title": "Chief Pilot", "salary": 6500},
        ]
    },
    "Hacker": {
        "min_level": 32,
        "workplace": "the dark web",
        "promotions": [
            {"hours": 0, "title": "Script Kiddie", "salary": 800},
            {"hours": 100, "title": "Grey Hat", "salary": 2000},
            {"hours": 300, "title": "Black Hat", "salary": 4000},
            {"hours": 700, "title": "Cybercriminal", "salary": 7000},
            {"hours": 1500, "title": "Dark Web Legend", "salary": 10500},
        ]
    },
    "Doctor": {
        "min_level": 34,
        "workplace": "the hospital",
        "promotions": [
            {"hours": 0, "title": "Medical Intern", "salary": 1000},
            {"hours": 100, "title": "Resident", "salary": 2500},
            {"hours": 300, "title": "General Practitioner", "salary": 5000},
            {"hours": 700, "title": "Specialist", "salary": 8500},
            {"hours": 1500, "title": "Chief of Surgery", "salary": 12500},
        ]
    },
    "Film Director": {
        "min_level": 48,
        "workplace": "the film set",
        "promotions": [
            {"hours": 0, "title": "Production Assistant", "salary": 900},
            {"hours": 100, "title": "Assistant Director", "salary": 2800},
            {"hours": 300, "title": "Independent Director", "salary": 6000},
            {"hours": 700, "title": "Studio Director", "salary": 10500},
            {"hours": 1500, "title": "Hollywood Director", "salary": 15500},
        ]
    },
    "Investment Banker": {
        "min_level": 50,
        "workplace": "Wall Street",
        "promotions": [
            {"hours": 0, "title": "Banking Intern", "salary": 1100},
            {"hours": 100, "title": "Junior Analyst", "salary": 3200},
            {"hours": 300, "title": "Senior Analyst", "salary": 7000},
            {"hours": 700, "title": "Vice President", "salary": 11500},
            {"hours": 1500, "title": "Managing Director", "salary": 16000},
        ]
    },
    "CEO": {
        "min_level": 65,
        "workplace": "the corporate headquarters",
        "promotions": [
            {"hours": 0, "title": "Startup Founder", "salary": 2000},
            {"hours": 100, "title": "Small Business Owner", "salary": 5500},
            {"hours": 300, "title": "Regional CEO", "salary": 10500},
            {"hours": 700, "title": "National CEO", "salary": 16500},
            {"hours": 1500, "title": "Global CEO", "salary": 22500},
        ]
    },
    "Crime Lord": {
        "min_level": 67,
        "workplace": "the underworld",
        "promotions": [
            {"hours": 0, "title": "Street Thug", "salary": 1800},
            {"hours": 100, "title": "Gang Member", "salary": 5000},
            {"hours": 300, "title": "Crime Boss", "salary": 9500},
            {"hours": 700, "title": "Cartel Leader", "salary": 15000},
            {"hours": 1500, "title": "Crime Lord", "salary": 22000},
        ]
    }
}

def check_level_up(total_xp, level):
    current_level = level
    levels_gained = 0
    for i in range(current_level):
        total_xp -= 5 * i**2 + 50 * i + 100
    for n in range(current_level, 100):
        xp_for_next_level = 5 * n**2 + 50 * n + 100
        if total_xp >= xp_for_next_level:
            levels_gained += 1
            total_xp -= xp_for_next_level
        else:
            break
    new_level = current_level + levels_gained
    return new_level, levels_gained

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
                ALTER TABLE users ADD COLUMN current_job TEXT DEFAULT NULL
                ''')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('''
                ALTER TABLE users ADD COLUMN current_title TEXT DEFAULT NULL
                ''')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('''
                ALTER TABLE users ADD COLUMN last_worked INTEGER DEFAULT 0
                ''')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('''
                ALTER TABLE users ADD COLUMN highest_job_level INTEGER DEFAULT -1
                ''')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    with sqlite3.connect('meepbot.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT balance FROM users WHERE chat_id = ?
        ''', (chat_id,))
        balance = c.fetchone()
        if balance is not None:
            await update.message.reply_text(f"💰 Your current balance is: €{balance[0]:.2f}, Boss!")
        else:
            await update.message.reply_text("⚠️ You don't have an account yet, Boss! Use /start to sign yourself up!")

async def work_ready_notification(context):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Get back to work you lazy motherfucker! You are ready to work again.💼"
    )

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    with sqlite3.connect('meepbot.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT last_worked FROM users WHERE chat_id = ?
        ''', (chat_id,))
        result = c.fetchone()
        if result is None:
            await update.message.reply_text("⚠️ Work? I don't even know who the fuck you are! Use /start to sign yourself up!")
            return
        last_worked = result[0]
        time_since_last_work = int(time.time() - last_worked)
        if time_since_last_work < 60:
            seconds_remaining = int(60 - time_since_last_work)
            await update.message.reply_text(f"Wow! I like the enthusiasm. But you can't work that hard. You need to wait {seconds_remaining} seconds before work again.")
        else:
            c.execute('''
                SELECT balance, hours_worked, salary, current_job, current_title, level, total_xp FROM users WHERE chat_id = ?
            ''', (chat_id,))
            balance, hours_worked, salary, current_job, current_title, level, total_xp = c.fetchone()
            if current_job is None or current_title is None:
                await update.message.reply_text(f"🚫 You're unemployed, broke, and probably smell like it too 🤢. Nobody's paying you for anything right now, Boss.\nUse /apply to find a job and start earning before you starve! 💸")
                return
            work_xp = 10 + (2 * JOBS[current_job]['min_level'])
            c.execute('''
                UPDATE users SET balance = ?, hours_worked = ?, last_worked = ?, total_xp = ? WHERE chat_id = ?
            ''', (balance + salary, hours_worked + 1, int(time.time()), total_xp + work_xp, chat_id))
            conn.commit()
            await update.message.reply_text(f"💼 You worked as a {current_title} at {JOBS[current_job]['workplace']} for an hour and earned €{salary:.2f}, Boss! Your total balance is now €{balance + salary:.2f}. Keep working to get promoted and earn more!")
            new_level, levels_gained = check_level_up(total_xp + work_xp, level)
            if levels_gained > 0:
                c.execute('''
                    UPDATE users SET level = ? WHERE chat_id = ?
                ''', (new_level, chat_id))
                conn.commit()
                if levels_gained == 1:
                    await update.message.reply_text(
                        f"⭐ *LEVEL UP!*\n"
                        f"You are now *Level {new_level}*, Boss!\n"
                        f"Keep working and spending to climb higher! 💪",
                        parse_mode='Markdown'
                        )
                elif levels_gained > 1:
                    await update.message.reply_text(
                        f"🚀 *{levels_gained} LEVELS AT ONCE?!*\n"
                        f"You jumped straight to *Level {new_level}*, Boss!\n"
                        f"Whatever you just did — do more of it. 🔥",
                        parse_mode='Markdown'
                    )
            promotions = JOBS[current_job]["promotions"]
            next_promotion = None
            for promotion in promotions:
                if hours_worked + 1 == promotion["hours"]:
                    next_promotion = promotion
                    break
            if next_promotion and salary < next_promotion["salary"]:
                c.execute('''
                    UPDATE users SET salary = ?, current_title = ? WHERE chat_id = ?
                ''', (next_promotion["salary"], next_promotion["title"], chat_id))
                await update.message.reply_text(f"🎉 Congratulations, {update.effective_user.first_name}! You've been promoted to {next_promotion['title']} and your new salary is €{next_promotion['salary']}/hr!")
                conn.commit()
            context.job_queue.run_once(work_ready_notification, 60, chat_id=chat_id)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    with sqlite3.connect('meepbot.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT first_name, username, balance, level, total_xp,  current_title, salary, hours_worked FROM users WHERE chat_id = ?
        ''', (chat_id,))
        result = c.fetchone()
        if result is None:
            await update.message.reply_text("⚠️ I don't even know who the fuck you are dumbass! Use /start to sign yourself up!")
        else:
            first_name, username, balance, level, total_xp, current_title, salary, hours_worked = result
            safe_name = (username or first_name).replace('_', '\\_')
            job_section = "💼 *Unemployed*" if current_title is None else f"💼 *{current_title}*\n💵 €{salary:.0f}/hr | ⏱ {hours_worked} hour(s)"
            await update.message.reply_text(
                f"👤 *{safe_name}*\n"
                f"💰 Balance: €{balance:.2f}\n"
                f"⭐ Level: {level} ({total_xp} XP)\n"
                f"{job_section}",
                parse_mode='Markdown'
            )

async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    with sqlite3.connect('meepbot.db') as conn:
        c = conn.cursor()
        c.execute('''
                  SELECT current_job, level, highest_job_level, total_xp FROM users WHERE chat_id = ?
                ''', (chat_id,))
        result = c.fetchone()
        if result is None:
            await update.message.reply_text("⚠️ I don't even know who the fuck you are dumbass! Use /start to sign yourself up!")
        else:
            current_job, level, highest_job_level, total_xp = result
            if not context.args:
                lines = []
                for i, (job_name, job_data) in enumerate(JOBS.items(), 1):
                    if level >= job_data["min_level"]:
                        eligible = '✅'
                    else:
                        eligible = '❌'
                    if current_job == job_name:
                        lines.append(f"🔹{eligible}{i}. *{job_name}* (Level {job_data['min_level']}+)\n💵 Starting salary: €{job_data['promotions'][0]['salary']}/hr")
                    else:
                        lines.append(f"{eligible}{i}. {job_name} (Level {job_data['min_level']}+)\n💵 Starting salary: €{job_data['promotions'][0]['salary']}/hr")
                text = "💼 *Available Jobs:*\n(✅ = eligible, ❌ = locked)\n\n" + "\n\n".join(lines) + "\n\n(⚠️ Switching jobs resets your hours worked to 0 and it's irreversible.)\n\nUse /apply [number] to apply for a job."
                await update.message.reply_text(text, parse_mode='Markdown')
            else:
                try:
                    job_number = int(context.args[0])
                    if job_number < 1 or job_number > len(JOBS):
                        await update.message.reply_text("⚠️ That's not a number from the list, dumb fuck? Use /apply to see the damn list.")
                        return
                    job_list = list(JOBS.items())
                    job_name, job_data = job_list[job_number - 1]
                    if job_name == current_job:
                        await update.message.reply_text("🙄 You already work there, dumbass. What, you forget where you work?")
                    elif level < job_data["min_level"]:
                        await update.message.reply_text(f"❌ Level {job_data['min_level']} required. You're Level {level}. Get your shit together and keep grinding.")
                    else:
                        starting_salary = job_data["promotions"][0]["salary"]
                        starting_title = job_data["promotions"][0]["title"]
                        xp_gain = 0
                        if job_data["min_level"]>highest_job_level:
                            xp_gain = 100 + (10 * job_data["min_level"])
                        c.execute('''
                                   UPDATE users SET salary = ?, current_job = ?, current_title = ?, hours_worked = ?, total_xp = ? WHERE chat_id = ?
                                ''', (starting_salary, job_name, starting_title, 0, total_xp + xp_gain, chat_id))
                        new_level, levels_gained = check_level_up(total_xp + xp_gain, level)
                        conn.commit()
                        if xp_gain > 0:
                            c.execute('''
                                   UPDATE users SET highest_job_level = ? WHERE chat_id = ?
                                ''', (job_data["min_level"], chat_id))
                            await update.message.reply_text(f"🎉 *Hired, Boss!*\nYou are now a *{starting_title}* at {job_data['workplace']}!\n💵 Starting salary: €{starting_salary:.0f}/hr\n⭐ +{xp_gain} XP for the career move!", parse_mode='Markdown')
                        else:
                            await update.message.reply_text(f"🎉 *Hired, Boss!*\nYou are now a *{starting_title}* at {job_data['workplace']}!\n💵 Starting salary: €{starting_salary:.0f}/hr", parse_mode='Markdown')
                        if levels_gained > 0:
                            c.execute('''
                                UPDATE users SET level = ? WHERE chat_id = ?
                            ''', (new_level, chat_id))
                            conn.commit()
                            if levels_gained == 1:
                                await update.message.reply_text(
                                    f"⭐ *LEVEL UP!*\n"
                                    f"You are now *Level {new_level}*, Boss!\n"
                                    f"Keep working and spending to climb higher! 💪",
                                    parse_mode='Markdown'
                                    )
                            elif levels_gained > 1:
                                await update.message.reply_text(
                                    f"🚀 *{levels_gained} LEVELS AT ONCE?!*\n"
                                    f"You jumped straight to *Level {new_level}*, Boss!\n"
                                    f"Whatever you just did — do more of it. 🔥",
                                    parse_mode='Markdown'
                                )

                except ValueError:
                    await update.message.reply_text("⚠️ That's not even a number, you idiot. Use /apply to see the damn list.")
                    return
                