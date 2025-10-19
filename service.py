import socket, json, threading

HOST = "127.0.0.1"
PORT = 9000

class MicroserviceClient:
    def __init__(self, name):
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.register()
        threading.Thread(target=self.listen, daemon=True).start()

    def register(self):
        self.sock.send(json.dumps({"action":"register","service":self.name}).encode())

    def subscribe(self, topic):
        self.sock.send(json.dumps({"action":"subscribe","topic":topic}).encode())

    def publish(self, topic, message):
        self.sock.send(json.dumps({"action":"publish","topic":topic,"message":message}).encode())

    def send_message(self, to, message):
        self.sock.send(json.dumps({"action":"message","to":to,"message":message}).encode())

    def listen(self):
        while True:
            data = self.sock.recv(4096)
            if not data: break
            msg = json.loads(data.decode())
            t = msg.get("type")
            if t == "topic_message":
                print(f"[TOPIC:{msg['topic']}] {msg['from']} -> {msg['message']}")
            elif t == "direct_message":
                print(f"[DM] {msg['from']} -> {msg['message']}")
            elif t == "error":
                print(f"[ERROR] {msg['message']}")

# Example Usage
if __name__ == "__main__":
    name = input("Enter your service name: ")
    client = MicroserviceClient(name)
    print("Commands: sub <topic>, pub <topic> <msg>, msg <to> <msg>")
    while True:
        cmd = input("> ").split(" ", 2)
        if not cmd: continue
        if cmd[0] == "sub": client.subscribe(cmd[1])
        elif cmd[0] == "pub": client.publish(cmd[1], cmd[2])
        elif cmd[0] == "msg": client.send_message(cmd[1], cmd[2])
