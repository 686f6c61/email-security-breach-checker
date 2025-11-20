"""
Email Security Breach Checker v2.0 - Utilidades de Exportación

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que maneja la exportación de datos a varios formatos 
(CSV, Excel, JSON).

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd

from .exceptions import FileOperationError
from .logger import logger
from .validators import validate_output_filename, validate_directory_path


class DataExporter:
    """Maneja la exportación de datos a varios formatos de archivo."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize data exporter.
        
        Args:
            output_dir: Directory to save files to. If None, uses default.
        """
        if output_dir is None:
            from config.settings import settings
            output_dir = settings.generated_dir
        
        validate_directory_path(output_dir)
        self.output_dir = output_dir
    
    def export_csv(
        self, 
        data: List[Dict[str, Any]], 
        filename: str,
        encoding: str = 'utf-8-sig'  # BOM for Excel compatibility
    ) -> Path:
        """
        Export data to CSV file.
        
        Args:
            data: List of dictionaries to export
            filename: Base filename (without extension)
            encoding: File encoding
            
        Returns:
            Path to created file
            
        Raises:
            FileOperationError: If export fails
        """
        logger.info(f"Exporting {len(data)} records to CSV: {filename}")
        
        try:
            # Validate and prepare filename
            safe_filename = validate_output_filename(filename)
            output_path = self.output_dir / f"{safe_filename}.csv"
            
            # Convert to DataFrame and export
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False, encoding=encoding)
            
            logger.info(f"CSV export successful: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"Failed to export CSV: {str(e)}"
            logger.error(error_msg)
            raise FileOperationError(error_msg)
    
    def export_excel(
        self, 
        data: List[Dict[str, Any]], 
        filename: str,
        include_summary: bool = True
    ) -> Path:
        """
        Export data to Excel file with multiple sheets.
        
        Args:
            data: List of dictionaries to export
            filename: Base filename (without extension)
            include_summary: Whether to include summary sheet
            
        Returns:
            Path to created file
            
        Raises:
            FileOperationError: If export fails
        """
        logger.info(f"Exporting {len(data)} records to Excel: {filename}")
        
        try:
            # Validate and prepare filename
            safe_filename = validate_output_filename(filename)
            output_path = self.output_dir / f"{safe_filename}.xlsx"
            
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Main data sheet
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='Breaches', index=False)
                
                if include_summary:
                    # Summary statistics
                    from .data_processor import BreachDataProcessor
                    stats = BreachDataProcessor.get_summary_statistics(data)
                    
                    # Create summary DataFrame
                    summary_data = [
                        ['Total emails checked', stats['total_emails_checked']],
                        ['Compromised emails', stats['compromised_emails']],
                        ['Safe emails', stats['safe_emails']],
                        ['Error emails', stats['error_emails']],
                        ['Total breach records', stats['total_breach_records']],
                        ['Compromise rate', f"{stats['compromise_rate']:.1f}%"]
                    ]
                    
                    summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Risk distribution
                    if stats['risk_distribution']:
                        risk_data = [[risk, count] for risk, count in stats['risk_distribution'].items()]
                        risk_df = pd.DataFrame(risk_data, columns=['Risk Level', 'Count'])
                        risk_df.to_excel(writer, sheet_name='Risk Analysis', index=False)
                    
                    # Top breaches
                    if stats['top_breaches']:
                        top_breaches_data = [[name, count] for name, count in stats['top_breaches'].items()]
                        top_breaches_df = pd.DataFrame(top_breaches_data, columns=['Breach Name', 'Affected Count'])
                        top_breaches_df.to_excel(writer, sheet_name='Top Breaches', index=False)
            
            logger.info(f"Excel export successful: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"Failed to export Excel: {str(e)}"
            logger.error(error_msg)
            raise FileOperationError(error_msg)
    
    def export_json(
        self, 
        data: List[Dict[str, Any]], 
        filename: str,
        pretty_print: bool = True
    ) -> Path:
        """
        Export data to JSON file.
        
        Args:
            data: List of dictionaries to export
            filename: Base filename (without extension)
            pretty_print: Whether to format JSON for readability
            
        Returns:
            Path to created file
            
        Raises:
            FileOperationError: If export fails
        """
        logger.info(f"Exporting {len(data)} records to JSON: {filename}")
        
        try:
            # Validate and prepare filename
            safe_filename = validate_output_filename(filename)
            output_path = self.output_dir / f"{safe_filename}.json"
            
            # Prepare JSON data with metadata
            from datetime import datetime
            from config.settings import settings
            
            json_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'generator': f"{settings.app_name} v{settings.app_version}",
                    'total_records': len(data)
                },
                'data': data
            }
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                if pretty_print:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(json_data, f, ensure_ascii=False)
            
            logger.info(f"JSON export successful: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"Failed to export JSON: {str(e)}"
            logger.error(error_msg)
            raise FileOperationError(error_msg)
    
    def export_all_formats(
        self, 
        data: List[Dict[str, Any]], 
        filename: str,
        formats: List[str] = None
    ) -> Dict[str, Path]:
        """
        Export data to multiple formats.
        
        Args:
            data: List of dictionaries to export
            filename: Base filename (without extension)
            formats: List of formats to export ('csv', 'excel', 'json')
            
        Returns:
            Dictionary mapping format names to file paths
            
        Raises:
            FileOperationError: If any export fails
        """
        if formats is None:
            formats = ['csv', 'excel', 'json']
        
        logger.info(f"Exporting to multiple formats: {formats}")
        
        results = {}
        
        for format_name in formats:
            try:
                if format_name.lower() == 'csv':
                    results['csv'] = self.export_csv(data, filename)
                elif format_name.lower() in ['excel', 'xlsx']:
                    results['excel'] = self.export_excel(data, filename)
                elif format_name.lower() == 'json':
                    results['json'] = self.export_json(data, filename)
                else:
                    logger.warning(f"Unsupported export format: {format_name}")
                    
            except Exception as e:
                error_msg = f"Failed to export {format_name}: {str(e)}"
                logger.error(error_msg)
                raise FileOperationError(error_msg)
        
        logger.info(f"Multi-format export completed: {list(results.keys())}")
        return results
    
    def get_export_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary of data for export purposes.
        
        Args:
            data: Data to summarize
            
        Returns:
            Dictionary with export summary
        """
        from .data_processor import BreachDataProcessor
        
        stats = BreachDataProcessor.get_summary_statistics(data)
        
        return {
            'record_count': len(data),
            'unique_emails': stats['total_emails_checked'],
            'compromised_count': stats['compromised_emails'],
            'safe_count': stats['safe_emails'],
            'error_count': stats['error_emails'],
            'file_sizes_estimate': {
                'csv': f"~{len(data) * 200} bytes",  # Rough estimate
                'excel': f"~{len(data) * 500} bytes",  # Rough estimate
                'json': f"~{len(data) * 300} bytes"   # Rough estimate
            }
        }