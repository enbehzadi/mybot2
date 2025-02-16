from flask import Flask, request, jsonify
from telegram import Bot
import asyncio

app = Flask(__name__)
bot = Bot(token="YOUR_BOT_TOKEN")

# ذخیره پیام‌ها (به عنوان مثال)
messages = []

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

@app.route('/messages/<int:chat_id>', methods=['GET'])
def get_user_messages(chat_id):
    user_messages = [msg for msg in messages if msg['chat_id'] == chat_id]
    if not user_messages:
        return jsonify({"error": "No messages found"}), 404
    return jsonify(user_messages)

@app.route('/send_message', methods=['POST'])
async def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    text = data.get('text')

    if not chat_id or not text:
        return jsonify({"error": "Invalid data"}), 400

    try:
        # ارسال پیام از طریق تلگرام
        await bot.send_message(chat_id=chat_id, text=text)
        messages.append({"chat_id": chat_id, "text": text})
        return jsonify({"status": "Message sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)