"""Context manager for BrowserSession."""

from typing import Optional
from pathlib import Path
from navegador_automate.browser.factory import BrowserFactory
from navegador_automate.browser.browser import BrowserSession


class BrowserContext:
    """Context manager for safe browser session management."""

    def __init__(
        self,
        browser_type: str = "firefox",
        headless: bool = False,
        download_dir: Optional[Path] = None,
    ):
        """
        Initialize context manager.

        Args:
            browser_type: Browser type (default: firefox).
            headless: Run headless (default: False).
            download_dir: Custom download directory.
        """
        self.browser_type = browser_type
        self.headless = headless
        self.download_dir = download_dir
        self.session: Optional[BrowserSession] = None

    def __enter__(self) -> BrowserSession:
        """Enter context and launch browser."""
        factory = BrowserFactory(self.browser_type).with_headless(self.headless)

        if self.download_dir:
            factory.with_download_dir(self.download_dir)

        self.session = factory.build()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and close browser."""
        if self.session:
            self.session.quit()
