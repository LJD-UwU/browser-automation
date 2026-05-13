"""Flow executor - executes steps from JSON."""

import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver
from navegador_automate.flows.definition import FlowDefinition
from navegador_automate.flows.parser import FlowParser
from navegador_automate.logger import log
from navegador_automate.browser.exceptions import (
    FlowExecutionError,
    BrowserTimeoutError,
    SelectorNotFoundError,
)


class Executor:
    """Execute browser automation flows."""

    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self, driver: WebDriver):
        """
        Initialize executor.

        Args:
            driver: Selenium WebDriver instance.
        """
        self.driver = driver
        self.parser = FlowParser()
        self.logs: List[str] = []

    def execute_flow(
        self,
        flow: FlowDefinition,
        credentials: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a complete flow (login + steps).

        Args:
            flow: FlowDefinition to execute.
            credentials: Dictionary with USERNAME, PASSWORD, etc.

        Returns:
            Dictionary with execution results.
        """
        self.logs.clear()
        credentials = credentials or {}

        try:
            log("Executor", f"Executing flow: {flow.name}", level="info")

            self._log(f"Starting flow: {flow.name}")

            login_steps = self.parser.load_steps(flow.login)
            self._log(f"Loaded {len(login_steps)} login steps")

            self.execute_steps(login_steps, credentials)
            self._log("Login completed successfully")

            main_steps = self.parser.load_steps(flow.steps)
            self._log(f"Loaded {len(main_steps)} main steps")

            self.execute_steps(main_steps, credentials)
            self._log("Main steps completed successfully")

            result = {
                "success": True,
                "flow_name": flow.name,
                "logs": self.logs,
                "downloaded_file": None,
            }

            if flow.download_keyword:
                downloaded_file = self._find_downloaded_file(flow.download_keyword)
                result["downloaded_file"] = str(downloaded_file) if downloaded_file else None
                self._log(f"Downloaded file: {result['downloaded_file']}")

            log("Executor", f"Flow {flow.name} completed successfully", level="info")
            return result

        except Exception as e:
            self._log(f"Error: {str(e)}")
            log("Executor", f"Flow {flow.name} failed: {e}", level="error")

            return {
                "success": False,
                "flow_name": flow.name,
                "error": str(e),
                "logs": self.logs,
                "downloaded_file": None,
            }

    def execute_steps(
        self,
        steps: List[Dict[str, Any]],
        credentials: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Execute list of steps.

        Args:
            steps: List of step dictionaries.
            credentials: Credentials for interpolation.

        Raises:
            FlowExecutionError: If any step fails.
        """
        credentials = credentials or {}

        for idx, step in enumerate(steps, 1):
            try:
                self.parser.validate_step(step)
                self._execute_step(step, credentials)
                self._log(f"Step {idx}/{len(steps)}: {step['command']} OK")

            except Exception as e:
                self._log(f"Step {idx}/{len(steps)}: {step['command']} FAILED - {str(e)}")
                raise FlowExecutionError(f"Step {idx} failed: {e}") from e

    def _execute_step(self, step: Dict[str, Any], credentials: Dict[str, Any]) -> None:
        """
        Execute a single step.

        Args:
            step: Step dictionary.
            credentials: Credentials for interpolation.

        Raises:
            FlowExecutionError: If step fails.
        """
        command = step.get("command", "").lower()
        target = step.get("target", "")
        value = step.get("value", "")

        target = self.parser.interpolate_value(target, credentials)
        value = self.parser.interpolate_value(value, credentials)

        log("Executor", f"Executing: {command} {target}", level="debug")

        if command == "open":
            self.driver.get(target)

        elif command == "click":
            element = self._find_element(target)
            element.click()

        elif command == "type":
            element = self._find_element(target)
            element.clear()
            element.send_keys(value)

        elif command == "pause":
            delay = int(value) / 1000  # value in milliseconds
            time.sleep(delay)

        elif command == "wait":
            timeout = int(value) / 1000 if value else 10
            self._wait_for_element(target, timeout)

        elif command == "key":
            self._press_key(value)

        elif command == "get_text":
            element = self._find_element(target)
            text = element.text
            self._log(f"Got text: {text[:50]}")

        elif command == "get_attribute":
            element = self._find_element(target)
            attr_value = element.get_attribute(value)
            self._log(f"Got attribute: {attr_value}")

        elif command == "check_visible":
            self._wait_for_element(target, timeout=2)

        else:
            raise FlowExecutionError(f"Unknown command: {command}")

    def _find_element(self, selector: str):
        """Find element with retry logic."""
        for attempt in range(self.MAX_RETRIES):
            try:
                selector_type, selector_value = self.parser.parse_selector(selector)

                if selector_type == "xpath":
                    from selenium.webdriver.common.by import By

                    return self.driver.find_element(By.XPATH, selector_value)
                elif selector_type == "css":
                    from selenium.webdriver.common.by import By

                    return self.driver.find_element(By.CSS_SELECTOR, selector_value)
                elif selector_type == "id":
                    from selenium.webdriver.common.by import By

                    return self.driver.find_element(By.ID, selector_value)
                else:
                    from selenium.webdriver.common.by import By

                    return self.driver.find_element(By.XPATH, selector_value)

            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise SelectorNotFoundError(f"Element not found: {selector}") from e

    def _wait_for_element(self, selector: str, timeout: float = 10) -> None:
        """Wait for element to appear."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        selector_type, selector_value = self.parser.parse_selector(selector)

        if selector_type == "xpath":
            by = By.XPATH
        elif selector_type == "css":
            by = By.CSS_SELECTOR
        elif selector_type == "id":
            by = By.ID
        else:
            by = By.XPATH

        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((by, selector_value)))
        except Exception as e:
            raise BrowserTimeoutError(f"Element not found: {selector} (timeout: {timeout}s)") from e

    def _press_key(self, key_name: str) -> None:
        """Press a keyboard key."""
        from selenium.webdriver.common.keys import Keys

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
            raise FlowExecutionError(f"Unknown key: {key_name}")

        self.driver.switch_to.active_element.send_keys(key)

    def _find_downloaded_file(self, keyword: str) -> Optional[Path]:
        """
        Find downloaded file by keyword in name.

        Args:
            keyword: Keyword to search in filename.

        Returns:
            Path to downloaded file or None.
        """
        from navegador_automate.utils.paths import DOWNLOAD_DIR

        try:
            for file in DOWNLOAD_DIR.glob("*"):
                if keyword.lower() in file.name.lower():
                    self._log(f"Found downloaded file: {file.name}")
                    return file

            self._log(f"No downloaded file found with keyword: {keyword}")
            return None

        except Exception as e:
            log("Executor", f"Error finding downloaded file: {e}", level="warning")
            return None

    def _log(self, message: str) -> None:
        """Add message to logs."""
        self.logs.append(message)
