"""
Módulo: certHandler.py

Este módulo contiene funciones para la selección y manejo de certificados utilizando 
la librería uiautomation. Las funcionalidades principales incluyen:

  - _seleccionar_certificado(lista_certificados, nombre_certificado):
      Recorre una lista de controles (certificados) y selecciona aquel que contenga 
      una subcadena específica en su propiedad Name. Hace clic sobre el certificado 
      encontrado y retorna True si la selección fue exitosa.

  - seleccionar_certificado_chrome(nombre_certificado='RICARDO ESCUDE'):
      Función principal que obtiene la ventana de certificados (a través de uiautomationHandler),
      espera a que se muestre el popup "Seleccionar un certificado" y obtiene la lista de 
      certificados. Luego, llama a _seleccionar_certificado para seleccionar el certificado 
      adecuado y por último, realiza un clic en el botón "Aceptar" para confirmar la selección.

Ejemplo de uso:

    if seleccionar_certificado_chrome("FRANCISCO JAVIER"):
        logging.info("Certificado seleccionado y confirmado correctamente.")
    else:
        logging.error("No se pudo seleccionar el certificado.")
"""

import loggerConfig
import uiautomation as auto
import time
import logging

import uiautomationHandler

def _seleccionar_certificado(lista_certificados, nombre_certificado):
    """
    Selecciona el certificado deseado de una lista de certificados.

    Recorre recursivamente la lista de controles (certificados) y busca aquel cuyo 
    atributo Name contenga la subcadena especificada en 'nombre_certificado'. Una vez 
    encontrado, realiza un clic en el certificado y retorna True; de lo contrario, 
    registra un error y retorna False.

    Args:
        lista_certificados (list): Lista de controles obtenidos (ej. DataItemControl) que representan certificados.
        nombre_certificado (str): Subcadena que debe contener el atributo Name del certificado deseado.

    Returns:
        bool: True si se encontró y se hizo clic en el certificado deseado, False en caso contrario.

    Ejemplo:
        found = _seleccionar_certificado(lista_certificados, "FRANCISCO JAVIER")
    """
    cert_encontrado = None
    found = False

    for certificado in lista_certificados:
        time.sleep(1)
        if nombre_certificado in certificado.Name:
            cert_encontrado = certificado
            break

    if cert_encontrado:
        logging.info(f"Certificado encontrado con nombre: {cert_encontrado.Name}")
        logging.info(f"Intentando hacer clic en el certificado: {cert_encontrado.Name}")
        cert_encontrado.Click()
        found = True
    else:
        logging.error(f"No hay certificados con el nombre '{nombre_certificado}'.")

    return found

def seleccionar_certificado_chrome(nombre_certificado='RICARDO ESCUDE'):
    """
    Función principal para obtener la ventana de certificados y seleccionar el certificado deseado.

    Esta función utiliza uiautomationHandler para:
      1. Obtener la ventana de certificados (se asume que es la ventana obtenida mediante obtener_ventana_chrome).
      2. Esperar a que se muestre el popup "Seleccionar un certificado" y obtener la lista de 
         controles que representan los certificados (usando esperar_popup_y_ejecutar y obtener_data_item_control).
      3. Utilizar la función _seleccionar_certificado para buscar y hacer clic en el certificado cuyo 
         atributo Name contenga la subcadena 'nombre_certificado'.
      4. Finalmente, hace clic en el botón "Aceptar" del popup para confirmar la selección.

    Args:
        nombre_certificado (str, optional): Texto o subcadena del nombre del certificado a seleccionar.
                                              Por defecto es 'RICARDO ESCUDE'.

    Returns:
        bool: True si se pudo seleccionar el certificado y se hizo clic en "Aceptar"; False en caso contrario.

    Ejemplo de uso:
        if seleccionar_certificado_chrome("FRANCISCO JAVIER"):
            logging.info("Certificado seleccionado y confirmado correctamente.")
        else:
            logging.error("No se pudo seleccionar el certificado.")
    """
    ventana_chrome = uiautomationHandler.obtener_ventana("Chrome", class_name="Chrome_WidgetWin_1")
    if not ventana_chrome:
        logging.error("No se encontró la ventana de certificados.")
        return False

    # Esperar el popup y obtener la lista de certificados como controles (DataItemControl)
    lista_certificados = uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "Seleccionar un certificado",
        accion=lambda popup: uiautomationHandler.obtener_data_item_control(popup),
        timeout=10
    )
    if lista_certificados is []:
        logging.warning("La lista de certificados está vacía.")
        return False

    logging.info(f"Primer certificado encontrado: {lista_certificados[0].Name if lista_certificados else 'Ninguno'}")

    # Intentar seleccionar el certificado y confirmar haciendo clic en el botón "Aceptar"
    if lista_certificados:
        _seleccionar_certificado(lista_certificados, nombre_certificado)
        uiautomationHandler.click_boton_en_popup(ventana_chrome, "Seleccionar un certificado", "Aceptar")
        return True
    else:
        return False