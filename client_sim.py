import argparse, ssl, time, sys
import paho.mqtt.client as mqtt

# Use EMQX public broker (always reachable via WebSockets)
BROKER = "broker.emqx.io"
PORT_WS = 8083        # plain WebSocket
PORT_WSS = 8084       # TLS encrypted WebSocket

def log(msg):
    print(msg)
    sys.stdout.flush()

def on_connect(client, userdata, flags, rc):
    log(f"Connected with result code {rc}")
    if rc == 0:
        log("✅ Connection successful")
    else:
        log("❌ Connection failed")

def on_message(client, userdata, msg):
    log(f"RECV <- {msg.topic}: {msg.payload.decode()}")

def run_pub(client_name, topic, payload, use_tls=False):
    port = PORT_WSS if use_tls else PORT_WS
    c = mqtt.Client(client_id=client_name, transport="websockets")
    if use_tls:
        c.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
    c.on_connect = on_connect
    c.connect(BROKER, port, 60)
    c.loop_start()
    time.sleep(1)
    for i in range(3):
        msg = f"{payload} [{i}]"
        log(f"PUB -> {msg}")
        c.publish(topic, msg)
        time.sleep(1)
    c.loop_stop()
    c.disconnect()
    log("Publisher finished.")

def run_sub(client_name, topic, use_tls=False):
    port = PORT_WSS if use_tls else PORT_WS
    c = mqtt.Client(client_id=client_name, transport="websockets")
    if use_tls:
        c.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
    c.on_message = on_message
    c.on_connect = on_connect
    c.connect(BROKER, port, 60)
    c.subscribe(topic)
    log(f"Subscribed to {topic} on {BROKER}:{port}")
    c.loop_forever()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pub","sub"], default="pub")
    p.add_argument("--client", default="client1")
    p.add_argument("--topic", default="/vit/test")
    p.add_argument("--payload", default="Hello MQTT!")
    p.add_argument("--tls", action="store_true")
    args = p.parse_args()

    if args.mode == "pub":
        run_pub(args.client, args.topic, args.payload, args.tls)
    else:
        run_sub(args.client, args.topic, args.tls)
