# Simple MQTT publisher/subscriber that uses TLS + client certs + sends data to Flask via SocketIO
import argparse, ssl, time, os
import paho.mqtt.client as mqtt
import socketio

# Directory where certs are stored
CERT_DIR = os.path.join(os.getcwd(), 'certs')

# Connect to Flask-SocketIO server
sio = socketio.Client()
try:
    # For local Docker/Render, use localhost
    sio.connect('http://localhost:5000')
except Exception as e:
    print("SocketIO connection failed:", e)

def make_client(client_name):
    """Create an MQTT client with TLS + client certs."""
    c = mqtt.Client(client_id=client_name)
    c.tls_set(ca_certs=os.path.join(CERT_DIR, 'ca', 'ca.crt'),
              certfile=os.path.join(CERT_DIR, 'clients', f'{client_name}.crt'),
              keyfile=os.path.join(CERT_DIR, 'clients', f'{client_name}.key'),
              tls_version=ssl.PROTOCOL_TLS_CLIENT)
    c.tls_insecure_set(False)
    return c

def run_pub(client_name, topic, payload):
    """Run MQTT publisher."""
    c = make_client(client_name)
    c.connect('localhost', 8883)
    c.loop_start()
    for i in range(3):
        msg = f"{payload} [{i}]"
        print('PUB ->', msg)
        c.publish(topic, msg)
        # Send message to Flask immediately (so you see it on web)
        try:
            sio.emit('mqtt_message', {'topic': topic, 'message': msg})
        except Exception as e:
            print("Socket emit failed:", e)
        time.sleep(1)
    c.loop_stop()
    c.disconnect()

def on_message(client, userdata, msg):
    """When message received from broker."""
    message = msg.payload.decode()
    topic = msg.topic
    print(f"RECV <- topic={topic} payload={message}")
    # Send the received message to Flask via SocketIO
    try:
        sio.emit('mqtt_message', {'topic': topic, 'message': message})
    except Exception as e:
        print("Socket emit failed:", e)

def run_sub(client_name, topic):
    """Run MQTT subscriber."""
    c = make_client(client_name)
    c.on_message = on_message
    c.connect('localhost', 8883)
    c.subscribe(topic)
    c.loop_start()
    print('Subscribed to', topic, '— press Ctrl-C to stop')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    c.loop_stop()
    c.disconnect()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['pub','sub'], default='pub')
    p.add_argument('--client', default='client1')
    p.add_argument('--topic', default='test/topic')
    p.add_argument('--payload', default='hello')
    args = p.parse_args()

    if args.mode == 'pub':
        run_pub(args.client, args.topic, args.payload)
    else:
        run_sub(args.client, args.topic)
