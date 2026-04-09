from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from navegador.state.change_detector import ChangeDetector
from navegador.filesystem.paths import BASE_DIR
from navegador.filesystem.file_utils import copiar_a_temp
from navegador.logging.logger import log
from navegador.browser.executor import Executor
from navegador.browser.browser import Browser


def extract_value(driver, selector: str, timeout: int = 15) -> str:
    """Extrae texto desde un selector soportado."""
    if selector.startswith("xpath="):
        by = By.XPATH
        value = selector[6:]
    elif selector.startswith("css="):
        by = By.CSS_SELECTOR
        value = selector[4:]
    else:
        by = By.XPATH
        value = selector

    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )
    return element.text.strip()


def run_flow(flow: dict):
    """Orquesta ejecución completa según reglas declarativas del flow."""

    name = flow["name"]

    # Si hay descarga, NO usar headless
    headless = not bool(flow.get("download_keyword"))

    browser = Browser(name=name, headless=headless)
    driver = browser.start()
    executor = Executor(driver, name)

    try:
        # Login
        if flow.get("login"):
            executor.execute_file(BASE_DIR / flow["login"])

        # Steps principales
        executor.execute_file(BASE_DIR / flow["steps"])

        # CASO 1: flujo simple
        if not flow.get("detect_change", False):
            if flow.get("download_keyword"):
                log(name, "Esperando y copiando descarga (flujo simple)...")
                copiar_a_temp(
                    keyword=flow["download_keyword"],
                    perfil=name
                )
            return

        # CASO 2: flujo con detección de cambio
        selector = flow["change_selector"]
        value = extract_value(driver, selector)

        detector = ChangeDetector(flow["path_cambio"])
        changed = detector.has_changed(value)

        if changed:
            log(name, f"Cambio detectado en selector: {value}")

            if flow.get("download_keyword"):
                copiar_a_temp(
                    keyword=flow["download_keyword"],
                    perfil=name
                )
        else:
            log(name, "No se detectaron cambios, se omite descarga")

    except Exception as e:
        log(name, f"Error en flujo: {e}", "ERROR")

    finally:
        browser.quit()


flows = [
    {
        "name": "Example Flow",
        "login": None,
        "steps": "flows/example.json",
        "download_keyword": "report",
        "detect_change": False,
    },
    {
        "name": "Himex Mail",
        "login": "flows/himex_mail_login.json",
        "steps": "flows/himex_mail_download.json",
        "download_keyword": "attachment",
        "detect_change": False,
    },
]


if __name__ == "__main__":
    for flow in flows:
        run_flow(flow)
