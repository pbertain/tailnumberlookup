# Tail Number Lookup

A modern web application for looking up FAA aircraft registration information by tail number (N-Number).

## Overview

This application provides both a web interface and API endpoints for querying FAA aircraft registration data. The backend automatically syncs with the FAA database multiple times per day to ensure data freshness.

## Features

- **Web Interface**: User-friendly search interface for tail numbers with modern AirPuff-themed design
- **JSON API**: RESTful API for programmatic access at `/api/v1/aircraft/{tail_number}`
- **cURL Text API**: Plain text format for cURL/CLI usage at `/api/v1/curl/aircraft/{tail_number}`
- **Swagger Documentation**: Interactive API docs at `/docs` with AirPuff color scheme
- **Automatic Data Sync**: Background service updates FAA data multiple times daily via systemd timer
- **SQLite Database**: Lightweight, file-based database storage

## Architecture

- **Backend**: Python FastAPI application
- **Frontend**: Modern HTML/CSS/JavaScript (vanilla, no frameworks)
- **Database**: SQLite (sufficient for FAA dataset size ~60-120 MB)
- **Data Sync**: systemd timer for automated updates (4 times daily)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pbertain/tailnumberlookup.git
   cd tailnumberlookup
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python -m backend.sync.database
   ```

5. **Download and import initial FAA data:**
   ```bash
   python -m backend.sync.sync_faa_data
   ```
   This will download the FAA data ZIP file and import it into SQLite.

6. **Start the API server:**
   ```bash
   uvicorn backend.api.main:app --host 0.0.0.0 --port 49080
   ```

7. **Access the application:**
   - Web interface: http://localhost:49080
   - API documentation: http://localhost:49080/docs
   - JSON API: http://localhost:49080/api/v1/aircraft/N12345
   - Text API: http://localhost:49080/api/v1/curl/aircraft/N12345

## Systemd Setup (Automated Sync)

To set up automated data synchronization:

1. **Copy systemd files to systemd directory:**
   ```bash
   sudo cp systemd/faa-sync.service systemd/faa-sync.timer /etc/systemd/system/
   ```

2. **Update paths in service file:**
   Edit `/etc/systemd/system/faa-sync.service` and update:
   - `WorkingDirectory` to your project path
   - `ExecStart` path to your Python virtual environment

3. **Enable and start the timer:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable faa-sync.timer
   sudo systemctl start faa-sync.timer
   ```

4. **Check timer status:**
   ```bash
   sudo systemctl status faa-sync.timer
   sudo systemctl list-timers faa-sync.timer
   ```

The timer runs at 00:00, 06:00, 12:00, and 18:00 daily.

## API Usage Examples

### JSON API
```bash
curl http://localhost:49080/api/v1/aircraft/N12345
```

### Text API (cURL-friendly)
```bash
curl http://localhost:49080/api/v1/curl/aircraft/N12345
```

### Health Check
```bash
curl http://localhost:49080/api/health
```

## Project Structure

```
tailnumberlookup/
├── backend/
│   ├── api/              # FastAPI application
│   │   ├── main.py       # API routes and endpoints
│   │   ├── models.py     # Pydantic models
│   │   └── database.py   # Database queries
│   └── sync/             # Data synchronization
│       ├── database.py           # SQLite schema
│       ├── download_faa_data.py  # Download FAA ZIP
│       ├── import_to_db.py       # Import CSVs to DB
│       └── sync_faa_data.py       # Main sync script
├── frontend/             # Web interface
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── systemd/             # Systemd service files
├── data/                # Database and extracted data (.gitignored)
├── requirements.txt
└── README.md
```

## Reference Implementations

- `reference_app_current/`: Current working implementation (MySQL-based)
- `reference_app_rewrite/`: Previous rewrite attempt

## Deployment

### Ansible Deployment

The application can be deployed using Ansible. See `ansible/README.md` for detailed instructions.

**Quick deploy:**
```bash
cd ansible
ansible-playbook --ask-vault-pass \
  -u ansible \
  --private-key ~/.ssh/keys/nirdclub__id_ed25519 \
  -i inventory.yml \
  playbook.yml
```

The playbook will:
- Install Python 3 and dependencies
- Deploy application to `/opt/tailnumberlookup`
- Set up systemd services (API on port 49080 and sync timer)
- Start and enable services

### Deployment Configuration

- **Host**: host74.nird.club
- **User**: ansible
- **SSH Key**: `~/.ssh/keys/nirdclub__id_ed25519`
- **Installation Path**: `/opt/tailnumberlookup`
- **API Port**: 49080

## Development

### Running Tests

The application can be tested by:
1. Starting the server: `uvicorn backend.api.main:app --port 49080`
2. Visiting the web interface at http://localhost:49080
3. Trying sample tail numbers like "N12345" (if in database)

### Manual Data Sync

To manually sync data without systemd:
```bash
python -m backend.sync.sync_faa_data
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

