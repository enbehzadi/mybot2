from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # فعال کردن CORS برای ارتباط با Flutter

# خواندن DATABASE_URL از متغیر محیطی
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def create_messages_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            telegram_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT,
            message_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("Table 'messages' created successfully.")

@app.route('/save_message', methods=['POST'])
def save_message():
    data = request.json
    telegram_id = data.get('telegram_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name', '')
    message_text = data.get('message_text')

    if not telegram_id or not first_name or not message_text:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO messages (telegram_id, first_name, last_name, message_text) VALUES (%s, %s, %s, %s)',
            (telegram_id, first_name, last_name, message_text)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Message saved"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/messages', methods=['GET'])
def get_all_messages():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM messages ORDER BY created_at DESC')
    messages = cur.fetchall()
    cur.close()
    conn.close()

    messages_list = []
    for message in messages:
        messages_list.append({
            "id": message[0],
            "telegram_id": message[1],
            "first_name": message[2],
            "last_name": message[3],
            "message_text": message[4],
            "created_at": message[5].strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify(messages_list)

if __name__ == '__main__':
    create_messages_table()  # ایجاد جدول اگر وجود نداشته باشد
    app.run(host='0.0.0.0', port=5000)