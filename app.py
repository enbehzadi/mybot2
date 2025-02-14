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
        print("Database connected successfully.")  # چاپ برای بررسی اتصال
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def home():
    return "سرور در حال اجرا است! به مسیر /messages برای دیدن پیام‌ها مراجعه کنید."

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
        # اضافه کردن پیام جدید
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO messages (telegram_id, first_name, last_name, message_text)
            VALUES (%s, %s, %s, %s) RETURNING id;
        ''', (telegram_id, first_name, last_name, message_text))
        message_id = cur.fetchone()[0]
        conn.commit()

        # حالا تمام پیام‌ها را فراخوانی می‌کنیم
        cur.execute('SELECT * FROM messages ORDER BY id DESC;')
        messages = cur.fetchall()
        cur.close()

        # اطمینان از اینکه پیام‌ها موجود هستند
        if not messages:
            return jsonify({"error": "No messages found"}), 404

        print(f"Message inserted with ID {message_id}")  # چاپ برای بررسی اینکه داده وارد شده است

        return jsonify({
            'id': message_id,
            'telegram_id': telegram_id,
            'first_name': first_name,
            'last_name': last_name,
            'message_text': message_text,
            'all_messages': messages  # ارسال تمام پیام‌ها همراه با پیام جدید
        }), 201
    except Exception as e:
        print(f"Error inserting message: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)