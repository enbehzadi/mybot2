from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os
import logging

# تنظیمات لاگ‌گیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دریافت توکن از متغیر محیطی
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("Error: Telegram bot token is missing!")
    exit(1)

# آدرس API
API_URL = os.getenv('API_URL', 'https://web-production-445f.up.railway.app/messages')

# دستور /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('سلام! پیام خود را ارسال کنید.')

# دریافت و ارسال پیام به API
async def add_message(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user

    message_data = {
        'telegram_id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name if user.last_name else "",
        'message_text': text
    }

    try:
        response = requests.post(API_URL, json=message_data)
        if response.status_code == 201:
            await update.message.reply_text(f"{user.first_name} عزیز، پیام شما دریافت شد ✅")
        else:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            await update.message.reply_text('❌ خطا در ارسال پیام.')
    except Exception as e:
        logger.error(f"Error sending message to API: {e}")
        await update.message.reply_text(f'❌ خطای سرور: {str(e)}')

# ارسال پیام به کاربر
async def send_message_to_user(context: CallbackContext, chat_id: int, message: str):
    try:
        chat_id = int(chat_id)
    except ValueError:
        logger.error("Invalid chat_id")
        return

    try:
        logger.info(f"Sending message to chat_id: {chat_id}, text: {message}")
        await context.bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logger.error(f"Error sending message: {e}")

# تنظیم و اجرای ربات
def main():
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_message))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    main()