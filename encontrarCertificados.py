import win32crypt
import win32com.client
import logging


def obtener_certificados_personales():
    try:
        # Acceder al almacén Personal de Windows
        store = win32com.client.Dispatch("CAPICOM.Store")
        store.Open(2, "My", 0)  # 2 = STORE_LOCATION_CURRENT_USER, "My" = Personal store

        certificados = store.Certificates
        logging.info(f"Certificados encontrados: {len(certificados)}")

        for cert in certificados:
            # Mostrar el sujeto y el emisor del certificado
            logging.info(f"Sujeto: {cert.Subject}")
            logging.info(f"Emisor: {cert.Issuer}")
            logging.info(f"Huella digital: {cert.Thumbprint}")

        store.Close()
    except Exception as e:
        logging.error(f"Error al acceder al almacén de certificados: {e}")


# Uso:
obtener_certificados_personales()
