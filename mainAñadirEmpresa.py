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
import loggerConfig
import logging
import webConfiguration
import pandas
import excelFunctions
import webFunctions
import funcionesNubelus  # Módulo específico para la aplicación Nubelus


# URLs de la aplicación Nubelus
WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_ENTIDAD = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"
WEB_NUBELUS_ACUERDOS = "https://portal.nubelus.es/?clave=waster2_gestionAcuerdosRepresentacion&pAccion=NUEVO"
WEB_NUBELUS_USUARIO = "https://portal.nubelus.es/?clave=nubelus_gestionUsuarios&pAccion=NUEVO"
WEB_NUBELUS_CENTROS = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientalesCentros&pAccion=NUEVO"
def main():
  # Configurar el driver de Selenium
  driver = webConfiguration.configure()

  # Iniciar sesión en Nubelus
  funcionesNubelus.iniciar_sesion(driver)
  time.sleep(5) # Tiempo para aceptar el pop up de google

  excel_empresa = pandas.read_excel(excelFunctions.EXCEL_RECOGIDAS)

  empresa_prueba = excel_empresa.iloc[0] # Toma la fila del Excel como empresa de prueba
  excelFunctions.añadir_empresa(driver, empresa_prueba)
  
  
  excelFunctions.añadir_centro(driver, empresa_prueba)
  # funcionesNubelus.crear_proveedor(driver)
  # time.sleep(1)
  # funcionesNubelus.crear_cliente(driver)
  # excelFunctions.añadir_usuario(driver, empresa_prueba)
  # funcionesNubelus.entrar_en_centro_medioambiental(driver)
  # excelFunctions.rellenar_datos_medioambientales(driver, empresa_prueba)
  # excelFunctions.añadir_autorizaciones(driver, empresa_prueba) # SACAR TEMA RESIDUOS
  # excelFunctions.añadir_horario(driver, empresa_prueba)
  # webFunctions.abrir_web(driver, WEB_NUBELUS_ACUERDOS)
  # excelFunctions.añadir_acuerdo_representacion(driver, empresa_prueba)
  # webFunctions.abrir_web(driver, WEB_NUBELUS_USUARIO)
  # excelFunctions.añadir_usuario(driver, empresa_prueba)

if __name__ == "__main__":
  main()
