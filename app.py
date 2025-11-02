from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import subprocess, threading, sys

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_client', methods=['POST'])
def start_client():
    data = request.json
    mode = data.get("mode", "pub")
    client = data.get("client", "client1")
    topic = data.get("topic", "test/topic")
    payload = data.get("payload", "hello")
    use_tls = data.get("use_tls", False)

    cmd = [sys.executable, "-u", "client_sim.py",
           "--mode", mode,
           "--client", client,
           "--topic", topic,
           "--payload", payload]
    if use_tls:
        cmd.append("--tls")

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

    def stream():
        for line in proc.stdout:
            socketio.emit("mqtt_log", {"line": line.strip()})
        proc.stdout.close()

    threading.Thread(target=stream, daemon=True).start()
    return jsonify({"status": "started", "pid": proc.pid})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
