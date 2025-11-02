# Simplified MQTT publisher/subscriber using test.mosquitto.org
import argparse, time
import paho.mqtt.client as mqtt
import socketio

# Public MQTT broker
BROKER_HOST = "test.mosquitto.org"
BROKER_PORT = 1883  # unencrypted port

# Connect to Flask SocketIO server
sio = socketio.Client()
try:
    sio.connect('http://localhost:5000')
except Exception:
    # For Render, replace localhost with your Render domain
    try:
        sio.connect('https://secure-mqtt-webapp.onrender.com')
    except Exception as e:
        print("SocketIO connection failed:", e)


def on_message(client, userdata, msg):
    message = msg.payload.decode()
    topic = msg.topic
    print(f"RECV <- topic={topic} payload={message}")
    try:
        sio.emit('mqtt_message', {'topic': topic, 'message': message})
    except Exception as e:
        print("Emit failed:", e)


def run_pub(client_name, topic, payload):
    c = mqtt.Client(client_id=client_name)
    c.connect(BROKER_HOST, BROKER_PORT, 60)
    c.loop_start()
    for i in range(3):
        msg = f"{payload} [{i}]"
        print("PUB ->", msg)
        c.publish(topic, msg)
        time.sleep(1)
    c.loop_stop()
    c.disconnect()


def run_sub(client_name, topic):
    c = mqtt.Client(client_id=client_name)
    c.on_message = on_message
    c.connect(BROKER_HOST, BROKER_PORT, 60)
    c.subscribe(topic)
    c.loop_start()
    print("Subscribed to", topic)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    c.loop_stop()
    c.disconnect()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['pub', 'sub'], default='pub')
    p.add_argument('--client', default='client1')
    p.add_argument('--topic', default='test/topic')
    p.add_argument('--payload', default='hello')
    args = p.parse_args()

    if args.mode == 'pub':
        run_pub(args.client, args.topic, args.payload)
    else:
        run_sub(args.client, args.topic)
