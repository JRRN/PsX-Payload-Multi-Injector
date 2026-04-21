# PS MultiInjector

![version](https://img.shields.io/badge/version-1.0.0-blue)

[Ver changelog](./docs/CHANGELOG.md)

READMEs por idioma: [Español](./README.md), [English](./docs/README_en.md), [Português](./docs/README_pt.md), [中文](./docs/README_zh.md), [한국어](./docs/README_ko.md)

Inyector multiplataforma de payloads para PS4/PS5 en Python con interfaz gráfica basado en la idea original de MaNu(TheWizWikii) https://github.com/TheWizWikii/PS5-PS4-Payload-injector-Pro

## Características
- Interfaz gráfica multiplataforma (PySide6/Qt)
- Descarga y selección de payloads desde GitHub
- Envío de payloads por TCP o Socat
- Multi-idioma (cambio dinámico de idioma con banderas)
- Resolución automática de Socat con caché, PATH del sistema y URLs opcionales
- Configuración con pydantic-settings

## Novedad de la versión 1.0.0
- Sistema de estilos renovado usando QSS para una UI más consistente entre plataformas.
- Ajustes de pruebas para ejecución headless con Qt (`QT_QPA_PLATFORM=offscreen`).

## Instalación

1. Clona el repositorio y entra en la carpeta:
   ```sh
   git clone <repo-url>
   cd PsX-Payload-Multi-Injector
   ```
2. Instala las dependencias (requiere Python 3.8+). Puedes usar `uv` (más rápido) o `pip`:
   
   Con uv (recomendado):
   ```sh
   uv pip install -r requirements.txt
   ```
   O con pip:
   ```sh
   pip install -r requirements.txt
   ```
   Perfiles opcionales:
   ```sh
   # Testing (runtime + pytest)
   uv pip install -r requirements-test.txt

   # Desarrollo (runtime + test + flake8 + watchdog)
   uv pip install -r requirements-dev.txt
   ```
3. Ejecuta la aplicación:
   ```sh
   python src/main.py
   ```

## Estructura del proyecto
- `src/` — Código fuente principal
- `tests/` — Pruebas unitarias y de integración con mocks
- `requirements.txt` — Dependencias runtime para publicación/ejecutable
- `requirements-test.txt` — Runtime + dependencias de test
- `requirements-dev.txt` — Runtime + test + herramientas de desarrollo
- `README.md` — Este archivo

## Tests

La suite de pruebas vive en `tests/`.

- Activa tu entorno virtual e instala dependencias:
   ```sh
   source .venv/bin/activate
   pip install -r requirements-test.txt
   ```
- Ejecuta las pruebas:
   ```sh
   pytest tests
   ```

La suite usa imports de paquete (`src.*`). `tests/conftest.py` añade la raíz del proyecto al path durante la recolección de `pytest`, así que no necesitas exportar `PYTHONPATH`.

## Logs y Depuración

Cuando la aplicación falla (especialmente en el `.app`/`.exe` compilado), se escribe un archivo de log automáticamente:

| Plataforma | Ubicación del log |
|---|---|
| **macOS** | `~/Library/Logs/PS_MultiInjector/app.log` |
| **Windows** | `%APPDATA%\PS_MultiInjector\Logs\app.log` |
| **Linux** | `~/.local/share/PS_MultiInjector/logs/app.log` |

Leer el log tras un crash:

```bash
# macOS / Linux
cat ~/Library/Logs/PS_MultiInjector/app.log      # macOS
cat ~/.local/share/PS_MultiInjector/logs/app.log  # Linux

# Windows (PowerShell)
type "$env:APPDATA\PS_MultiInjector\Logs\app.log"
```

Cuando se ejecuta como bundle compilado (`PyInstaller`), `stdout` y `stderr` también se redirigen a este archivo, por lo que cualquier excepción no manejada aparecerá allí. En desarrollo (`uv run src/main.py`) el log se sigue escribiendo pero los errores también son visibles en la terminal.

## Dependencias

### Dependencias Runtime
- **Python 3.8+** (requerido)
- **PySide6** (framework GUI Qt para la interfaz)
- **socat** (opcional pero recomendado para inyección de payloads en PS4/PS5)
  - Sin socat: Solo disponible el método TCP para inyección de payloads
  - Con socat: Disponibles ambos métodos TCP y Socat para comunicación con PS4/PS5

### Instalando Socat

Socat es una dependencia opcional pero recomendada para inyección avanzada de payloads en PS4/PS5. La app detectará automáticamente su disponibilidad y desactivará el checkbox de Socat si no se encuentra.

**macOS (Intel y Apple Silicon)**
```bash
brew install socat
```

**Linux (Ubuntu/Debian)**
```bash
sudo apt install socat
```

**Linux (Fedora/RHEL)**
```bash
sudo dnf install socat
```

**Linux (Arch)**
```bash
sudo pacman -S socat
```

**Windows**
Cuatro opciones:
1. **WSL (Recomendado)** — Instala Windows Subsystem for Linux, luego usa los comandos Linux anteriores
2. **MSYS2/Cygwin** — Instala vía el gestor de paquetes
3. **scoop** — `scoop install socat`
4. **Binario manual** — Ver [SOCAT_MANUAL_SETUP.md](./docs/SOCAT_MANUAL_SETUP.md) para instrucciones detalladas por SO

### Instalación Manual del Binario

Para colocar manualmente el binario de socat en el directorio de la app, consulta [SOCAT_MANUAL_SETUP.md](./docs/SOCAT_MANUAL_SETUP.md) con instrucciones paso a paso para cada sistema operativo.

**Rutas rápidas:**
- **macOS:** `~/Library/Application Support/PS_MultiInjector/socat/`
- **Windows:** `%APPDATA%\PS_MultiInjector\socat\`
- **Linux:** `~/.local/share/PS_MultiInjector/socat/`

Si socat no se encuentra, la app:
- Mostrará un mensaje explicando cómo instalarlo
- Desactivará el checkbox "Activar SOCAT"
- Seguirá permitiendo inyección de payloads basada en TCP

## Uso de Socat para PS4/PS5

Socat proporciona un método alternativo a TCP para inyectar payloads en consolas PS4/PS5. Ofrece:
- Mejor confiabilidad para ciertas configuraciones de red
- Soporte para escenarios de enrutamiento complejo
- Capacidades avanzadas de manipulación de sockets

La app detecta automáticamente la disponibilidad de socat:
- Si se encuentra: El checkbox "Activar SOCAT" está activo
- Si no se encuentra: El checkbox está desactivado con instrucciones de instalación mostradas

## Resolución de Socat (Técnico)

El orden de resolución de Socat es:
1. Binario en caché dentro del directorio de datos del usuario.
2. Binario del sistema encontrado en `PATH`.
3. Descarga desde URL configurada (solo cuando hay una fuente válida/configurada).

Fuentes validadas y comportamiento actual:

| Plataforma | Arquitectura | Comportamiento por defecto |
|---|---|---|
| macOS | arm64 / x86_64 | Usar `socat` del sistema con Homebrew (`brew install socat`) |
| Linux | x86_64 | Soporta auto-descarga (URL por defecto), o usar `socat` del sistema |
| Linux | arm64 | Usar paquete de la distro (`apt`, `dnf`, `pacman`) |
| Windows | x86_64 | Usar `socat` del sistema (MSYS2/Cygwin), o definir `SOCAT_WIN_URL` en `.env` |
| Windows | arm64 | Usar binario del sistema/gestor de paquetes o URL interna personalizada |

Notas:
- Las URLs públicas antiguas de static-binaries para macOS y Windows ya no son fiables, por eso no se usan por defecto.
- Puedes sobrescribir URLs por `.env` si controlas una fuente binaria confiable.
- Los binarios de Socat en caché se guardan en el directorio de datos del usuario (no dentro del bundle de la app).
- Las operaciones de Socat tienen un timeout configurable (por defecto: 30 segundos) para inyección de payloads en PS4/PS5.

## Notas
- El selector de idioma usa banderas Unicode reales gracias al paquete `open_flags` (no requiere imágenes locales).
- Puedes agregar más idiomas creando archivos JSON en `src/lang`.
- Requiere conexión a internet para descargar la lista de payloads y cualquier binario de Socat obtenido externamente.
- La lista de payloads debe estar en formato JSON con secciones `PS4` y/o `PS5`.
- Antes de enviar, la app valida el formato de IP y el rango de puerto (1-65535). Tanto la carga inicial de payloads como los envíos se ejecutan en segundo plano para mantener la interfaz fluida.

## Cómo agregar un nuevo idioma

El selector de idioma detecta automáticamente los archivos `*.json` en `src/lang`, por lo que no necesitas añadir listas hardcodeadas en el código para idiomas nuevos.

Pasos recomendados:

1. Crea un nuevo archivo de traducción con formato locale en minúsculas, por ejemplo:
   - `src/lang/fr-fr.json`
   - `src/lang/ja-jp.json`
2. Copia todas las claves existentes desde `src/lang/en-us.json` (o `src/lang/es-es.json`) y traduce solo los valores.
3. Mantén las claves en `snake_case` y no elimines ninguna.
4. Ejecuta tests para validar paridad de claves:
   ```sh
   python -m pytest tests/test_config_and_lang.py -v
   ```
5. Reinicia la app: el nuevo idioma aparecerá automáticamente en el selector.

Notas:
- El nombre del archivo define el locale mostrado (`en-us`, `es-es`, etc.).
- La bandera se resuelve desde el país del locale (`us`, `es`, `jp`, etc.).
- La configuración de idioma usa locales completos (`xx-yy`). No se mantienen aliases de código base (`en`, `es`, etc.).

## Uso de `uv` y `watchdog` para desarrollo

Para un flujo de desarrollo moderno y rápido, puedes usar `uv` para instalar dependencias y ejecutar la app, y `watchdog` (con `watchmedo`) para autorecargar la aplicación al guardar cambios en los archivos Python.

1. Instala dependencias con uv:
   ```sh
   uv pip install -r requirements-dev.txt
   ```
2. Ejecuta la app normalmente:
   ```sh
   uv run src/main.py
   ```
3. Para desarrollo con autoreload (recarga automática al guardar):
   ```sh
   watchmedo auto-restart --pattern="*.py" --recursive -- uv run src/main.py
   ```

Esto reiniciará la app cada vez que modifiques cualquier archivo `.py` en el proyecto.

## Generar ejecutables nativos

Puedes generar un ejecutable para tu sistema operativo localmente usando los scripts en `build_local/`:

- **Linux, macOS o Windows:**
   ```sh
   python build_local/build_local.py
   ```

Esto generará un ejecutable en la carpeta `dist/` con el nombre y versión correspondiente a tu arquitectura y sistema. Debes ejecutar el script en cada plataforma para obtener el binario nativo de esa arquitectura (no se generan binarios universales).


## Agradecimientos

- [MaNu (TheWizWikii)](https://github.com/TheWizWikii)
