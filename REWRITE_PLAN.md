# Tail Number Lookup - Rewrite Plan

## Overview
This document outlines the plan for rewriting the FAA Tail Number Lookup application with a modern, maintainable architecture.

## Current State Analysis

### Reference App (reference_app_current/)
- **Database**: MySQL (requires separate database server)
- **Data Sync**: Uses MySQL with pymysql, syncs via cron job
- **API**: FastAPI with basic endpoints
- **Frontend**: Simple HTML/CSS using AirPuff branding
- **Data Source**: Downloads `ReleasableAircraft.zip` from FAA, extracts CSVs (MASTER.txt, ACFTREF.txt, ENGINE.txt)

### Data Volume Assessment
Based on typical FAA registration data:
- **Aircraft Records**: ~350,000-400,000 active registrations
- **Aircraft Models**: ~10,000-15,000 model codes
- **Engine Types**: ~5,000-8,000 engine codes
- **Estimated DB Size**: ~60-120 MB (well within SQLite limits)

**Conclusion**: SQLite is perfectly suitable for this dataset.

## New Architecture

### 1. Backend (`backend/`)

#### Data Sync Module (`sync/`)
- **download_faa_data.py**: Downloads and extracts FAA ZIP file
  - Handles retries, checksums, incremental updates
  - Extracts to `data/FAA_Database/`
- **import_to_db.py**: Parses CSVs and imports to SQLite
  - Uses SQLAlchemy ORM for cleaner code
  - Handles incremental updates (track via file metadata table)
  - Links aircraft → aircraft_model → engine relationships
- **database.py**: SQLite database initialization and schema
  - SQLite database at `data/faa_aircraft.db`
  - Schema mirrors current MySQL structure
  - Includes indexes for performance

#### API Server (`api/`)
- **main.py**: FastAPI application
  - JSON endpoints: `/api/v1/aircraft/{tail_number}`
  - cURL-friendly text endpoints: `/api/v1/curl/aircraft/{tail_number}`
  - Health check: `/api/health`
  - Swagger/OpenAPI docs at `/docs` (customized to match AirPuff color scheme)
- **models.py**: Pydantic models for API responses
- **database.py**: Database connection and queries

#### Systemd Integration
- **systemd/**: Timer and service units for automated sync
  - `faa-sync.timer`: Runs 3-4 times daily
  - `faa-sync.service`: Executes sync script

### 2. Frontend (`frontend/`)

#### Static Assets
- **index.html**: Main search interface
- **styles.css**: Modern styling (maintains AirPuff color scheme, enhanced)
- **script.js**: API integration and UI handling

#### Design Improvements
- Keep AirPuff logo and color scheme as baseline
- Add subtle animations and transitions
- Improve mobile responsiveness
- Add search history/localStorage
- Better error handling and loading states
- Enhanced data visualization (formatted dates, readable status codes)

### 3. Project Structure

```
tailnumberlookup/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py         # Pydantic models
│   │   └── database.py       # DB queries
│   ├── sync/
│   │   ├── __init__.py
│   │   ├── download_faa_data.py
│   │   ├── import_to_db.py
│   │   └── database.py       # DB schema/init
│   └── __init__.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── systemd/
│   ├── faa-sync.service
│   └── faa-sync.timer
├── data/                     # .gitignored
│   ├── FAA_Database/         # Extracted CSVs
│   └── faa_aircraft.db       # SQLite database
├── requirements.txt
├── .env.example
├── README.md
└── LICENSE
```

## Implementation Steps

### Phase 1: Backend Foundation
1. Set up SQLite schema (migrate from MySQL)
2. Create database initialization script
3. Implement download script
4. Implement import script with incremental updates
5. Test data sync end-to-end

### Phase 2: API Development
1. Set up FastAPI application structure
2. Implement JSON API endpoint (`/api/v1/aircraft/{tail_number}`)
3. Implement cURL-friendly text API endpoint (`/api/v1/curl/aircraft/{tail_number}`)
4. Add health check endpoint
5. Customize Swagger UI to match AirPuff color scheme
6. Add error handling and validation

### Phase 3: Frontend
1. Create modern HTML structure
2. Style with enhanced AirPuff theme
3. Implement JavaScript API integration
4. Add search functionality and result display
5. Improve UX with loading states and error messages

### Phase 4: Systemd Integration
1. Create systemd timer unit
2. Create systemd service unit
3. Test automated sync

### Phase 5: Testing & Documentation
1. Test all endpoints
2. Test data sync process
3. Update README with setup instructions
4. Document API endpoints

## Technical Decisions

### SQLite vs MySQL
- **SQLite chosen** because:
  - Dataset size is manageable (~60-120 MB)
  - No need for concurrent writes (single sync process)
  - Simpler deployment (no separate DB server)
  - Easier backup (single file)
  - Performance sufficient for read-heavy workload

### API Formats
- **JSON**: Primary format for web frontend and API consumers
- **cURL Text Format**: Human-readable format for cURL/CLI usage
  - Endpoint: `/api/v1/curl/aircraft/{tail_number}`
  - Example: `curl https://api.example.com/api/v1/curl/aircraft/N12345`
- **Swagger Documentation**: Interactive API docs at `/docs` with AirPuff-themed styling

### Update Frequency
- **3-4 times daily**: Balance between freshness and server load
- Systemd timer allows flexible scheduling
- Incremental updates (only process changed files)

### AirPuff Branding
- Maintain logo and color scheme from reference
- Enhance with modern CSS features (gradients, shadows, transitions)
- Improve typography and spacing
- Add subtle animations for better UX

## Dependencies

### Backend
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: ORM for database
- `pydantic`: Data validation
- `python-dotenv`: Environment variables
- `requests`: HTTP client for downloads
- `pytz`: Timezone handling

### Frontend
- No external dependencies (vanilla JS)
- Optional: Consider adding a lightweight CSS framework if needed

## Security Considerations

- Environment variables for sensitive config
- Input validation on all API endpoints
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting (consider for production)
- HTTPS (production deployment)

## Future Enhancements (Post-Rewrite)

- Search by owner name, model, manufacturer
- Export functionality (CSV, JSON)
- API authentication (if needed)
- Caching layer for frequently accessed records
- Admin dashboard for monitoring sync status

