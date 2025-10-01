"""
Módulo: RegageMetalls.py

Este módulo recorre todas las carpetas dentro de /output, lee los archivos .json de cada una,
construye el enlace de detalle de expediente de MITECO para cada registro y lo abre en el navegador
utilizando Selenium y las funciones auxiliares de webFunctions y downloadFunctions.

Flujo general:
  1. Lee todas las carpetas dentro de output.
  2. Para cada archivo .json dentro de cada carpeta, construye el enlace personalizado de MITECO.
  3. Abre el enlace en el navegador con Selenium, realiza la autenticación y descarga los archivos asociados en una carpeta única por iteración.
  4. Repite el proceso para todos los registros.

Ejemplo de uso:
    Ejecutar este script abrirá secuencialmente todos los enlaces de los .json en output en el navegador y descargará los archivos correspondientes.
"""

# Imports básicos de Python
import os
import json
import shutil
import logging
import time
from typing import List

# Imports propios del proyecto
import src.funciones.certHandler as certHandler
from funciones import downloadFunctions, webFunctions
from utils import webConfiguration, loggerConfig
from src.utils.config import BASE_DIR, cargar_variables
from selenium.common.exceptions import TimeoutException, WebDriverException

# Variables de configuración
INFO_CERTS = os.path.join(BASE_DIR, "data", "informacionCertsMetalls.txt")
info = cargar_variables(INFO_CERTS)

def get_linkMiteco(regage_val, nif_productor, nif_representante):
    """
    Construye el enlace de detalle de expediente de MITECO para un registro dado.
    """
    linkMiteco = (
        "https://sede.miteco.gob.es/portal/site/seMITECO/area_personal"
        "?btnDetalleProc=btnDetalleProc"
        "&pagina=1"
        f"&idExpediente={regage_val}"
        "&idProcedimiento=736"
        "&idSubOrganoResp=11"
        f"&idDocIdentificativo={nif_productor}"
        f"&idDocRepresentante={nif_representante}"
        "&idEstadoSeleccionado=-1"
        "&idTipoProcSeleccionado=EN+REPRESENTACION+(REA)"
        f"&regInicial={regage_val}"
        f"&nifTitular={nif_productor}"
        "&numPagSolSelec=10#no-back-button"
    )
    logging.info("[INFO-01] Enlace MITECO generado: %s", linkMiteco)
    return linkMiteco

def autenticar_y_seleccionar_certificado(driver):
    """
    Realiza el proceso de autenticación y selección de certificado en la web de MITECO,
    con varios intentos en caso de fallo.
    """
    max_intentos = 100
    for intento in range(1, max_intentos + 1):
        try:
            webFunctions.esperar_elemento_por_id(driver, "breadcrumb")
            webFunctions.clickar_boton_por_value(driver, "acceder")
            webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")
            certHandler.seleccionar_certificado_chrome(info.get("NOMBRE_CERT"))
            logging.info(f"[INFO-02] Autenticación completada en el intento {intento}.")
            break
        except Exception as e:
            logging.warning(f"[WARN-01] Intento {intento}/{max_intentos} fallido en autenticación: {e}")
            time.sleep(0.5)
    else:
        logging.error(f"[ERR-01] No se pudo completar la autenticación tras {max_intentos} intentos.")
        raise Exception("Fallo en la autenticación tras varios intentos")

def descargar_documentos(driver, download_path, numDownloads=2):
    """
    Lanza la descarga de los documentos asociados a un expediente MITECO.
    El driver ya debe estar en la página correcta después de la autenticación.
    Cierra el navegador inmediatamente después de hacer clic en los PDFs.
    """
    archivos_descargados = []
    old_state = downloadFunctions.snapshot_folder_state(download_path)
    try:
        # Lanzar descargas
        webFunctions.clickar_todos_los_links(driver, ".pdf")
        logging.info("[INFO-03] Clic en los PDFs realizado.")

        # Esperar la descarga (sin navegador)
        logging.info(f"[INFO-04] Esperando {numDownloads} descargas en {download_path}...")
        archivos_descargados = downloadFunctions.wait_for_new_download(download_path, old_state, numDownloads)
        logging.info(f"[INFO-05] Archivos descargados: {archivos_descargados}")

    except Exception as e:
        logging.error(f"[ERR-02] Error durante la descarga de documentos: {e}")
    finally:
        try:
            driver.quit()
            logging.info("[INFO-06] Navegador cerrado después de intentar descargar los PDFs.")
        except Exception as quit_error:
            logging.error(f"[ERR-03] Error cerrando el navegador en finally: {quit_error}")

    return archivos_descargados

