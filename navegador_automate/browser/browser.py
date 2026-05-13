"""BrowserSession: Selenium wrapper without Config dependency."""

from pathlib import Path
from typing import Optional, List
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from navegador_automate.logger import log
from navegador_automate.browser.exceptions import (
    BrowserLaunchError,
    BrowserTimeoutError,
    SelectorNotFoundError,
)
from navegador_automate.drivers.detector import DriverDetector
from navegador_automate.utils.paths import PROFILES_DIR, DOWNLOAD_DIR


class BrowserSession:
    """High-level browser session interface."""

    def __init__(
        self,
        browser_type: str,
        headless: bool = False,
        download_dir: Optional[Path] = None,
        profile_dir: Optional[Path] = None,
    ):
        """
        Initialize browser session.

        Args:
            browser_type: Browser type (firefox, edge, chrome, safari).
            headless: Run in headless mode.
            download_dir: Custom download directory.
            profile_dir: Custom profile directory.
        """
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.download_dir = download_dir or DOWNLOAD_DIR
        self.profile_dir = profile_dir or (PROFILES_DIR / browser_type)
        self.driver = None

    def launch(self) -> None:
        """
        Launch browser.

        Raises:
            BrowserLaunchError: If browser fails to launch.
        """
        try:
            log("BrowserSession", f"Launching {self.browser_type}", level="info")

            detector = DriverDetector(self.browser_type)
            driver_path = detector.get_driver_path()

            if self.browser_type == "firefox":
                self.driver = self._launch_firefox(driver_path)
            elif self.browser_type == "edge":
                self.driver = self._launch_edge(driver_path)
            elif self.browser_type == "chrome":
                self.driver = self._launch_chrome(driver_path)
            else:
                raise BrowserLaunchError(f"Unsupported browser: {self.browser_type}")

            self.driver.set_page_load_timeout(30)
            log("BrowserSession", f"{self.browser_type} launched", level="info")

        except Exception as e:
            raise BrowserLaunchError(f"Failed to launch {self.browser_type}: {e}")

    def _launch_firefox(self, driver_path: Path) -> webdriver.Firefox:
        """Launch Firefox browser."""
        options = webdriver.FirefoxOptions()

        if self.headless:
            options.add_argument("--headless")

        options.add_argument("--width=1920")
        options.add_argument("--height=1080")

        prefs = {
            "browser.download.folderList": 2,
            "browser.download.manager.showWhenStarting": False,
            "browser.download.dir": str(self.download_dir),
            "browser.helperApps.neverAsk.saveToDisk": "application/octet-stream,application/pdf",
        }
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", str(self.download_dir))

        return webdriver.Firefox(options=options, service=webdriver.FirefoxService(str(driver_path)))

    def _launch_edge(self, driver_path: Path) -> webdriver.Edge:
        """Launch Edge browser."""
        options = webdriver.EdgeOptions()

        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("detach", True)

        return webdriver.Edge(options=options, service=webdriver.EdgeService(str(driver_path)))

    def _launch_chrome(self, driver_path: Path) -> webdriver.Chrome:
        """Launch Chrome browser."""
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
        }
        options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(options=options, service=webdriver.ChromeService(str(driver_path)))

    def open(self, url: str) -> None:
        """
        Open URL.

        Args:
            url: URL to open.
        """
        if not self.driver:
            self.launch()

        log("BrowserSession", f"Opening {url}", level="debug")
        self.driver.get(url)

    def click(self, selector: str) -> None:
        """
        Click element by selector.

        Args:
            selector: CSS or XPath selector.

        Raises:
            SelectorNotFoundError: If element not found.
        """
        element = self._find_element(selector)
        log("BrowserSession", f"Clicking {selector}", level="debug")
        element.click()

    def type_text(self, selector: str, text: str) -> None:
        """
        Type text into element.

        Args:
            selector: CSS or XPath selector.
            text: Text to type.

        Raises:
            SelectorNotFoundError: If element not found.
        """
        element = self._find_element(selector)
        element.clear()
        log("BrowserSession", f"Typing into {selector}", level="debug", secure=True)
        element.send_keys(text)

    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """
        Wait for element to be present.

        Args:
            selector: CSS or XPath selector.
            timeout: Timeout in seconds.

        Returns:
            True if element found, False otherwise.

        Raises:
            BrowserTimeoutError: If timeout exceeded.
        """
        try:
            by, value = self._parse_selector(selector)
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((by, value)))
            log("BrowserSession", f"Element found: {selector}", level="debug")
            return True
        except TimeoutException:
            raise BrowserTimeoutError(f"Element not found: {selector} (timeout: {timeout}s)")

    def press_key(self, key_name: str) -> None:
        """
        Press a key.

        Args:
            key_name: Key name (ENTER, TAB, ESCAPE, etc.).
        """
        key_map = {
            "ENTER": Keys.ENTER,
            "TAB": Keys.TAB,
            "ESCAPE": Keys.ESCAPE,
            "SPACE": Keys.SPACE,
            "DELETE": Keys.DELETE,
            "BACKSPACE": Keys.BACKSPACE,
        }

        key = key_map.get(key_name.upper())
        if not key:
            raise ValueError(f"Unknown key: {key_name}")

        self.driver.switch_to.active_element.send_keys(key)
        log("BrowserSession", f"Pressed key: {key_name}", level="debug")

    def get_text(self, selector: str) -> str:
        """
        Get element text.

        Args:
            selector: CSS or XPath selector.

        Returns:
            Element text.

        Raises:
            SelectorNotFoundError: If element not found.
        """
        element = self._find_element(selector)
        return element.text

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get element attribute.

        Args:
            selector: CSS or XPath selector.
            attribute: Attribute name.

        Returns:
            Attribute value or None.

        Raises:
            SelectorNotFoundError: If element not found.
        """
        element = self._find_element(selector)
        return element.get_attribute(attribute)

    def is_element_visible(self, selector: str) -> bool:
        """
        Check if element is visible.

        Args:
            selector: CSS or XPath selector.

        Returns:
            True if visible, False otherwise.
        """
        try:
            by, value = self._parse_selector(selector)
            wait = WebDriverWait(self.driver, 2)
            wait.until(EC.visibility_of_element_located((by, value)))
            return True
        except (TimeoutException, StaleElementReferenceException):
            return False

    def pause(self, seconds: float) -> None:
        """
        Pause execution.

        Args:
            seconds: Number of seconds to pause.
        """
        log("BrowserSession", f"Pausing for {seconds}s", level="debug")
        time.sleep(seconds)

    def quit(self) -> None:
        """Close browser session."""
        if self.driver:
            self.driver.quit()
            log("BrowserSession", "Browser closed", level="info")

    def __enter__(self) -> "BrowserSession":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.quit()

    def _find_element(self, selector: str):
        """
        Find element by selector.

        Args:
            selector: CSS or XPath selector.

        Returns:
            WebElement.

        Raises:
            SelectorNotFoundError: If element not found.
        """
        try:
            by, value = self._parse_selector(selector)
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            raise SelectorNotFoundError(f"Element not found: {selector}")

    @staticmethod
    def _parse_selector(selector: str) -> tuple:
        """
        Parse selector string to (By, value).

        Args:
            selector: Selector in format "css=...", "xpath=...", "id=...", etc.

        Returns:
            Tuple of (By type, selector value).
        """
        if selector.startswith("xpath="):
            return (By.XPATH, selector[6:])
        elif selector.startswith("css="):
            return (By.CSS_SELECTOR, selector[4:])
        elif selector.startswith("id="):
            return (By.ID, selector[3:])
        elif selector.startswith("name="):
            return (By.NAME, selector[5:])
        elif selector.startswith("class="):
            return (By.CLASS_NAME, selector[6:])
        elif selector.startswith("tag="):
            return (By.TAG_NAME, selector[4:])
        else:
            return (By.XPATH, selector)
