"""
Módulo: nimaFunctions.py

Este módulo proporciona funciones de alto nivel para automatizar la búsqueda y extracción de información
de centros y gestores en los portales NIMA de Valencia, Madrid, Castilla-La Mancha y Cataluña mediante Selenium.
Las funciones lanzan excepciones con mensajes descriptivos en caso de error, de modo que se pueda devolver un error HTTP adecuado
en el endpoint correspondiente.
"""

import logging
import webFunctions
import webConfiguration
import excelFunctions

URL_NIMA_CASTILLA = "https://ireno.castillalamancha.es/forms/geref000.htm"
URL_NIMA_VALENCIA = "https://residuos.gva.es/RES_BUSCAWEB/buscador_residuos_avanzado.aspx"
URL_NIMA_MADRID = "https://gestiona.comunidad.madrid/pcea_nima_web/html/web/InicioAccion.icm"
URL_NIMA_CATALUÑA = "https://sdr.arc.cat/sdr/ListNimas.do?menu=G"

# Estructura estándar para empresa y centro
EMPRESA_KEYS = [
    "nif", "nombre", "direccion", "cp", "provincia", "telefono"
]
CENTRO_KEYS = [
    "nima", "nombre", "direccion", "cp", "provincia", "codigo_ine", "telefono", "autorizaciones", "codigos_residuos"
]

def _fill_empresa(data):
    return {
        "nif": data.get("nif", ""),
        "nombre": data.get("nombre", ""),
        "direccion": data.get("direccion", ""),
        "cp": data.get("cp", ""),
        "provincia": data.get("provincia", ""),
        "telefono": data.get("telefono", "")
    }

def _fill_centro(data):
    codigos = data.get("codigos_residuos", [])
    if "P02" not in codigos:
        codigos.append("P02")
    return {
        "nima": data.get("nima", ""),
        "nombre": data.get("nombre", ""),
        "direccion": data.get("direccion", ""),
        "cp": data.get("cp", ""),
        "provincia": data.get("provincia", ""),
        "codigo_ine": data.get("codigo_ine", ""),
        "telefono": data.get("telefono", ""),
        "autorizaciones": data.get("autorizaciones", []),
        "codigos_residuos": codigos
    }

