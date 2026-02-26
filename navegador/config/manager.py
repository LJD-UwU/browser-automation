import json, os
from navegador.filesystem.file_utils import buscar_config_json


class ConfigManager:
    """Carga y expone configuración desde config.json."""

    def __init__(self):
        self.config_path = buscar_config_json()

    def load_config(self) -> dict:
        """Devuelve el diccionario completo de configuración."""
        if not os.path.isfile(self.config_path):
            return {}

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}