import json

# We’ll separate each JSON message with a newline (\n)
DELIMITER = b"\n"


def encode(data: dict) -> bytes:
    """
    Convert a Python dict into JSON bytes with delimiter.
    Ensures each message is newline-terminated for framing.
    """
    try:
        return (json.dumps(data, separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to encode message: {e}")


def decode_stream(buffer: bytes):
    """
    Decode a continuous byte stream into individual JSON messages.

    TCP is a stream protocol — you may receive:
        - half a JSON message
        - multiple JSONs in one recv()
    This function safely splits the buffer by newline, decodes each
    full JSON, and returns:
        (list_of_decoded_messages, leftover_bytes)
    """
    messages = []
    try:
        parts = buffer.split(DELIMITER)
        for part in parts[:-1]:  # complete messages
            if part.strip():
                try:
                    # decode each JSON part safely
                    messages.append(json.loads(part.decode("utf-8")))
                except json.JSONDecodeError:
                    # skip malformed JSON fragments
                    continue

        leftover = parts[-1]  # last part (incomplete JSON)
        return messages, leftover
    except Exception as e:
        # In case of corrupted buffer or unexpected format
        print(f"[ERROR] decode_stream failed: {e}")
        return [], buffer
