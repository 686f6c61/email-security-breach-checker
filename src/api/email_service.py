"""
Email Security Breach Checker v2.0 - Servicio de Email

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que proporciona funcionalidad de email usando la API 
Resend en lugar de SMTP tradicional para mayor confiabilidad y características modernas.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

from typing import Optional, Dict, Any
from pathlib import Path
import base64

import httpx

from config.settings import settings
from utils.exceptions import EmailServiceError
from utils.logger import logger


class ResendEmailService:
    """Servicio de email usando API Resend."""
    
    def __init__(self):
        """Inicializar servicio de email Resend."""
        self.api_key = settings.resend_api_key
        self.sender_email = settings.sender_email
        self.base_url = "https://api.resend.com/emails"
        
        # HTTP client for Resend API
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    def send_breach_report(
        self,
        recipient: str,
        attachment_path: Path,
        breach_count: int = 0,
        custom_message: Optional[str] = None,
        breach_details: Optional[list] = None,
        force_send: bool = False
    ) -> Dict[str, Any]:
        """
        Send breach report email with attachment.
        
        Args:
            recipient: Recipient email address
            attachment_path: Path to the report file to attach
            breach_count: Number of breaches found (for personalization)
            custom_message: Optional custom message to include
            
        Returns:
            Response from Resend API
            
        Raises:
            EmailServiceError: If email sending fails
        """
        logger.info(f"Sending breach report to {recipient}")
        
        # Get language preference
        is_spanish = settings.email_language == 'es'
        
        # Prepare email content based on language
        if is_spanish:
            subject = "Reporte de brechas de seguridad encontradas"

            if breach_count > 0:
                body = self._get_spanish_breach_body(breach_count, breach_details, custom_message)
            else:
                # Don't send email if no breaches and setting is enabled (unless force_send is True)
                if settings.send_email_only_with_breaches and not force_send:
                    logger.info(f"No breaches found and SEND_EMAIL_ONLY_WITH_BREACHES is enabled. Skipping email.")
                    return {"id": "skipped", "reason": "no_breaches"}
                else:
                    body = self._get_spanish_no_breaches_body(custom_message)
                    subject = "Reporte de seguridad - Sin brechas encontradas"
        else:
            subject = "Security breach report found"

            if breach_count > 0:
                body = self._get_english_breach_body(breach_count, breach_details, custom_message)
            else:
                # Don't send email if no breaches and setting is enabled (unless force_send is True)
                if settings.send_email_only_with_breaches and not force_send:
                    logger.info(f"No breaches found and SEND_EMAIL_ONLY_WITH_BREACHES is enabled. Skipping email.")
                    return {"id": "skipped", "reason": "no_breaches"}
                else:
                    body = self._get_english_no_breaches_body(custom_message)
                    subject = "Security report - No breaches found"
        
        try:
            # Prepare email data with attachment
            email_data = {
                "from": f"Email Security Checker <{self.sender_email}>",
                "to": [recipient],
                "subject": subject,
                "html": self._format_html_body(body, attachment_path, breach_count)
            }

            # Add attachment if file exists
            if attachment_path and attachment_path.exists():
                try:
                    with open(attachment_path, 'rb') as f:
                        file_content = f.read()
                        file_base64 = base64.b64encode(file_content).decode('utf-8')

                    email_data["attachments"] = [
                        {
                            "filename": attachment_path.name,
                            "content": file_base64
                        }
                    ]
                    logger.debug(f"Attached file: {attachment_path.name} ({len(file_content)} bytes)")
                except Exception as e:
                    logger.warning(f"Failed to attach file {attachment_path}: {str(e)}")

            logger.debug(f"Sending email via Resend API to {recipient}")
            response = self.client.post(self.base_url, json=email_data)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Email sent successfully to {recipient}. Message ID: {result.get('id')}")
                return result
            else:
                error_msg = f"Failed to send email: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise EmailServiceError(error_msg)
                
        except httpx.RequestError as e:
            error_msg = f"Network error sending email: {str(e)}"
            logger.error(error_msg)
            raise EmailServiceError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logger.error(error_msg)
            raise EmailServiceError(error_msg)
    
    def _format_html_body(self, text_body: str, attachment_path: Path, breach_count: int) -> str:
        """
        Convert text body to HTML format.

        Args:
            text_body: Plain text email body
            attachment_path: Path to attached file
            breach_count: Number of breaches found

        Returns:
            HTML formatted email body
        """
        # Convert line breaks to <br> and format as HTML
        html_body = text_body.replace('\n', '<br>\n')
        
        # Add styling
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Email Security Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .alert {{
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 10px;
            margin: 10px 0;
        }}
        .success {{
            background-color: #e8f5e8;
            border-left: 4px solid #4caf50;
            padding: 10px;
            margin: 10px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    {html_body}
    
    <div class="footer">
        <p>This email was sent by <strong>Email Security Breach Checker</strong> v{settings.app_version}</p>
        <p><a href="https://github.com/686f6c61/email-security-breach-checker" style="color: #4a90e2; text-decoration: none;">GitHub Repository</a></p>
        <p style="margin-top: 10px; color: #999;">If you didn't request this security check, please ignore this email.</p>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _get_spanish_breach_body(self, breach_count: int, breach_details: Optional[list], custom_message: Optional[str]) -> str:
        """Get Spanish email body for breaches found."""
        body = f"""Hola,

