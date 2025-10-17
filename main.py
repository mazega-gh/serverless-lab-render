from flask import Flask, request, jsonify
import os

app = Flask(__name__)

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
    data = request.get_json()
    message = data.get('message', '') if data else ''
    return jsonify({
        "status": "simulated_save", 
        "message": message,
        "note": "Database integration will be added later"
    })

@app.route('/messages')
def get_messages():
    return jsonify({
        "status": "simulated_data",
        "messages": [
            {"id": 1, "text": "Пример сообщения 1", "time": "2024-01-01T12:00:00"},
            {"id": 2, "text": "Пример сообщения 2", "time": "2024-01-01T12:05:00"}
        ],
        "note": "Database integration will be added later"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)