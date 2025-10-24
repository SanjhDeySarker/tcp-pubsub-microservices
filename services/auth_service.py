from pubsub.client import PubSubClient
import time


def on_user_created(topic, message):
    print(f"[EVENT] New {topic} from user-service: {message}")


if __name__ == "__main__":
    client = PubSubClient("auth-service")

    # Subscribe to user_created events
    client.subscribe("user_created", on_user_created)

    print("✅ auth-service running. Listening for messages...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.close()
