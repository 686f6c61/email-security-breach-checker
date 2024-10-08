# Importaciones necesarias
import csv  # Para leer y escribir archivos CSV
import time  # Para manejar pausas en el código
import pandas as pd  # Para manejar datos tabulares y exportar a Excel
import httpx  # Cliente HTTP para hacer peticiones a la API
import socket  # Para configurar el tiempo de espera de las conexiones
import json  # Para manejar datos en formato JSON
from rich.console import Console  # Para mejorar la presentación en consola
from rich.table import Table  # Para crear tablas bonitas en la consola
from rich import box  # Para estilos de bordes en las tablas
from rich import print
from rich.panel import Panel
from rich.text import Text
import smtplib  # Para enviar correos electrónicos
from email.mime.multipart import MIMEMultipart  # Para crear mensajes de correo con adjuntos
from email.mime.base import MIMEBase  # Para manejar archivos adjuntos en correos
from email.mime.text import MIMEText  # Para añadir texto al cuerpo del correo
from email import encoders  # Para codificar archivos adjuntos
import os  # Para operaciones del sistema de archivos
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env
from pathlib import Path

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar el tiempo de espera de las conexiones
socket.setdefaulttimeout(10)  # 10 segundos de tiempo de espera

# Crear una instancia de Console para una mejor presentación en la terminal
console = Console()

# Obtener las variables de entorno
API_KEY = os.getenv('HIBP_API_KEY')
SMTP2GO_EMAIL = os.getenv('SMTP2GO_EMAIL')
SMTP2GO_USERNAME = os.getenv('SMTP2GO_USERNAME')
SMTP2GO_PASSWORD = os.getenv('SMTP2GO_PASSWORD')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')  

def mostrar_entradilla():
    """
    Muestra una entradilla con información del programa en un recuadro ASCII.
    Esta función proporciona una presentación visual atractiva del programa,
    incluyendo su título, versión, descripción y enlace al repositorio de GitHub.
    """
    titulo = Text("Verificador de Brechas de Seguridad en correo electrónico", style="bold cyan")
    version = Text("Versión 0.1", style="italic green")
    descripcion = Text("Este programa verifica si las direcciones de correo electrónico han sido comprometidas en brechas de seguridad conocidas.", style="yellow")
    repo = Text("GitHub: https://github.com/686f6c61", style="blue underline")
    
    contenido = f"{titulo}\n\n{version}\n\n{descripcion}\n\n{repo}"
    panel = Panel(contenido, expand=False, border_style="bold blue")
    console.print(panel)

def verificar_configuracion():
    """
    Verifica que todas las variables de entorno necesarias estén configuradas.
    Esta función es crucial para asegurar que el programa tenga acceso a todas
    las credenciales y configuraciones necesarias antes de ejecutar sus operaciones principales.
    """
    variables_requeridas = ['HIBP_API_KEY', 'SMTP2GO_EMAIL', 'SMTP2GO_USERNAME', 'SMTP2GO_PASSWORD', 'SENDER_EMAIL']  # Actualizado
    for var in variables_requeridas:
        if not os.getenv(var):
            console.print(f"[bold red]Error: La variable de entorno {var} no está configurada en el archivo .env[/bold red]")
            return False
    return True

def leer_csv(archivo):
    """
    Lee un archivo CSV y devuelve una lista de correos electrónicos.
    Esta función es fundamental para procesar archivos de entrada que contienen
    múltiples direcciones de correo electrónico para su verificación.
    """
    correos = []
    with open(archivo, 'r') as f:
        lector = csv.reader(f)
        for fila in lector:
            correos.append(fila[0])  # Asume que el correo está en la primera columna
    return correos

