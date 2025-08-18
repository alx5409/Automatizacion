import os
import sys

if getattr(sys, 'frozen', False):
    # Ejecución como ejecutable (.exe), por ejemplo, creado con PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Ejecución como script (.py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def cargar_variables(filepath):
    strings = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    strings[key.strip()] = value.strip()
    return strings