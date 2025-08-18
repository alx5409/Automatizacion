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
    Realiza el proceso de autenticación y selección de certificado en la web de MITECO.
    """
    webFunctions.esperar_elemento_por_id(driver, "breadcrumb")
    webFunctions.clickar_boton_por_value(driver, "acceder")
    webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")
    certHandler.seleccionar_certificado_chrome(info.get("NOMBRE_CERT"))

def descargar_documentos(driver, linkMiteco, download_path, numDownloads=2):
    """
    Lanza la descarga de los documentos asociados a un expediente MITECO.
    Cierra el navegador después de descargar los documentos necesarios.
    """
    webFunctions.abrir_web(driver, linkMiteco)
    old_state = downloadFunctions.snapshot_folder_state(download_path)

    # Lanzar descargas
    webFunctions.clickar_todos_los_links(driver, ".pdf")

    # Esperar la descarga
    logging.info(f"Esperando {numDownloads} descargas en {download_path}...")
    archivos_descargados = downloadFunctions.wait_for_new_download(download_path, old_state, numDownloads)

    logging.info(f"Archivos descargados: {archivos_descargados}")
    return archivos_descargados

def procesar_registro(registro):
    """
    Procesa un único registro de regage.json: abre el enlace, autentica, descarga y guarda los archivos.
    Cierra el navegador después de procesar cada registro.
    """
    regage = registro.get("regage", "")
    nif_productor = registro.get("nif_productor", "")
    nif_representante = registro.get("nif_representante", "")
    nombre_productor = registro.get("nombre_productor", "desconocido").replace(" ", "_")
    nombre_residuo = registro.get("nombre_residuo", "desconocido").replace(" ", "_").replace("*", "")

    try:
        # Construir la URL
        linkMiteco = get_linkMiteco(regage, nif_productor, nif_representante)
        logging.info(f"Abrir enlace: {linkMiteco}")

        # Configurar el navegador y abrir la URL
        driver = webConfiguration.configure()
        if not driver:
            logging.error("No se pudo iniciar el navegador.")
            return

        webFunctions.abrir_web(driver, linkMiteco)

        # Autenticar y seleccionar certificado
        autenticar_y_seleccionar_certificado(driver)

        # Configurar carpeta de descargas única para este producto
        download_path = downloadFunctions.setup_descarga(driver, nombre_productor, nombre_residuo)

        # Descargar documentos y cerrar el navegador
        archivos_descargados = descargar_documentos(driver, linkMiteco, download_path)
        downloadFunctions.finalizar_descarga(driver)
        logging.info(f"Descarga finalizada para {nombre_residuo} ({nombre_productor}).")
        driver.quit()  # Cierra el navegador después de descargar los documentos
        return archivos_descargados

    except TimeoutException as e:
        logging.error(f"Timeout al procesar registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
    except WebDriverException as e:
        logging.error(f"Error del navegador al procesar registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
    except Exception as e:
        logging.error(f"Error procesando registro: regage={regage}, productor={nif_productor}, representante={nif_representante}. Error: {e}")
    finally:
        try:
            driver.quit()
        except Exception as quit_error:
            logging.error(f"Error cerrando el navegador: {quit_error}")

def procesar_multiple_regages(max_registros=10):
    """
    Procesa un número limitado de registros de /output/{nombre_productor}/regage_{nombre_residuo}.json.
    Cierra y abre un nuevo navegador para cada registro.
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
            with open(ruta_json, "r", encoding="utf-8") as f:
                try:
                    registro = json.load(f)
                except Exception as e:
                    logging.error(f"Error leyendo {ruta_json}: {e}")
                    continue

            # Procesar el registro y cerrar el navegador después de cada uno
            procesar_registro(registro)
            registros_procesados += 1

            # Pausa para evitar sobrecargar el servidor
            time.sleep(5)

            # Mover el archivo procesado a la carpeta trash
            trash_dir = os.path.join(BASE_DIR, "trash")
            os.makedirs(trash_dir, exist_ok=True)
            destino = os.path.join(trash_dir, os.path.basename(ruta_json))
            try:
                shutil.move(ruta_json, destino)
                logging.info(f"Archivo {os.path.basename(ruta_json)} movido a {destino}.")
            except Exception as e:
                logging.error(f"Error al mover {ruta_json} a trash: {e}")


if __name__ == "__main__":
    procesar_multiple_regages()