def verificar_correo(correo):
    """
    Verifica un correo electrónico usando la API de Have I Been Pwned.
    Esta función realiza la consulta principal a la API de HIBP para determinar
    si un correo electrónico ha sido comprometido en alguna brecha de seguridad conocida.
    """
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{correo}"
    headers = {
        "hibp-api-key": API_KEY,
        "user-agent": "VerificadorCorreosScript"
    }
    params = {
        "truncateResponse": "false"  # Para obtener todos los detalles de las brechas
    }
    
    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=params)
    
    # Imprimir información de depuración
    console.print(f"\nRespuesta para {correo}:")
    console.print(f"Código de estado: {response.status_code}")
    console.print(f"Encabezados de respuesta:")
    console.print(json.dumps(dict(response.headers), indent=2))
    console.print(f"Contenido de la respuesta:")
    console.print(response.text)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        console.print(f"No se encontraron brechas para {correo}")
        return []
    elif response.status_code == 401:
        console.print("Error de autenticación. Verifica tu clave API.")
        return None
    elif response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        console.print(f"Límite de tasa excedido. Esperando {retry_after} segundos.")
        time.sleep(retry_after)
        return verificar_correo(correo)  # Intentar de nuevo después de esperar
    else:
        console.print(f"Error al verificar {correo}: {response.status_code}")
        return None

def listar_archivos_csv(directorio):
    """
    Lista los archivos CSV en el directorio especificado.
    Esta función ayuda al usuario a identificar los archivos disponibles para su procesamiento.
    """
    archivos_csv = [f for f in os.listdir(directorio) if f.endswith('.csv')]
    if archivos_csv:
        console.print("[bold cyan]Archivos CSV disponibles:[/bold cyan]")
        for archivo in archivos_csv:
            console.print(f"- {archivo}")
    else:
        console.print("[yellow]No se encontraron archivos CSV en el directorio.[/yellow]")

def verificar_correos_desde_archivo(archivo):
    """
    Verifica todos los correos en un archivo CSV.
    Esta función procesa un archivo completo de correos electrónicos, realizando
    verificaciones individuales para cada uno y respetando los límites de tasa de la API.
    """
    correos = leer_csv(archivo)
    resultados = {}
    for correo in correos:
        resultados[correo] = verificar_correo(correo)
        time.sleep(1.5)  # Pausa para respetar el límite de tasa de la API
    return resultados

def agregar_correo_manual():
    """
    Permite al usuario agregar y verificar un correo manualmente.
    Esta función proporciona una interfaz para verificar correos individuales sin necesidad de un archivo CSV.
    """
    correo = console.input("[bold yellow]Ingrese el correo electrónico a verificar: [/bold yellow]")
    return {correo: verificar_correo(correo)}

def procesar_resultados(resultados):
    """
    Procesa los resultados de la verificación y los formatea para su presentación.
    Esta función toma los datos crudos de la API y los estructura en un formato más legible y analizable.
    """
    datos = []
    for correo, brechas in resultados.items():
        if brechas:
            for brecha in brechas:
                datos.append({
                    'Correo': correo,
                    'Nombre de la brecha': brecha.get('Name', 'Desconocido'),
                    'Título': brecha.get('Title', 'Desconocido'),
                    'Dominio': brecha.get('Domain', 'Desconocido'),
                    'Fecha de la brecha': brecha.get('BreachDate', 'Desconocida'),
                    'Cuentas afectadas': str(brecha.get('PwnCount', 'Desconocido')),
                    'Datos comprometidos': ', '.join(brecha.get('DataClasses', ['Desconocido'])),
                    'Es verificado': 'Sí' if brecha.get('IsVerified', False) else 'No',
                    'Es sensible': 'Sí' if brecha.get('IsSensitive', False) else 'No'
                })
        else:
            datos.append({
                'Correo': correo,
                'Nombre de la brecha': 'No comprometido',
                'Título': '-',
                'Dominio': '-',
                'Fecha de la brecha': '-',
                'Cuentas afectadas': '-',
                'Datos comprometidos': '-',
                'Es verificado': '-',
                'Es sensible': '-'
            })
    return datos

