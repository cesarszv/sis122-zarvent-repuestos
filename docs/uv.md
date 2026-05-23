# UV en este proyecto

`uv` es la herramienta oficial del proyecto para manejar Python. En este repo
reemplaza los pasos manuales de crear entorno virtual, instalar dependencias y
recordar que ejecutable de Python usar.

## Por que usamos UV

Elegimos `uv` porque el proyecto debe poder ejecutarse rapido en mas de un
equipo sin perder tiempo configurando Python a mano.

| Razon | Que aporta al proyecto |
| --- | --- |
| Un solo comando de instalacion | `uv sync` prepara el entorno desde `pyproject.toml` y `uv.lock`. |
| Reproducibilidad | `uv.lock` deja registradas las versiones resueltas. |
| Menos pasos manuales | No hay que activar un entorno antes de cada comando. |
| Misma idea en Linux, MacOS y Windows | Cambia la terminal, no cambia el flujo del proyecto. |
| Buen ajuste para estudiantes junior | Se memoriza `uv sync` y `uv run`, no una cadena larga de comandos. |

No se eligio para hacer el proyecto "mas avanzado". Se eligio para reducir
errores de entorno y concentrar la defensa en MySQL y el modelo relacional.

## Archivos que usa UV

| Archivo | Funcion |
| --- | --- |
| `pyproject.toml` | Declara el nombre del proyecto, version de Python y dependencias. |
| `uv.lock` | Guarda las versiones exactas que `uv` resolvio. |
| `.python-version` | Indica la version de Python que debe usar el proyecto. |
| `.venv/` | Entorno local creado por `uv`. No se sube a Git. |

`.venv/` sigue existiendo, pero no lo creamos manualmente. Lo administra `uv`.

## Como funciona

`uv sync` hace tres cosas:

1. Lee `pyproject.toml`.
2. Usa `uv.lock` como referencia de dependencias.
3. Crea o actualiza `.venv/` con lo necesario para ejecutar el proyecto.

`uv run` ejecuta un comando dentro del entorno del proyecto:

```bash
uv run python scripts/development/check_python_environment.py
```

Eso evita activar el entorno manualmente. El comando ya sabe usar el Python y
las librerias del proyecto.

## Instalar UV

### Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Si no tienes `curl`:

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
uv --version
```

### MacOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Alternativa con Homebrew:

```bash
brew install uv
uv --version
```

### Windows

En PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

Si `uv` no aparece, cierra y abre la terminal.

## Primer uso del proyecto

### Linux

```bash
uv python install 3.14
uv sync
uv run python scripts/development/check_python_environment.py
```

### MacOS

```bash
uv python install 3.14
uv sync
uv run python scripts/development/check_python_environment.py
```

### Windows

```powershell
uv python install 3.14
uv sync
uv run python scripts\development\check_python_environment.py
```

## Comandos frecuentes

| Comando | Para que sirve |
| --- | --- |
| `uv --version` | Verifica que `uv` esta instalado. |
| `uv python install 3.14` | Instala la version de Python usada por el repo. |
| `uv sync` | Prepara o actualiza el entorno del proyecto. |
| `uv run python <archivo>` | Ejecuta un script con el entorno del proyecto. |
| `uv run python -m <modulo>` | Ejecuta un modulo de Python del proyecto. |
| `uv lock` | Actualiza el archivo `uv.lock` si cambian dependencias. |

## Como ejecutar la app

### Linux

```bash
uv run python -m zarvent_repuestos.interfaces.web.app
```

### MacOS

```bash
uv run python -m zarvent_repuestos.interfaces.web.app
```

### Windows

```powershell
uv run python -m zarvent_repuestos.interfaces.web.app
```

## Como instalar una nueva dependencia

Si el equipo decide agregar una libreria, no se edita `uv.lock` a mano.

### Linux

```bash
uv add nombre-paquete
uv sync
```

### MacOS

```bash
uv add nombre-paquete
uv sync
```

### Windows

```powershell
uv add nombre-paquete
uv sync
```

Esto actualiza `pyproject.toml` y `uv.lock`.

## Que no hacemos

En este proyecto no documentamos un segundo flujo con instalacion manual de
dependencias o activacion manual de entornos. Pueden servir en otros proyectos,
pero aqui agregan variacion innecesaria.

Nuestro flujo oficial es:

```text
uv sync
uv run ...
```

## Fuentes

- Documentacion oficial de `uv`: <https://docs.astral.sh/uv/>
- Instalacion oficial: <https://docs.astral.sh/uv/getting-started/installation/>
- Locking y syncing: <https://docs.astral.sh/uv/concepts/projects/sync/>
- Python con `uv`: <https://docs.astral.sh/uv/guides/install-python/>
