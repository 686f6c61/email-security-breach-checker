#!/usr/bin/env python3
"""
Email Security Breach Checker v2.0 - Punto de Entrada CLI

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Script de punto de entrada para la interfaz de línea de comandos 
del verificador de seguridad de emails.

Uso:
    python3 cli_entry.py [opciones]

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import sys
from pathlib import Path

# Añadir src al path para importaciones
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cli import main

if __name__ == "__main__":
    sys.exit(main())