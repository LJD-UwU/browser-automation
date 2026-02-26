from pathlib import Path


class ChangeDetector:
    """Detecta cambios en un valor específico extraído del DOM."""

    def __init__(self, path: str):
        self.file_path = Path(path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def has_changed(self, new_value: str) -> bool:
        """Retorna True si el valor cambió respecto al almacenado."""
        if not self.file_path.exists():
            self.file_path.write_text(new_value, encoding="utf-8")
            return True

        old_value = self.file_path.read_text(encoding="utf-8")

        if old_value.strip() != new_value.strip():
            self.file_path.write_text(new_value, encoding="utf-8")
            return True

        return False