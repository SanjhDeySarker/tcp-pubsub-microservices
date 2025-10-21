import socket
import json
import threading
import time

from .protocol import encode, decode


class PubSubClient:
    """
    A TCP-based Pub/Sub + Direct Messaging client.
    Handles:
      - Service registration
      - Topic subscription
      - Message publishing
      - Direct service-to-service messaging
    """

    def __init__(self, service_name, host="127.0.0.1", port=9000):
        self.service_name = service_name
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Try connecting to the broker with retries
        self.connect_with_retry()

        # Register service with broker
        self.register()

        # Start background thread to listen for messages
        threading.Thread(target=self.listen, daemon=True).start()

    # ---------------------------------------------------------------------
    # Connection Helpers
    # ---------------------------------------------------------------------
    def connect_with_retry(self, retries=5, delay=1):
        """Try to connect to the broker with a few retries."""
        for attempt in range(1, retries + 1):
            try:
                self.sock.connect((self.host, self.port))
                print(f"[CONNECTED] to broker at {self.host}:{self.port}")
                return
            except ConnectionRefusedError:
                print(f"[WAITING] Broker not ready (attempt {attempt}/{retries})...")
                time.sleep(delay)
        raise ConnectionError("Could not connect to broker after several attempts")

    # ---------------------------------------------------------------------
    # Registration
    # ---------------------------------------------------------------------
    def register(self):
        """Register the current service name with the broker."""
        payload = {"action": "register", "service": self.service_name}
        self.sock.send(encode(payload))

    # ---------------------------------------------------------------------
    # Topic Operations
    # ---------------------------------------------------------------------
    def subscribe(self, topic):
        """Subscribe to a topic."""
        payload = {"action": "subscribe", "topic": topic}
        self.sock.send(encode(payload))
        print(f"[SUBSCRIBED] to topic '{topic}'")

    def publish(self, topic, message):
        """Publish a message to a topic."""
        payload = {"action": "publish", "topic": topic, "message": message}
        self.sock.send(encode(payload))
        print(f"[PUBLISHED] {topic} -> {message}")

    # ---------------------------------------------------------------------
    # Direct Messaging
    # ---------------------------------------------------------------------
    def send_message(self, to_service, message):
        """Send a direct message to another registered service."""
        payload = {"action": "message", "to": to_service, "message": message}
        try:
            self.sock.send(encode(payload))
            print(f"[SENT] Direct message to {to_service}: {message}")
        except (ConnectionResetError, BrokenPipeError):
            print("[ERROR] Connection lost while sending direct message.")

    # ---------------------------------------------------------------------
    # Listener Loop
    # ---------------------------------------------------------------------
    def listen(self):
        """Listen for incoming messages from the broker."""
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    print("[DISCONNECTED] Broker closed connection.")
                    break

                msg = decode(data)
                self.handle_message(msg)

            except (ConnectionResetError, ConnectionAbortedError):
                print("[ERROR] Connection aborted by the broker.")
                break
            except Exception as e:
                print(f"[ERROR] Unexpected: {e}")
                break

    # ---------------------------------------------------------------------
    # Message Handling
    # ---------------------------------------------------------------------
    def handle_message(self, msg):
        """Handle incoming messages from the broker."""
        msg_type = msg.get("type")

        if msg_type == "topic_message":
            print(f"[TOPIC:{msg['topic']}] {msg['from']} -> {msg['message']}")
        elif msg_type == "direct_message":
            print(f"[DM] {msg['from']} -> {msg['message']}")
        elif msg_type == "error":
            print(f"[ERROR] {msg['message']}")
        else:
            print(f"[INFO] {msg}")

