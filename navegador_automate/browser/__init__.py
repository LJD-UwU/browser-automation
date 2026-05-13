"""Browser module for navegador-automate."""

from navegador_automate.browser.browser import BrowserSession
from navegador_automate.browser.factory import BrowserFactory
from navegador_automate.browser.context import BrowserContext
from navegador_automate.browser.exceptions import (
    NavigadorException,
    BrowserLaunchError,
    BrowserTimeoutError,
    SelectorNotFoundError,
    DriverNotFoundError,
)

__all__ = [
    "BrowserSession",
    "BrowserFactory",
    "BrowserContext",
    "NavigadorException",
    "BrowserLaunchError",
    "BrowserTimeoutError",
    "SelectorNotFoundError",
    "DriverNotFoundError",
]
