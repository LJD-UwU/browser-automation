"""WebDriver detection for multiple OS and browsers."""

import platform
import subprocess
import re
from pathlib import Path
from typing import Optional
from navegador_automate.logger import log
from navegador_automate.browser.exceptions import DriverNotFoundError


class DriverDetector:
    """Detect installed browser versions and driver paths."""

    def __init__(self, browser: str):
        """
        Initialize driver detector.

        Args:
            browser: Browser name (firefox, edge, chrome, safari).
        """
        self.browser = browser.lower()
        self.system = platform.system()
        self.os_name = self._get_os_name()

    def _get_os_name(self) -> str:
        """Get normalized OS name."""
        if self.system == "Windows":
            return "windows"
        elif self.system == "Darwin":
            return "macos"
        else:
            return "linux"

    def get_browser_version(self) -> Optional[str]:
        """
        Detect installed browser version.

        Returns:
            Browser version string or None if not found.
        """
        if self.system == "Windows":
            return self._detect_windows_version()
        elif self.system == "Darwin":
            return self._detect_macos_version()
        else:
            return self._detect_linux_version()

    def _detect_windows_version(self) -> Optional[str]:
        """Detect browser version on Windows via registry."""
        try:
            import winreg

            browser_paths = {
                "firefox": r"SOFTWARE\Mozilla\Mozilla Firefox",
                "chrome": r"SOFTWARE\Google\Chrome\BLBeacon",
                "edge": r"SOFTWARE\Microsoft\Edge\BLBeacon",
            }

            if self.browser not in browser_paths:
                return None

            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, browser_paths[self.browser]) as key:
                    version, _ = winreg.QueryValueEx(key, "version")
                    return version
            except (OSError, FileNotFoundError):
                return None

        except ImportError:
            log("DriverDetector", "winreg not available", level="warning")
            return None

    def _detect_macos_version(self) -> Optional[str]:
        """Detect browser version on macOS."""
        try:
            if self.browser == "firefox":
                cmd = [
                    "mdls",
                    "-name",
                    "kMDItemVersion",
                    "/Applications/Firefox.app",
                ]
            elif self.browser == "chrome":
                cmd = [
                    "mdls",
                    "-name",
                    "kMDItemVersion",
                    "/Applications/Google Chrome.app",
                ]
            elif self.browser == "safari":
                cmd = [
                    "mdls",
                    "-name",
                    "kMDItemVersion",
                    "/Applications/Safari.app",
                ]
            else:
                return None

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            match = re.search(r"(\d+\.\d+)", result.stdout)
            return match.group(1) if match else None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def _detect_linux_version(self) -> Optional[str]:
        """Detect browser version on Linux."""
        try:
            cmd_map = {
                "firefox": "firefox --version",
                "chrome": "google-chrome --version",
                "chromium": "chromium --version",
                "edge": "microsoft-edge --version",
            }

            if self.browser not in cmd_map:
                return None

            result = subprocess.run(
                cmd_map[self.browser].split(),
                capture_output=True,
                text=True,
                timeout=5,
            )
            match = re.search(r"(\d+\.\d+)", result.stdout)
            return match.group(1) if match else None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def get_driver_path(self) -> Path:
        """
        Get path to WebDriver executable.

        Returns:
            Path to WebDriver.

        Raises:
            DriverNotFoundError: If driver is not found.
        """
        version = self.get_browser_version()

        if not version:
            log(
                "DriverDetector",
                f"Could not detect {self.browser} version",
                level="warning",
            )
            return self._get_fallback_driver()

        driver_path = self._get_cached_driver_path(version)

        if driver_path.exists():
            log(
                "DriverDetector",
                f"Found cached driver: {driver_path}",
                level="debug",
            )
            return driver_path

        log(
            "DriverDetector",
            f"Cached driver not found, using webdriver-manager",
            level="info",
        )
        return self._get_fallback_driver()

    def _get_cached_driver_path(self, version: str) -> Path:
        """Get expected cached driver path."""
        from navegador_automate.utils.paths import get_driver_cache_path

        driver_map = {
            "firefox": "geckodriver",
            "chrome": "chromedriver",
            "edge": "msedgedriver",
            "safari": "safaridriver",
        }

        driver_name = driver_map.get(self.browser, "driver")

        if self.os_name == "windows":
            driver_name += ".exe"

        return get_driver_cache_path(self.browser, version, self.os_name) / driver_name

    def _get_fallback_driver(self) -> Path:
        """Get driver using webdriver-manager fallback."""
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.microsoft import EdgeChromiumDriverManager

            manager_map = {
                "firefox": GeckoDriverManager(),
                "chrome": ChromeDriverManager(),
                "edge": EdgeChromiumDriverManager(),
            }

            if self.browser not in manager_map:
                raise DriverNotFoundError(
                    f"No webdriver-manager support for {self.browser}"
                )

            driver_path = manager_map[self.browser].install()
            log(
                "DriverDetector",
                f"Downloaded driver via webdriver-manager: {driver_path}",
                level="info",
            )
            return Path(driver_path)

        except ImportError:
            raise DriverNotFoundError(
                "webdriver-manager not installed. "
                "Install with: pip install webdriver-manager"
            )
