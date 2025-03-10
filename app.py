from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os
import logging

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("Error: Telegram bot token is missing!")
    exit(1)

# API URL
API_URL = os.getenv('API_URL', 'https://web-production-445f.up.railway.app/messages')

# Create menu keyboard
def get_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Send Emergency Message"],
            ["About Me", "My Resume"],
            ["Contact Me"]
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
        "Hello! Please choose an option from the menu:",
        reply_markup=get_menu_keyboard()
    )

# /menu command
async def menu(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Menu:",
        reply_markup=get_menu_keyboard()
    )

# Handle menu selections
async def handle_menu(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user

    # Save user's selection in the API
    await send_to_api(user, text)

    if text == "Send Emergency Message":
        await update.message.reply_text("Please send your emergency message:")
        context.user_data['waiting_for_emergency_message'] = True
    elif text == "About Me":
        about_me = """
        I am a mobile developer specializing in Android and iOS. My primary expertise is mobile programming, and I have 8 years of experience. I started with Java and later moved to Kotlin, Swift, and currently Flutter. I am also familiar with backend languages such as .NET Core, React, Flask, PHP, and Golang.
        """
        await update.message.reply_text(about_me)
    elif text == "My Resume":
        resume_link = "https://enbehzadi.github.io/resume"  # Your resume link
        await update.message.reply_text(f"You can view my resume at the following link:\n{resume_link}")
    elif text == "Contact Me":
        contact_info = """
        You can contact me through the following methods:
        📧 Email: enbehzadi@gmail.com
        📞 Phone: +989158059590
        """
        await update.message.reply_text(contact_info)
    else:
        await update.message.reply_text("Please use the menu.")

# Handle emergency message
async def handle_emergency_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_emergency_message', False):
        text = update.message.text
        user = update.message.from_user

        # Save emergency message in the API
        await send_to_api(user, f"Emergency Message: {text}")

        await update.message.reply_text("Your emergency message has been sent ✅")
        # Clear the state
        context.user_data['waiting_for_emergency_message'] = False
    else:
        await update.message.reply_text("Please use the menu.")

# Setup and run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_emergency_message))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()