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
        self._drivers_dir: Optional[Path] = None

    @staticmethod
    def edge() -> "BrowserFactory":
        return BrowserFactory("edge")

    @staticmethod
    def chrome() -> "BrowserFactory":
        return BrowserFactory("chrome")

    @staticmethod
    def firefox() -> "BrowserFactory":
        return BrowserFactory("firefox")

    def with_headless(self, enabled: bool = True) -> "BrowserFactory":
        self._headless = enabled
        return self

    def with_download_dir(self, directory) -> "BrowserFactory":
        """Set download directory for browser file downloads."""
        self._download_dir = Path(directory)
        return self

    def with_profile_dir(self, directory) -> "BrowserFactory":
        self._profile_dir = Path(directory)
        return self

    def with_driver_path(self, path) -> "BrowserFactory":
        """Set an explicit driver executable path (skips auto-detection)."""
        self._driver_path = Path(path)
        return self

    def with_drivers_dir(self, directory) -> "BrowserFactory":
        """
        Set the directory where WebDriver binaries will be downloaded and cached.

        By default, navegador_automate detects the calling project's root directory
        and creates a 'drivers/' subfolder there.  Use this method to override that
        location explicitly.

        Example::

            BrowserFactory.edge() \\
                .with_drivers_dir(r"C:\\MyProject\\drivers") \\
                .with_download_dir(DOWNLOAD_DIR) \\
                .build()
        """
        self._drivers_dir = Path(directory)
        return self

    def view_window(self, visible: bool = True) -> "BrowserFactory":
        """Control browser window visibility."""
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
            drivers_dir=self._drivers_dir,
        )
        session.launch()
        return session
