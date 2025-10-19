import socket, threading, json

HOST = "127.0.0.1"
PORT = 9000

subscriptions = {}  # topic -> list of sockets
services = {}       # service_name -> socket

def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")
    service_name = None
    try:
        while True:
            data = conn.recv(4096)
            if not data: break
            msg = json.loads(data.decode())
            action = msg.get("action")

            if action == "register":
                service_name = msg.get("service")
                services[service_name] = conn
                print(f"[REGISTERED] {service_name} @ {addr}")
                conn.send(json.dumps({"status":"ok"}).encode())

            elif action == "subscribe":
                topic = msg.get("topic")
                subscriptions.setdefault(topic, []).append(conn)
                print(f"[SUBSCRIBED] {service_name or addr} -> {topic}")

            elif action == "publish":
                topic = msg.get("topic")
                message = msg.get("message")
                print(f"[PUBLISH] {service_name} -> {topic}: {message}")
                for sub in subscriptions.get(topic, []):
                    try:
                        sub.send(json.dumps({
                            "type":"topic_message",
                            "topic": topic,
                            "from": service_name,
                            "message": message
                        }).encode())
                    except: pass

            elif action == "message":
                to_service = msg.get("to")
                message = msg.get("message")
                print(f"[MESSAGE] {service_name} -> {to_service}: {message}")
                target_conn = services.get(to_service)
                if target_conn:
                    target_conn.send(json.dumps({
                        "type":"direct_message",
                        "from": service_name,
                        "message": message
                    }).encode())
                else:
                    conn.send(json.dumps({"type":"error","message":f"{to_service} not found"}).encode())
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        if service_name in services: del services[service_name]
        conn.close()
        print(f"[DISCONNECTED] {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[BROKER RUNNING] {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
