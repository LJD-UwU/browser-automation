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

        login_path = self._resolve_path(self.login)
        steps_path = self._resolve_path(self.steps)

        if not login_path.exists():
            raise FileNotFoundError(f"Login file not found: {self.login}")
        if not steps_path.exists():
            raise FileNotFoundError(f"Steps file not found: {self.steps}")

        if self.detect_change and not self.change_selector:
            raise ValueError("change_selector required when detect_change=True")

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve file path, checking relative and package-relative paths."""
        path = Path(file_path)

        if path.is_absolute() or path.exists():
            return path

        try:
            import steps_flows
            steps_flows_dir = Path(steps_flows.__file__).parent

            if file_path.startswith("steps_flows/"):
                relative_path = file_path[len("steps_flows/"):]
                package_path = steps_flows_dir / relative_path
            else:
                package_path = steps_flows_dir / file_path

            if package_path.exists():
                return package_path
        except (ImportError, AttributeError):
            pass

        return path

    def __repr__(self) -> str:
        """Return flow representation."""
        return f"FlowDefinition(name='{self.name}', login='{self.login}', steps='{self.steps}')"
