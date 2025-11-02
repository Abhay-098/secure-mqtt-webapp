# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all files to the container
COPY . /app

# Install dependencies (Flask + SocketIO + MQTT)
RUN pip install --no-cache-dir \
    flask \
    flask-socketio \
    python-socketio \
    paho-mqtt \
    eventlet

# Expose Flask app port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
