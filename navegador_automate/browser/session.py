"""BrowserSession: Minimal Selenium wrapper."""

from pathlib import Path
from typing import Optional
import time

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from navegador_automate.utils.logger import log
from navegador_automate.drivers.detector import DriverDetector


class BrowserSession:
    """Simple Selenium WebDriver wrapper."""

    def __init__(
        self,
        browser_type: str,
        headless: bool = False,
        download_dir: Optional[Path] = None,
        profile_dir: Optional[Path] = None,
        driver_path: Optional[Path] = None,
        drivers_dir: Optional[Path] = None,
    ):
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.download_dir = Path(download_dir) if download_dir else Path.home() / "Downloads"
        self.profile_dir = Path(profile_dir) if profile_dir else Path.home() / ".browser_profiles" / browser_type
        self.driver_path = Path(driver_path) if driver_path else None
        self.drivers_dir = Path(drivers_dir) if drivers_dir else None
        self.driver = None
        self.timeout = 15

    def launch(self) -> None:
        """Launch the browser."""
        log("BrowserSession", f"Launching {self.browser_type}", level="info")

        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        if not self.driver_path:
            detector = DriverDetector(self.browser_type, drivers_dir=self.drivers_dir)
            self.driver_path = detector.get_driver_path()

        if self.browser_type == "edge":
            self._launch_edge()
        elif self.browser_type == "chrome":
            self._launch_chrome()
        elif self.browser_type == "firefox":
            self._launch_firefox()
        else:
            raise ValueError(f"Unsupported browser: {self.browser_type}")

        log("BrowserSession", f"{self.browser_type} launched", level="info")

    def _launch_edge(self) -> None:
        """Launch Edge browser."""
        options = EdgeOptions()
        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")

        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.open_pdf_in_system_reader": False,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "browser.show_hub_popup_on_download_start": False,
        }
        options.add_experimental_option("prefs", prefs)

        service = EdgeService(executable_path=str(self.driver_path))
        self.driver = webdriver.Edge(service=service, options=options)

    def _launch_chrome(self) -> None:
        """Launch Chrome browser."""
        options = ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        }
        options.add_experimental_option("prefs", prefs)

        service = ChromeService(executable_path=str(self.driver_path))
        self.driver = webdriver.Chrome(service=service, options=options)

    def _launch_firefox(self) -> None:
        """Launch Firefox browser.

        Firefox uses profile arguments and about:config prefs for configuration —
        NOT --user-data-dir (that is a Chromium-only argument which causes Firefox
        to fail silently or error).
        """
        options = FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")

        # Download preferences via about:config
        options.set_preference("browser.download.dir", str(self.download_dir))
        options.set_preference("browser.download.folderList", 2)  # 2 = custom dir
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/octet-stream,application/zip,text/csv,"
            "application/vnd.ms-excel,"
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Persistent profile directory (Firefox-compatible way)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        options.add_argument("-profile")
        options.add_argument(str(self.profile_dir))

        # Window size (Firefox uses these args instead of --window-size)
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")

        service = FirefoxService(executable_path=str(self.driver_path))
        self.driver = webdriver.Firefox(service=service, options=options)

    def open(self, url: str) -> None:
        """Navigate to URL."""
        if not self.driver:
            self.launch()
        self.driver.get(url)
        log("BrowserSession", f"Opened: {url}", level="debug")

    def click(self, selector: str) -> None:
        """Click element."""
        element = self._find_element(selector)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.2)
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)
        log("BrowserSession", f"Clicked: {selector}", level="debug")

    def type_text(self, selector: str, text: str) -> None:
        """Type text into element."""
        element = self._find_element(selector)
        element.clear()
        element.send_keys(text)
        log("BrowserSession", f"Typed into: {selector}", level="debug")

    def pause(self, seconds: float) -> None:
        """Wait for specified seconds."""
        time.sleep(seconds)

    def get_text(self, selector: str) -> str:
        """Get element text."""
        element = self._find_element(selector)
        return element.text.strip()

    def get_attribute(self, selector: str, attr: str) -> str:
        """Get element attribute."""
        element = self._find_element(selector)
        return element.get_attribute(attr)

    def quit(self) -> None:
        """Close browser."""
        if self.driver:
            self.driver.quit()
            log("BrowserSession", "Browser closed", level="info")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()

    def _find_element(self, selector: str):
        """Find element by selector."""
        by, value = self._parse_selector(selector)
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    @staticmethod
    def _parse_selector(selector: str):
        """Parse selector string."""
        if selector.startswith("xpath="):
            return (By.XPATH, selector[6:])
        elif selector.startswith("css="):
            return (By.CSS_SELECTOR, selector[4:])
        elif selector.startswith("id="):
            return (By.ID, selector[3:])
        elif selector.startswith("name="):
            return (By.NAME, selector[5:])
        elif selector.startswith("//"):
            return (By.XPATH, selector)
        else:
            return (By.XPATH, selector)
