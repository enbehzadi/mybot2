from telegram import Update, ReplyKeyboardMarkup
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

# ارسال پیام به API
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

# دستور /start
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    # ذخیره رویداد استارت به عنوان یک پیام
    await send_to_api(user, "Start")

    await update.message.reply_text(
        "سلام! لطفا یک گزینه از منو انتخاب کنید:",
        reply_markup=get_menu_keyboard()
    )

# دستور /menu
async def menu(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "منو:",
        reply_markup=get_menu_keyboard()
    )

# مدیریت انتخاب گزینه‌های منو
async def handle_menu(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user

    # ذخیره انتخاب کاربر در API
    await send_to_api(user, text)

    if text == "Send Emergency Message":
        await update.message.reply_text("لطفا پیام اضطراری خود را ارسال کنید:")
        context.user_data['waiting_for_emergency_message'] = True
    elif text == "About Me":
        about_me = """
        من یک توسعه‌دهنده موبایل و بک‌اند هستم که عاشق یادگیری بدون مرز هستم.
        به برنامه‌نویسی علاقه‌مندم و عاشق زبان ترکی هستم.
        """
        await update.message.reply_text(about_me)
    elif text == "My Resume":
        resume_link = "https://enbehzadi.github.io/resume"  # لینک رزومه شما
        await update.message.reply_text(f"رزومه من را می‌توانید از طریق لینک زیر مشاهده کنید:\n{resume_link}")
    elif text == "Contact Me":
        contact_info = """
        برای ارتباط با من می‌توانید از راه‌های زیر استفاده کنید:
        📧 ایمیل: enbehzadi@gmail.com
        📞 شماره تماس: +989158059590
        """
        await update.message.reply_text(contact_info)
    else:
        await update.message.reply_text("لطفا از منو استفاده کنید.")

# دریافت و ارسال پیام اضطراری
async def handle_emergency_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_emergency_message', False):
        text = update.message.text
        user = update.message.from_user

        # ذخیره پیام اضطراری در API
        await send_to_api(user, f"Emergency Message: {text}")

        await update.message.reply_text("پیام اضطراری شما ارسال شد ✅")
        # پاک کردن وضعیت
        context.user_data['waiting_for_emergency_message'] = False
    else:
        await update.message.reply_text("لطفا از منو استفاده کنید.")

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
