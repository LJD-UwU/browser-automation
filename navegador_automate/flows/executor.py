"""Flow executor: execute JSON-defined automation steps."""

import json
import time
from pathlib import Path
from typing import Dict, Any

from navegador_automate.utils.logger import log


class Executor:
    """Execute automation steps from JSON files."""

    def __init__(self, browser_session, name: str, variables: Dict[str, str] = None):
        """
        Initialize executor.

        Args:
            browser_session: BrowserSession instance
            name: Name for logging
            variables: Dict of variables to interpolate (${KEY})
        """
        self.session = browser_session
        self.name = name
        self.variables = variables or {}
        self.timeout = 15

    def execute_file(self, json_path: str | Path) -> None:
        """Execute all steps from JSON file."""
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        log(self.name, f"Executing: {json_path.name}", level="info")

        with open(json_path, "r", encoding="utf-8") as f:
            steps = json.load(f)

        for i, step in enumerate(steps, 1):
            try:
                self._execute_step(step)
            except Exception as e:
                log(self.name, f"Error at step {i}: {e}", level="error")
                raise

    def _execute_step(self, step: Dict[str, Any]) -> None:
        """Execute a single step."""
        command = step.get("command", "").lower()
        target = self._replace(step.get("target", ""))
        value = self._replace(step.get("value", ""))

        log(self.name, f"→ {command}: {target}", level="debug")

        if command == "open":
            self.session.open(target)

        elif command == "click":
            self.session.click(target)

        elif command in ["type", "sendkeys"]:
            self.session.type_text(target, value)

        elif command == "pause":
            ms = int(value) if value else 1000
            self.session.pause(ms / 1000)

        elif command == "wait":
            seconds = int(value) if value else 1
            self.session.pause(float(seconds))

        else:
            log(self.name, f"Unknown command: {command}", level="warning")

    def _replace(self, text: str) -> str:
        """Replace ${KEY} with values from variables dict."""
        if not isinstance(text, str):
            return text

        if not text.startswith("${") or not text.endswith("}"):
            return text

        key = text[2:-1]
        if key not in self.variables:
            raise ValueError(f"Variable not found: {key}")

        return self.variables[key]
