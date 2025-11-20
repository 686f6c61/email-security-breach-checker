"""
Email Security Breach Checker v2.0 - Utilidades de Validación

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que proporciona funciones de validación para emails, 
archivos y otros inputs de la aplicación.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import re
import csv
from pathlib import Path
from typing import List, Optional

from .exceptions import ValidationError, FileOperationError


def validate_email(email: str) -> bool:
    """
    Validar formato de dirección de email.
    
    Args:
        email: Dirección de email a validar
        
    Returns:
        True si es válido, lanza ValidationError si es inválido
        
    Raises:
        ValidationError: Si el formato del email es inválido
    """
    if not email or not isinstance(email, str):
        raise ValidationError("El email no puede estar vacío o ser None")
    
    # Patrón regex básico para email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email.strip()):
        raise ValidationError(f"Formato de email inválido: {email}")
    
    return True


def validate_csv_file(file_path: Path) -> List[str]:
    """
    Validar y leer archivo CSV que contiene direcciones de email.
    
    Args:
        file_path: Ruta al archivo CSV
        
    Returns:
        Lista de direcciones de email
        
    Raises:
        FileOperationError: If file cannot be read or is invalid
        ValidationError: If email addresses in file are invalid
    """
    if not file_path.exists():
        raise FileOperationError(f"File does not exist: {file_path}")
    
    if not file_path.is_file():
        raise FileOperationError(f"Path is not a file: {file_path}")
    
    if file_path.suffix.lower() != '.csv':
        raise FileOperationError(f"File must be a CSV file: {file_path}")
    
    emails = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)

            # Common header names to skip
            header_keywords = ['email', 'correo', 'e-mail', 'mail', 'emails', 'correos', 'address', 'direccion']

            for row_num, row in enumerate(reader, 1):
                if not row:  # Skip empty rows
                    continue

                # Get first non-empty column
                email = None
                for cell in row:
                    if cell.strip():
                        email = cell.strip()
                        break

                if not email:
                    continue

                # Skip header row if it matches common header keywords
                if row_num == 1 and email.lower() in header_keywords:
                    continue

                # Try to validate email
                try:
                    validate_email(email)
                    emails.append(email)
                except ValidationError:
                    # If first row and validation fails, assume it's a header and skip
                    if row_num == 1:
                        continue
                    # For other rows, raise the error
                    raise
    
    except UnicodeDecodeError:
        raise FileOperationError(f"File encoding error. Please ensure file is UTF-8 encoded: {file_path}")
    except csv.Error as e:
        raise FileOperationError(f"CSV parsing error in {file_path}: {str(e)}")
    except Exception as e:
        raise FileOperationError(f"Error reading file {file_path}: {str(e)}")
    
    if not emails:
        raise ValidationError(f"No valid email addresses found in {file_path}")
    
    return emails


def validate_output_filename(filename: str) -> str:
    """
    Validate and sanitize output filename.
    
    Args:
        filename: Proposed filename
        
    Returns:
        Sanitized filename
        
    Raises:
        ValidationError: If filename is invalid
    """
    if not filename or not isinstance(filename, str):
        raise ValidationError("Filename cannot be empty or None")
    
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename.strip())
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    if not sanitized:
        raise ValidationError("Filename contains only invalid characters")
    
    return sanitized


def validate_directory_path(path: Path) -> bool:
    """
    Validate directory path exists and is writable.
    
    Args:
        path: Directory path to validate
        
    Returns:
        True if valid
        
    Raises:
        FileOperationError: If directory is invalid or not writable
    """
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileOperationError(f"Cannot create directory {path}: {str(e)}")
    
    if not path.is_dir():
        raise FileOperationError(f"Path is not a directory: {path}")
    
    # Test write permissions
    test_file = path / '.write_test'
    try:
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        raise FileOperationError(f"Directory is not writable: {path} - {str(e)}")
    
    return True