"""
Módulo: mainPopUpAutorizacion.py

Este script automatiza la interacción con la aplicación Nubelus,
específicamente en la gestión de autorizaciones de centros de entidades medioambientales.

Flujo de acciones:
  1. Inicia sesión en Nubelus.
  2. Navega a la sección "Ficheros" y luego a "Centros de entidades medioambientales".
  3. Selecciona el registro de "ECO TITAN S.L.".
  4. Selecciona la opción "Autorizaciones" en el menú desplegable.
  5. Hace clic en el botón "Añadir autorización" para abrir el formulario (pop-up).
  6. Rellena los campos del formulario:
       - Campo "pAutorizacion_medioambiental": se escribe "Autorizacion".
       - Campo "pDenominacion": se escribe "Denominacion".
       - Campo de autocompletar: se escribe "P04" y se simula pulsar ENTER.
  7. Finalmente, se hace clic en el botón de cancelar para cerrar el pop-up.

Ejemplo de uso:
  Ejecuta este script para realizar el flujo de autorización automáticamente.
"""

import os
import time
import logging
import pandas
import uiautomation as auto
import certHandler
import excelFunctions
import loggerConfig
import webConfiguration
import webFunctions
import funcionesNubelus
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URLs de la aplicación Nubelus
WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_EXCEL = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"

# Configurar el driver de Selenium
driver = webConfiguration.configure()

# Iniciar sesión en Nubelus
funcionesNubelus.iniciar_sesion(driver)
time.sleep(5)

# Navegar a la sección de "Centros de entidades medioambientales" desde "Ficheros"
webFunctions.clickar_boton_por_link(driver, "Ficheros")
webFunctions.clickar_boton_por_link(driver, "Centros de entidades medioambientales")

# Seleccionar el registro "ECO TITAN S.L." y la sección "Autorizaciones"
webFunctions.clickar_boton_por_texto_registro(driver, "ECO TITAN S.L.")
webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Autorizaciones")

# Abrir el formulario (pop-up) para añadir una autorización
webFunctions.clickar_boton_por_texto(driver, "Añadir autorización")

# Buscar el pop-up donde se introduce la nueva autorización
popup = webFunctions.encontrar_pop_up_por_id(driver, "div_nuevo_AUTORIZACIONES")

# Rellenar el formulario del pop-up:
# Escribir en el campo "pAutorizacion_medioambiental"
webFunctions.escribir_en_elemento_por_name(popup, "pAutorizacion_medioambiental", "Autorizacion")
# Escribir en el campo "pDenominacion"
webFunctions.escribir_en_elemento_por_name(popup, "pDenominacion", "Denominacion")
# Escribir en el campo de autocompletar (se utiliza una clase única, "ui-autocomplete-input")
webFunctions.completar_campo_y_confirmar_seleccion_por_class(popup, "ui-autocomplete-input", "P04", "ui-a-value")
# Clic en el botón de cancelar para cerrar el pop-up sin confirmar el alta
webFunctions.clickar_boton_por_clase(popup, "miBoton.cancelar")
