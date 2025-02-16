from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask_cors import CORS

def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "سرور در حال اجرا است! به مسیر /messages برای دیدن پیام‌ها مراجعه کنید."

@app.route('/messages', methods=['GET'])
def get_messages():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM messages ORDER BY id DESC;')
            messages = cur.fetchall()
            return jsonify(messages if messages else {"error": "No messages found"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/messages', methods=['POST'])
def add_message():
    new_message = request.get_json()
    required_fields = ['telegram_id', 'first_name', 'last_name', 'message_text']
    if not all(field in new_message for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
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
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=False)
