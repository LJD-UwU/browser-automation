"""Driver manager: download and manage WebDriver binaries.

Drivers are stored in:
  1. A custom path provided via environment variable NAV_DRIVERS_DIR, OR
  2. The calling project's directory (detected via inspect.stack), OR
  3. A platform-specific user data directory as fallback.
"""

import inspect
import io
import os
import platform
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Optional

import requests

from navegador_automate.utils.logger import log


def _detect_project_dir() -> Path:
    """
    Walk the call stack to find the outermost caller that is NOT inside
    the navegador_automate package itself. That file's parent directory
    is treated as the 'project root'. Falls back to CWD.
    """
    lib_marker = "navegador_automate"
    for frame_info in reversed(inspect.stack()):
        filename = frame_info.filename
        if not filename or filename == "<string>":
            continue
        p = Path(filename).resolve()
        if lib_marker in str(p):
            continue
        if "site-packages" in str(p) or ("lib" + os.sep + "python") in str(p):
            continue
        return p.parent
    return Path.cwd()


def _get_drivers_dir() -> Path:
    """
    Return the directory where driver binaries should be stored.

    Priority:
    1. NAV_DRIVERS_DIR environment variable
    2. <project_root>/drivers
    3. Platform user data dir fallback
    """
    env_path = os.environ.get("NAV_DRIVERS_DIR")
    if env_path:
        p = Path(env_path)
        p.mkdir(parents=True, exist_ok=True)
        return p

    project_dir = _detect_project_dir()
    drivers_dir = project_dir / "drivers"
    try:
        drivers_dir.mkdir(parents=True, exist_ok=True)
        return drivers_dir
    except OSError:
        pass

    system = platform.system()
    if system == "Windows":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    fallback = base / "navegador-automate" / "drivers"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