# --- VALENCIA ---
def extraer_datos_valencia(driver):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Valencia.
    Devuelve un diccionario con los datos relevantes.
    Incluye todos los códigos de residuos disponibles para el centro como una lista.
    """
    # Datos de la empresa
    nombre_empresa = webFunctions.obtener_texto_elemento_por_id(driver, "NOMBREEMPRESA1-0") or ""
    nif = webFunctions.obtener_texto_elemento_por_id(driver, "ENIF1-0") or ""
    direccion = webFunctions.obtener_texto_elemento_por_id(driver, "EDIRECCION1-0") or ""
    codigo_postal = webFunctions.obtener_texto_elemento_por_id(driver, "ECODIPOS1-0") or ""
    provincia = webFunctions.obtener_texto_elemento_por_id(driver, "Text8-0") or ""
    telefono = webFunctions.obtener_texto_elemento_por_id(driver, "ETELEFONO1-0") or ""

    # Datos del centro
    nombre_centro = webFunctions.obtener_texto_elemento_por_id(driver, "NOMBRECENTRO1-0-0") or ""
    nima = webFunctions.obtener_texto_elemento_por_id(driver, "FCENCODCENTRO1-0-0") or ""
    direccion_centro = webFunctions.obtener_texto_elemento_por_id(driver, "FDIRECCION1-0-0") or ""
    cp_centro = ""  # No disponible
    provincia_centro = webFunctions.obtener_texto_elemento_por_id(driver, "Text7-0-0") or ""
    codigo_ine_municipio = webFunctions.obtener_texto_elemento_por_id(driver, "FCODINE1-0-0") or ""
    codigo_ine_provincia = codigo_ine_municipio[:2] if codigo_ine_municipio else ""
    telefono_centro = webFunctions.obtener_texto_elemento_por_id(driver, "FTELEFONO1-0-0") or ""

    # Códigos de residuos (como lista)
    autorizaciones = []
    idx = 0
    while True:
        try:
            autorizacion = webFunctions.obtener_texto_elemento_por_id(driver, f"Text10-0-0-{idx}")
            if autorizacion:
                autorizacion_split = autorizacion.split()
                if autorizacion_split:
                    autorizaciones.append(autorizacion_split[0])
            idx += 1
        except Exception:
            break  # Sale del bucle cuando no encuentra más autorizaciones
    
    # Extraer codigos_residuos de las autorizaciones encontradas
    claves_autorizacion = list(excelFunctions.dic_codigos_residuos_valencia.keys())
    codigos_residuos = []
    for autorizacion in autorizaciones:
        for clave in claves_autorizacion:
            if clave in autorizacion and clave not in codigos_residuos:
                codigos_residuos.append(clave)

    empresa = _fill_empresa({
        "nif": nif,
        "nombre": nombre_empresa,
        "direccion": direccion,
        "cp": codigo_postal,
        "provincia": provincia,
        "telefono": telefono
    })
    centro = _fill_centro({
        "nima": nima,
        "nombre": nombre_centro,
        "direccion": direccion_centro,
        "cp": cp_centro,
        "provincia": provincia_centro,
        "codigo_ine": codigo_ine_municipio,
        "telefono": telefono_centro,
        "autorizaciones": autorizaciones,
        "codigos_residuos": codigos_residuos
    })
    return {
        "empresa": empresa,
        "centros": [centro]
    }

def busqueda_NIMA_Valencia(nif):
    """
    Busca todos los centros asociados a un NIF en la web de NIMA Valencia y devuelve un JSON con los datos de la empresa
    y una lista de sus centros asociados.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_VALENCIA)
    webFunctions.escribir_en_elemento_por_id(driver, "ctl00_ContentPlaceHolder1_txtNIF", nif)
    webFunctions.clickar_boton_por_id(driver, "ctl00_ContentPlaceHolder1_btBuscar")

    empresa = None
    centros = []
    try:
        # Buscar todos los enlaces de gestor en la tabla de resultados y guardar sus URLs
        enlaces = webFunctions.encontrar_elementos(
            driver,
            webFunctions.By.XPATH,
            "//a[starts-with(@id, 'ctl00_ContentPlaceHolder1_gvResultados_ctl') and contains(@id, '_hypGestor')]"
        )
        logging.info(f"Encontrados {len(enlaces)} centros asociados al NIF {nif}.")
        urls_centros = [enlace.get_attribute("href") for enlace in enlaces]

        for url in urls_centros:
            try:
                driver.get(url)
                logging.info(f"Procesando URL: {url}")
                datos_centro = extraer_datos_valencia(driver)
                if datos_centro:
                    # Solo guardar los datos de empresa del primer centro
                    if empresa is None and "empresa" in datos_centro:
                        empresa = datos_centro["empresa"]
                    # Guardar solo los datos del centro
                    if "centros" in datos_centro:
                        centros.extend(datos_centro["centros"])
            except Exception as e:
                logging.error(f"ERROR procesando la URL {url}: {e}")
                continue
        # No es necesario hacer driver.back() porque vamos directo a la siguiente URL
    except Exception as e:
        logging.error(f"ERROR: No se han podido procesar los centros asociados: {e}")
    driver.quit()
    
    if empresa and centros:
        return {
            "empresa": empresa,
            "centros": centros
        }
    else:
        return {
            "empresa": _fill_empresa({}),
            "centros": []
        }

