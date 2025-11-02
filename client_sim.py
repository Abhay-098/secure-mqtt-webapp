# MQTT publisher/subscriber using WebSockets + optional TLS
import argparse, ssl, time
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT_WS = 8081  # MQTT over WebSockets (Render allows)
TOPIC_DEFAULT = "/vit/test"

def on_connect(client, userdata, flags, rc):
    print("Connected to broker with code", rc)
    if rc == 0:
        print("✅ Connection successful")
    else:
        print("❌ Connection failed")

def on_message(client, userdata, msg):
    print(f"RECV <- {msg.topic}: {msg.payload.decode()}")

def run_pub(client_name, topic, payload, use_tls=False):
    c = mqtt.Client(client_id=client_name, transport="websockets")
    if use_tls:
        c.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
    c.on_connect = on_connect
    c.connect(BROKER, PORT_WS, 60)
    c.loop_start()
    for i in range(3):
        msg = f"{payload} [{i}]"
        print("PUB ->", msg)
        c.publish(topic, msg)
        time.sleep(1)
    c.loop_stop()
    c.disconnect()
    print("Publisher finished.")

def run_sub(client_name, topic, use_tls=False):
    c = mqtt.Client(client_id=client_name, transport="websockets")
    if use_tls:
        c.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
    c.on_message = on_message
    c.on_connect = on_connect
    c.connect(BROKER, PORT_WS, 60)
    c.subscribe(topic)
    print(f"Subscribed to {topic} ({'TLS' if use_tls else 'Unsecure'})")
    c.loop_forever()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pub", "sub"], default="pub")
    p.add_argument("--client", default="client1")
    p.add_argument("--topic", default=TOPIC_DEFAULT)
    p.add_argument("--payload", default="Hello MQTT!")
    p.add_argument("--tls", action="store_true")
    args = p.parse_args()

    if args.mode == "pub":
        run_pub(args.client, args.topic, args.payload, args.tls)
    else:
        run_sub(args.client, args.topic, args.tls)
