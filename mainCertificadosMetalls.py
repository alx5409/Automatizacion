"""
Módulo: mainCertificados.py

Este módulo orquesta el flujo de automatización para la gestión de certificados en la web de MITECO,
utilizando Selenium para interactuar con la interfaz web y uiautomation junto con funciones auxiliares
de autoFirmaHandler y certHandler para la selección del certificado a utilizar (por DNIe o certificado electrónico).

Flujo general:
  1. Procesa todas las subcarpetas dentro de la carpeta /input.
  2. En cada subcarpeta, procesa todos los archivos XML y mueve el XML procesado a /trash/{nombre_productor}.
  3. Cuando no quedan XML en la subcarpeta, mueve el PDF de esa subcarpeta a la carpeta del último {nombre_productor} en /trash.
  4. Cuando termina con una subcarpeta, pasa a la siguiente y al finalizar todas termina el proceso.

Ejemplo de uso:
    Ejecutar este script inicia el flujo de automatización para el proceso de certificados en MITECO.
    Al finalizar, se cierra el navegador.
"""

# Imports básicos de Python
import pandas as pd
import logging
import time
import os
import shutil
import tempfile
import subprocess
import re
import json
import glob
import sys
import unicodedata
import loggerConfig
import tkinter as tk
from tkinter import ttk
import typing
from typing import Union, Optional, List, Dict
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re

# Imports de Selenium y WebDriver
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchWindowException, NoSuchFrameException, WebDriverException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Imports de uiautomation
import uiautomation as auto
import uiautomationHandler

# Imports propios del proyecto
import autoFirmaHandler
import certHandler
import extraerXMLE3L
import loggerConfig
import webConfiguration
import webFunctions
import funcionesNubelus
import excelFunctions
from config import BASE_DIR, cargar_variables
from datetime import datetime, timedelta

# Variables de configuración
WEB_MITECO = (
    "https://sede.miteco.gob.es/portal/site/seMITECO/login?"
    "urlLoginRedirect=L3BvcnRhbC9zaXRlL3NlTUlURUNPL3BvcnRsZXRfYnVzP2lkX3Byb2NlZGltaWVudG89NzM2"
    "JmlkZW50aWZpY2Fkb3JfcGFzbz1QUkVJTklDSU8mc3ViX29yZ2Fubz0xMSZwcmV2aW9fbG9naW49MQ=="
)
URL_CONTRATOS_TRATAMIENTOS = "https://portal.nubelus.es/?clave=waster2_gestionContratosTratamiento"
INPUT_DIR = os.path.join(BASE_DIR, "input")
EXCEL_INPUT_DIR = os.path.join(BASE_DIR, "entrada", "excel_input.xls")  # Ruta del Excel de entrada
TRASH_DIR = os.path.join(BASE_DIR, "trash")
INFO_CERTS = os.path.join(BASE_DIR, "data", "informacionCertsMetalls.txt")
info = cargar_variables(INFO_CERTS)

def get_pdf_file_from_folder(folder_path):
    """
    Busca el primer archivo PDF en la carpeta indicada.
    Si no encuentra ninguno, devuelve None.
    """
    for f in os.listdir(folder_path):
        if f.lower().endswith('.pdf'):
            logging.info(f"Archivo PDF encontrado: {f}")
            return os.path.join(folder_path, f)
    logging.error(f"No se encontró ningún archivo PDF en la carpeta '{folder_path}'.")
    return None

