"""Browser module for navegador-automate."""

from navegador_automate.browser.session import BrowserSession
from navegador_automate.browser.factory import BrowserFactory
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
    "NavigadorException",
    "BrowserLaunchError",
    "BrowserTimeoutError",
    "SelectorNotFoundError",
    "DriverNotFoundError",
]
