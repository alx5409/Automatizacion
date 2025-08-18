# Importar módulos y librerías generales

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

# Importar modulos de Selenium
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common import (
    TimeoutException,
    NoSuchWindowException,
    NoSuchFrameException,
    WebDriverException,
    NoSuchElementException,
    ElementNotInteractableException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys


# Importar modulos del proyecto
import funcionesNubelus
import excelFunctions
import uiautomationHandler
import webConfiguration
import webFunctions
import config
import loggerConfig
import webConfiguration
import mainNotificarCT



ruta_excel_input = "entrada/excel_recogidas.xls"  # Ruta del Excel de entrada

def main():
    # Comprueba que el formato de los datos del Excel son correctos
    excel_input = excelFunctions.comprobar_datos_excel(ruta_excel_input)
    excel_fila = excel_input.iloc[0]
    # Prepara la carpeta y mueve el PDF antes de cualquier otra operación
    ruta_destino = excelFunctions.preparar_carpeta_para_pdf_y_xml(excel_fila)
    # Configura el navegador de Selenium
    driver = webConfiguration.configure()
    # Activa la protección mejorada para aceptar descargas xml
    funcionesNubelus.activar_proteccion_mejorada_chrome(driver)
    # Inicia sesión en Nubelus
    funcionesNubelus.iniciar_sesion(driver)
    # Descarga el Excel de entidades medioambientales
    excel_entidades = excelFunctions.descargar_excel_entidades(driver)
    # Comprueba si la empresa ya está en nubelus
    coincidencias_entidades = excelFunctions.coincidencias_en_entidades(excel_fila, excel_entidades)
    # Si la empresa está lo añade a excel_fils, si no está en nubelus, la añade y ejecuta todo el proceso de creación: desde empresa a contratos
    if coincidencias_entidades is None:
        excelFunctions.crear_contratos_desde_empresa(driver, excel_fila, ruta_destino)
    else:
        excel_fila['nombre_empresa'] = coincidencias_entidades
    # Descarga el Excel de centros medioambientales
    excel_centros = excelFunctions.descargar_excel_centros(driver)
    coincidencias_centros = excelFunctions.coincidencias_en_centros(excel_fila, excel_centros)
    # Si el centro no está en nubelus, lo añade y ejecuta todo el proceso de creación: desde centro a contratos
    if coincidencias_centros is None:
        excelFunctions.crear_contratos_desde_centros(driver, excel_fila, ruta_destino)
    excel_clientes = excelFunctions.descargar_excel_clientes(driver)
    # Comprueba si el cliente ya está en nubelus
    coincidencias_clientes = excelFunctions.coincidencias_en_clientes(excel_fila, excel_clientes)
    # Si el cliente no está en nubelus, lo añade y ejecuta todo el proceso de creación: desde cliente a contratos
    if coincidencias_clientes is None:
        excelFunctions.crear_contratos_desde_clientes(driver, excel_fila,  ruta_destino)
    # Descarga el Excel de usuarios
    usuarios = excelFunctions.descargar_excel_usuarios(driver)
    # Si el usuario no está en nubelus, lo añade
    coincidencias_usuarios = excelFunctions.coincidencias_en_usuarios(excel_fila, usuarios)
    if coincidencias_usuarios is None:
        excelFunctions.crear_contratos_desde_usuarios(driver, excel_fila, ruta_destino)
    # Descarga el Excel de acuerdos de representación
    acuerdos_representacion = excelFunctions.descargar_excel_acuerdos_representacion(driver)
    # Comprueba si el acuerdo de representación ya existe
    coincidencias_acuerdos = excelFunctions.coincidencias_en_acuerdos_representacion(excel_fila, acuerdos_representacion)
    # Si el acuerdo de representación no existe, lo añade
    if coincidencias_acuerdos is None:
        excelFunctions.crear_contratos_desde_acuerdos_representacion(driver, excel_fila, ruta_destino)
    # Descarga el Excel de contratos de tratamiento
    contratos_tratamiento = excelFunctions.descargar_excel_contratos(driver)
    # Comprueba los contratos de tratamiento que ya existen
    coincidencias_contratos = excelFunctions.coincidencias_en_contratos(excel_fila, contratos_tratamiento)
    # Crea los contratos faltantes (todos si no hay ninguno, parciales si faltan algunos)
    excelFunctions.crear_contratos_faltantes(driver, excel_fila, coincidencias_contratos, ruta_destino)

if __name__ == "__main__":
    main()