He completado el análisis de seguridad de las direcciones de correo electrónico que solicitaste.

ALERTA: Se encontraron {breach_count} brechas de seguridad que requieren tu atención inmediata.

Por favor revisa el reporte adjunto que contiene:
- Información detallada de cada brecha
- Qué datos fueron comprometidos
- Acciones recomendadas para proteger tus cuentas

Recomiendo encarecidamente:
1. Cambiar las contraseñas de las cuentas afectadas inmediatamente
2. Activar la autenticación de dos factores donde esté disponible
3. Monitorear actividades sospechosas

{self._format_breach_details_spanish(breach_details) if breach_details else ''}

{custom_message or ''}

Si tienes alguna pregunta o necesitas ayuda para proteger tus cuentas, no dudes en contactarme.

Saludos cordiales,
686f6c61
Email Security Checker"""
        return body
    
    def _get_english_breach_body(self, breach_count: int, breach_details: Optional[list], custom_message: Optional[str]) -> str:
        """Get English email body for breaches found."""
        body = f"""Hello,

I've completed security breach analysis for email addresses you requested.

ALERT: Found {breach_count} security breaches that require your immediate attention.

Please review the attached report file which contains:
- Detailed information about each breach
- What data was compromised
- Recommended actions to secure your accounts

I strongly recommend you:
1. Change passwords for affected accounts immediately
2. Enable two-factor authentication where available
3. Monitor for suspicious activity

{self._format_breach_details_english(breach_details) if breach_details else ''}

{custom_message or ''}

If you have any questions or need help securing your accounts, please don't hesitate to reach out.

Best regards,
686f6c61
Email Security Checker"""
        return body
    
    def _get_spanish_no_breaches_body(self, custom_message: Optional[str]) -> str:
        """Get Spanish email body when no breaches found."""
        return f"""Hola,

Buenas noticias. He completado el análisis de seguridad y no se encontraron brechas conocidas para las direcciones de correo electrónico que solicitaste.

TODOS SEGUROS: Tus direcciones de correo parecen estar seguras según las bases de datos de brechas actuales.

Aún recomiendo:
- Usar contraseñas fuertes y únicas
- Activar la autenticación de dos factores
- Realizar chequeos de seguridad regularmente

{custom_message or ''}

Saludos cordiales,
686f6c61
Email Security Checker"""
    
    def _get_english_no_breaches_body(self, custom_message: Optional[str]) -> str:
        """Get English email body when no breaches found."""
        return f"""Hello,

Good news! I've completed security breach analysis and found no known breaches for email addresses you requested.

