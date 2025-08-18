"""
Módulo: uiautomationHandler.py

Este módulo proporciona funciones auxiliares para la interacción con la interfaz de usuario
mediante la librería uiautomation. Permite localizar ventanas, popups y controles específicos,
así como realizar acciones sobre ellos, facilitando la automatización de flujos de trabajo
gráficos como la selección de certificados y la interacción con AutoFirma.

Funcionalidades principales:
  - Buscar y activar la ventana de Google Chrome.
  - Buscar y activar la ventana de diálogo de certificados de Windows.
  - Buscar y hacer clic en botones dentro de popups.
  - Esperar la aparición de popups y ejecutar acciones sobre ellos.
  - Buscar recursivamente controles de tipo DataItemControl.

Ejemplos de uso:

    # Buscar la ventana de Chrome
    ventana_chrome = obtener_ventana_chrome(timeout=10)

    # Hacer clic en un botón "Abrir AutoFirma" dentro de un popup llamado "¿Abrir AutoFirma?"
    click_boton_en_popup(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma", timeout=5)

    # Esperar a que aparezca el popup "Seleccionar un certificado" y obtener los controles DataItemControl
    certificados = esperar_popup_y_ejecutar(
        ventana_chrome,
        "Seleccionar un certificado",
        accion=lambda popup: obtener_data_item_control(popup),
        timeout=10
    )
"""

import loggerConfig
import uiautomation as auto
import time
import logging

def obtener_ventana(nombre_ventana: str, class_name: str = None, timeout: int = 10):
    """
    Busca y activa una ventana por nombre y opcionalmente por class_name.

    Args:
        nombre_ventana (str): Nombre (o parte del nombre) de la ventana a buscar.
        class_name (str, optional): Nombre de la clase de la ventana (ClassName). Si es None, no se filtra por clase.
        timeout (int, optional): Tiempo máximo de espera en segundos. Por defecto 10.

    Returns:
        Control: El control de la ventana encontrada o None si no se encuentra.

    Ejemplo de uso:
        ventana_chrome = obtener_ventana("Chrome", class_name="Chrome_WidgetWin_1", timeout=10)
        ventana_cert = obtener_ventana("Diálogo de seguridad del almacén Windows", timeout=10)
    """
    logging.info(f"Buscando ventana: '{nombre_ventana}'" + (f", class_name: '{class_name}'" if class_name else ""))
    ventana_encontrada = None
    start_time = time.time()
    while not ventana_encontrada and (time.time() - start_time) < timeout:
        for ventana in auto.GetRootControl().GetChildren():
            if nombre_ventana in ventana.Name and (class_name is None or ventana.ClassName == class_name):
                ventana_encontrada = ventana
                break
        time.sleep(0.5)

    if ventana_encontrada:
        logging.info(f"Ventana encontrada: {ventana_encontrada.Name}")
        ventana_encontrada.SetActive()
        return ventana_encontrada
    else:
        logging.error(f"No se encontró la ventana '{nombre_ventana}'.")
        return None

def click_boton_en_popup(ventana_principal, popup_name: str, button_name: str, timeout: int = 5) -> bool:
    """
    Busca y hace clic en un botón específico dentro de un popup dado.

    Args:
        ventana_principal: Control de la ventana sobre la cual se buscará el popup.
        popup_name (str): Nombre del popup a buscar.
        button_name (str): Nombre del botón a clickar dentro del popup.
        timeout (int, optional): Tiempo máximo de espera en segundos. Por defecto 5.

    Returns:
        bool: True si se encontró y se hizo clic en el botón; False en caso contrario.

    Ejemplo de uso:
        click_boton_en_popup(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma", timeout=5)
    """
    logging.info(f"Buscando botón '{button_name}' en popup '{popup_name}'...")
    popup = ventana_principal.Control(
        searchDepth=20,
        ControlType=auto.ControlType.CustomControl,
        Name=popup_name
    )
    if popup.Exists(maxSearchSeconds=timeout):
        boton = popup.ButtonControl(Name=button_name)
        if boton.Exists(maxSearchSeconds=timeout):
            logging.info(f"¡Botón '{button_name}' encontrado! Haciendo click...")
            boton.Click()
            return True
        else:
            logging.error(f"No se encontró el botón '{button_name}' en el popup '{popup_name}'.")
            return False
    else:
        logging.error(f"No se encontró el popup '{popup_name}' para buscar el botón '{button_name}'.")
        return False

def esperar_popup_y_ejecutar(ventana_principal, popup_name: str, accion: callable = None, timeout: int = 10):
    """
    Espera a que se muestre un popup (definido por su Name) en la ventana y,
    si se encuentra, ejecuta la función 'accion' pasándole el control del popup.

    Args:
        ventana_principal: Control de la ventana obtenido por uiautomation.
        popup_name (str): Nombre del popup a esperar.
        accion (callable, optional): Función que se ejecutará pasando el popup como argumento.
                                     Si no se proporciona, se devuelve el control del popup.
        timeout (int, optional): Tiempo máximo de espera en segundos. Por defecto 10.

    Returns:
        Si se define 'accion': devuelve el resultado de la acción.
        Si no se define 'accion': devuelve el control del popup.
        En caso de error (no se encuentra el popup) se devuelve None.

    Ejemplo de uso:
        # Hacer click en "Abrir AutoFirma" en un popup llamado "¿Abrir AutoFirma?"
        esperar_popup_y_ejecutar(
            ventana_chrome,
            "¿Abrir AutoFirma?",
            accion=lambda popup: click_boton_en_popup(ventana_chrome, "¿Abrir AutoFirma?", "Abrir AutoFirma", timeout=5),
            timeout=10
        )
    """
    logging.info(f"Esperando popup '{popup_name}'...")
    popup = None
    start_time = time.time()
    while not popup and (time.time() - start_time) < timeout:
        popup = ventana_principal.Control(
            searchDepth=20,
            ControlType=auto.ControlType.CustomControl,
            Name=popup_name
        )
        if not popup.Exists():
            popup = None
            time.sleep(0.5)
    if popup:
        logging.info(f"Popup '{popup_name}' detectado.")
        if accion is not None:
            return accion(popup)
        else:
            return popup
    else:
        logging.error(f"No se encontró el popup '{popup_name}'.")
        return None

def obtener_data_item_control(control):
    """
    Busca recursivamente controles de tipo DataItemControl dentro de un control.

    Args:
        control: Control en el cual se realizará la búsqueda.

    Returns:
        list: Una lista de controles de tipo DataItemControl encontrados dentro de 'control'.

    Ejemplo de uso:
        data_items = obtener_data_item_control(control_principal)
    """
    data_items = []
    for hijo in control.GetChildren():
        logging.debug(f"{hijo.ControlTypeName}")
        if hijo.ControlTypeName == 'DataItemControl':
            data_items.append(hijo)
        else:
            data_items.extend(obtener_data_item_control(hijo))
    return data_items