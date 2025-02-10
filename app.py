from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# تنظیمات اتصال به PostgreSQL از متغیر محیطی
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL تنظیم نشده است. آن را در Railway اضافه کنید.")

# تابع برای ایجاد اتصال به پایگاه داده
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# دریافت پیام‌ها
@app.route('/messages', methods=['GET'])
def get_messages():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM messages;')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(messages)

# افزودن پیام جدید
@app.route('/messages', methods=['POST'])
def add_message():
    try:
        new_message = request.get_json()
        telegram_id = new_message.get('telegram_id')
        first_name = new_message.get('first_name')
        last_name = new_message.get('last_name')
        message_text = new_message.get('message_text')

        if not all([telegram_id, first_name, last_name, message_text]):
            return jsonify({'error': 'تمام فیلدها باید مقدار داشته باشند'}), 400

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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# اجرای سرور روی پورت دریافتی از متغیر محیطی (مورد نیاز Railway)
if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)