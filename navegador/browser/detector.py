from pathlib import Path
import platform

from navegador.browser.downloader import download_msedgedriver
from navegador.filesystem.paths import BASE_DIR
from navegador.logging.logger import log


class DriverDetector:
    """
    Verifica la existencia del msedgedriver y lo descarga si es necesario.
    """

    def __init__(self, name: str):
        self.name = name
        self.drivers_dir = BASE_DIR / "drivers"

    def get_driver_path(self) -> Path:
        driver_name = (
            "msedgedriver.exe"
            if platform.system() == "Windows"
            else "msedgedriver"
        )

        driver_path = self.drivers_dir / driver_name

        if driver_path.exists():
            log(self.name, f"Usando msedgedriver local: {driver_path}", "INFO")
            return driver_path

        log(self.name, "msedgedriver no encontrado, iniciando descarga", "INFO")
        return download_msedgedriver(self.drivers_dir, self.name)