from flask import Flask, request, jsonify
import pg8000
import os
from urllib.parse import urlparse
import datetime

app = Flask(__name__)

# Подключение к БД
def get_db_connection():
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found")
            return None
            
        url = urlparse(DATABASE_URL)
        
        # Подключаемся к базе
        conn = pg8000.connect(
            database=url.path[1:],  # убираем первый символ '/'
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        print("✅ Database connected successfully!")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

# Создание таблицы при старте
def init_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
            conn.commit()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database init error: {e}")
        finally:
            conn.close()

# Инициализируем БД при старте
init_db()

@app.route('/')
def hello():
    return "Hello, Serverless! 🚀\n", 200, {'Content-Type': 'text/plain'}

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({
        "status": "received",
        "you_sent": data,
        "length": len(str(data)) if data else 0
    })

@app.route('/save', methods=['POST'])
def save_message():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database not available"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
        
    message = data.get('message', '')
    
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (content) VALUES (%s) RETURNING id", (message,))
            message_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({"status": "saved", "id": message_id, "message": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/messages')
def get_messages():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database not available"}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 10")
            rows = cur.fetchall()
            messages = []
            for row in rows:
                messages.append({
                    "id": row[0],
                    "text": row[1],
                    "time": row[2].isoformat() if hasattr(row[2], 'isoformat') else str(row[2])
                })
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/health')
def health_check():
    conn = get_db_connection()
    db_status = "connected" if conn else "disconnected"
    if conn:
        conn.close()
    return jsonify({
        "status": "healthy",
        "database": db_status
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)