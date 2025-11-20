"""
Email Security Breach Checker v2.0 - Tests de Validación

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Tests unitarios para las utilidades de validación de la aplicación.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import pytest
from pathlib import Path
import tempfile
import csv

from src.utils.validators import validate_email, validate_csv_file, validate_output_filename
from src.utils.exceptions import ValidationError, FileOperationError


class TestEmailValidator:
    """Tests de funcionalidad de validación de emails."""
    
    def test_valid_emails(self):
        """Probar direcciones de email válidas."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_invalid_emails(self):
        """Probar direcciones de email inválidas."""
        invalid_emails = [
            "",
            "invalid-email",
            "@example.com",
            "test@",
            "test.example.com",
            "test@.com",
            "test@example.",
            None
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                validate_email(email)
    
    def test_email_case_insensitive(self):
        """Probar que la validación de email es insensible a mayúsculas/minúsculas."""
        assert validate_email("Test@EXAMPLE.COM") is True
        assert validate_email("user@DOMAIN.COM") is True


class TestCSVValidator:
    """Tests de funcionalidad de validación de archivos CSV."""
    
    def test_valid_csv_file(self):
        """Probar lectura de archivo CSV válido."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['test@example.com'])
            writer.writerow(['user@domain.com'])
            writer.writerow(['admin@test.org'])
            temp_path = Path(f.name)
        
        try:
            emails = validate_csv_file(temp_path)
            assert len(emails) == 3
            assert 'test@example.com' in emails
            assert 'user@domain.com' in emails
            assert 'admin@test.org' in emails
        finally:
            temp_path.unlink()
    
    def test_csv_with_empty_rows(self):
        """Probar archivo CSV con filas vacías."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['test@example.com'])
            writer.writerow([])  # Fila vacía
            writer.writerow([''])
            writer.writerow(['user@domain.com'])
            temp_path = Path(f.name)
        
        try:
            emails = validate_csv_file(temp_path)
            assert len(emails) == 2
            assert 'test@example.com' in emails
            assert 'user@domain.com' in emails
        finally:
            temp_path.unlink()
    
    def test_csv_with_multiple_columns(self):
        """Probar archivo CSV con múltiples columnas (debe usar la primera no vacía)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['test@example.com', 'extra', 'data'])
            writer.writerow(['', 'user@domain.com', 'more'])
            temp_path = Path(f.name)
        
        try:
            emails = validate_csv_file(temp_path)
            assert len(emails) == 2
            assert 'test@example.com' in emails
            assert 'user@domain.com' in emails
        finally:
            temp_path.unlink()
    
    def test_nonexistent_file(self):
        """Probar manejo de archivo no existente."""
        with pytest.raises(FileOperationError):
            validate_csv_file(Path("/nonexistent/file.csv"))
    
    def test_non_csv_file(self):
        """Probar manejo de archivo no CSV."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"not a csv file")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(FileOperationError):
                validate_csv_file(temp_path)
        finally:
            temp_path.unlink()
    
    def test_csv_with_invalid_emails(self):
        """Probar archivo CSV con emails inválidos."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['test@example.com'])
            writer.writerow(['invalid-email'])
            writer.writerow(['user@domain.com'])
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValidationError):
                validate_csv_file(temp_path)
        finally:
            temp_path.unlink()


class TestOutputFilenameValidator:
    """Tests de funcionalidad de validación de nombre de archivo de salida."""
    
    def test_valid_filenames(self):
        """Probar nombres de archivo válidos."""
        valid_filenames = [
            "report",
            "security_report_2023",
            "breach-analysis",
            "file_with_123_numbers"
        ]
        
        for filename in valid_filenames:
            result = validate_output_filename(filename)
            assert result == filename
    
    def test_invalid_characters(self):
        """Probar nombres de archivo con caracteres inválidos."""
        invalid_filenames = [
            "file<name",
            "file>name",
            "file:name",
            "file\"name",
            "file/name",
            "file\\name",
            "file|name",
            "file?name",
            "file*name"
        ]
        
        for filename in invalid_filenames:
            result = validate_output_filename(filename)
            assert "_" not in result or result != filename
    
    def test_empty_and_whitespace_filenames(self):
        """Probar nombres de archivo vacíos y solo con espacios en blanco."""
        invalid_filenames = [
            "",
            "   ",
            "\t\n",
            None
        ]
        
        for filename in invalid_filenames:
            with pytest.raises(ValidationError):
                validate_output_filename(filename)
    
    def test_filename_sanitization(self):
        """Probar que los caracteres inválidos son sanitizados apropiadamente."""
        test_cases = [
            ("file<name>", "file_name_"),
            ("file>name", "file_name_"),
            ("file:name", "file_name_"),
            ("file/name", "file_name_"),
            ("file\\name", "file_name_"),
            ("file|name", "file_name_"),
            ("file?name", "file_name_"),
            ("file*name", "file_name_")
        ]
        
        for input_name, expected_pattern in test_cases:
            result = validate_output_filename(input_name)
            assert "<" not in result
            assert ">" not in result
            assert ":" not in result
            assert "/" not in result
            assert "\\" not in result
            assert "|" not in result
            assert "?" not in result
            assert "*" not in result
    
    def test_leading_trailing_dots_and_spaces(self):
        """Probar eliminación de puntos y espacios iniciales/finales."""
        test_cases = [
            ("  filename  ", "filename"),
            ("..filename..", "filename"),
            ("  .filename.  ", "filename"),
            ("...filename...", "filename")
        ]
        
        for input_name, expected in test_cases:
            result = validate_output_filename(input_name)
            assert result == expected