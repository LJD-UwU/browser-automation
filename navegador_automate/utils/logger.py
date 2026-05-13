"""Simple logging utility."""

import sys
from datetime import datetime


def log(component: str, message: str, level: str = "info") -> None:
    """Log a message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    level_upper = level.upper()

    # Color codes
    colors = {
        "INFO": "\033[94m",  # Blue
        "ERROR": "\033[91m",  # Red
        "WARNING": "\033[93m",  # Yellow
        "OK": "\033[92m",  # Green
        "DEBUG": "\033[90m",  # Gray
    }

    color = colors.get(level_upper, "")
    reset = "\033[0m"

    if sys.stdout.isatty():
        print(f"{color}[{timestamp}] [{level_upper}] {component}: {message}{reset}")
    else:
        print(f"[{timestamp}] [{level_upper}] {component}: {message}")