ALL CLEAR: Your email addresses appear to be secure based on current breach databases.

I still recommend:
- Using strong, unique passwords
- Enabling two-factor authentication
- Regular security checkups

{custom_message or ''}

Best regards,
686f6c61
Email Security Checker"""
    
    def _format_breach_details_spanish(self, breach_details: Optional[list]) -> str:
        """Format breach details in Spanish."""
        if not breach_details:
            return ""

        # Get unique breaches (avoid duplicates from multiple emails)
        unique_breaches = {}
        for breach in breach_details:
            name = breach.get('Name', 'Desconocido')
            if name not in unique_breaches:
                unique_breaches[name] = breach

        breach_list = list(unique_breaches.values())

        details = "\n\nDETALLES DE LAS BRECHAS ENCONTRADAS:\n"
        for i, breach in enumerate(breach_list, 1):  # Show ALL breaches
            name = breach.get('Name', 'Desconocido')
            domain = breach.get('Domain', 'N/A')
            breach_date = breach.get('BreachDate', 'Desconocida')
            pwn_count = breach.get('PwnCount', 0)
            data_classes = breach.get('DataClasses', [])

            details += f"\n{i}. {name}"
            details += f"\n   - Dominio: {domain}"
            details += f"\n   - Fecha: {breach_date}"
            details += f"\n   - Cuentas afectadas: {pwn_count:,}"
            details += f"\n   - Datos comprometidos: {', '.join(data_classes)}"
            details += "\n"

        return details
    
    def _format_breach_details_english(self, breach_details: Optional[list]) -> str:
        """Format breach details in English."""
        if not breach_details:
            return ""

        # Get unique breaches (avoid duplicates from multiple emails)
        unique_breaches = {}
        for breach in breach_details:
            name = breach.get('Name', 'Unknown')
            if name not in unique_breaches:
                unique_breaches[name] = breach

        breach_list = list(unique_breaches.values())

        details = "\n\nBREACH DETAILS FOUND:\n"
        for i, breach in enumerate(breach_list, 1):  # Show ALL breaches
            name = breach.get('Name', 'Unknown')
            domain = breach.get('Domain', 'N/A')
            breach_date = breach.get('BreachDate', 'Unknown')
            pwn_count = breach.get('PwnCount', 0)
            data_classes = breach.get('DataClasses', [])

            details += f"\n{i}. {name}"
            details += f"\n   - Domain: {domain}"
            details += f"\n   - Date: {breach_date}"
            details += f"\n   - Accounts affected: {pwn_count:,}"
            details += f"\n   - Data compromised: {', '.join(data_classes)}"
            details += "\n"

        return details
    
    def send_test_email(self, recipient: str) -> Dict[str, Any]:
        """
        Send a test email to verify configuration.
        
        Args:
            recipient: Recipient email address
            
        Returns:
            Response from Resend API
        """
        logger.info(f"Sending test email to {recipient}")
        
        email_data = {
            "from": f"Email Security Checker <{self.sender_email}>",
            "to": [recipient],
            "subject": "Test Email - Email Security Checker",
            "html": f"""
<!DOCTYPE html>
<html>
<body>
    <h2>Test Email Successful</h2>
    <p>This is a test email from Email Security Breach Checker v{settings.app_version}.</p>
    <p>Your email service configuration is working correctly.</p>
    <br>
    <p>Best regards,<br>686f6c61<br>Email Security Checker</p>
</body>
</html>
            """
        }
        
        try:
            response = self.client.post(self.base_url, json=email_data)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Test email sent successfully to {recipient}")
                return result
            else:
                error_msg = f"Failed to send test email: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise EmailServiceError(error_msg)
                
        except Exception as e:
            error_msg = f"Error sending test email: {str(e)}"
            logger.error(error_msg)
            raise EmailServiceError(error_msg)
    
    def close(self) -> None:
        """Close the HTTP client."""
        if hasattr(self.client, 'close'):
            self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()