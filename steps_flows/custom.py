"""
Ejemplo 4: Flujos personalizados sin flows_config
Demuestra ejecución ad-hoc de flujos custom.
"""

from navegador_automate import BrowserFactory, FlowOrchestrator


def main():
    """Run custom flow execution example."""
    print("🌐 Iniciando navegador Firefox...")
    browser = BrowserFactory.firefox(headless=False).build()

    try:
        print("⚙️  Inicializando orquestador...")
        orch = FlowOrchestrator(browser)

        print("\n▶️  Ejecutando flujo custom 'data_export'...")
        result = orch.run_flow(
            name="data_export",
            login="steps_flows/data/json/mail.json",
            steps="steps_flows/data/json/basePlan.json",
            download_keyword="export",
        )

        print(f"\n✅ Flujo completado: {result['success']}")

        if result.get("logs"):
            print("📝 Logs de ejecución:")
            for log in result["logs"][:5]:  # Primeros 5 logs
                print(f"  - {log}")
            if len(result["logs"]) > 5:
                print(f"  ... y {len(result['logs']) - 5} más")

        if result.get("downloaded_file"):
            print(f"📥 Archivo descargado: {result['downloaded_file']}")

        if not result.get("success") and result.get("error"):
            print(f"❌ Error: {result['error']}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        print("\n🛑 Cerrando navegador...")
        browser.quit()
        print("✅ Navegador cerrado")


if __name__ == "__main__":
    main()
