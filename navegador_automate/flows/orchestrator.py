"""Flow orchestrator: execute flows using command definitions."""

from typing import Dict, Any, Optional, Callable
from pathlib import Path

from navegador_automate.flows.executor import Executor
from navegador_automate.utils.logger import log


class _RunProxy:
    """
    Proxy que expone cada comando de COMMANDS como un método callable.

    Implementa __dir__ para que IDEs como VS Code y PyCharm muestren
    los comandos disponibles en el autocompletado al escribir orch.run.<TAB>.
    """

    def __init__(self, orchestrator: "FlowOrchestrator"):
        self._orchestrator = orchestrator

    def __dir__(self):
        """Expone los comandos disponibles al autocompletado del IDE."""
        base = list(super().__dir__())
        return base + list(self._orchestrator.commands.keys())

    def __getattr__(self, name: str) -> Callable:
        if name.startswith("_"):
            raise AttributeError(name)
        if name in self._orchestrator.commands:
            def _run() -> Dict[str, Any]:
                return self._orchestrator.execute_command(name)
            _run.__name__ = name
            _run.__doc__ = (
                f"Ejecuta el comando '{name}'.\n"
                f"Flujos: {[f['name'] for f in self._orchestrator.commands[name].get('flows', [])]}"
            )
            return _run
        raise AttributeError(
            f"Comando '{name}' no encontrado. "
            f"Disponibles: {list(self._orchestrator.commands.keys())}"
        )

    def __repr__(self) -> str:
        cmds = list(self._orchestrator.commands.keys())
        return f"<RunProxy commands={cmds}>"


class FlowOrchestrator:
    """Orchestrate flow execution."""

    def __init__(
        self,
        browser_session,
        commands: Optional[Dict[str, Dict[str, Any]]] = None,
        credentials: Optional[Dict[str, str]] = None,
    ):
        """
        Args:
            browser_session: BrowserSession instance.
            commands: Dict de comandos (importar COMMANDS desde flows_config).
            credentials: Variables ${KEY} adicionales — tienen prioridad sobre config.json.
        """
        self.session = browser_session
        self.commands = commands or {}
        self.credentials = credentials or {}
        self.run = _RunProxy(self)

    def execute_command(self, command_name: str) -> Dict[str, Any]:
        """Ejecuta un comando por nombre."""
        if command_name not in self.commands:
            available = list(self.commands.keys())
            raise ValueError(f"Comando '{command_name}' no encontrado. Disponibles: {available}")

        command_config = self.commands[command_name]
        flows = command_config.get("flows", [])

        log("FlowOrchestrator", f"Executing command: {command_name}", level="info")

        results = []
        for flow in flows:
            try:
                result = self._execute_flow(flow)
                results.append(result)
            except Exception as e:
                log("FlowOrchestrator", f"Flow {flow.get('name')} failed: {e}", level="error")
                results.append({"success": False, "error": str(e)})

        return {
            "command": command_name,
            "success": all(r.get("success", False) for r in results),
            "results": results,
        }

    def _execute_flow(self, flow: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un flujo individual."""
        name = flow.get("name")
        login_file = flow.get("login")
        steps_file = flow.get("steps")

        log("FlowOrchestrator", f"→ Flow: {name}", level="info")

        try:
            executor = Executor(self.session, name, self.credentials)

            if login_file:
                executor.execute_file(login_file)

            executor.execute_file(steps_file)

            log("FlowOrchestrator", f"✓ Flow {name} completed", level="info")
            return {"success": True, "flow_name": name}

        except Exception as e:
            log("FlowOrchestrator", f"✗ Flow {name} failed: {e}", level="error")
            return {"success": False, "flow_name": name, "error": str(e)}
