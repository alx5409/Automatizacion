# Guía de uso - mainNubebot

## ¿Qué hace este programa?

Este programa automatiza la gestión de contratos y notificaciones en la plataforma Nubelus a partir de los datos de recogidas de residuos del excel: excel_recogidas.xls

---

## ¿Cómo se usa?

1. **Prepara los archivos de entrada:**
   - Coloca el archivo Excel de recogidas en la carpeta `entrada` con el nombre `excel_recogidas.xls`.
   - Coloca el PDF asociado en la misma carpeta `entrada`.

2. **Ejecuta el programa:**

   - Haz doble clic en el ejecutable mainNubebot.exe.


3. **Funcionamiento general:**
   - El programa creará una carpeta en `input` con el nombre del PDF.
   - Copiará el PDF a esa carpeta.
   - Todos los archivos XML generados y descargados se guardarán en esa carpeta.
   - El programa irá comprobando y creando en Nubelus las entidades, centros, clientes, usuarios, acuerdos y contratos según los datos del Excel.

---

## ¿Qué hacer en caso de error?

- **Errores comunes:**
  - **Faltan archivos de entrada:** Asegúrate de que el Excel y el PDF están en la carpeta `entrada` y el excel tiene el nombre correcto: excel_recogidas.xls
  - **Faltan columnas en el Excel:** El log indicará qué columna falta. Corrige el archivo Excel y vuelve a ejecutar el programa.
  - **Problemas con el navegador:** Comprueba que tienes Google Chrome instalado y actualizado.
  - **Errores de conexión o login:** Verifica tu conexión a Internet y las credenciales de acceso a Nubelus.

- **¿Dónde ver los errores?**
  - Todos los errores y advertencias se registran en el archivo de logs. Consulta ese archivo para detalles técnicos.

- **¿Qué hacer si el programa se detiene?**
  - Corrige el problema (por ejemplo, añade el archivo que falta, corrige el Excel, etc.).
  - Vuelve a ejecutar el programa.

---

## Consejos adicionales

- **No cierres el navegador manualmente** mientras el programa está en marcha, esto causará un error.
- **No modifiques los archivos de entrada** mientras el programa se está ejecutando.
- Si necesitas soporte, guarda el archivo de log y proporciona el mensaje de error exacto.

---
