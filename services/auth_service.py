from pubsub.client import PubSubClient
import time

def on_user_created(message, sender):
    print(f"[EVENT] New user event from {sender}: {message}")

client = PubSubClient("auth-service")

# Subscribe to topic with callback
client.subscribe("user_created", on_user_created)

print("✅ auth-service running. Listening for messages...")
while True:
    time.sleep(1)
