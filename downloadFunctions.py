import logging
from config import BASE_DIR
import loggerConfig
import os
import json
import time
from selenium import webdriver

import webConfiguration
import webFunctions

WEB = "https://ash-speed.hetzner.com/"

def ensure_download_path(path: str) -> str:
    """Crea el directorio si no existe y devuelve la ruta absoluta."""
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)

def configure_driver_download_path(driver: webdriver.Chrome, download_path: str):
    """Configura un driver existente para descargar en el path dado."""
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {
            "behavior": "allow",
            "downloadPath": os.path.abspath(download_path)
        }
    }
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params["params"])

def snapshot_folder_state(path: str) -> dict:
    """
    Devuelve un snapshot del estado actual de los archivos válidos en el directorio de descargas.
    Solo incluye archivos que no sean temporales ni .htm.
    """
    files = [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
        and not f.endswith('.crdownload')
        and not f.endswith('.htm')
    ]
    state = {
        "path": os.path.abspath(path),
        "files": sorted(files)
    }
    return state

def save_snapshot(snapshot: dict, filename: str):
    """Guarda el snapshot en un JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=4)

def load_snapshot(filename: str) -> dict:
    """Carga un snapshot desde un JSON."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def detect_new_file(old_state: dict, new_state: dict) -> str | None:
    """Devuelve el nombre del archivo nuevo si lo hay (ignorando crdownload)."""
    old_files = set(old_state["files"])
    new_files = set(f for f in new_state["files"] if not f.endswith('.crdownload') and not f.endswith('.htm'))
    new_entries = new_files - old_files
    return next(iter(new_entries), None)

def wait_for_new_download(download_path: str, old_state: dict, num_descargas: int = 1, timeout: int = 7200) -> list:
    """
    Espera hasta detectar el número de archivos nuevos indicados (ignorando .crdownload y .htm) o agotar el tiempo.
    Si un archivo descargado tiene el mismo nombre que uno existente, detecta también los renombrados (nombre (1).pdf, etc).
    Devuelve la lista de nombres de archivos nuevos detectados (con nombres únicos).
    """
    archivos_detectados = set()
    old_files_set = set(old_state["files"])
    old_files_mtime = {}
    for f in old_state["files"]:
        ruta = os.path.join(download_path, f)
        if os.path.exists(ruta):
            old_files_mtime[f] = os.path.getmtime(ruta)
    checked_files = set()

    for _ in range(timeout):
        time.sleep(1)
        new_state = snapshot_folder_state(download_path)
        # Archivos válidos (sin .crdownload ni .htm)
        valid_files = [f for f in new_state["files"] if not f.endswith('.crdownload') and not f.endswith('.htm')]

        # Detectar archivos realmente nuevos
        nuevos = set(valid_files) - old_files_set
        archivos_detectados.update(nuevos)

        # Detectar archivos renombrados por el navegador (nombre (1).pdf, nombre (2).pdf, ...)
        for archivo in valid_files:
            if archivo in checked_files:
                continue
            ruta = os.path.join(download_path, archivo)
            # Si el archivo existía antes, pero ha cambiado su fecha de modificación, es una nueva descarga
            if archivo in old_files_set:
                try:
                    if os.path.getmtime(ruta) > old_files_mtime.get(archivo, 0):
                        archivos_detectados.add(archivo)
                        checked_files.add(archivo)
                except Exception:
                    continue
            # Si es un archivo con patrón nombre (n).ext y no estaba antes, también lo añadimos
            elif any(
                archivo.startswith(base_name[:-len(ext)]) and archivo.endswith(ext)
                for base_name in old_files_set
                for ext in [os.path.splitext(base_name)[1]]
            ):
                archivos_detectados.add(archivo)
                checked_files.add(archivo)

        if len(archivos_detectados) >= num_descargas:
            for archivo in archivos_detectados:
                logging.info(f"Archivo nuevo detectado: {archivo}")
            return list(archivos_detectados)

    logging.error(f"No se detectaron todas las descargas esperadas ({num_descargas}). Solo detectados: {len(archivos_detectados)}")
    return list(archivos_detectados)

# ------------------- FUNCIONES REUTILIZABLES PARA OTROS SCRIPTS -------------------

def setup_descarga(driver: webdriver.Chrome, folder_name: str, product_name: str) -> str:
    """
    Prepara el entorno de descargas para Selenium.
    Crea (o utiliza, si ya existe) la carpeta BASE_DIR/descargas/[folder_name]/[product_name] y configura el driver para descargar ahí.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        folder_name (str): Nombre de la carpeta de la empresa.
        product_name (str): Nombre de la carpeta para el producto (en este caso, para el PDF).
    
    Returns:
        str: Ruta absoluta de la carpeta de descargas.
    """
    base_download_folder = os.path.join(BASE_DIR, "descargas")
    
    # Usar (o crear) la carpeta de la empresa
    empresa_folder = os.path.join(base_download_folder, folder_name)
    if not os.path.exists(empresa_folder):
        os.makedirs(empresa_folder, exist_ok=True)
    
    # Usar (o crear) la carpeta del producto dentro de la empresa
    producto_folder = os.path.join(empresa_folder, product_name)
    if not os.path.exists(producto_folder):
        os.makedirs(producto_folder, exist_ok=True)
    
    download_path = ensure_download_path(producto_folder)
    configure_driver_download_path(driver, download_path)
    logging.info(f"Descargas configuradas en: {download_path}")
    return download_path

def finalizar_descarga(driver: webdriver.Chrome):
    """
    Limpia la configuración de descargas si es necesario y permite continuar con el flujo Selenium.
    Actualmente solo cierra el driver, pero se puede ampliar si se requiere lógica adicional.
    """
    driver.quit()
    logging.info("Driver cerrado tras la descarga.")
