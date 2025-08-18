"""
Módulo: webFunctions.py

Este módulo contiene funciones auxiliares para interactuar con elementos web utilizando Selenium WebDriver.
Las funcionalidades incluyen:
  - Abrir una URL en el navegador.
  - Esperar a que un elemento sea visible.
  - Hacer clic en elementos mediante diversas estrategias de localización.
  - Escribir texto en campos de entrada.
  - Seleccionar opciones en un <select>.
  - Manejar ventanas/pestañas y alertas.
  - Capturar pantallas y obtener logs del navegador.
  
Cada función incluye documentación sobre sus parámetros, lo que retorna o si lanza excepciones.
"""

import glob
import logging
import os
import unicodedata
import time
from typing import Union, Optional, List, Dict
from selenium import webdriver
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

# Tiempo de espera global (en segundos)
DEFAULT_TIMEOUT = 5

def abrir_web(driver: webdriver.Chrome, url: str) -> None:
    """
    Abre la URL especificada en el navegador.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        url (str): URL a abrir.

    Ejemplo:
        abrir_web(driver, "https://example.com")
    """
    driver.get(url)
    logging.info(f"Web '{url}' abierta.")

def esperar_elemento(driver: webdriver.Chrome, by: By, value: str, timeout: int = DEFAULT_TIMEOUT) -> WebDriverWait:
    """
    Espera hasta que un elemento sea visible en la página utilizando la estrategia de localización especificada.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        by (By): Estrategia de localización (By.ID, By.XPATH, By.CSS_SELECTOR, etc.).
        value (str): Valor del selector.
        timeout (int, optional): Tiempo máximo de espera en segundos. Valor por defecto: DEFAULT_TIMEOUT.

    Returns:
        WebDriverWait: Objeto wait si el elemento es encontrado.

    Raises:
        TimeoutException: Si el elemento no se encuentra dentro del tiempo de espera.
    """
    if not by:
        raise ValueError(f"Estrategia de localización '{by}' no válida.")
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(EC.visibility_of_element_located((by, value)))
        return wait
    except TimeoutException:
        logging.error(f"Timeout al esperar el elemento con '{by}' = '{value}'")
        raise


def encontrar_elemento(driver, by, value, timeout=DEFAULT_TIMEOUT):
    """
    Espera y devuelve un elemento localizado en toda la página.
    Reintenta hasta 5 veces con esperas de 0.5s entre intentos.
    """
    intentos = 5
    for intento in range(intentos):
        try:
            esperar_elemento(driver, by, value, timeout)
            elemento = driver.find_element(by, value)
            logging.info(f"Elemento encontrado con '{by}' = '{value}'.")
            return elemento
        except TimeoutException:
            if intento == intentos - 1:
                raise
        except Exception as e:
            logging.error(f"Falló al encontrar el elemento con '{by}' = '{value}' (intento {intento+1}): {e}")
            if intento == intentos - 1:
                raise
        time.sleep(0.5)

def encontrar_elemento_relativo(elemento, by, value):
    """
    Devuelve un elemento relativo a otro elemento (como find_element sobre un WebElement).
    Recibe la estrategia de localización como objeto By (no como string).
    """
    try:
        elemento_rel = elemento.find_element(by, value)
        logging.info(f"Elemento relativo encontrado con '{by}' = '{value}'.")
        return elemento_rel
    except Exception as e:
        logging.error(f"Falló al encontrar el elemento relativo con '{by}' = '{value}': {e}")
        raise

def encontrar_elementos(driver, by, value, timeout=DEFAULT_TIMEOUT):
    """
    Espera a que al menos un elemento sea visible y devuelve una lista de elementos localizados en toda la página.
    """
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_any_elements_located((by, value)))
        elementos = driver.find_elements(by, value)
        logging.info(f"{len(elementos)} elementos encontrados con '{by}' = '{value}'.")
        return elementos
    except TimeoutException:
        logging.warning(f"No se encontraron elementos con '{by}' = '{value}' en el tiempo especificado.")
        return []
    except Exception as e:
        logging.error(f"Error al buscar elementos con '{by}' = '{value}': {e}")
        return []

