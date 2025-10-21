from pubsub.client import PubSubClient
import time

def on_user_created(msg):
    print(f"[USER SERVICE RECEIVED] {msg}")

client = PubSubClient("user-service")

client.subscribe("user_created", on_user_created)

time.sleep(1)
client.publish("user_created", "User 101 created!")

time.sleep(1)
client.send_message("auth-service", "Ping from user-service!")

print("✅ user-service running. Press Ctrl+C to exit.")
while True:
    time.sleep(1)
