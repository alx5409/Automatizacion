import webConfiguration
import pandas
import excelFunctions
import webFunctions
import funcionesNubelus
import time

# URLs de la aplicación Nubelus
WEB_NUBELUS = "https://portal.nubelus.es"
WEB_NUBELUS_ENTIDAD = "https://portal.nubelus.es/?clave=waster2_gestionEntidadesMedioambientales&pAccion=NUEVO"
WEB_NUBELUS_ACUERDOS = "https://portal.nubelus.es/?clave=waster2_gestionAcuerdosRepresentacion&pAccion=NUEVO"
WEB_NUBELUS_CONTRATOS = "https://portal.nubelus.es/?clave=waster2_gestionContratosTratamiento&pAccion=NUEVO"

WEB_NUBELUS_TRATAMIENTOS = "https://portal.nubelus.es/?clave=waster2_gestionContratosTratamiento"
URL_SEGURIDAD = "chrome://settings/security"

def main():
    # Configurar el driver de Selenium
    driver = webConfiguration.configure()

    driver.get(URL_SEGURIDAD)
    time.sleep(5) # Tiempo para clickar manualmente en Protección Mejorada
    
    # Iniciar sesión en Nubelus
    funcionesNubelus.iniciar_sesion(driver)
    time.sleep(5)  # Tiempo para aceptar el pop up de google

    webFunctions.abrir_web(driver, WEB_NUBELUS_TRATAMIENTOS)

    excel_empresa = pandas.read_excel(excelFunctions.EXCEL_RECOGIDAS)
    empresa_prueba = excel_empresa.iloc[36]  # Toma la fila del Excel como empresa de prueba METALLS DEL CAMP, S.L.

    excelFunctions.añadir_contratos_tratamientos(driver, empresa_prueba)
    time.sleep(5)

if __name__ == "__main__":
    main()
