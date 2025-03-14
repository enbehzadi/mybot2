from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os
import logging


from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2


app = Flask(__name__)
CORS(app)  # فعال کردن CORS برای ارتباط با Flutter

# تنظیمات اتصال به PostgreSQL
DATABASE_URL = "postgresql://postgres:KLvPStKIpwAfwfRQJyaMZFzHtFHuRhKE@mainline.proxy.rlwy.net:44269/railway"

# تابع برای اتصال به پایگاه داده
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# ایجاد جدول پیام‌ها (اگر وجود نداشته باشد)
def create_messages_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            telegram_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT,
            message_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Endpoint برای ذخیره پیام
@app.route('/messages', methods=['POST'])
def save_message():
    data = request.json
    telegram_id = data.get('telegram_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name', '')
    message_text = data.get('message_text')

    if not telegram_id or not first_name or not message_text:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO messages (telegram_id, first_name, last_name, message_text) VALUES (%s, %s, %s, %s)',
        (telegram_id, first_name, last_name, message_text)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success", "message": "Message saved"}), 201

# Endpoint برای دریافت تمام پیام‌ها
@app.route('/messages', methods=['GET'])
def get_all_messages():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM messages ORDER BY created_at DESC')
    messages = cur.fetchall()
    cur.close()
    conn.close()

    # تبدیل نتیجه به فرمت JSON
    messages_list = []
    for message in messages:
        messages_list.append({
            "id": message[0],
            "telegram_id": message[1],
            "first_name": message[2],
            "last_name": message[3],
            "message_text": message[4],
            "created_at": message[5].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify(messages_list)

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

# API URL
API_URL = os.getenv('API_URL', 'https://web-production-445f.up.railway.app/messages')

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

# /start command
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    # Save the start event as a message
    await send_to_api(user, "Start")

    await update.message.reply_text(
        "Hello! I am a mobile and backend developer passionate about limitless learning.\nI love programming and am a big fan of the Turkish language.\nPlease choose an option from the menu:",
        reply_markup=get_menu_keyboard()
    )

# /menu command
async def menu(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Menu:",
        reply_markup=get_menu_keyboard()
    )

# Handle menu options
async def handle_menu(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user

    # Save user's selection to API
    await send_to_api(user, text)

    if text == "Send Emergency Message":
        await update.message.reply_text("Please send your emergency message:")
        context.user_data['waiting_for_emergency_message'] = True
    elif text == "About Me":
        about_me = """
        I am a mobile and backend developer passionate about limitless learning.\nI love programming and am a big fan of the Turkish language.
        """
        await update.message.reply_text(about_me)
    elif text == "My Resume":
        resume_link = "https://enbehzadi.github.io/resume"  # Your resume link
        await update.message.reply_text(f"You can view my resume via the link below:\n{resume_link}")
    elif text == "Contact Me":
        contact_info = """
        You can contact me through the following ways:\n📧 Email: enbehzadi@gmail.com\n📞 Phone: +989158059590
        """
        await update.message.reply_text(contact_info)
    elif text == "Play Game":  # اضافه کردن دستور بازی
        await play_game(update, context)
    else:
        await update.message.reply_text("Please use the menu.")

# Handle emergency messages
async def handle_emergency_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_emergency_message', False):
        text = update.message.text
        user = update.message.from_user

        # Save emergency message to API
        await send_to_api(user, f"Emergency Message: {text}")

        await update.message.reply_text("Your emergency message has been sent ✅")
        # Clear the waiting status
        context.user_data['waiting_for_emergency_message'] = False
    else:
        # If not waiting for an emergency message, treat it as a regular menu option
        await handle_menu(update, context)

# Play game command
async def play_game(update: Update, context: CallbackContext):
    game_short_name = "your_game_short_name"  # این را از BotFather دریافت کنید
    await update.message.reply_game(game_short_name)

# Bot setup and execution
def main():
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_emergency_message))  # Handle emergency messages first
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))  # Handle regular menu options

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()