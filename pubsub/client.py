import socket
import threading
import json
import time
from .protocol import encode, decode_stream


class PubSubClient:
    """
    A TCP-based Pub/Sub + Direct Messaging client.
    Supports:
        - service registration
        - topic subscription
        - topic publishing
        - direct messaging
        - realtime presence updates
    """

    def __init__(self, service_name, host="127.0.0.1", port=9000, auto_subscribe_presence=True):
        self.service_name = service_name
        self.host = host
        self.port = port
        self.sock = None
        self.buffer = b""
        self.subscriptions = {}
        self.connected = False
        self.auto_subscribe_presence = auto_subscribe_presence

        self._connect()
        self._register_service()

        # Start background listener thread
        listener = threading.Thread(target=self._listen_loop, daemon=True)
        listener.start()

        # Optionally auto-subscribe to presence updates
        if self.auto_subscribe_presence:
            self.subscribe("presence_updates", self._handle_presence_update)

    # -------------------------------
    # Connection Management
    # -------------------------------

    def _connect(self):
        """Connect to broker"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.connected = True
        print(f"[CONNECTED] to broker at {self.host}:{self.port}")

    def _register_service(self):
        """Register this service name with the broker"""
        payload = {"action": "register", "service": self.service_name}
        self.sock.send(encode(payload))
        print(f"[REGISTERED] {self.service_name}")

    # -------------------------------
    # Core Messaging Methods
    # -------------------------------

    def subscribe(self, topic, callback=None):
        """Subscribe to a topic. Optionally attach a callback."""
        payload = {"action": "subscribe", "topic": topic}
        self.sock.send(encode(payload))
        if callback:
            self.subscriptions[topic] = callback
        print(f"[SUBSCRIBED] to topic '{topic}'")

    def publish(self, topic, message):
        """Publish message to a topic"""
        payload = {"action": "publish", "topic": topic, "message": message}
        self.sock.send(encode(payload))
        print(f"[PUBLISHED] {topic} -> {message}")

    def send_message(self, to_service, message):
        """Send direct message to another registered service"""
        payload = {"action": "message", "to": to_service, "message": message}
        try:
            self.sock.send(encode(payload))
            print(f"[SENT] Direct message to {to_service}: {message}")
        except ConnectionAbortedError:
            print("[ERROR] Connection aborted while sending message. Reconnecting...")
            self._reconnect()

    # -------------------------------
    # Listening Loop
    # -------------------------------

    def _listen_loop(self):
        """Background thread: continuously listens for broker messages"""
        try:
            while self.connected:
                data = self.sock.recv(4096)
                if not data:
                    print("[DISCONNECTED] Broker closed connection.")
                    self.connected = False
                    break

                self.buffer += data
                messages, self.buffer = decode_stream(self.buffer)

                for msg in messages:
                    self._handle_message(msg)
        except Exception as e:
            print(f"[ERROR] Listener crashed: {e}")
            self.connected = False
            self._reconnect()

    def _reconnect(self):
        """Try reconnecting after connection failure"""
        print("[RECONNECT] Attempting to reconnect...")
        time.sleep(2)
        try:
            self._connect()
            self._register_service()
            # re-subscribe to all topics
            for topic, callback in self.subscriptions.items():
                self.subscribe(topic, callback)
            print("[RECONNECTED] Successfully reconnected.")
        except Exception as e:
            print(f"[RECONNECT FAILED] {e}")

    # -------------------------------
    # Message Handling
    # -------------------------------

    def _handle_message(self, msg):
        """Route incoming message to proper handler"""
        msg_type = msg.get("type")
        topic = msg.get("topic")
        sender = msg.get("from")
        message = msg.get("message")

        if msg_type == "topic_message":
            if topic in self.subscriptions:
                try:
                    self.subscriptions[topic](message, sender)
                except Exception as e:
                    print(f"[ERROR] Callback for topic '{topic}' failed: {e}")
            else:
                print(f"[TOPIC:{topic}] {sender} -> {message}")

        elif msg_type == "direct_message":
            print(f"[DM] {sender} -> {message}")

        elif msg_type == "presence_update":
            self._handle_presence_update(msg)

        elif msg_type == "error":
            print(f"[ERROR] {msg.get('message')}")

        else:
            print(f"[INFO] {msg}")

    def _handle_presence_update(self, msg, *_):
        """Handle presence notifications from broker"""
        update_type = msg.get("update")
        service = msg.get("service")

        if update_type == "joined":
            print(f"[PRESENCE] ✅ Service joined: {service}")
        elif update_type == "left":
            print(f"[PRESENCE] ❌ Service left: {service}")
        else:
            print(f"[PRESENCE] {msg}")

    # -------------------------------
    # Graceful Shutdown
    # -------------------------------

    def close(self):
        """Close the client connection"""
        self.connected = False
        if self.sock:
            self.sock.close()
        print(f"[CLOSED] Connection closed for {self.service_name}")
