"""
Email Security Breach Checker v2.0 - Excepciones Personalizadas

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que define todas las excepciones personalizadas utilizadas 
en la aplicación para mejor manejo de errores y depuración.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""


class EmailSecurityException(Exception):
    """Excepción base para todos los errores relacionados con seguridad de emails."""
    pass


class ConfigurationError(EmailSecurityException):
    """Se lanza cuando hay un problema de configuración."""
    pass


class APIError(EmailSecurityException):
    """Se lanza cuando hay un error relacionado con la API."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimitError(APIError):
    """Se lanza cuando se excede el límite de rate de la API."""
    
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Se lanza cuando falla la autenticación de la API."""
    pass


class ValidationError(EmailSecurityException):
    """Se lanza cuando falla la validación de input."""
    pass


class FileOperationError(EmailSecurityException):
    """Se lanza cuando fallan las operaciones de archivo."""
    pass


class EmailServiceError(EmailSecurityException):
    """Se lanza cuando fallan las operaciones del servicio de email."""
    pass


class CacheError(EmailSecurityException):
    """Se lanza cuando fallan las operaciones de caché."""
    pass