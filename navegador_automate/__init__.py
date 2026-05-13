"""navegador-automate: Browser automation library with JSON flow orchestration."""

__version__ = "0.1.0"
__author__ = "LJD-UwU"

from navegador_automate.browser import BrowserFactory, BrowserSession, BrowserContext
from navegador_automate.flows import (
    FlowDefinition,
    Executor,
    FlowParser,
    FlowOrchestrator,
)
from navegador_automate.logger import log, setup_logger

__all__ = [
    "BrowserFactory",
    "BrowserSession",
    "BrowserContext",
    "FlowDefinition",
    "Executor",
    "FlowParser",
    "FlowOrchestrator",
    "log",
    "setup_logger",
]