def procesar_registro(registro):
    """
    Procesa un único registro de regage.json: abre el enlace, autentica, descarga y guarda los archivos.
    Cierra completamente el navegador después de hacer clic en los PDFs para evitar bloqueos.
    """
    regage = registro.get("regage", "")
    nif_productor = registro.get("nif_productor", "")
    nif_representante = registro.get("nif_representante", "")
    nombre_productor = registro.get("nombre_productor", "desconocido").replace(" ", "_")
    nombre_residuo = registro.get("nombre_residuo", "desconocido").replace(" ", "_").replace("*", "")

    driver = None
    logging.info(f"[INFO-07] Iniciando procesamiento para regage={regage}, productor={nif_productor}, representante={nif_representante}")
    
    try:
        # Construir la URL
        linkMiteco = get_linkMiteco(regage, nif_productor, nif_representante)
        logging.info(f"[INFO-08] Procesando registro: {nombre_residuo} ({nombre_productor})")
        logging.info(f"[INFO-09] Enlace a abrir: {linkMiteco}")

        # Configurar el navegador
        driver = webConfiguration.configure()
        if not driver:
            logging.error("[ERR-04] No se pudo iniciar el navegador.")
            return None

        # Intentar abrir la web con reintentos
        max_intentos = 5000
        for intento in range(1, max_intentos + 1):
            try:
                webFunctions.abrir_web(driver, linkMiteco)
                logging.info(f"[INFO-10] Web abierta correctamente en el intento {intento}.")
                break
            except Exception as e:
                logging.warning(f"[WARN-02] Intento {intento}/{max_intentos} fallido al abrir la web: {e}")
                time.sleep(0.5)
        else:
            logging.error(f"[ERR-05] No se pudo abrir la web tras {max_intentos} intentos.")
            return None

        # Autenticar y seleccionar certificado con reintentos
        max_intentos_auth = 5000
        for intento in range(1, max_intentos_auth + 1):
            try:
                autenticar_y_seleccionar_certificado(driver)
                logging.info(f"[INFO-11] Autenticación completada en el intento {intento}.")
                break
            except Exception as e:
                logging.warning(f"[WARN-03] Intento de autenticación {intento}/{max_intentos_auth} fallido: {e}")
                time.sleep(0.5)
        else:
            logging.error(f"[ERR-06] No se pudo completar la autenticación tras {max_intentos_auth} intentos.")
            return None

        # Volver a abrir el enlace después de la autenticación con reintentos
        for intento in range(1, max_intentos + 1):
            try:
                webFunctions.abrir_web(driver, linkMiteco)
                logging.info(f"[INFO-12] Web reabierta después de autenticación en el intento {intento}.")
                break
            except Exception as e:
                logging.warning(f"[WARN-04] Intento {intento}/{max_intentos} fallido al reabrir la web: {e}")
                time.sleep(0.5)
        else:
            logging.error(f"[ERR-07] No se pudo reabrir la web tras {max_intentos} intentos.")
            return None

        # Configurar carpeta de descargas única para este producto
        download_path = downloadFunctions.setup_descarga(driver, nombre_productor, nombre_residuo)
        logging.info(f"[INFO-13] Carpeta de descarga configurada: {download_path}")

        # Descargar documentos (se cerrará el navegador dentro de esta función)
        archivos_descargados = descargar_documentos(driver, download_path)
        driver = None  # El driver ya fue cerrado en descargar_documentos
        
        logging.info(f"[INFO-14] Descarga finalizada para {nombre_residuo} ({nombre_productor}).")
        logging.info(f"[INFO-15] Archivos descargados: {archivos_descargados}")
        
        return archivos_descargados

    except TimeoutException as e:
        logging.error(f"[ERR-08] Timeout al procesar registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
        return None
    except WebDriverException as e:
        logging.error(f"[ERR-09] Error del navegador al procesar registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
        return None
    except Exception as e:
        logging.error(f"[ERR-10] Error procesando registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
        return None
    finally:
        # Cerrar completamente el navegador si aún está abierto
        if driver:
            try:
                driver.quit()
                logging.info(f"[INFO-16] Navegador cerrado en finally para {nombre_residuo} ({nombre_productor}).")
            except Exception as quit_error:
                logging.error(f"[ERR-11] Error cerrando el navegador en finally: {quit_error}")

def procesar_multiple_regages(max_registros=100):
    """
    Procesa un número limitado de registros de /output/{nombre_productor}/regage_{nombre_residuo}.json.
    Cada registro abre un nuevo navegador, procesa y lo cierra inmediatamente.
    """
    output_base = os.path.join(BASE_DIR, "output")
    if not os.path.exists(output_base):
        logging.error(f"[ERR-12] No se encontró la carpeta: {output_base}")
        return

    carpetas = [os.path.join(output_base, d) for d in os.listdir(output_base) if os.path.isdir(os.path.join(output_base, d))]
    if not carpetas:
        logging.error(f"[ERR-13] No se encontraron carpetas de productor en: {output_base}")
        return

    registros_procesados = 0
    for carpeta in carpetas:
        archivos_json = [f for f in os.listdir(carpeta) if f.lower().endswith('.json')]
        for archivo_json in archivos_json:
            if registros_procesados >= max_registros:
                logging.info(f"[INFO-17] Se alcanzó el límite de registros procesados: {max_registros}")
                return

            ruta_json = os.path.join(carpeta, archivo_json)
            logging.info(f"[INFO-18] Procesando archivo {registros_procesados + 1}/{max_registros}: {archivo_json}")
            
            with open(ruta_json, "r", encoding="utf-8") as f:
                try:
                    registro = json.load(f)
                except Exception as e:
                    logging.error(f"[ERR-14] Error leyendo {ruta_json}: {e}")
                    continue

            # Procesar el registro (abre navegador, procesa y lo cierra)
            archivos_descargados = procesar_registro(registro)
            registros_procesados += 1

            # Mover el archivo procesado a la carpeta trash
            # Extrae el nombre del productor del registro
            nombre_productor = registro.get("nombre_productor", "desconocido").replace(" ", "_")
            trash_dir = os.path.join(BASE_DIR, "trash", nombre_productor)
            os.makedirs(trash_dir, exist_ok=True)
            destino = os.path.join(trash_dir, os.path.basename(ruta_json))
            try:
                shutil.move(ruta_json, destino)
                logging.info(f"[INFO-19] Archivo {os.path.basename(ruta_json)} movido a {destino}.")
            except Exception as e:
                logging.error(f"[ERR-15] Error al mover {ruta_json} a trash: {e}")

            # Pausa entre registros para evitar bloqueos
            logging.info(f"[INFO-20] Esperando 10 segundos antes del siguiente registro...")
            time.sleep(10)

    logging.info(f"[INFO-21] Procesamiento completado. Total de registros procesados: {registros_procesados}")


if __name__ == "__main__":
    procesar_multiple_regages()