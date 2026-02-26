import json
import time
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from navegador.logging.logger import log
from navegador.config.manager import ConfigManager


class Executor:
    """Ejecutor universal de pasos definidos en archivos JSON."""

    def __init__(self, driver, name: str, timeout: int = 15):
        self.driver = driver
        self.name = name
        self.timeout = timeout
        self.variables = ConfigManager().load_config()

    def _replace(self, value):
        """Reemplaza variables tipo ${KEY} usando config.json."""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            key = value[2:-1]
            if key not in self.variables or not self.variables[key]:
                raise ValueError(f"Variable no definida o vacía: {key}")
            return self.variables[key]
        return value

    def _parse_selector(self, selector: str):
        """Interpreta selectores soportados."""
        if selector.startswith("xpath="):
            return By.XPATH, selector[6:]
        if selector.startswith("css="):
            return By.CSS_SELECTOR, selector[4:]
        if selector.startswith("id="):
            return By.ID, selector[3:]
        if selector.startswith("name="):
            return By.NAME, selector[5:]
        if selector.startswith("//") or selector.startswith("(/"):
            return By.XPATH, selector

        log(self.name, f"Selector no reconocido: {selector}", "WARNING")
        return By.XPATH, selector

    def execute_file(self, json_path: str):
        """Ejecuta todos los pasos definidos en un archivo JSON."""
        log(self.name, f"Ejecutando JSON: {os.path.basename(json_path)}")

        with open(json_path, "r", encoding="utf-8") as f:
            steps = json.load(f)

        for step in steps:
            self._execute_step(step)

    def _ensure_active_window(self):
        """Asegura que exista y se use la última ventana."""
        if not self.driver.window_handles:
            raise RuntimeError("No hay ventanas de navegador activas")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def _execute_step(self, step: dict):
        """Ejecuta un solo paso."""
        command = step.get("command")
        target = self._replace(step.get("target", ""))
        value = self._replace(step.get("value", ""))

        try:
            self._ensure_active_window()

            by = selector = None
            wait = WebDriverWait(self.driver, self.timeout)

            # PRE-WAIT unificado
            if command in ["click", "type", "sendKeys"]:
                by, selector = self._parse_selector(target)
                log(self.name, f"Esperando elemento: {target}", "INFO")
                wait.until(EC.presence_of_element_located((by, selector)))
                wait.until(EC.element_to_be_clickable((by, selector)))

            if command == "open":
                self.driver.get(target)
                log(self.name, f"Abrir: {target}")

            elif command == "pause":
                ms = int(value) if value else 1000
                time.sleep(ms / 1000)

            elif command == "click":
                element = self.driver.find_element(by, selector)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    element
                )
                time.sleep(0.3)
                try:
                    element.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", element)

                log(self.name, f"Click en: {target}")

            elif command in ["type", "sendKeys"]:
                element = self.driver.find_element(by, selector)

                # Forzar foco real
                self.driver.execute_script("arguments[0].click();", element)
                element.clear()

                teclas = {
                    "KEY_ENTER": Keys.ENTER,
                    "KEY_TAB": Keys.TAB,
                    "KEY_ESCAPE": Keys.ESCAPE,
                    "KEY_SPACE": Keys.SPACE,
                    "KEY_BACKSPACE": Keys.BACKSPACE,
                    "KEY_DELETE": Keys.DELETE,
                    "KEY_UP": Keys.ARROW_UP,
                    "KEY_DOWN": Keys.ARROW_DOWN,
                    "KEY_LEFT": Keys.ARROW_LEFT,
                    "KEY_RIGHT": Keys.ARROW_RIGHT,
                }

                if value in teclas:
                    element.send_keys(teclas[value])
                else:
                    element.send_keys(value)

                log(self.name, f"Escribiendo en: {target}")

            else:
                log(self.name, f"Comando desconocido: {command}", "WARNING")

            # Pausa humana ligera
            time.sleep(0.8)

        except Exception as e:
            log(
                self.name,
                f"[STEP FAILED] command={command} | target={target} | value={value} | error={type(e).__name__}: {e}",
                "ERROR",
            )
            raise