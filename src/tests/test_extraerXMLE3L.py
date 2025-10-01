import os
import json
from funciones.extraerXMLE3L import extraer_info_xml, normalizar_nombre

if __name__ == "__main__":
    # Ruta al XML de prueba
    xml_path = "NT30460004811420250013409.xml"
    regage = "NT30460004811420250013409"

    # Ejecutar la función de extracción
    data = extraer_info_xml(xml_path, regage)

    # Mostrar el JSON generado por pantalla
    print("JSON generado:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # Comprobar si el archivo se ha guardado correctamente
    nombre_productor = normalizar_nombre(data.get("nombre_productor", "desconocido"))
    nombre_residuo = normalizar_nombre(data.get("nombre_residuo", ""))
    output_dir = os.path.join("output", nombre_productor)
    json_file = os.path.join(output_dir, f"{regage}_{nombre_residuo}.json")
    if os.path.exists(json_file):
        print(f"Archivo JSON guardado en: {json_file}")
    else:
        print("No se encontró el archivo JSON esperado.")
