import socket
import threading
from .protocol import encode, decode, REGISTER, SUBSCRIBE, PUBLISH, MESSAGE
from .utils import log

class PubSubClient:
    def __init__(self, service_name, host="127.0.0.1", port=9000):
        self.service_name = service_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.register()
        threading.Thread(target=self.listen, daemon=True).start()

    def register(self):
        self.sock.send(encode({"action": REGISTER, "service": self.service_name}))
        log("REGISTER", f"Service '{self.service_name}' connected.")

    def subscribe(self, topic, callback):
        self.sock.send(encode({"action": SUBSCRIBE, "topic": topic}))
        log("SUBSCRIBE", f"{self.service_name} subscribed to '{topic}'")
        self.callback = callback

    def publish(self, topic, message):
        self.sock.send(encode({"action": PUBLISH, "topic": topic, "message": message}))
        log("PUBLISH", f"{self.service_name} -> {topic}: {message}")

    def send_message(self, to_service, message):
        self.sock.send(encode({"action": MESSAGE, "to": to_service, "message": message}))
        log("MESSAGE", f"{self.service_name} -> {to_service}: {message}")

    def listen(self):
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            msg = decode(data)
            msg_type = msg.get("type")

            if msg_type == "topic_message":
                log("EVENT", f"[{msg['topic']}] {msg['from']} -> {msg['message']}")
                if hasattr(self, "callback"):
                    self.callback(msg["message"])
            elif msg_type == "direct_message":
                log("DM", f"{msg['from']} -> {msg['message']}")
            elif msg_type == "error":
                log("ERROR", msg["message"])
