"""
flows_config.py
===============
Define los flujos de automatización y el mapa de COMMANDS para FlowOrchestrator.

Las variables ${...} en los JSON de pasos se resuelven desde:
  1. steps_flows/config.py  →  dict CONFIG  (URLs y credenciales)
  2. credentials= pasado a FlowOrchestrator  (override en runtime)

Para configurar el proyecto edita  steps_flows/config.py.
"""

from pathlib import Path
from typing import Dict, Any

from navegador_automate.flows.orchestrator import FlowOrchestrator, _RunProxy

DATA_DIR = Path(__file__).parent / "data" / "json"

if not DATA_DIR.exists():
    raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")


# ── Definición de flujos ──────────────────────────────────────────────────────

FLOW_BASE_PLAN = {
    "name":             "basePlan",
    "login":            str(DATA_DIR / "mail.json"),
    "steps":            str(DATA_DIR / "basePlan.json"),
    "download_keyword": "ZJ",
}

FLOW_REAL_TIME = {
    "name":             "realTime",
    "login":            str(DATA_DIR / "mail.json"),
    "steps":            str(DATA_DIR / "realTimeProduction.json"),
    "download_keyword": "Real-time production report",
}

FLOW_PLM_BUSQUEDA = {
    "name":             "plmBusqueda",
    "login":            str(DATA_DIR / "mail.json"),
    "steps":            str(DATA_DIR / "plmBusqueda.json")
}

FLOW_LOSS_TIME = {
    "name":             "lossTime",
    "login":            str(DATA_DIR / "mail.json"),
    "steps":            str(DATA_DIR / "lossTime.json"),
    "download_keyword": "Production daily results report",
}


# ── Mapa de comandos ──────────────────────────────────────────────────────────

COMMANDS: Dict[str, Dict[str, Any]] = {
    "basePlan": {
        "flows":    [FLOW_BASE_PLAN],
        "parallel": False,
    },
    "realTime": {
        "flows":    [FLOW_REAL_TIME],
        "parallel": False,
    },
    "plmBusqueda": {
        "flows":    [FLOW_PLM_BUSQUEDA],
        "parallel": False,
    },
    "lossTime": {
        "flows":    [FLOW_LOSS_TIME],
        "parallel": False,
    },
    "all": {
        "flows":       [FLOW_BASE_PLAN, FLOW_REAL_TIME, FLOW_LOSS_TIME],
        "parallel":    True,
        "max_workers": 3,
    },
}


# ── RunProxy tipado ───────────────────────────────────────────────────────────
# Esta clase le dice al IDE exactamente qué métodos existen en orch.run
# Actualiza esta clase cuando agregues nuevos comandos a COMMANDS.

class RunProxy(_RunProxy):
    """
    Subclase tipada de _RunProxy con los comandos disponibles como métodos.

    El IDE muestra estos métodos en el autocompletado al escribir  orch.run.<TAB>
    Si agregas un nuevo flujo en COMMANDS, agrega el método correspondiente aquí.
    """

    def basePlan(self) -> Dict[str, Any]:
        """Descarga el reporte Base Plan (ZJ*.xlsx)."""
        return self._orchestrator.execute_command("basePlan")

    def realTime(self) -> Dict[str, Any]:
        """Descarga el reporte Real-Time Production."""
        return self._orchestrator.execute_command("realTime")

    def lossTime(self) -> Dict[str, Any]:
        """Descarga el reporte Loss Time (Production daily results)."""
        return self._orchestrator.execute_command("lossTime")

    def all(self) -> Dict[str, Any]:
        """Ejecuta basePlan + realTime + lossTime en paralelo."""
        return self._orchestrator.execute_command("all")


class TypedFlowOrchestrator(FlowOrchestrator):
    """
    FlowOrchestrator con  orch.run  tipado para autocompletado del IDE.

    Uso:
        from steps_flows.flows_config import TypedFlowOrchestrator, COMMANDS

        orch = TypedFlowOrchestrator(browser, commands=COMMANDS)
        result = orch.run.basePlan()   # ← el IDE muestra los métodos disponibles
    """

    run: RunProxy  # type: ignore[assignment]

    def __init__(self, browser_session, commands=None, credentials=None):
        super().__init__(browser_session, commands=commands, credentials=credentials)
        self.run = RunProxy(self)


__all__ = [
    "FLOW_BASE_PLAN",
    "FLOW_REAL_TIME",
    "FLOW_LOSS_TIME",
    "COMMANDS",
    "DATA_DIR",
    "RunProxy",
    "TypedFlowOrchestrator",
]
