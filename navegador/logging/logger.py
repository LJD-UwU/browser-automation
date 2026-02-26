import threading
from datetime import datetime


_lock = threading.Lock()


def log(name: str, message: str, level: str = "INFO"):
    """Imprime un mensaje de log con timestamp y protección thread-safe."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with _lock:
        print(f"[{timestamp}] [{name}] [{level}] {message}")