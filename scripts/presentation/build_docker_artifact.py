"""Build script: regenera `presentation/source/` desde la raiz del repo.

Este script es el puente entre el codigo fuente versionado en git y
el artefacto Docker que se copia al USB para la defensa. La idea es
mantener una sola fuente de verdad (el repo) y producir el artefacto
de forma automatica y repetible.

Uso:

    uv run python scripts/presentation/build_docker_artifact.py

Que hace:

1. Detecta la raiz del repo a partir de la ubicacion del propio
   script (`scripts/presentation/` -> raiz).
2. Borra y recrea `presentation/source/` vacio.
3. Copia todo el contenido del repo a `presentation/source/`,
   excluyendo solo caches y basura temporal (ver EXCLUDED_PATTERNS).
4. Se incluyen `.env`, `.gitignore`, `presentation/spec/`, etc. a
   proposito: el artefacto debe ser autosuficiente y reflejar el
   estado real del repo en el momento de la defensa.

El script es idempotente: cada ejecucion reemplaza
`presentation/source/` desde cero. No toca el resto de
`presentation/` (docker-compose.yml, Dockerfile.web, etc).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


# Directorios y archivos que NO se copian al artefacto. Lista chica
# y conservadora: solo caches y basura temporal. Se incluyen los
# `.env`, `.gitignore`, `pyproject.toml`, `uv.lock`, `tests/`, `docs/`,
# `spec/`, etc. a proposito, para que la defensa tenga el contexto
# completo.
EXCLUDED_PATTERNS = (
    # Control de versiones
    ".git",
    # Entornos virtuales
    ".venv",
    # Caches de Python
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    # Caches de herramientas
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    # Empaquetado
    "*.egg-info",
    # Auto-referencia: evita recursion al regenerar el artefacto.
    # El segmento `source` aparece en `presentation/source/...`
    "source",
    # Configuracion local del dev (basura para el artefacto)
    ".idea",
    ".vscode",
    ".cszv",
    ".agents",
    "skills-lock.json",
    "sis122-finalproject.code-workspace",
    # Symlinks a AGENTS.md (duplicarian contenido)
    "CLAUDE.md",
    "GEMINI.md",
)


# Confirmaciones minimas que el script imprime al final. Si alguna
# falta, el dev debe investigar antes de usar el artefacto.
REQUIRED_ENTRIES = (
    "pyproject.toml",
    "uv.lock",
    ".python-version",
    "src",
    "scripts",
    "database",
    "docs",
    "README.md",
)


def _repo_root() -> Path:
    """Devuelve la raiz del repo a partir de la ubicacion del script.

    El script vive en `<repo>/scripts/presentation/`. La raiz esta
    dos niveles arriba.
    """
    return Path(__file__).resolve().parents[2]


def _presentation_dir(repo_root: Path) -> Path:
    return repo_root / "presentation"


def _source_dir(presentation_dir: Path) -> Path:
    return presentation_dir / "source"


def _should_skip_extension(path: Path) -> bool:
    """Filtro adicional para extensiones de archivos (no segmentos)."""
    suffix_patterns = (".pyc", ".pyo", ".pyd")
    return any(path.name.endswith(suffix) for suffix in suffix_patterns)


def _copy_repo_to_source(repo_root: Path, source_dir: Path) -> int:
    """Copia `repo_root` a `source_dir` aplicando las exclusiones.

    Devuelve la cantidad de archivos copiados.
    """
    copied = 0
    for src_path in sorted(repo_root.rglob("*")):
        if src_path == repo_root:
            continue
        if not src_path.exists():
            continue
        if src_path.is_dir():
            continue
        rel = src_path.relative_to(repo_root)
        # Filtro por segmento (componentes de path)
        if any(part in EXCLUDED_PATTERNS for part in rel.parts):
            continue
        # Filtro por extension
        if _should_skip_extension(src_path):
            continue
        dest = source_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest)
        copied += 1
    return copied


def _verify_required(source_dir: Path) -> list[str]:
    """Devuelve la lista de entradas requeridas que faltan."""
    missing: list[str] = []
    for entry in REQUIRED_ENTRIES:
        if not (source_dir / entry).exists():
            missing.append(entry)
    return missing


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenera presentation/source/ desde la raiz del repo.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra que se haria sin modificar archivos.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    repo_root = _repo_root()
    presentation_dir = _presentation_dir(repo_root)
    source_dir = _source_dir(presentation_dir)

    if not (repo_root / "pyproject.toml").exists():
        print(f"❌ No se encontro pyproject.toml en {repo_root}.")
        print("   Este script debe correr desde la raiz del repo.")
        return 1

    print(f"📁 Repo root:       {repo_root}")
    print(f"📁 Presentation:    {presentation_dir}")
    print(f"📁 Source destino:  {source_dir}")

    if source_dir.exists():
        if args.dry_run:
            print(f"🔍 [dry-run] Borraria {source_dir} y lo recrearia.")
        else:
            print(f"🧹 Borrando {source_dir}...")
            shutil.rmtree(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("🔍 [dry-run] Copiaria el repo aplicando exclusiones.")
        print(f"🔍 [dry-run] Exclusiones: {EXCLUDED_PATTERNS}")
        return 0

    copied = _copy_repo_to_source(repo_root, source_dir)
    print(f"📋 {copied} archivos copiados a {source_dir}.")

    missing = _verify_required(source_dir)
    if missing:
        print(f"❌ Faltan entradas requeridas: {missing}")
        return 1

    print("✅ Artefacto regenerado correctamente.")
    print(f"   Revisar: ls -la {source_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
