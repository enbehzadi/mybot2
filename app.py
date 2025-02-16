from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask_cors import CORS
from telegram import Bot
from psycopg2 import pool

# تنظیمات مربوط به پایگاه داده
def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None

# تنظیمات اتصال به pool پایگاه داده برای مدیریت بهتر اتصالات
def get_db_pool():
    try:
        return psycopg2.pool.SimpleConnectionPool(1, 10, os.getenv('DATABASE_URL'))
    except Exception as e:
        print("Error creating connection pool:", e)
        return None

app = Flask(__name__)
CORS(app)

# توکن ربات تلگرام
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    print("Error: Telegram bot token is missing!")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

@app.route('/')
def home():
    return "سرور در حال اجرا است! به مسیر /messages برای دیدن پیام‌ها مراجعه کنید."

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    required_fields = ['chat_id', 'text']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        chat_id = int(data['chat_id'])
    except ValueError:
        return jsonify({"error": "Invalid chat_id"}), 400

    text = data['text']

    if not TELEGRAM_BOT_TOKEN:
        return jsonify({"error": "Telegram bot token is missing"}), 500

    try:
        print(f"Sending message to chat_id: {chat_id}, text: {text}")
        bot.send_message(chat_id=chat_id, text=text)
        return jsonify({"status": "Message sent successfully"}), 200
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/messages', methods=['GET'])
def get_messages():
    db_pool = get_db_pool()
    if not db_pool:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        conn = db_pool.getconn()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM messages;')
            messages = cur.fetchall()
            return jsonify(messages if messages else {"error": "No messages found"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            db_pool.putconn(conn)

@app.route('/messages', methods=['POST'])
def add_message():
    new_message = request.get_json()
    required_fields = ['telegram_id', 'first_name', 'last_name', 'message_text']
    if not all(field in new_message for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    db_pool = get_db_pool()
    if not db_pool:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute('''INSERT INTO messages (telegram_id, first_name, last_name, message_text)
                           VALUES (%s, %s, %s, %s) RETURNING id;''',
                        (new_message['telegram_id'], new_message['first_name'],
                         new_message['last_name'], new_message['message_text']))
            message_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({"id": message_id, **new_message}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            db_pool.putconn(conn)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=False)
