# Verificador de Brechas de Seguridad de Correos Electrónicos

Este script de Python verifica si las direcciones de correo electrónico han sido comprometidas en brechas de seguridad conocidas utilizando la API de Have I Been Pwned (HIBP). Permite a los usuarios verificar correos desde un archivo CSV o manualmente, muestra los resultados en una tabla formateada, guarda los resultados en archivos CSV o Excel, y ofrece la opción de enviar el informe por correo electrónico si se encuentran brechas.

## Características

- Verificación de correos electrónicos utilizando la API de Have I Been Pwned.
- Lectura de correos electrónicos desde un archivo CSV.
- Verificación manual de correos electrónicos individuales.
- Visualización de resultados en una tabla formateada en la consola.
- Exportación de resultados a CSV y Excel.
- Envío de informes por correo electrónico utilizando SMTP2GO.
- Manejo seguro de credenciales mediante variables de entorno.

## Requisitos

- Python 3.7+
- Bibliotecas de Python (ver `requirements.txt`)

## Instalación

1. Clona este repositorio o descarga el script.
2. Crea un entorno virtual (recomendado):
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Configuración

Este proyecto utiliza variables de entorno para manejar información sensible. Por defecto, se configuran para usar la API de Have I Been Pwned (HIBP) y el servicio de correo SMTP2GO, pero puedes adaptarlas según tus necesidades.

1. Crea un archivo `.env` en el mismo directorio que el script con el siguiente contenido:

   ```
   # Configuración de Have I Been Pwned (HIBP)
   HIBP_API_KEY=tu_clave_api_de_hibp

   # Configuración de SMTP2GO (o tu servicio de correo preferido)
   SMTP2GO_EMAIL=tu_correo@tudominio.com
   SMTP2GO_USERNAME=tu_usuario_smtp2go
   SMTP2GO_PASSWORD=**********
   SENDER_EMAIL=tu_correo_remitente@tudominio.com
   ```

2. Reemplaza los valores de ejemplo con tus credenciales reales:
   - Para HIBP: Obtén tu API key en [https://haveibeenpwned.com/API/Key](https://haveibeenpwned.com/API/Key)
   - Para SMTP2GO: Regístrate en [https://www.smtp2go.com/](https://www.smtp2go.com/) y obtén tus credenciales

   Si prefieres usar otro servicio de correo, asegúrate de ajustar las variables de entorno y el código de envío de correo.

3. Crea las carpetas 'deposito' y 'generados' en el mismo directorio que el script:
   ```
   mkdir deposito generados
   ```

## Uso

Ejecuta el script con:


```
python script.py
```

Sigue las instrucciones en pantalla para:
1. Verificar correos desde un archivo CSV.
2. Agregar y verificar un correo manualmente.
3. Guardar los resultados en CSV o Excel.
4. Enviar los resultados por correo electrónico (si se encuentran brechas).

## Estructura del Proyecto

- `script.py`: El script principal.
- `requirements.txt`: Lista de dependencias del proyecto.
- `.env`: Archivo para almacenar variables de entorno (no incluido en el repositorio).
- `README.md`: Este archivo.

## Funciones Principales

- `verificar_correo(correo)`: Verifica un correo electrónico usando la API de HIBP.
- `verificar_correos_csv(archivo)`: Verifica todos los correos en un archivo CSV.
- `mostrar_resultados(datos)`: Muestra los resultados en una tabla formateada.
- `guardar_csv(datos, nombre_archivo)`: Guarda los resultados en un archivo CSV.
- `guardar_excel(datos, nombre_archivo)`: Guarda los resultados en un archivo Excel.
- `enviar_correo(destinatario, archivo_adjunto)`: Envía un correo con el informe adjunto.


## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de hacer un pull request.

## Licencia

[MIT License](https://opensource.org/licenses/MIT)
