

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
from typing import List, Optional


# =========================
# MODELO
# =========================
@dataclass(frozen=True)
class ScriptItem:
    """
    Representa un script Python como un objeto.
    Antes: el script era un string.
    Mejora: ahora es una entidad con comportamiento.
    """
    path: Path

    @property
    def name(self) -> str:
        return self.path.name


# =========================
# REPOSITORIO
# =========================
class ScriptRepository:
    """
    Responsable SOLO de acceder al sistema de archivos.
    Mejora: se separa la lógica de exploración del menú y la UI.
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def get_unidades(self) -> List[Path]:
        """Obtiene las carpetas principales (Unidades)."""
        if not self.base_dir.exists():
            return []
        return sorted([p for p in self.base_dir.iterdir() if p.is_dir()])

    def get_subcarpetas(self, unidad_dir: Path) -> List[Path]:
        """Obtiene las subcarpetas de una unidad."""
        if not unidad_dir.exists():
            return []
        return sorted([p for p in unidad_dir.iterdir() if p.is_dir()])

    def get_scripts(self, carpeta_dir: Path) -> List[ScriptItem]:
        """
        Obtiene los scripts .py y los devuelve como objetos.
        Mejora: devuelve objetos, no strings.
        """
        if not carpeta_dir.exists():
            return []

        scripts = [
            p for p in carpeta_dir.iterdir()
            if p.is_file() and p.suffix == ".py"
        ]
        return [ScriptItem(p) for p in sorted(scripts)]


# =========================
# VISOR DE CÓDIGO
# =========================
class ScriptViewer:
    """
    Responsable SOLO de leer y mostrar el código.
    Mejora: lectura de archivos desacoplada del menú.
    """

    def show(self, script_path: Path) -> Optional[str]:
        try:
            code = script_path.read_text(encoding="utf-8")
            print(f"\n--- Código de {script_path.name} ---\n")
            print(code)
            return code
        except FileNotFoundError:
            print("Archivo no encontrado.")
        except UnicodeDecodeError:
            print("Error de codificación al leer el archivo.")
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
        return None


# =========================
# EJECUTOR
# =========================
class ScriptRunner:
    """
    Responsable SOLO de ejecutar scripts.
    Mejora: usa el mismo intérprete de Python del dashboard.
    """

    def __init__(self) -> None:
        self.python = sys.executable

    def run(self, script_path: Path) -> None:
        try:
            subprocess.run([self.python, str(script_path)], check=False)
        except Exception as e:
            print(f"Error al ejecutar el script: {e}")


# =========================
# INTERFAZ DE USUARIO
# =========================
class MenuUI:
    """
    Responsable SOLO de mostrar menús y pedir opciones.
    Mejora: menús reutilizables.
    """

    def show_menu(self, title: str, options: List[str], extra: List[str]) -> str:
        print(f"\n{title}")
        for i, opt in enumerate(options, start=1):
            print(f"{i} - {opt}")
        for line in extra:
            print(line)
        return input("Seleccione una opción: ").strip()


# =========================
# APLICACIÓN PRINCIPAL
# =========================
class DashboardApp:
    """
    Controlador principal del programa.
    Mejora: orquesta las clases sin mezclar responsabilidades.
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
                print("No se encontraron unidades.")
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
                print("No hay scripts en esta carpeta.")
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

            script = scripts[idx].path
            if self.viewer.show(script):
                if input("¿Ejecutar? (1=Sí / 0=No): ") == "1":
                    self.runner.run(script)

            input("\nPresiona Enter para continuar...")

    @staticmethod
    def _to_index(choice: str, size: int) -> Optional[int]:
        """Convierte la opción del usuario a un índice seguro."""
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
    base_dir = Path(__file__).resolve().parent
    app = DashboardApp(base_dir)
    app.run()
