# Tail Number Lookup

A modern web application for looking up FAA aircraft registration information by tail number (N-Number).

## Overview

This application provides both a web interface and API endpoints for querying FAA aircraft registration data. The backend automatically syncs with the FAA database multiple times per day to ensure data freshness.

## Features

- **Web Interface**: User-friendly search interface for tail numbers
- **JSON API**: RESTful API for programmatic access
- **Plain Text API**: Simple cURL-friendly text output format
- **Automatic Data Sync**: Background service updates FAA data multiple times daily
- **SQLite Database**: Lightweight, file-based database storage

## Architecture

- **Backend**: Python FastAPI application
- **Frontend**: Modern HTML/CSS/JavaScript
- **Database**: SQLite (sufficient for FAA dataset size)
- **Data Sync**: systemd timer for automated updates

## Reference Implementations

- `reference_app_current/`: Current working implementation
- `reference_app_rewrite/`: Previous rewrite attempt

## Development

This repository is under active development. The rewrite is in progress to modernize the architecture and improve maintainability.

## License

MIT License - see [LICENSE](LICENSE) file for details.

