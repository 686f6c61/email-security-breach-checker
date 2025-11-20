# EMAIL SECURITY BREACH CHECKER V2.0

Una aplicación Python diseñada para monitorizar la seguridad de cuentas de correo empresariales y generar informes automáticos de brechas de seguridad utilizando la API de Have I Been Pwned (HIBP). Ideal para equipos de IT, administradores de sistemas y profesionales de ciberseguridad que necesitan mantener un control continuo sobre la exposición de credenciales corporativas.

## ÍNDICE

- [EMAIL SECURITY BREACH CHECKER V2.0](#email-security-breach-checker-v20)
  - [ÍNDICE](#índice)
  - [CARACTERISTICAS PRINCIPALES](#caracteristicas-principales)
  - [REQUISITOS](#requisitos)
  - [INSTALACION](#instalacion)
    - [Método Rápido (Recomendado)](#método-rápido-recomendado)
    - [Método Manual](#método-manual)
  - [CONFIGURACION](#configuracion)
    - [OBTENER API KEYS](#obtener-api-keys)
  - [USO](#uso)
    - [INICIO RAPIDO](#inicio-rapido)
    - [MODO INTERACTIVO](#modo-interactivo)
    - [CAPTURAS DE PANTALLA DEL PROCESO](#capturas-de-pantalla-del-proceso)
    - [MODO CLI](#modo-cli)
      - [EJEMPLOS DE USO](#ejemplos-de-uso)
      - [OPCIONES CLI](#opciones-cli)
      - [LIMITES DE RATE HIBP](#limites-de-rate-hibp)
  - [ESTRUCTURA DE ARCHIVOS](#estructura-de-archivos)
  - [FORMATOS DE EXPORTACION](#formatos-de-exportacion)
    - [CSV](#csv)
    - [Excel (XLSX)](#excel-xlsx)
    - [JSON](#json)
  - [CARACTERISTICAS TECNICAS](#caracteristicas-tecnicas)
    - [SISTEMA DE CACHE](#sistema-de-cache)
    - [ANALISIS DE RIESGOS](#analisis-de-riesgos)
    - [LOGGING ESTRUCTURADO](#logging-estructurado)
    - [MANEJO DE ERRORES](#manejo-de-errores)
  - [EMAILS DE REPORTES](#emails-de-reportes)
    - [CONFIGURACION DE EMAILS](#configuracion-de-emails)
    - [CONTENIDO DEL EMAIL](#contenido-del-email)
  - [DESARROLLO](#desarrollo)
    - [EJECUTAR TESTS](#ejecutar-tests)
    - [FORMATO DE CODIGO](#formato-de-codigo)
    - [ANALISIS ESTATICO](#analisis-estatico)
  - [SOLUCION DE PROBLEMAS](#solucion-de-problemas)
    - [API Keys Issues](#api-keys-issues)
    - [Rate Limit Issues](#rate-limit-issues)
    - [Email Issues](#email-issues)
    - [CSV File Issues](#csv-file-issues)
    - [Permisos](#permisos)
    - [Python Version](#python-version)
  - [CONTRIBUCIONES](#contribuciones)
  - [LICENCIA](#licencia)
  - [SEGURIDAD](#seguridad)
  - [SOPORTE](#soporte)
  - [AGRADECIMIENTOS](#agradecimientos)

## CARACTERISTICAS PRINCIPALES

- Verificación segura usando la API oficial de Have I Been Pwned
- Email moderno con Resend API
- Interfaz profesional con la librería Rich
- Múltiples formatos de exportación (CSV, Excel, JSON)
- Caché inteligente para evitar llamadas repetitivas a la API
- Seguridad mejorada - sin API keys en el código
- Logging estructurado para mejor depuración
- Validación robusta de emails y archivos
- Análisis de riesgos con estadísticas detalladas
- Soporte multi-idioma (español/inglés)
- Envío de emails solo cuando se encuentran brechas
- Script de inicio automático con configuración asistida

## REQUISITOS

- Python 3.8+
- API key de Have I Been Pwned
- API key de Resend (para envío de emails)

## INSTALACION

### Método Rápido (Recomendado)

Usa el script `cli_start.sh` que configura todo automáticamente:

```bash
git clone https://github.com/686f6c61/email-security-breach-checker.git
cd email-security-breach-checker
chmod +x cli_start.sh
./cli_start.sh
```

El script automáticamente:
- ✅ Verifica la versión de Python (3.8+)
- ✅ Crea el entorno virtual
- ✅ Instala todas las dependencias
- ✅ Crea el archivo .env desde .env.example
- ✅ Configura la estructura de directorios
- ✅ Crea un archivo CSV de ejemplo
- ✅ Inicia la aplicación en modo interactivo

![Inicio con cli_start.sh](assets/01%20cli_start.sh%20levantando%20entorno%20python.png)

Una vez iniciada la aplicación, verás el menú principal:

![Menú principal](assets/02%20configuración%20válidad%20-%20menu%20aplicación.png)

### Método Manual

Si prefieres instalar manualmente:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/686f6c61/email-security-breach-checker.git
   cd email-security-breach-checker
   ```

2. **Crear entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con tus API keys
   ```

5. **Crear estructura de directorios:**
   ```bash
   mkdir -p data/deposito data/generados cache logs
   ```

## CONFIGURACION

Edita el archivo `.env` con tus credenciales:

```env
# Have I Been Pwned API Key
# Obtén la tuya en: https://haveibeenpwned.com/API/Key
HIBP_API_KEY=your_hibp_api_key_here

# Resend API Key
# Obtén la tuya en: https://resend.com/api-keys
RESEND_API_KEY=your_resend_api_key_here

# Email remitente (debe estar verificado en Resend)
SENDER_EMAIL=your_email@yourdomain.com

# Email destinatario para modo enterprise
ENTERPRISE_RECIPIENT_EMAIL=admin@yourcompany.com

# Configuración de idioma (es/en)
EMAIL_LANGUAGE=es

# Enviar email solo cuando hay brechas (true/false)
SEND_EMAIL_ONLY_WITH_BREACHES=true

# Tier de suscripción HIBP (Pwned 1-5)
HIBP_TIER=Pwned 2
```

### OBTENER API KEYS

1. **Have I Been Pwned:**
   - Visita [https://haveibeenpwned.com/API/Key](https://haveibeenpwned.com/API/Key)
   - Regístra una cuenta gratuita
   - Genera tu API key

2. **Resend:**
   - Visita [https://resend.com/api-keys](https://resend.com/api-keys)
   - Crea una cuenta
   - Verifica tu dominio
   - Genera una API key

## USO

### INICIO RAPIDO

Para iniciar la aplicación con configuración automática:

```bash
./cli_start.sh
```

### MODO INTERACTIVO

Para iniciar manualmente el modo interactivo:

```bash
python3 main.py
```

El menú interactivo te permitirá:
1. Verificar emails desde archivo CSV
2. Verificar un email individual
3. Listar archivos CSV disponibles
4. Probar configuración de email
5. Salir

### CAPTURAS DE PANTALLA DEL PROCESO

**1. Verificación de emails desde CSV:**

![Verificar emails desde CSV](assets/03%20Verificar%20emails%20desde%20archivo%20csv.png)

**2. Proceso de análisis y consulta a HIBP:**

![Proceso de análisis](assets/04%20proceso%20de%20toma%20de%20datos.png)

**3. Tabla de resultados en consola:**

![Tabla de resultados](assets/05%20Tabla%20de%20resultados%20en%20consola.png)

**4. Estadísticas del análisis:**

![Estadísticas](assets/06%20stadisticas.png)

**5. Opciones de envío de email:**

![Opciones de envío](assets/07%20envio%20mails.png)

**6. Email recibido con reporte:**

![Email recibido](assets/08%20Mail%20envio.png)

**7. Reporte Excel adjunto - Métricas:**

![Excel - Métricas](assets/09%20Métricas%20escel.png)

**8. Reporte Excel - Nivel de riesgo:**

![Excel - Risk Level](assets/10%20Risk%20level%20excel.png)

**9. Reporte Excel - Detalles de brechas:**

![Excel - Breach Details](assets/11%20Breach%20name%20Excel.png)

### MODO CLI

Para uso automatizado y scripts, puedes usar la interfaz CLI:

```bash
python3 cli_entry.py [OPCIONES]
```

#### EJEMPLOS DE USO

**Verificar un email individual:**
```bash
python3 cli_entry.py --email user@example.com
```

**Verificar emails desde archivo CSV:**
```bash
python3 cli_entry.py --file emails.csv
```

**Modo Enterprise - procesamiento por lotes:**
```bash
python3 cli_entry.py --file company_emails.csv --enterprise --recipient admin@company.com
```

**Exportar a formatos específicos:**
```bash
python3 cli_entry.py --file emails.csv --export csv excel --output company_report
```

**Modo silencioso para automatización:**
```bash
python3 cli_entry.py --file emails.csv --batch-size 100 --quiet
```

#### OPCIONES CLI

| Opcion | Descripcion |
|--------|-------------|
| `--email, -e` | Email individual para verificar |
| `--file, -f` | Archivo CSV con emails a verificar |
| `--export` | Formatos de exportacion (csv, excel, json) |
| `--output, -o` | Nombre de archivo de salida (sin extension) |
| `--recipient, -r` | Email destinatario del reporte |
| `--no-email` | Omitir envio de email |
| `--enterprise` | Modo empresarial optimizado |
| `--batch-size` | Tamano de lote para procesamiento |
| `--tier` | Tier de suscripcion HIBP (Pwned 1-5) |
| `--verbose, -v` | Salida detallada |
| `--quiet, -q` | Modo silencioso |

#### LIMITES DE RATE HIBP

La aplicacion es consciente de los limites de la API HIBP:

| Tier | RPM | Limite Dominios | Precio |
|------|-----|-----------------|--------|
| Pwned 1 | 10 | 25/mes | $4.50 |
| Pwned 2 | 50 | 100/mes | $22.00 |
| Pwned 3 | 100 | 500/mes | $37.50 |
| Pwned 4 | 500 | Ilimitado | $163.00 |
| Pwned 5 | 1000 | Ilimitado | $326.00 |

Para actualizar tu tier: `python3 cli_entry.py --tier "Pwned 2"`

## ESTRUCTURA DE ARCHIVOS

```
email-security-breach-checker/
├── src/                         # Codigo fuente modular
│   ├── api/                     # Clientes de API
│   │   ├── hibp.py              # Cliente Have I Been Pwned
│   │   └── email_service.py     # Servicio de email Resend
│   ├── config/                  # Configuracion
│   │   └── settings.py          # Gestion de configuracion
│   ├── ui/                      # Interfaz de usuario
│   │   └── display.py           # Visualizacion con Rich
│   └── utils/                   # Utilidades
│       ├── cache.py             # Sistema de cache
│       ├── data_processor.py    # Procesamiento de datos
│       ├── exceptions.py        # Excepciones personalizadas
│       ├── export.py            # Exportacion de datos
│       ├── logger.py            # Sistema de logging
│       └── validators.py        # Validacion de inputs
├── data/                        # Datos de usuario
│   ├── deposito/                # Archivos CSV de entrada
│   └── generados/               # Reportes generados
├── cache/                       # Cache de API
├── logs/                        # Logs de aplicacion
├── tests/                       # Tests unitarios
├── main.py                      # Aplicacion principal
├── cli_entry.py                 # Entry point CLI
├── cli_start.sh                 # Script de inicio automatico
├── requirements.txt             # Dependencias
├── .env.example                 # Plantilla de configuracion
└── README.md                    # Este archivo
```

## FORMATOS DE EXPORTACION

La aplicacion puede exportar resultados en multiples formatos:

### CSV
- Formato simple y universal
- Compatible con Excel y otras herramientas

### Excel (XLSX)
- Multiples hojas con analisis detallado
- Incluye resumen estadistico
- Graficos de distribucion de riesgos

### JSON
- Estructura de datos completa
- Metadatos incluidos
- Ideal para integracion con otras aplicaciones

## CARACTERISTICAS TECNICAS

### SISTEMA DE CACHE
- Cache local de resultados por 24 horas
- Reduce llamadas a la API
- Acelera verificaciones repetitivas

### ANALISIS DE RIESGOS
- Clasificacion automatica: Bajo, Medio, Alto, Critico
- Basado en tipo de datos comprometidos
- Considera tamano y verificacion de la brecha

### LOGGING ESTRUCTURADO
- Niveles de log configurables
- Salida a consola con colores
- Archivos de log rotativos

### MANEJO DE ERRORES
- Excepciones personalizadas
- Recuperacion automatica de rate limits
- Mensajes claros para el usuario

## EMAILS DE REPORTES

### CONFIGURACION DE EMAILS

Los emails se envian con las siguientes caracteristicas:

- **Idioma:** Español (configurable con EMAIL_LANGUAGE=es/en)
- **Envio condicional:** Solo cuando se encuentran brechas (SEND_EMAIL_ONLY_WITH_BREACHES=true)
- **Sin emojis:** Texto profesional limpio
- **Informacion detallada:** Datos especificos de cada brecha desde API HIBP
- **Firma personalizada:** 686f6c61

### CONTENIDO DEL EMAIL

**Asunto:** `Reporte de brechas de seguridad encontradas`

**Cuando hay brechas:**
```
Hola,

He completado el análisis de seguridad de las direcciones de correo electrónico que solicitaste.

ALERTA: Se encontraron X brechas de seguridad que requieren tu atención inmediata.

Por favor revisa el reporte adjunto que contiene:
- Información detallada de cada brecha
- Qué datos fueron comprometidos
- Acciones recomendadas para proteger tus cuentas

Recomiendo encarecidamente:
1. Cambiar las contraseñas de las cuentas afectadas inmediatamente
2. Activar la autenticación de dos factores donde esté disponible
3. Monitorear actividades sospechosas

DETALLES DE LAS BRECHAS ENCONTRADAS:

1. Adobe
   - Dominio: adobe.com
   - Fecha: 2019-10-03
   - Cuentas afectadas: 152,445,632
   - Datos comprometidos: Email addresses, Passwords, Usernames

2. LinkedIn
   - Dominio: linkedin.com
   - Fecha: 2021-06-22
   - Cuentas afectadas: 700,000,000
   - Datos comprometidos: Email addresses, Names, Phone numbers

... (todas las brechas encontradas se muestran completas)

Si tienes alguna pregunta o necesitas ayuda para proteger tus cuentas, no dudes en contactarme.

Saludos cordiales,
686f6c61
Email Security Checker
```

**Cuando no hay brechas:** No se envia email (configuracion SEND_EMAIL_ONLY_WITH_BREACHES=true)

## DESARROLLO

### EJECUTAR TESTS
```bash
pytest tests/
```

### FORMATO DE CODIGO
```bash
black src/
```

### ANALISIS ESTATICO
```bash
flake8 src/
mypy src/
```

## SOLUCION DE PROBLEMAS

### API Keys Issues

**Problema:** Configuration invalid
**Solución:**
```bash
# Verificar configuración
cat .env | grep -E "(API_KEY|EMAIL)"

# Test API keys
python3 -c "
from src.config.settings import settings
print('HIBP:', '✓' if settings.hibp_api_key != 'your_hibp_api_key_here' else '✗')
print('RESEND:', '✓' if settings.resend_api_key != 'your_resend_api_key_here' else '✗')
"
```

### Rate Limit Issues

**Problema:** Rate limit exceeded
**Solución:**
- Actualizar HIBP tier en .env (`HIBP_TIER=Pwned 4`)
- Reducir `BATCH_SIZE` en comando CLI
- Verificar que el cache está funcionando
- La aplicación reintenta automáticamente hasta 3 veces

### Email Issues

**Problema:** Emails no se envían
**Solución:**
```bash
# Test email configuration
python3 cli_entry.py --email test@example.com --verbose

# Verificar dominio verificado en Resend
# Login: https://resend.com/domains
```

**Problema:** Rate limit de Resend (2 req/sec)
**Solución:** La aplicación maneja esto automáticamente con delays de 600ms entre emails

### CSV File Issues

**Problema:** Invalid email format en header
**Solución:** La aplicación detecta automáticamente headers en múltiples idiomas (email, correo, e-mail, mail)

```bash
# Validar formato CSV
head -5 data/deposito/emails_ejemplo.csv

# Contar emails válidos
grep -E "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" data/deposito/emails_ejemplo.csv | wc -l

# Crear archivo de prueba
echo -e "email\ntest@example.com\nuser@domain.com" > data/test.csv
```

### Permisos

**Problema:** Permission denied en cli_start.sh
**Solución:**
```bash
chmod +x cli_start.sh
./cli_start.sh
```

### Python Version

**Problema:** Python version incompatible
**Solución:**
```bash
python3 --version  # Debe ser 3.8+
# Si no: sudo apt install python3.8 python3.8-venv python3-pip
```

## CONTRIBUCIONES

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## LICENCIA

Este proyecto está licenciado bajo la MIT License - ver el archivo [LICENSE](LICENSE) para detalles.

## SEGURIDAD

- **Sin API keys en el código** - Todas las credenciales usan variables de entorno
- **Validacion de inputs** - Proteccion contra inyeccion y datos maliciosos
- **HTTPS obligatorio** - Todas las comunicaciones usan TLS
- **Rate limiting** - Respeta los limites de la API con reintentos automáticos
- **Logging seguro** - Nunca se loguean credenciales

## SOPORTE

Si encuentras algun problema o tienes sugerencias:

1. **Revisa los [issues existentes](https://github.com/686f6c61/email-security-breach-checker/issues)**
2. **Crea un nuevo issue** con detalles del problema y logs
3. **Contacta al maintainer del proyecto**

## AGRADECIMIENTOS

- [Have I Been Pwned](https://haveibeenpwned.com/) por la API de brechas
- [Resend](https://resend.com/) por el servicio de email moderno
- [Rich](https://rich.readthedocs.io/) por la interfaz de consola
