# Secure MQTT Web App - Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy app files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure cert generator is executable
RUN chmod +x generate_certs.sh

EXPOSE 5000

# Default command: run Flask app
CMD ["python", "app.py"]

RUN pip install flask-socketio


