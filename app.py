from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import subprocess, threading, sys, os, time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    """
    Simulate certificate generation (Render cannot run OpenSSL commands).
    Creates fake files under ./certs/ and returns a message.
    """
    os.makedirs("certs/ca", exist_ok=True)
    os.makedirs("certs/clients", exist_ok=True)
    with open("certs/ca/ca.crt", "w") as f:
        f.write("-----BEGIN CERTIFICATE-----\nFAKE_CA_CERTIFICATE\n-----END CERTIFICATE-----")
    with open("certs/clients/client1.crt", "w") as f:
        f.write("-----BEGIN CERTIFICATE-----\nFAKE_CLIENT_CERT\n-----END CERTIFICATE-----")
    time.sleep(1)
    return jsonify({"status": "ok", "output": "✅ Certificates generated (simulated for demo)"})

@app.route("/start_client", methods=["POST"])
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
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    def stream():
        for line in iter(proc.stdout.readline, ''):
            if line.strip():
                socketio.emit("mqtt_log", {"line": line.strip()})
        proc.stdout.close()

    threading.Thread(target=stream, daemon=True).start()
    return jsonify({"status": "started", "pid": proc.pid})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
