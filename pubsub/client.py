import socket
import json
import threading
from typing import Callable, Optional

# Helper functions
def encode(data: dict) -> bytes:
    return (json.dumps(data) + "\n").encode()

def decode(data: bytes) -> dict:
    return json.loads(data.decode().strip())

class PubSubClient:
    def __init__(self, service_name: str, host="127.0.0.1", port=9000):
        self.service_name = service_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.callbacks = {}
        print(f"[CONNECTED] to broker at {host}:{port}")
        self.register()
        threading.Thread(target=self.listen, daemon=True).start()

    def register(self):
        payload = {"action": "register", "service": self.service_name}
        self.sock.send(encode(payload))

    # ✳️ Subscribe with optional filter
    def subscribe(self, topic: str, callback: Optional[Callable] = None, filter_func: Optional[Callable] = None):
        self.callbacks[topic] = {"callback": callback, "filter": filter_func}
        payload = {"action": "subscribe", "topic": topic}
        self.sock.send(encode(payload))
        print(f"[SUBSCRIBED] to '{topic}' with filter {filter_func.__name__ if filter_func else 'None'}")

    def publish(self, topic: str, message):
        payload = {"action": "publish", "topic": topic, "message": message}
        self.sock.send(encode(payload))
        print(f"[PUBLISHED] {topic} -> {message}")

    def send_message(self, to_service: str, message):
        payload = {"action": "message", "to": to_service, "message": message}
        self.sock.send(encode(payload))
        print(f"[SENT] Direct message to {to_service}: {message}")

    def listen(self):
        buffer = b""
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    print("[DISCONNECTED] Broker closed connection.")
                    break
                buffer += data
                while b"\n" in buffer:
                    msg_raw, buffer = buffer.split(b"\n", 1)
                    msg = decode(msg_raw)
                    self.handle_message(msg)
            except Exception as e:
                print(f"[ERROR] Listener: {e}")
                break

    def handle_message(self, msg):
        msg_type = msg.get("type")

        if msg_type == "topic_message":
            topic = msg["topic"]
            message = msg["message"]
            sender = msg.get("from")

            if topic in self.callbacks:
                cb_info = self.callbacks[topic]
                callback = cb_info.get("callback")
                filter_func = cb_info.get("filter")

                # ✳️ Check filter before invoking callback
                if filter_func:
                    try:
                        if not filter_func(message):
                            return  # Skip message if filter returns False
                    except Exception as e:
                        print(f"[FILTER ERROR] {e}")
                        return

                if callback:
                    try:
                        callback(message, sender)
                    except Exception as e:
                        print(f"[ERROR] Callback for topic '{topic}' failed: {e}")
                else:
                    print(f"[{topic}] {sender} -> {message}")

        elif msg_type == "direct_message":
            print(f"[DM] {msg['from']} -> {msg['message']}")
        elif msg_type == "error":
            print(f"[ERROR] {msg['message']}")
        else:
            print(f"[INFO] {msg}")
