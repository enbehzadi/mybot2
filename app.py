from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # فعال کردن CORS برای همه دامنه‌ها

# تنظیمات اتصال به PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:yourpassword@localhost:5432/my_telegram_bot')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route('/')
def home():
    return "سرور در حال اجرا است! به مسیر /messages برای دیدن پیام‌ها مراجعه کنید."

# روت برای دریافت پیام‌ها از پایگاه داده
@app.route('/messages', methods=['GET'])
def get_messages():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM messages;')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(messages)

# روت برای ذخیره پیام‌های جدید در پایگاه داده
@app.route('/messages', methods=['POST'])
def add_message():
    new_message = request.get_json()
    telegram_id = new_message['telegram_id']
    first_name = new_message['first_name']
    last_name = new_message['last_name']
    message_text = new_message['message_text']

    conn = get_db_connection()
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)