class DriverManager:
    """
    Gestor de binarios de WebDriver con descarga y cacheo automático.

    Descarga los drivers necesarios (msedgedriver.exe, chromedriver, etc.)
    los valida y los cachea para evitar descargas repetidas.
    """

    def __init__(self, browser: str, drivers_dir: Optional[Path] = None) -> None:
        """
        Inicializar el gestor de WebDriver.

        Args:
            browser: Tipo de navegador ("edge", "chrome", "firefox")
            drivers_dir: Directorio para almacenar drivers.
                        Si None, usa detección automática.
        """
        self.browser = browser.lower()
        self.system = platform.system()
        self._drivers_dir = drivers_dir

    @property
    def drivers_dir(self) -> Path:
        """
        Obtener el directorio donde se almacenan o cachean binarios de WebDriver.

        Prioridad de resolución:
            1. Directorio configurado explícitamente via constructor
            2. Directorio raíz del proyecto detectado + '/drivers'
            3. Fallback a directorio de datos del usuario por plataforma:
               - Windows: %APPDATA%/navegador-automate/drivers
               - Linux: ~/.local/share/navegador-automate/drivers
               - macOS: ~/Library/Application Support/navegador-automate/drivers

        Returns:
            Path: Ruta del directorio para almacenar drivers

        Note:
            El directorio se crea automáticamente si no existe.

        Example:
            >>> manager = DriverManager("edge")
            >>> print(manager.drivers_dir)
            PosixPath('/home/user/proyecto/drivers')
        """
        if self._drivers_dir is not None:
            return self._drivers_dir
        return _get_drivers_dir()

    def get_driver_path(self) -> Path:
        """
        Obtener ruta al ejecutable del WebDriver.

        Descarga el driver si no está presente, valida su versión
        y retorna la ruta completa al ejecutable.

        Returns:
            Path: Ruta al ejecutable del WebDriver

        Raises:
            RuntimeError: Si no se puede descargar o validar el driver

        Example:
            >>> manager = DriverManager("chrome")
            >>> path = manager.get_driver_path()
            >>> print(path)
            PosixPath('/drivers/chromedriver')
        """
        if self.browser == "edge":
            return self._get_edge_driver()
        elif self.browser == "chrome":
            return self._get_chrome_driver()
        elif self.browser == "firefox":
            return self._get_firefox_driver()
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")

    # ── Edge ────────────────────────────────────────────────────────────────

    def _get_edge_driver(self) -> Path:
        dest_dir = self.drivers_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        driver_name = "msedgedriver.exe" if self.system == "Windows" else "msedgedriver"
        driver_path = dest_dir / driver_name

        if driver_path.exists():
            log("DriverManager", f"Found cached Edge driver: {driver_path}", level="info")
            return driver_path

        log("DriverManager", "Downloading MSEdgeDriver...", level="info")
        version = self._get_edge_version()
        return self._download_edge_driver(version, dest_dir)

    def _get_edge_version(self) -> str:
        try:
            if self.system == "Windows":
                output = subprocess.check_output(
                    ["reg", "query", r"HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon", "/v", "version"],
                    stderr=subprocess.DEVNULL, text=True,
                )
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
                if match:
                    return match.group(1)
            elif self.system == "Linux":
                output = subprocess.check_output(["microsoft-edge", "--version"], text=True)
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
                if match:
                    return match.group(1)
        except Exception as e:
            log("DriverManager", f"Could not detect Edge version: {e}", level="warning")

        raise RuntimeError(
            "Could not detect Edge version. Ensure Edge is installed or set NAV_DRIVERS_DIR "
            "and place msedgedriver manually."
        )

    def _download_edge_driver(self, version: str, dest_dir: Path) -> Path:
        if self.system == "Windows":
            url = f"https://msedgedriver.microsoft.com/{version}/edgedriver_win64.zip"
        elif self.system == "Linux":
            url = f"https://msedgedriver.microsoft.com/{version}/edgedriver_linux64.zip"
        else:
            raise RuntimeError(f"Unsupported OS: {self.system}")

        log("DriverManager", f"Downloading MSEdgeDriver {version} from {url}", level="info")
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(dest_dir)

        driver_name = "msedgedriver.exe" if self.system == "Windows" else "msedgedriver"
        driver_path = dest_dir / driver_name

        if not driver_path.exists():
            raise RuntimeError(f"MSEdgeDriver not found after extraction in {dest_dir}")

        driver_path.chmod(0o755)
        log("DriverManager", f"Downloaded MSEdgeDriver {version} to {driver_path}", level="info")
        return driver_path

    # ── Chrome ───────────────────────────────────────────────────────────────

    def _get_chrome_driver(self) -> Path:
        dest_dir = self.drivers_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        driver_name = "chromedriver.exe" if self.system == "Windows" else "chromedriver"
        driver_path = dest_dir / driver_name

        if driver_path.exists():
            log("DriverManager", f"Found cached Chrome driver: {driver_path}", level="info")
            return driver_path

        log("DriverManager", "Downloading ChromeDriver...", level="info")
        version = self._get_chrome_version()
        return self._download_chrome_driver(version, dest_dir)

    def _get_chrome_version(self) -> str:
        try:
            if self.system == "Windows":
                output = subprocess.check_output(
                    ["reg", "query", r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon", "/v", "version"],
                    stderr=subprocess.DEVNULL, text=True,
                )
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
                if match:
                    return match.group(1).rsplit(".", 1)[0]
            elif self.system == "Linux":
                output = subprocess.check_output(["google-chrome", "--version"], text=True)
                match = re.search(r"(\d+\.\d+\.\d+)", output)
                if match:
                    return match.group(1)
        except Exception as e:
            log("DriverManager", f"Could not detect Chrome version: {e}", level="warning")
        return "latest"

    def _download_chrome_driver(self, version: str, dest_dir: Path) -> Path:
        if self.system == "Windows":
            url = (f"https://googlechromelabs.github.io/chrome-for-testing/"
                   f"latest/chrome-for-testing/{version}/win64/chromedriver-{version}.zip")
        elif self.system == "Linux":
            url = (f"https://googlechromelabs.github.io/chrome-for-testing/"
                   f"latest/chrome-for-testing/{version}/linux64/chromedriver-{version}.zip")
        else:
            raise RuntimeError(f"Unsupported OS: {self.system}")

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(dest_dir)

        driver_name = "chromedriver.exe" if self.system == "Windows" else "chromedriver"
        driver_path = dest_dir / driver_name
        if not driver_path.exists():
            for found in dest_dir.rglob(driver_name):
                driver_path = found
                break

        driver_path.chmod(0o755)
        log("DriverManager", f"Downloaded ChromeDriver {version} to {driver_path}", level="info")
        return driver_path

    # ── Firefox ──────────────────────────────────────────────────────────────

    def _get_firefox_driver(self) -> Path:
        dest_dir = self.drivers_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        driver_name = "geckodriver.exe" if self.system == "Windows" else "geckodriver"
        driver_path = dest_dir / driver_name

        if driver_path.exists():
            log("DriverManager", f"Found cached Firefox driver: {driver_path}", level="info")
            return driver_path

        log("DriverManager", "Downloading GeckoDriver...", level="info")
        return self._download_firefox_driver(dest_dir)

    def _download_firefox_driver(self, dest_dir: Path) -> Path:
        GECKO_VERSION = "0.35.0"

        if self.system == "Windows":
            url = f"https://github.com/mozilla/geckodriver/releases/download/v{GECKO_VERSION}/geckodriver-v{GECKO_VERSION}-win64.zip"
            is_zip = True
        elif self.system == "Linux":
            url = f"https://github.com/mozilla/geckodriver/releases/download/v{GECKO_VERSION}/geckodriver-v{GECKO_VERSION}-linux64.tar.gz"
            is_zip = False
        elif self.system == "Darwin":
            url = f"https://github.com/mozilla/geckodriver/releases/download/v{GECKO_VERSION}/geckodriver-v{GECKO_VERSION}-macos.tar.gz"
            is_zip = False
        else:
            raise RuntimeError(f"Unsupported OS: {self.system}")

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        if is_zip:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(dest_dir)
        else:
            import tarfile
            with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as t:
                t.extractall(dest_dir)

        driver_name = "geckodriver.exe" if self.system == "Windows" else "geckodriver"
        driver_path = dest_dir / driver_name

        if not driver_path.exists():
            raise RuntimeError(f"GeckoDriver not found after extraction in {dest_dir}")

        driver_path.chmod(0o755)
        log("DriverManager", f"Downloaded GeckoDriver v{GECKO_VERSION} to {driver_path}", level="info")
        return driver_path
