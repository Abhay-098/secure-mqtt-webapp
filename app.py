from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import subprocess, os, threading, time, sys

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    script = os.path.join(os.getcwd(), "generate_certs.sh")
    if not os.path.exists(script):
        return jsonify({"status": "error", "output": "generate_certs.sh not found"}), 404
    proc = subprocess.run([script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return jsonify({"status": "ok", "output": proc.stdout})

@app.route("/start_client", methods=["POST"])
def start_client():
    mode = request.json.get("mode", "pub")
    client = request.json.get("client", "client1")
    topic = request.json.get("topic", "test/topic")
    payload = request.json.get("payload", "hello from webapp")
    use_tls = request.json.get("use_tls", False)

    cmd = [
        sys.executable, "client_sim.py",
        "--mode", mode,
        "--client", client,
        "--topic", topic,
        "--payload", payload
    ]
    if use_tls:
        cmd.append("--tls")

    def stream_output(process):
        for line in iter(process.stdout.readline, ''):
            socketio.emit("mqtt_log", {"line": line.strip()})
        process.stdout.close()

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    threading.Thread(target=stream_output, args=(proc,)).start()
    return jsonify({"status": "started", "pid": proc.pid})

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
