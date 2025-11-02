from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import subprocess, os, threading, time, sys

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    # Simulate certificate generation (you can remove if not used)
    try:
        os.makedirs('certs', exist_ok=True)
        return jsonify({'status': 'ok', 'output': 'Certificates generated (simulated).'})
    except Exception as e:
        return jsonify({'status': 'error', 'output': str(e)}), 500


@app.route('/start_client', methods=['POST'])
def start_client():
    mode = request.json.get('mode', 'pub')  # 'pub' or 'sub'
    client = request.json.get('client', 'client1')
    topic = request.json.get('topic', 'test/topic')
    payload = request.json.get('payload', 'Hello from webapp')

    # Launch client_sim.py with args
    cmd = [sys.executable, 'client_sim.py', '--mode', mode, '--client', client,
           '--topic', topic, '--payload', payload]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    time.sleep(0.3)
    return jsonify({'status': 'started', 'pid': proc.pid})


# Relay messages received from client_sim.py back to web UI
@socketio.on('mqtt_message')
def handle_mqtt_message(data):
    socketio.emit('mqtt_message', data)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0',
                 port=5000, allow_unsafe_werkzeug=True)
