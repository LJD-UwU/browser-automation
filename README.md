# 🧭 Navegador

**Navegador** es un motor de automatización de navegador basado en **flujos declarativos en JSON**, diseñado para ejecutar procesos repetitivos en la web de forma **estable, escalable y multiplataforma (Windows / Linux)** usando Selenium y Microsoft Edge.

El objetivo del proyecto es **separar completamente la lógica de automatización del código**, permitiendo que los flujos se definan únicamente con archivos JSON.

---

## 🚀 Características principales

- ✅ Automatización basada en steps declarativos (JSON)

- ✅ Soporte para login reutilizable

- ✅ Detección de cambios en la web antes de descargar

- ✅ Descargas estables (manejo de `(1)`, `(2)`, etc.)

- ✅ Copia/movimiento automático de archivos a carpeta temporal

- ✅ Descarga automática de msedgedriver (sin usar PATH)

- ✅ Compatible con Windows y Linux

- ✅ Arquitectura modular y extensible

- ✅ Logging centralizado


---

## 📁 Estructura del proyecto

```pl
navegador/
├── main.py                 # Orquestador principal
├── README.md
├── requirements.txt
│
├── navegador/
│   ├── browser/            # Selenium + Edge
│   │   ├── browser.py      # Inicia y cierra el navegador
│   │   ├── executor.py     # Ejecuta pasos JSON
│   │   ├── detector.py     # Detecta/descarga msedgedriver
│   │   └── downloader.py  # Descarga driver según versión de Edge
│   │
│   ├── flows/              # Flujos declarativos
│   │   └── example.json
│   │
│   ├── filesystem/         # Manejo de archivos
│   │   ├── paths.py        # Rutas del sistema
│   │   └── file_utils.py   # Descargas, copias, temporales
│   │
│   ├── config/             # Configuración del usuario
│   │   ├── config.json
│   │   └── manager.py
│   │
│   ├── state/              # Estado persistente
│   │   └── change_detector.py
│   │
│   └── logging/            # Logging centralizado
│       └── logger.py
│
└── drivers/                # msedgedriver descargado automáticamente
```

---

## 🧠 Concepto clave: Flujos declarativos

Un **flow** describe **qué hacer**, no **cómo hacerlo**.

Ejemplo de flujo:

```json
{
  "name": "RealTime",
  "login": "flows/mail.json",
  "steps": "flows/real_time.json",
  "download_keyword": "Real-time production report",
  "detect_change": false
}
```

### Campos del flow

| **Campo** |  **Descripción**|
|-----------|-----------------|
`name`        |       Nombre del flujo (y del perfil del navegador)
`login`       |       JSON con pasos de login (opcional)
`steps`       |       JSON con pasos principales
`download_keyword`    |       Texto para detectar archivo descargado
`detect_change`       |        Si se debe validar cambio antes de descargar
`change_selector`     |       Selector XPath/CSS para detectar cambio
`path_cambio`         |       Archivo donde se guarda el último valor

---

## 🧾 Formato de pasos JSON

Cada archivo JSON contiene una lista de pasos:


```json
[
  {
    "command": "open",
    "target": "https://example.com",
    "value": ""
  },
  {
    "command": "click",
    "target": "xpath=//button[@id='login']",
    "value": ""
  },
  {
    "command": "type",
    "target": "id=username",
    "value": "${USERNAME}"
  }
]
```

### Comandos soportados
| Comando | Descripción |
|---------|-------------|
`open`        |    Navega a una URL
`click`       |    Click en un elemento
`type` / `sendKeys`     |    Escribe texto
`pause`       |   Pausa en ms
`Teclas`      |   `KEY_ENTER`, `KEY_TAB`, `KEY_ESCAPE`, etc.

Las variables `${VAR}` se cargan desde `config.json`.

---

## 🔐 Configuración (`config.json`)

Archivo para credenciales y variables:

```json
{
  "USERNAME": "usuario",
  "PASSWORD": "secreto"
}
```

Se acceden automáticamente desde los JSON usando `${USERNAME}`.

# 📥 Descargas y archivos temporales

- Las descargas se detectan por keyword

- Si hay múltiples archivos:

    - Se elige el de número más alto `(N)`

    - Se valida que el tamaño sea estable

- El archivo final se mueve o copia a:

    ```plaintext
    TEMP_DIR = %TEMP%/uppph_daily_temp
    ```

Esto evita:

- conflictos

- archivos bloqueados

- descargas incompletas

---

## 🌐 Navegador y driver

- Se usa Microsoft Edge

- El sistema:

    - detecta la versión instalada

    - descarga el `msedgedriver` exacto

    - lo guarda en `drivers`/

- No se requiere modificar PATH

> ⚠️ Si un flujo descarga archivos, NO se usa headless para garantizar estabilidad.

---

## 🔄 Detección de cambios

Para flujos que solo deben ejecutarse si algo cambió:

1. Se lee un valor de la web (XPath/CSS)

2. Se compara contra el último valor guardado

3. Solo si cambia, se ejecuta la descarga

Esto evita:

- descargas innecesarias

- reprocesos

- ruido operativo

---

## ▶️ Ejecución

Desde la raíz del proyecto:

```bash
python main.py
```

---

## 🧪 Recomendaciones de uso

- Usar un flow por proceso

- Reutilizar `login.json`

- Evitar selectores frágiles

- Probar flows sin headless al inicio

- Mantener los JSON simples

---

## 🛣️ Mejoras futuras (roadmap)

- CLI: `python -m navegador run flow.json`

- Ejecución paralela de flows

- Retry policy por paso

- Screenshots en error

- Reportes de ejecución

- Validación de esquema JSON

- Modo `dry-run`

---

## 📌 Note del proyecto

>[!NOTE]
>El código no cambia.
>Los flujos sí.

Navegador está pensado para que el código sea estable y los procesos evolucionen únicamente editando JSON.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia especificada en el archivo [`LICENSE`](LICENSE "Ver licencia").