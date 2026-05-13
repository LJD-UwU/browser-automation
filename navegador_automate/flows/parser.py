"""JSON flow parser."""

from pathlib import Path
from typing import List, Dict, Any
from navegador_automate.utils.file_manager import FileManager
from navegador_automate.logger import log
from navegador_automate.browser.exceptions import InvalidFlowDefinitionError


class FlowParser:
    """Parse JSON flow files."""

    @staticmethod
    def load_steps(file_path: Path | str) -> List[Dict[str, Any]]:
        """
        Load steps from JSON file.

        Args:
            file_path: Path to JSON file.

        Returns:
            List of step dictionaries.

        Raises:
            InvalidFlowDefinitionError: If file is invalid.
        """
        file_path = Path(file_path)

        try:
            data = FileManager.read_json(file_path)

            if not isinstance(data, list):
                raise InvalidFlowDefinitionError(
                    f"Steps file must contain a list, got {type(data).__name__}"
                )

            log("FlowParser", f"Loaded {len(data)} steps from {file_path}", level="debug")
            return data

        except FileNotFoundError as e:
            raise InvalidFlowDefinitionError(f"File not found: {file_path}") from e
        except ValueError as e:
            raise InvalidFlowDefinitionError(f"Invalid JSON: {file_path} - {e}") from e

    @staticmethod
    def validate_step(step: Dict[str, Any]) -> bool:
        """
        Validate step structure.

        Args:
            step: Step dictionary.

        Returns:
            True if valid.

        Raises:
            InvalidFlowDefinitionError: If step is invalid.
        """
        required_fields = ["command", "target"]

        for field in required_fields:
            if field not in step:
                raise InvalidFlowDefinitionError(f"Step missing required field: {field}")

        command = step.get("command", "").lower()
        valid_commands = [
            "open",
            "click",
            "type",
            "pause",
            "wait",
            "key",
            "get_text",
            "get_attribute",
            "check_visible",
        ]

        if command not in valid_commands:
            raise InvalidFlowDefinitionError(f"Unknown command: {command}")

        return True

    @staticmethod
    def parse_selector(target: str) -> tuple:
        """
        Parse selector string.

        Args:
            target: Selector string (xpath=..., css=..., id=..., etc).

        Returns:
            Tuple of (selector_type, selector_value).
        """
        if not target:
            return None, None

        known_types = ["xpath", "css", "id", "name", "class", "tag"]

        for sel_type in known_types:
            prefix = f"{sel_type}="
            if target.startswith(prefix):
                selector_value = target[len(prefix) :]
                return sel_type, selector_value

        return "xpath", target

    @staticmethod
    def interpolate_value(value: str, credentials: Dict[str, Any]) -> str:
        """
        Interpolate ${VAR} placeholders with credentials.

        Args:
            value: Value with placeholders.
            credentials: Dictionary of credentials.

        Returns:
            Interpolated value.
        """
        if not isinstance(value, str) or not credentials:
            return value

        result = value
        for key, val in credentials.items():
            placeholder = f"${{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(val))
                log(
                    "FlowParser",
                    f"Interpolated {placeholder}",
                    level="debug",
                    secure=True,
                )

        return result
