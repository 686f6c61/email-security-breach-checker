"""
Email Security Breach Checker v2.0 - Configuración

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que maneja toda la gestión de configuración incluyendo 
variables de entorno, API keys y configuraciones de la aplicación.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()


class Settings:
    """Clase de configuración centralizada para la aplicación."""
    
    def __init__(self):
        """Inicializar configuración desde variables de entorno."""
        self._hibp_api_key: Optional[str] = os.getenv('HIBP_API_KEY')
        self._resend_api_key: Optional[str] = os.getenv('RESEND_API_KEY')
        self._sender_email: Optional[str] = os.getenv('SENDER_EMAIL')
        self._enterprise_recipient_email: Optional[str] = os.getenv('ENTERPRISE_RECIPIENT_EMAIL')
        
        # Configuración de idioma y email
        self._email_language = os.getenv('EMAIL_LANGUAGE', 'es').lower()  # 'es' o 'en'
        self._send_email_only_with_breaches = os.getenv('SEND_EMAIL_ONLY_WITH_BREACHES', 'true').lower() == 'true'
        
        # Configuración de la aplicación
        self.app_name = "Email Security Breach Checker"
        self.app_version = "2.0.0"
        self.github_repo = "https://github.com/686f6c61/email-security-breach-checker"
        
        # Configuración y límites de API HIBP
        self.hibp_base_url = "https://haveibeenpwned.com/api/v3"
        self.hibp_subscription_url = "https://haveibeenpwned.com/Subscription"
        self.hibp_api_docs_url = "https://haveibeenpwned.com/API/v3"
        
        # Límites de rate HIBP basados en tier de suscripción
        self.hibp_rate_limits = {
            'Pwned 1': {'rpm': 10, 'domain_limit': 25, 'price': 4.50},
            'Pwned 2': {'rpm': 50, 'domain_limit': 100, 'price': 22.00},
            'Pwned 3': {'rpm': 100, 'domain_limit': 500, 'price': 37.50},
            'Pwned 4': {'rpm': 500, 'domain_limit': float('inf'), 'price': 163.00},
            'Pwned 5': {'rpm': 1000, 'domain_limit': float('inf'), 'price': 326.00}
        }
        
        # Por defecto Pwned 1 (tier gratuito)
        self.hibp_tier = os.getenv('HIBP_TIER', 'Pwned 1')
        tier_config = self.hibp_rate_limits.get(self.hibp_tier, self.hibp_rate_limits['Pwned 1'])
        
        # Calculate delay based on RPM (requests per minute)
        self.hibp_rate_limit_rpm = tier_config['rpm']
        self.hibp_rate_limit_delay = 60.0 / self.hibp_rate_limit_rpm  # seconds between requests
        self.hibp_domain_limit = tier_config['domain_limit']
        
        # General settings
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '10'))  # seconds
        self.cache_ttl_hours = int(os.getenv('CACHE_TTL_HOURS', '24'))
        
        # Directory settings
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.deposit_dir = self.data_dir / "deposito"
        self.generated_dir = self.data_dir / "generados"
        
        # Docker/Container settings
        self.is_docker = os.getenv('DOCKER_ENV', 'false').lower() == 'true'
        self.batch_size = int(os.getenv('BATCH_SIZE', '50'))  # For enterprise processing
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.data_dir, self.deposit_dir, self.generated_dir]:
            directory.mkdir(exist_ok=True)
    
    @property
    def hibp_api_key(self) -> str:
        """Get HIBP API key from environment."""
        if not self._hibp_api_key:
            raise ValueError("HIBP_API_KEY environment variable is required")
        return self._hibp_api_key
    
    @property
    def resend_api_key(self) -> str:
        """Get Resend API key from environment."""
        if not self._resend_api_key:
            raise ValueError("RESEND_API_KEY environment variable is required")
        return self._resend_api_key
    
    @property
    def sender_email(self) -> str:
        """Get sender email from environment."""
        if not self._sender_email:
            raise ValueError("SENDER_EMAIL environment variable is required")
        return self._sender_email
    
    @property
    def enterprise_recipient_email(self) -> Optional[str]:
        """Get enterprise recipient email from environment."""
        return self._enterprise_recipient_email
    
    @property
    def email_language(self) -> str:
        """Get email language preference."""
        return self._email_language if self._email_language in ['es', 'en'] else 'es'
    
    @property
    def send_email_only_with_breaches(self) -> bool:
        """Get preference to send email only when breaches are found."""
        return self._send_email_only_with_breaches
    
    def validate_configuration(self) -> bool:
        """Validate that all required configuration is present."""
        try:
            _ = self.hibp_api_key
            _ = self.resend_api_key
            _ = self.sender_email
            return True
        except ValueError:
            return False
    
    def get_tier_info(self) -> dict:
        """Get current HIBP tier information."""
        return {
            'tier': self.hibp_tier,
            'rpm': self.hibp_rate_limit_rpm,
            'delay': self.hibp_rate_limit_delay,
            'domain_limit': self.hibp_domain_limit,
            'price': self.hibp_rate_limits[self.hibp_tier]['price']
        }
    
    def should_warn_about_rate_limit(self, email_count: int) -> tuple[bool, str]:
        """
        Check if user should be warned about rate limits.
        
        Args:
            email_count: Number of emails to process
            
        Returns:
            Tuple of (should_warn, warning_message)
        """
        tier_info = self.get_tier_info()
        
        # Warn if processing will take more than 5 minutes
        estimated_time_minutes = (email_count * self.hibp_rate_limit_delay) / 60
        
        if estimated_time_minutes > 5:
            return True, (
                f"⚠️  Processing {email_count} emails with {tier_info['tier']} tier "
                f"will take approximately {estimated_time_minutes:.1f} minutes.\n"
                f"Consider upgrading to a higher tier for faster processing:\n"
                f"{self.hibp_subscription_url}"
            )
        
        # Warn if approaching domain limit
        if email_count > tier_info['domain_limit'] * 0.8 and tier_info['domain_limit'] != float('inf'):
            return True, (
                f"⚠️  You're approaching the domain limit of {tier_info['domain_limit']} "
                f"emails for {tier_info['tier']} tier.\n"
                f"Consider upgrading for unlimited domain searches:\n"
                f"{self.hibp_subscription_url}"
            )
        
        return False, ""
    
    def get_optimal_batch_size(self) -> int:
        """Get optimal batch size for current tier."""
        if self.is_docker:
            # In Docker, we can process larger batches
            return min(self.batch_size, self.hibp_rate_limit_rpm)
        else:
            # Interactive mode - smaller batches for better UX
            return min(10, self.hibp_rate_limit_rpm // 2)


# Global settings instance
settings = Settings()