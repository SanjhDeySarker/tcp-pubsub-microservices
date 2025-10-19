from pubsub_client import PubSubClient
import time

# 1️⃣ Initialize client and register service
client = PubSubClient("user-service")

# 2️⃣ Subscribe to a topic (e.g. "user_created")
client.subscribe("user_created", lambda msg: print(f"[EVENT RECEIVED] {msg}"))

# 3️⃣ Publish a message
time.sleep(1)  # Small delay to ensure subscription is registered
client.publish("user_created", "User 101 created!")

# 4️⃣ Send direct message to another service (optional)
time.sleep(1)
client.send_message("auth-service", "Ping from user-service!")

# 5️⃣ Keep script running to listen for incoming messages
print("✅ user-service is running and listening for messages... (Press Ctrl+C to exit)")
while True:
    time.sleep(1)
