import json

DELIMITER = b"\n"  # newline separates JSON messages


def encode(data: dict) -> bytes:
    """Convert dict -> JSON bytes with delimiter."""
    return (json.dumps(data) + "\n").encode()


def decode_stream(buffer: bytes):
    """Split buffer into multiple JSON messages."""
    messages = []
    parts = buffer.split(DELIMITER)
    for part in parts[:-1]:  # all complete JSONs
        if part.strip():
            try:
                messages.append(json.loads(part))
            except json.JSONDecodeError:
                pass
    return messages, parts[-1]  # return leftover