def clickar_elemento(driver: webdriver.Chrome, by: By, value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Espera a que un elemento sea visible y realiza un clic en él.
    Reintenta hasta 5 veces con esperas de 0.5s entre intentos.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        by (By): Estrategia de localización del elemento.
        value (str): Valor del selector.
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Raises:
        TimeoutException: Si el elemento no se encuentra en el tiempo especificado.
        Exception: Si ocurre un error al hacer clic.
    """
    intentos = 5
    for intento in range(intentos):
        try:
            esperar_elemento(driver, by, value, timeout)
            elemento = driver.find_element(by, value)
            elemento.click()
            logging.info(f"Elemento clickado con '{by}' = '{value}'.")
            return
        except TimeoutException:
            if intento == intentos - 1:
                raise
        except Exception as e:
            logging.error(f"Falló al clickar el elemento con '{by}' = '{value}' (intento {intento+1}): {e}")
            if intento == intentos - 1:
                raise
        time.sleep(0.5)

def esperar_elemento_por_id(driver: webdriver.Chrome, element_id: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Espera hasta que un elemento con el ID especificado sea visible en la página.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        element_id (str): Valor del atributo id del elemento.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    esperar_elemento(driver, By.ID, element_id, timeout)

def esperar_elemento_por_clase(driver: webdriver.Chrome, clase: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Espera hasta que un elemento con la clase CSS especificada sea visible en la página.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        clase (str): Nombre de la clase CSS.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    selector = f".{clase}"
    esperar_elemento(driver, By.CSS_SELECTOR, selector, timeout)

def clickar_boton_por_id(driver: webdriver.Chrome, id: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un botón o elemento identificable por su atributo ID.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        id (str): Valor del atributo id del botón.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    clickar_elemento(driver, By.ID, id, timeout)

def clickar_boton_por_value(driver: webdriver.Chrome, value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un botón (<input>) que tiene el atributo 'value' especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        value (str): Valor del atributo value del botón.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    selector = f"input[value='{value}']"
    clickar_elemento(driver, By.CSS_SELECTOR, selector, timeout)

def clickar_span_por_texto(driver: webdriver.Chrome, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un elemento <span> que contiene el texto especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        texto (str): Texto contenido en el <span>.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    xpath = f"//span[contains(text(),'{texto}')]"
    clickar_elemento(driver, By.XPATH, xpath, timeout)

def clickar_input_por_texto(driver: webdriver.Chrome, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un elemento <input> que contiene el texto especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        texto (str): Texto contenido en el <input>.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    xpath = f"//input[contains(text(),'{texto}')]"
    clickar_elemento(driver, By.XPATH, xpath, timeout)

def clickar_boton_por_texto(driver: webdriver.Chrome, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un botón (<button>) que contiene el texto especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        texto (str): Texto contenido en el botón.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    
    Ejemplo:
        clickar_boton_por_texto(driver, "Añadir autorización")
    """
    xpath = f"//button[contains(., '{texto}')]"
    clickar_elemento(driver, By.XPATH, xpath, timeout)

def clickar_boton_con_titulo(driver: webdriver.Chrome, titulo: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en cualquier elemento que contenga el atributo title especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        titulo (str): Valor exacto del atributo title que se espera que tenga el elemento.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    xpath = f"//*[@title='{titulo}']"
    clickar_elemento(driver, By.XPATH, xpath, timeout)

def clickar_ui_a_value_por_texto(driver: webdriver.Chrome, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un elemento <div> que contenga exactamente el texto especificado y que tenga la clase "ui-a-value".
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        texto (str): Texto contenido en el <div> que se desea clickar.
        timeout (int, optional): Tiempo máximo de espera en segundos. Valor por defecto DEFAULT_TIMEOUT.
    
    Ejemplo:
        clickar_div_por_texto(driver, "P04")
    """
    xpath = f"//div[contains(@class, 'ui-a-value') and normalize-space(text())='{texto}']"
    clickar_elemento(driver, By.XPATH, xpath, timeout)

def clickar_boton_por_link(driver: webdriver.Chrome, link: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un enlace (<a>) que contenga el texto especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        link (str): Texto del enlace.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    
    Ejemplo:
        clickar_boton_por_link(driver, "Contacto")
    """
    xpath = f"//a[contains(text(), '{link}')]"
    clickar_elemento(driver, By.XPATH, xpath, timeout)

def clickar_todos_los_links(driver: webdriver.Chrome, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en todos los enlaces <a> cuyo texto visible contenga el string especificado,
    utilizando la función clickar_elemento para cada uno.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        texto (str): Texto que debe estar contenido en el texto visible del enlace.
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Ejemplo:
        clickar_todos_los_links(driver, "Descargar")
    """
    try:
        time.sleep(2)  # Espera inicial para que la página cargue
        enlaces = driver.find_elements(By.XPATH, f"//a[contains(text(), '{texto}')]")
        if not enlaces:
            logging.error(f"No se encontraron enlaces con texto '{texto}'.")
            return
        logging.info(f"Encontrados {len(enlaces)} enlaces con texto '{texto}'.")
        for enlace in enlaces:
            enlace_texto = enlace.text.strip().split()[0]
            if enlace:
                try:
                    clickar_elemento(driver, By.XPATH, f"//a[contains(text(), '{enlace_texto}') and contains(text(), '.pdf')]", timeout)
                    time.sleep(2)
                except Exception as e:
                    logging.warning(f"No se pudo hacer clic en el enlace con texto '{enlace_texto}': {e}")
                    continue
    except Exception as e:
        logging.error(f"Error al buscar enlaces con texto '{texto}': {e}")

def clickar_enlace_por_onclick(driver: webdriver.Chrome, onclick_value: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """
    Hace clic en un enlace (<a>) que tenga el atributo onclick con el valor especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        onclick_value (str): Valor exacto del atributo onclick.
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Returns:
        bool: True si se hizo click, False si no se encontró el enlace.
    """
    xpath = f"//a[@onclick=\"{onclick_value}\"]"
    try:
        clickar_elemento(driver, By.XPATH, xpath, timeout)
        print('Click realizado en el enlace con onclick.')
        return True
    except Exception:
        print('ERROR: El enlace con ese onclick NO está presente en la página.')
        return False

def clickar_boton_por_clase(driver: webdriver.Chrome, clase: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en el primer elemento que tenga la clase CSS especificada.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        clase (str): Nombre de la clase CSS.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    selector = f".{clase}"
    clickar_elemento(driver, By.CSS_SELECTOR, selector, timeout)

def clickar_imagen_generar_excel(driver, timeout=20):
    """
    Espera a que la imagen para generar el EXCEL esté presente y sea clickeable, y hace click en ella.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        timeout (int): Tiempo máximo de espera en segundos.

    Returns:
        bool: True si se hizo click, False si no se encontró la imagen.
    """
    try:
        xpath = "//img[@id='imagen_generarPDF_todos' and contains(@title, 'EXCEL')]"
        clickar_elemento(driver, By.XPATH, xpath, timeout)
        logging.info('Click realizado en la imagen para generar el EXCEL.')
        logging.info('Esperando la descarga del EXCEL...')
        return True
    except Exception:
        logging.error('ERROR: No se encontró la imagen para generar el EXCEL.')
        return False

def abrir_link_por_boton_id(driver: webdriver.Chrome, id_boton: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un botón que abre una nueva ventana o pestaña.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        boton (str): Texto del botón.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    
    Ejemplo:
        abrir_ventana_por_boton(driver, "Abrir ventana")
    """
    # Esperar a que el botón esté visible
    esperar_elemento_por_id(driver, id_boton, timeout)
    # Abre el enlace que contiene el botón
    elemento = driver.find_element(By.ID, id_boton)
    enlace_boton = elemento.get_attribute("href")
    abrir_web(driver, enlace_boton)
    logging.info(f"Enlace abierto por el botón: {id_boton}")

def abrir_nueva_pestana(driver: webdriver.Chrome, url: str) -> bool:
    """
    Abre una nueva pestaña con la URL especificada y cambia el foco a ella.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        url (str): URL a abrir en la nueva pestaña.
    
    Returns:
        bool: True si la nueva pestaña se abrió correctamente y se cambió el foco, False en caso contrario.
    
    Ejemplo:
        abrir_nueva_pestana(driver, "https://example.com")
    """
    try:
        handle_actual = driver.current_window_handle
        driver.execute_script(f"window.open('{url}', '_blank');")
        logging.info(f"Se abrió una nueva pestaña con la URL: {url}")
        # Cambiar el foco a la nueva pestaña
        handles = driver.window_handles
        nuevas = [h for h in handles if h != handle_actual]
        if nuevas:
            driver.switch_to.window(nuevas[-1])
            logging.info("Foco cambiado a la nueva pestaña.")
            return True
        else:
            logging.warning("No se detectó una nueva pestaña después de abrirla.")
            return False
    except WebDriverException as e:
        logging.error(f"Error al abrir nueva pestaña con URL '{url}': {e}")
        return False

def cambiar_a_ventana(driver: webdriver.Chrome, indice: int) -> None:
    """
    Cambia el enfoque del navegador a otra ventana o pestaña especificada por su índice.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        indice (int): Índice de la ventana/pestaña a la que se desea cambiar.
    
    Raises:
        IndexError: Si el índice es inválido.
    
    Ejemplo:
        cambiar_a_ventana(driver, 1)
    """
    try:
        handles = driver.window_handles
        driver.switch_to.window(handles[indice])
        logging.info(f"Cambiado a la pestaña '{driver.title}'.")
    except IndexError:
        raise IndexError(f"Índice de ventana inválido: {indice}. Existen {len(driver.window_handles)} ventanas.")
    except NoSuchWindowException as e:
        logging.error(f"No se pudo cambiar a la ventana: {e}")
        raise

def capturar_pantalla(driver: webdriver.Chrome, ruta_archivo: str, timeout: int = 10) -> bool:
    """
    Espera a que la página se cargue completamente y guarda una captura de pantalla en la ubicación especificada.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        ruta_archivo (str): Ruta (incluyendo nombre de archivo) donde se guardará la imagen (.png).
        timeout (int, opcional): Tiempo máximo de espera para la carga de la página en segundos.
    
    Returns:
        bool: True si se realizó la captura, False en caso contrario.
    
    Ejemplo:
        capturar_pantalla(driver, "screenshots/pagina.png")
    """
    try:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        logging.info("La página se cargó completamente antes de la captura.")
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        exito = driver.get_screenshot_as_file(ruta_archivo)
        if exito:
            logging.info(f"Captura de pantalla guardada en: {ruta_archivo}")
        else:
            logging.warning(f"No se pudo guardar la captura en: {ruta_archivo}")
        return exito
    except WebDriverException as e:
        logging.error(f"Error al capturar pantalla: {e}")
        return False
    except Exception as e:
        logging.error(f"Error inesperado al capturar pantalla: {e}")
        return False

def obtener_logs_navegador(driver: webdriver.Chrome) -> List[Dict]:
    """
    Obtiene los logs del navegador (nivel 'browser').

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
    
    Returns:
        List[Dict]: Lista de entradas de log del navegador.
    
    Nota:
        Es necesario habilitar los logs al iniciar el navegador (utilizar la capacidad 'goog:loggingPrefs').
    """
    try:
        logs = driver.get_log("browser")
        return logs
    except WebDriverException as e:
        logging.error(f"No se pudieron obtener los logs del navegador: {e}")
        return []

def escribir_en_elemento(driver: webdriver.Chrome, by: By, value: str, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Ubica un elemento en la página y escribe el texto especificado en él.
    Reintenta hasta 5 veces con esperas de 0.5s entre intentos.
    """
    intentos = 5
    for intento in range(intentos):
        try:
            esperar_elemento(driver, by, value, timeout)
            elemento = driver.find_element(by, value)
            elemento.clear()
            elemento.send_keys(texto)
            logging.info(f"Se escribió texto en el elemento localizado por {by}='{value}': '{texto}'")
            return
        except TimeoutException:
            if intento == intentos - 1:
                raise
        except Exception as e:
            logging.error(f"Error al escribir en el elemento con {by}='{value}' (intento {intento+1}): {e}")
            if intento == intentos - 1:
                raise
        time.sleep(0.5)

def escribir_en_elemento_por_id(driver: webdriver.Chrome, element_id: str, texto: str) -> None:
    """
    Escribe en un elemento identificado por su ID.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        element_id (str): ID del elemento.
        texto (str): Texto a escribir.
        
    Ejemplo:
        escribir_en_elemento_por_id(driver, "usuario", "admin")
    """
    try:
        escribir_en_elemento(driver, By.ID, element_id, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el elemento con ID '{element_id}': {e}")
        raise

def escribir_en_elemento_por_id_y_enter(driver: webdriver.Chrome, element_id: str, texto: str) -> None:
    """
    Escribe en un elemento identificado por su ID y pulsa Enter después de escribir.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        element_id (str): ID del elemento.
        texto (str): Texto a escribir.

    Ejemplo:
        escribir_en_elemento_por_id_y_enter(driver, "usuario", "admin")
    """
    try:
        escribir_en_elemento(driver, By.ID, element_id, texto)
        input_element = driver.find_element(By.ID, element_id)
        input_element.send_keys(Keys.ENTER)
        logging.info(f"Se escribió texto y se pulsó Enter en el elemento con ID '{element_id}'.")
    except Exception as e:
        logging.error(f"No se pudo escribir y pulsar Enter en el elemento con ID '{element_id}': {e}")
        raise

def escribir_en_elemento_por_name(driver: webdriver.Chrome, name: str, texto: str) -> None:
    """
    Escribe en un elemento identificado por el atributo name.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        name (str): Valor del atributo name del elemento.
        texto (str): Texto a escribir.
    
    Ejemplo:
        escribir_en_elemento_por_name(driver, "usuario", "admin")
    """
    try:
        escribir_en_elemento(driver, By.NAME, name, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el elemento con name '{name}': {e}")
        raise

def escribir_en_elemento_por_name_y_enter(driver: webdriver.Chrome, name: str, texto: str) -> None:
    """
    Escribe en un elemento identificado por el atributo name y pulsa Enter después de escribir.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        name (str): Valor del atributo name del elemento.
        texto (str): Texto a escribir.

    Ejemplo:
        escribir_en_elemento_por_name_y_enter(driver, "usuario", "admin")
    """
    try:
        escribir_en_elemento(driver, By.NAME, name, texto)
        input_element = driver.find_element(By.NAME, name)
        input_element.send_keys(Keys.ENTER)
        logging.info(f"Se escribió texto y se pulsó Enter en el elemento con name '{name}'.")
    except Exception as e:
        logging.error(f"No se pudo escribir y pulsar Enter en el elemento con name '{name}': {e}")
        raise

def escribir_en_elemento_por_name_y_enter_pausa(driver: webdriver.Chrome, name: str, texto: str) -> None:
    """
    Escribe en un elemento identificado por el atributo name y pulsa Enter después de escribir.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        name (str): Valor del atributo name del elemento.
        texto (str): Texto a escribir.

    Ejemplo:
        escribir_en_elemento_por_name_y_enter(driver, "usuario", "admin")
    """
    try:
        escribir_en_elemento(driver, By.NAME, name, texto)
        input_element = driver.find_element(By.NAME, name)
        time.sleep(2)
        input_element.send_keys(Keys.ENTER)
        logging.info(f"Se escribió texto y se pulsó Enter en el elemento con name '{name}'.")
    except Exception as e:
        logging.error(f"No se pudo escribir y pulsar Enter en el elemento con name '{name}': {e}")
        raise

def escribir_en_elemento_por_placeholder(driver: webdriver.Chrome, placeholder_text: str, texto: str) -> None:
    """
    Escribe en un campo de entrada localizado por su atributo placeholder.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        placeholder_text (str): Valor del atributo placeholder.
        texto (str): Texto a escribir.
    
    Ejemplo:
        escribir_en_elemento_por_placeholder(driver, "Teclea para buscar", "resultado")
    """
    try:
        xpath = f"//*[@placeholder='{placeholder_text}']"
        escribir_en_elemento(driver, By.XPATH, xpath, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el elemento con placeholder '{placeholder_text}': {e}")
        raise

def escribir_en_elemento_por_class(driver: webdriver.Chrome, class_name: str, texto: str) -> None:
    """
    Escribe en un elemento localizado por su clase CSS.

    Nota: Si el elemento posee múltiples clases, asegúrate de pasar una única clase.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        class_name (str): Nombre de la clase CSS.
        texto (str): Texto a escribir.
    
    Ejemplo:
        escribir_en_elemento_por_class(driver, "input-search", "Buscar")
    """
    try:
        escribir_en_elemento(driver, By.CLASS_NAME, class_name, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el elemento con class '{class_name}': {e}")
        raise

def escribir_en_elemento_por_label(driver: webdriver.Chrome, input: str, texto: str) -> None:
    """
    Escribe en un campo de entrada localizado por el texto de su etiqueta <label>.

    Busca un <input> que esté dentro de un <label> cuyo <span> contenga el texto especificado.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        input (str): Texto contenido en el <span> de la etiqueta <label>.
        texto (str): Texto a escribir en el campo de entrada.

    Ejemplo:
        escribir_en_elemento_por_label(driver, "Fecha de nacimiento", "01/01/2000")
    """
    try:
        xpath = f"//label[span[contains(text(), '{input}')]]//input"
        escribir_en_elemento(driver, By.XPATH, xpath, texto)
    except Exception as e:
        logging.error(f"No se pudo escribir en el input asociado al label '{input}': {e}")
        raise

def aceptarAlerta(driver: webdriver.Chrome) -> None:
    """
    Espera a que aparezca una alerta en el navegador y la acepta.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
    
    Ejemplo:
        aceptarAlerta(driver)
    """
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        logging.info("Alerta aceptada correctamente.")
    except TimeoutException:
        logging.error("No hay alerta presente para aceptar.")

def seleccionar_elemento(driver: webdriver.Chrome, by: By, value: str, opcion: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Selecciona una opción en un elemento <select> basándose en el texto visible.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        by (By): Estrategia de localización para el <select> (By.ID, By.NAME, etc.).
        value (str): Valor del selector del <select>.
        opcion (str): Texto visible de la opción a seleccionar.
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Ejemplo:
        seleccionar_elemento(driver, By.ID, "pais", "España")
    """
    try:
        esperar_elemento(driver, by, value, timeout)
        elemento = driver.find_element(by, value)
        select_obj = Select(elemento)
        select_obj.select_by_visible_text(opcion)
        logging.info(f"Opción '{opcion}' seleccionada en el elemento con '{by}' = '{value}'.")
    except TimeoutException:
        raise
    except Exception as e:
        logging.error(f"Falló al seleccionar la opción '{opcion}' en el elemento con '{by}' = '{value}': {e}")
        raise

def seleccionar_elemento_por_link_text(driver: webdriver.Chrome, select_id: str, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Selecciona una opción de un <select> identificado por su ID, usando el texto visible.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        select_id (str): ID del elemento <select>.
        texto (str): Texto visible de la opción a seleccionar.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    seleccionar_elemento(driver, By.ID, select_id, texto, timeout)

def seleccionar_elemento_por_class(driver: webdriver.Chrome, class_name: str, texto: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Selecciona una opción en un <select> localizado por su clase CSS usando el texto visible.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        class_name (str): Nombre de la clase CSS del <select>.
        texto (str): Texto visible de la opción a seleccionar.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    seleccionar_elemento(driver, By.CLASS_NAME, class_name, texto, timeout)

def seleccionar_elemento_por_id(driver: webdriver.Chrome, element_id: str, opcion: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Selecciona una opción en un <select> identificado por su ID.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        element_id (str): ID del elemento <select>.
        opcion (str): Texto visible de la opción a seleccionar.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    seleccionar_elemento(driver, By.ID, element_id, opcion, timeout)

def seleccionar_elemento_por_nombre(driver: webdriver.Chrome, name: str, opcion: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Selecciona una opción en un <select> identificado por el atributo name.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        name (str): Valor del atributo name del <select>.
        opcion (str): Texto visible de la opción a seleccionar.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    seleccionar_elemento(driver, By.NAME, name, opcion, timeout)

def seleccionar_elemento_por_name(driver: webdriver.Chrome, name: str, opcion: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Selecciona una opción en un <select> localizado por su tag name utilizando el texto visible.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        tag_name (str): Tag name del <select>.
        opcion (str): Texto visible de la opción a seleccionar.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    seleccionar_elemento(driver, By.NAME, name, opcion, timeout)



def encontrar_pop_up(driver: webdriver.Chrome, by: By, value: str) -> webdriver.remote.webelement.WebElement:
    """
    Busca y retorna un elemento pop-up localizado por la estrategia y valor especificados.

    Args:
        driver (webdriver.Chrome): Instancia activa del navegador.
        by (By): Estrategia de localización (By.ID, By.CLASS_NAME, etc.).
        value (str): Valor del selector.

    Returns:
        WebElement: Elemento WebElement correspondiente al pop-up encontrado.

    Ejemplo:
        popup = encontrar_pop_up(driver, By.ID, "div_modal")
    """
    return driver.find_element(by, value)

def encontrar_pop_up_por_id(driver: webdriver.Chrome, id: str) -> webdriver.remote.webelement.WebElement:
    """
    Busca y retorna un elemento pop-up localizado por su atributo ID.

    Args:
        driver (webdriver.Chrome): Instancia activa del navegador.
        id (str): ID del elemento pop-up a buscar.

    Returns:
        WebElement: Elemento WebElement correspondiente al pop-up encontrado.

    Ejemplo:
        popup = encontrar_pop_up_por_id(driver, "div_modal")
    """
    return driver.find_element(By.ID, id)

def encontrar_pop_up_por_clase(driver: webdriver.Chrome, clase: str) -> webdriver.remote.webelement.WebElement:
    """
    Busca y retorna un elemento pop-up localizado por su clase CSS.

    Args:
        driver (webdriver.Chrome): Instancia activa del navegador.
        clase (str): Clase CSS del elemento pop-up a buscar.

    Returns:
        WebElement: Elemento WebElement correspondiente al pop-up encontrado.

    Ejemplo:
        popup = encontrar_pop_up_por_clase(driver, "mi-clase-popup")
    """
    return driver.find_element(By.CLASS_NAME, clase)

def aceptar_pop_up(popup_div: webdriver.Chrome, boton: str) -> None:
    """
    Hace clic en un botón de aceptación dentro de un pop-up.
    
    Args:
        popup_div (webdriver.Chrome): Elemento contenedor del pop-up.
        boton (str): Clase CSS del botón a presionar.
    
    Ejemplo:
        aceptar_pop_up(popup_div, "miBoton.aceptar")
    """
    clickar_boton_por_clase(popup_div, boton)

def abrir_link_por_boton_id(driver: webdriver.Chrome, id_boton: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un botón identificado por su ID y abre el enlace asociado en la misma pestaña.

    Utiliza la función esperar_elemento_por_id para esperar a que el botón esté visible,
    obtiene el atributo 'href' del botón y navega a esa URL usando abrir_web.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        id_boton (str): ID del botón que contiene el enlace.
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Ejemplo:
        abrir_link_por_boton_id(driver, "btnAbrirEnlace")
    """
    esperar_elemento_por_id(driver, id_boton, timeout)
    elemento = driver.find_element(By.ID, id_boton)
    enlace = elemento.get_attribute("href")
    if not enlace:
        logging.error(f"El botón con ID '{id_boton}' no contiene un atributo 'href'.")
        raise ValueError(f"El botón con ID '{id_boton}' no contiene un enlace.")
    abrir_web(driver, enlace)
    logging.info(f"Enlace '{enlace}' abierto por el botón con ID '{id_boton}'.")

def esperar_y_obtener_texto(driver, by, value, timeout=DEFAULT_TIMEOUT):
    """
    Espera a que un elemento sea visible y devuelve su texto.
    """
    try:
        esperar_elemento(driver, by, value, timeout)
        elemento = driver.find_element(by, value)
        texto = elemento.text
        logging.info(f"Texto obtenido: {texto}")
        return texto
    except Exception as e:
        logging.error(f"Error al obtener texto del elemento con '{by}' = '{value}': {e}")
        return ""

def obtener_texto_elemento_por_id(driver: webdriver.Chrome, elemento_id: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Obtiene el texto de un elemento <span> dentro de un elemento identificado por su ID, dentro de un iframe.
    """
    try:
        iframe = encontrar_elemento(driver, By.TAG_NAME, "iframe", timeout)
        driver.switch_to.frame(iframe)
        xpath = f"//*[@id='{elemento_id}']//span"
        elemento = encontrar_elemento(driver, By.XPATH, xpath, timeout)
        texto = elemento.text
        logging.info(f"Texto obtenido del elemento con ID '{elemento_id}': {texto}")
        return texto
    finally:
        driver.switch_to.default_content()

def obtener_texto_por_parte(driver: webdriver.Chrome, parte_texto: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    Busca un elemento que contenga una parte del texto especificado y devuelve la cadena de texto completa de ese elemento.
    Reintenta hasta 3 veces con esperas de 0.5s entre intentos.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        parte_texto (str): Fragmento del texto a buscar dentro de los elementos.
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Returns:
        str or None: El texto completo del elemento encontrado, o None si no se encuentra.

    Ejemplo:
        texto = buscar_texto_por_parte(driver, "Ejemplo de texto")
    """
    intentos = 3
    for intento in range(intentos):
        try:
            xpath = f"//*[contains(text(), '{parte_texto}')]"
            esperar_elemento(driver, By.XPATH, xpath, timeout)
            elemento = driver.find_element(By.XPATH, xpath)
            texto_completo = elemento.text
            logging.info(f"Texto encontrado que contiene '{parte_texto}': {texto_completo}")
            return texto_completo
        except Exception as e:
            logging.error(f"No se encontró ningún elemento que contenga '{parte_texto}' (intento {intento+1}): {e}")
            if intento == intentos - 1:
                return None
        time.sleep(1)

def leer_texto_por_campo(driver, campo, timeout=5):
    """
    Busca un <td> que contenga un <b> con el texto 'campo' y devuelve el texto que sigue a ese campo.
    Si no lo encuentra, devuelve None.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        campo (str): Texto exacto del campo a buscar (incluyendo los dos puntos).
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Returns:
        str: El texto encontrado después del campo, o None si no se encuentra.
    """
    try:
        xpath = f"//td[b[normalize-space(text())='{campo}']]"
        td = encontrar_elemento(driver, By.XPATH, xpath, timeout)
        texto_completo = td.text
        if texto_completo.startswith(campo):
            valor = texto_completo[len(campo):].strip()
        else:
            valor = texto_completo.split(f"{campo}", 1)[-1].strip()
        return valor if valor else None
    except Exception as e:
        logging.error(f"Error al leer el campo '{campo}': {e}")
        return None

def leer_texto_por_campo_indice(driver, campo, indice=0, timeout=5):
    """
    Igual que leer_texto_por_campo, pero permite elegir el índice del elemento encontrado.
    """
    try:
        xpath = f"(//td[b[normalize-space(text())='{campo}']])[{indice+1}]"
        td = encontrar_elemento(driver, By.XPATH, xpath, timeout)
        texto_completo = td.text
        if texto_completo.startswith(campo):
            valor = texto_completo[len(campo):].strip()
        else:
            valor = texto_completo.split(f"{campo}", 1)[-1].strip()
        return valor if valor else None
    except Exception as e:
        logging.error(f"Error al leer el campo '{campo}' (índice {indice}): {e}")
        return None

def completar_campo_y_confirmar_seleccion(driver: webdriver.Chrome, buscar_por: By, locator: str, texto: str, boton_confirmacion_locator: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Ingresa un valor en un campo (usando el método especificado y locator),
    espera un breve lapso y luego hace click en un botón de confirmación identificado por su locator.

    Args:
        driver (webdriver.Chrome): Instancia del WebDriver.
        buscar_por (By): Método de búsqueda para el campo (By.NAME, By.ID, etc.).
        locator (str): Valor del locator para el campo.
        texto (str): Texto a ingresar.
        boton_confirmacion_locator (str): Valor del locator del botón de confirmación (se asume se buscará por clase).
        delay (int, optional): Tiempo en segundos a esperar antes del click. Por defecto es 1.

    Raises:
        Exception: Si ocurre algún error en alguna de las acciones.
    """
    escribir_en_elemento(driver, buscar_por, locator, texto, timeout)
    time.sleep(1)
    clickar_boton_por_clase(driver, boton_confirmacion_locator, timeout)

def completar_campo_y_confirmar_seleccion_por_name(driver: webdriver.Chrome, nombre: str, texto: str, boton_confirmacion_locator: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Wrapper que completa un campo identificado por su atributo name y confirma la selección.

    Args:
        driver (webdriver.Chrome): Instancia del WebDriver.
        nombre (str): Valor del atributo name del campo.
        texto (str): Texto a ingresar.
        boton_confirmacion_locator (str): Clase CSS del botón de confirmación.
        delay (int, optional): Tiempo en segundos a esperar antes de hacer click.
    """
    completar_campo_y_confirmar_seleccion(driver, By.NAME, nombre, texto, boton_confirmacion_locator, timeout)

def completar_campo_y_confirmar_seleccion_por_id(driver: webdriver.Chrome, id_value: str, texto: str, boton_confirmacion_locator: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Wrapper que completa un campo identificado por su atributo id y confirma la selección.

    Args:
        driver (webdriver.Chrome): Instancia del WebDriver.
        id_value (str): Valor del atributo id del campo.
        texto (str): Texto a ingresar.
        boton_confirmacion_locator (str): Clase CSS del botón de confirmación.
        delay (int, optional): Tiempo en segundos a esperar antes de hacer click.
    """
    completar_campo_y_confirmar_seleccion(driver, By.ID, id_value, texto, boton_confirmacion_locator, timeout)

def completar_campo_y_confirmar_seleccion_por_class(driver: webdriver.Chrome, class_name: str, texto: str, boton_confirmacion_locator: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Wrapper que completa un campo identificado por su clase CSS y confirma la selección.

    Args:
        driver (webdriver.Chrome): Instancia del WebDriver.
        class_name (str): Nombre de la clase CSS del campo.
        texto (str): Texto a ingresar.
        boton_confirmacion_locator (str): Clase CSS del botón de confirmación.
        delay (int, optional): Tiempo en segundos a esperar antes de hacer click.
    """
    completar_campo_y_confirmar_seleccion(driver, By.CLASS_NAME, class_name, texto, boton_confirmacion_locator, timeout)

def completar_campo_y_enter_por_name(driver, campo_name, valor):
    """
    Completa un campo de formulario identificado por su atributo 'name' y simula la pulsación de la tecla Enter.

    Args:
        driver (selenium.webdriver): Instancia del controlador del navegador.
        campo_name (str): Valor del atributo 'name' del campo de formulario a completar.
        valor (str): Texto que se desea ingresar en el campo.
    """
    escribir_en_elemento_por_name(driver, campo_name, valor)
    time.sleep(1.5)
    pulsar_enter_en_elemento_por_name(driver, campo_name)

def pulsar_enter_en_elemento(driver: webdriver.Chrome, by: By, value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Espera a que un elemento sea visible y pulsa la tecla Enter sobre él.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        by (By): Estrategia de localización del elemento (By.ID, By.NAME, etc.).
        value (str): Valor del selector.
        timeout (int, optional): Tiempo máximo de espera en segundos.
    """
    try:
        esperar_elemento(driver, by, value, timeout)
        elemento = driver.find_element(by, value)
        elemento.send_keys(Keys.ENTER)
        logging.info(f"Se pulsó Enter en el elemento localizado por {by}='{value}'.")
    except Exception as e:
        logging.error(f"No se pudo pulsar Enter en el elemento con {by}='{value}': {e}")
        raise

def pulsar_enter_en_elemento_por_id(driver: webdriver.Chrome, element_id: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Pulsa Enter en un elemento identificado por su ID.
    """
    pulsar_enter_en_elemento(driver, By.ID, element_id, timeout)

def pulsar_enter_en_elemento_por_name(driver: webdriver.Chrome, name: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Pulsa Enter en un elemento identificado por su atributo name.
    """
    pulsar_enter_en_elemento(driver, By.NAME, name, timeout)

def pulsar_enter_en_elemento_por_class(driver: webdriver.Chrome, class_name: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Pulsa Enter en un elemento identificado por su clase CSS.
    """
    pulsar_enter_en_elemento(driver, By.CLASS_NAME, class_name, timeout)

def encontrar_pop_up_por_on_click(driver: webdriver.Chrome, onclick_value: str, timeout: int = DEFAULT_TIMEOUT) -> webdriver.remote.webelement.WebElement:
    """
    Busca y retorna un elemento pop-up localizado por el atributo 'onclick' con el valor especificado,
    sin hacer click en el elemento.

    Args:
        driver (webdriver.Chrome): Instancia activa del navegador.
        onclick_value (str): Valor exacto del atributo onclick a buscar.
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Returns:
        WebElement: Elemento WebElement correspondiente al pop-up encontrado.

    Ejemplo:
        popup = encontrar_pop_up_por_on_click(driver, "editar_empresa_autorizada_origen()")
    """
    xpath = f"//*[@onclick=\"{onclick_value}\"]"
    popup = driver.find_element(By.XPATH, xpath)
    popup.click()
    return popup

def clickar_boton_por_on_click(driver: webdriver.Chrome, onclick_value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """
    Hace clic en un botón o elemento que tenga el atributo onclick con el valor especificado.

    Args:
        driver (webdriver.Chrome): Instancia activa del navegador.
        onclick_value (str): Valor exacto del atributo onclick a buscar (por ejemplo, 'nuevo_FACTURACION()').
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Ejemplo:
        clickar_boton_por_on_click(driver, "nuevo_FACTURACION()")
    """
    xpath = f"//*[@onclick=\"{onclick_value}\"]"
    esperar_elemento(driver, By.XPATH, xpath, timeout)
    elemento = driver.find_element(By.XPATH, xpath)
    elemento.click()

def obtener_texto_elemento_por_xpath(driver: webdriver.Chrome, xpath: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Obtiene el texto de un elemento localizado por su XPath.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        xpath (str): Expresión XPath del elemento.
        timeout (int, optional): Tiempo máximo de espera en segundos.

    Returns:
        str: El texto del elemento, o "" si no se encuentra.
    """
    try:
        esperar_elemento(driver, By.XPATH, xpath, timeout)
        elemento = driver.find_element(By.XPATH, xpath)
        texto = elemento.text
        logging.info(f"Texto obtenido del elemento con XPath '{xpath}': {texto}")
        return texto
    except Exception as e:
        logging.error(f"Error al obtener texto del elemento con XPath '{xpath}': {e}")
        return ""

def clickar_div_residuo_por_nombre(driver, nombre_residuo, timeout=10):
    """
    Hace clic en el <div> con clase 'denominacion col-3-5 tab-3-5 tel-9' que contiene un <label> con 'Denominación'
    y cuyo texto contiene el nombre del residuo (comparación flexible: sin tildes, mayúsculas ni espacios extra).
    """
    xpath = (
        "//div[contains(@class, 'denominacion') and contains(@class, 'col-3-5') "
        "and contains(@class, 'tab-3-5') and contains(@class, 'tel-9') "
        "and .//label[contains(text(),'Denominación')] "
        "and contains(normalize-space(.), '{}')]"
    ).format(nombre_residuo.strip())

    intentos = 5
    for intento in range(intentos):
        try:
            elemento = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            elemento.click()
            return
        except Exception as e:
            if intento == intentos - 1:
                raise
            time.sleep(0.5)

def escribir_en_elemento_por_name_y_enter_escape(driver: webdriver.Chrome, name: str, texto: str) -> None:
    """
    Escribe en un elemento identificado por el atributo name y pulsa Enter después de escribir.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        name (str): Valor del atributo name del elemento.
        texto (str): Texto a escribir.

    Ejemplo:
        escribir_en_elemento_por_name_y_enter(driver, "usuario", "admin")
    """
    try:
        escribir_en_elemento(driver, By.NAME, name, texto)
        input_element = driver.find_element(By.NAME, name)
        time.sleep(2)
        input_element.send_keys(Keys.ESCAPE)
        logging.info(f"Se escribió texto y se pulsó Enter en el elemento con name '{name}'.")
    except Exception as e:
        logging.error(f"No se pudo escribir y pulsar Enter en el elemento con name '{name}': {e}")
        raise

## Probar con el campo de codigo de tratamiento en nubelus