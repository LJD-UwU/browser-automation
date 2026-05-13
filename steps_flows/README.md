# Steps Flows - Example Scripts

Este directorio contiene ejemplos de cómo usar `navegador-automate` con flujos predefinidos.

## Archivos

### Configuración
- **flows_config.py** - Define `FLOW_*` y `COMMANDS` reutilizables
  - `FLOW_BASE_PLAN` - Flujo de plan base
  - `FLOW_REAL_TIME` - Flujo de tiempo real
  - `FLOW_LOSS_TIME` - Flujo de pérdida de tiempo
  - `COMMANDS` - Comandos predefinidos (base, real, loss, all)

### Ejemplos
- **basic.py** - Uso simple de `BrowserFactory`
  - Crear navegador
  - Navegar a sitio
  - Hacer clic y escribir
  - Esperar elementos

- **flows_orchestration.py** - Usar `FlowOrchestrator` con comandos
  - Cargar comandos de `flows_config`
  - Ejecutar comando individual
  - Ver resultados

- **parallel.py** - Ejecución paralela de flujos
  - Ejecutar múltiples flujos simultáneamente
  - Medir tiempo
  - Ver resultados combinados

- **custom.py** - Flujos personalizados sin config
  - Crear flujo custom ad-hoc
  - Ejecutar sin `flows_config`

### Datos
- **data/json/** - Archivos JSON con pasos
  - `mail.json` - Pasos de login
  - `basePlan.json` - Pasos principales base
  - `realTimeProduction.json` - Pasos de tiempo real
  - `lossTime.json` - Pasos de pérdida de tiempo

## Uso

### Ejecutar ejemplo básico
```bash
cd steps_flows
python basic.py
```

### Ejecutar flujos con orquestación
```bash
cd steps_flows
python flows_orchestration.py
```

### Ejecutar flujos en paralelo
```bash
cd steps_flows
python parallel.py
```

### Ejecutar flujo custom
```bash
cd steps_flows
python custom.py
```

## Structure de Flujos

Un flujo requiere:
1. **login** - Ruta a JSON con pasos de autenticación
2. **steps** - Ruta a JSON con pasos principales
3. **name** - Nombre del flujo
4. **download_keyword** - (opcional) Palabra clave para detectar descargas

### Estructura de JSON de pasos

```json
[
  {
    "command": "open",
    "target": "https://example.com",
    "value": ""
  },
  {
    "command": "type",
    "target": "id=email",
    "value": "${USERNAME}"
  },
  {
    "command": "click",
    "target": "xpath=//button[@type='submit']",
    "value": ""
  },
  {
    "command": "wait",
    "target": "id=dashboard",
    "value": "10000"
  }
]
```

### Comandos Soportados

- **open** - Abrir URL
- **click** - Hacer clic en elemento
- **type** - Escribir texto en campo
- **pause** - Pausar N milisegundos
- **wait** - Esperar elemento (timeout en ms)
- **key** - Presionar tecla (ENTER, TAB, etc)
- **get_text** - Obtener texto de elemento
- **get_attribute** - Obtener atributo de elemento
- **check_visible** - Verificar que elemento es visible

### Selectores Soportados

- `xpath=//div[@id='test']` - XPath
- `css=.button-class` - CSS Selector
- `id=myElement` - ID
- `name=fieldName` - Name attribute
- `class=className` - Class
- `tag=div` - Tag name
- `//div[@id='test']` - XPath (default)

### Variables Interpoladas

Las credenciales se interpolan en los pasos:
- `${USERNAME}` - Reemplazado con USERNAME
- `${PASSWORD}` - Reemplazado con PASSWORD
- Otros: `${VAR}` se reemplaza con credenciales['VAR']

## Flujo de Ejecución

### Secuencial
```python
# Los flujos se ejecutan uno tras otro
orch.run("base")  # Ejecuta FLOW_BASE_PLAN
result = orch.run_sequence(["base", "real"])  # Secuencial
```

### Paralelo
```python
# Los flujos se ejecutan simultáneamente
orch.run("all")  # Si COMMANDS["all"]["parallel"] = True
result = orch.run_parallel(["base", "real"])  # En paralelo
```

## Resultados

Cada ejecución retorna un diccionario con:

```python
{
    "success": True,           # Éxito general
    "flow_name": "basePlan",   # O "command": "base"
    "logs": [...],             # Registro de pasos
    "downloaded_file": "/path/to/file.xlsx",  # Si aplica
    "error": "Error message",  # Si falló
}
```

## Notas

- Los navegadores se lanzan automáticamente en `factory.build()`
- Los flujos continúan incluso si un paso falla (graceful degradation)
- Los logs son detallados para debugging
- Las credenciales se maskean en logs (no se loguean contraseñas)
- Ejecución paralela con ThreadPoolExecutor (max_workers=3-5)

## Próximos Pasos

Para crear tus propios flujos:

1. Crear JSON con pasos
2. Crear FlowDefinition
3. Agregar a COMMANDS
4. Ejecutar con FlowOrchestrator

Ejemplo:
```python
from navegador_automate import FlowDefinition, FlowOrchestrator

mi_flow = FlowDefinition(
    name="mi_flujo",
    login="steps_flows/data/json/mail.json",
    steps="steps_flows/data/json/mi_flujo.json",
)

orch = FlowOrchestrator(browser, credentials=creds)
result = orch.run_flow(
    name="mi_flujo",
    login="steps_flows/data/json/mail.json",
    steps="steps_flows/data/json/mi_flujo.json",
)
```
