# pubsub/broker.py
import socket
import threading
from .protocol import encode, decode_stream
from datetime import datetime

HOST = "127.0.0.1"
PORT = 9000

# service_name -> conn
services = {}

# topic -> list of (conn)
subscriptions = {}

def log(tag, msg):
    t = datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] [{tag}] {msg}")

def broadcast_presence(action, service_name):
    """
    Send a presence_update message to all subscribers of topic "presence".
    action: "join" or "leave"
    """
    all_services = list(services.keys())
    payload = {
        "type": "presence_update",
        "action": action,
        "service": service_name,
        "services": all_services
    }
    for sub in subscriptions.get("presence", []):
        try:
            sub.send(encode(payload))
        except Exception:
            # ignore failing subscribers
            pass

def handle_client(conn, addr):
    log("CONNECT", f"{addr} connected.")
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
                # --- REGISTER ---
                if action == "register":
                    service_name = msg.get("service")
                    if service_name:
                        services[service_name] = conn
                        log("REGISTER", f"{service_name} registered @ {addr}")
                        # ack
                        try:
                            conn.send(encode({"status": "ok", "message": f"Registered as {service_name}"}))
                        except Exception:
                            pass
                        # broadcast presence join
                        broadcast_presence("join", service_name)

                # --- SUBSCRIBE ---
                elif action == "subscribe":
                    topic = msg.get("topic")
                    if topic:
                        subscriptions.setdefault(topic, []).append(conn)
                        log("SUBSCRIBE", f"{service_name or addr} -> {topic}")

                        # If someone subscribes to 'presence', immediately send current list
                        if topic == "presence":
                            try:
                                conn.send(encode({
                                    "type": "presence_update",
                                    "action": "current",
                                    "service": None,
                                    "services": list(services.keys())
                                }))
                            except Exception:
                                pass

                # --- PUBLISH ---
                elif action == "publish":
                    topic = msg.get("topic")
                    message = msg.get("message")
                    log("PUBLISH", f"{service_name} -> {topic}: {message}")
                    for subscriber in subscriptions.get(topic, []):
                        try:
                            subscriber.send(encode({
                                "type": "topic_message",
                                "topic": topic,
                                "from": service_name,
                                "message": message
                            }))
                        except Exception:
                            pass

                # --- DIRECT MESSAGE ---
                elif action == "message":
                    to_service = msg.get("to")
                    message = msg.get("message")
                    log("MESSAGE", f"{service_name} -> {to_service}: {message}")
                    target_conn = services.get(to_service)
                    if target_conn:
                        try:
                            target_conn.send(encode({
                                "type": "direct_message",
                                "from": service_name,
                                "message": message
                            }))
                        except Exception:
                            pass
                    else:
                        try:
                            conn.send(encode({
                                "type": "error",
                                "message": f"Service '{to_service}' not found"
                            }))
                        except Exception:
                            pass

    except Exception as e:
        log("ERROR", f"{addr}: {e}")

    finally:
        # Clean up on disconnect
        log("DISCONNECT", f"{addr} disconnected.")
        # remove from services dict
        if service_name and service_name in services:
            try:
                del services[service_name]
            except KeyError:
                pass
            # Broadcast presence leave
            broadcast_presence("leave", service_name)

        # remove conn from all subscriptions
        for topic, subs in list(subscriptions.items()):
            subscriptions[topic] = [s for s in subs if s != conn]
            if not subscriptions[topic]:
                del subscriptions[topic]

        try:
            conn.close()
        except Exception:
            pass

def start_broker():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    log("BROKER", f"Running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_broker()
