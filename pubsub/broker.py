import socket
import threading
from .protocol import encode, decode, REGISTER, SUBSCRIBE, PUBLISH, MESSAGE
from .utils import log

HOST = "127.0.0.1"
PORT = 9000

subscriptions = {}  # topic -> list of sockets
services = {}       # service_name -> socket

def handle_client(conn, addr):
    service_name = None
    log("CONNECT", f"{addr} connected.")

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            msg = decode(data)
            action = msg.get("action")

            # Register service
            if action == REGISTER:
                service_name = msg.get("service")
                services[service_name] = conn
                log("REGISTER", f"{service_name} registered @ {addr}")
                conn.send(encode({"status": "ok", "message": f"Registered as {service_name}"}))

            # Subscribe to topic
            elif action == SUBSCRIBE:
                topic = msg.get("topic")
                subscriptions.setdefault(topic, []).append(conn)
                log("SUBSCRIBE", f"{service_name} subscribed to '{topic}'")

            # Publish to topic
            elif action == PUBLISH:
                topic = msg.get("topic")
                message = msg.get("message")
                log("PUBLISH", f"{service_name} -> {topic}: {message}")

                for subscriber in subscriptions.get(topic, []):
                    subscriber.send(encode({
                        "type": "topic_message",
                        "topic": topic,
                        "from": service_name,
                        "message": message
                    }))

            # Direct message
            elif action == MESSAGE:
                to_service = msg.get("to")
                message = msg.get("message")
                log("MESSAGE", f"{service_name} -> {to_service}: {message}")

                if to_service in services:
                    target = services[to_service]
                    target.send(encode({
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
        log("ERROR", f"{service_name or addr}: {e}")
    finally:
        if service_name and service_name in services:
            del services[service_name]
        conn.close()
        log("DISCONNECT", f"{addr} disconnected.")


def start_broker():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    log("BROKER", f"Running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
