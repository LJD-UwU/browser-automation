"""BrowserFactory: Builder pattern for browser creation."""

from pathlib import Path
from typing import Optional

from navegador_automate.browser.session import BrowserSession
from navegador_automate.utils.logger import log


class BrowserFactory:
    """Factory for creating BrowserSession instances."""

    def __init__(self, browser_type: str):
        self._browser_type = browser_type
        self._headless = False
        self._download_dir: Optional[Path] = None
        self._profile_dir: Optional[Path] = None
        self._driver_path: Optional[Path] = None

    @staticmethod
    def edge() -> "BrowserFactory":
        """Create Edge factory."""
        return BrowserFactory("edge")

    @staticmethod
    def chrome() -> "BrowserFactory":
        """Create Chrome factory."""
        return BrowserFactory("chrome")

    @staticmethod
    def firefox() -> "BrowserFactory":
        """Create Firefox factory."""
        return BrowserFactory("firefox")

    def with_headless(self, enabled: bool = True) -> "BrowserFactory":
        """Set headless mode."""
        self._headless = enabled
        return self

    def with_download_dir(self, directory: Path | str) -> "BrowserFactory":
        """Set download directory."""
        self._download_dir = Path(directory) if isinstance(directory, str) else directory
        return self

    def with_profile_dir(self, directory: Path | str) -> "BrowserFactory":
        """Set profile directory."""
        self._profile_dir = Path(directory) if isinstance(directory, str) else directory
        return self

    def with_driver_path(self, path: Path | str) -> "BrowserFactory":
        """Set driver path."""
        self._driver_path = Path(path) if isinstance(path, str) else path
        return self

    def view_window(self, visible: bool = True) -> "BrowserFactory":
        """
        Control browser window visibility.

        Args:
            visible: True to show window, False to hide (headless mode)

        Returns:
            self (for method chaining)
        """
        self._headless = not visible
        return self

    def build(self) -> BrowserSession:
        """Build and launch browser."""
        log("BrowserFactory", f"Building {self._browser_type}", level="info")

        session = BrowserSession(
            browser_type=self._browser_type,
            headless=self._headless,
            download_dir=self._download_dir,
            profile_dir=self._profile_dir,
            driver_path=self._driver_path,
        )
        session.launch()
        return session
