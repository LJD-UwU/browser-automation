"""Flow definition dataclass."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class FlowDefinition:
    """Define a reusable browser automation flow.

    Attributes:
        name: Flow name (e.g., "basePlan").
        login: Path to JSON file with login steps.
        steps: Path to JSON file with main steps.
        download_keyword: Keyword to identify downloaded files.
        detect_change: Whether to detect page changes.
        change_selector: Selector to monitor for changes.
        path_cambio: Path to save change detection results.
    """

    name: str
    login: str
    steps: str
    download_keyword: Optional[str] = None
    detect_change: bool = False
    change_selector: Optional[str] = None
    path_cambio: Optional[str] = None

    def __post_init__(self):
        """Validate flow definition."""
        if not self.name:
            raise ValueError("Flow name cannot be empty")
        if not self.login:
            raise ValueError("Login path cannot be empty")
        if not self.steps:
            raise ValueError("Steps path cannot be empty")

        login_path = Path(self.login)
        steps_path = Path(self.steps)

        if not login_path.exists():
            raise FileNotFoundError(f"Login file not found: {self.login}")
        if not steps_path.exists():
            raise FileNotFoundError(f"Steps file not found: {self.steps}")

        if self.detect_change and not self.change_selector:
            raise ValueError("change_selector required when detect_change=True")

    def __repr__(self) -> str:
        """Return flow representation."""
        return f"FlowDefinition(name='{self.name}', login='{self.login}', steps='{self.steps}')"
