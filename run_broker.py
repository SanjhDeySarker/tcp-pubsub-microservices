import socket, json, threading

class PubSubClient:
    def __init__(self, name, host="127.0.0.1", port=9000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.name = name
        self.sock.send(json.dumps({"action":"register","service":name}).encode())
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            data = self.sock.recv(4096)
            if not data: break
            msg = json.loads(data.decode())
            print(msg)

    def subscribe(self, topic): self.sock.send(json.dumps({"action":"subscribe","topic":topic}).encode())
    def publish(self, topic, msg): self.sock.send(json.dumps({"action":"publish","topic":topic,"message":msg}).encode())
    def send_message(self, to, msg): self.sock.send(json.dumps({"action":"message","to":to,"message":msg}).encode())
