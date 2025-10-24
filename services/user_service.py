from pubsub.client import PubSubClient
import time

if __name__ == "__main__":
    client = PubSubClient("user-service")

    time.sleep(1)  # wait for registration

    # Publish an event
    client.publish("user_created", "User 101 created!")

    # Send direct message to auth-service
    time.sleep(1)
    client.send_message("auth-service", "Ping from user-service!")

    print("✅ user-service running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.close()
