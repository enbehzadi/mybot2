from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os

TOKEN = '7322999847:AAF5YpZDm4vGEmLWPGB6ht2lCcFmm6g5Ixs'
API_URL = os.getenv('API_URL', 'https://web-production-445f.up.railway.app/messages')

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('سلام! پیام خود را ارسال کنید.')

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
            await update.message.reply_text('❌ خطا در ارسال پیام.')
    except Exception as e:
        await update.message.reply_text(f'❌ خطای سرور: {str(e)}')

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_message))

    application.run_polling()

if __name__ == '__main__':
    main()
