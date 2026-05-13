"""Utilities module for navegador-automate."""

from navegador_automate.utils.file_manager import FileManager
from navegador_automate.utils.paths import (
    DATA_DIR,
    DRIVERS_DIR,
    PROFILES_DIR,
    DOWNLOAD_DIR,
    LOGS_DIR,
    ensure_dirs,
)

__all__ = [
    "FileManager",
    "DATA_DIR",
    "DRIVERS_DIR",
    "PROFILES_DIR",
    "DOWNLOAD_DIR",
    "LOGS_DIR",
    "ensure_dirs",
]
