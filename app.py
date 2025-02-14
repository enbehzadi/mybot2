from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# دریافت DATABASE_URL از متغیرهای محیطی
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Make sure it is defined in your Railway environment.")

# تابع برای ایجاد اتصال به دیتابیس
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None

@app.route('/')
def home():
    return "سرور در حال اجرا است! به مسیر /messages برای دیدن پیام‌ها مراجعه کنید."

@app.route('/messages', methods=['GET'])
def get_messages():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM messages;')
        messages = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/messages', methods=['POST'])
def add_message():
    new_message = request.get_json()
    if not all(k in new_message for k in ('telegram_id', 'first_name', 'last_name', 'message_text')):
        return jsonify({"error": "Missing required fields"}), 400

    telegram_id = new_message['telegram_id']
    first_name = new_message['first_name']
    last_name = new_message['last_name']
    message_text = new_message['message_text']

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO messages (telegram_id, first_name, last_name, message_text)
            VALUES (%s, %s, %s, %s) RETURNING id;
        ''', (telegram_id, first_name, last_name, message_text))
        message_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'id': message_id, 'telegram_id': telegram_id, 'first_name': first_name, 'last_name': last_name, 'message_text': message_text}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)