"""
Ejemplo 1: Uso básico de BrowserFactory
Demuestra creación simple de navegador sin Config manual.
"""

from navegador_automate import BrowserFactory


def main():
    """Run basic browser example."""
    print("🌐 Iniciando navegador Firefox...")
    browser = BrowserFactory.firefox(headless=False).build()

    try:
        print("📄 Abriendo sitio de ejemplo...")
        browser.open("https://example.com")

        print("✅ Sitio abierto correctamente")
        title = browser.driver.title
        print(f"📋 Título de página: {title}")

        print("⏳ Esperando elemento...")
        if browser.wait_for_element("xpath=//*[@id='main']"):
            print("✅ Elemento encontrado")

        print("🎯 Haciendo clic en enlace...")
        browser.click("xpath=//a[@href='#']")
        print("✅ Clic realizado")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        print("🛑 Cerrando navegador...")
        browser.quit()
        print("✅ Navegador cerrado")


if __name__ == "__main__":
    main()
