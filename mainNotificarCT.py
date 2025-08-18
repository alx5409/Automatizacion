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
import webConfiguration
import webFunctions
import config
import loggerConfig
import webConfiguration

URL_CONTRATOS_TRATAMIENTOS = "https://portal.nubelus.es/?clave=waster2_gestionContratosTratamiento"
RUTA_EXCEL_INPUT = "entrada/excel_input.xls"  # Ruta del Excel de entrada

def main():
    excel_input = pd.read_excel("entrada/excel_input.xls")
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
    excelFunctions.editar_notificaciones_peligrosos(driver)
    logging.info("Notificaciones de peligrosos editadas correctamente.")
    driver.quit()

if __name__ == "__main__":
    main()