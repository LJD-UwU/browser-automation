"""Driver manager: download and manage WebDriver binaries."""

import platform
import subprocess
import re
import requests
import zipfile
import io
from pathlib import Path

from navegador_automate.utils.logger import log


class DriverManager:
    """Manage WebDriver binaries for Edge, Chrome, Firefox."""

    def __init__(self, browser: str):
        self.browser = browser.lower()
        self.system = platform.system()

    def get_driver_path(self) -> Path:
        """Get or download the appropriate WebDriver."""
        if self.browser == "edge":
            return self._get_edge_driver()
        elif self.browser == "chrome":
            return self._get_chrome_driver()
        elif self.browser == "firefox":
            return self._get_firefox_driver()
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")

    def _get_edge_driver(self) -> Path:
        """Get or download MSEdgeDriver."""
        drivers_dir = Path(__file__).parent / "binaries"
        drivers_dir.mkdir(parents=True, exist_ok=True)

        driver_name = "msedgedriver.exe" if self.system == "Windows" else "msedgedriver"
        driver_path = drivers_dir / driver_name

        if driver_path.exists():
            log("DriverManager", f"Found cached Edge driver: {driver_path}", level="info")
            return driver_path

        log("DriverManager", "Downloading MSEdgeDriver...", level="info")
        version = self._get_edge_version()
        return self._download_edge_driver(version, drivers_dir)

    def _get_chrome_driver(self) -> Path:
        """Get or download ChromeDriver."""
        drivers_dir = Path(__file__).parent / "binaries"
        drivers_dir.mkdir(parents=True, exist_ok=True)

        driver_name = "chromedriver.exe" if self.system == "Windows" else "chromedriver"
        driver_path = drivers_dir / driver_name

        if driver_path.exists():
            log("DriverManager", f"Found cached Chrome driver: {driver_path}", level="info")
            return driver_path

        log("DriverManager", "Downloading ChromeDriver...", level="info")
        version = self._get_chrome_version()
        return self._download_chrome_driver(version, drivers_dir)

    def _get_firefox_driver(self) -> Path:
        """Get or download GeckoDriver."""
        drivers_dir = Path(__file__).parent / "binaries"
        drivers_dir.mkdir(parents=True, exist_ok=True)

        driver_name = "geckodriver.exe" if self.system == "Windows" else "geckodriver"
        driver_path = drivers_dir / driver_name

        if driver_path.exists():
            log("DriverManager", f"Found cached Firefox driver: {driver_path}", level="info")
            return driver_path

        log("DriverManager", "Downloading GeckoDriver...", level="info")
        return self._download_firefox_driver(drivers_dir)

    def _get_edge_version(self) -> str:
        """Get installed Edge version."""
        try:
            if self.system == "Windows":
                output = subprocess.check_output(
                    ["reg", "query", r"HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon", "/v", "version"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
                if match:
                    return match.group(1)
            elif self.system == "Linux":
                output = subprocess.check_output(["microsoft-edge", "--version"], text=True)
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
                if match:
                    return match.group(1)
        except Exception as e:
            log("DriverManager", f"Could not detect Edge version: {e}", level="warning")

        return "latest"

    def _get_chrome_version(self) -> str:
        """Get installed Chrome version."""
        try:
            if self.system == "Windows":
                output = subprocess.check_output(
                    ["reg", "query", r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon", "/v", "version"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
                if match:
                    return match.group(1).rsplit(".", 1)[0]
            elif self.system == "Linux":
                output = subprocess.check_output(["google-chrome", "--version"], text=True)
                match = re.search(r"(\d+\.\d+\.\d+)", output)
                if match:
                    return match.group(1)
        except Exception as e:
            log("DriverManager", f"Could not detect Chrome version: {e}", level="warning")

        return "latest"

    def _download_edge_driver(self, version: str, dest_dir: Path) -> Path:
        """Download MSEdgeDriver for specific version."""
        if version == "latest":
            version = "latest"

        if self.system == "Windows":
            url = f"https://msedgedriver.microsoft.com/{version}/edgedriver_win64.zip"
        elif self.system == "Linux":
            url = f"https://msedgedriver.microsoft.com/{version}/edgedriver_linux64.zip"
        else:
            raise RuntimeError(f"Unsupported OS: {self.system}")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(dest_dir)

        driver_name = "msedgedriver.exe" if self.system == "Windows" else "msedgedriver"
        driver_path = dest_dir / driver_name
        driver_path.chmod(0o755)

        log("DriverManager", f"Downloaded MSEdgeDriver {version} to {driver_path}", level="info")
        return driver_path

    def _download_chrome_driver(self, version: str, dest_dir: Path) -> Path:
        """Download ChromeDriver for specific version."""
        if version == "latest":
            version = "latest"

        if self.system == "Windows":
            url = f"https://googlechromelabs.github.io/chrome-for-testing/latest/chrome-for-testing/{version}/win64/chromedriver-{version}.zip"
        elif self.system == "Linux":
            url = f"https://googlechromelabs.github.io/chrome-for-testing/latest/chrome-for-testing/{version}/linux64/chromedriver-{version}.zip"
        else:
            raise RuntimeError(f"Unsupported OS: {self.system}")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(dest_dir)

            driver_name = "chromedriver.exe" if self.system == "Windows" else "chromedriver"
            driver_path = dest_dir / driver_name
            driver_path.chmod(0o755)

            log("DriverManager", f"Downloaded ChromeDriver {version} to {driver_path}", level="info")
            return driver_path
        except Exception as e:
            log("DriverManager", f"ChromeDriver download failed: {e}", level="error")
            raise

    def _download_firefox_driver(self, dest_dir: Path) -> Path:
        """Download GeckoDriver (latest version)."""
        if self.system == "Windows":
            url = "https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-win64.zip"
        elif self.system == "Linux":
            url = "https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz"
        elif self.system == "Darwin":
            url = "https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-macos.tar.gz"
        else:
            raise RuntimeError(f"Unsupported OS: {self.system}")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        if self.system == "Windows":
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(dest_dir)
        else:
            import tarfile
            with tarfile.open(fileobj=io.BytesIO(response.content)) as t:
                t.extractall(dest_dir)

        driver_name = "geckodriver.exe" if self.system == "Windows" else "geckodriver"
        driver_path = dest_dir / driver_name
        driver_path.chmod(0o755)

        log("DriverManager", f"Downloaded GeckoDriver to {driver_path}", level="info")
        return driver_path
