"""navegador-automate: Browser automation library with JSON flow orchestration."""

__version__ = "0.2.0"
__author__ = "LJD-UwU"

from navegador_automate.browser import BrowserFactory, BrowserSession
from navegador_automate.flows import Executor, FlowOrchestrator
from navegador_automate.utils.logger import log

__all__ = [
    "BrowserFactory",
    "BrowserSession",
    "Executor",
    "FlowOrchestrator",
    "log",
]
