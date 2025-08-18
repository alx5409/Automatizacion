"""
Módulo: mainEmpresa.py

Este script automatiza el proceso de agregar empresas en la aplicación Nubelus.
El flujo de acciones es el siguiente:
  1. Configura el driver de Selenium y abre la web de Nubelus.
  2. Inicia sesión en Nubelus.
  3. Navega a la sección "Ficheros" y luego a "Entidades medioambientales".
  4. Interactúa con el pop-up para generar el Excel:
       - Clic en el ícono de opciones.
       - Clic en el botón para generar Excel.
       - Espera a que aparezca el pop-up y lo acepta.
  5. Vuelve al menú principal y obtiene las empresas no añadidas desde la información del Excel.
  6. Añade las empresas obtenidas mediante la función correspondiente.

Ejemplo de uso:
    Ejecuta este script para automatizar la adición de empresas en Nubelus.
"""

import time
import excelFunctions
import loggerConfig
import logging
import webConfiguration
import webFunctions
import funcionesNubelus  # Módulo específico para la aplicación Nubelus

# URLs de la aplicación Nubelus
WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_EXCEL = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"

# Configurar el driver de Selenium
driver = webConfiguration.configure()

# Iniciar sesión en Nubelus
funcionesNubelus.iniciar_sesion(driver)
time.sleep(5)

# Navegar a la sección "Entidades medioambientales" a partir del menú "Ficheros"
webFunctions.clickar_boton_por_link(driver, "Ficheros")
webFunctions.clickar_boton_por_link(driver, "Entidades medioambientales")

# Interacción para generar Excel:
# 1. Clic en el botón de opciones (icon-ellipsis-vertical).
webFunctions.clickar_boton_por_clase(driver, "icon-ellipsis-vertical")
# 2. Clic en el botón para generar Excel (por id).
webFunctions.clickar_boton_por_id(driver, "moa_bGenerar_excel")
time.sleep(2)
# 3. Espera a que aparezca el pop-up asociado a la generación del Excel.
webFunctions.esperar_elemento_por_id(driver, "div_relacion2excel")
popup = webFunctions.encontrar_pop_up_por_id(driver, "div_relacion2excel")
# 4. Acepta el pop-up haciendo clic en el botón con la clase "miBoton.aceptar".
webFunctions.aceptar_pop_up(popup, "miBoton.aceptar")

# Navegar al menú principal para continuar el flujo
webFunctions.clickar_boton_por_clase(driver, "navbar.superMenu")

# Obtener las empresas que aún no han sido añadidas (según el Excel recogido)
empresas_añadir = excelFunctions.sacar_empresas_no_añadidas(driver)
# Añadir las empresas obtenidas en el sistema
excelFunctions.añadir_empresa(driver, empresas_añadir)
