"""BrowserFactory: Builder pattern for BrowserSession creation."""

from pathlib import Path
from typing import Optional
from navegador_automate.browser.browser import BrowserSession
from navegador_automate.logger import log


class BrowserFactory:
    """Factory for creating BrowserSession instances using builder pattern."""

    def __init__(self, browser_type: str):
        """
        Initialize factory.

        Args:
            browser_type: Browser type (firefox, edge, chrome, safari).
        """
        self._browser_type = browser_type
        self._headless = False
        self._download_dir: Optional[Path] = None
        self._profile_dir: Optional[Path] = None

    @staticmethod
    def firefox() -> "BrowserFactory":
        """Create Firefox factory."""
        log("BrowserFactory", "Creating Firefox factory", level="debug")
        return BrowserFactory("firefox")

    @staticmethod
    def edge() -> "BrowserFactory":
        """Create Edge factory."""
        log("BrowserFactory", "Creating Edge factory", level="debug")
        return BrowserFactory("edge")

    @staticmethod
    def chrome() -> "BrowserFactory":
        """Create Chrome factory."""
        log("BrowserFactory", "Creating Chrome factory", level="debug")
        return BrowserFactory("chrome")

    @staticmethod
    def safari() -> "BrowserFactory":
        """Create Safari factory."""
        log("BrowserFactory", "Creating Safari factory", level="debug")
        return BrowserFactory("safari")

    def with_headless(self, enabled: bool = True) -> "BrowserFactory":
        """
        Enable headless mode.

        Args:
            enabled: Whether to run headless.

        Returns:
            Self for chaining.
        """
        self._headless = enabled
        log("BrowserFactory", f"Headless mode: {enabled}", level="debug")
        return self

    def with_download_dir(self, directory: Path | str) -> "BrowserFactory":
        """
        Set custom download directory.

        Args:
            directory: Directory path.

        Returns:
            Self for chaining.
        """
        self._download_dir = Path(directory)
        log("BrowserFactory", f"Download dir: {self._download_dir}", level="debug")
        return self

    def with_profile_dir(self, directory: Path | str) -> "BrowserFactory":
        """
        Set custom profile directory.

        Args:
            directory: Directory path.

        Returns:
            Self for chaining.
        """
        self._profile_dir = Path(directory)
        log("BrowserFactory", f"Profile dir: {self._profile_dir}", level="debug")
        return self

    def build(self) -> BrowserSession:
        """
        Build and launch BrowserSession.

        Returns:
            Configured BrowserSession.
        """
        log("BrowserFactory", f"Building {self._browser_type} session", level="info")

        session = BrowserSession(
            browser_type=self._browser_type,
            headless=self._headless,
            download_dir=self._download_dir,
            profile_dir=self._profile_dir,
        )

        session.launch()
        return session
