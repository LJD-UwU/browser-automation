"""
Ejemplo 2: Orquestación de flujos con FlowOrchestrator
Demuestra ejecución de flujos predefinidos desde flows_config.
"""

from navegador_automate import BrowserFactory, FlowOrchestrator
from flows_config import COMMANDS


def main():
    """Run orchestrator example with predefined commands."""
    print("🌐 Iniciando navegador Firefox...")
    browser = BrowserFactory.firefox(headless=False).build()

    try:
        print("⚙️  Inicializando orquestador...")
        orch = FlowOrchestrator(
            browser,
            commands=COMMANDS,
            credentials={
                "USERNAME": "user@example.com",
                "PASSWORD": "secret123",
            },
        )

        print("📋 Comandos disponibles:")
        for cmd in orch.get_command_names():
            print(f"  - {cmd}")

        print("\n▶️  Ejecutando comando 'base' (secuencial)...")
        result = orch.run("base")

        print(f"\n✅ Resultado: {result['success']}")
        print(f"📊 Flujos ejecutados:")
        for flow_name, flow_result in result["flows"].items():
            status = "✅" if flow_result["success"] else "❌"
            print(f"  {status} {flow_name}")

            if flow_result.get("downloaded_file"):
                print(f"     📥 {flow_result['downloaded_file']}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        print("\n🛑 Cerrando navegador...")
        browser.quit()
        print("✅ Navegador cerrado")


if __name__ == "__main__":
    main()
