import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def get_folder_names(base_path):
    """Get list of folder names in the base path"""
    folder_names = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    return folder_names

def print_summary(total_folders, processed_folders):
    """Print summary table"""
    table = Table(title="Processing Summary")
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right", style="magenta")
    
    table.add_row("Total Folders", str(total_folders))
    table.add_row("Processed", str(processed_folders))
    table.add_row("Remaining", str(total_folders - processed_folders))
    
    console.print(table)

def move_to_completed(base_dir, folder):
    """Move processed folder to completed directory"""
    try:
        completed_dir = os.path.join(os.path.dirname(base_dir), "completed")
        if not os.path.exists(completed_dir):
            os.makedirs(completed_dir)
        os.rename(os.path.join(base_dir, folder), 
                 os.path.join(completed_dir, folder))
        console.print(f"[blue]ℹ️[/blue] Moved {folder} to completed directory")
    except Exception as e:
        console.print(f"[yellow]⚠️[/yellow] Could not move folder: {str(e)}")