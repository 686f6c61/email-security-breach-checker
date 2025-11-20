#!/usr/bin/env python3
"""
Email Security Breach Checker v2.0 - Aplicación Principal

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Aplicación Python moderna para verificar si las direcciones de correo 
electrónico han sido comprometidas en brechas de seguridad conocidas utilizando 
la API de Have I Been Pwned (HIBP).

Uso:
    python main.py

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Añadir src al path para importaciones
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import settings
from api.hibp import HIBPClient
from api.email_service import ResendEmailService
from utils.data_processor import BreachDataProcessor
from utils.export import DataExporter
from utils.validators import validate_email, validate_csv_file
from utils.exceptions import (
    EmailSecurityException,
    ConfigurationError,
    APIError,
    ValidationError,
    FileOperationError,
    EmailServiceError
)
from ui.display import display
from utils.logger import logger


class EmailSecurityApp:
    """Clase principal de la aplicación Email Security Breach Checker."""
    
    def __init__(self):
        """Inicializar aplicación."""
        self.hibp_client: Optional[HIBPClient] = None
        self.email_service: Optional[ResendEmailService] = None
        self.data_processor = BreachDataProcessor()
        self.data_exporter = DataExporter()
        self.enterprise_mode = False
    
    def initialize(self) -> bool:
        """
        Inicializar servicios de la aplicación.
        
        Returns:
            True si la inicialización fue exitosa, False en caso contrario
        """
        try:
            # Validar configuración
            if not settings.validate_configuration():
                display.show_configuration_status(False)
                return False
            
            display.show_configuration_status(True)
            
            # Inicializar clientes
            self.hibp_client = HIBPClient()
            self.email_service = ResendEmailService()
            
            logger.info("Aplicación inicializada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar la aplicación: {str(e)}")
            display.show_error(f"Error de inicialización: {str(e)}")
            return False
    
    def check_single_email(self, email: str) -> Dict[str, Any]:
        """
        Verificar un solo email en busca de brechas.
        
        Args:
            email: Dirección de correo electrónico a verificar
            
        Returns:
            Diccionario con resultados de brechas
        """
        try:
            validate_email(email)
            logger.info(f"Verificando email individual: {email}")
            
            if not self.hibp_client:
                raise ConfigurationError("Cliente HIBP no inicializado")
            
            breaches = self.hibp_client.check_email(email)
            return {email: breaches}
            
        except ValidationError as e:
            logger.error(f"Email inválido {email}: {str(e)}")
            display.show_error(f"Email inválido: {str(e)}")
            return {email: None}
        except Exception as e:
            logger.error(f"Error verificando {email}: {str(e)}")
            display.show_error(f"Error verificando {email}: {str(e)}")
            return {email: None}
    
    def check_emails_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Verificar emails desde un archivo CSV.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            Diccionario con resultados de brechas
        """
        try:
            emails = validate_csv_file(file_path)
            logger.info(f"Verificando {len(emails)} emails desde {file_path}")
            
            if not self.hibp_client:
                raise ConfigurationError("Cliente HIBP no inicializado")
            
            with display.show_progress("Verificando emails", len(emails)) as progress:
                task = progress.add_task("Procesando emails...", total=len(emails))
                
                results = {}
                for i, email in enumerate(emails):
                    try:
                        breaches = self.hibp_client.check_email(email)
                        results[email] = breaches
                        progress.update(task, advance=1, description=f"Verificando {email}...")
                    except Exception as e:
                        logger.error(f"Error verificando {email}: {str(e)}")
                        results[email] = None
                        progress.update(task, advance=1, description=f"Error verificando {email}")
            
            return results
            
        except (ValidationError, FileOperationError) as e:
            logger.error(f"Error de archivo: {str(e)}")
            display.show_error(f"Error de archivo: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            display.show_error(f"Error inesperado: {str(e)}")
            return {}
    
    def process_and_display_results(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Procesar resultados y mostrarlos al usuario.
        
        Args:
            results: Resultados brutos de brechas
            
        Returns:
            Datos procesados listos para exportar
        """
        if not results:
            display.show_warning("No hay resultados para procesar")
            return []
        
        # Procesar los datos
        processed_data = self.data_processor.process_breach_results(results)
        
        # Mostrar resultados
        display.show_results_table(processed_data)
        
        # Mostrar estadísticas resumidas
        stats = self.data_processor.get_summary_statistics(processed_data)
        display.show_summary_statistics(stats)
        
        return processed_data
    
    def export_results(self, data: List[Dict[str, str]]) -> Dict[str, Path]:
        """
        Exportar resultados a los formatos seleccionados.
        
        Args:
            data: Datos procesados para exportar
            
        Returns:
            Diccionario mapeando formatos a rutas de archivo
        """
        if not data:
            display.show_warning("No hay datos para exportar")
            return {}
        
        try:
            # Obtener preferencias de exportación
            filename = display.prompt_for_output_filename()
            formats = display.prompt_for_export_formats()
            
            # Exportar datos
            exported_files = self.data_exporter.export_all_formats(data, filename, formats)
            
            # Mostrar mensaje de éxito
            for format_name, file_path in exported_files.items():
                display.show_success(f"Exportado {format_name.upper()}: {file_path}")
            
            return exported_files
            
        except Exception as e:
            logger.error(f"Error de exportación: {str(e)}")
            display.show_error(f"Exportación fallida: {str(e)}")
            return {}
    
    def send_individual_emails(self, raw_results: Dict[str, Any], exported_files: Dict[str, Path], force_send_all: bool = True) -> bool:
        """
        Enviar emails individuales a cada usuario con solo sus brechas.

        Args:
            raw_results: Resultados brutos de brechas desde API HIBP (dict: email -> brechas)
            exported_files: Diccionario de archivos exportados
            force_send_all: Si es True, envía a todos sin importar si tienen brechas (default: True)

        Returns:
            True si todos los emails se enviaron exitosamente
        """
        import time

        if not self.email_service:
            display.show_error("Servicio de email no disponible")
            return False

        success_count = 0
        total_count = len(raw_results)

        display.show_info(f"Enviando emails individuales a {total_count} direcciones...")

        for index, (email, breaches) in enumerate(raw_results.items()):
            # Normalize breaches - convert None to empty list
            if breaches is None:
                breaches = []

            # Create individual data for this email
            individual_data = self.data_processor.process_breach_results({email: breaches})

            # Get breach count
            stats = self.data_processor.get_summary_statistics(individual_data)
            breach_count = stats.get('compromised_emails', 0)

            # Solo omitir si force_send_all es False y no hay brechas
            if not force_send_all and breach_count == 0 and settings.send_email_only_with_breaches:
                logger.info(f"Skipping {email} - no breaches and SEND_EMAIL_ONLY_WITH_BREACHES enabled")
                continue

            # Choose attachment file (prefer Excel, then CSV)
            attachment_path = None
            if 'excel' in exported_files:
                attachment_path = exported_files['excel']
            elif 'csv' in exported_files:
                attachment_path = exported_files['csv']

            if not attachment_path:
                logger.warning(f"No attachment available for {email}")
                continue

            try:
                with display.show_progress(f"Enviando email a {email}"):
                    result = self.email_service.send_breach_report(
                        recipient=email,
                        attachment_path=attachment_path,
                        breach_count=breach_count,
                        breach_details=breaches if breaches else [],
                        force_send=force_send_all
                    )

                if result.get("id") != "skipped":
                    display.show_success(f"✅ Email enviado a {email}")
                    logger.info(f"Email individual enviado a {email}")
                    success_count += 1
                else:
                    logger.info(f"Email omitido para {email}: {result.get('reason')}")

            except Exception as e:
                logger.error(f"Error enviando email a {email}: {str(e)}")
                display.show_error(f"❌ Error enviando email a {email}: {str(e)}")

            # Add delay between emails to respect Resend rate limit (2 req/sec)
            # Wait 600ms between emails to be safe (allows ~1.6 emails/sec)
            if index < total_count - 1:  # Don't wait after last email
                time.sleep(0.6)

        display.show_success(f"📧 Emails individuales enviados exitosamente: {success_count}/{total_count}")
        return success_count > 0

    def send_email_report(self, data: List[Dict[str, str]], exported_files: Dict[str, Path], recipient: Optional[str] = None, raw_results: Optional[Dict[str, Any]] = None) -> bool:
        """
        Enviar reporte por email al usuario.
        
        Args:
            data: Datos procesados de brechas
            exported_files: Diccionario de archivos exportados
            recipient: Email del destinatario opcional (para modo enterprise)
            raw_results: Resultados brutos de brechas desde API HIBP
            
        Returns:
            True si el email se envió exitosamente
        """
        if not self.email_service:
            display.show_error("Servicio de email no disponible")
            return False
        
        try:
            # Contar brechas para personalización
            stats = self.data_processor.get_summary_statistics(data)
            breach_count = stats['compromised_emails']
            
            # Verificar si debemos enviar email solo cuando hay brechas
            if breach_count == 0 and settings.send_email_only_with_breaches:
                logger.info("No se encontraron brechas y SEND_EMAIL_ONLY_WITH_BREACHES está activado. Omitiendo email.")
                return True  # Retornar True ya que este es el comportamiento esperado
            
            # Obtener destinatario (modo enterprise o preguntar)
            if not recipient:
                recipient = settings.enterprise_recipient_email
            
            if not recipient:
                if self.enterprise_mode:
                    display.show_error("No hay destinatario configurado para modo enterprise")
                    return False
                else:
                    # Preguntar si el usuario quiere enviar email
                    if not display.confirm_send_email(breach_count):
                        return False
                    
                    # Obtener destinatario
                    recipient = display.prompt_for_email_recipient()
            
            validate_email(recipient)
            
            # Elegir archivo para adjuntar (preferir Excel, luego CSV)
            attachment_path = None
            if 'excel' in exported_files:
                attachment_path = exported_files['excel']
            elif 'csv' in exported_files:
                attachment_path = exported_files['csv']
            
            if not attachment_path:
                display.show_warning("No hay archivos disponibles para adjuntar")
                return False
            
            # Extraer detalles de brechas desde resultados brutos
            breach_details = []
            if raw_results:
                for email, breaches in raw_results.items():
                    if breaches:
                        breach_details.extend(breaches)
            
            # Enviar email
            with display.show_progress("Enviando email"):
                result = self.email_service.send_breach_report(
                    recipient=recipient,
                    attachment_path=attachment_path,
                    breach_count=breach_count,
                    breach_details=breach_details
                )
            
            # Verificar si el email fue omitido
            if result.get("id") == "skipped":
                logger.info(f"Email omitido: {result.get('reason')}")
                return True
            
            display.show_success(f"Email enviado a {recipient}")
            logger.info(f"Reporte por email enviado a {recipient}")
            return True
            
        except ValidationError as e:
            display.show_error(f"Email de destinatario inválido: {str(e)}")
            return False
        except EmailServiceError as e:
            display.show_error(f"Error al enviar email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado enviando email: {str(e)}")
            display.show_error(f"Error al enviar email: {str(e)}")
            return False

    def run_interactive_mode(self) -> None:
        """Ejecutar aplicación en modo interactivo."""
        display.show_banner()
        
        if not self.initialize():
            return
        
        while True:
            try:
                choice = display.show_menu([
                    "Verificar emails desde archivo CSV",
                    "Verificar email individual",
                    "Listar archivos CSV disponibles",
                    "Probar configuración de email",
                    "Salir"
                ])
                
                if choice == "1":
                    self._handle_csv_mode()
                elif choice == "2":
                    self._handle_single_email_mode()
                elif choice == "3":
                    self._handle_list_files()
                elif choice == "4":
                    self._handle_test_email()
                elif choice == "5":
                    display.show_success("¡Hasta luego!")
                    break
                    
            except KeyboardInterrupt:
                display.show_info("\nOperación cancelada por el usuario")
                break
            except EOFError:
                logger.info("No hay entrada disponible. Saliendo del modo interactivo.")
                display.show_info("\nNo hay terminal interactiva disponible")
                break
            except Exception as e:
                logger.error(f"Error inesperado en modo interactivo: {str(e)}")
                display.show_error(f"Error inesperado: {str(e)}")
                break
    
    def _handle_csv_mode(self) -> None:
        """Manejar modo de verificación desde archivo CSV."""
        filename = display.prompt_for_file(settings.deposit_dir)

        if not filename or filename.lower() == 'back':
            return

        # Add .csv extension if not present
        if not filename.endswith('.csv'):
            filename = f"{filename}.csv"

        file_path = settings.deposit_dir / filename

        with display.show_progress("Leyendo y verificando emails"):
            results = self.check_emails_from_file(file_path)

        if results:
            processed_data = self.process_and_display_results(results)
            exported_files = self.export_results(processed_data)

            if exported_files:
                # Get breach count for confirmation
                stats = self.data_processor.get_summary_statistics(processed_data)
                breach_count = stats.get('compromised_emails', 0)

                # Ask if user wants to send email
                if display.confirm_send_email(breach_count):
                    # If multiple emails were checked, ask for send mode
                    email_count = len(results)

                    if email_count > 1:
                        send_mode = display.prompt_email_send_mode(email_count)

                        if send_mode == "admin":
                            # Send only to admin
                            recipient = display.prompt_for_email_recipient()
                            if recipient:
                                self.send_email_report(processed_data, exported_files, recipient, results)

                        elif send_mode == "individual":
                            # Send to each user individually
                            self.send_individual_emails(results, exported_files)

                        elif send_mode == "both":
                            import time
                            # Send to admin
                            recipient = display.prompt_for_email_recipient()
                            if recipient:
                                self.send_email_report(processed_data, exported_files, recipient, results)
                                # Wait 600ms before sending individual emails to respect rate limit
                                time.sleep(0.6)
                            # Also send to each individual
                            self.send_individual_emails(results, exported_files)
                    else:
                        # Single email - just send to recipient
                        recipient = display.prompt_for_email_recipient()
                        if recipient:
                            self.send_email_report(processed_data, exported_files, recipient, results)
    
    def _handle_single_email_mode(self) -> None:
        """Manejar modo de verificación de email individual."""
        email = display.prompt_for_email()

        if not email:
            return

        with display.show_progress("Verificando email"):
            results = self.check_single_email(email)

        if results:
            processed_data = self.process_and_display_results(results)
            exported_files = self.export_results(processed_data)

            if exported_files:
                # Get breach count for confirmation
                stats = self.data_processor.get_summary_statistics(processed_data)
                breach_count = stats.get('compromised_emails', 0)

                # Ask if user wants to send email
                if display.confirm_send_email(breach_count):
                    # Ask where to send the report
                    recipient = display.prompt_single_email_recipient(email)
                    if recipient:
                        self.send_email_report(processed_data, exported_files, recipient, results)
    
    def _handle_list_files(self) -> None:
        """Manejar modo de listado de archivos."""
        csv_files = [f.name for f in settings.deposit_dir.glob("*.csv")]
        display.show_file_list(csv_files, "Archivos CSV en Directorio de Depósito")
    
    def _handle_test_email(self) -> None:
        """Manejar modo de prueba de email."""
        if not self.email_service:
            display.show_error("Servicio de email no disponible")
            return
        
        try:
            recipient = display.prompt_for_email_recipient()
            validate_email(recipient)
            
            with display.show_progress("Enviando email de prueba"):
                result = self.email_service.send_test_email(recipient)
            
            display.show_success(f"Email de prueba enviado a {recipient}")
            
        except ValidationError as e:
            display.show_error(f"Email inválido: {str(e)}")
        except EmailServiceError as e:
            display.show_error(f"Email de prueba fallido: {str(e)}")

    def cleanup(self) -> None:
        """Limpiar recursos."""
        try:
            if self.hibp_client:
                self.hibp_client.close()
            if self.email_service:
                self.email_service.close()
        except Exception as e:
            logger.error(f"Error durante la limpieza: {str(e)}")


def main() -> None:
    """Punto de entrada principal de la aplicación."""
    app = EmailSecurityApp()
    
    try:
        app.run_interactive_mode()
    except KeyboardInterrupt:
        display.show_info("\nAplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        display.show_error(f"Error fatal: {str(e)}")
        sys.exit(1)
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()