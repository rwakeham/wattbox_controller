# WattBox Controller

A simple Python tool to control WattBox outlets via HTTP/HTTPS.

## Features

- Auto-detects HTTP Basic or Digest Authentication
- Configurable via CLI arguments, environment variables, or `.env` file
- Automatically follows redirects (HTTP → HTTPS)
- Ignores HTTPS certificate verification issues
- Control outlets: on, off, or reset

## Installation

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Create a `.env` file for your credentials:

```bash
WATTBOX_URL=http://172.16.19.184
WATTBOX_USERNAME=your_username
WATTBOX_PASSWORD=your_password
```

## Usage

### Quick Start

With credentials in `.env` file:

```bash
python wattbox_controller.py -o 3 -a off
python wattbox_controller.py -o 3 -a on
python wattbox_controller.py -o 3 -a reset
```

### Command Line Options

```bash
python wattbox_controller.py --url http://172.16.19.184 --username admin --password secret -o 3 -a off
```

**Available Options:**
- `--url`, `-u`: WattBox base URL (default: `http://172.16.19.184` or `WATTBOX_URL`)
- `--username`: Username (default: `wattbox` or `WATTBOX_USERNAME`)
- `--password`: Password (default: `wattbox` or `WATTBOX_PASSWORD`)
- `--outlet`, `-o`: Outlet number (required)
- `--action`, `-a`: Action - `on`, `off`, or `reset` (default: `off`)
- `--verbose`, `-v`: Show detailed output
- `--help`, `-h`: Show help message

### Configuration Priority

1. Command line arguments (highest priority)
2. `.env` file variables
3. Environment variables
4. Default values

## Requirements

- Python 3.6+
- requests
- urllib3
- python-dotenv

## Security Notes

- SSL certificate verification is disabled for self-signed certificates
- Store credentials in `.env` file (already in `.gitignore`)
- Avoid passing credentials via command line in shared environments


