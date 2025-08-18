"""
Módulo: autoFirmaHandler.py

Este módulo proporciona funciones para la automatización del proceso de firma digital mediante AutoFirma,
utilizando la librería uiautomation y funciones auxiliares de uiautomationHandler.

Funcionalidades principales:
  - Imprimir los títulos de las ventanas abiertas en el sistema.
  - Recorrer y mostrar la jerarquía de controles de una ventana para depuración.
  - Obtener recursivamente todos los controles de tipo RadioButton.
  - Seleccionar un certificado específico y confirmar la selección en el diálogo de seguridad de Windows.
  - Orquestar el flujo completo de interacción con AutoFirma, incluyendo la gestión de popups y selección de certificados.

Ejemplo de uso:

    # Para seleccionar un certificado y confirmar en AutoFirma:
    if seleccionar_certificado(ventana_cert, "FRANCISCO JAVIER"):
        logging.info("Certificado seleccionado y confirmado correctamente.")
    else:
        logging.error("No se pudo seleccionar el certificado.")

    # Para iniciar el proceso de firma a través de AutoFirma:
    firmar_en_autofirma()
"""

import logging
import time
import loggerConfig
import uiautomation
import uiautomationHandler

def enviar_enter_a_ventana(ventana_control):
    """
    Envía la tecla Enter al WindowControl especificado.

    Args:
        ventana_control: Control de ventana (WindowControl) de uiautomation.
    """
    if ventana_control and ventana_control.Exists():
        ventana_control.SetActive()
        ventana_control.Click()
        time.sleep(1)  # Espera breve para asegurar que la ventana está activa
        uiautomation.SendKeys('{Tab}')
        time.sleep(1)  # Espera breve para asegurar que la ventana está activa
        uiautomation.SendKeys('{Enter}')
        logging.info("Se envió Enter a la ventana activa.")
    else:
        logging.error("No se encontró la ventana o no está activa para enviar Enter.")

def mostrar_arbol_elementos(control, nivel=0):
    """
    Recorre recursivamente un control y sus hijos, mostrando TypeName y Name en logging.warning(),
    con indentación para visualizar la jerarquía.

    Args:
        control: Control raíz de uiautomation.
        nivel (int): Nivel de profundidad para indentación visual.
    """
    if not control:
        logging.warning("Control no encontrado o es None.")
        return
    indent = "  " * nivel
    logging.warning(f"{indent}{control.ControlTypeName} | Name: {control.Name}")
    for hijo in control.GetChildren():
        mostrar_arbol_elementos(hijo, nivel + 1)

def listar_elementos(control, nivel=0):
    """
    Recorre recursivamente un control y sus hijos, mostrando TypeName y Name en logging.warning().

    Args:
        control: Control raíz de uiautomation.
        nivel (int): Nivel de profundidad para indentación visual.
    """
    if not control:
        logging.warning("Control no encontrado o es None.")
        return
    indent = "  " * nivel
    logging.warning(f"{indent}{control.ControlTypeName}: {control.Name}")
    for hijo in control.GetChildren():
        listar_elementos(hijo, nivel + 1)

def print_open_windows_titles():
    """
    Imprime el título de todas las ventanas abiertas en el sistema.

    Recorre las ventanas hijas del control raíz de uiautomation y escribe el título de cada una.

    Ejemplo de uso:
        print_open_windows_titles()
    """
    for w in uiautomation.GetRootControl().GetChildren():
        logging.warning(f'Window: {w.Name}')

def _obtener_radio_buttons(control):
    """
    Recorre recursivamente un control y devuelve todos los controles de tipo RadioButton.

    Args:
        control: Control en el cual se realizará la búsqueda de RadioButton.

    Returns:
        list: Lista de controles de tipo RadioButton encontrados.

    Ejemplo de uso:
        radios = _obtener_radio_buttons(ventana_cert)
    """
    radios = []
    for child in control.GetChildren():
        if child.ControlTypeName == 'RadioButton':
            radios.append(child)
        else:
            radios.extend(_obtener_radio_buttons(child))
    return radios

def seleccionar_certificado(ventana_cert, nombre_certificado="FRANCISCO JAVIER"):
    """
    Selecciona el certificado que contenga la subcadena especificada en el parámetro nombre_certificado,
    utilizando los controles DataItemControl obtenidos mediante uiautomationHandler, y hace clic en 
    el botón "Aceptar" del popup "Diálogo de seguridad de almacén Windows".

    Args:
        ventana_cert: Control de la ventana de certificados.
        nombre_certificado (str, optional): Subcadena que debe contener el nombre del certificado. 
                                            Por defecto "FRANCISCO JAVIER".

    Returns:
        bool: True si se pudo seleccionar el certificado y se hizo clic en "Aceptar"; False en caso contrario.

    Ejemplo de uso:
        if seleccionar_certificado(ventana_cert, "FRANCISCO JAVIER"):
            logging.info("Certificado seleccionado y confirmado correctamente.")
        else:
            logging.error("No se pudo seleccionar el certificado.")
    """
    if not ventana_cert:
        logging.error("No se encontró la ventana de certificado.")
        return False
    
    # Obtener todos los controles tipo DataItemControl (se asume que representan los certificados)
    boton = uiautomationHandler.obtener_data_item_control(ventana_cert)
    if not boton:
        logging.error("No se encontraron controles de certificado.")
        return False

    if boton:
        logging.info(f"Certificado encontrado: {boton.Name}. Seleccionándolo...")
        boton.Click()
        return True
    else:
        logging.error(f"No se encontró un certificado que contenga '{boton}'.")
        return False

def firmar_en_autofirma():
    """
    Inicia el proceso de firma en AutoFirma.

    Utiliza uiautomationHandler para:
      1. Obtener la ventana de Chrome.
      2. Esperar y hacer clic en el popup "¿Abrir AutoFirma?" mediante un callback.
      3. Listar las ventanas abiertas para diagnóstico.
      4. Esperar y ejecutar la selección del certificado a través del popup "Diálogo de seguridad del almacén Windows".
      5. Finalmente, vuelve a intentar la selección del certificado para continuar el proceso de firma.

    Ejemplo de uso:
        firmar_en_autofirma()
    """
    ventana_chrome = uiautomationHandler.obtener_ventana("Chrome", class_name="Chrome_WidgetWin_1")
    # Esperar el popup "¿Abrir AutoFirma?" y hacer clic en el botón "Abrir AutoFirma"
    uiautomationHandler.esperar_popup_y_ejecutar(
        ventana_chrome,
        "¿Abrir AutoFirma?",
        accion=lambda popup: uiautomationHandler.click_boton_en_popup(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma"),
        timeout=10
    )
    # Esperar el popup "Diálogo de seguridad del almacén Windows" y ejecutar la selección de certificado
    time.sleep(5)
    ventana_dialogo = uiautomationHandler.obtener_ventana("Diálogo de seguridad del almacén Windows")
    enviar_enter_a_ventana(ventana_dialogo)
    time.sleep(100)
    
    