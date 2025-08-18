import loggerConfig
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def configure():
    # Configurar el WebDriver para Google Chrome
    options = webdriver.ChromeOptions()

    # options.add_argument(r'--user-data-dir=C:\Users\Metalls1\AppData\Local\Google\Chrome\User Data')
    options.add_argument('--profile-directory=Profile 2')
    options.add_argument("--no-first-run --no-default-browser-check")
    options.add_argument("--disable-features=ChromeWhatsNewUI")
    options.add_argument("--disable-gpu")  # Desactiva el uso de la GPU
    options.add_argument("--disable-software-rasterizer")  # Desactiva el rasterizador de software

    # Opcional: para que veas errores o popups
    # options.add_argument("--headless")  # puedes quitarlo temporalmente

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")  # Desactiva las notificaciones push
    options.add_argument("--disable-gcm-services")  # Desactiva los servicios de GCM
    options.add_argument("--disable-cloud-import")  # Desactiva la importación en la nube
    options.add_argument("--disable-popup-blocking")  # Desactiva el bloqueo de popups
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,  # Desactiva el gestor de contraseñas
        "profile.password_manager_enabled": False,  # Evita guardar contraseñas
        "profile.default_content_setting_values.notifications": 2  # Opcional: desactiva notificaciones
    })
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=Service(), options=options)
        return driver
    except Exception as e:
        logging.error(f"Error al iniciar el navegador: {e}")
        return None
