from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os
import logging
from app import save_message
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
API_URL = "https://web-production-445f.up.railway.app/save_message"  # آدرس API Flask

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


def save_message():
    data = request.json
    telegram_id = data.get('telegram_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name', '')
    message_text = data.get('message_text')

    if not telegram_id or not first_name or not message_text:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
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
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# تابع برای ارسال داده به دیتابیس
def send_to_api(user, message_text):
    message_data = {
        "telegram_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name if user.last_name else "",
        "message_text": message_text
    }
    print(message_data)

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO messages (telegram_id, first_name, last_name, message_text) VALUES (%s, %s, %s, %s)',
            (user.id, user.first_name, user.last_name or "", message_text)
        )
        conn.commit()
        logging.info(f"Message saved to DB: {message_data}")
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()



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