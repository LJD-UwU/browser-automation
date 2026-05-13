"""Flow orchestrator - manages command execution and flow orchestration."""

from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from navegador_automate.flows.definition import FlowDefinition
from navegador_automate.flows.executor import Executor
from navegador_automate.logger import log
from navegador_automate.browser.exceptions import FlowExecutionError


@dataclass
class CommandConfig:
    """Configuration for a command."""

    flows: List[FlowDefinition]
    parallel: bool = False
    max_workers: int = 5


class _RunProxy:
    """Proxy for dynamic run.commandName() syntax."""

    def __init__(self, orchestrator: "FlowOrchestrator"):
        self.orchestrator = orchestrator

    def __call__(self, command_name: str) -> Dict[str, Any]:
        """Allow run('commandName') syntax."""
        return self.orchestrator._execute_command(command_name)

    def __getattr__(self, name: str) -> callable:
        """Allow run.commandName() syntax."""
        if name == "all":
            return self.orchestrator._run_all_commands
        if name in self.orchestrator.commands:
            return lambda: self.orchestrator._execute_command(name)
        raise AttributeError(f"Command not found: {name}")


class FlowOrchestrator:
    """Orchestrate execution of multiple flows."""

    def __init__(
        self,
        browser,
        commands: Optional[Dict[str, Dict[str, Any]]] = None,
        credentials: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            browser: BrowserSession instance.
            commands: Dictionary of command configurations.
            credentials: Credentials for flow execution (USERNAME, PASSWORD, etc).
        """
        self.browser = browser
        self.executor = Executor(browser.driver, download_dir=browser.download_dir)
        self.credentials = credentials or {}
        self.commands = self._parse_commands(commands or {})
        self.results: Dict[str, Any] = {}
        self.run = _RunProxy(self)

    def run_flow(
        self,
        name: str,
        login: str,
        steps: str,
        download_keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a custom flow without predefined command.

        Args:
            name: Flow name.
            login: Path to login steps JSON.
            steps: Path to main steps JSON.
            download_keyword: Keyword for file detection.

        Returns:
            Execution result.
        """
        log("FlowOrchestrator", f"Running custom flow: {name}", level="info")

        flow = FlowDefinition(
            name=name,
            login=login,
            steps=steps,
            download_keyword=download_keyword,
        )

        result = self.executor.execute_flow(flow, self.credentials)
        self.results[name] = result
        return result

    def run_sequence(self, command_names: List[str]) -> Dict[str, Any]:
        """
        Execute multiple commands sequentially.

        Args:
            command_names: List of command names.

        Returns:
            Combined results.
        """
        log(
            "FlowOrchestrator",
            f"Running {len(command_names)} commands sequentially",
            level="info",
        )

        all_results = {"commands": {}, "success": True, "total_time": 0}

        for cmd_name in command_names:
            try:
                result = self.run(cmd_name)
                all_results["commands"][cmd_name] = result

                if not result.get("success", False):
                    all_results["success"] = False

            except Exception as e:
                log("FlowOrchestrator", f"Command {cmd_name} failed: {e}", level="error")
                all_results["commands"][cmd_name] = {"success": False, "error": str(e)}
                all_results["success"] = False

        return all_results

    def run_parallel(self, command_names: List[str]) -> Dict[str, Any]:
        """
        Execute multiple commands in parallel.

        Args:
            command_names: List of command names.

        Returns:
            Combined results.
        """
        log(
            "FlowOrchestrator",
            f"Running {len(command_names)} commands in parallel",
            level="info",
        )

        all_results = {"commands": {}, "success": True}

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_cmd = {
                executor.submit(self.run, cmd_name): cmd_name
                for cmd_name in command_names
            }

            for future in as_completed(future_to_cmd):
                cmd_name = future_to_cmd[future]

                try:
                    result = future.result()
                    all_results["commands"][cmd_name] = result

                    if not result.get("success", False):
                        all_results["success"] = False

                except Exception as e:
                    log(
                        "FlowOrchestrator",
                        f"Command {cmd_name} failed: {e}",
                        level="error",
                    )
                    all_results["commands"][cmd_name] = {"success": False, "error": str(e)}
                    all_results["success"] = False

        return all_results

    def set_credentials(self, credentials: Dict[str, Any]) -> None:
        """
        Update credentials.

        Args:
            credentials: New credentials dict.
        """
        self.credentials = credentials
        log("FlowOrchestrator", "Credentials updated", level="debug", secure=True)

    def get_command_names(self) -> List[str]:
        """Get list of available command names."""
        return list(self.commands.keys())

    def _parse_commands(self, commands_dict: Dict[str, Dict]) -> Dict[str, CommandConfig]:
        """
        Parse commands dictionary into CommandConfig objects.

        Args:
            commands_dict: Raw commands dictionary.

        Returns:
            Dictionary of CommandConfig objects.
        """
        parsed = {}

        for cmd_name, cmd_config in commands_dict.items():
            flows = cmd_config.get("flows", [])
            parallel = cmd_config.get("parallel", False)
            max_workers = cmd_config.get("max_workers", 5)

            if not flows:
                log(
                    "FlowOrchestrator",
                    f"Command '{cmd_name}' has no flows",
                    level="warning",
                )
                continue

            parsed[cmd_name] = CommandConfig(
                flows=flows,
                parallel=parallel,
                max_workers=max_workers,
            )

        return parsed

    def _run_sequence(
        self, command_name: str, flows: List[FlowDefinition]
    ) -> Dict[str, Any]:
        """
        Execute flows sequentially for a command.

        Args:
            command_name: Command name.
            flows: List of FlowDefinition objects.

        Returns:
            Execution result.
        """
        result = {
            "command": command_name,
            "flows": {},
            "success": True,
            "flow_count": len(flows),
        }

        for flow in flows:
            try:
                flow_result = self.executor.execute_flow(flow, self.credentials)
                result["flows"][flow.name] = flow_result

                if not flow_result.get("success", False):
                    result["success"] = False
                    log(
                        "FlowOrchestrator",
                        f"Flow {flow.name} failed",
                        level="error",
                    )

            except Exception as e:
                result["flows"][flow.name] = {"success": False, "error": str(e)}
                result["success"] = False
                log(
                    "FlowOrchestrator",
                    f"Flow {flow.name} error: {e}",
                    level="error",
                )

        return result

    def _run_parallel(
        self, command_name: str, flows: List[FlowDefinition]
    ) -> Dict[str, Any]:
        """
        Execute flows in parallel for a command.

        Args:
            command_name: Command name.
            flows: List of FlowDefinition objects.

        Returns:
            Execution result.
        """
        result = {
            "command": command_name,
            "flows": {},
            "success": True,
            "flow_count": len(flows),
            "parallel": True,
        }

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_flow = {
                executor.submit(self.executor.execute_flow, flow, self.credentials): flow
                for flow in flows
            }

            for future in as_completed(future_to_flow):
                flow = future_to_flow[future]

                try:
                    flow_result = future.result()
                    result["flows"][flow.name] = flow_result

                    if not flow_result.get("success", False):
                        result["success"] = False

                except Exception as e:
                    result["flows"][flow.name] = {"success": False, "error": str(e)}
                    result["success"] = False
                    log(
                        "FlowOrchestrator",
                        f"Flow {flow.name} error: {e}",
                        level="error",
                    )

        return result

    def _execute_command(self, command_name: str) -> Dict[str, Any]:
        """Execute a command by name."""
        if command_name not in self.commands:
            raise ValueError(f"Command not found: {command_name}")
        config = self.commands[command_name]
        log("FlowOrchestrator", f"Running command: {command_name}", level="info")
        if config.parallel:
            return self._run_parallel(command_name, config.flows)
        else:
            return self._run_sequence(command_name, config.flows)

    def _run_all_commands(self) -> Dict[str, Any]:
        """Execute all commands sequentially."""
        log("FlowOrchestrator", f"Running all {len(self.commands)} commands", level="info")
        return self.run_sequence(list(self.commands.keys()))
