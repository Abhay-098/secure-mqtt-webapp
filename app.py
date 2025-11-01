from flask import Flask, render_template, jsonify, request
import subprocess, os, threading, time, sys
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Run the generate_certs.sh script
    script = os.path.join(os.getcwd(), 'generate_certs.sh')
    try:
        proc = subprocess.run([script], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return jsonify({'status':'ok','output':proc.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'status':'error','output':e.stderr}), 500

@app.route('/start_client', methods=['POST'])
def start_client():
    mode = request.json.get('mode','pub')  # 'pub' or 'sub'
    client = request.json.get('client','client1')
    topic = request.json.get('topic','test/topic')
    payload = request.json.get('payload','hello from webapp')
    # Launch client_sim.py with args
    cmd = [sys.executable, 'client_sim.py', '--mode', mode, '--client', client, '--topic', topic, '--payload', payload]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Do not block; capture a little and return PID
    time.sleep(0.2)
    return jsonify({'status':'started','pid':proc.pid})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
