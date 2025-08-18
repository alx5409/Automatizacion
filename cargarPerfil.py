import os
import shutil
import tempfile
import logging
import subprocess
import re
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import BASE_DIR

logging.basicConfig(level=logging.INFO)

# 🗂️ Ruta donde están los certificados PFX
PFX_FOLDER = os.path.join(BASE_DIR, "certificados")
CERT_PASSWORD = "tu_contraseña"
NOMBRE_CERTIFICADO = "RICARDO ESCUDE"  # parte del nombre del sujeto (CN)

def buscar_pfx_por_nombre(directorio, nombre_cert, password=None):
    for pfx_file in glob.glob(os.path.join(directorio, "*.pfx")):
        try:
            with open(pfx_file, "rb") as f:
                data = f.read()
                private_key, cert, _ = pkcs12.load_key_and_certificates(
                    data,
                    password.encode() if password else None
                )
                if cert and nombre_cert.lower() in cert.subject.rfc4514_string().lower():
                    logging.info(f"Coincidencia encontrada: {pfx_file}")
                    return pfx_file
        except Exception:
            continue  # Ignora pfx corruptos o con contraseña incorrecta
    logging.warning("No se encontró ningún certificado .pfx con ese nombre.")
    return None

def importar_certificado(pfx_path, password):
    try:
        comando = [
            "certutil",
            "-f",
            "-p", password,
            "-importpfx",
            pfx_path
        ]
        result = subprocess.run(comando, capture_output=True, text=True)
        output = result.stdout
        logging.info("Certificado importado:\n" + output)

        match = re.search(r"Número de serie:\s*([A-Fa-f0-9]+)", output)
        if match:
            serie = match.group(1).strip()
            logging.info(f"Número de serie detectado: {serie}")
            return serie
    except Exception as e:
        logging.error(f"Error al importar certificado: {e}")
    return None

def buscar_thumbprint_por_serie(serie):
    try:
        comando = ["certutil", "-store", "My"]
        result = subprocess.run(comando, capture_output=True, text=True)
        output = result.stdout

        bloques = output.split("Certificado:")
        for bloque in bloques:
            if serie.lower() in bloque.lower():
                match = re.search(r"Huella digital de certificado.*?:\s*([a-fA-F0-9\s]+)", bloque)
                if match:
                    thumbprint = match.group(1).replace(" ", "").strip()
                    logging.info(f"Huella digital encontrada: {thumbprint}")
                    return thumbprint
    except Exception as e:
        logging.error(f"Error buscando la huella digital: {e}")
    return None

def eliminar_certificado(thumbprint):
    try:
        comando = ["certutil", "-delstore", "My", thumbprint]
        result = subprocess.run(comando, capture_output=True, text=True)
        logging.info("Certificado eliminado:\n" + result.stdout)
    except Exception as e:
        logging.error(f"No se pudo eliminar el certificado: {e}")

def create_temp_chrome_profile():
    temp_dir = tempfile.mkdtemp(prefix="chrome_profile_")
    logging.info(f"Perfil temporal creado en: {temp_dir}")
    return temp_dir

def delete_profile_dir(path):
    try:
        shutil.rmtree(path)
        logging.info(f"Perfil eliminado: {path}")
    except Exception as e:
        logging.error(f"No se pudo eliminar el perfil: {e}")

def launch_chrome_with_temp_profile(user_data_dir):
    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-popup-blocking")

    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        input("Pulsa Enter para cerrar el navegador...")
        driver.quit()
    except Exception as e:
        logging.error("Error al iniciar el navegador: %s", e)
        raise

if __name__ == "__main__":
    temp_profile = create_temp_chrome_profile()
    thumbprint = None

    try:
        pfx_path = buscar_pfx_por_nombre(PFX_FOLDER, NOMBRE_CERTIFICADO, CERT_PASSWORD)
        if pfx_path:
            serie = importar_certificado(pfx_path, CERT_PASSWORD)
            if serie:
                thumbprint = buscar_thumbprint_por_serie(serie)
        else:
            logging.error("No se encontró el archivo .pfx para el certificado solicitado.")
            exit(1)

        launch_chrome_with_temp_profile(temp_profile)
    finally:
        if thumbprint:
            eliminar_certificado(thumbprint)
        delete_profile_dir(temp_profile)
