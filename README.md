# ICS CLI Tool

A command-line tool to quickly extract and display events from an ICS file. Supports terminal tables, CSV export, and Markdown output.

## Features

- **Parses ICS files** and extracts event details.
- **Shows only future events by default** (past events optional).
- **Rich terminal table display** using `rich`.
- **Export as CSV or Markdown**.
- **Short mode**: Shows only the next n events (defaults to 5); complete listing available.

## Installation

### **Option 1: Using `pip`**

```sh
pip install -r requirements.txt
```

### **Option 2: Using `poetry`**

```sh
poetry install
```

## Usage

### **Display upcoming events in a table (default)**

```sh
python ics_events.py my_calendar.ics
```

### **Show all events (including past)**

```sh
python ics_events.py my_calendar.ics --all
```

### **Show only the next 10 events**

```sh
python ics_events.py my_calendar.ics --short
```

### **Show the next 5 events**

```sh
python ics_events.py my_calendar.ics --short 5
```

### **Show all events (no filtering)**

```sh
python ics_events.py my_calendar.ics --all
```

### **Show the next 25 events**

```sh
python ics_events.py my_calendar.ics --short 20
```

### **Export the next 15 events to CSV**

```sh
python ics_events.py my_calendar.ics --format csv -o events.csv --short 15
```

### **Export to CSV**

```sh
python ics_events.py my_calendar.ics --format csv -o events.csv
```

### **Export to Markdown**

```sh
python ics_events.py my_calendar.ics --format markdown -o events.md
```

## License

MIT License © 2025 Andy Piper
