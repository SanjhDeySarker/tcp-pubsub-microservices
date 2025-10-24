from pubsub.client import PubSubClient

def on_user_created(message, sender):
    print(f"[AUTH SERVICE] Got event from {sender}: {message}")

# Only accept users with ID > 100
def filter_user(msg):
    return msg.get("user_id", 0) > 100

client = PubSubClient("auth-service")
client.subscribe("user_created", callback=on_user_created, filter_func=filter_user)

print("✅ auth-service running. Listening for messages...")
while True:
    pass
