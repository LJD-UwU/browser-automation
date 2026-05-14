"""Flow executor: execute JSON-defined automation steps.

Variables ${KEY} en los pasos JSON se resuelven desde:
  1. El dict `variables` pasado al constructor (credenciales de FlowOrchestrator)
  2. config.json en la raíz del proyecto que llama a la librería

config.json tiene prioridad MENOR que las credenciales pasadas directamente,
permitiendo override en tiempo de ejecución sin tocar el archivo.
"""

import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from navegador_automate.utils.logger import log


# ── Resolución de config.json ─────────────────────────────────────────────────

def _find_config_json() -> Optional[Path]:
    """
    Busca config.json en varias ubicaciones conocidas, en orden de prioridad:
      1. steps_flows/data/json/config.json  (ubicación preferida)
      2. config.json en la raíz del proyecto
      3. backend/config/config.json  (compatibilidad con Ejemplo)
    """
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        # 1. Ubicación preferida: steps_flows/data/json/config.json
        candidate = parent / "steps_flows" / "data" / "json" / "config.json"
        if candidate.exists():
            return candidate
        # 2. Raíz del proyecto
        candidate = parent / "config.json"
        if candidate.exists():
            return candidate
        # 3. Compatibilidad con estructura del Ejemplo
        candidate = parent / "backend" / "config" / "config.json"
        if candidate.exists():
            return candidate
    return None


def _load_config_json() -> Dict[str, str]:
    """Carga config.json y devuelve su contenido como dict (vacío si no existe)."""
    path = _find_config_json()
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


# ── Utilidades de calendario / dropdown (portadas del Ejemplo) ────────────────

def _previous_working_day(reference: datetime = None) -> datetime:
    """Devuelve el día hábil inmediatamente anterior a reference (o hoy)."""
    if reference is None:
        reference = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    candidate = reference - timedelta(days=1)
    while candidate.weekday() in (5, 6):   # sábado=5, domingo=6
        candidate -= timedelta(days=1)
    return candidate


_OPTION_PATTERN = re.compile(r"^ZJ(\d{2})(\d{2})(\d{2})(\d{2})-\d+$")


def _parse_option(text: str):
    m = _OPTION_PATTERN.match(text.strip())
    if not m:
        return None
    yy, mm, dd, vv = m.groups()
    try:
        return datetime(2000 + int(yy), int(mm), int(dd)), int(vv)
    except ValueError:
        return None


def _resolve_best_option(options: list, reference: datetime = None) -> str:
    """Selecciona la opción más reciente anterior a reference del dropdown."""
    if reference is None:
        reference = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    parsed = []
    for opt in options:
        result = _parse_option(opt)
        if result:
            fecha, version = result
            parsed.append((fecha, version, opt))
    if not parsed:
        raise Exception(
            f"Ninguna opción tiene el formato ZJ{{AA}}{{MM}}{{DD}}{{VV}}-{{sufijo}}. "
            f"Muestra: {options[:5]}"
        )
    parsed.sort(key=lambda x: (x[0], x[1]), reverse=True)
    for fecha, version, texto in parsed:
        if fecha < reference:
            return texto
    return parsed[0][2]


# ── Executor ──────────────────────────────────────────────────────────────────

