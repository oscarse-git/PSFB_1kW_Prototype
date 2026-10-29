from pathlib import Path
import shutil

# Carpeta que contiene todas las librerías
ROOT = Path(r'C:\Users\oscar\Desktop\Uni\Master Advanced Power Electronics\Semester 3\PBL-PSFB_1kW\PSFB_PCB\Components')

# Carpetas que queremos conservar
KEEP = {"kicad", "kicadv6", "3d"}

for component in ROOT.iterdir():
    if not component.is_dir():
        continue

    # Buscar recursivamente las carpetas KiCad
    for folder in component.rglob("*"):
        if folder.is_dir() and folder.name.lower() in KEEP:
            continue

    # Eliminar carpetas no deseadas, conservando la estructura
    def clean(folder):
        for subfolder in list(folder.iterdir()):
            if not subfolder.is_dir():
                continue

            if subfolder.name.lower() in KEEP:
                continue

            # Si contiene carpetas KiCad, limpiar su interior
            if any(
                p.is_dir() and p.name.lower() in KEEP
                for p in subfolder.rglob("*")
            ):
                clean(subfolder)
            else:
                print(f"Eliminando: {subfolder}")
                shutil.rmtree(subfolder)

    clean(component)

print("Limpieza completada.")