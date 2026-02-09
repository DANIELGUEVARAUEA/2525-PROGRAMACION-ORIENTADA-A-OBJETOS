import os
import subprocess
import sys
from pathlib import Path


# :MEJORA 1: Use pathlib para manejar rutas de forma más segura y multiplataforma.
# :MEJORA 2:  estructuramos mejor con constantes y funciones pequeñas.
BASE_DIR = Path(__file__).resolve().parent


def leer_codigo(ruta_script: Path) -> str | None:
    # :MEJORA 3:el archivo con encoding='utf-8' para evitar los errores con tildes/ñ.
    # :MEJORA 4: Validando para que realmente sea un archivo antes de abrirlo.
    try:
        if not ruta_script.is_file():
            print("El archivo no existe o no es un archivo válido.")
            return None

        with ruta_script.open("r", encoding="utf-8") as archivo:
            return archivo.read()

    except Exception as e:
        # :MEJORA 5: Mensaje de error más informativo y centralizado.
        print(f"Ocurrió un error al leer el archivo: {e}")
        return None


def mostrar_codigo(ruta_script: Path) -> bool:
    # :MEJORA 6: Separación de responsabilidades:
    #           leer_codigo() lee, mostrar_codigo() imprime y decide si fue exitoso.
    codigo = leer_codigo(ruta_script)
    if codigo is None:
        return False

    print(f"\n--- Código de {ruta_script.name} ---\n")
    print(codigo)
    return True


def ejecutar_codigo(ruta_script: Path) -> None:
    # :MEJORA 7: Ejecutamos con el mismo intérprete de Python que corre este dashboard (sys.executable),
    #           así evitamos problemas de "python" vs "python3" o entornos virtuales.
    try:
        python_exe = sys.executable

        # :MEJORA 8: Abrimos una nueva terminal según el sistema operativo, de forma más clara.
        if os.name == "nt":  # Windows
            # Abre CMD y deja la ventana abierta (/k)
            subprocess.Popen(["cmd", "/k", python_exe, str(ruta_script)])
        else:
            # :MEJORA 9: Intentamos varias terminales comunes en Linux/Mac.
            #           Si no hay terminal disponible, ejecutamos en la misma consola.
            terminales = [
                ["xterm", "-hold", "-e"],
                ["gnome-terminal", "--"],
                ["konsole", "-e"],
                ["mate-terminal", "-e"],
                ["xfce4-terminal", "-e"],
            ]

            for t in terminales:
                try:
                    subprocess.Popen(t + [python_exe, str(ruta_script)])
                    return
                except FileNotFoundError:
                    continue

            # Si no se encontró una terminal gráfica, ejecuta en la consola actual
            # (esto funciona en cualquier Unix si estás en una terminal ya abierta).
            subprocess.run([python_exe, str(ruta_script)], check=False)

    except Exception as e:
        print(f"Ocurrió un error al ejecutar el código: {e}")


def pedir_opcion(mensaje: str) -> str:
    # :MEJORA 10: Función para pedir input y limpiar espacios, evita errores por entradas con espacios.
    return input(mensaje).strip()


def listar_carpetas(ruta: Path) -> list[Path]:
    # :MEJORA 11: Listado ordenado alfabéticamente para que el menú sea consistente.
    return sorted([p for p in ruta.iterdir() if p.is_dir()], key=lambda x: x.name.lower())


def listar_scripts_py(ruta: Path) -> list[Path]:
    # :MEJORA 12: Listado ordenado de scripts .py
    return sorted([p for p in ruta.iterdir() if p.is_file() and p.suffix == ".py"], key=lambda x: x.name.lower())


def mostrar_menu():
    # :MEJORA 13: Mantenemos un diccionario claro para unidades, pero con rutas reales.
    unidades = {
        "1": BASE_DIR / "Unidad 1",
        "2": BASE_DIR / "Unidad 2",
    }

    while True:
        print("\nMenu Principal - Dashboard")
        for key, ruta in unidades.items():
            print(f"{key} - {ruta.name}")
        print("0 - Salir")

        eleccion = pedir_opcion("Elige una unidad o '0' para salir: ")

        if eleccion == "0":
            print("Saliendo del programa.")
            return

        if eleccion not in unidades:
            print("Opción no válida. Por favor, intenta de nuevo.")
            continue

        ruta_unidad = unidades[eleccion]

        # :MEJORA 14: Validamos existencia de la carpeta unidad antes de entrar.
        if not ruta_unidad.exists():
            print(f"No existe la carpeta: {ruta_unidad}")
            continue

        mostrar_sub_menu(ruta_unidad)


def mostrar_sub_menu(ruta_unidad: Path):
    sub_carpetas = listar_carpetas(ruta_unidad)

    # :MEJORA 15: Si no hay subcarpetas, avisamos en lugar de mostrar un menú vacío.
    if not sub_carpetas:
        print(f"\nNo hay subcarpetas dentro de: {ruta_unidad.name}")
        return

    while True:
        print(f"\nSubmenú - {ruta_unidad.name}")
        for i, carpeta in enumerate(sub_carpetas, start=1):
            print(f"{i} - {carpeta.name}")
        print("0 - Regresar al menú principal")

        eleccion = pedir_opcion("Elige una subcarpeta o '0' para regresar: ")

        if eleccion == "0":
            return

        # :MEJORA 16: Validación de número sin reventar el programa.
        if not eleccion.isdigit():
            print("Opción no válida. Debes ingresar un número.")
            continue

        idx = int(eleccion) - 1
        if not (0 <= idx < len(sub_carpetas)):
            print("Opción no válida. Por favor, intenta de nuevo.")
            continue

        mostrar_scripts(sub_carpetas[idx])


def mostrar_scripts(ruta_sub_carpeta: Path):
    while True:
        scripts = listar_scripts_py(ruta_sub_carpeta)

        print(f"\nScripts - {ruta_sub_carpeta.name}")
        if not scripts:
            # :MEJORA 17: Si no hay scripts, lo informamos.
            print("No hay scripts .py en esta carpeta.")
            print("0 - Regresar al submenú anterior")
            eleccion = pedir_opcion("Elige '0' para regresar: ")
            if eleccion == "0":
                return
            continue

        for i, script in enumerate(scripts, start=1):
            print(f"{i} - {script.name}")

        print("0 - Regresar al submenú anterior")
        print("9 - Regresar al menú principal")

        eleccion = pedir_opcion("Elige un script, '0' para regresar o '9' para menú principal: ")

        if eleccion == "0":
            return
        if eleccion == "9":
            # :MEJORA 18: Retornamos para volver al menú principal sin romper el flujo.
            return

        if not eleccion.isdigit():
            print("Opción no válida. Debes ingresar un número.")
            continue

        idx = int(eleccion) - 1
        if not (0 <= idx < len(scripts)):
            print("Opción no válida. Por favor, intenta de nuevo.")
            continue

        ruta_script = scripts[idx]
        ok = mostrar_codigo(ruta_script)

        if ok:
            ejecutar = pedir_opcion("¿Desea ejecutar el script? (1: Sí, 0: No): ")
            if ejecutar == "1":
                ejecutar_codigo(ruta_script)
            elif ejecutar == "0":
                print("No se ejecutó el script.")
            else:
                print("Opción no válida. Regresando al menú de scripts.")

        input("\nPresiona Enter para volver al menú de scripts.")


# Ejecutar el dashboard
if __name__ == "__main__":
    # :MEJORA 19: Punto de entrada claro, solo llama al menú principal.
    mostrar_menu()
