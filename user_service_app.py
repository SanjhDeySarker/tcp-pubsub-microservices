from pubsub_client import PubSubClient
import time

# 1️⃣ Initialize client and register service
client = PubSubClient("user-service")

# 2️⃣ Subscribe to topic
client.subscribe("user_created")

# 3️⃣ Publish a message
time.sleep(1)  # small delay to ensure subscriptions are registered
client.publish("user_created", "User 101 created!")

# 4️⃣ Send direct message to another service
time.sleep(1)
client.send_message("auth-service", "Ping!")

# 5️⃣ Keep the script running to listen for messages
print("Listening for messages... Press Ctrl+C to exit.")
while True:
    time.sleep(1)
