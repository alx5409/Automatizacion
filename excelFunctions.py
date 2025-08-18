"""
Módulo: excelFunctions.py

Este módulo contiene funciones para procesar información proveniente de archivos Excel y 
automatizar la adición de empresas y centros en la aplicación Nubelus utilizando Selenium WebDriver.

Funciones principales:
    - _esperar_descarga(carpeta, extension=".xlsx", timeout=30):
          Espera a que se complete la descarga de un archivo con la extensión indicada en la carpeta especificada.
    - _nif_no_encontrados_en_nubelus(cif_nubelus, datos_recogidas):
          Retorna un DataFrame con las filas cuyos NIF (cif_recogida) no se encuentran en la lista de Nubelus.
    - sacarEmpresasNoAñadidas(driver):
          Procesa los archivos Excel para obtener los datos de empresas que no se han añadido en Nubelus.
    - añadirEmpresas(driver, empresas_añadir):
          Itera sobre el DataFrame 'empresas_añadir' y realiza las acciones necesarias para añadir cada empresa mediante Selenium.
    - sacar_centros_no_encontrados_en_nubelus(centros_nubelus, datos_recogidas):
          Filtra los centros que no han sido encontrados en Nubelus a partir de la columna "nombre_recogida".
    - sacar_centros_no_añadidos(driver):
          Procesa los archivos Excel para obtener los centros medioambientales que no han sido añadidos.
    - añadirCentros(driver, centro_añadir):
          Itera sobre el DataFrame 'centro_añadir' y realiza las acciones necesarias para añadir cada centro en la aplicación.

Ejemplo de uso:
    empresas = sacarEmpresasNoAñadidas(driver)
    añadirEmpresas(driver, empresas)
    
    centros = sacar_centros_no_añadidos(driver)
    añadirCentros(driver, centros)
"""

import glob
import os
import time
import pandas as pd
import json
import logging
import re
import unicodedata
import sys
from config import BASE_DIR
import webFunctions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import shutil
import funcionesNubelus
import downloadFunctions

# Directorio donde se espera la descarga de archivos Excel
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
# Ruta del archivo Excel recogidas
#EXCEL_RECOGIDAS = os.path.join(BASE_DIR, "data", "excel_recogidas.xls")
#data_recogidas = pd.read_excel(EXCEL_RECOGIDAS)

URL_SEGURIDAD = "chrome://settings/security"
WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_ENTIDAD = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales"
WEB_NUBELUS_ENTIDAD_NUEVO = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"
WEB_NUBELUS_ACUERDOS = "https://portal.nubelus.es/?clave=waster2_gestionAcuerdosRepresentacion"
WEB_NUBELUS_ACUERDOS_NUEVO = "https://portal.nubelus.es/?clave=waster2_gestionAcuerdosRepresentacion&pAccion=NUEVO"
WEB_NUBELUS_USUARIO = "https://portal.nubelus.es/?clave=nubelus_gestionUsuarios"
WEB_NUBELUS_USUARIO_NUEVO = "https://portal.nubelus.es/?clave=nubelus_gestionUsuarios&pAccion=NUEVO"
WEB_NUBELUS_CENTROS = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientalesCentros"
WEB_NUBELUS_CENTROS_NUEVO = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientalesCentros&pAccion=NUEVO"
WEB_NUBELUS_CONTRATOS = "https://portal.nubelus.es/?clave=waster2_gestionContratosTratamiento"
WEB_NUBELUS_CONTRATOS_NUEVO = "https://portal.nubelus.es/?clave=waster2_gestionContratosTratamiento&pAccion=NUEVO"
WEB_NUBELUS_CLIENTES = "https://portal.nubelus.es/?clave=factucit2_gestionClientes_n1"
WEB_NUBELUS_CLIENTES_NUEVO = "https://portal.nubelus.es/?clave=factucit2_gestionClientes_n1&pAccion=NUEVO"

dic_formas_juridicas = {
    "A": "Sociedades anónimas",
    "B": "Sociedades de responsabilidad limitada",
    "C": "Sociedades colectivas",
    "D": "Sociedades comanditarias",
    "E": "Comunidades de bienes y herencias yacentes",
    "F": "Sociedades cooperativas",
    "G": "Asociaciones",
    "H": "Comunidades de propietarios en régimen de propiedad horizontal",
    "J": "Sociedades civiles, con o sin personalidad jurídica",
    "N": "Entidades extranjeras",
    "P": "Corporaciones Locales",
    "Q": "Organismos públicos",
    "R": "Congregaciones e instituciones religiosas",
    "S": "Órganos de la Administración del Estado y de las Comunidades Autónomas",
    "U": "Uniones Temporales de Empresas",
    #"V": "Sociedad Agraria de Transformación",
    "W": "Establecimientos permanentes de entidades no residentes en España"
}

dic_codigos_residuos_valencia = {
    "A01": "Agente de residuos peligrosos",
    "A02": "Agente de residuos no peligrosos",
    "E01": "Gestor de tratamiento de residuos peligrosos",
    "E02": "Gestor de tratamiento de residuos no peligrosos",
    "G01": "Centro Gestor de residuos peligrosos",
    "G02": "Centro Gestor intermedio de residuos peligrosos (almacenamiento)",
    #"G03": "Transportista de residuos peligrosos asumiendo titularidad (Recogedor)",
    "G04": "Centro Gestor de residuos no peligrosos",
    "G05": "Centro Gestor intermedio de residuos no peligrosos (almacenamiento)",
    "G06": "Plataforma logística de RAEE",
    "N01": "Negociante de residuos peligrosos",
    "N02": "Negociante de residuos no peligrosos",
    "P01": "Productor de residuos peligrosos",
    "P02": "Pequeño productor de residuos peligrosos",
    "P03": "Productor de residuos no peligrosos",
    "P04": "Actividad productora de Residuos No Peligrosos en cantidad inferior a 1000 tn anuales y por tanto no sometida al régimen de comu",
    "P05": "Poseedor de residuos y, por tanto, no sometido a régimen de autorización o comunicación (accidentes, obras puntuales, comunidade",
    "SCR": "Sistema colectivo de Responsabilidad ampliada",
    "SIR": "Sistema individual de Responsabilidad ampliada",
    "T01": "Transportista de residuos peligrosos",
    "T02": "Transportista de residuos no peligrosos"
}

def _esperar_descarga(carpeta: str, extension: str = ".xlsx", timeout: int = 30) -> str:
    """
    Espera a que se descargue un archivo con la extensión especificada en la carpeta indicada.
    
    Args:
        carpeta (str): Ruta del directorio donde se espera la descarga.
        extension (str, opcional): Extensión del archivo buscado. Valor por defecto ".xlsx".
        timeout (int, opcional): Tiempo máximo de espera en segundos.
        
    Returns:
        str: Ruta del archivo descargado.
        
    Raises:
        TimeoutError: Si no se encuentra ningún archivo descargado en el tiempo indicado.
    """
    tiempo_inicio = time.time()
    while time.time() - tiempo_inicio < timeout:
        archivos = glob.glob(os.path.join(carpeta, f"*{extension}"))
        if archivos:
            # Se aseguran de que el archivo no esté en proceso de descarga (sin extensión .crdownload)
            finalizados = [f for f in archivos if not f.endswith('.crdownload')]
            if finalizados:
                return finalizados[0]
        time.sleep(1)
    raise TimeoutError("Descarga no completada en el tiempo esperado.")