def mostrar_resultados(datos):
    """
    Muestra los resultados en una tabla formateada en la consola.
    Esta función presenta los resultados de manera visualmente atractiva y fácil de leer para el usuario.
    """
    table = Table(title="Resultados de la verificación", box=box.ROUNDED)
    
    # Añadir columnas
    for columna in datos[0].keys():
        table.add_column(columna, style="cyan", no_wrap=True)
    
    # Añadir filas
    for fila in datos:
        values = list(fila.values())
        if fila['Nombre de la brecha'] == 'No comprometido':
            table.add_row(*values, style="green")
        else:
            table.add_row(*values, style="red")
    
    console.print(table)

def guardar_csv(datos, nombre_archivo):
    """
    Guarda los resultados en un archivo CSV.
    Esta función permite exportar los resultados para su posterior análisis o referencia.
    """
    df = pd.DataFrame(datos)
    df.to_csv(nombre_archivo, index=False)
    console.print(f"[green]Resultados guardados en {nombre_archivo}[/green]")

def guardar_excel(datos, nombre_archivo):
    """
    Guarda los resultados en un archivo Excel.
    Similar a guardar_csv, pero en formato Excel para mayor compatibilidad y funcionalidad.
    """
    df = pd.DataFrame(datos)
    df.to_excel(nombre_archivo, index=False)
    console.print(f"[green]Resultados guardados en {nombre_archivo}[/green]")

def enviar_correo(destinatario, archivo_adjunto):
    """
    Envía un correo electrónico con el informe adjunto usando SMTP2GO.
    Esta función permite compartir los resultados de manera segura y eficiente por correo electrónico.
    """
    # Configuración de SMTP2GO
    smtp_server = "mail.smtp2go.com"
    smtp_port = 2525

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = destinatario
    msg['Subject'] = "Informe de verificación de brechas de seguridad"

    # Cuerpo del mensaje
    cuerpo = """
Hola,

Soy el script de seguridad de Rafa y te envío adjunto el informe de verificación de brechas de seguridad en formato Excel.

En el archivo encontrarás información sobre posibles compromisos de seguridad relacionados con las direcciones de correo electrónico que hemos analizado. Te sugiero que le des un vistazo y, si es necesario, tomes las medidas necesarias para proteger tus cuentas.

Si tienes alguna pregunta o inquietud, no dudes en contactar a Rafa.

Saludos,
El Script de R,
    """
    msg.attach(MIMEText(cuerpo, 'plain'))

    # Adjuntar el archivo
    with open(archivo_adjunto, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(archivo_adjunto)}",
    )
    msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(SMTP2GO_USERNAME, SMTP2GO_PASSWORD)
        
        # Enviar el correo
        texto = msg.as_string()
        server.sendmail(SMTP2GO_EMAIL, destinatario, texto)
        
        # Cerrar la conexión
        server.quit()
        
        console.print("[green]Correo enviado exitosamente.[/green]")
    except Exception as e:
        console.print(f"[red]Error al enviar el correo: {str(e)}[/red]")

def menu_principal():
    """
    Muestra el menú principal y devuelve la opción seleccionada.
    Esta función proporciona la interfaz principal del usuario para navegar por las diferentes funcionalidades del programa.
    """
    console.print("\n[bold cyan]Menú principal:[/bold cyan]")
    console.print("1. Verificar correos desde CSV")
    console.print("2. Agregar y verificar correo manualmente")
    console.print("3. Listar archivos CSV disponibles")
    console.print("4. Salir")
    return console.input("[bold yellow]Seleccione una opción: [/bold yellow]")

def verificar_correos_csv():
    """
    Maneja el proceso de verificar correos desde un archivo CSV.
    Esta función orquesta el proceso completo de selección de archivo, verificación y presentación de resultados.
    """
    while True:
        nombre_archivo = console.input("[bold yellow]Ingrese el nombre del archivo CSV en la carpeta 'deposito' (o 'atrás' para volver): [/bold yellow]")
        if nombre_archivo.lower() == 'atrás':
            return
        
        ruta_archivo = Path('deposito') / nombre_archivo
        if not ruta_archivo.exists():
            console.print(f"[bold red]El archivo {nombre_archivo} no existe en la carpeta 'deposito'.[/bold red]")
            continue

        with console.status("[bold green]Verificando correos...[/bold green]"):
            resultados = verificar_correos_desde_archivo(str(ruta_archivo))
        if resultados:
            datos = procesar_resultados(resultados)
            mostrar_resultados(datos)
            guardar_resultados(datos)
        break

