from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
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

# آیدی شما برای دریافت پیام‌های اضطراری (مثلاً آیدی عددی شما در تلگرام)
YOUR_CHAT_ID = 123456789  # این را با آیدی خود جایگزین کنید

# ایجاد کیبورد منو
def get_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Send Emergency Message"],
            ["About Me", "My Resume"],
            ["Contact Me"]
        ],
        resize_keyboard=True  # کوچک کردن دکمه‌ها برای نمایش بهتر
    )

# دستور /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome! Please choose an option from the menu below:",
        reply_markup=get_menu_keyboard()
    )

# دستور /menu
async def menu(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Here is the menu:",
        reply_markup=get_menu_keyboard()
    )

# مدیریت انتخاب گزینه‌های منو
async def handle_menu(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user

    if text == "Send Emergency Message":
        await update.message.reply_text("Please send your emergency message:")
        context.user_data['waiting_for_emergency_message'] = True
    elif text == "About Me":
        about_me = """
        I am a mobile and backend developer who loves learning without limits.
        I am passionate about programming and adore the Turkish language.
        """
        await update.message.reply_text(about_me)
    elif text == "My Resume":
        resume_link = "https://enbehzadi.github.io/resume"  # لینک رزومه شما
        await update.message.reply_text(f"You can view my resume at the following link:\n{resume_link}")
    elif text == "Contact Me":
        contact_info = """
        You can contact me through the following:
        📧 Email: enbehzadi@gmail.com
        📞 Phone: +989158059590
        """
        await update.message.reply_text(contact_info)
    else:
        await update.message.reply_text("Please use the menu.")

# دریافت و ارسال پیام اضطراری
async def handle_emergency_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_emergency_message', False):
        text = update.message.text
        user = update.message.from_user

        # ارسال پیام به شما (یا آیدی مشخص)
        try:
            await context.bot.send_message(
                chat_id=YOUR_CHAT_ID,
                text=f"🚨 Emergency Message from {user.first_name} ({user.username}):\n\n{text}"
            )
            await update.message.reply_text("Your emergency message has been sent ✅")
        except Exception as e:
            logger.error(f"Error sending emergency message: {e}")
            await update.message.reply_text("❌ Failed to send your emergency message. Please try again later.")

        # پاک کردن وضعیت
        context.user_data['waiting_for_emergency_message'] = False
    else:
        await update.message.reply_text("Please use the menu.")

# تنظیم و اجرای ربات
def main():
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_emergency_message))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    main()
