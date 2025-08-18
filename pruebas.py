import selenium
from selenium import webdriver
import webConfiguration
import time
URL_SEGURIDAD = "chrome://settings/security"
# driver = webConfiguration.configure()
driver = selenium.webdriver.Chrome()
driver.get(URL_SEGURIDAD)
time.sleep(5)  # Espera a que la página cargue completamente