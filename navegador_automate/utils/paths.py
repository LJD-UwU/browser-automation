"""Path management for navegador-automate."""

from pathlib import Path
import platform
import os


def _get_platform_data_dir() -> Path:
    """Get platform-specific data directory."""
    system = platform.system()

    if system == "Windows":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    return base / "navegador-automate"


DATA_DIR = _get_platform_data_dir()
DRIVERS_DIR = DATA_DIR / "drivers"
PROFILES_DIR = DATA_DIR / "profiles"
DOWNLOAD_DIR = DATA_DIR / "downloads"
LOGS_DIR = DATA_DIR / "logs"

LOG_FILE = LOGS_DIR / "navegador-automate.log"


def ensure_dirs() -> None:
    """Create all necessary directories."""
    for directory in [DATA_DIR, DRIVERS_DIR, PROFILES_DIR, DOWNLOAD_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def get_driver_cache_path(browser: str, version: str, os_name: str) -> Path:
    """
    Get cache path for a specific driver version.

    Args:
        browser: Browser name (firefox, edge, chrome, safari).
        version: Driver version.
        os_name: OS name (windows, linux, macos).

    Returns:
        Path to cached driver.
    """
    return DRIVERS_DIR / browser / version / os_name


ensure_dirs()
