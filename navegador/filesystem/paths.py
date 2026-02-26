from pathlib import Path
import platform
import tempfile

SYSTEM = platform.system()

# Raíz del proyecto (navegador/)
BASE_DIR = Path(__file__).resolve().parents[2]

# Descargas del navegador
DOWNLOAD_DIR = Path.home() / "Downloads"

# Temp interno del sistema
TEMP_DIR = Path(tempfile.gettempdir()) / "uppph_daily_temp"

# Estado (hashes, txt, etc.)
STATE_DIR = BASE_DIR / "state"


def default_profiles_dir() -> Path:
    """Devuelve la ruta base de perfiles según el sistema operativo."""
    if SYSTEM == "Windows":
        return Path("C:/profiles")
    return Path.home() / "profiles"


PROFILES_DIR = default_profiles_dir()


def ensure_directories():
    """Crea todas las carpetas necesarias."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


# Crear carpetas al importar el módulo
ensure_directories()