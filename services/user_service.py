from pubsub.client import PubSubClient
import time

client = PubSubClient("user-service")

# Wait a bit to make sure the broker is aware of both services
time.sleep(1)

client.publish("user_created", "User 101 created!")

# Wait again before sending direct message (to ensure auth-service has registered)
time.sleep(2)
client.send_message("auth-service", "Ping from user-service!")

print("✅ user-service running. Press Ctrl+C to exit.")
while True:
    time.sleep(1)
