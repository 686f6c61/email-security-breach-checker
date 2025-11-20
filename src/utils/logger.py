"""
Email Security Breach Checker v2.0 - Sistema de Logging

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que proporciona configuración centralizada de logging 
para la aplicación con soporte de colores y archivos rotativos.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from config.settings import settings


class ColoredFormatter(logging.Formatter):
    """Formateador personalizado con colores para diferentes niveles de log."""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        """Formatear registro de log con colores."""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Añadir color al nombre del nivel
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


def setup_logger(
    name: str = "email_security_checker",
    level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Configurar logger con salida a consola y opcionalmente a archivo.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta opcional del archivo de log
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create default logger
log_file = settings.base_dir / "logs" / "app.log"
log_file.parent.mkdir(exist_ok=True)
logger = setup_logger(log_file=log_file)