def actualizar_fechas_xml(xml_path):
    """
    Modifica las fechas del XML en las etiquetas <prepared> y atributos NTDate, NTStartDate, NTEndDate de <wasteNT>.
    Procesa el archivo como texto plano, sin usar ElementTree.
    """
    hoy = datetime.now()
    hoy_str = hoy.strftime("%Y-%m-%d")
    hoy_iso = hoy.strftime("%Y-%m-%dT%H:%M:%S")
    start_date = (hoy + timedelta(days=11)).strftime("%Y-%m-%d")
    end_date = (hoy + timedelta(days=3*365)).strftime("%Y-%m-%d")  # Aproximación de 3 años

    with open(xml_path, "r", encoding="utf-8") as f:
        xml_text = f.read()

    # Reemplazar <prepared>...</prepared>
    xml_text = re.sub(r"<prepared>.*?</prepared>", f"<prepared>{hoy_iso}</prepared>", xml_text, flags=re.DOTALL)

    # Reemplazar atributos en <wasteNT ...>
    def replace_nt_attrs(match):
        tag = match.group(0)
        tag = re.sub(r'NTDate="[^"]*"', f'NTDate="{hoy_str}"', tag)
        tag = re.sub(r'NTStartDate="[^"]*"', f'NTStartDate="{start_date}"', tag)
        tag = re.sub(r'NTEndDate="[^"]*"', f'NTEndDate="{end_date}"', tag)
        return tag

    xml_text = re.sub(r"<wasteNT\b[^>]*>", replace_nt_attrs, xml_text)

    # Asegurar que la raíz sea <ns2:e3l> con los namespaces requeridos
    ns2_tag = '<ns2:e3l xmlns:ns2="e3l://eterproject.org/3.0/e3l" xmlns:ns3="e3l://eterproject.org/3.0/documentation" schemaVersion="3.0">'
    xml_text = re.sub(r"<e3l\b[^>]*>", ns2_tag, xml_text, count=1)
    xml_text = re.sub(r"<ns2:e3l\b[^>]*>", ns2_tag, xml_text, count=1)

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_text)
    return xml_path

def guardar_regage_json(data, output_dir):
    """
    Guarda el contenido en un archivo regage.json en output_dir.
    Si ya existe, crea regage_1.json, regage_2.json, etc. para no sobrescribir.
    """
    base_name = "regage"
    ext = ".json"
    filename = base_name + ext
    counter = 1
    full_path = os.path.join(output_dir, filename)
    while os.path.exists(full_path):
        filename = f"{base_name}_{counter}{ext}"
        full_path = os.path.join(output_dir, filename)
        counter += 1
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return full_path

def mover_a_trash(origen, nombre_productor):
    """
    Mueve un archivo a la carpeta /trash/{nombre_productor}.
    """
    destino_dir = os.path.join(TRASH_DIR, nombre_productor)
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, os.path.basename(origen))
    shutil.move(origen, destino)
    logging.info(f"Archivo '{os.path.basename(origen)}' movido a '{destino_dir}'.")

