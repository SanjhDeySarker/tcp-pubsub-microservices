import socket
import threading
import json
from .protocol import encode, decode_stream


class PubSubClient:
    def __init__(self, service_name: str, host: str = "127.0.0.1", port: int = 9000):
        self.service_name = service_name
        self.host = host
        self.port = port
        self.sock = None
        self.buffer = b""
        self.callbacks = {}  # topic -> callback
        self.running = False

        self._connect()
        self._register()

        # Start listener thread
        listener = threading.Thread(target=self._listen, daemon=True)
        listener.start()

    # ----------------------------------------------------------
    # Connection + Registration
    # ----------------------------------------------------------
    def _connect(self):
        """Connect to the broker."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"[CONNECTED] to broker at {self.host}:{self.port}")

    def _register(self):
        """Register the service with the broker."""
        payload = {"action": "register", "service": self.service_name}
        self.sock.send(encode(payload))
        print(f"[REGISTERED] {self.service_name}")

    # ----------------------------------------------------------
    # Core Messaging
    # ----------------------------------------------------------
    def subscribe(self, topic: str, callback=None):
        """Subscribe to a topic and optionally attach a callback."""
        payload = {"action": "subscribe", "topic": topic}
        self.sock.send(encode(payload))
        print(f"[SUBSCRIBED] to topic '{topic}'")

        if callback:
            self.callbacks[topic] = callback

    def publish(self, topic: str, message):
        """Publish a message to a topic."""
        payload = {"action": "publish", "topic": topic, "message": message}
        self.sock.send(encode(payload))
        print(f"[PUBLISHED] {topic} -> {message}")

    def send_message(self, to_service: str, message):
        """Send direct message to another service."""
        payload = {"action": "message", "to": to_service, "message": message}
        try:
            self.sock.send(encode(payload))
            print(f"[SENT] Direct message to {to_service}: {message}")
        except Exception as e:
            print(f"[ERROR] Failed to send message to {to_service}: {e}")

    # ----------------------------------------------------------
    # Internal Listener
    # ----------------------------------------------------------
    def _listen(self):
        """Background thread: listen for incoming messages."""
        self.running = True
        try:
            while self.running:
                data = self.sock.recv(4096)
                if not data:
                    print("[DISCONNECTED] Broker closed connection.")
                    break

                self.buffer += data
                messages, self.buffer = decode_stream(self.buffer)

                for msg in messages:
                    self._handle_message(msg)
        except ConnectionResetError:
            print("[ERROR] Connection lost.")
        except Exception as e:
            print(f"[ERROR] Listener failed: {e}")
        finally:
            self.sock.close()

    # ----------------------------------------------------------
    # Message Handling
    # ----------------------------------------------------------
    def _handle_message(self, msg: dict):
        msg_type = msg.get("type")

        # Direct service-to-service message
        if msg_type == "direct_message":
            sender = msg.get("from")
            message = msg.get("message")
            print(f"[DM] {sender} -> {message}")

        # Topic-based message
        elif msg_type == "topic_message":
            topic = msg.get("topic")
            sender = msg.get("from")
            message = msg.get("message")
            print(f"[TOPIC:{topic}] {sender} -> {message}")

            callback = self.callbacks.get(topic)
            if callback:
                try:
                    callback(topic, message)
                except Exception as e:
                    print(f"[ERROR] Callback for topic '{topic}' failed: {e}")

        # Error or info
        elif msg_type == "error":
            print(f"[ERROR] {msg.get('message')}")
        else:
            print(f"[INFO] {msg}")

    # ----------------------------------------------------------
    # Cleanup
    # ----------------------------------------------------------
    def close(self):
        """Close the connection cleanly."""
        self.running = False
        if self.sock:
            self.sock.close()
        print("[CLOSED] Connection closed.")
