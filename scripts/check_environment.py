import importlib
import sys


REQUIRED_MODULES = [
    ("bcrypt", "bcrypt"),
    ("flask", "flask"),
    ("mysql.connector", "mysql-connector-python"),
    ("dotenv", "python-dotenv"),
]


def main():
    print(f"Python: {sys.version.split()[0]}")

    missing = []

    for module_name, package_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
            print(f"OK: {package_name}")
        except ImportError:
            print(f"FALTA: {package_name}")
            missing.append(package_name)

    if missing:
        print()
        print("Instala las dependencias antes de ejecutar el proyecto.")
        print("Python nativo: py -m pip install -r requirements.txt")
        print("UV: uv sync")
        return 1

    print()
    print("Entorno listo para ejecutar el codigo Python del proyecto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
