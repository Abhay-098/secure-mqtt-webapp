# Secure MQTT Web App
**Project:** Enhancing IoT Security: Implementing a Secure MQTT Protocol  

## What this project provides
- A web-based control panel (Flask) to **generate a CA, server and client certificates** using OpenSSL.
- `docker-compose.yml` and `mosquitto.conf` to run a Mosquitto broker configured for **TLS + client certificate authentication**.
- Example **Python MQTT clients** (publisher & subscriber) that connect over TLS using generated certificates.
- A simple frontend to generate certs and run simulated clients from the server.
- Scripts and instructions to run the complete environment on Linux / WSL / macOS (Docker required).

## Requirements
- Docker & docker-compose
- Python 3.8+
- OpenSSL installed (for the cert generation script) OR you can use Dockerized OpenSSL
- pip packages: flask, paho-mqtt

## Quick start (Linux / WSL / macOS)
1. Clone or unzip this project.
2. Generate certs (creates `ca`, `broker`, and `clients` folders):
   ```bash
   ./generate_certs.sh
   ```
3. Start Mosquitto:
   ```bash
   docker-compose up -d
   ```
4. Start the Flask web app:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
   Open http://127.0.0.1:5000

## Files
- `generate_certs.sh` - bash script that generates CA, broker, and client certs using OpenSSL.
- `docker-compose.yml` - runs Eclipse Mosquitto with mounted certs and `mosquitto.conf`.
- `mosquitto.conf` - broker configuration to enforce TLS and require client certificates.
- `app.py` - Flask web app (control UI + endpoints to call cert script and simulate clients).
- `client_sim.py` - Example TLS-capable publisher/subscriber using Paho MQTT.
- `templates/index.html`, `static/*` - frontend UI.
- `README.md` - this file.

## Notes
- This project implements the architecture and algorithm described in the provided PDF (TLS v1.3, X.509 cert auth). See the original project PDF for background and test cases. fileciteturn0file0
- Running Docker and OpenSSL may require elevated privileges. If you cannot run Docker locally, you can generate certs locally and provide them to a remote broker.
