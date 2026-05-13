"""Centralized logging for navegador-automate."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "navegador_automate",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure and return a logger with file + stdout handlers.

    Args:
        name: Logger name.
        level: Logging level (default: INFO).
        log_file: Path to log file. If None, only stdout.
        max_bytes: Max log file size before rotation (default: 10MB).
        backup_count: Number of backup files to keep (default: 5).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


_default_logger = setup_logger()


def log(component: str, message: str, level: str = "info", secure: bool = False) -> None:
    """
    Log a message without exposing passwords.

    Args:
        component: Component name (e.g., "BrowserFactory", "Executor").
        message: Message to log.
        level: Log level ("debug", "info", "warning", "error").
        secure: If True, mask sensitive values in message.
    """
    if secure:
        message = _mask_sensitive_data(message)

    log_message = f"[{component}] {message}"
    getattr(_default_logger, level)(log_message)


def _mask_sensitive_data(message: str) -> str:
    """Mask passwords and sensitive values in log messages."""
    sensitive_keywords = ["password", "token", "secret", "api_key", "credential"]
    masked = message

    for keyword in sensitive_keywords:
        if keyword.lower() in masked.lower():
            masked = masked.replace("=", "=***")

    return masked


def get_logger(name: str = "navegador_automate") -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)