class Executor:
    """Execute automation steps from JSON files."""

    def __init__(self, browser_session, name: str, variables: Dict[str, str] = None):
        """
        Args:
            browser_session: BrowserSession instance
            name: Nombre del flujo (para logs)
            variables: Variables ${KEY} — se combinan con config.json.
                       Las variables aquí pasadas tienen prioridad sobre config.json.
        """
        self.session = browser_session
        self.name = name
        self.timeout = 15

        # Combinar config.json (base) + variables explícitas (override)
        config = _load_config_json()
        self.variables = {**config, **(variables or {})}

        if config:
            log(self.name, f"Config cargado desde config.json ({len(config)} variables)", level="debug")

    # ── Ejecución de archivos ─────────────────────────────────────────────────

    def execute_file(self, json_path) -> None:
        """Execute all steps from JSON file."""
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        log(self.name, f"Executing: {json_path.name}", level="info")

        with open(json_path, "r", encoding="utf-8") as f:
            steps = json.load(f)

        for i, step in enumerate(steps, 1):
            try:
                self._execute_step(step)
            except Exception as e:
                log(self.name, f"Error at step {i}: {e}", level="error")
                raise

    # ── Dispatch de comandos ──────────────────────────────────────────────────

    def _execute_step(self, step: Dict[str, Any]) -> None:
        """Dispatch y ejecuta un paso individual."""
        command = step.get("command", "").lower()
        target_raw = step.get("target", "")
        value_raw  = step.get("value", "")

        # Solo reemplazar variables en value; target puede contener max_scan= sin ${}
        target = self._replace(target_raw) if self._is_variable(target_raw) else target_raw
        value  = self._replace(value_raw)

        log(self.name, f"→ {command}: {target}", level="debug")

        if command == "open":
            self.session.open(target)

        elif command == "click":
            self.session.click(target)

        elif command in ["type", "sendkeys"]:
            special = {
                "KEY_ENTER":  Keys.ENTER,
                "KEY_TAB":    Keys.TAB,
                "KEY_ESCAPE": Keys.ESCAPE,
                "KEY_SPACE":  Keys.SPACE,
            }
            self.session.type_text(target, special.get(value, value))

        elif command == "pause":
            ms = int(value) if value else 1000
            self.session.pause(ms / 1000)

        elif command == "wait":
            # wait puede ser milisegundos (value) o esperar elemento (target)
            if value and value.isdigit():
                self.session.pause(int(value) / 1000)
            else:
                log(self.name, f"wait: ignorando selector '{target}' (no implementado)", level="debug")
                self.session.pause(1)

        elif command == "select_date":
            # target = selector del popup, value = "YYYY-MM-DD" o "${AUTO}"
            resolved_value = self._replace(value_raw)
            if resolved_value == "__AUTO__":
                self.select_arco_date(target, "__AUTO__")
            else:
                self.select_arco_date(target, resolved_value)

        elif command == "select_option":
            # value = texto exacto o "${AUTO}"
            # target puede tener "max_scan=N" para auto
            resolved_value = self._replace(value_raw)
            if resolved_value == "__AUTO__":
                max_scan = 50
                if target_raw.startswith("max_scan="):
                    try:
                        max_scan = int(target_raw.split("=")[1])
                    except (ValueError, IndexError):
                        pass
                self.select_ant_option_auto(max_scan=max_scan)
            else:
                self.select_ant_option(option_text=resolved_value)

        else:
            log(self.name, f"Unknown command: {command}", level="warning")

        time.sleep(0.5)

    # ── Calendario Arco ───────────────────────────────────────────────────────

    def _get_arco_popup(self, selector: str):
        by, value = self._parse_selector(selector)
        wait = WebDriverWait(self.session.driver, self.timeout)
        popups = wait.until(EC.presence_of_all_elements_located((by, value)))
        popup = next((p for p in popups if p.is_displayed()), None)
        if not popup:
            raise Exception("No se encontró popup visible del calendario Arco")
        return popup

    def _navigate_arco_to_month(self, popup, target_date: datetime):
        for _ in range(24):
            labels = popup.find_elements(By.CSS_SELECTOR, ".arco-picker-header-label")
            year, month = int(labels[0].text), int(labels[1].text)
            if year == target_date.year and month == target_date.month:
                break
            arrow = (
                ".arco-icon-right"
                if (year, month) < (target_date.year, target_date.month)
                else ".arco-icon-left"
            )
            popup.find_element(By.CSS_SELECTOR, arrow).click()
            time.sleep(0.3)

    def _click_arco_day(self, popup, target_date: datetime):
        for cell in popup.find_elements(By.CSS_SELECTOR, ".arco-picker-cell-in-view"):
            day_text = cell.find_element(By.CSS_SELECTOR, ".arco-picker-date-value").text
            if day_text == str(target_date.day):
                self.session.driver.execute_script(
                    "arguments[0].click();",
                    cell.find_element(By.CSS_SELECTOR, ".arco-picker-date")
                )
                return
        raise Exception(f"No se encontró el día {target_date.day} en el calendario Arco")

    def select_arco_date(self, selector: str, date_input: str):
        """Selecciona fecha en calendario Arco. date_input = 'YYYY-MM-DD' o '__AUTO__'."""
        if date_input == "__AUTO__":
            target_date = _previous_working_day()
            log(self.name, f"AUTO calendario → {target_date.strftime('%Y-%m-%d')}")
        else:
            target_date = datetime.strptime(date_input, "%Y-%m-%d")

        popup = self._get_arco_popup(selector)
        self._navigate_arco_to_month(popup, target_date)
        self._click_arco_day(popup, target_date)
        log(self.name, f"Fecha seleccionada: {target_date.strftime('%Y-%m-%d')}")

    # ── Dropdown Ant Design ───────────────────────────────────────────────────

    def _get_ant_menu(self):
        wait = WebDriverWait(self.session.driver, self.timeout)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ant-select-dropdown-menu")))
        menus = self.session.driver.find_elements(By.CSS_SELECTOR, "ul.ant-select-dropdown-menu")
        for menu in menus:
            try:
                parent = menu.find_element(By.XPATH, "ancestor::div[contains(@class,'ant-select-dropdown')]")
                if "display: none" in (parent.get_attribute("style") or ""):
                    continue
            except Exception:
                pass
            if menu.is_displayed():
                return menu
        return menus[0] if menus else None

    def _click_option_el(self, el):
        self.session.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        time.sleep(0.3)
        try:
            el.click()
        except Exception:
            self.session.driver.execute_script("arguments[0].click();", el)

    def select_ant_option(self, option_text: str):
        """Selecciona opción del dropdown Ant Design por texto exacto."""
        log(self.name, f"Seleccionando opción: '{option_text}'")
        menu = self._get_ant_menu()
        if menu is None:
            raise Exception("No se encontró ant-select-dropdown-menu")
        try:
            xpath = (f".//li[contains(@class,'ant-select-dropdown-menu-item') "
                     f"and normalize-space(text())='{option_text}']")
            el = menu.find_element(By.XPATH, xpath)
        except Exception:
            items = menu.find_elements(By.CSS_SELECTOR, "li.ant-select-dropdown-menu-item")
            el = next((i for i in items if i.text.strip() == option_text), None)
            if el is None:
                sample = [i.text.strip() for i in items[:10]]
                raise Exception(f"Opción '{option_text}' no encontrada. Disponibles: {sample}")
        self._click_option_el(el)

    def select_ant_option_auto(self, max_scan: int = 50):
        """Selecciona la opción más reciente (anterior a hoy) del dropdown Ant Design."""
        log(self.name, f"Resolviendo opción automáticamente (max_scan={max_scan})…")
        menu = self._get_ant_menu()
        if menu is None:
            raise Exception("No se encontró ant-select-dropdown-menu")
        xpath = (f"(//ul[contains(@class,'ant-select-dropdown-menu')]"
                 f"//li[contains(@class,'ant-select-dropdown-menu-item')])"
                 f"[position() <= {max_scan}]")
        items = self.session.driver.find_elements(By.XPATH, xpath)
        if not items:
            items = menu.find_elements(By.CSS_SELECTOR, "li.ant-select-dropdown-menu-item")[:max_scan]
        all_texts = [i.text.strip() for i in items if i.text.strip()]
        best = _resolve_best_option(all_texts)
        el = next((i for i in items if i.text.strip() == best), None)
        if el is None:
            raise Exception(f"Elemento <li> no encontrado para '{best}'")
        self._click_option_el(el)
        log(self.name, f"Opción auto-seleccionada: '{best}'")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _is_variable(self, text: str) -> bool:
        return isinstance(text, str) and text.startswith("${") and text.endswith("}")

    def _replace(self, text: str) -> str:
        """Reemplaza ${KEY} con valores del dict de variables.

        - ${AUTO} → "__AUTO__" (token interno para fecha automática)
        - ${KEY}  → valor de self.variables[KEY]
        """
        if not isinstance(text, str):
            return text
        if not text.startswith("${") or not text.endswith("}"):
            return text
        key = text[2:-1]
        if key == "AUTO":
            return "__AUTO__"
        if key not in self.variables:
            raise ValueError(
                f"Variable '${{{key}}}' no encontrada. "
                f"Agrégala a config.json o pásala en credentials al FlowOrchestrator."
            )
        return self.variables[key]

    def _parse_selector(self, selector: str):
        if selector.startswith("xpath="):
            return By.XPATH, selector[6:]
        if selector.startswith("css="):
            return By.CSS_SELECTOR, selector[4:]
        if selector.startswith("id="):
            return By.ID, selector[3:]
        if selector.startswith("name="):
            return By.NAME, selector[5:]
        if selector.startswith("//"):
            return By.XPATH, selector
        return By.XPATH, selector
