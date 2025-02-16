from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import psycopg2
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

# اتصال به دیتابیس PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

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

# ذخیره اطلاعات کاربر در دیتابیس
def save_user(telegram_id, first_name, last_name, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (telegram_id, first_name, last_name, username)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (telegram_id) DO NOTHING
    ''', (telegram_id, first_name, last_name, username))
    conn.commit()
    cursor.close()
    conn.close()

# ذخیره پیام در دیتابیس
def save_message(user_id, message_text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO messages (user_id, message_text)
    VALUES (%s, %s)
    ''', (user_id, message_text))
    conn.commit()
    cursor.close()
    conn.close()

# دستور /start
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    # ذخیره اطلاعات کاربر در دیتابیس
    save_user(user.id, user.first_name, user.last_name, user.username)
    # ذخیره پیام استارت در دیتابیس
    save_message(user.id, "Start")

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

    # ذخیره انتخاب کاربر در دیتابیس
    save_message(user.id, text)

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

        # ذخیره پیام اضطراری در دیتابیس
        save_message(user.id, f"Emergency Message: {text}")

        await update.message.reply_text("Your emergency message has been sent ✅")
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
