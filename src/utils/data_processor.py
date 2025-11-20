"""
Email Security Breach Checker v2.0 - Procesamiento de Datos

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que maneja el procesamiento de datos de brechas, 
formateo de resultados y preparación de datos para exportación.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from .logger import logger


class BreachDataProcessor:
    """Procesa datos de brechas para visualización y exportación."""
    
    @staticmethod
    def process_breach_results(
        results: Dict[str, Optional[List[Dict[str, Any]]]]
    ) -> List[Dict[str, str]]:
        """
        Process raw breach results into a format suitable for display and export.
        
        Args:
            results: Dictionary mapping emails to their breach data or None
            
        Returns:
            List of processed breach records
        """
        logger.info(f"Processing breach results for {len(results)} emails")
        
        processed_data = []
        
        for email, breaches in results.items():
            if breaches is None:
                # Error occurred during checking
                processed_data.append({
                    'Correo': email,
                    'Nombre de la brecha': 'Error al verificar',
                    'Título': '-',
                    'Dominio': '-',
                    'Fecha de la brecha': '-',
                    'Cuentas afectadas': '-',
                    'Datos comprometidos': '-',
                    'Es verificado': '-',
                    'Es sensible': '-',
                    'Riesgo': 'Error'
                })
            elif not breaches:
                # No breaches found
                processed_data.append({
                    'Correo': email,
                    'Nombre de la brecha': 'No comprometido',
                    'Título': '-',
                    'Dominio': '-',
                    'Fecha de la brecha': '-',
                    'Cuentas afectadas': '-',
                    'Datos comprometidos': '-',
                    'Es verificado': '-',
                    'Es sensible': '-',
                    'Riesgo': 'Bajo'
                })
            else:
                # Process each breach
                for breach in breaches:
                    risk_level = BreachDataProcessor._assess_risk_level(breach)
                    
                    processed_data.append({
                        'Correo': email,
                        'Nombre de la brecha': breach.get('Name', 'Desconocido'),
                        'Título': breach.get('Title', 'Desconocido'),
                        'Dominio': breach.get('Domain', 'Desconocido'),
                        'Fecha de la brecha': breach.get('BreachDate', 'Desconocida'),
                        'Cuentas afectadas': BreachDataProcessor._format_number(breach.get('PwnCount', 0)),
                        'Datos comprometidos': ', '.join(breach.get('DataClasses', ['Desconocido'])),
                        'Es verificado': 'Sí' if breach.get('IsVerified', False) else 'No',
                        'Es sensible': 'Sí' if breach.get('IsSensitive', False) else 'No',
                        'Riesgo': risk_level
                    })
        
        logger.info(f"Processed {len(processed_data)} breach records")
        return processed_data
    
    @staticmethod
    def _assess_risk_level(breach: Dict[str, Any]) -> str:
        """
        Assess risk level based on breach characteristics.
        
        Args:
            breach: Breach data dictionary
            
        Returns:
            Risk level string (Crítico, Alto, Medio, Bajo)
        """
        risk_score = 0
        
        # Check for sensitive data types
        data_classes = breach.get('DataClasses', [])
        sensitive_data = [
            'Email addresses', 'Passwords', 'Phone numbers', 'Physical addresses',
            'Social security numbers', 'Credit card numbers', 'Bank account numbers',
            'Personal health information', 'Government-issued IDs'
        ]
        
        sensitive_matches = sum(1 for data_type in data_classes if data_type in sensitive_data)
        risk_score += sensitive_matches * 2
        
        # Check breach size
        pwn_count = breach.get('PwnCount', 0)
        if pwn_count > 100000000:  # 100M+
            risk_score += 3
        elif pwn_count > 10000000:  # 10M+
            risk_score += 2
        elif pwn_count > 1000000:  # 1M+
            risk_score += 1
        
        # Check if verified
        if breach.get('IsVerified', False):
            risk_score += 1
        
        # Check if sensitive breach
        if breach.get('IsSensitive', False):
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 8:
            return 'Crítico'
        elif risk_score >= 5:
            return 'Alto'
        elif risk_score >= 3:
            return 'Medio'
        else:
            return 'Bajo'
    
    @staticmethod
    def _format_number(number: int) -> str:
        """
        Format large numbers for display.
        
        Args:
            number: Number to format
            
        Returns:
            Formatted number string
        """
        if number >= 1000000000:
            return f"{number/1000000000:.1f}B"
        elif number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return str(number)
    
    @staticmethod
    def get_summary_statistics(processed_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate summary statistics from processed data.
        
        Args:
            processed_data: List of processed breach records
            
        Returns:
            Dictionary with summary statistics
        """
        total_emails = len(set(record['Correo'] for record in processed_data))
        total_records = len(processed_data)
        
        # Count by risk level
        risk_counts = {}
        breach_counts = {}
        
        compromised_emails = set()
        error_emails = set()
        
        for record in processed_data:
            risk = record['Riesgo']
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
            
            if record['Nombre de la brecha'] not in ['No comprometido', 'Error al verificar']:
                breach_counts[record['Nombre de la brecha']] = breach_counts.get(record['Nombre de la brecha'], 0) + 1
                compromised_emails.add(record['Correo'])
            elif record['Nombre de la brecha'] == 'Error al verificar':
                error_emails.add(record['Correo'])
        
        return {
            'total_emails_checked': total_emails,
            'compromised_emails': len(compromised_emails),
            'safe_emails': total_emails - len(compromised_emails) - len(error_emails),
            'error_emails': len(error_emails),
            'total_breach_records': total_records,
            'risk_distribution': risk_counts,
            'top_breaches': dict(sorted(breach_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'compromise_rate': (len(compromised_emails) / total_emails * 100) if total_emails > 0 else 0
        }
    
    @staticmethod
    def filter_by_risk_level(
        processed_data: List[Dict[str, str]], 
        min_risk_level: str = 'Bajo'
    ) -> List[Dict[str, str]]:
        """
        Filter data by minimum risk level.
        
        Args:
            processed_data: List of processed breach records
            min_risk_level: Minimum risk level to include
            
        Returns:
            Filtered list of records
        """
        risk_hierarchy = {'Bajo': 1, 'Medio': 2, 'Alto': 3, 'Crítico': 4}
        min_level = risk_hierarchy.get(min_risk_level, 1)
        
        filtered_data = []
        for record in processed_data:
            record_risk = record.get('Riesgo', 'Bajo')
            if risk_hierarchy.get(record_risk, 0) >= min_level:
                filtered_data.append(record)
        
        return filtered_data
    
    @staticmethod
    def get_unique_breaches(processed_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Get unique breach information from processed data.
        
        Args:
            processed_data: List of processed breach records
            
        Returns:
            List of unique breach records
        """
        seen_breaches = set()
        unique_breaches = []
        
        for record in processed_data:
            breach_name = record.get('Nombre de la brecha')
            if breach_name and breach_name not in ['No comprometido', 'Error al verificar']:
                breach_key = (breach_name, record.get('Dominio'), record.get('Fecha de la brecha'))
                if breach_key not in seen_breaches:
                    seen_breaches.add(breach_key)
                    unique_breaches.append({
                        'Nombre': breach_name,
                        'Dominio': record.get('Dominio'),
                        'Fecha': record.get('Fecha de la brecha'),
                        'Cuentas afectadas': record.get('Cuentas afectadas'),
                        'Datos comprometidos': record.get('Datos comprometidos'),
                        'Es verificado': record.get('Es verificado'),
                        'Es sensible': record.get('Es sensible'),
                        'Riesgo': record.get('Riesgo')
                    })
        
        return unique_breaches