from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os

TOKEN = '7322999847:AAF5YpZDm4vGEmLWPGB6ht2lCcFmm6g5Ixs'
API_URL = 'http://127.0.0.1:5000/messages'

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('سلام! پیام خود را ارسال کنید.')

async def add_message(update: Update, context: CallbackContext):
    text = update.message.text
    telegram_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name if update.message.from_user.last_name else ""

    message_data = {
        'telegram_id': telegram_id,
        'first_name': first_name,
        'last_name': last_name,
        'message_text': text
    }

    response = requests.post(API_URL, json=message_data)
    if response.status_code == 201:
        await update.message.reply_text(first_name +' '+last_name+' ''عزیز پیام شما دریافت شد')
    else:
        await update.message.reply_text('خطا در ارسال پیام.')

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_message))

    application.run_polling()

if __name__ == '__main__':
    main()