def guardar_resultados(datos):
    """
    Maneja el proceso de guardar los resultados y enviar por correo si es necesario.
    """
    Path('generados').mkdir(exist_ok=True)

    while True:
        console.print("\n[bold cyan]Formatos de salida disponibles:[/bold cyan]")
        console.print("1. CSV")
        console.print("2. Excel (XLSX)")
        console.print("3. Ambos formatos")
        console.print("4. Atrás")
        
        opcion = console.input("[bold yellow]Seleccione el formato de salida (1-4): [/bold yellow]")
        
        if opcion == "4":
            return

        if opcion not in ["1", "2", "3"]:
            console.print("[bold red]Opción no válida. Por favor, intente de nuevo.[/bold red]")
            continue

        nombre_base = console.input("[bold yellow]Ingrese el nombre base para el archivo de salida (sin extensión): [/bold yellow]")
        
        archivo_csv = None
        archivo_excel = None
        
        try:
            if opcion in ["1", "3"]:
                archivo_csv = Path('generados') / f"{nombre_base}.csv"
                guardar_csv(datos, str(archivo_csv))
            if opcion in ["2", "3"]:
                archivo_excel = Path('generados') / f"{nombre_base}.xlsx"
                guardar_excel(datos, str(archivo_excel))
            
            # Preguntar si se desea enviar por correo
            enviar_informe = console.input("[bold yellow]¿Desea enviar el informe por correo electrónico? (s/n): [/bold yellow]").lower()
            if enviar_informe == 's':
                destinatario = console.input("[bold yellow]Ingrese la dirección de correo electrónico del destinatario: [/bold yellow]")
                
                # Determinar qué archivo enviar
                archivo_adjunto = archivo_excel if archivo_excel else archivo_csv
                
                if archivo_adjunto:
                    enviar_correo(destinatario, str(archivo_adjunto))
                else:
                    console.print("[bold red]No se generó ningún archivo para enviar.[/bold red]")
            
            break  # Salir del bucle después de guardar y posiblemente enviar
        
        except Exception as e:
            console.print(f"[bold red]Error al guardar los resultados:[/bold red]")
            console.print(f"[red]Tipo de error: {type(e).__name__}[/red]")
            console.print(f"[red]Descripción: {str(e)}[/red]")
            console.print("[red]Detalles del error:[/red]")
            import traceback
            console.print(traceback.format_exc())
            
            if console.input("[bold yellow]¿Desea intentar de nuevo? (s/n): [/bold yellow]").lower() != 's':
                break

def main():
    """
    Función principal que maneja el flujo del programa.
    """
    mostrar_entradilla()
    
    if not verificar_configuracion():
        console.print("[bold yellow]No se puede continuar debido a la falta de configuración en el archivo .env[/bold yellow]")
        return

    try:
        while True:
            opcion = menu_principal()
            
            if opcion == "1":
                verificar_correos_csv()
            elif opcion == "2":
                resultado = agregar_correo_manual()
                datos = procesar_resultados(resultado)
                mostrar_resultados(datos)
                guardar_resultados(datos)
            elif opcion == "3":
                listar_archivos_csv('deposito')
            elif opcion == "4":
                console.print("[bold green]¡Hasta luego![/bold green]")
                break
            else:
                console.print("[bold red]Opción no válida. Por favor, intente de nuevo.[/bold red]")
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Programa interrumpido por el usuario. ¡Hasta luego![/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error inesperado: {str(e)}[/bold red]")
    finally:
        console.print("[bold green]Gracias por usar el programa. ¡Hasta la próxima![/bold green]")

if __name__ == "__main__":
    main()