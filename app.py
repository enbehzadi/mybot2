from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os
import logging
from flask import Flask, jsonify
import sqlite3

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the token from the environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("Error: Telegram bot token is missing!")
    exit(1)

# API URLs
API_URL = os.getenv('API_URL', 'https://web-production-445f.up.railway.app/messages')
FLUTTER_API_URL = os.getenv('FLUTTER_API_URL', 'https://your-flutter-app-url.com/messages')

# Game URL (URL بازی شما)
GAME_URL = "https://your-server.com/game.html"  # این را با URL بازی خود جایگزین کنید

# Create the menu keyboard
def get_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Send Emergency Message"],
            ["About Me", "My Resume"],
            ["Contact Me"],
            ["Play Game"]  # اضافه کردن دکمه بازی
        ],
        resize_keyboard=True  # Resize buttons for better display
    )

# Send message to API
async def send_to_api(user, message_text):
    message_data = {
        'telegram_id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name if user.last_name else "",
        'message_text': message_text
    }

    try:
        response = requests.post(API_URL, json=message_data)
        if response.status_code == 201:
            logger.info(f"Message saved: {message_text}")
        else:
            logger.error(f"API Error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error sending message to API: {e}")

# Fetch messages for Flutter app
async def fetch_messages(update: Update, context: CallbackContext):
    try:
        response = requests.get(FLUTTER_API_URL)
        if response.status_code == 200:
            messages = response.json()
            await update.message.reply_text(f"Fetched {len(messages)} messages from the database.")
        else:
            await update.message.reply_text("Failed to fetch messages.")
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        await update.message.reply_text("Error fetching messages.")

# /start command
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    await send_to_api(user, "Start")

    await update.message.reply_text(
        "Hello! Please choose an option from the menu:",
        reply_markup=get_menu_keyboard()
    )

# Add the new /fetch_messages command
async def fetch_messages_command(update: Update, context: CallbackContext):
    await fetch_messages(update, context)

# Flask API setup
app = Flask(__name__)
DB_PATH = os.getenv('DB_PATH', 'database.db')

# Fetch messages from SQLite
def get_messages():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, first_name, last_name, message_text FROM messages")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"telegram_id": row[0], "first_name": row[1], "last_name": row[2], "message_text": row[3]}
        for row in rows
    ]

@app.route('/api/messages', methods=['GET'])
def fetch_messages_api():
    messages = get_messages()
    return jsonify(messages)

# Bot setup and execution
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fetch_messages", fetch_messages_command))

    application.run_polling()

    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
