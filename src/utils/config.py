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

# Configuración de fechas
AÑOS_VIGENCIA_CONTRATO = 5
AÑOS_VIGENCIA_CONTRATO_CORTO = 3

# Empresas por defecto
EMPRESA_DESTINO_DEFAULT = "METALLS DEL CAMP, S.L."
OPERADOR_TRASLADOS_DEFAULT = "ECO TITAN S.L."

# Autorizaciones por defecto
AUTORIZACIONES = {
    "valencia_peligroso": "157/G02/CV",
    "valencia_no_peligroso": "374/G04/CV",
    "otros_peligroso": "4570002919",
    "otros_no_peligroso": "G04"
}