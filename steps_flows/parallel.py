"""
Ejemplo 3: Ejecución paralela de flujos
Demuestra ejecutar múltiples flujos simultáneamente.
"""

import time
from navegador_automate import BrowserFactory, FlowOrchestrator
from flows_config import COMMANDS


def main():
    """Run parallel flow execution example."""
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

        print("\n⏱️  Midiendo tiempo de ejecución paralela...")
        start_time = time.time()

        print("▶️  Ejecutando comando 'all' (PARALELO)...")
        result = orch.run("all")

        elapsed = time.time() - start_time

        print(f"\n✅ Resultado: {result['success']}")
        print(f"⏱️  Tiempo total: {elapsed:.2f}s")
        print(f"📊 Flujos ejecutados en paralelo:")

        for flow_name, flow_result in result["flows"].items():
            status = "✅" if flow_result["success"] else "❌"
            print(f"  {status} {flow_name}")

            if flow_result.get("logs"):
                print(f"     📝 Pasos: {len(flow_result['logs'])}")

            if flow_result.get("downloaded_file"):
                print(f"     📥 {flow_result['downloaded_file']}")

        print(f"\n💡 Consejo: Con paralelismo, N flujos tardan ~(max_time)/max_workers")
        print(f"   En este caso: 3 flujos en paralelo con max_workers=3")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        print("\n🛑 Cerrando navegador...")
        browser.quit()
        print("✅ Navegador cerrado")


if __name__ == "__main__":
    main()
