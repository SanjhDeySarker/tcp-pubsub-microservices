import datetime

def log(event: str, message: str):
    """Simple timestamped logger."""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{event}] {message}")
