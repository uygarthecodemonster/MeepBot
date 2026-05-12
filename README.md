# MeepBot 🤖
A personal assistant bot for Telegram designed for TU/e students.

## Features
- **📅 Schedule Integration:** Fetches upcoming classes from the TU/e calendar using `.ics` parsing.
- **📧 Email Summarizer:** Uses the Gmail API (OAuth 2.0) to list unread subject lines directly in Telegram.
- **⏳ Smart Logic:** Handles edge cases like weekend schedules and "Remark" location formatting.

## Tech Stack
- **Language:** Python 3.x
- **Framework:** `python-telegram-bot` (Asynchronous)
- **APIs:** Google Gmail API, TU/e MyTimetable (iCal)
- **Libraries:** `ics`, `requests`, `google-auth`

## Setup
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Add your `credentials.json` from the Google Cloud Console.
4. Run `python bot.py`.
