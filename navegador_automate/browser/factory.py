"""
BrowserFactory: Constructor fluido para instancias de BrowserSession.

Proporciona un patrón Builder para crear navegadores configurados
de manera declarativa con soporte para Edge, Chrome y Firefox.

Ejemplo:
    >>> browser = BrowserFactory.edge() \\
    ...     .with_headless(False) \\
    ...     .with_download_dir(r"C:\\Downloads") \\
    ...     .build()
"""

from pathlib import Path
from typing import Optional, Union

from navegador_automate.browser.session import BrowserSession
from navegador_automate.utils.logger import log


class BrowserFactory:
    """
    Factory pattern para crear BrowserSession configurados.

    Permite encadenar métodos de configuración antes de construir
    la instancia final del navegador.

    Atributos privados:
        _browser_type: Tipo de navegador ("edge", "chrome", "firefox")
        _headless: Ejecutar sin interfaz gráfica
        _profile_dir: Directorio de perfil del usuario
        _download_dir: Directorio para descargas
        _driver_path: Ruta personalizada al ejecutable del driver
    """

    def __init__(self, browser_type: str) -> None:
        """
        Inicializar el factory con un tipo de navegador.

        Args:
            browser_type: Tipo de navegador ("edge", "chrome", "firefox")

        Raises:
            ValueError: Si browser_type no es válido

        Example:
            >>> factory = BrowserFactory("edge")
        """
        valid_types = ["edge", "chrome", "firefox"]
        if browser_type.lower() not in valid_types:
            raise ValueError(
                f"browser_type debe ser uno de {valid_types}, "
                f"recibido: {browser_type}"
            )

        self._browser_type = browser_type.lower()
        self._headless = True
        self._profile_dir: Optional[Path] = None
        self._download_dir: Optional[Path] = None
        self._driver_path: Optional[Path] = None
        self._drivers_dir: Optional[Path] = None

    @staticmethod
    def edge() -> "BrowserFactory":
        """
        Crear un factory configurado para Microsoft Edge.

        Edge es el navegador recomendado para la mayoría de scripts
        de automatización debido a mejor rendimiento y compatibilidad
        con Windows.

        Returns:
            BrowserFactory: Instancia configurada para Edge

        Example:
            >>> browser = BrowserFactory.edge().build()
            >>> browser.get("https://example.com")
        """
        return BrowserFactory("edge")

    @staticmethod
    def chrome() -> "BrowserFactory":
        """
        Crear un factory configurado para Google Chrome.

        Chrome es el navegador más compatible con Selenium y ofrece
        mejor debugging y compatibilidad multiplataforma.

        Returns:
            BrowserFactory: Instancia configurada para Chrome

        Example:
            >>> browser = BrowserFactory.chrome().build()
        """
        return BrowserFactory("chrome")

    @staticmethod
    def firefox() -> "BrowserFactory":
        """
        Crear un factory configurado para Mozilla Firefox.

        Firefox es el navegador de código abierto con mejor privacidad
        y control fino sobre configuración del navegador.

        Returns:
            BrowserFactory: Instancia configurada para Firefox

        Example:
            >>> browser = BrowserFactory.firefox().build()
        """
        return BrowserFactory("firefox")

    def with_headless(self, enabled: bool = True) -> "BrowserFactory":
        """
        Configurar modo headless (sin interfaz gráfica).

        En modo headless, el navegador se ejecuta sin mostrar ventana.
        Útil para scripts automatizados en servidor o CI/CD.
        En False, muestra la ventana del navegador (recomendado para debug).

        Args:
            enabled: True = sin GUI (más rápido), False = con GUI (debug)
                    Defaults to True.

        Returns:
            BrowserFactory: Self para encadenamiento de métodos

        Example:
            >>> browser = BrowserFactory.edge() \\
            ...     .with_headless(False) \\  # Ver lo que hace
            ...     .build()
        """
        self._headless = enabled
        return self

    def with_profile_dir(self, directory: Union[str, Path]) -> "BrowserFactory":
        """
        Establecer directorio de perfil del usuario.

        El perfil del navegador contiene historial, cookies, extensiones
        y configuraciones guardadas. Útil para reutilizar sesiones.

        Args:
            directory: Ruta al directorio de perfil del navegador.
                      Puede ser string o Path object.

        Returns:
            BrowserFactory: Self para encadenamiento de métodos

        Raises:
            FileNotFoundError: Si el directorio no existe

        Example:
            >>> browser = BrowserFactory.edge() \\
            ...     .with_profile_dir(r"C:\\Users\\User\\AppData\\Local\\Microsoft\\Edge\\User Data") \\
            ...     .build()
        """
        profile_path = Path(directory)
        if not profile_path.exists():
            raise FileNotFoundError(f"Directorio de perfil no encontrado: {profile_path}")

        self._profile_dir = profile_path
        return self

    def with_download_dir(self, directory: Union[str, Path]) -> "BrowserFactory":
        """
        Establecer directorio para descargas automáticas.

        Configura el navegador para descargar archivos automáticamente
        al directorio especificado sin mostrar diálogos.

        Args:
            directory: Ruta al directorio de descargas.
                      Se crea si no existe.

        Returns:
            BrowserFactory: Self para encadenamiento de métodos

        Example:
            >>> browser = BrowserFactory.edge() \\
            ...     .with_download_dir(r"C:\\Downloads") \\
            ...     .build()
        """
        self._download_dir = Path(directory)
        self._download_dir.mkdir(parents=True, exist_ok=True)
        return self

    def with_driver_path(self, path: Union[str, Path]) -> "BrowserFactory":
        """
        Establecer ruta personalizada al ejecutable del WebDriver.

        Por defecto, Selenium busca el driver en PATH.
        Use este método si tiene el driver en ubicación personalizada.

        Args:
            path: Ruta completa al ejecutable del driver
                 (msedgedriver.exe, chromedriver, geckodriver, etc.)

        Returns:
            BrowserFactory: Self para encadenamiento de métodos

        Raises:
            FileNotFoundError: Si el archivo del driver no existe

        Example:
            >>> browser = BrowserFactory.edge() \\
            ...     .with_driver_path(r"C:\\drivers\\msedgedriver.exe") \\
            ...     .build()
        """
        driver_path = Path(path)
        if not driver_path.exists():
            raise FileNotFoundError(f"Driver no encontrado: {driver_path}")

        self._driver_path = driver_path
        return self

    def with_drivers_dir(self, directory: Union[str, Path]) -> "BrowserFactory":
        """
        Set the directory where WebDriver binaries will be downloaded and cached.

        By default, navegador_automate detects the calling project's root directory
        and creates a 'drivers/' subfolder there.  Use this method to override that
        location explicitly.

        Example::

            BrowserFactory.edge() \\
                .with_drivers_dir(r"C:\\MyProject\\drivers") \\
                .with_download_dir(DOWNLOAD_DIR) \\
                .build()
        """
        self._drivers_dir = Path(directory)
        return self

    def view_window(self, visible: bool = True) -> "BrowserFactory":
        """
        Controlar visibilidad de la ventana del navegador.

        Similar a with_headless() pero con semántica inversa.
        True = mostrar ventana, False = ocultar.

        Args:
            visible: True = ventana visible, False = ventana oculta.
                    Defaults to True.

        Returns:
            BrowserFactory: Self para encadenamiento de métodos

        Note:
            Este método es ignorado si headless=True.

        Example:
            >>> browser = BrowserFactory.edge() \\
            ...     .view_window(True) \\  # Mostrar ventana
            ...     .build()
        """
        self._headless = not visible
        return self

    def build(self) -> BrowserSession:
        """
        Construir y retornar la instancia configurada de BrowserSession.

        Crea un WebDriver con toda la configuración acumulada
        en los métodos anteriores.

        Returns:
            BrowserSession: Navegador configurado listo para usar

        Raises:
            WebDriverException: Si el driver no se puede lanzar
            FileNotFoundError: Si el ejecutable del driver no existe

        Example:
            >>> factory = BrowserFactory.edge() \\
            ...     .with_headless(False) \\
            ...     .with_download_dir(r"C:\\Downloads")
            >>> browser = factory.build()
            >>> browser.get("https://example.com")
            >>> browser.quit()
        """
        log("BrowserFactory", f"Building {self._browser_type}", level="info")

        session = BrowserSession(
            browser_type=self._browser_type,
            headless=self._headless,
            download_dir=self._download_dir,
            profile_dir=self._profile_dir,
            driver_path=self._driver_path,
            drivers_dir=self._drivers_dir,
        )
        session.launch()
        return session
