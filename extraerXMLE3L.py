import os
import json
import xml.etree.ElementTree as ET

def normalizar_nombre(nombre):
    """
    Normaliza el nombre para usarlo como nombre de archivo/carpeta.
    """
    return (
        nombre.replace(" ", "_")
        .replace("*", "")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("?", "")
        .replace('"', "")
        .replace("<", "")
        .replace(">", "")
        .replace("|", "")
    )

def guardar_regage_json(data, output_dir, nombre_residuo, codigo_regage):
    """
    Guarda el contenido en un archivo {codigo_regage}_{nombre_residuo}.json en output_dir.
    Si ya existe, crea {codigo_regage}_{nombre_residuo}_1.json, etc. para no sobrescribir.
    """
    base_name = f"{codigo_regage}_{normalizar_nombre(nombre_residuo)}"
    ext = ".json"
    filename = base_name + ext
    counter = 1
    full_path = os.path.join(output_dir, filename)
    while os.path.exists(full_path):
        filename = f"{base_name}_{counter}{ext}"
        full_path = os.path.join(output_dir, filename)
        counter += 1
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return full_path

# Guardar historial global en BASE_DIR/historial.json usando una función
def guardar_historial(data):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    historial_path = os.path.join(BASE_DIR, "historial.json")

    # Leer historial existente o crear uno nuevo
    if os.path.exists(historial_path):
        with open(historial_path, "r", encoding="utf-8") as f:
            try:
                historial = json.load(f)
                if not isinstance(historial, list):
                    historial = []
            except Exception:
                historial = []
    else:
        historial = []

    # Añadir el nuevo registro
    historial.append(data)

    # Guardar historial actualizado
    with open(historial_path, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

def extraer_info_xml(path_xml, regage):
    """
    Extrae información relevante del archivo E3L/XML para construir el objeto JSON solicitado.
    """
    tree = ET.parse(path_xml)
    root = tree.getroot()

    # Representante
    nif_representante = ""
    representante = root.find('.//representativeEntity/nationalId')
    if representante is not None and representante.text:
        nif_representante = representante.text.strip()

    # Nombre del representante (de <reasonName>)
    nombre_representante = ""
    representante_nombre = root.find('.//NTTransferOperatorData/entityName/reason/reasonName')
    if representante_nombre is not None and representante_nombre.text:
        nombre_representante = representante_nombre.text.strip()

    # Productor
    nombre_productor = ""
    productor_surname = ""
    # Buscar el responsable del centro del productor
    producer_data = root.find('.//NTProducerData')
    if producer_data is not None:
        responsible = producer_data.find('.//centerResponsiblePerson/personName')
        if responsible is not None:
            name_elem = responsible.find('name')
            surname_elem = responsible.find('surname1')
            if name_elem is not None and name_elem.text:
                nombre_productor = name_elem.text.strip()
            if surname_elem is not None and surname_elem.text:
                productor_surname = surname_elem.text.strip()
            if productor_surname and productor_surname != "-":
                nombre_productor += " " + productor_surname

    nif_productor = ""
    productor_nif = root.find('.//NTProducerData/entityId/nationalId')
    if productor_nif is not None and productor_nif.text:
        nif_productor = productor_nif.text.strip()

    # Residuo
    nombre_residuo = ""
    residuo = root.find('.//NTResidueIdentification/residueDescription')
    if residuo is not None and residuo.text:
        nombre_residuo = residuo.text.strip()

    # Construir el diccionario con los datos
    data = {
        "nombre_representante": nombre_representante,
        "nif_representante": nif_representante,
        "nombre_productor": nombre_productor,
        "nif_productor": nif_productor,
        "nombre_residuo": nombre_residuo,
        "regage": regage
    }

    guardar_historial(data)
    
    # Guardar el JSON en output/{nombre_productor}/{codigo_regage}_{nombre_residuo}.json
    output_dir = os.path.join("output", normalizar_nombre(nombre_representante))
    os.makedirs(output_dir, exist_ok=True)
    guardar_regage_json(data, output_dir, nombre_residuo, regage)

    return data