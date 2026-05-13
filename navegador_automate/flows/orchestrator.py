"""Flow orchestrator: execute flows using command definitions."""

from typing import Dict, Any, Optional
from pathlib import Path

from navegador_automate.flows.executor import Executor
from navegador_automate.utils.logger import log


class _RunProxy:
    """Proxy for dynamic run.commandName() syntax."""

    def __init__(self, orchestrator: "FlowOrchestrator"):
        self.orchestrator = orchestrator

    def __getattr__(self, name: str):
        """Allow orch.run.basePlan() syntax."""
        if name in self.orchestrator.commands:
            return lambda: self.orchestrator.execute_command(name)
        raise AttributeError(f"Command not found: {name}")


class FlowOrchestrator:
    """Orchestrate flow execution."""

    def __init__(
        self,
        browser_session,
        commands: Optional[Dict[str, Dict[str, Any]]] = None,
        credentials: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            browser_session: BrowserSession instance
            commands: Dict mapping command names to flow configurations
            credentials: Dict with USERNAME, PASSWORD, etc.
        """
        self.session = browser_session
        self.commands = commands or {}
        self.credentials = credentials or {}
        self.run = _RunProxy(self)

    def execute_command(self, command_name: str) -> Dict[str, Any]:
        """Execute a named command."""
        if command_name not in self.commands:
            raise ValueError(f"Unknown command: {command_name}")

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
        """Execute a single flow."""
        name = flow.get("name")
        login_file = flow.get("login")
        steps_file = flow.get("steps")

        log("FlowOrchestrator", f"→ Flow: {name}", level="info")

        try:
            executor = Executor(self.session, name, self.credentials)

            # Execute login steps
            if login_file:
                executor.execute_file(login_file)

            # Execute main steps
            executor.execute_file(steps_file)

            log("FlowOrchestrator", f"✓ Flow {name} completed", level="info")

            return {
                "success": True,
                "flow_name": name,
                "downloaded_file": None,
            }

        except Exception as e:
            log("FlowOrchestrator", f"✗ Flow {name} failed: {e}", level="error")
            return {
                "success": False,
                "flow_name": name,
                "error": str(e),
            }
