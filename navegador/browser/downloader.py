import platform, subprocess, re, requests, zipfile, io
from pathlib import Path

from navegador.logging.logger import log


def _get_edge_version_windows() -> str:
    """Obtiene la versión COMPLETA de Microsoft Edge en Windows."""
    output = subprocess.check_output(
        [
            "reg",
            "query",
            r"HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon",
            "/v",
            "version",
        ],
        stderr=subprocess.DEVNULL,
        text=True,
    )

    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
    if not match:
        raise RuntimeError("No se pudo parsear versión de Edge (Windows)")

    return match.group(1)


def _get_edge_version_linux() -> str:
    """Obtiene la versión COMPLETA de Microsoft Edge en Linux."""
    output = subprocess.check_output(
        ["microsoft-edge", "--version"],
        text=True,
    )

    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
    if not match:
        raise RuntimeError("No se pudo parsear versión de Edge (Linux)")

    return match.group(1)


def _build_driver_url(version: str, system: str) -> str:
    if system == "Windows":
        return f"https://msedgedriver.microsoft.com/{version}/edgedriver_win64.zip"
    elif system == "Linux":
        return f"https://msedgedriver.microsoft.com/{version}/edgedriver_linux64.zip"
    else:
        raise RuntimeError("Sistema operativo no soportado")


def download_msedgedriver(dest_dir: Path, name: str) -> Path:
    """
    Descarga msedgedriver correspondiente EXACTAMENTE a la versión instalada de Edge.
    """
    system = platform.system()

    if system == "Windows":
        version = _get_edge_version_windows()
    elif system == "Linux":
        version = _get_edge_version_linux()
    else:
        raise RuntimeError("Sistema operativo no soportado")

    url = _build_driver_url(version, system)

    log(name, f"Descargando msedgedriver {version}", "INFO")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    dest_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(dest_dir)

    driver_name = "msedgedriver.exe" if system == "Windows" else "msedgedriver"
    driver_path = dest_dir / driver_name

    try:
        driver_path.chmod(0o755)
    except Exception:
        pass  # En Windows o FS restringidos puede fallar sin afectar

    log(name, f"Driver listo: {driver_path}", "OK")
    return driver_path