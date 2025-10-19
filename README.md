# 🚀 TCP Pub/Sub Microservices (Python)

A lightweight **TCP-based Pub/Sub + Direct Messaging system** built in Python — designed for **microservices communication without HTTP overhead**.

This system allows microservices to:
- Register with a central **broker**
- Subscribe to topics
- Publish events to other services
- Send **direct service-to-service messages**

---

## 🧱 Architecture Overview

+-------------------+ +------------------+
| user-service | ---> | |
| (Publisher) | | TCP Broker |
+-------------------+ | (Pub/Sub Core) |
| |
+-------------------+ <--- | |
| auth-service | | |
| (Subscriber) | | |
+-------------------+ +------------------+


### ✨ Features

| Feature | Description |
|----------|-------------|
| 🧩 Service Registration | Each microservice identifies itself by name |
| 📡 Topic Subscription | Subscribe to one or more event topics |
| 📤 Publish Messages | Broadcast events to all subscribers |
| 💬 Direct Messaging | Send point-to-point messages between services |
| ⚙️ Lightweight | Pure Python TCP sockets, no HTTP or REST overhead |
| 🧠 Extensible | Can be wrapped into any microservice architecture |

---

## 📁 Project Structure

tcp_pubsub_project/
│
├── pubsub/
│ ├── init.py
│ ├── broker.py # Pub/Sub broker server
│ ├── client.py # Pub/Sub client interface
│ ├── protocol.py # Message protocol definitions
│ └── utils.py # Helper utilities (logging, etc.)
│
├── services/
│ ├── user_service.py # Example publisher
│ └── auth_service.py # Example subscriber
│
├── examples/
│ └── demo.py
│
├── run_broker.py # Entry point to start the broker
├── requirements.txt
└── README.md

---

## ⚙️ Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/SanjhDeySarker/tcp-pubsub-microservices.git
cd tcp-pubsub-microservices

2️⃣ Create a Virtual Environment

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies

pip install -r requirements.txt

🚀 Running the System

python run_broker.py

Output:

[BROKER] Running on 127.0.0.1:9000

🧩 Step 2: Start auth-service
python services/auth_service.py


Output:

✅ auth-service running. Press Ctrl+C to exit.

🧩 Step 3: Start user-service
python services/user_service.py


Output:

✅ user-service running. Press Ctrl+C to exit.
[EVENT] [user_created] user-service -> User 101 created!

🧠 How It Works

Broker (run_broker.py)
Manages all client connections, topic subscriptions, and direct messages.

Client (Microservice)
Each microservice creates a PubSubClient instance, registers with the broker, subscribes to topics, and can publish or message other services.

Communication Flow

user-service publishes event → Broker → Notifies all subscribers

user-service sends direct message → Broker → Forwards to auth-service

💬 Example Console Output
[REGISTER] user-service connected.
[SUBSCRIBE] user-service subscribed to 'user_created'
[PUBLISH] user-service -> user_created: User 101 created!
[EVENT] [user_created] user-service -> User 101 created!
[DM] user-service -> Ping from user-service!

🧱 Future Enhancements

🔐 Add authentication (service tokens)

🧵 Add reconnection & fault tolerance

🧩 Add message persistence (for offline subscribers)

🧰 Expose metrics and admin API

🐳 Dockerize using docker-compose


