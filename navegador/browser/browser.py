from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium import webdriver

from navegador.browser.detector import DriverDetector
from navegador.filesystem.paths import PROFILES_DIR, DOWNLOAD_DIR
from navegador.logging.logger import log


class Browser:
    def __init__(self, name: str, headless: bool = False):
        """
        headless=False por defecto para garantizar descargas estables.
        """
        self.name = name
        self.headless = headless
        self.driver = None

    def start(self):
        log(self.name, "Iniciando navegador")

        profile_path = PROFILES_DIR / self.name
        profile_path.mkdir(parents=True, exist_ok=True)

        options = Options()

        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # Permite inspección en caso de fallo
        options.add_experimental_option("detach", True)

        prefs = {
            "download.default_directory": str(DOWNLOAD_DIR),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.open_pdf_in_system_reader": False,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "browser.show_hub_popup_on_download_start": False,
        }
        options.add_experimental_option("prefs", prefs)

        detector = DriverDetector(self.name)
        driver_path = detector.get_driver_path()

        service = Service(executable_path=str(driver_path))
        self.driver = webdriver.Edge(service=service, options=options)

        log(self.name, "Edge iniciado correctamente", "OK")
        return self.driver

    def quit(self):
        if self.driver:
            log(self.name, "Cerrando navegador")
            try:
                self.driver.quit()
            finally:
                self.driver = None