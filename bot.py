from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import aiohttp
import os

TOKEN = '7322999847:AAF5YpZDm4vGEmLWPGB6ht2lCcFmm6g5Ixs'
API_URL = 'https://web-production-445f.up.railway.app/messages'

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

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=message_data) as response:
            if response.status == 201:
                await update.message.reply_text(f'{first_name} {last_name} عزیز پیام شما دریافت شد.')
            else:
                await update.message.reply_text(f'خطا در ارسال پیام. کد خطا: {response.status}')

async def handle_photo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    photo = update.message.photo[-1].file_id

    # ذخیره فایل یا ارسال به سرور
    message_data = {
        'telegram_id': user_id,
        'first_name': first_name,
        'message_text': 'تصویر دریافت شد.'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=message_data) as response:
            if response.status == 201:
                await update.message.reply_text(f'{first_name} عزیز تصویر شما دریافت شد.')
            else:
                await update.message.reply_text(f'خطا در ارسال تصویر. کد خطا: {response.status}')

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # اضافه کردن پشتیبانی از تصاویر

    application.run_polling()

if __name__ == '__main__':
    main()