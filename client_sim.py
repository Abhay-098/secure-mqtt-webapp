# Simple MQTT publisher/subscriber with optional TLS + client certs
import argparse, ssl, time, os
import paho.mqtt.client as mqtt

# Default broker for Render testing
BROKER_UNSECURE = "test.mosquitto.org"
BROKER_SECURE = "test.mosquitto.org"
PORT_UNSECURE = 1883
PORT_SECURE = 8883

CERT_DIR = os.path.join(os.getcwd(), "certs")

def make_client(client_name, use_tls=False):
    c = mqtt.Client(client_id=client_name)
    if use_tls:
        c.tls_set(
            ca_certs=os.path.join(CERT_DIR, "ca", "ca.crt") if os.path.exists(os.path.join(CERT_DIR, "ca", "ca.crt")) else None,
            tls_version=ssl.PROTOCOL_TLS_CLIENT
        )
        c.tls_insecure_set(False)
    return c


def run_pub(client_name, topic, payload, use_tls=False):
    c = make_client(client_name, use_tls)
    port = PORT_SECURE if use_tls else PORT_UNSECURE
    c.connect(BROKER_SECURE if use_tls else BROKER_UNSECURE, port)
    c.loop_start()
    for i in range(3):
        msg = f"{payload} [{i}]"
        print("PUB ->", msg)
        c.publish(topic, msg)
        time.sleep(1)
    c.loop_stop()
    c.disconnect()


def on_message(client, userdata, msg):
    print(f"RECV <- topic={msg.topic} payload={msg.payload.decode()}")


def run_sub(client_name, topic, use_tls=False):
    c = make_client(client_name, use_tls)
    c.on_message = on_message
    port = PORT_SECURE if use_tls else PORT_UNSECURE
    c.connect(BROKER_SECURE if use_tls else BROKER_UNSECURE, port)
    c.subscribe(topic)
    c.loop_start()
    print(f"Subscribed to {topic} — {'TLS' if use_tls else 'Unsecure'} mode active")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    c.loop_stop()
    c.disconnect()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pub", "sub"], default="pub")
    p.add_argument("--client", default="client1")
    p.add_argument("--topic", default="test/topic")
    p.add_argument("--payload", default="hello")
    p.add_argument("--tls", action="store_true", help="Enable TLS mode")
    args = p.parse_args()

    if args.mode == "pub":
        run_pub(args.client, args.topic, args.payload, args.tls)
    else:
        run_sub(args.client, args.topic, args.tls)
