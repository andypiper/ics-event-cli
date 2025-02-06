#!/usr/bin/env python3
"""
ICS Event Extractor CLI Tool

Extracts events from an ICS (iCalendar) file and displays them in a table,
or exports them as CSV or Markdown.

Features:
- Displays future events by default.
- Supports showing past events with `--all` option.
- Sorts events chronologically.
- Allows output in `table`, `csv`, or `markdown` format.
- Supports `--short N` to display only the next N events (default: 5).

MIT License
Copyright (c) 2025 Andy Piper
"""

import click
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from ics import Calendar
from rich.console import Console
from rich.table import Table

console = Console()

class ICSError(Exception):
    """exception for ICS processing errors."""
    pass

def parse_ics(file_path: Path, include_past: bool = False) -> List[Tuple[str, str, str]]:
    """
    Parse the ICS file and extract event data.

    Args:
        file_path: Path to the .ics file
        include_past: Whether to include past events

    Returns:
        List of tuples containing (date, location, event name)

    Raises:
        ICSError: Error reading or parsing the file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                calendar = Calendar(f.read())
            except Exception as e:
                raise ICSError(f"Failed to parse ICS file: {e}")
    except UnicodeDecodeError:
        raise ICSError("File encoding error. Check that the file is UTF-8 encoded.")
    except OSError as e:
        raise ICSError(f"Failed to read file: {e}")

    events = []
    now = datetime.now().date()

    for event in calendar.events:
        date = event.begin.date()
        location = event.location or "Unknown"
        name = event.name or "No Title"

        if include_past or date >= now:
            events.append((date.isoformat(), location, name))

    return sorted(events, key=lambda x: x[0])

def validate_output_path(path: Optional[Path], format: str) -> Path:
    """
    Validates and returns the output file path.

    Args:
        path: The output path specified
        format: The desired output format

    Returns:
        A Path object for the output file

    Raises:
        click.BadParameter: If path is invalid
    """
    if not path:
        path = Path(f"events.{format}")

    # Check if directory exists
    if not path.parent.exists():
        raise click.BadParameter(f"Directory {path.parent} does not exist")

    # Check if file is writable
    try:
        path.touch(exist_ok=True)
        path.unlink()
    except OSError:
        raise click.BadParameter(f"Cannot write to {path}")

    return path


def display_table(events: List[Tuple[str, str, str]]) -> None:
    """
    Displays events in a rich terminal table.

    Args:
        events (list): List of events to display.
    """
    table = Table(title="Event Schedule")
    table.add_column("Date", style="cyan", justify="center")
    table.add_column("Location", style="magenta")
    table.add_column("Event Name", style="green")

    for event in events:
        table.add_row(*event)

    console.print(table)


def output_csv(events: List[Tuple[str, str, str]], output_file: Path) -> None:
    """
    Saves events as a CSV file.

    Args:
        events (list]: List of events to save.
        output_file (str): Output file name.
    """
    try:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
           writer = csv.writer(f)
           writer.writerow(["Date", "Location", "Event Name"])
           writer.writerows(events)
    except OSError as e:
        raise ICSError(f"Failed to write CSV file: {e}")

    console.print(f"CSV file saved: [bold]{output_file}[/bold]")


def output_markdown(events: List[Tuple[str, str, str]], output_file: Path) -> None:
    """
    Saves events as a Markdown table.

    Args:
        events (list]: List of events to save.
        output_file (str): Output file name.
    """
    md_table = "| Date | Location | Event Name |\n|---|---|---|\n"
    md_table += "\n".join(
        [f"| {date} | {location} | {name} |" for date, location, name in events]
    )

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_table)
    except OSError as e:
        raise ICSError(f"Failed to write Markdown file: {e}")

    console.print(f"Markdown file saved: [bold]{output_file}[/bold]")


@click.command()
@click.argument("ics_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "csv", "markdown"], case_sensitive=False),
    default="table",
    help="Output format: table, csv, or markdown",
)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Output file (for CSV or Markdown)",
)
@click.option(
    "--all", "-a",
    is_flag=True,
    help="Include past events",
)
@click.option(
    "--short", "-s",
    type=click.IntRange(min=1),
    default=5,
    help="Show only the next N events (default: 5)",
)
def cli(ics_file: Path, format: str, output: Optional[Path], all: bool, short: Optional[int]):
    """
    Extracts and displays events from an ICS file.
    """
    try:
        events = parse_ics(ics_file, include_past=all)

        if not events:
            console.print("[bold red]No events found in the ICS file.[/bold red]")
            return

        if short is not None:
            events = events[:short]  # Show only the next N events

        if format == "table":
            display_table(events)
        elif format == "csv":
            output = output or "events.csv"
            output_csv(events, output)
        elif format == "markdown":
            output = output or "events.md"
            output_markdown(events, output)

    except ICSError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        raise click.Abort()

if __name__ == "__main__":
    cli()

