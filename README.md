# navegador-automate 🚀

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-60%2F60-brightgreen)

Librería de automatización de navegadores con orquestación de flujos JSON. Sin configuración manual, sin dependencias externas complicadas.

## 🎯 Características

- ✅ **BrowserFactory (Builder Pattern)** - Crear navegadores sin configuración
- ✅ **FlowDefinition** - Definir flujos con JSON
- ✅ **Executor** - Ejecutar pasos automatizados
- ✅ **FlowOrchestrator** - Orquestar múltiples flujos
- ✅ **Ejecución Paralela** - ThreadPoolExecutor integrado
- ✅ **Multi-OS** - Windows, macOS, Linux
- ✅ **Multi-Browser** - Firefox, Edge, Chrome, Safari
- ✅ **Retry Automático** - Manejo de timeouts
- ✅ **Logging Centralizado** - Con rotación automática
- ✅ **Variable Interpolation** - ${USERNAME}, ${PASSWORD}, etc
- ✅ **60 Tests** - 100% path coverage

## 📦 Instalación

### Desde PyPI (próximamente)
```bash
pip install navegador-automate
```

### Desde el repositorio
```bash
git clone https://github.com/LJD-UwU/navegador-automate.git
cd navegador-automate
pip install -e .
```

### Con dependencias de desarrollo
```bash
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Uso Simple (BrowserFactory)
```python
from navegador_automate import BrowserFactory

# Sin Config manual ✅
browser = BrowserFactory.firefox(headless=False).build()

browser.open("https://example.com")
browser.click("xpath=//button[@id='login']")
browser.type_text("id=email", "user@example.com")
browser.type_text("id=password", "secret")
browser.wait_for_element("id=dashboard")

browser.quit()
```

### Uso con Context Manager
```python
from navegador_automate import BrowserContext

with BrowserContext("firefox", headless=False) as browser:
    browser.open("https://example.com")
    browser.click("xpath=//button")
    # Browser auto-closes
```

### Orquestación de Flujos
```python
from navegador_automate import BrowserFactory, FlowOrchestrator
from steps_flows.flows_config import COMMANDS

with BrowserFactory.edge() \
    .with_download_dir("/downloads") \
    .view_window(True) \
    .build() as browser:

    orch = FlowOrchestrator(
        browser,
        commands=COMMANDS,
        credentials={
            "USERNAME": "user@example.com",
            "PASSWORD": "secret123"
        }
    )

    result = orch.run.basePlan()
```

## 📋 Builder Pattern

```python
factory = (
    BrowserFactory.edge()
    .view_window(True)           # Show/hide window
    .with_download_dir("/path")  # Custom download folder
    .with_profile_dir("/path")   # Custom profile folder
)

browser = factory.build()
```

### Window Visibility

```python
# Show window (default)
BrowserFactory.edge().view_window(True).build()

# Hide window (headless mode)
BrowserFactory.edge().view_window(False).build()

# Equivalent: use with_headless()
BrowserFactory.edge().with_headless(False).build()
```

## 🔗 Selectores Soportados

```python
# XPath
browser.click("xpath=//button[@id='submit']")

# CSS
browser.click("css=.button-primary")

# ID
browser.click("id=submit-btn")

# Name
browser.click("name=action")

# Class
browser.click("class=btn")

# Tag
browser.click("tag=button")
```

## 🔄 Comandos de Flujos JSON

```json
[
  {"command": "open", "target": "https://example.com", "value": ""},
  {"command": "type", "target": "id=email", "value": "${USERNAME}"},
  {"command": "type", "target": "id=password", "value": "${PASSWORD}"},
  {"command": "click", "target": "xpath=//button[@type='submit']", "value": ""},
  {"command": "wait", "target": "id=dashboard", "value": "10000"},
  {"command": "pause", "target": "", "value": "2000"},
  {"command": "key", "target": "", "value": "ENTER"}
]
```

## 📝 Ejemplos

Ver directorio `steps_flows/` para ejemplos completos:

- `basic.py` - Uso simple BrowserFactory
- `flows_orchestration.py` - Orquestación con flows_config
- `parallel.py` - Ejecución paralela
- `custom.py` - Flujos personalizados

```bash
cd steps_flows

# Ejecutar ejemplo
python basic.py
python flows_orchestration.py
python parallel.py
python custom.py
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=navegador_automate

# Test específico
pytest tests/test_factory.py -v
```

## 📚 Documentación Completa

- [TAREA 1: Browser + Factory + Drivers](TAREA_1_COMPLETADA.md)
- [TAREA 2: FlowDefinition + Executor](TAREA_2_COMPLETADA.md)
- [TAREA 3: FlowOrchestrator](TAREA_3_COMPLETADA.md)
- [TAREA 4: Flujos + Scripts](TAREA_4_COMPLETADA.md)
- [TAREA 5: Setup + Docs + CI/CD](TAREA_5_COMPLETADA.md)

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 👤 Autor

- **LJD-UwU** - Desarrollo inicial

---

**Made with ❤️ by LJD-UwU**