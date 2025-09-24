import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import track, Progress
from oper_fm_automation import NBTC_Automation
from utils import get_folder_names, print_summary, move_to_completed
import time
console = Console()
# load_dotenv()

def main():
    # Create header
    console.print(Panel.fit("🤖 NBTC Automation System", style="bold blue"))

    # Credentials


    # Get absolute path
    current_path = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_path, "picture")

    # Initialize automation
    with console.status("[bold green]Initializing automation...") as status:
        automation = NBTC_Automation()
        automation.login()
        automation.navigate_to_fm_page()
        console.print("[green]✓[/green] Initialization complete")

    while True:
        folder_names = get_folder_names(base_dir)
        if not folder_names:
            console.print("[yellow]No folders to process![/yellow]")
            break

        total_folders = len(folder_names)
        console.print(f"\n[yellow]Found {total_folders} folders to process[/yellow]")

        # Process each folder with progress tracking
        processed_count = 0
        with Progress() as progress:
            # Simple progress bar without percentage
            task = progress.add_task("[cyan]Processing...", total=total_folders)
            
            for folder in folder_names:
                console.print(Panel(f"[bold blue]Processing Folder: {folder}[/bold blue]"))
                picture_dir = os.path.join(base_dir, folder)
                
                try:
                    with console.status("[bold yellow]Running input_fm...") as status:
                        automation.input_fm(folder)
                        time.sleep(2)
                        console.print("[green]✓[/green] Input FM completed")

                    with console.status("[bold yellow]Processing details...") as status:
                        automation.input_detail_fm(picture_dir)
                        # time.sleep(5)
                        console.print("[green]✓[/green] Details processed")

                    # Move processed folder
                    move_to_completed(base_dir, folder)
                    processed_count += 1
                    progress.update(task, advance=1)  # Simple progress update
                    console.print(f"[green]✓[/green] Successfully processed {folder}")

                except Exception as e:
                    console.print(Panel(f"[red]Error processing {folder}:[/red]\n{str(e)}", 
                                      style="red"))
                    continue

                console.print("─" * 50)

        # Print summary after each batch
        print_summary(total_folders, processed_count)

    # Final message
    console.print(Panel.fit(
        "[bold green]🎉 All folders have been processed successfully![/bold green]",
        style="green"
    ))

    # Auto-close browser
    console.print("[dim]Closing browser automatically...[/dim]")
    automation.close()

if __name__ == "__main__":
    main()