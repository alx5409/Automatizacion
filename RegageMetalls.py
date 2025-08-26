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
import certHandler
import downloadFunctions
import webConfiguration
import webFunctions
import loggerConfig
from config import BASE_DIR, cargar_variables
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
            logging.info(f"Autenticación completada en el intento {intento}.")
            break
        except Exception as e:
            logging.warning(f"Intento {intento}/{max_intentos} fallido en autenticación: {e}")
            time.sleep(0.5)
    else:
        logging.error(f"No se pudo completar la autenticación tras {max_intentos} intentos.")
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
        logging.info("Clic en los PDFs realizado.")

        # Esperar la descarga (sin navegador)
        logging.info(f"Esperando {numDownloads} descargas en {download_path}...")
        archivos_descargados = downloadFunctions.wait_for_new_download(download_path, old_state, numDownloads)
        logging.info(f"Archivos descargados: {archivos_descargados}")

    except Exception as e:
        logging.error(f"Error durante la descarga de documentos: {e}")
    finally:
        try:
            driver.quit()
            logging.info("Navegador cerrado después de intentar descargar los PDFs.")
        except Exception as quit_error:
            logging.error(f"Error cerrando el navegador en finally: {quit_error}")

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
    logging.info(f"Iniciando procesamiento para regage={regage}, productor={nif_productor}, representante={nif_representante}")
    
    try:
        # Construir la URL
        linkMiteco = get_linkMiteco(regage, nif_productor, nif_representante)
        logging.info(f"Procesando registro: {nombre_residuo} ({nombre_productor})")
        logging.info(f"Enlace a abrir: {linkMiteco}")

        # Configurar el navegador
        driver = webConfiguration.configure()
        if not driver:
            logging.error("No se pudo iniciar el navegador.")
            return None

        # Intentar abrir la web con reintentos
        max_intentos = 5000
        for intento in range(1, max_intentos + 1):
            try:
                webFunctions.abrir_web(driver, linkMiteco)
                logging.info(f"Web abierta correctamente en el intento {intento}.")
                break
            except Exception as e:
                logging.warning(f"Intento {intento}/{max_intentos} fallido al abrir la web: {e}")
                time.sleep(0.5)
        else:
            logging.error(f"No se pudo abrir la web tras {max_intentos} intentos.")
            return None

        # Autenticar y seleccionar certificado con reintentos
        max_intentos_auth = 5000
        for intento in range(1, max_intentos_auth + 1):
            try:
                autenticar_y_seleccionar_certificado(driver)
                logging.info(f"Autenticación completada en el intento {intento}.")
                break
            except Exception as e:
                logging.warning(f"Intento de autenticación {intento}/{max_intentos_auth} fallido: {e}")
                time.sleep(0.5)
        else:
            logging.error(f"No se pudo completar la autenticación tras {max_intentos_auth} intentos.")
            return None

        # Volver a abrir el enlace después de la autenticación con reintentos
        for intento in range(1, max_intentos + 1):
            try:
                webFunctions.abrir_web(driver, linkMiteco)
                logging.info(f"Web reabierta después de autenticación en el intento {intento}.")
                break
            except Exception as e:
                logging.warning(f"Intento {intento}/{max_intentos} fallido al reabrir la web: {e}")
                time.sleep(0.5)
        else:
            logging.error(f"No se pudo reabrir la web tras {max_intentos} intentos.")
            return None

        # Configurar carpeta de descargas única para este producto
        download_path = downloadFunctions.setup_descarga(driver, nombre_productor, nombre_residuo)

        # Descargar documentos (se cerrará el navegador dentro de esta función)
        archivos_descargados = descargar_documentos(driver, download_path)
        driver = None  # El driver ya fue cerrado en descargar_documentos
        
        logging.info(f"Descarga finalizada para {nombre_residuo} ({nombre_productor}).")
        logging.info(f"Archivos descargados: {archivos_descargados}")
        
        return archivos_descargados

    except TimeoutException as e:
        logging.error(f"Timeout al procesar registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
        return None
    except WebDriverException as e:
        logging.error(f"Error del navegador al procesar registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
        return None
    except Exception as e:
        logging.error(f"Error procesando registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
        return None
    finally:
        # Cerrar completamente el navegador si aún está abierto
        if driver:
            try:
                driver.quit()
                logging.info(f"Navegador cerrado en finally para {nombre_residuo} ({nombre_productor}).")
            except Exception as quit_error:
                logging.error(f"Error cerrando el navegador en finally: {quit_error}")

def procesar_multiple_regages(max_registros=100):
    """
    Procesa un número limitado de registros de /output/{nombre_productor}/regage_{nombre_residuo}.json.
    Cada registro abre un nuevo navegador, procesa y lo cierra inmediatamente.
    """
    output_base = os.path.join(BASE_DIR, "output")
    if not os.path.exists(output_base):
        logging.error(f"No se encontró la carpeta: {output_base}")
        return

    carpetas = [os.path.join(output_base, d) for d in os.listdir(output_base) if os.path.isdir(os.path.join(output_base, d))]
    if not carpetas:
        logging.error(f"No se encontraron carpetas de productor en: {output_base}")
        return

    registros_procesados = 0
    for carpeta in carpetas:
        archivos_json = [f for f in os.listdir(carpeta) if f.lower().endswith('.json')]
        for archivo_json in archivos_json:
            if registros_procesados >= max_registros:
                logging.info(f"Se alcanzó el límite de registros procesados: {max_registros}")
                return

            ruta_json = os.path.join(carpeta, archivo_json)
            logging.info(f"Procesando archivo {registros_procesados + 1}/{max_registros}: {archivo_json}")
            
            with open(ruta_json, "r", encoding="utf-8") as f:
                try:
                    registro = json.load(f)
                except Exception as e:
                    logging.error(f"Error leyendo {ruta_json}: {e}")
                    continue

            # Procesar el registro (abre navegador, procesa y lo cierra)
            archivos_descargados = procesar_registro(registro)
            registros_procesados += 1

            # Mover el archivo procesado a la carpeta trash
            trash_dir = os.path.join(BASE_DIR, "trash")
            os.makedirs(trash_dir, exist_ok=True)
            destino = os.path.join(trash_dir, os.path.basename(ruta_json))
            try:
                shutil.move(ruta_json, destino)
                logging.info(f"Archivo {os.path.basename(ruta_json)} movido a {destino}.")
            except Exception as e:
                logging.error(f"Error al mover {ruta_json} a trash: {e}")

            # Pausa entre registros para evitar bloqueos
            logging.info(f"Esperando 10 segundos antes del siguiente registro...")
            time.sleep(10)

    logging.info(f"Procesamiento completado. Total de registros procesados: {registros_procesados}")


if __name__ == "__main__":
    procesar_multiple_regages()