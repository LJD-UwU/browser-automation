import shutil
import time
import re
from pathlib import Path

from navegador.logging.logger import log
from navegador.filesystem.paths import DOWNLOAD_DIR, TEMP_DIR


def _extraer_numero(nombre: str) -> int:
    """
    Extrae el número final (N) de 'archivo (N).xlsx'.
    Si no hay número, devuelve 0.
    """
    match = re.search(r"\((\d+)\)", nombre)
    return int(match.group(1)) if match else 0


def esperar_descarga(
    keyword: str,
    timeout: int = 120,
    estabilidad: int = 3,
    perfil: str = ""
) -> Path:
    """
    Espera a que se complete la descarga más reciente que contenga `keyword`.
    Si hay múltiples archivos, toma el de mayor número (N) y fecha.
    """
    inicio = time.time()
    ultimo_tamano = -1
    estable_count = 0

    log(perfil, f"Esperando descarga con keyword: '{keyword}'", "INFO")

    while time.time() - inicio < timeout:
        candidatos = [
            f for f in DOWNLOAD_DIR.iterdir()
            if (
                keyword in f.name
                and f.is_file()
                and not f.name.endswith(".crdownload")
                and not f.name.startswith("~$")
            )
        ]

        if candidatos:
            archivo = max(
                candidatos,
                key=lambda f: (_extraer_numero(f.name), f.stat().st_mtime)
            )

            tam = archivo.stat().st_size

            if tam == ultimo_tamano and tam > 0:
                estable_count += 1
                if estable_count >= estabilidad:
                    log(
                        perfil,
                        f"Descarga completa detectada: {archivo.name}",
                        "OK"
                    )
                    return archivo
            else:
                ultimo_tamano = tam
                estable_count = 0

        time.sleep(0.5)

    raise TimeoutError(
        f"No se completó la descarga con keyword '{keyword}'"
    )


def copiar_a_temp(
    keyword: str,
    timeout: int = 120,
    perfil: str = "",
    origen: Path | None = None
) -> Path:
    """
    Obtiene un archivo (por descarga o ruta externa) y lo lleva a TEMP_DIR.

    - Si proviene de DOWNLOAD_DIR → se mueve
    - Si proviene de otra ruta → se copia
    """

    if origen:
        archivo_origen = origen
    else:
        archivo_origen = esperar_descarga(
            keyword=keyword,
            timeout=timeout,
            perfil=perfil
        )

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    destino = TEMP_DIR / archivo_origen.name

    if destino.exists():
        destino.unlink()

    try:
        if DOWNLOAD_DIR.resolve() in archivo_origen.resolve().parents:
            shutil.move(str(archivo_origen), destino)
            accion = "movido"
        else:
            shutil.copy2(str(archivo_origen), destino)
            accion = "copiado"

        log(perfil, f"Archivo {accion} a temp: {destino}", "OK")
        return destino

    except Exception as e:
        log(perfil, f"Error al llevar archivo a temp: {e}", "ERROR")
        raise
