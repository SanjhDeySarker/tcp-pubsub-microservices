import socket
import threading
from .protocol import encode, decode_stream

HOST = "127.0.0.1"
PORT = 9000

clients = {}
subscriptions = {}

print(f"[BROKER] Running on {HOST}:{PORT}")

def handle_client(conn, addr):
    print(f"[CONNECT] {addr} connected.")
    buffer = b""
    service_name = None
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data
            messages, buffer = decode_stream(buffer)

            for msg in messages:
                action = msg.get("action")
                if action == "register":
                    service_name = msg["service"]
                    clients[service_name] = conn
                    print(f"[REGISTER] {service_name} registered @ {addr}")
                    conn.send(encode({"status": "ok", "message": f"Registered as {service_name}"}))

                elif action == "subscribe":
                    topic = msg["topic"]
                    subscriptions.setdefault(topic, []).append(conn)
                    print(f"[SUBSCRIBE] {service_name} -> {topic}")

                elif action == "publish":
                    topic = msg["topic"]
                    message = msg["message"]
                    print(f"[PUBLISH] {service_name} -> {topic}: {message}")
                    for subscriber in subscriptions.get(topic, []):
                        subscriber.send(encode({
                            "type": "topic_message",
                            "topic": topic,
                            "from": service_name,
                            "message": message
                        }))

                elif action == "message":
                    to_service = msg["to"]
                    message = msg["message"]
                    print(f"[MESSAGE] {service_name} -> {to_service}: {message}")
                    target_conn = clients.get(to_service)
                    if target_conn:
                        target_conn.send(encode({
                            "type": "direct_message",
                            "from": service_name,
                            "message": message
                        }))
                    else:
                        conn.send(encode({
                            "type": "error",
                            "message": f"Service '{to_service}' not found"
                        }))
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        print(f"[DISCONNECT] {addr} disconnected.")
        if service_name and service_name in clients:
            del clients[service_name]
        conn.close()


def start_broker():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[BROKER] Running on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_broker()