def _nif_no_encontrados_en_nubelus(cif_nubelus, datos_recogidas: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra del DataFrame 'datos_recogidas' aquellas filas cuyo 'cif_recogida' no se encuentre
    en los valores de 'cif_nubelus'.

    Args:
        cif_nubelus: Serie o lista con los NIF existentes en Nubelus.
        datos_recogidas (pandas.DataFrame): DataFrame con los datos recogidos del Excel.

    Returns:
        pandas.DataFrame: DataFrame con las filas cuyos NIF no han sido encontrados en Nubelus.
    """
    filas_no_encontradas = []
    for idx, fila in datos_recogidas.iterrows():
        cif_valor = fila['cif_recogida']
        if cif_valor not in cif_nubelus.values:
            filas_no_encontradas.append(fila)
    return pd.DataFrame(filas_no_encontradas)


def limpiar_campo(valor):
    # Si es NaN o None, devolver vacío
    if pd.isnull(valor):
        return ""
    # Convertir a string y quitar espacios al principio y final
    valor_str = str(valor).strip()
    # Normalizar acentos y ñ
    valor_str = unicodedata.normalize('NFKD', valor_str).encode('ascii', 'ignore').decode('ascii')
    # Si es un número de teléfono, quitar decimales y ceros a la izquierda
    if valor_str.replace('.', '', 1).isdigit():
        valor_str = valor_str.split('.')[0]  # Quitar decimales
        valor_str = valor_str.lstrip('0')    # Quitar ceros a la izquierda
    return valor_str

# def sacar_empresas_no_añadidas(driver: webdriver.Chrome) -> pd.DataFrame:
#     """
#     Procesa los  archivos Excel para identificar las empresas que aún no han sido añadidas en Nubelus.
    
#     El proceso consiste en:
#       1. Esperar a que se descargue el archivo Excel esperado.
#       2. Leer el archivo Excel descargado y el Excel de recogida.
#       3. Comparar el NIF de las entidades medioambientales con el listado recogido.
      
#     Args:
#         driver (webdriver.Chrome): Instancia del navegador.
        
#     Returns:
#         pandas.DataFrame: DataFrame con los datos de las empresas no añadidas.
        
#     Si la descarga falla, se cierra el navegador y se finaliza la ejecución.
#     """
#     try:
#         archivo_xlsx = _esperar_descarga(DOWNLOAD_DIR)
#         logging.info(f"Archivo descargado: {archivo_xlsx}")
#     except TimeoutError as e:
#         logging.error(e)
#         driver.quit()
#         sys.exit()

#     # Leer los Excel con pandas
#     entidades_medioambientales = pd.read_excel(archivo_xlsx)
#     #excel_recogidas = pd.read_excel(EXCEL_RECOGIDAS)

#     # Obtener los NIF de Nubelus
#     cif_nubelus = entidades_medioambientales["NIF"]

#     # Seleccionar únicamente las columnas de interés del Excel recogidas
#     datos = excel_recogidas[[
#         'cif_recogida', 'nombre_recogida', 'direccion_recogida', 'cp_recogida',
#         'poblacion_recogida', 'provincia_recogida', 'email_recogida', 'telf_recogida'
#     ]]

#     datos_no_encontrados = _nif_no_encontrados_en_nubelus(cif_nubelus, datos)
#     return datos_no_encontrados
def forma_juridica_empresa(cif: str) -> str:
    """
    Determina la forma jurídica de una empresa según su CIF.

    Args:
        cif (str): El CIF de la empresa.

    Returns:
        str: Forma Jurídica según la primera letra del CIF, o 'Otros' si no se encuentra.
    """
    if not cif or not isinstance(cif, str):
        return "Otros"
    letra = cif.strip().upper()[0]
    return dic_formas_juridicas.get(letra, "Otros")

def validar_nif(nif):
    """
    Valida el formato del NIF español (empresa o persona física).
    Ejemplos válidos: B86681426, 12345678B
    Lanza ValueError si el formato es incorrecto.
    """
    if not isinstance(nif, str):
        raise ValueError("El NIF debe ser una cadena de texto.")
    nif = nif.strip().upper()
    if not re.fullmatch(r"([A-Z]\d{8}|\d{8}[A-Z])", nif):
        raise ValueError(f"Formato de NIF incorrecto: {nif}")
    return True

def forma_fiscal_por_cif(cif: str) -> str:
    if cif and cif[-1].isalpha():
        forma_fiscal = "Física"
    else:
        forma_fiscal = "Jurídica"
    
    return forma_fiscal
        

def añadir_empresa(driver: webdriver.Chrome, fila) -> None:
    """
    Añade una empresa individualmente en la aplicación web mediante Selenium.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        empresa (Union[pandas.Series, dict]): Datos de la empresa a añadir. Puede ser una Serie de pandas o un diccionario.
    """
    webFunctions.abrir_web(driver, WEB_NUBELUS_ENTIDAD_NUEVO)
    try:
        logging.info(f"Añadiendo empresa: {fila['nombre_recogida']}")
        
        # 1. Completar el campo Nombre
        webFunctions.esperar_elemento(driver, By.ID, "pDenominacion", timeout=10)
        webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", fila["nombre_recogida"])
        
        # 2. Validar y completar el campo NIF
        # validar_nif(fila["cif_recogida"])  # Validar el formato del NIF
        webFunctions.escribir_en_elemento_por_name(driver, "pNif", fila["cif_recogida"])
        
        # 3. Completar el campo de forma fiscal: Física si el último carácter del CIF es letra, Jurídica si el primero es letra
        cif = str(fila["cif_recogida"]).strip()
        forma_fiscal = forma_fiscal_por_cif(cif)
        webFunctions.seleccionar_elemento_por_nombre(driver, "pForma_fiscal", forma_fiscal)

        time.sleep(1)
        
        # 4. Completar el campo de Forma Jurídica y Nombre Fiscal si es Jurídica
        if forma_fiscal == "Jurídica":
            forma_juridica = forma_juridica_empresa(fila["cif_recogida"])
            time.sleep(1)  # Espera para que el campo se active
            webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_forma_juridica" ,forma_juridica)
            time.sleep(0.5)
            webFunctions.escribir_en_elemento_por_name_y_enter(driver, "pNombre_fiscal", fila["nombre_recogida"])

        # 4. Completar el campo Nombre y Apellidos si es una persona física
        elif forma_fiscal == "Física":
            nombre, *apellidos = str(fila["nombre_recogida"]).strip().split()
            webFunctions.escribir_en_elemento_por_name(driver, "pNombre", nombre)
            webFunctions.escribir_en_elemento_por_name(driver, "pApellidos", " ".join(apellidos))

        # 5. Completar el campo Domicilio
        webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", fila["direccion_recogida"])
        print("antes de municipio")
        # 6. Completar el campo Municipio
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_ine_municipio", str(fila["poblacion_recogida"]))
        print("después de municipio")
        # 7. Completar el campo Provincia
        webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", fila["provincia_recogida"])
        
        # 8. Completar el campo CP
        webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", str(fila["cp_recogida"]))
        
        # 9. Completar el campo Teléfono
        webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", str(fila["telf_recogida"]))
        
        # 10. Completar el campo Email
        webFunctions.escribir_en_elemento_por_name(driver, "pEmail", fila["email_recogida"])

        # 11. Añadir NIMA
        webFunctions.escribir_en_elemento_por_name(driver, "pNima", str(fila.get("nima_codigo", "")))

        # 12. Completar el campo Autorización
        webFunctions.escribir_en_elemento_por_name(driver, "pAutorizacion_medioambiental", str(fila.get("nima_cod_peligrosos", "")))

        # 13. Añadir tipo
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_ema", "P02")

        # 14. Confirmar la adición (clic en botón de aceptar o cancelar o guardar según corresponda)
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")


        
        # Espera para que la acción se procese
        time.sleep(1)
    except Exception as error:
        logging.error(f"Error al añadir la empresa {fila.get('nombre_recogida', '')}: {error}")
        if funcionesNubelus.preguntar_por_pantalla():
            logging.info("Continuando con la siguiente empresa...")
        else:
            logging.info("Saliendo del proceso de adición de empresas.")
            driver.quit()
            sys.exit()

def añadir_empresas(driver: webdriver.Chrome, empresas_añadir: pd.DataFrame) -> None:
    """
    Itera sobre el DataFrame 'empresas_añadir' y realiza las acciones necesarias para 
    añadir cada empresa en la aplicación web mediante Selenium.

    Se asume que el formulario para añadir empresas ya está visible en la aplicación.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        empresas_añadir (pandas.DataFrame): DataFrame con los datos de las empresas a añadir.
    
    Ejemplo:
        añadirEmpresas(driver, empresas_df)
    """
    for idx, empresa in empresas_añadir.iterrows():
        # Clic en el botón "nuevo"
        webFunctions.clickar_boton_por_clase(driver, "miBoton.nuevo")
        añadir_empresa(driver, empresa)


def quitar_tildes(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def is_denominacion_correcto(nombre_recogida: str, denominacion: str) -> bool:
    """
    Compara dos cadenas (nombre_recogida y denominacion) para determinar si coinciden
    ignorando signos especiales, mayúsculas/minúsculas, tildes y contenido entre paréntesis.
    Considera coincidencia si al menos una palabra clave está en la denominación.
    """
    nombre_recogida = quitar_tildes(str(nombre_recogida).upper())
    denominacion = quitar_tildes(str(denominacion).upper())

    # Quita signos especiales
    signos_especiales = ['.', ',', '-', '&', 'Y']
    for signo in signos_especiales:
        nombre_recogida = nombre_recogida.replace(signo, '')
        denominacion = denominacion.replace(signo, '')

    # Elimina contenido entre paréntesis en nombre_recogida
    nombre_recogida = re.sub(r'\(.*?\)', '', nombre_recogida).strip()

    # Divide en palabras y comprueba si todas están en denominacion
    palabras = nombre_recogida.split()
    for palabra in palabras:
        if palabra not in denominacion:
            return False
    return True


def sacar_centros_no_encontrados_en_nubelus(centros_nubelus: pd.DataFrame, datos_recogidas: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra los centros de datos_recogidas cuyos nombres no se encuentran (según comparación flexible)
    en la columna 'Denominación' de centros_nubelus.

    Args:
        centros_nubelus (pandas.DataFrame): DataFrame con columnas 'Denominación' y 'EMA'.
        datos_recogidas (pandas.DataFrame): DataFrame con columna 'nombre_recogida' y otros datos.

    Returns:
        pandas.DataFrame: DataFrame con los centros no encontrados, añadiendo la columna 'EMA' si corresponde.
    """
    filas_no_encontradas = []
    denominacion_to_ema = dict(zip(centros_nubelus['Denominación'], centros_nubelus['EMA']))

    for idx, fila in datos_recogidas.iterrows():
        encontrado = False
        for denominacion in centros_nubelus['Denominación']:
            if is_denominacion_correcto(fila['nombre_recogida'], denominacion):
                encontrado = True
                break
        if not encontrado:
            fila_dict = fila.to_dict()
            # Intenta asociar la EMA si el nombre coincide exactamente, si no, deja vacío
            fila_dict['EMA'] = denominacion_to_ema.get(fila['nombre_recogida'], '')
            filas_no_encontradas.append(fila_dict)

    return pd.DataFrame(filas_no_encontradas)

def sacar_empresas_no_encontradas_en_nubelus(centros_nubelus: pd.DataFrame, datos_recogidas: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra los centros de datos_recogidas cuyos nombres no se encuentran (según comparación flexible)
    en la columna 'Denominación' de centros_nubelus.

    Args:
        centros_nubelus (pandas.DataFrame): DataFrame con columnas 'Denominación' y 'EMA'.
        datos_recogidas (pandas.DataFrame): DataFrame con columna 'nombre_recogida' y otros datos.

    Returns:
        pandas.DataFrame: DataFrame con los centros no encontrados, añadiendo la columna 'EMA' si corresponde.
    """
    filas_no_encontradas = []
    denominacion_to_ema = dict(zip(centros_nubelus['Denominación'], centros_nubelus['EMA']))

    for idx, fila in datos_recogidas.iterrows():
        encontrado = False
        for denominacion in centros_nubelus['Denominación']:
            if is_denominacion_correcto(fila['nombre_recogida'], denominacion):
                encontrado = True
                break
        if not encontrado:
            fila_dict = fila.to_dict()
            # Intenta asociar la EMA si el nombre coincide exactamente, si no, deja vacío
            fila_dict['EMA'] = denominacion_to_ema.get(fila['nombre_recogida'], '')
            filas_no_encontradas.append(fila_dict)

    return pd.DataFrame(filas_no_encontradas)

# def sacar_centros_no_añadidos(driver: webdriver.Chrome) -> pd.DataFrame:
#     """
#     Procesa los archivos Excel para obtener los centros medioambientales que aún no han sido añadidos en Nubelus.
    
#     El proceso es el siguiente:
#       1. Espera la descarga del archivo Excel.
#       2. Lee el archivo Excel descargado y el archivo de recogida.
#       3. Selecciona los datos relevantes de cada uno.
#       4. Llama a la función de filtrado para identificar centros no encontrados.
      
#     Args:
#         driver (webdriver.Chrome): Instancia del navegador.
        
#     Returns:
#         pandas.DataFrame: DataFrame con los centros no añadidos.
#     """
#     try:
#         archivo_xlsx = _esperar_descarga(DOWNLOAD_DIR)
#         logging.info(f"Archivo descargado: {archivo_xlsx}")
#     except TimeoutError as e:
#         logging.error(e)
#         driver.quit()
#         sys.exit()

#     centros_medioambientales = pd.read_excel(archivo_xlsx)
#     excel_recogidas = pd.read_excel(EXCEL_RECOGIDAS)

#     # Seleccionar columnas de interés
#     centros = centros_medioambientales[['Denominación', 'EMA']]
#     datos = excel_recogidas[['nombre_recogida', 'direccion_recogida', 'cp_recogida',
#                               'poblacion_recogida', 'provincia_recogida', 'email_recogida',
#                               'telf_recogida']]

#     # Llamar a la función para filtrar centros no encontrados
#     sacar_centros_no_encontrados_en_nubelus(centros, datos)
#     return datos

def coincidencias_en_entidades(excel_input, excel_entidades):
    """
    Si el 'cif_recogida' de excel_input está en 'NIF' de excel_entidades,
    devuelve el valor del campo 'Denominación' asociado a ese NIF.
    Si no hay coincidencia, devuelve None.
    """
    try:
        nif = excel_input['cif_recogida']
        coincidencias = excel_entidades[excel_entidades['NIF'] == nif]
        if not coincidencias.empty:
            return coincidencias.iloc[0]['Denominación'] # Devuelve la denominación asociada al NIF
        else:
            return None
    except Exception as error:
        logging.error(f"Error en coincidencias_en_entidades: {error}")
        return None

def coincidencias_en_centros(excel_input, excel_centros):
    """
    Devuelve True si el 'nombre_recogida' de excel_input está en 'Denominación' de excel_centros.
    Si no hay coincidencia, devuelve None.
    """
    try:
        if excel_input['nombre_recogida'] in excel_centros['Denominación'].values:
            return True
        else:
            return None
    except Exception as error:
        logging.error(f"Error en coincidencias_en_centros: {error}")
        return None

def coincidencias_en_usuarios(excel_input, excel_usuarios):
    """
    Devuelve True si el 'nombre_recogida' de excel_input está en 'Nombre' de excel_usuarios.
    Si no hay coincidencia, devuelve None.
    """
    try:
        if excel_input['nombre_recogida'] in excel_usuarios['Nombre'].values:
            return True
        else:
            return None
    except Exception as error:
        logging.error(f"Error en coincidencias_en_usuarios: {error}")
        return None

def coincidencias_en_acuerdos_representacion(excel_input, excel_acuerdos):
    """
    Devuelve True si el 'nombre_recogida' de excel_input está en 'EMA representada' de excel_acuerdos.
    Si no hay coincidencia, devuelve None.
    """
    try:
        if excel_input['nombre_recogida'] in excel_acuerdos['EMA representada'].values:
            return True
        else:
            return None
    except Exception as error:
        logging.error(f"Error en coincidencias_en_acuerdos_representacion: {error}")
        return None

def coincidencias_en_contratos(excel_input, excel_contratos):
    """
    Devuelve un DataFrame con las filas de excel_contratos cuyo 'Origen' coincide con 'nombre_recogida' de excel_input.
    Si no hay coincidencias, devuelve None.
    """
    try:
        coincidencias = excel_contratos[excel_contratos['Origen'] == excel_input['nombre_recogida']]
        if not coincidencias.empty:
            return coincidencias
        else:
            return None
    except Exception as error:
        logging.error(f"Error en coincidencias_en_contratos: {error}")
        return None

def coincidencias_en_clientes(excel_input, excel_clientes):
    """
    Devuelve True si el 'nombre_recogida' de excel_input está en 'Denominación' de excel_clientes.
    Si no hay coincidencia, devuelve None.
    """
    try:
        if excel_input['nombre_recogida'] in excel_clientes['Denominación'].values:
            return True
        else:
            return None
    except Exception as error:
        logging.error(f"Error en coincidencias_en_clientes: {error}")
        return None

def añadir_centro(nombre_empresa, driver: webdriver.Chrome, fila) -> None:
    """
    Añade un centro individualmente en la aplicación web mediante Selenium.

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        centro (Union[pandas.Series, dict]): Datos del centro a añadir. Puede ser una Serie de pandas o un diccionario.
    """
    webFunctions.abrir_web(driver, WEB_NUBELUS_CENTROS_NUEVO)
    try:
        logging.info(f"Añadiendo centro: {fila['nombre_recogida']}")

        # 1. Completar el campo Denominación
        webFunctions.esperar_elemento(driver, By.ID, "pDenominacion", timeout=10)
        webFunctions.escribir_en_elemento_por_id(driver, "pDenominacion", fila["nombre_recogida"])

        # 2. Completar el campo Entidad MA
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_ema", fila["nombre_empresa"])

        # 3. Completar el campo Domicilio
        webFunctions.escribir_en_elemento_por_name(driver, "pDomicilio", fila["direccion_recogida"])

        # 4. Completar el campo Municipio
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_ine_municipio", str(fila["poblacion_recogida"]))

        # 5. Completar el campo Provincia
        webFunctions.escribir_en_elemento_por_name(driver, "pPoblacion", fila["provincia_recogida"])

        # 6. Completar el campo Código Postal
        webFunctions.escribir_en_elemento_por_name(driver, "pCodigoPostal", str(fila["cp_recogida"]))

        # 7. Completar el campo Teléfono
        webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", str(fila["telf_recogida"]))
        
        # 8. Completar el campo Email
        webFunctions.escribir_en_elemento_por_name(driver, "pEmail", fila["email_recogida"])

        # 9. Completar el campo NIMA
        webFunctions.escribir_en_elemento_por_name(driver, "pNima", str(fila.get("nima_codigo", "")))

        # 10. Completar el campo Autorización
        webFunctions.escribir_en_elemento_por_name(driver, "pAutorizacion_medioambiental", str(fila.get("nima_cod_peligrosos", "")))

        # 11. Completar el campo Tipo
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_tipo_ema", "P02")

        # 9. Confirmar la adición (clic en botón de aceptar o guardar)
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")

        # Espera para que la acción se procese
        time.sleep(1)

        # Añade las autorizaciones del centro
        añadir_autorizaciones(driver, fila)
        rellenar_datos_medioambientales(driver, fila)
    except Exception as error:
        logging.error(f"Error al añadir el centro {fila.get('nombre_recogida', '')}: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info("Continuando con el siguiente centro...")
        else:
            logging.info("Saliendo del proceso de adición de centros.")
            driver.quit()
            sys.exit()

def añadir_centros(driver: webdriver.Chrome, centros_añadir: pd.DataFrame) -> None:
    """
    Itera sobre el DataFrame 'centros_añadir' y añade cada centro usando añadirCentro.
    """
    for idx, centro in centros_añadir.iterrows():
        webFunctions.clickar_boton_por_clase(driver, "miBoton.nuevo")
        añadir_centro(driver, centro)


def extraer_datos_centro_castilla_desde_excel(ruta_excel):
    """
    Lee un archivo Excel (.xls) y devuelve un JSON estructurado con la información de la sede y los centros.
    """
    logging.info(f"Procesando archivo Excel: {ruta_excel}")
    datos_castilla = pd.read_excel(ruta_excel, header=1)
    logging.info(f"{datos_castilla}")
    ruta_xlsx = ruta_excel.replace('.xls', '.xlsx')
    logging.info(f"Guardando datos en: {ruta_xlsx}")
    try:
        datos_castilla.to_excel(ruta_xlsx, index=False)
    except Exception as e:
        logging.error(f"Error al guardar el archivo Excel: {e}")
        raise

    # Filtra filas válidas (donde 'Unnamed: 0' es un número)
    filas_validas = datos_castilla[datos_castilla['Unnamed: 0'].apply(
        lambda x: isinstance(x, (int, float)) and x > 0 and float(x).is_integer()
    )]

    # --- Empresa: toma la primera fila válida ---
    if not filas_validas.empty:
        fila_empresa = filas_validas.iloc[0]
        telefono_empresa = fila_empresa.get('TELÉFONO', 0)
        if pd.isnull(telefono_empresa):
            telefono_empresa = 0
        else:
            try:
                telefono_empresa = int(telefono_empresa)
            except Exception:
                telefono_empresa = 0
        empresa = {
            "nombre": fila_empresa.get('NOMBRE', ''),
            "provincia": fila_empresa.get('PROVINCIA', ''),
            "municipio": fila_empresa.get('LOCALIDAD', ''),
            "direccion": fila_empresa.get('DOMICILIO', ''),
            "telefono": telefono_empresa,
            "email": fila_empresa.get('E-MAIL', ''),
            "coordenadas": fila_empresa.get('COORDENADAS', ''),
        }
        # Eliminar nif si por alguna razón está presente
        empresa.pop('nif', None)
    else:
        empresa = {}

    # --- Centros: todas las filas válidas ---
    centros = []
    for _, fila in filas_validas.iterrows():
        telefono_centro = fila.get('TELÉFONO', 0)
        if pd.isnull(telefono_centro):
            telefono_centro = 0
        else:
            try:
                telefono_centro = int(telefono_centro)
            except Exception:
                telefono_centro = 0
        centro = {
            "nima": fila.get('NIMA', ''),
            "num_autorizacion": fila.get('Nº AUTORIZACIÓN', ''),
            "tipo_expediente": fila.get('TIPO EXPEDIENTEs', ''),
            "nombre": fila.get('NOMBRE', ''),
            "provincia": fila.get('PROVINCIA', ''),
            "municipio": fila.get('LOCALIDAD', ''),
            "direccion": fila.get('DOMICILIO', ''),
            "telefono": telefono_centro,
            "email": fila.get('E-MAIL', ''),
            "coordenadas": fila.get('COORDENADAS', ''),
            "codigo_ler": fila.get('CODIGO LER', ''),
            "codigo_raee": fila.get('CODIGO RAEE', ''),
            "descripcion_codigo": fila.get('DESCRICPCION CODIGO', ''),
        }
        # Eliminar nif si por alguna razón está presente
        centro.pop('nif', None)
        centros.append(centro)

    resultado = {
        "empresa": empresa,
        "centros": centros
    }
    return resultado


def esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60):
    import glob, os, time, logging

    carpeta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
    tiempo_inicio = time.time()
    archivo_final = None

    while time.time() - tiempo_inicio < timeout:
        archivos = glob.glob(os.path.join(carpeta_descargas, f"*{extension}"))
        finalizados = [f for f in archivos if not f.endswith('.crdownload')]
        if finalizados:
            archivo_final = max(finalizados, key=os.path.getmtime)
            size = -1
            while True:
                new_size = os.path.getsize(archivo_final)
                if new_size == size:
                    break
                size = new_size
                time.sleep(1)
            break

    datos_dict = None
    archivo_xlsx = None
    try:
        if not archivo_final:
            logging.error("No se descargó ningún archivo en el tiempo esperado.")
            return None

        logging.info(f"Archivo descargado: {archivo_final}")
        datos_dict = extraer_datos_centro_castilla_desde_excel(archivo_final)
        logging.info("Datos extraídos del Excel.")
        archivo_xlsx = archivo_final.replace('.xls', '.xlsx')
    finally:
        # Borrar el archivo .xls
        if archivo_final and os.path.exists(archivo_final):
            try:
                os.remove(archivo_final)
                logging.info(f"Archivo eliminado: {archivo_final}")
            except Exception as e:
                logging.error(f"No se pudo eliminar el archivo: {archivo_final}. Error: {e}")

        # Borrar el archivo .xlsx generado
        if archivo_xlsx and os.path.exists(archivo_xlsx):
            try:
                os.remove(archivo_xlsx)
                logging.info(f"Archivo eliminado: {archivo_xlsx}")
            except Exception as e:
                logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")

    return datos_dict

def añadir_horario(driver, fila):
    """
    Navega a la sección 'Otros', abre el pop-up de aviso y añade un horario de prueba.
    """
    try:
        webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Otros")
        time.sleep(1)
        webFunctions.clickar_boton_con_titulo(driver, "Editar")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_cambiar_aviso")
        str_horario = "MAÑANAS: " + str(fila.get("horario_m_1", "")) + " - " + str(fila.get("horario_m_2", "")) + "\n" + \
            "TARDES: " + str(fila.get("horario_t_1", "")) + " - " + str(fila.get("horario_t_2", ""))
        webFunctions.escribir_en_elemento_por_name(popup, "pAviso", str_horario)
        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        driver = oldDriver
    except Exception as error:
        logging.error(f"Error al añadir horario para la empresa.")

def rellenar_datos_medioambientales(driver, fila):
    """
    Rellena los datos medioambientales en el formulario correspondiente usando los datos de la fila 'empresa'.
    """
    try:
        webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Datos medioambientales")
        time.sleep(1)
        webFunctions.clickar_boton_por_clase(driver, "miBoton.editar.solapa_descripcion")

        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_editar_DATOS_MEDIOAMBIENTALES")
        webFunctions.esperar_elemento(popup, By.CLASS_NAME, "pNima")
        # Rellenar campos con los datos de la empresa
        webFunctions.escribir_en_elemento_por_name(popup, "pNima", str(fila.get("nima_codigo", "")))
        webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_nombre", str(fila.get("nombre_recogida", "")))
        webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_nif", str(fila.get("cif_recogida", "")))
        webFunctions.escribir_en_elemento_por_name(popup, "pResponsable_ma_cargo", str(fila.get("nombre_recogida", "")))
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(popup, "pDenominacion_ine_municipio", str(fila.get("poblacion_recogida", "")))

        time.sleep(1)
        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        driver = oldDriver
    except Exception as error:
        logging.error(f"Error al rellenar datos medioambientales para la empresa {fila.get('nombre_recogida', '')}: {error}")
    
def obtener_fecha_modificada(fecha):
    """
    Obtiene la fecha y la convierte de formato YYYY-MM-DD a DD-MM-YYYY si es posible.

    Args:
        fecha (str): Fecha en formato string.

    Returns:
        str: Fecha en formato DD-MM-YYYY o la original si no es posible convertir.
    """
    fecha = str(fecha)[:10]  # Truncar a longitud 10
    if len(fecha) == 10 and fecha[4] == '-' and fecha[7] == '-':
        partes = fecha.split('-')
        fecha_modificada = f"{partes[2]}-{partes[1]}-{partes[0]}"
    else:
        fecha_modificada = fecha
    return fecha_modificada

def fecha_caducidad(fecha_inicio):
    """
    Recibe una fecha en formato DD-MM-YYYY, suma 5 años y resta un día.
    Devuelve la fecha resultante en el mismo formato DD-MM-YYYY.
    """
    # Extraer día, mes y año
    try:
        partes = str(fecha_inicio)[:10].split('-')
        dia = int(partes[0])
        mes = int(partes[1])
        anio = int(partes[2])

        # Sumar 5 años
        nuevo_anio = anio + 5

        # Restar un día
        dia -= 1
        if dia == 0:
            mes -= 1
            if mes == 0:
                mes = 12
                nuevo_anio -= 1
            # Días por mes (considerando años bisiestos para febrero)
            if mes == 2:
                if (nuevo_anio % 4 == 0 and (nuevo_anio % 100 != 0 or nuevo_anio % 400 == 0)):
                    dia = 29
                else:
                    dia = 28
            elif mes in [1,3,5,7,8,10,12]:
                dia = 31
            else:
                dia = 30

        return f"{dia:02d}-{mes:02d}-{nuevo_anio:04d}"
    except Exception:
        return fecha_inicio

def fecha_caducidad_3(fecha_inicio):
    """
    Recibe una fecha en formato DD-MM-YYYY, suma 5 años y resta un día.
    Devuelve la fecha resultante en el mismo formato DD-MM-YYYY.
    """
    # Extraer día, mes y año
    try:
        partes = str(fecha_inicio)[:10].split('-')
        dia = int(partes[0])
        mes = int(partes[1])
        anio = int(partes[2])

        # Sumar 3 años
        nuevo_anio = anio + 3

        # Restar un día
        dia -= 1
        if dia == 0:
            mes -= 1
            if mes == 0:
                mes = 12
                nuevo_anio -= 1
            # Días por mes (considerando años bisiestos para febrero)
            if mes == 2:
                if (nuevo_anio % 4 == 0 and (nuevo_anio % 100 != 0 or nuevo_anio % 400 == 0)):
                    dia = 29
                else:
                    dia = 28
            elif mes in [1,3,5,7,8,10,12]:
                dia = 31
            else:
                dia = 30

        return f"{dia:02d}-{mes:02d}-{nuevo_anio:04d}"
    except Exception:
        return fecha_inicio

def añadir_acuerdo_representacion(driver, fila):
    """
    Navega a la sección de acuerdos de representación y añade un acuerdo usando los datos de la fila 'empresa'.
    Reintenta hasta 5 veces en caso de error.
    """
    webFunctions.abrir_web(driver, WEB_NUBELUS_ACUERDOS_NUEVO)
    intentos = 5
    for intento in range(intentos):
        try:
            time.sleep(1)
            webFunctions.completar_campo_y_enter_por_name(driver, "pDenominacion_ema_representada", str(fila.get("nombre_recogida", "")))
            fecha_inicio = obtener_fecha_modificada(str(fila.get("fecha_inicio", "")))
            fecha_fin = obtener_fecha_modificada(str(fila.get("fecha_fin", "")))
            webFunctions.escribir_en_elemento_por_name(driver, "pFecha", fecha_inicio)
            webFunctions.escribir_en_elemento_por_name(driver, "pFecha_caducidad", fecha_fin)
            webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")
            time.sleep(1)  # Espera para que la acción se procese
            return
        except Exception as error:
            logging.error(f"Error al añadir acuerdo de representación para la empresa (intento {intento+1}): {error}")
            if intento == intentos - 1:
                continuar = funcionesNubelus.preguntar_por_pantalla()
                if continuar:
                    logging.info("Continuando tras error en acuerdo de representación...")
                else:
                    logging.info("Saliendo del proceso de adición de acuerdos de representación.")
                    driver.quit()
                    sys.exit()
            time.sleep(1)

def codigo_residuos_por_autorizacion(codigo_autorizacion: str) -> str:
    """
    Devuelve la clave del código de residuos si la encuentra como subcadena exacta en el número de autorización.
    Si no encuentra ninguna clave, devuelve una cadena vacía.
    """
    if not codigo_autorizacion or not isinstance(codigo_autorizacion, str):
        return ""
    autorizacion_limpia = ''.join(c for c in codigo_autorizacion if c.isalnum()).upper()
    # Devuelve la clave encontrada o una cadena vacía #
    return next((clave for clave in dic_codigos_residuos_valencia if clave in autorizacion_limpia), "P02")

def denominacion_por_autorizacion(codigo_autorizacion: str) -> str:
    """
    Devuelve la denominación (valor) asociada a la clave del diccionario dic_codigos_residuos_valencia
    si alguna clave está como subcadena en el número de autorización.
    Si no encuentra ninguna clave, devuelve una cadena vacía.
    """
    if not codigo_autorizacion or not isinstance(codigo_autorizacion, str):
        return ""
    autorizacion_limpia = ''.join(c for c in codigo_autorizacion if c.isalnum()).upper()
    for clave, valor in dic_codigos_residuos_valencia.items():
        if clave in autorizacion_limpia:
            return valor
    return codigo_autorizacion

def añadir_autorizaciones(driver, fila):
    """
    Navega a la sección 'Autorizaciones' y añade una autorización usando los datos de la fila 'empresa'.
    """
    try:
        webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Autorizaciones")
        time.sleep(1)
        webFunctions.clickar_boton_por_texto(driver, "Añadir autorización")

        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_nuevo_AUTORIZACIONES")

        # Completar campos del formulario de autorización
        webFunctions.escribir_en_elemento_por_name(popup, "pAutorizacion_medioambiental", str(fila.get('nima_cod_peligrosos', '')))

        #Completar el campo Denominación
        webFunctions.escribir_en_elemento_por_name(popup, "pDenominacion", str(fila.get('nima_nom_peligrosos', '')))

        # Completar el campo Tipo
        webFunctions.escribir_en_elemento_por_name(popup, "pDenominacion_ema", "P02")
        time.sleep(1)
        
        webFunctions.clickar_boton_por_clase(driver, "BUSCAR_TIPO_ENTIDAD_MEDIOAMBIENTAL.noref.ui-menu-item")
        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        driver = oldDriver
    except Exception as error:
        logging.error(f"Error al añadir autorización para la empresa {fila.get('nombre_recogida', '')}: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info("Continuando con la siguiente autorización...")
        else:
            logging.info("Saliendo del proceso de adición de autorizaciones.")
            driver.quit()
            sys.exit()

def añadir_usuario(driver, fila):
    """
    Añade un usuario a la empresa usando los datos de la fila 'empresa'.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        fila (pandas.Series): Fila del DataFrame con los datos de la empresa.
    """
    webFunctions.abrir_web(driver, WEB_NUBELUS_USUARIO_NUEVO)
    try:
        
        # Completar campos del formulario
        webFunctions.escribir_en_elemento_por_name(driver, "pUsuario", fila["nombre_recogida"].replace(" ", ""))
        webFunctions.escribir_en_elemento_por_name(driver, "pAlias", fila["nombre_recogida"])
        webFunctions.escribir_en_elemento_por_name(driver, "pEmail", fila["email_recogida"])
        webFunctions.escribir_en_elemento_por_name(driver, "pTelefono", fila["telf_recogida"])
        webFunctions.seleccionar_elemento_por_name(driver, "pRol", "EMA")
        try:
            webFunctions.completar_campo_y_confirmar_seleccion_por_name(
                driver, "pDenominacion_ema", str(fila.get("nombre_recogida", "")), "BUSCAR_ENTIDAD_MEDIOAMBIENTAL.noref.ui-menu-item"
            )
            webFunctions.completar_campo_y_confirmar_seleccion_por_name(
                driver, "pDenominacion_entidad_ma_centro", str(fila.get("nombre_recogida", "")), "BUSCAR_ENTIDAD_MEDIOAMBIENTAL_CENTRO.noref.ui-menu-item"
            )
        except Exception as e:
            logging.error(f"Error al completar campos de denominación EMA o centro: {e}")
        # Confirmar la adición
        webFunctions.esperar_elemento(driver, By.CLASS_NAME, "miBoton.aceptar")
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")
        
        time.sleep(1)  # Espera para que la acción se procese
    except Exception as error:
        logging.error(f"Error al añadir usuario para la empresa {fila.get('nombre_recogida', '')}: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info("Continuando con el siguiente usuario...")
        else:
            logging.info("Saliendo del proceso de adición de usuarios.")
            driver.quit()
            sys.exit()

def añadir_contrato_tratamiento(driver, fila, residuo):
    """
    Añade un contrato de tratamiento a la empresa usando los datos de la fila 'empresa'.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        fila (pandas.Series): Fila del DataFrame con los datos de la empresa.
    """
    webFunctions.abrir_web(driver, WEB_NUBELUS_CONTRATOS_NUEVO)
    try:
        fecha_inicio = obtener_fecha_modificada(fila["fecha_inicio"])

        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pFecha", fecha_inicio)
        time.sleep(0.5)
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pFecha_caducidad", fecha_caducidad_3(fecha_inicio))
        time.sleep(0.5)
        # Si es un segundo centro, se selecciona como centro de recogida, si no toma el nombre de la empresa
        if fila['nombre_empresa'] is not None and fila['nombre_empresa'].strip() != "":
            webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_origen", fila.get("nombre_empresa", ""))
            time.sleep(0.5)
            webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_origen_centro", fila.get("nombre_recogida", ""))
        else:
           webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_origen", fila.get("nombre_recogida", "")) 
        time.sleep(0.5)

        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_destino", "METALLS DEL CAMP, S.L.") # METALLS DEL CAMP, S.L. siempre
        time.sleep(0.5)
        provincia = str(fila.get("provincia_recogida", "")).strip().upper()
        provincia_normalizada = quitar_tildes(provincia)
        provincias_valencia = [
            "VALENCIA", "ALICANTE", "CASTELLON",
            "VALÈNCIA", "ALACANT", "CASTELLÓ",
            "CASTELLÓN"
        ]
        provincias_valencia_normalizadas = [quitar_tildes(p).upper() for p in provincias_valencia]
        if provincia_normalizada in provincias_valencia_normalizadas or residuo.get("nombre", "").strip().upper() == "HIDROCARBUROS CON AGUA*":
            webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_destino_centro", "METALLS DEL CAMP ( SERRA D") # METALLS DEL CAMP ( SERRA D'ESPADA ) si es de valencia
            # Depende si el residuo es o no peligroso
            time.sleep(1)
            if residuo.get("tipo") == "peligroso":  
                webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_autorizacion_destino", "157/G02/CV")
            elif residuo.get("tipo") == "no peligroso":
                webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_autorizacion_destino", "374/G04/CV")

        else:
            webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_destino_centro", "METALLS DEL CAMP, S.L.U. (EL ROMERAL)") # Si es de otra parte
            time.sleep(1)
            if residuo.get("tipo") == "peligroso":
                webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_autorizacion_destino", "4570002919") # Siempre suponer que es peligroso
            elif residuo.get("tipo") == "no peligroso":
                webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_autorizacion_destino", "G04") # Siempre suponer que es no peligroso
        time.sleep(1)

        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_operador_traslados", "ECO TITAN S.L.") # Siempre ECO TITAN
        time.sleep(1)
        if residuo.get("tipo") == "peligroso":
            webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_autorizacion_operador_traslados", "87/A01/CV") # Si es peligroso
        elif residuo.get("tipo") == "no peligroso":
            webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_autorizacion_operador_traslados", "305/A02/CV")
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pDenominacion_residuo", residuo.get("nombre", ""))
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "pKilos_totales", residuo.get("cantidad", ""))
        webFunctions.clickar_boton_por_clase(driver, "miBoton.aceptar")
    except Exception as error:
        logging.error(f"Error al añadir contrato de tratamiento para la empresa {fila.get('nombre_recogida', '')}: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info("Continuando con el siguiente contrato de tratamiento...")
        else:
            logging.info("Saliendo del proceso de adición de contratos de tratamiento.")
            driver.quit()
            sys.exit()

def añadir_contratos_tratamientos(driver, fila, nombre_empresa=None, ruta_destino=None):
    """
    Añade los contratos de tratamiento para la empresa usando los datos de la fila 'empresa'
    y todos los residuos y cantidades del archivo residuos.txt, junto con su(s) centro(s) y tratamiento(s) asociado(s).
    Incluye manejo de errores con varios intentos.
    """
    intentos = 5
    for intento in range(intentos):
        try:
            residuos_centros = residuos_y_tratamientos_json()
            for item in residuos_centros:
                residuo = item["residuo"]
                centros = item.get("centros", [])
                nombre_residuo = residuo.get("nombre", "").strip().upper()

                # Siempre se usa el primer centro si existe, si no, solo el residuo
                if centros:
                    residuo_con_centro = residuo.copy()
                    residuo_con_centro["centro"] = centros[0]
                    contrato_residuo = residuo_con_centro
                else:
                    contrato_residuo = residuo

                # Crear contrato de tratamiento para todos los residuos
                añadir_contrato_tratamiento(driver, fila, contrato_residuo)
                time.sleep(1)
                # Añadir tratamientos para el residuo
                añadir_tratamientos(driver, fila, item)
                time.sleep(1)
                # Solo para peligrosos, crear notificación
                if "*" in nombre_residuo:
                    provincia = fila.get("provincia_recogida", "").strip().upper()
                    crear_notificacion_tratamiento(driver, ruta_destino, provincia)
                    time.sleep(1)

                # Crear facturación para todos los residuos
                añadir_facturacion(driver, fila, contrato_residuo)
            return
        except Exception as error:
            logging.error(f"Error al añadir contratos de tratamiento (intento {intento+1}): {error}")
            if intento == intentos - 1:
                continuar = funcionesNubelus.preguntar_por_pantalla()
                if continuar:
                    logging.info("Continuando tras error en contratos de tratamiento...")
                else:
                    logging.info("Saliendo del proceso de adición de contratos de tratamiento.")
                    driver.quit()
                    sys.exit()
            time.sleep(1)

def crear_notificacion_tratamiento(driver, ruta_destino=None, provincia: str = ""):
    """
    Crea una notificación en la plataforma Nubelus.
    Descarga el archivo en la carpeta 'ruta_destino' si se indica, si no en 'input'.
    """
    webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Notificación")
    time.sleep(1)
    try:
        provincia_normalizada = quitar_tildes(str(provincia)).strip().upper()
        provincias_validas = [
            "VALENCIA", "ALICANTE", "CASTELLON",
            "VALÈNCIA", "ALACANT", "CASTELLÓ",
            "CASTELLÓN"
        ]
        provincias_validas_normalizadas = [quitar_tildes(p).strip().upper() for p in provincias_validas]

        # Siempre guardar en la carpeta con el nombre del PDF, pero en output o input según provincia
        if provincia_normalizada in provincias_validas_normalizadas:
            base_folder = os.path.join(BASE_DIR, "output")
        else:
            base_folder = os.path.join(BASE_DIR, "input")

        # ruta_destino debe ser el nombre de la carpeta preparada con el nombre del PDF
        if ruta_destino is not None:
            download_path = os.path.join(base_folder, os.path.basename(ruta_destino))
        else:
            # Si no se pasa ruta_destino, usar la carpeta base (output o input)
            download_path = base_folder

        downloadFunctions.ensure_download_path(download_path)
        downloadFunctions.configure_driver_download_path(driver, download_path)

        old_state = downloadFunctions.snapshot_folder_state(download_path)

        if provincia_normalizada not in provincias_validas_normalizadas:
            webFunctions.clickar_boton_por_clase(driver, "icon-magic")
            nuevos = downloadFunctions.wait_for_new_download(download_path, old_state, num_descargas=1, timeout=120)
        else:
            webFunctions.clickar_boton_por_on_click(driver, "adcr_notificar()")
            nuevos = downloadFunctions.wait_for_new_download(download_path, old_state, num_descargas=1, timeout=120)
            editar_notificacion_tratamiento(driver)
        if nuevos:
            logging.info(f"Archivo de notificación descargado en: {nuevos[0]}")
        else:
            logging.error("No se detectó la descarga del archivo de notificación en la carpeta destino.")

    except Exception as error:
        logging.error(f"Error al crear notificación de tratamiento: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info("Continuando con la siguiente notificación...")
        else:
            logging.info("Saliendo del proceso de creación de notificaciones.")
            driver.quit()
            sys.exit()
        return

def editar_notificacion_tratamiento(driver):
    webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Notificación")
    time.sleep(1)
    webFunctions.clickar_boton_por_on_click(driver, "editar_NOTIFICACION()")
    popup = webFunctions.encontrar_pop_up_por_id(driver, "div_editar_NOTIFICACION")
    webFunctions.seleccionar_elemento_por_name(popup, "pNt_notificada_sn", "Si")
    webFunctions.clickar_boton_por_clase(popup, "icon-ok")

def editar_notificaciones_peligrosos(driver):
    """
    Edita la notificación de cada contrato de tratamiento para los residuos peligrosos (con asterisco)
    usando la función editar_notificacion_tratamiento de excelFunctions.
    """
    residuos_centros = residuos_y_tratamientos_json()
    for item in residuos_centros:
        residuo = item["residuo"]
        nombre_residuo = str(residuo.get("nombre", "")).strip().upper()
        if "*" in nombre_residuo:
            webFunctions.clickar_div_residuo_por_nombre(driver, nombre_residuo)
            editar_notificacion_tratamiento(driver)
            webFunctions.abrir_web(driver, WEB_NUBELUS_CONTRATOS)

def editar_notificacion_nubelus(driver, fila):
    """
    Función temporalmente desactivada - no hace nada.
    """
    pass
    
    # webFunctions.abrir_web(driver, WEB_NUBELUS_CONTRATOS)
    # webFunctions.clickar_boton_por_on_click(driver, "filtrar()")
    # webFunctions.escribir_en_elemento_por_name_y_enter_pausa(driver, "waster2_gestionContratosTratamiento__fDenominacion_origen", fila.get("nombre_recogida"))
    # webFunctions.clickar_boton_por_clase(driver, "miBoton.buscar")
    # editar_notificaciones_peligrosos(driver)
    # logging.info("Notificaciones de peligrosos editadas correctamente.")

def añadir_tratamientos(driver, fila, residuo):
    """
    Añade los tratamientos indicados usando los datos de la fila y el residuo (json).
    Si el residuo tiene varios centros, añade tratamientos para cada uno.
    Usa el centro asociado que viene en residuo["centro"] o en residuo["centros"].
    """
    webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Tratamientos")
    time.sleep(1)
    try:
        nombre_residuo = residuo.get("nombre", "").strip().upper()
        centros = residuo.get("centros", [])
        if centros and isinstance(centros, list):
            for idx, centro in enumerate(centros, start=1):
                residuo_con_centro = residuo.copy()
                residuo_con_centro["centro"] = centro
                añadir_tratamiento(driver, fila, residuo_con_centro, indice=idx)
        else:
            añadir_tratamiento(driver, fila, residuo, indice=1)
    except Exception as error:
        logging.error(f"Error al añadir tratamientos para el residuo {nombre_residuo} de la empresa {fila.get('nombre_recogida', '')}: {error}")

def añadir_tratamiento(driver, fila, residuo, indice=1):
    """
    Añade un tratamiento individual usando los datos de la fila, el residuo (json) y el índice de tratamiento.
    Usa el centro y tratamiento asociados que vienen en el json de residuo["centro"].

    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        fila (pandas.Series): Fila del DataFrame con los datos de la empresa.
        residuo (dict): Diccionario con los datos del residuo.
        indice (int): Índice del tratamiento (1, 2 o 3).
    """
    try:
        webFunctions.clickar_boton_por_clase(driver, f"miBoton.editar.editar_{indice}.sinTexto.dcha")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, f"div_editar_tratamiento_posterior_{indice}")
        time.sleep(0.5)
        centro = residuo.get("centro", {})
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(popup, f"pDenominacion_ema_{indice}", centro.get("centro", ""))
        time.sleep(0.5)
        webFunctions.escribir_en_elemento_por_name_y_enter_escape(popup, f"pTratamiento_posterior_{indice}_codigo_ler_2", centro.get("tratamiento", ""))

        webFunctions.esperar_elemento(popup, By.CLASS_NAME, "icon-ok")

        webFunctions.clickar_boton_por_clase(popup, "icon-ok")
        driver = oldDriver
        time.sleep(1)
    except Exception as error:
        logging.error(f"Error al añadir tratamiento {indice} para la empresa {fila.get('nombre_recogida', '')}: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info(f"Continuando con el siguiente tratamiento {indice}...")
        else:
            logging.info("Saliendo del proceso de adición de tratamientos.")
            driver.quit()
            sys.exit()

def residuos_y_tratamientos_json():
    """
    Devuelve una lista de diccionarios con residuos y centros asociados, 
    leyendo directamente del archivo JSON en data/datos_json.txt
    """
    ruta_json = os.path.join("data", "datos_json.txt")
    
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # El JSON ya tiene la estructura correcta que esperamos
        return datos
        
    except FileNotFoundError:
        logging.error(f"No se encontró el archivo {ruta_json}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Error al parsear JSON en {ruta_json}: {e}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado al leer {ruta_json}: {e}")
        return []

def añadir_facturacion(driver, fila, residuo):
    """
    Añade la facturación para un residuo concreto usando los datos de la fila y el residuo.
    Incluye manejo de errores con try-except.
    """
    try:
        webFunctions.seleccionar_elemento_por_id(driver, "fContenido_seleccionado", "Facturación")
        time.sleep(2)

        oldDriver = driver
        webFunctions.clickar_boton_por_on_click(driver, "nuevo_FACTURACION()")
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_nuevo_FACTURACION")

        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(popup, "pNombre_cliente", fila.get("nombre_recogida", ""))
        webFunctions.escribir_en_elemento_por_name_y_enter_pausa(popup, "pDenominacion_producto", residuo.get("nombre", ""))
        residuo_nombre = residuo.get("nombre")

        if residuo_nombre in ["ENVASES PLASTICOS CONTAMINADOS*", "FILTROS DE AIRE"]:
            webFunctions.seleccionar_elemento_por_name(popup, "pCantidad_modo", "Valor fijo")
            webFunctions.seleccionar_elemento_por_name(popup, "pPrecio_modo_venta", "T/Precio 1")
            webFunctions.escribir_en_elemento_por_name_y_enter_pausa(popup, "pCantidad_valor", "1")
        time.sleep(2)
        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        driver = oldDriver
        time.sleep(2)
    except Exception as error:
        logging.error(f"Error al añadir facturación para la empresa {fila.get('nombre_recogida', '')}: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info("Continuando con la siguiente facturación...")
        else:
            logging.info("Saliendo del proceso de adición de facturación.")
            driver.quit()
            sys.exit()

def leer_excel(ruta_excel):
    """
    Lee un archivo Excel desde la carpeta 'data' y devuelve un DataFrame.
    
    Args:
        excel_input (str): Nombre del archivo Excel a leer (por ejemplo, 'mi_excel.xlsx').
        
    Returns:
        pd.DataFrame: DataFrame con los datos del archivo Excel.
    """
    return pd.read_excel(ruta_excel)

def comprobar_datos_excel(excel_input):
    """
    Comprueba si el archivo Excel tiene las columnas necesarias para el proceso de adición de centros.
    Además, limpia cada campo usando limpiar_campo para que los datos sean utilizables.
    Lee el archivo desde la carpeta 'data'.

    Args:
        excel_input (str): Nombre del archivo Excel a comprobar (por ejemplo, 'mi_excel.xlsx').

    Returns:
        pd.DataFrame or bool: DataFrame limpio si el archivo tiene las columnas necesarias, False en caso contrario.
    """
    try:
        df = leer_excel(excel_input)
        required_columns = ['nombre_recogida', 'direccion_recogida', 'cp_recogida',
                            'poblacion_recogida', 'provincia_recogida', 'email_recogida',
                            'telf_recogida']
        if not all(col in df.columns for col in required_columns):
            return False
        
        # Comprobar que existen todas las columnas requeridas
        if not all(col in df.columns for col in required_columns):
            for col in required_columns:
                if col not in df.columns:
                    logging.info(f"Falta la columna requerida en el archivo Excel: {col}")
            return False

        # Limpiar cada campo de las columnas requeridas
        for col in required_columns:
            df[col] = df[col].apply(limpiar_campo)
        
        # Validar que el teléfono tenga 9 dígitos, si no, dejarlo vacío
        def limpiar_telefono(tel):
            """
            Limpia el campo teléfono:
            - Si hay dos números separados por una barra ("/"), toma solo el primero.
            - Elimina cualquier carácter no numérico.
            - Si el resultado tiene 9 dígitos, lo devuelve; si no, devuelve cadena vacía.
            """
            tel_str = str(tel)
            # Si hay una barra, toma solo la parte antes de la barra
            if "/" in tel_str:
                tel_str = tel_str.split("/")[0]
            # Elimina cualquier carácter que no sea dígito
            solo_digitos = ''.join(filter(str.isdigit, tel_str))
            if len(solo_digitos) == 9:
                return solo_digitos
            return ""

        df['telf_recogida'] = df['telf_recogida'].apply(limpiar_telefono)

        return df
    except Exception as e:
        logging.error(f"Error al comprobar el archivo Excel: {e}. Los datos no están en el formato correcto.")
        sys.exit()
def esperar_descarga_completa(ruta_archivo, timeout=30):
    """
    Espera a que el archivo exista y no tenga extensión .crdownload.
    """
    tiempo_inicio = time.time()
    while True:
        if os.path.exists(ruta_archivo) and not os.path.exists(ruta_archivo + ".crdownload"):
            break
        if time.time() - tiempo_inicio > timeout:
            raise TimeoutError("Descarga no completada en el tiempo esperado.")
        time.sleep(1)

def descargar_excel_entidades(driver):
    """
    Descarga el Excel de entidades desde Nubelus y devuelve un DataFrame con su contenido.
    """
    try:
        webFunctions.abrir_web(driver, WEB_NUBELUS_ENTIDAD)
        webFunctions.esperar_elemento_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_id(driver, "moa_bGenerar_excel")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_relacion2excel")
        try:
            webFunctions.clickar_boton_por_on_click(popup, "aceptar_relacion2excel()")
        except Exception as e:
            logging.info(f"Error al aceptar el pop-up: {e}")
        driver = oldDriver

        archivo_xlsx = os.path.join(DOWNLOAD_DIR, "Entidades medioambientales.xlsx")
        try:
            esperar_descarga_completa(archivo_xlsx)
            logging.info(f"Archivo descargado: {archivo_xlsx}")
        except TimeoutError as e:
            logging.error(e)
            continuar = funcionesNubelus.preguntar_por_pantalla()
            if not continuar:
                driver.quit()
                sys.exit()
            return None

        df = pd.read_excel(archivo_xlsx)
        try:
            os.remove(archivo_xlsx)
            logging.info(f"Archivo eliminado: {archivo_xlsx}")
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")
        return df
    except Exception as error:
        logging.error(f"Error al descargar el Excel de entidades: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if not continuar:
            driver.quit()
            sys.exit()
        return None

def descargar_excel_centros(driver):
    """
    Descarga el Excel de centros desde Nubelus y devuelve un DataFrame con su contenido.
    """
    try:
        webFunctions.abrir_web(driver, WEB_NUBELUS_CENTROS)
        webFunctions.esperar_elemento_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_id(driver, "moa_bGenerar_excel")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_relacion2excel")
        try:
            webFunctions.clickar_boton_por_on_click(popup, "aceptar_relacion2excel()")
        except Exception as e:
            logging.info(f"Error al aceptar el pop-up: {e}")
        driver = oldDriver

        archivo_xlsx = os.path.join(DOWNLOAD_DIR, "Centros de entidades medioambientales.xlsx")
        try:
            esperar_descarga_completa(archivo_xlsx)
            logging.info(f"Archivo descargado: {archivo_xlsx}")
        except TimeoutError as e:
            logging.error(e)
            continuar = funcionesNubelus.preguntar_por_pantalla()
            if not continuar:
                driver.quit()
                sys.exit()
            return None

        df = pd.read_excel(archivo_xlsx)
        try:
            os.remove(archivo_xlsx)
            logging.info(f"Archivo eliminado: {archivo_xlsx}")
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")
        return df
    except Exception as error:
        logging.error(f"Error al descargar el Excel de centros: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if not continuar:
            driver.quit()
            sys.exit()
        return None

def descargar_excel_clientes(driver):
    """
    Descarga el Excel de clientes desde Nubelus y devuelve un DataFrame con su contenido.
    """
    try:
        webFunctions.abrir_web(driver, WEB_NUBELUS_CLIENTES)
        webFunctions.esperar_elemento_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_id(driver, "moa_bGenerar_excel")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_relacion2excel")
        try:
            webFunctions.clickar_boton_por_on_click(popup, "aceptar_relacion2excel()")
        except Exception as e:
            logging.info(f"Error al aceptar el pop-up: {e}")
        driver = oldDriver

        archivo_xlsx = os.path.join(DOWNLOAD_DIR, "Clientes.xlsx")
        try:
            esperar_descarga_completa(archivo_xlsx)
            logging.info(f"Archivo descargado: {archivo_xlsx}")
        except TimeoutError as e:
            logging.error(e)
            continuar = funcionesNubelus.preguntar_por_pantalla()
            if not continuar:
                driver.quit()
                sys.exit()
            return None

        df = pd.read_excel(archivo_xlsx)
        try:
            os.remove(archivo_xlsx)
            logging.info(f"Archivo eliminado: {archivo_xlsx}")
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")
        return df
    except Exception as error:
        logging.error(f"Error al descargar el Excel de clientes: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if not continuar:
            driver.quit()
            sys.exit()
        return None

def descargar_excel_usuarios(driver):
    """
    Descarga el Excel de usuarios desde Nubelus y devuelve un DataFrame con su contenido.
    """
    try:
        webFunctions.abrir_web(driver, WEB_NUBELUS_USUARIO)
        webFunctions.esperar_elemento_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_id(driver, "moa_bGenerar_excel")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_relacion2excel")
        try:
            webFunctions.clickar_boton_por_on_click(popup, "aceptar_relacion2excel()")
        except Exception as e:
            logging.info(f"Error al aceptar el pop-up: {e}")
        driver = oldDriver

        archivo_xlsx = os.path.join(DOWNLOAD_DIR, "Usuarios.xlsx")
        try:
            esperar_descarga_completa(archivo_xlsx)
            logging.info(f"Archivo descargado: {archivo_xlsx}")
        except TimeoutError as e:
            logging.error(e)
            continuar = funcionesNubelus.preguntar_por_pantalla()
            if not continuar:
                driver.quit()
                sys.exit()
            return None

        df = pd.read_excel(archivo_xlsx)
        try:
            os.remove(archivo_xlsx)
            logging.info(f"Archivo eliminado: {archivo_xlsx}")
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")
        return df
    except Exception as error:
        logging.error(f"Error al descargar el Excel de usuarios: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if not continuar:
            driver.quit()
            sys.exit()
        return None

def descargar_excel_acuerdos_representacion(driver):
    """
    Descarga el Excel de acuerdos de representación desde Nubelus y devuelve un DataFrame con su contenido.
    """
    try:
        webFunctions.abrir_web(driver, WEB_NUBELUS_ACUERDOS)
        webFunctions.esperar_elemento_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_id(driver, "moa_bGenerar_excel")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_relacion2excel")
        try:
            webFunctions.clickar_boton_por_on_click(popup, "aceptar_relacion2excel()")
        except Exception as e:
            logging.info(f"Error al aceptar el pop-up: {e}")
        driver = oldDriver

        archivo_xlsx = os.path.join(DOWNLOAD_DIR, "Acuerdos de representación.xlsx")
        try:
            esperar_descarga_completa(archivo_xlsx)
            logging.info(f"Archivo descargado: {archivo_xlsx}")
        except TimeoutError as e:
            logging.error(e)
            continuar = funcionesNubelus.preguntar_por_pantalla()
            if not continuar:
                driver.quit()
                sys.exit()
            return None

        df = pd.read_excel(archivo_xlsx)
        try:
            os.remove(archivo_xlsx)
            logging.info(f"Archivo eliminado: {archivo_xlsx}")
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")
        return df
    except Exception as error:
        logging.error(f"Error al descargar el Excel de acuerdos de representación: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if not continuar:
            driver.quit()
            sys.exit()
        return None

def descargar_excel_contratos(driver):
    """
    Descarga el Excel de contratos desde Nubelus y devuelve un DataFrame con su contenido.
    """
    try:
        webFunctions.abrir_web(driver, WEB_NUBELUS_CONTRATOS)
        webFunctions.esperar_elemento_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_clase(driver, "miBoton.mas_opciones")
        webFunctions.clickar_boton_por_id(driver, "moa_bGenerar_excel")
        oldDriver = driver
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_relacion2excel")
        try:
            webFunctions.clickar_boton_por_on_click(popup, "aceptar_relacion2excel()")
        except Exception as e:
            logging.info(f"Error al aceptar el pop-up: {e}")
        driver = oldDriver

        archivo_xlsx = os.path.join(DOWNLOAD_DIR, "Contratos tratamiento.xlsx")
        try:
            esperar_descarga_completa(archivo_xlsx)
            logging.info(f"Archivo descargado: {archivo_xlsx}")
        except TimeoutError as e:
            logging.error(e)
            continuar = funcionesNubelus.preguntar_por_pantalla()
            if not continuar:
                driver.quit()
                sys.exit()
            return None

        df = pd.read_excel(archivo_xlsx)
        try:
            os.remove(archivo_xlsx)
            logging.info(f"Archivo eliminado: {archivo_xlsx}")
        except Exception as e:
            logging.error(f"No se pudo eliminar el archivo: {archivo_xlsx}. Error: {e}")
        return df
    except Exception as error:
        logging.error(f"Error al descargar el Excel de contratos: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if not continuar:
            driver.quit()
            sys.exit()
        return None

def completar_datos_centro(driver, fila):
    """
    Completa los datos del centro de la empresa en la plataforma Nubelus.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        fila (pandas.Series): Fila del DataFrame con los datos de la empresa.
    """
    try:
        webFunctions.abrir_web(driver, WEB_NUBELUS_CENTROS)
        webFunctions.clickar_boton_por_clase(driver, "icon-bolt")

        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_buscar_1")
        webFunctions.completar_campo_y_enter_por_name(popup, "pDenominacion", fila.get("nombre_recogida", ""))
        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        # añadir_autorizaciones(driver, fila)
        rellenar_datos_medioambientales(driver, fila)
    except Exception as error:
        logging.error(f"Error al completar datos del centro para la empresa {fila.get('nombre_recogida', '')}: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info("Continuando con el siguiente centro...")
        else:
            logging.info("Saliendo del proceso de adición de centros.")
            driver.quit()
            sys.exit()

def añadir_cliente_empresa(driver, fila):
    """
    Añade un cliente a la plataforma Nubelus usando los datos de la fila 'empresa'.
    
    Args:
        driver (webdriver.Chrome): Instancia del navegador.
        fila (pandas.Series): Fila del DataFrame con los datos de la empresa.
    """
    try:
        webFunctions.abrir_web(driver, WEB_NUBELUS_ENTIDAD)
        webFunctions.clickar_boton_por_clase(driver, "icon-bolt")
        popup = webFunctions.encontrar_pop_up_por_id(driver, "div_buscar_1")
        webFunctions.completar_campo_y_enter_por_name(popup, 
            "pDenominacion", fila.get("nombre_recogida", ""))
        webFunctions.clickar_boton_por_clase(popup, "miBoton.aceptar")
        time.sleep(0.5)
        funcionesNubelus.crear_proveedor(driver)
        funcionesNubelus.crear_cliente(driver)
    except Exception as error:
        logging.error(f"Error al añadir cliente para la empresa {fila.get('nombre_recogida', '')}: {error}")
        continuar = funcionesNubelus.preguntar_por_pantalla()
        if continuar:
            logging.info("Continuando con el siguiente cliente...")
        else:
            logging.info("Saliendo del proceso de adición de clientes.")
            driver.quit()
            sys.exit()
    
def crear_contratos_faltantes(driver, fila, coincidencias_contratos, ruta_destino=None):
    """
    Crea contratos de tratamiento solo para los residuos que no están ya en los contratos existentes
    para la empresa actual, usando la columna 'Denominacion' del DataFrame coincidencias_contratos.
    Si todos los residuos ya están creados, muestra un mensaje y no hace nada.
    """
    residuos_centros = residuos_y_tratamientos_json()
    
    # Si no hay ningún contrato hecho, crear todos
    if coincidencias_contratos is None:
        residuos_faltantes = residuos_centros
    else:
        residuos_excel = [
            quitar_tildes(str(r_excel)).strip().upper()
            for r_excel in coincidencias_contratos['Denominacion']
        ]
        residuos_faltantes = []
        for item in residuos_centros:
            residuo = item["residuo"]
            nombre_residuo = quitar_tildes(str(residuo.get("nombre", ""))).strip().upper()
            if nombre_residuo not in residuos_excel:
                residuos_faltantes.append(item)

    if not residuos_faltantes:
        logging.info("Todos los contratos de tratamiento ya están creados para esta empresa.")
        sys.exit()

    for item in residuos_faltantes:
        residuo = item["residuo"]
        nombre_residuo = quitar_tildes(str(residuo.get("nombre", ""))).strip().upper()
        centros = item.get("centros", [])

        if centros:
            residuo_con_centro = residuo.copy()
            residuo_con_centro["centro"] = centros[0]
            contrato_residuo = residuo_con_centro
        else:
            contrato_residuo = residuo

        añadir_contrato_tratamiento(driver, fila, contrato_residuo)
        provincia = fila.get("provincia_recogida", "").strip().upper()
        time.sleep(1)
        añadir_tratamientos(driver, fila, item)
        if "*" in nombre_residuo:
            time.sleep(1)
            crear_notificacion_tratamiento(driver, ruta_destino, provincia)
            time.sleep(1)

        añadir_facturacion(driver, fila, contrato_residuo)
    editar_notificacion_nubelus(driver, fila)    
    driver.quit()
    logging.info("Contratos faltantes creados correctamente.")      

def crear_contratos_desde_empresa(driver, fila, ruta_destino=None):
        añadir_empresa(driver, fila)
        funcionesNubelus.crear_proveedor(driver)
        funcionesNubelus.crear_cliente(driver)
        completar_datos_centro(driver, fila)
        añadir_usuario(driver, fila)
        añadir_acuerdo_representacion(driver, fila)
        añadir_contratos_tratamientos(driver, fila, ruta_destino)
        logging.info("Contratos creados correctamente: desde empresa a contratos")
        driver.quit()
        sys.exit()

def crear_contratos_desde_centros(driver, fila, ruta_destino=None):
    """
    Crea contratos de tratamiento desde la pestaña 'Centros' de la empresa.
    Primero añade el centro, luego crea los contratos de tratamiento para cada residuo.
    """
    añadir_centro(driver, fila)
    añadir_cliente_empresa(driver,fila)
    añadir_usuario(driver, fila)
    añadir_acuerdo_representacion(driver, fila)
    añadir_contratos_tratamientos(driver, fila, ruta_destino)
    logging.info("Contratos creados correctamente: desde centro a contratos")
    driver.quit()
    sys.exit()

def crear_contratos_desde_clientes(driver, fila, ruta_destino=None):
    """
    Crea contratos de tratamiento desde la pestaña 'Clientes' de la empresa.
    Primero añade el cliente, luego crea los contratos de tratamiento para cada residuo.
    """
    añadir_cliente_empresa(driver, fila)
    añadir_usuario(driver, fila)
    añadir_acuerdo_representacion(driver, fila)
    añadir_contratos_tratamientos(driver, fila, ruta_destino)
    logging.info("Contratos creados correctamente: desde cliente a contratos")
    driver.quit()
    sys.exit()

def crear_contratos_desde_usuarios(driver, fila, ruta_destino=None):
    """
    Crea contratos de tratamiento desde la pestaña 'Acuerdos de representación' de la empresa.
    Primero añade el acuerdo, luego crea los contratos de tratamiento para cada residuo.
    """
    añadir_usuario(driver, fila)
    añadir_acuerdo_representacion(driver, fila)
    añadir_contratos_tratamientos(driver, fila, ruta_destino)
    logging.info("Contratos creados correctamente: desde usuario a contratos")
    driver.quit()
    sys.exit()

def preparar_carpeta_para_pdf_y_xml(excel_fila):
    """
    Busca el PDF en la carpeta 'entrada', crea una carpeta en 'output' si la provincia es de la Comunidad Valenciana,
    o en 'input' si no lo es, mueve el PDF a esa carpeta y devuelve la ruta para guardar los XML ahí.
    """
    carpeta_entrada = "entrada"
    carpeta_input = "input"
    carpeta_output = "output"

    # Busca el primer PDF en la carpeta entrada
    pdfs = [f for f in os.listdir(carpeta_entrada) if f.lower().endswith(".pdf")]
    if not pdfs:
        raise FileNotFoundError("No se encontró ningún PDF en la carpeta 'entrada'.")
    nombre_pdf = pdfs[0]
    nombre_carpeta = os.path.splitext(nombre_pdf)[0]

    # Extrae la provincia del DataFrame excel_fila si existe la columna 'provincia_recogida'
    provincia = excel_fila.get("provincia_recogida", "").strip()
    provincia_normalizada = quitar_tildes(provincia).strip().upper()
    provincias_valencianas = [
            "VALENCIA", "ALICANTE", "CASTELLON",
            "VALÈNCIA", "ALACANT", "CASTELLÓ",
            "CASTELLÓN"
        ]

    if provincia_normalizada in [quitar_tildes(p).upper() for p in provincias_valencianas]:
        carpeta_destino = carpeta_output
    else:
        carpeta_destino = carpeta_input

    ruta_destino = os.path.join(carpeta_destino, nombre_carpeta)

    # Crea la carpeta destino si no existe
    os.makedirs(ruta_destino, exist_ok=True)

    # Mueve el PDF a la nueva carpeta
    ruta_pdf_origen = os.path.join(carpeta_entrada, nombre_pdf)
    ruta_pdf_destino = os.path.join(ruta_destino, nombre_pdf)
    shutil.copy2(ruta_pdf_origen, ruta_pdf_destino)

    # Devuelve la ruta donde guardar los XML
    return ruta_destino

def crear_contratos_desde_acuerdos_representacion(driver, fila, ruta_destino=None):
    """
    Crea contratos de tratamiento desde la pestaña 'Acuerdos de representación' de la empresa.
    Primero añade el acuerdo, luego crea los contratos de tratamiento para cada residuo.
    """
    añadir_acuerdo_representacion(driver, fila)
    añadir_usuario(driver, fila)
    añadir_contratos_tratamientos(driver, fila, ruta_destino)
    logging.info("Contratos creados correctamente: desde acuerdo a contratos")
    driver.quit()
    sys.exit()