from pubsub.client import PubSubClient
import time

def on_user_event(msg):
    print(f"[AUTH SERVICE RECEIVED] {msg}")

client = PubSubClient("auth-service")

client.subscribe("user_created", on_user_event)

print("✅ auth-service running. Press Ctrl+C to exit.")
while True:
    time.sleep(1)
