"""Driver detector: locate or download WebDriver binaries."""

from pathlib import Path
from navegador_automate.drivers.manager import DriverManager
from navegador_automate.utils.logger import log


class DriverDetector:
    """Detect and provide WebDriver for the specified browser."""

    def __init__(self, browser: str):
        self.browser = browser.lower()
        self.manager = DriverManager(browser)

    def get_driver_path(self) -> Path:
        """Get path to WebDriver executable (download if necessary)."""
        try:
            driver_path = self.manager.get_driver_path()
            if not driver_path.exists():
                raise FileNotFoundError(f"Driver not found at {driver_path}")
            log("DriverDetector", f"Using driver: {driver_path}", level="info")
            return driver_path
        except Exception as e:
            log("DriverDetector", f"Error getting driver: {e}", level="error")
            raise
