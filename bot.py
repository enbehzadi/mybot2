from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
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
    # ایجاد منو با دکمه‌های اینلاین
    keyboard = [
        [InlineKeyboardButton("Send Message", callback_data='send_message')],
        [InlineKeyboardButton("About Me", callback_data='about_me')],
        [InlineKeyboardButton("My Resume", callback_data='resume')],
        [InlineKeyboardButton("Contact Me", callback_data='contact')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose an option from the menu:', reply_markup=reply_markup)

# مدیریت کلیک روی دکمه‌های منو
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'send_message':
        await query.edit_message_text(text="Please send your message:")
        # ذخیره وضعیت برای دریافت پیام بعدی
        context.user_data['waiting_for_message'] = True
    elif query.data == 'about_me':
        await query.edit_message_text(text="I am a software developer who loves programming and learning new things.")
    elif query.data == 'resume':
        # ارسال لینک رزومه
        resume_link = "https://example.com/resume"  # Replace with your actual resume link
        await query.edit_message_text(text=f"You can view my resume at the following link:\n{resume_link}")
    elif query.data == 'contact':
        # ارسال اطلاعات تماس
        contact_info = """
        You can contact me through the following:
        📧 Email: example@example.com
        📞 Phone: +98 123 456 7890
        """
        await query.edit_message_text(text=contact_info)

# دریافت و ارسال پیام به API
async def add_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_message', False):
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
                await update.message.reply_text(f"Dear {user.first_name}, your message has been received ✅")
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                await update.message.reply_text('❌ Error sending message.')
        except Exception as e:
            logger.error(f"Error sending message to API: {e}")
            await update.message.reply_text(f'❌ Server error: {str(e)}')
        
        # پاک کردن وضعیت
        context.user_data['waiting_for_message'] = False
    else:
        await update.message.reply_text("Please use the menu.")

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
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_message))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    main()
