#!/usr/bin/env python3
"""
ICS Event Extractor CLI Tool

Extracts events from an ICS (iCalendar) file and displays them in a table,
or exports them as CSV or Markdown.

Features:
- Displays only future events by default.
- Supports showing past events with `--all` option.
- Sorts events chronologically.
- Allows output in `table`, `csv`, or `markdown` format.
- Supports `--short N` to display only the next N events (default: 10).

MIT License
Copyright (c) 2025 Andy Piper
"""

import click
import csv
import pandas as pd
from ics import Calendar
from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()


def parse_ics(file_path: str, include_past: bool = False):
    """
    Parses the ICS file and extracts event data.

    Args:
        file_path (str): Path to the .ics file.
        include_past (bool): Whether to include past events.

    Returns:
        list: A sorted list of tuples (date, location, event name).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        calendar = Calendar(f.read())

    events = []
    now = datetime.now().date()

    for event in calendar.events:
        date = event.begin.date()
        location = event.location if event.location else "Unknown"
        name = event.name if event.name else "No Title"

        if include_past or date >= now:
            events.append((date.isoformat(), location, name))

    return sorted(events, key=lambda x: x[0])


def display_table(events: list):
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


def output_csv(events: list, output_file: str):
    """
    Saves events as a CSV file.

    Args:
        events (list]: List of events to save.
        output_file (str): Output file name.
    """
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Location", "Event Name"])
        writer.writerows(events)

    console.print(f"✅ CSV file saved: [bold]{output_file}[/bold]")


def output_markdown(events: list, output_file: str):
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

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_table)

    console.print(f"✅ Markdown file saved: [bold]{output_file}[/bold]")


@click.command()
@click.argument("ics_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "csv", "markdown"], case_sensitive=False),
    default="table",
    help="Output format: table, csv, or markdown",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file (for CSV or Markdown)",
)
@click.option(
    "--all",
    is_flag=True,
    help="Include past events",
)
@click.option(
    "--short",
    "-s",
    type=int,
    default=None,
    help="Show only the next N events (default: 10)",
)
def cli(ics_file: str, format: str, output: str, all: bool, short: int):
    """
    Extracts and displays events from an ICS file.

    Args:
        ics_file (str): Path to the ICS file.
        format (str): Output format: table, csv, or markdown.
        output (str): Output file name (for CSV or Markdown).
        all (bool): Whether to include past events.
        short (int): Number of events to show in short mode.
    """
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


if __name__ == "__main__":
    cli()

