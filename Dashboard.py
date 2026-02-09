from __future__ import annotations

# :MEJORA 1: Quite imports duplicados y deje solo lo necesario.
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


# :MEJORA 2: Base dir consistente y multiplataforma.
BASE_DIR = Path(__file__).resolve().parent


# =========================
# MODELO
# =========================
@dataclass(frozen=True)
class ScriptItem:
    """
    Representa un script Python como un objeto.
    #:MEJORA 3: Pasamos de strings a objetos (mejor OOP y mantenimiento).
    """
    path: Path

    @property
    def name(self) -> str:
        return self.path.name


# =========================
# REPOSITORIO (Filesystem)
# =========================
class ScriptRepository:
    """
    Responsable SOLO de acceder al sistema de archivos.
    #:MEJORA 4: Separación de las responsabilidades (SRP).
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def get_unidades(self) -> List[Path]:
        # #:MEJORA 5: Validamos existencia y ordenamos alfabéticamente.
        if not self.base_dir.exists():
            return []
        return sorted([p for p in self.base_dir.iterdir() if p.is_dir()],
                      key=lambda x: x.name.lower())

    def get_subcarpetas(self, unidad_dir: Path) -> List[Path]:
        if not unidad_dir.exists():
            return []
        return sorted([p for p in unidad_dir.iterdir() if p.is_dir()],
                      key=lambda x: x.name.lower())

    def get_scripts(self, carpeta_dir: Path) -> List[ScriptItem]:
        if not carpeta_dir.exists():
            return []

        scripts = sorted(
            [p for p in carpeta_dir.iterdir() if p.is_file() and p.suffix == ".py"],
            key=lambda x: x.name.lower()
        )
        return [ScriptItem(p) for p in scripts]


# =========================
# VISOR DE CÓDIGO
# =========================
class ScriptViewer:
    """
    Responsable SOLO de leer y mostrar el código.
    """

    def show(self, script_path: Path) -> Optional[str]:
        # #:MEJORA 6: Leemos con UTF-8 para evitar los errores con tildes/ñ.
        try:
            if not script_path.is_file():
                print("Archivo no encontrado.")
                return None

            code = script_path.read_text(encoding="utf-8")
            print(f"\n--- Código de {script_path.name} ---\n")
            print(code)
            return code

        except UnicodeDecodeError:
            print("Error de codificación al leer el archivo (no es UTF-8).")
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
        return None


# =========================
# EJECUTOR
# =========================
class ScriptRunner:
    """
    Responsable SOLO de ejecutar scripts.
    """

    def __init__(self) -> None:
        # #:MEJORA 7: Usamos el mismo Python que ejecuta este dashboard.
        self.python = sys.executable

    def run(self, script_path: Path) -> None:
        try:
            # #:MEJORA 8: Ejecutamos en terminal aparte si se puede (Windows),
            #            y si no, ejecutamos en la misma consola.
            if os.name == "nt":
                subprocess.Popen(["cmd", "/k", self.python, str(script_path)])
            else:
                subprocess.run([self.python, str(script_path)], check=False)

        except Exception as e:
            print(f"Error al ejecutar el script: {e}")


# =========================
# INTERFAZ DE USUARIO
# =========================
class MenuUI:
    """
    Responsable SOLO de mostrar menús y pedir opciones.
    """

    def show_menu(self, title: str, options: List[str], extra: List[str]) -> str:
        print(f"\n{title}")
        for i, opt in enumerate(options, start=1):
            print(f"{i} - {opt}")
        for line in extra:
            print(line)
        # #:MEJORA 9: strip() para evitar problemas por espacios.
        return input("Seleccione una opción: ").strip()


# =========================
# APLICACIÓN PRINCIPAL
# =========================
class DashboardApp:
    """
    Controlador principal del programa.
    """

    def __init__(self, base_dir: Path) -> None:
        self.repo = ScriptRepository(base_dir)
        self.viewer = ScriptViewer()
        self.runner = ScriptRunner()
        self.ui = MenuUI()

    def run(self) -> None:
        while True:
            unidades = self.repo.get_unidades()
            if not unidades:
                print("No se encontraron carpetas (unidades) en la ruta base.")
                print(f"Ruta base actual: {self.repo.base_dir}")
                return

            choice = self.ui.show_menu(
                "Menú Principal - Dashboard",
                [u.name for u in unidades],
                ["0 - Salir"]
            )

            if choice == "0":
                print("Saliendo del programa.")
                return

            idx = self._to_index(choice, len(unidades))
            if idx is None:
                print("Opción inválida.")
                continue

            self._unidad_menu(unidades[idx])

    def _unidad_menu(self, unidad_dir: Path) -> None:
        while True:
            sub = self.repo.get_subcarpetas(unidad_dir)
            if not sub:
                print(f"No hay subcarpetas dentro de: {unidad_dir.name}")
                return

            choice = self.ui.show_menu(
                f"Unidad: {unidad_dir.name}",
                [s.name for s in sub],
                ["0 - Regresar"]
            )

            if choice == "0":
                return

            idx = self._to_index(choice, len(sub))
            if idx is None:
                print("Opción inválida.")
                continue

            self._scripts_menu(sub[idx])

    def _scripts_menu(self, carpeta_dir: Path) -> None:
        while True:
            scripts = self.repo.get_scripts(carpeta_dir)
            if not scripts:
                print("No hay scripts .py en esta carpeta.")
                return

            choice = self.ui.show_menu(
                f"Scripts en {carpeta_dir.name}",
                [s.name for s in scripts],
                ["0 - Regresar"]
            )

            if choice == "0":
                return

            idx = self._to_index(choice, len(scripts))
            if idx is None:
                print("Opción inválida.")
                continue

            script_path = scripts[idx].path
            if self.viewer.show(script_path):
                if input("¿Ejecutar? (1=Sí / 0=No): ").strip() == "1":
                    self.runner.run(script_path)

            input("\nPresiona Enter para continuar...")

    @staticmethod
    def _to_index(choice: str, size: int) -> Optional[int]:
        # #:MEJORA 10: Conversión segura de opción a índice.
        try:
            idx = int(choice) - 1
            if 0 <= idx < size:
                return idx
        except ValueError:
            pass
        return None


# =========================
# PUNTO DE ENTRADA
# =========================
if __name__ == "__main__":
    # #:MEJORA 11: Solo un entrypoint (sin duplicados ni conflictos).
    app = DashboardApp(BASE_DIR)
    app.run()
