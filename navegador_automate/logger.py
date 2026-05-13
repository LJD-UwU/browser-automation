"""Minimalist logging for navegador-automate."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "navegador_automate",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """Configure logger with minimalist format."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter("%(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


_default_logger = setup_logger()


def _get_timestamp() -> str:
    """Get current time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")


def log(component: str, message: str, level: str = "info", secure: bool = False) -> None:
    """Log message in minimalist format like macro.py."""
    if secure:
        message = _mask_sensitive_data(message)

    tag_map = {"debug": "DBUG", "info": "INFO", "warning": "WARN", "error": "ERR"}
    tag = tag_map.get(level, "INFO")
    timestamp = _get_timestamp()

    log_message = f"[{tag}] [{timestamp}] {message}"
    getattr(_default_logger, level)(log_message)


def _mask_sensitive_data(message: str) -> str:
    """Mask passwords and sensitive values."""
    keywords = ["password", "token", "secret", "api_key", "credential"]
    masked = message
    for keyword in keywords:
        if keyword.lower() in masked.lower():
            masked = masked.replace("=", "=***")
    return masked


def get_logger(name: str = "navegador_automate") -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)
