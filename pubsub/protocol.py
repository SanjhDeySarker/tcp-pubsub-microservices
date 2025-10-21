import json

def encode(data: dict) -> bytes:
    """Encode Python dict to JSON bytes."""
    return json.dumps(data).encode()

def decode(data: bytes) -> dict:
    """Decode bytes to Python dict."""
    return json.loads(data.decode())

# Define common message actions
REGISTER = "register"
SUBSCRIBE = "subscribe"
PUBLISH = "publish"
MESSAGE = "message"
