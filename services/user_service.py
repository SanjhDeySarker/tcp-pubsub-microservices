from pubsub.client import PubSubClient
import time

client = PubSubClient("user-service")

time.sleep(1)
client.publish("user_created", {"user_id": 50, "name": "Alice"})
client.publish("user_created", {"user_id": 150, "name": "Bob"})

time.sleep(1)
client.send_message("auth-service", "Ping from user-service!")
print("✅ user-service running. Press Ctrl+C to exit.")
while True:
    pass