def rellenar_formulario(driver):
    """
    Rellena el formulario principal de la web de MITECO con los datos del certificado.
    """
    webFunctions.escribir_en_elemento_por_id(driver, "id_direccion", info.get("DIRECCION"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_pais", info.get("PAIS"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_provincia", info.get("PROVINCIA"))
    webFunctions.seleccionar_elemento_por_id(driver, "id_municipio", info.get("MUNICIPIO"))
    webFunctions.escribir_en_elemento_por_id(driver, "id_codigo_postal", info.get("CODIGO_POSTAL"))
    webFunctions.escribir_en_elemento_por_id(driver, "id_correo_electronico", info.get("CORREO_ELECTRONICO"))

def autenticar_y_seleccionar_certificado(driver):
    """
    Realiza el proceso de autenticación y selección de certificado en la web de MITECO.
    """
    webFunctions.clickar_boton_por_value(driver, "acceder")
    webFunctions.clickar_boton_por_texto(driver, "Acceso DNIe / Certificado electrónico")
    certHandler.seleccionar_certificado_chrome(info.get("NOMBRE_CERT"))

def procesar_xml(xml_path, nif):
    """
    Procesa un archivo XML: automatiza el flujo web, ejecuta la firma y extrae la información relevante.
    Si ocurre cualquier error, se informa y se cierra el driver actual.
    """
    logging.info(f"--- Procesando archivo XML: {os.path.basename(xml_path)} ---")
    driver = webConfiguration.configure()
    try:
        webFunctions.abrir_web(driver, WEB_MITECO)
        webFunctions.esperar_elemento_por_id(driver, "breadcrumb")

        autenticar_y_seleccionar_certificado(driver)
        webFunctions.esperar_elemento_por_id(driver, "wrapper", timeout=15)
        webFunctions.clickar_boton_por_id(driver, "id_presenta_solicitud_3")
        webFunctions.escribir_en_elemento_por_id(driver, "id_nif_remitente", nif)
        webFunctions.clickar_boton_por_id(driver, "id_btnOtroSol")
        time.sleep(1)
        rellenar_formulario(driver)

        webFunctions.clickar_boton_por_id(driver, "btnForm")
        time.sleep(5)

        webFunctions.clickar_boton_por_id(driver, "tipoEnvioNtA")
        actualizar_fechas_xml(xml_path)
        webFunctions.escribir_en_elemento_por_id(driver, "file", xml_path)

        webFunctions.clickar_boton_por_clase(driver, "loginBtn")
        webFunctions.clickar_boton_por_texto(driver, "Continuar")

        webFunctions.clickar_boton_por_id(driver, "btnForm")
        webFunctions.clickar_boton_por_id(driver, "bSiguiente")
        webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")
        time.sleep(2)
        webFunctions.clickar_boton_por_id(driver, "idFirmarRegistrar")

        autoFirmaHandler.firmar_en_autofirma()

        regage = webFunctions.obtener_texto_por_parte(driver, "Descargar Justificante:").split()[-1]
        logging.info(f"Código de justificante obtenido: {regage}")

        json_result = extraerXMLE3L.extraer_info_xml(xml_path, regage)
        logging.info(f"Información extraída del XML: {json_result}")

        return json_result

    except Exception as e:
        logging.error(f"Error procesando '{os.path.basename(xml_path)}': {e}", exc_info=True)
    finally:
        try:
            driver.quit()
        except Exception as e_quit:
            logging.error(f"Error cerrando driver: {e_quit}")

def procesar_archivos_xml_en_subcarpetas():
    """
    Procesa todas las subcarpetas dentro de INPUT_DIR.
    En cada subcarpeta, procesa los XML y mueve los archivos igual que antes.
    Al terminar con una subcarpeta, pasa a la siguiente.
    """
    subcarpetas = [os.path.join(INPUT_DIR, d) for d in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))]
    if not subcarpetas:
        logging.info("No se encontraron subcarpetas en la carpeta 'input'.")
        return

    for subdir in subcarpetas:
        logging.info(f"Procesando subcarpeta: {os.path.basename(subdir)}")
        xml_files = sorted([os.path.join(subdir, f) for f in os.listdir(subdir) if f.lower().endswith('.xml')])

        while xml_files:
            procesados_esta_vuelta = []
            for xml_file in xml_files:
                try:
                    primera_palabra = os.path.basename(subdir).split()[0]
                    resultado = procesar_xml(xml_file, primera_palabra)
                    if resultado is None:
                        continue
                    nombre_productor = resultado.get("nombre_productor", "desconocido").replace(" ", "_")
                    mover_a_trash(xml_file, nombre_productor)
                    procesados_esta_vuelta.append(xml_file)
                except Exception as e:
                    logging.error(f"Error procesando '{os.path.basename(xml_file)}': {e}")

            xml_files = sorted([os.path.join(subdir, f) for f in os.listdir(subdir) if f.lower().endswith('.xml')])
            if not procesados_esta_vuelta and xml_files:
                logging.error(f"No se ha podido procesar ninguno de los archivos XML restantes en {subdir}.")
                break
        logging.info(f"Procesamiento completado para subcarpeta: {os.path.basename(subdir)}")

    logging.info("Proceso completado. Todas las subcarpetas procesadas.")

def notificar_contratos_tratamiento():
    excel_input = pd.read_excel(EXCEL_INPUT_DIR)
    fila = excel_input.iloc[0]  # Obtiene la primera fila del DataFrame
    # Configura el navegador de Selenium
    driver = webConfiguration.configure()
    # Inicia sesión en Nubelus
    funcionesNubelus.iniciar_sesion(driver)
    webFunctions.abrir_web(driver, URL_CONTRATOS_TRATAMIENTOS)
    
    # Filtra la busqueda por el nombre del cliente
    webFunctions.clickar_boton_por_on_click(driver, "filtrar()")
    webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "waster2_gestionContratosTratamiento__fDenominacion_origen", fila.get("nombre_recogida"))
    webFunctions.clickar_boton_por_clase(driver, "miBoton.buscar")
    # Edita las notificaciones de peligrosos a: Sí
    excelFunctions.editar_notificaciones_peligrosos(driver)
    logging.info("Notificaciones de peligrosos editadas correctamente.")
    driver.quit()
    
def main():
    """
    Función principal que marca como notificado el contrato en nubelus e inicia el procesamiento de los archivos XML en todas las subcarpetas de input.
    """
    # notificar_contratos_tratamiento()
    # logging.info("Notificaciones de contratos de tratamiento editadas correctamente.")

    procesar_archivos_xml_en_subcarpetas()
    logging.info("Todos los procesos han finalizado correctamente.")

if __name__ == "__main__":
    main()