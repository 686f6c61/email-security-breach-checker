"""
Email Security Breach Checker v2.0 - Interfaz de Línea de Comandos

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que proporciona una CLI moderna usando argparse para 
operación no interactiva del verificador de seguridad de emails.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

from config.settings import settings
from utils.validators import validate_email, validate_csv_file
from utils.exceptions import EmailSecurityException, ValidationError
from ui.display import display


class EmailSecurityCLI:
    """Interfaz de Línea de Comandos para Email Security Breach Checker."""
    
    def __init__(self):
        """Inicializar CLI."""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Crear el parser de argumentos."""
        parser = argparse.ArgumentParser(
            prog="email-security-checker",
            description="Verificar si las direcciones de correo han sido comprometidas en brechas de seguridad",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
Ejemplos:
  # Verificar email individual
  %(prog)s --email usuario@ejemplo.com
  
  # Verificar emails desde archivo CSV
  %(prog)s --file emails.csv
  
  # Modo Enterprise - verificar todos los emails de la empresa
  %(prog)s --file empresa_emails.csv --enterprise --recipient admin@empresa.com
  
  # Exportar a formatos específicos
  %(prog)s --file emails.csv --export csv excel
  
  # Modo optimizado para Docker
  %(prog)s --file emails.csv --docker --batch-size 100

Límites de Rate HIBP (Actual: {settings.get_tier_info()['tier']}):
  RPM: {settings.get_tier_info()['rpm']} peticiones/minuto
  Domain Limit: {settings.get_tier_info()['domain_limit'] if settings.get_tier_info()['domain_limit'] != float('inf') else 'Unlimited'}
  Upgrade: {settings.hibp_subscription_url}
            """
        )
        
        # Input options
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument(
            "--email", "-e",
            help="Single email address to check"
        )
        input_group.add_argument(
            "--file", "-f",
            type=Path,
            help="CSV file containing email addresses to check"
        )
        
        # Output options
        parser.add_argument(
            "--export", 
            nargs="+",
            choices=["csv", "excel", "json"],
            default=["csv", "excel"],
            help="Export formats (default: csv excel)"
        )
        
        parser.add_argument(
            "--output", "-o",
            help="Output filename (without extension)"
        )
        
        parser.add_argument(
            "--no-cache",
            action="store_true",
            help="Disable cache and force fresh API calls"
        )
        
        # Email options
        parser.add_argument(
            "--recipient", "-r",
            help="Email address to send report to"
        )
        
        parser.add_argument(
            "--no-email",
            action="store_true",
            help="Skip sending email report"
        )
        
        # Enterprise options
        parser.add_argument(
            "--enterprise",
            action="store_true",
            help="Enterprise mode - optimized for bulk processing"
        )
        
        parser.add_argument(
            "--batch-size",
            type=int,
            default=settings.get_optimal_batch_size(),
            help=f"Batch size for processing (default: {settings.get_optimal_batch_size()})"
        )
        
        # Docker options
        parser.add_argument(
            "--docker",
            action="store_true",
            help="Docker optimized mode"
        )
        
        # Configuration options
        parser.add_argument(
            "--config",
            type=Path,
            help="Path to configuration file"
        )
        
        parser.add_argument(
            "--tier",
            choices=["Pwned 1", "Pwned 2", "Pwned 3", "Pwned 4", "Pwned 5"],
            help="HIBP subscription tier"
        )
        
        # Other options
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Verbose output"
        )
        
        parser.add_argument(
            "--quiet", "-q",
            action="store_true",
            help="Quiet mode - minimal output"
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {settings.app_version}"
        )
        
        return parser
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """Parse command line arguments."""
        parsed_args = self.parser.parse_args(args)
        
        # Validate arguments
        self._validate_args(parsed_args)
        
        return parsed_args
    
    def _validate_args(self, args: argparse.Namespace) -> None:
        """Validate parsed arguments."""
        try:
            # Validate email if provided
            if args.email:
                validate_email(args.email)
            
            # Validate file if provided
            if args.file:
                if not args.file.exists():
                    raise ValidationError(f"File not found: {args.file}")
                if not args.file.is_file():
                    raise ValidationError(f"Path is not a file: {args.file}")
                if args.file.suffix.lower() != '.csv':
                    raise ValidationError(f"File must be CSV: {args.file}")
            
            # Validate recipient if provided
            if args.recipient:
                validate_email(args.recipient)
            
            # Check for conflicting options
            if args.verbose and args.quiet:
                raise ValidationError("Cannot use --verbose and --quiet together")
            
            # Warn about rate limits for large files
            if args.file and args.file.exists():
                try:
                    emails = validate_csv_file(args.file)
                    should_warn, warning = settings.should_warn_about_rate_limit(len(emails))
                    if should_warn and not args.quiet:
                        display.show_warning(warning)
                except ValidationError:
                    pass  # Will be caught later
            
        except ValidationError as e:
            display.show_error(str(e))
            sys.exit(1)
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI application.
        
        Args:
            args: Command line arguments (defaults to sys.argv)
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            parsed_args = self.parse_args(args)
            
            # Import here to avoid circular imports
            from main import EmailSecurityApp
            
            # Create and configure app
            app = EmailSecurityApp()
            
            # Override settings based on CLI args
            if parsed_args.tier:
                settings.hibp_tier = parsed_args.tier
                # Recalculate rate limits
                tier_config = settings.hibp_rate_limits[parsed_args.tier]
                settings.hibp_rate_limit_rpm = tier_config['rpm']
                settings.hibp_rate_limit_delay = 60.0 / tier_config['rpm']
                settings.hibp_domain_limit = tier_config['domain_limit']
            
            if parsed_args.docker:
                settings.is_docker = True
            
            if parsed_args.batch_size:
                settings.batch_size = parsed_args.batch_size
            
            # Initialize app
            if not app.initialize():
                return 1
            
            # Process based on input type
            if parsed_args.email:
                success = self._process_single_email(app, parsed_args)
            elif parsed_args.file:
                success = self._process_file(app, parsed_args)
            else:
                return 1
            
            return 0 if success else 1
            
        except KeyboardInterrupt:
            if not parsed_args.quiet:
                display.show_info("Operation cancelled by user")
            return 130
        except EmailSecurityException as e:
            display.show_error(str(e))
            return 1
        except Exception as e:
            display.show_error(f"Unexpected error: {str(e)}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1
        finally:
            # Cleanup
            if 'app' in locals():
                app.cleanup()
    
    def _process_single_email(self, app: 'EmailSecurityApp', args: argparse.Namespace) -> bool:
        """Process a single email address."""
        if not args.quiet:
            display.show_info(f"Checking email: {args.email}")
        
        results = app.check_single_email(args.email)
        
        if not results:
            return False
        
        processed_data = app.process_and_display_results(results)
        
        # Export if requested
        exported_files = {}
        if args.output:
            exported_files = app.export_results(processed_data)
        
        # Send email if requested
        if not args.no_email:
            # Get breach count for confirmation
            stats = app.data_processor.get_summary_statistics(processed_data)
            breach_count = stats.get('compromised_emails', 0)

            # Ask for confirmation unless recipient was specified in args
            should_send = True
            if not args.recipient and not args.quiet:
                should_send = display.confirm_send_email(breach_count)

            if should_send:
                recipient = args.recipient or settings.enterprise_recipient_email
                if not recipient and not args.quiet:
                    # For single email, offer to send to the checked email or another
                    recipient = display.prompt_single_email_recipient(args.email)

                if recipient:
                    return app.send_email_report(processed_data, exported_files, recipient, results)
        
        return True
    
    def _process_file(self, app: 'EmailSecurityApp', args: argparse.Namespace) -> bool:
        """Process emails from a CSV file."""
        if not args.quiet:
            display.show_info(f"Processing file: {args.file}")
        
        # Get emails for validation
        try:
            emails = validate_csv_file(args.file)
            if not args.quiet:
                display.show_info(f"Found {len(emails)} email addresses to check")
        except ValidationError as e:
            display.show_error(str(e))
            return False
        
        # Process in batches if enterprise mode
        if args.enterprise or args.docker:
            return self._process_in_batches(app, emails, args)
        else:
            results = app.check_emails_from_file(args.file)
            
            if not results:
                return False
            
            processed_data = app.process_and_display_results(results)
            
            # Export if requested
            exported_files = {}
            if args.output:
                exported_files = app.export_results(processed_data)
            
            # Send email if requested
            if not args.no_email:
                # Get breach count for confirmation
                stats = app.data_processor.get_summary_statistics(processed_data)
                breach_count = stats.get('compromised_emails', 0)

                # Ask for confirmation unless recipient was specified in args
                should_send = True
                if not args.recipient and not args.quiet:
                    should_send = display.confirm_send_email(breach_count)

                if should_send:
                    recipient = args.recipient or settings.enterprise_recipient_email
                    if not recipient and not args.quiet:
                        recipient = display.prompt_for_email_recipient()

                    if recipient:
                        return app.send_email_report(processed_data, exported_files, recipient, results)
            
            return True
    
    def _process_in_batches(self, app: 'EmailSecurityApp', emails: List[str], args: argparse.Namespace) -> bool:
        """Process emails in batches for enterprise mode."""
        batch_size = args.batch_size
        total_emails = len(emails)
        all_results = {}
        all_processed_data = []
        
        if not args.quiet:
            display.show_info(f"Processing {total_emails} emails in batches of {batch_size}")
        
        for i in range(0, total_emails, batch_size):
            batch_emails = emails[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_emails + batch_size - 1) // batch_size
            
            if not args.quiet:
                display.show_info(f"Processing batch {batch_num}/{total_batches} ({len(batch_emails)} emails)")
            
            # Create temporary CSV for this batch
            import tempfile
            import csv
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                writer = csv.writer(f)
                for email in batch_emails:
                    writer.writerow([email])
                temp_file = Path(f.name)
            
            try:
                # Process batch
                results = app.check_emails_from_file(temp_file)
                all_results.update(results)
                
                # Process and accumulate data
                batch_processed = app.data_processor.process_breach_results(results)
                all_processed_data.extend(batch_processed)
                
            finally:
                temp_file.unlink()
        
        # Display final results
        if not args.quiet:
            app.process_and_display_results(all_results)
        
        # Export if requested
        exported_files = {}
        if args.output:
            exported_files = app.export_results(all_processed_data)
        
        # Send email if requested
        if not args.no_email:
            # Get breach count for confirmation
            stats = app.data_processor.get_summary_statistics(all_processed_data)
            breach_count = stats.get('compromised_emails', 0)

            # Ask for confirmation unless recipient was specified in args
            should_send = True
            if not args.recipient and not args.quiet:
                should_send = display.confirm_send_email(breach_count)

            if should_send:
                recipient = args.recipient or settings.enterprise_recipient_email
                if not recipient and not args.quiet:
                    recipient = display.prompt_for_email_recipient()

                if recipient:
                    return app.send_email_report(all_processed_data, exported_files, recipient, all_results)
        
        return True


def main() -> int:
    """Main CLI entry point."""
    cli = EmailSecurityCLI()
    return cli.run()