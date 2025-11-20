"""
Email Security Breach Checker v2.0 - Interfaz de Usuario

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que proporciona una hermosa salida por consola para la aplicación 
usando la librería Rich.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.tree import Tree
from rich.layout import Layout
from rich.columns import Columns
from rich import box

from config.settings import settings
from utils.logger import logger


class DisplayManager:
    """Manages all console display operations using Rich."""
    
    def __init__(self):
        """Initialize display manager."""
        self.console = Console()
    
    def show_banner(self) -> None:
        """Display application banner."""
        title = Text(settings.app_name, style="bold cyan")
        version = Text(f"Version {settings.app_version}", style="italic green")
        description = Text(
            "Verifies if email addresses have been compromised in security breaches",
            style="yellow"
        )
        repo = Text(settings.github_repo, style="blue underline")
        
        content = f"{title}\n\n{version}\n\n{description}\n\n{repo}"
        panel = Panel(
            content,
            expand=False,
            border_style="bold blue",
            title="🔒 Email Security Checker",
            title_align="center"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_configuration_status(self, is_valid: bool) -> None:
        """
        Display configuration status.
        
        Args:
            is_valid: Whether configuration is valid
        """
        if is_valid:
            status_text = Text("✅ Configuration Valid", style="bold green")
            self.console.print(Panel(status_text, border_style="green"))
        else:
            status_text = Text("❌ Configuration Invalid", style="bold red")
            details = Text(
                "Please check your .env file and ensure all required variables are set:\n"
                "- HIBP_API_KEY\n"
                "- RESEND_API_KEY\n"
                "- SENDER_EMAIL",
                style="red"
            )
            self.console.print(Panel(status_text + "\n\n" + details, border_style="red"))
    
    def show_results_table(self, data: List[Dict[str, str]]) -> None:
        """
        Display results in a formatted table.
        
        Args:
            data: Processed breach data to display
        """
        if not data:
            self.console.print("[yellow]No data to display[/yellow]")
            return
        
        table = Table(
            title="🔍 Security Breach Analysis Results",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        # Add columns
        columns = ['Correo', 'Nombre de la brecha', 'Fecha', 'Cuentas afectadas', 'Riesgo']
        for column in columns:
            table.add_column(column, style="cyan", no_wrap=True)
        
        # Add rows
        for record in data:
            # Style based on risk level
            risk = record.get('Riesgo', 'Bajo')
            if risk == 'Crítico':
                row_style = "bold red"
            elif risk == 'Alto':
                row_style = "red"
            elif risk == 'Medio':
                row_style = "yellow"
            elif risk == 'Error':
                row_style = "bold magenta"
            else:
                row_style = "green"
            
            # Select and format columns for display
            display_values = [
                record.get('Correo', '-'),
                record.get('Nombre de la brecha', '-'),
                record.get('Fecha de la brecha', '-'),
                record.get('Cuentas afectadas', '-'),
                risk
            ]
            
            table.add_row(*display_values, style=row_style)
        
        self.console.print(table)
    
    def show_summary_statistics(self, stats: Dict[str, Any]) -> None:
        """
        Display summary statistics.
        
        Args:
            stats: Statistics dictionary
        """
        # Create summary panel
        summary_text = Text.assemble(
            ("📊 Summary Statistics\n\n", "bold cyan"),
            (f"Total emails checked: ", "white"),
            (f"{stats['total_emails_checked']}", "bold yellow"),
            ("\n", ""),
            (f"Compromised emails: ", "white"),
            (f"{stats['compromised_emails']}", "bold red"),
            ("\n", ""),
            (f"Safe emails: ", "white"),
            (f"{stats['safe_emails']}", "bold green"),
            ("\n", ""),
            (f"Error emails: ", "white"),
            (f"{stats['error_emails']}", "bold magenta"),
            ("\n", ""),
            (f"Compromise rate: ", "white"),
            (f"{stats['compromise_rate']:.1f}%", "bold yellow" if stats['compromise_rate'] > 20 else "green")
        )
        
        self.console.print(Panel(summary_text, title="📈 Summary", border_style="cyan"))
        
        # Show risk distribution if available
        if stats.get('risk_distribution'):
            risk_table = Table(title="Risk Distribution", box=box.SIMPLE)
            risk_table.add_column("Risk Level", style="cyan")
            risk_table.add_column("Count", style="yellow")
            
            risk_colors = {
                'Crítico': 'red',
                'Alto': 'red',
                'Medio': 'yellow',
                'Bajo': 'green',
                'Error': 'magenta'
            }
            
            for risk_level, count in stats['risk_distribution'].items():
                color = risk_colors.get(risk_level, 'white')
                risk_table.add_row(risk_level, f"[{color}]{count}[/{color}]")
            
            self.console.print(risk_table)
    
    def show_progress(self, description: str, total: Optional[int] = None):
        """
        Create a progress context manager.
        
        Args:
            description: Description for the progress bar
            total: Total items to process
            
        Returns:
            Progress context manager
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
    
    def show_file_list(self, files: List[str], title: str = "Files") -> None:
        """
        Display a list of files.
        
        Args:
            files: List of file names
            title: Title for the list
        """
        if not files:
            self.console.print(f"[yellow]No {title.lower()} found[/yellow]")
            return
        
        tree = Tree(f"📁 {title}")
        for file in files:
            tree.add(f"📄 {file}")
        
        self.console.print(tree)
    
    def prompt_for_file(self, directory: Path) -> Optional[str]:
        """
        Prompt user to select a file from directory.
        
        Args:
            directory: Directory to list files from
            
        Returns:
            Selected filename or None
        """
        files = [f.name for f in directory.glob("*.csv")]
        
        if not files:
            self.console.print(f"[red]No CSV files found in {directory}[/red]")
            return None
        
        self.show_file_list(files, f"CSV files in {directory.name}")
        
        return Prompt.ask(
            "[bold yellow]Enter filename (or 'back' to return)[/bold yellow]",
            default=files[0] if files else None
        )
    
    def prompt_for_email(self) -> str:
        """
        Prompt user to enter an email address.
        
        Returns:
            Email address entered by user
        """
        return Prompt.ask("[bold yellow]Enter email address to check[/bold yellow]")
    
    def prompt_for_output_filename(self) -> str:
        """
        Prompt user for output filename.
        
        Returns:
            Filename entered by user
        """
        return Prompt.ask(
            "[bold yellow]Enter output filename (without extension)[/bold yellow]"
        )
    
    def prompt_for_export_formats(self) -> List[str]:
        """
        Prompt user to select export formats.
        
        Returns:
            List of selected formats
        """
        self.console.print("\n[bold cyan]Available export formats:[/bold cyan]")
        self.console.print("1. CSV")
        self.console.print("2. Excel (XLSX)")
        self.console.print("3. JSON")
        self.console.print("4. All formats")
        
        choice = Prompt.ask(
            "[bold yellow]Select format (1-4)[/bold yellow]",
            choices=["1", "2", "3", "4"],
            default="4"
        )
        
        format_map = {
            "1": ["csv"],
            "2": ["excel"],
            "3": ["json"],
            "4": ["csv", "excel", "json"]
        }
        
        return format_map[choice]
    
    def prompt_for_email_recipient(self) -> str:
        """
        Prompt user for email recipient.
        
        Returns:
            Email address entered by user
        """
        return Prompt.ask(
            "[bold yellow]Enter recipient email address[/bold yellow]"
        )
    
    def confirm_send_email(self, breach_count: int) -> bool:
        """
        Ask user if they want to send email report.

        Args:
            breach_count: Number of breaches found

        Returns:
            True if user wants to send email
        """
        if breach_count > 0:
            message = f"[bold red]Found {breach_count} breach(es). Send email report?[/bold red]"
        else:
            message = "[bold green]No breaches found. Send email report anyway?[/bold green]"

        return Confirm.ask(message)

    def prompt_email_send_mode(self, email_count: int) -> str:
        """
        Ask user how they want to send emails for multiple addresses.

        Args:
            email_count: Number of email addresses checked

        Returns:
            'admin' for admin only, 'individual' for each user, 'both' for both
        """
        self.console.print(f"\n[bold cyan]Email sending options for {email_count} addresses:[/bold cyan]")
        self.console.print("1. Send to administrator only (one email with all breaches)")
        self.console.print("2. Send to each user individually (each gets only their breaches)")
        self.console.print("3. Both (admin gets all + each user gets their own)")

        choice = Prompt.ask(
            "[bold yellow]Select sending mode[/bold yellow]",
            choices=["1", "2", "3"],
            default="1"
        )

        mode_map = {
            "1": "admin",
            "2": "individual",
            "3": "both"
        }

        return mode_map[choice]

    def prompt_single_email_recipient(self, checked_email: str) -> Optional[str]:
        """
        Ask user where to send report for a single email check.

        Args:
            checked_email: The email address that was checked

        Returns:
            Email address to send to, or None to cancel
        """
        self.console.print(f"\n[bold cyan]Send report for {checked_email}:[/bold cyan]")
        self.console.print(f"1. Send to {checked_email} (the checked email)")
        self.console.print("2. Send to another email address")
        self.console.print("3. Don't send")

        choice = Prompt.ask(
            "[bold yellow]Select option[/bold yellow]",
            choices=["1", "2", "3"],
            default="1"
        )

        if choice == "1":
            return checked_email
        elif choice == "2":
            return self.prompt_for_email_recipient()
        else:
            return None

    def confirm_action(self, message: str, default: bool = False) -> bool:
        """
        Ask user for confirmation.
        
        Args:
            message: Confirmation message
            default: Default response
            
        Returns:
            True if user confirms
        """
        return Confirm.ask(f"[bold yellow]{message}[/bold yellow]", default=default)
    
    def show_error(self, message: str) -> None:
        """
        Display error message.
        
        Args:
            message: Error message to display
        """
        self.console.print(f"[bold red]❌ Error: {message}[/bold red]")
    
    def show_success(self, message: str) -> None:
        """
        Display success message.
        
        Args:
            message: Success message to display
        """
        self.console.print(f"[bold green]✅ {message}[/bold green]")
    
    def show_warning(self, message: str) -> None:
        """
        Display warning message.
        
        Args:
            message: Warning message to display
        """
        self.console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")
    
    def show_info(self, message: str) -> None:
        """
        Display info message.
        
        Args:
            message: Info message to display
        """
        self.console.print(f"[bold blue]ℹ️  {message}[/bold blue]")
    
    def show_menu(self, options: List[str], title: str = "Menu") -> str:
        """
        Display menu and get user selection.
        
        Args:
            options: List of menu options
            title: Menu title
            
        Returns:
            Selected option
        """
        self.console.print(f"\n[bold cyan]{title}:[/bold cyan]")
        for i, option in enumerate(options, 1):
            self.console.print(f"{i}. {option}")
        
        choice = Prompt.ask(
            "[bold yellow]Select an option[/bold yellow]",
            choices=[str(i) for i in range(1, len(options) + 1)]
        )
        
        return choice


# Global display manager instance
display = DisplayManager()