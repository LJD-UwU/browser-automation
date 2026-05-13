"""WebDriver download and caching."""

import zipfile
from pathlib import Path
from typing import Optional
import requests
from navegador_automate.logger import log
from navegador_automate.browser.exceptions import DownloadError


class DriverDownloader:
    """Download and cache WebDriver binaries."""

    BASE_URLS = {
        "firefox": "https://github.com/mozilla/geckodriver/releases/download/v{version}/geckodriver-v{version}-{platform}.zip",
        "chrome": "https://chromedriver.chromium.org/downloads",
        "edge": "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/",
    }

    PLATFORM_MAP = {
        ("Windows", "firefox"): "win64",
        ("Windows", "chrome"): "win64",
        ("Windows", "edge"): "win64",
        ("Darwin", "firefox"): "macos",
        ("Darwin", "chrome"): "mac64",
        ("Darwin", "edge"): "mac64",
        ("Linux", "firefox"): "linux64",
        ("Linux", "chrome"): "linux64",
        ("Linux", "edge"): "linux64",
    }

    def __init__(self, browser: str, version: str, os_name: str):
        """
        Initialize downloader.

        Args:
            browser: Browser name (firefox, chrome, edge).
            version: Driver version to download.
            os_name: OS name (windows, macos, linux).
        """
        self.browser = browser.lower()
        self.version = version
        self.os_name = os_name

    def download(self, dest_dir: Path) -> Path:
        """
        Download and extract driver.

        Args:
            dest_dir: Directory to extract driver to.

        Returns:
            Path to extracted driver executable.

        Raises:
            DownloadError: If download or extraction fails.
        """
        import platform

        system = platform.system()

        if self.browser == "firefox":
            return self._download_firefox(dest_dir, system)
        elif self.browser == "chrome":
            log("DriverDownloader", "Manual Chrome driver download required", level="warning")
            raise DownloadError(
                "Chrome driver download not automated. "
                "Use webdriver-manager or download manually."
            )
        elif self.browser == "edge":
            log("DriverDownloader", "Manual Edge driver download required", level="warning")
            raise DownloadError(
                "Edge driver download not automated. "
                "Use webdriver-manager or download manually."
            )
        else:
            raise DownloadError(f"Download not supported for {self.browser}")

    def _download_firefox(self, dest_dir: Path, system: str) -> Path:
        """Download Firefox GeckoDriver."""
        platform_key = (system, self.browser)
        if platform_key not in self.PLATFORM_MAP:
            raise DownloadError(f"Unsupported platform for {self.browser}")

        platform_str = self.PLATFORM_MAP[platform_key]
        url = self.BASE_URLS["firefox"].format(version=self.version, platform=platform_str)

        try:
            log("DriverDownloader", f"Downloading from {url}", level="info")

            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            zip_path = dest_dir / f"geckodriver-{self.version}.zip"
            dest_dir.mkdir(parents=True, exist_ok=True)

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            log("DriverDownloader", f"Downloaded: {zip_path}", level="debug")

            extract_dir = dest_dir / f"geckodriver-{self.version}"
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(extract_dir)

            zip_path.unlink()

            driver_name = "geckodriver.exe" if system == "Windows" else "geckodriver"
            driver_path = extract_dir / driver_name

            if not driver_path.exists():
                raise DownloadError(f"Driver not found in archive: {driver_path}")

            driver_path.chmod(0o755)
            log("DriverDownloader", f"Extracted driver: {driver_path}", level="info")

            return driver_path

        except requests.RequestException as e:
            raise DownloadError(f"Failed to download driver: {e}")
        except (zipfile.BadZipFile, FileNotFoundError) as e:
            raise DownloadError(f"Failed to extract driver: {e}")