# --- MADRID ---
def extraer_datos_madrid(driver):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Madrid.
    Devuelve un diccionario con los datos de la sede y del centro.
    Además, extrae todas las autorizaciones válidas y las guarda en una lista bajo la clave 'autorizaciones' en el centro.
    """
    # Usa las claves del diccionario de excelFunctions
    claves_autorizacion = list(excelFunctions.dic_codigos_residuos_valencia.keys())

    # Datos del EMA (empresa)
    datos_empresa = {
        "nif": webFunctions.leer_texto_por_campo(driver, "NIF:") or "",
        "nombre": webFunctions.leer_texto_por_campo(driver, "Razón Social:") or "",
        "direccion": webFunctions.leer_texto_por_campo(driver, "Dirección Sede:") or "",
        "cp": webFunctions.leer_texto_por_campo(driver, "CP:") or "",
        "provincia": webFunctions.leer_texto_por_campo(driver, "Provincia:") or "",
        "telefono": ""  # No disponible
    }

    # Datos del centro (usando el segundo elemento para cada campo)
    datos_centro = {
        "nima": webFunctions.leer_texto_por_campo(driver, "NIMA:") or "",
        "nombre": webFunctions.leer_texto_por_campo(driver, "Denominación del Centro:") or "",
        "direccion": webFunctions.leer_texto_por_campo(driver, "Dirección Centro:") or "",
        "cp": webFunctions.leer_texto_por_campo_indice(driver, "CP:", indice=1) or "",
        "provincia": webFunctions.leer_texto_por_campo_indice(driver, "Provincia:", indice=1) or "",
        "codigo_ine": webFunctions.leer_texto_por_campo_indice(driver, "Código INE Municipio:", indice=1) or "",
        "telefono": "",  # No disponible
        "autorizaciones": [],
        "codigos_residuos": []
    }

    # Extraer autorizaciones válidas
    autorizaciones = []
    try:
        elementos_p = driver.find_elements(webFunctions.By.TAG_NAME, "p")
        for elem in elementos_p:
            texto = elem.text
            if len(texto) == 17: # Solo se queda con las autorizaciones con formato valido
                autorizaciones.append(texto)

    except Exception as e:
        logging.error(f"Error extrayendo autorizaciones en Madrid: {e}")

    datos_centro["autorizaciones"] = autorizaciones

    # Extraer codigos_residuos de las autorizaciones encontradas
    codigos_residuos = []
    for autorizacion in autorizaciones:
        for clave in claves_autorizacion:
            if clave in autorizacion and clave not in codigos_residuos:
                codigos_residuos.append(clave)
    datos_centro["codigos_residuos"] = codigos_residuos

    empresa = _fill_empresa(datos_empresa)
    centro = _fill_centro(datos_centro)
    return {
        "empresa": empresa,
        "centros": [centro]
    }

def busqueda_NIMA_Madrid(nif):
    """
    Busca todos los centros asociados a un NIF en la web de NIMA Madrid y devuelve un JSON con los datos de la sede
    y una lista de sus centros asociados.
    """
    driver = webConfiguration.configure()
    webFunctions.abrir_web(driver, URL_NIMA_MADRID)
    webFunctions.escribir_en_elemento_por_id(driver, "nif", nif)

    # Buscar y hacer click en el enlace <a> con onclick="buscar('form');"
    webFunctions.clickar_enlace_por_onclick(driver, "buscar('form');")

    empresa = None
    centros = []
    try:
        # Guarda todos los onclicks de los botones de consultar
        botones = webFunctions.encontrar_elementos(
            driver,
            webFunctions.By.XPATH,
            "//input[@type='button' and @value='Consultar' and contains(@onclick, 'consultar(')]"
        )
        logging.info(f"Encontrados {len(botones)} centros asociados al NIF {nif}.")
        onclicks = [boton.get_attribute("onclick") for boton in botones]

        for onclick in onclicks:
            try:
                boton = webFunctions.encontrar_elemento(
                    driver,
                    webFunctions.By.XPATH,
                    f"//input[@type='button' and @value='Consultar' and @onclick=\"{onclick}\"]"
                )
                if boton:
                    boton.click()
                    try:
                        datos_centro = extraer_datos_madrid(driver)
                        if datos_centro:
                            if empresa is None and "empresa" in datos_centro:
                                empresa = datos_centro["empresa"]
                            if "centros" in datos_centro:
                                for centro in datos_centro["centros"]:
                                    # Añadir P02 si no está
                                    if "codigos_residuos" in centro:
                                        if "P02" not in centro["codigos_residuos"]:
                                            centro["codigos_residuos"].append("P02")
                                    else:
                                        centro["codigos_residuos"] = ["P02"]
                                    centros.append(centro)
                    except Exception as e:
                        logging.error(f"ERROR: No se han podido extraer los datos del centro en Madrid: {e}")
                    driver.back()
                else:
                    logging.warning("No se encontró el botón 'Consultar' para el onclick esperado.")
            except Exception as e:
                logging.error(f"ERROR: No se pudo encontrar o hacer click en el botón 'Consultar': {e}")
    except Exception as e:
        logging.error(f"ERROR: No se han podido procesar los centros asociados en Madrid para el NIF {nif}. Excepción: {e}")
    driver.quit()
    if empresa and centros:
        return {
            "empresa": empresa,
            "centros": centros
        }
    else:
        return {
            "empresa": _fill_empresa({}),
            "centros": []
        }

# --- CASTILLA-LA MANCHA ---
def busqueda_NIMA_Castilla(nif):
    """
    Busca todos los centros asociados a un NIF en la web de NIMA Castilla-La Mancha y devuelve un JSON con los datos de la empresa
    y una lista de sus centros asociados. Devuelve None si no encuentra resultados.
    """
    driver = webConfiguration.configure()
    datos_json = None
    try:
        webFunctions.abrir_web(driver, URL_NIMA_CASTILLA)
        webFunctions.clickar_boton_por_id(driver, "enlace_productores")
        webFunctions.escribir_en_elemento_por_id(driver, "input_NIF_CIF", nif)
        webFunctions.clickar_boton_por_id(driver, "boton_buscar")
        if webFunctions.clickar_imagen_generar_excel(driver, timeout=60):
            datos_json = excelFunctions.esperar_y_guardar_datos_centro_json_Castilla(extension=".xls", timeout=60)
            if not datos_json:
                logging.error("No se pudieron extraer los datos desde el Excel en Castilla")
        else:
            logging.error("No se ha encontrado la imagen para generar el Excel en Castilla.")
    except Exception:
        logging.error("No se ha podido generar o procesar el Excel en Castilla.")
    finally:
        driver.quit()
    # Estandarizar estructura
    empresa_dict = datos_json["empresa"] if datos_json and "empresa" in datos_json else {}
    empresa = _fill_empresa(empresa_dict)
    # Eliminar el campo 'nif' del resultado final para Castilla
    if "nif" in empresa:
        empresa["nif"] = nif
    centros = []
    if datos_json and "centros" in datos_json:
        for centro in datos_json["centros"]:
            # Añadir P02 si no está
            codigos = centro.get("codigos_residuos", [])
            if "P02" not in codigos:
                codigos.append("P02")
            centro["codigos_residuos"] = codigos
            centros.append(_fill_centro(centro))
    return {
        "empresa": empresa,
        "centros": centros
    }

# --- CATALUÑA ---
def extraer_datos_cataluña(driver, nif):
    """
    Extrae los datos principales de la ficha de un centro en la web de NIMA Cataluña.
    Devuelve un diccionario con los datos de la empresa y una lista de centros.
    Lanza mensajes de error claros y evita mostrar stacktraces de Selenium.
    """
    logging.info(f"Buscando NIF: {nif}")
    selector_nif = f"//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nif:'] and contains(., '{nif}')]"
    try:
        webFunctions.esperar_elemento(driver, "xpath", selector_nif)
        logging.info("Elemento NIF encontrado")
    except Exception as e:
        mensaje = str(e).splitlines()[0] if str(e) else repr(e)
        logging.error(f"No se encontró el elemento NIF para el NIF {nif}: {mensaje}")
        return None

    # Extraer NIF
    valor_nif = ""
    try:
        texto_div_nif = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nif)
        valor_nif = texto_div_nif.split("Nif:")[-1].strip() if "Nif:" in texto_div_nif else ""
    except Exception as e:
        logging.error(f"Error extrayendo NIF del div: {e}")

    selector_nima = "//div[contains(@class, 'col-xs-4') and b[normalize-space(text())='Nima:']]"
    nima = ""
    try:
        texto_div_nima = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_nima)
        nima = texto_div_nima.split("Nima:")[-1].strip() if "Nima:" in texto_div_nima else ""
    except Exception as e:
        logging.error(f"Error extrayendo NIMA: {e}")

    selector_razon = "//div[contains(@class, 'col-xs-8') and b[normalize-space(text())='Raó social:']]"
    nombre_empresa = ""
    try:
        texto_div_razon = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_razon)
        if "Raó social:" in texto_div_razon:
            nombre_empresa = texto_div_razon.split("Raó social:")[-1].strip()
            nombre_empresa = " ".join(nombre_empresa.split())
    except Exception as e:
        logging.error(f"Error extrayendo Razón Social: {e}")
    selector_codis = "//div[contains(@class, 'col-xs-8') and b[normalize-space(text())='Codis:']]"
    codigos_residuo = ""
    try:
        texto_div_codis = webFunctions.esperar_y_obtener_texto(driver, "xpath", selector_codis)
        if "Codis:" in texto_div_codis:
            codigos_residuo = texto_div_codis.split("Codis:")[-1].strip()
            codigos_residuo = " ".join(codigos_residuo.split())
    except Exception as e:
        logging.error(f"Error extrayendo Códigos de residuo: {e}")

    # Extraer todos los centros de la tabla
    selector_trs = "//tr[contains(@class, 'llistaopen1') or contains(@class, 'llistaopen2')]"
    centros = []
    try:
        filas = webFunctions.encontrar_elementos(driver, webFunctions.By.XPATH, selector_trs)
        for fila in filas:
            celdas = fila.find_elements("tag name", "td")
            centro = {
                "nima": celdas[0].text.strip() if len(celdas) > 0 else "",
                "nombre": "",  # No disponible
                "direccion": celdas[2].text.strip() if len(celdas) > 2 else "",
                "cp": celdas[3].text.strip() if len(celdas) > 3 else "",
                "provincia": "",  # No disponible
                "codigo_ine": celdas[3].text.strip()[:2] if len(celdas) > 3 else "",
                "telefono": "",  # No disponible
                "autorizaciones": [celdas[1].text.strip()] if len(celdas) > 1 else [],
                "codigos_residuos": [codigos_residuo] if codigos_residuo else []
            }
            centros.append(_fill_centro(centro))
    except Exception as e:
        logging.error(f"Error extrayendo filas de centros: {e}")
    empresa = _fill_empresa({
        "nif": valor_nif,
        "nombre": nombre_empresa,
        "direccion": "",
        "cp": "",
        "provincia": "",
        "telefono": ""
    })
    return {
        "empresa": empresa,
        "centros": centros
    }

def busqueda_NIMA_Cataluña(nif):
    driver = webConfiguration.configure()
    try:
        webFunctions.abrir_web(driver, URL_NIMA_CATALUÑA)
        webFunctions.escribir_en_elemento_por_name(driver, "cercaNif", nif)
        webFunctions.clickar_boton_por_texto(driver, "CERCAR")
        datos_json = extraer_datos_cataluña(driver, nif)
        if (
            not datos_json or
            not isinstance(datos_json, dict) or
            "empresa" not in datos_json or
            "centros" not in datos_json
        ):
            return {
                "empresa": _fill_empresa({}),
                "centros": []
            }
    except Exception as e:
        driver.quit()
        return {
            "empresa": _fill_empresa({}),
            "centros": []
        }
    driver.quit()
    return datos_json