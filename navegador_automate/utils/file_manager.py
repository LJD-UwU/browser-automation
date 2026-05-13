"""File management utilities for navegador-automate."""

import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from navegador_automate.logger import log


class FileManager:
    """Utility class for file operations."""

    @staticmethod
    def read_json(file_path: Path | str) -> Dict[str, Any] | List[Dict[str, Any]]:
        """
        Read JSON file.

        Args:
            file_path: Path to JSON file.

        Returns:
            Parsed JSON data.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If JSON is invalid.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            log("FileManager", f"File not found: {file_path}", level="error")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            log("FileManager", f"Invalid JSON: {file_path} - {e}", level="error")
            raise

    @staticmethod
    def write_json(file_path: Path | str, data: Dict[str, Any] | List[Any]) -> None:
        """
        Write JSON file.

        Args:
            file_path: Path to output JSON file.
            data: Data to write.
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        log("FileManager", f"JSON written: {file_path}", level="debug")

    @staticmethod
    def read_file(file_path: Path | str, encoding: str = "utf-8") -> str:
        """
        Read text file.

        Args:
            file_path: Path to file.
            encoding: File encoding (default: utf-8).

        Returns:
            File content.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def write_file(file_path: Path | str, content: str, encoding: str = "utf-8") -> None:
        """
        Write text file.

        Args:
            file_path: Path to output file.
            content: Content to write.
            encoding: File encoding (default: utf-8).
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)

    @staticmethod
    def find_files(directory: Path | str, pattern: str = "*") -> List[Path]:
        """
        Find files in directory matching pattern.

        Args:
            directory: Directory path.
            pattern: Glob pattern (default: "*").

        Returns:
            List of matching file paths.
        """
        directory = Path(directory)
        return list(directory.glob(pattern))

    @staticmethod
    def extract_zip(zip_path: Path | str, extract_to: Path | str) -> None:
        """
        Extract ZIP file.

        Args:
            zip_path: Path to ZIP file.
            extract_to: Directory to extract to.
        """
        zip_path = Path(zip_path)
        extract_to = Path(extract_to)

        extract_to.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_to)

        log("FileManager", f"ZIP extracted: {zip_path}", level="debug")

    @staticmethod
    def delete_file(file_path: Path | str, ignore_missing: bool = False) -> None:
        """
        Delete file.

        Args:
            file_path: Path to file.
            ignore_missing: If True, don't raise error if file missing.
        """
        file_path = Path(file_path)

        try:
            file_path.unlink()
            log("FileManager", f"File deleted: {file_path}", level="debug")
        except FileNotFoundError:
            if not ignore_missing:
                raise

    @staticmethod
    def file_exists(file_path: Path | str) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()

    @staticmethod
    def get_file_size(file_path: Path | str) -> int:
        """Get file size in bytes."""
        return Path(file_path).stat().st_size
