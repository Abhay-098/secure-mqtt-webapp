from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import subprocess, os, threading, sys, time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Simulated certificate generation
    time.sleep(1)
    return jsonify({'status': 'ok', 'output': '✅ Certificates generated (simulated for demo)'})

@app.route('/start_client', methods=['POST'])
def start_client():
    mode = request.json.get('mode', 'pub')
    client = request.json.get('client', 'client1')
    topic = request.json.get('topic', '/vit/test')
    payload = request.json.get('payload', 'Hello MQTT!')
    use_tls = request.json.get('use_tls', False)

    cmd = [sys.executable, "-u", "client_sim.py",
           "--mode", mode,
           "--client", client,
           "--topic", topic,
           "--payload", payload]
    if use_tls:
        cmd.append("--tls")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def stream_output():
        for line in iter(proc.stdout.readline, ''):
            if line.strip():
                socketio.emit('mqtt_log', {'line': line.strip()})
        proc.stdout.close()
        proc.wait()

    threading.Thread(target=stream_output, daemon=True).start()

    return jsonify({'status': 'started', 'pid': proc.pid})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
