"""Custom exceptions for navegador-automate."""


class NavigadorException(Exception):
    """Base exception for navegador-automate."""

    pass


class DriverNotFoundError(NavigadorException):
    """Raised when WebDriver is not found."""

    pass


class BrowserTimeoutError(NavigadorException):
    """Raised when browser operation times out."""

    pass


class BrowserLaunchError(NavigadorException):
    """Raised when browser fails to launch."""

    pass


class SelectorNotFoundError(NavigadorException):
    """Raised when element selector is not found."""

    pass


class InvalidFlowDefinitionError(NavigadorException):
    """Raised when flow definition is invalid."""

    pass


class FlowExecutionError(NavigadorException):
    """Raised when flow execution fails."""

    pass


class DownloadError(NavigadorException):
    """Raised when file download fails."""

    pass


class ChangeDetectionError(NavigadorException):
    """Raised when change detection fails."""

    pass
