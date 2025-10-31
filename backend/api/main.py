"""
FastAPI application for Tail Number Lookup API.
"""
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.openapi.utils import get_openapi
from datetime import datetime
from pathlib import Path

from .database import get_aircraft_by_tail_number, check_database_health, get_db_connection
from .models import AircraftResponse, HealthResponse
from .debug import router as debug_router


# Create FastAPI app
app = FastAPI(
    title="Tail Number Lookup API",
    description="API for querying FAA aircraft registration data by tail number (N-Number)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include debug router
app.include_router(debug_router)


def format_aircraft_text_vital(aircraft_data: dict) -> str:
    """Format aircraft data as plain text with vital stats (for web UI display)."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"AIRCRAFT INFORMATION - {aircraft_data.get('n_number', 'N/A')}")
    lines.append("=" * 60)
    lines.append("")
    
    # Vital stats (what would be shown in web UI)
    vital_fields = {
        'n_number': 'N-Number',
        'serial_number': 'Serial Number',
        'aircraft_manufacturer_name': 'Aircraft Manufacturer',
        'aircraft_model_name': 'Aircraft Model',
        'year_mfr': 'Year Manufactured',
        'number_of_engines': 'Number of Engines',
        'number_of_seats': 'Number of Seats',
        'engine_manufacturer_name': 'Engine Manufacturer',
        'engine_model_name': 'Engine Model',
        'horsepower': 'Horsepower',
        'pounds_of_thrust': 'Thrust (lbs)',
        'registrant_name': 'Registrant Name',
        'street1': 'Street Address',
        'street2': 'Street Address 2',
        'city': 'City',
        'state': 'State',
        'zip_code': 'Zip Code',
        'country_mail_code': 'Country Code',
        'last_activity_date': 'Last Activity Date',
        'cert_issue_date': 'Certificate Issue Date',
        'cert_requested': 'Certification Requested',
        'type_aircraft': 'Aircraft Type',
        'type_engine': 'Engine Type',
        'status_code': 'Status Code',
        'airworthiness_date': 'Airworthiness Date',
        'expiration_date': 'Expiration Date',
        'unique_id': 'Unique ID',
        'kit_mfr': 'Kit Manufacturer',
        'kit_model_code': 'Kit Model Code',
        'mode_s_code_hex': 'Mode S Code (Hex)'
    }
    
    for key, label in vital_fields.items():
        value = aircraft_data.get(key)
        if value is not None and value != "":
            # Format dates nicely if they're date strings
            if 'date' in key and value:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    value = dt.strftime('%B %d, %Y')
                except:
                    pass
            lines.append(f"{label:.<30} {value}")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_aircraft_text(aircraft_data: dict) -> str:
    """Format aircraft data as plain text for cURL endpoint."""
    # Use vital stats format for consistency
    return format_aircraft_text_vital(aircraft_data)


# Custom OpenAPI schema with AirPuff theming
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom info for theming
    openapi_schema["info"]["x-logo"] = {
        "url": "https://airpuff.info/web/icons/airpuff-logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Custom Swagger UI HTML with AirPuff styling
swagger_ui_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Tail Number Lookup API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <link rel="icon" type="image/png" href="https://airpuff.info/web/icons/airpuff-logo.png" />
    <style>
        /* AirPuff-inspired color scheme */
        :root {
            --airpuff-primary: #1e3a5f;
            --airpuff-secondary: #2d5aa0;
            --airpuff-accent: #ffd700;
            --airpuff-bg: #f5f5f5;
            --airpuff-text: #333;
        }
        
        /* Override Swagger UI colors */
        .swagger-ui .topbar {
            background-color: var(--airpuff-primary);
            border-bottom: 3px solid var(--airpuff-accent);
        }
        
        .swagger-ui .topbar .download-url-wrapper {
            display: none;
        }
        
        .swagger-ui .info .title {
            color: var(--airpuff-primary);
        }
        
        .swagger-ui .btn.execute {
            background-color: var(--airpuff-secondary);
        }
        
        .swagger-ui .btn.execute:hover {
            background-color: var(--airpuff-primary);
        }
        
        .swagger-ui .scheme-container {
            background-color: var(--airpuff-bg);
            border-top: 2px solid var(--airpuff-accent);
        }
        
        /* Logo styling */
        .swagger-ui .topbar-wrapper img {
            content: url('https://airpuff.info/web/icons/airpuff-logo.png');
            max-height: 40px;
            padding: 5px;
        }
        
        body {
            background-color: var(--airpuff-bg);
        }
        
        .swagger-ui .info {
            margin: 20px 0;
        }
        
        .swagger-ui .opblock.opblock-get .opblock-summary {
            border-color: var(--airpuff-secondary);
        }
        
        .swagger-ui .opblock.opblock-get .opblock-summary-method {
            background-color: var(--airpuff-secondary);
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                layout: "StandaloneLayout",
                deepLinking: true,
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1
            });
        };
    </script>
</body>
</html>
"""


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with AirPuff theming."""
    return HTMLResponse(content=swagger_ui_html)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    db_healthy = check_database_health()
    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        database="connected" if db_healthy else "disconnected",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/v1/stats")
async def get_stats():
    """
    Get database statistics for frontend display.
    Returns counts, sample data, and database file information.
    """
    from backend.api.database import get_db_path
    from pathlib import Path
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM aircraft")
        aircraft_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM aircraft_model")
        model_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM engine")
        engine_count = cursor.fetchone()[0]
        
        # Sample tail numbers
        cursor.execute("SELECT n_number FROM aircraft ORDER BY n_number LIMIT 10")
        sample_numbers = [row[0] for row in cursor.fetchall()]
        
        # Database file info
        db_path = get_db_path()
        db_size = 0
        page_count = 0
        page_size = 0
        if db_path.exists():
            stat = db_path.stat()
            db_size = stat.st_size / (1024 * 1024)  # Size in MB
            
            # Get SQLite page info
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
        
        # Get last sync time from file_metadata
        cursor.execute("SELECT MAX(file_create_date) FROM file_metadata")
        last_sync_result = cursor.fetchone()
        last_sync = last_sync_result[0] if last_sync_result[0] else None
        
        # Get SQLite version
        cursor.execute("SELECT sqlite_version()")
        sqlite_version = cursor.fetchone()[0]
        
        return {
            "database_type": "SQLite",
            "sqlite_version": sqlite_version,
            "total_records": aircraft_count,
            "model_records": model_count,
            "engine_records": engine_count,
            "database_size_mb": round(db_size, 2),
            "page_count": page_count,
            "page_size_bytes": page_size,
            "database_file": str(db_path),
            "sample_tail_numbers": sample_numbers,
            "last_sync": last_sync,
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        conn.close()


@app.get("/api/v1/aircraft/{tail_number}", response_model=AircraftResponse)
async def get_aircraft_json(tail_number: str):
    """
    Get aircraft information by tail number in JSON format.
    
    Args:
        tail_number: Aircraft tail number (N-Number), e.g., "N12345" or "12345"
    
    Returns:
        AircraftResponse with all available aircraft data
    """
    aircraft_data = get_aircraft_by_tail_number(tail_number)
    
    if not aircraft_data:
        raise HTTPException(
            status_code=404,
            detail=f"Aircraft with tail number {tail_number} not found"
        )
    
    return AircraftResponse(**aircraft_data)


@app.get("/api/v1/curl/aircraft/{tail_number}", response_class=PlainTextResponse)
async def get_aircraft_text(tail_number: str):
    """
    Get aircraft information by tail number in plain text format (for cURL).
    
    Args:
        tail_number: Aircraft tail number (N-Number), e.g., "N12345" or "12345"
    
    Returns:
        Plain text formatted aircraft data
    """
    aircraft_data = get_aircraft_by_tail_number(tail_number)
    
    if not aircraft_data:
        raise HTTPException(
            status_code=404,
            detail=f"Aircraft with tail number {tail_number} not found"
        )
    
    text_output = format_aircraft_text(aircraft_data)
    return PlainTextResponse(content=text_output)


@app.get("/curl/v1/aircraft/{tail_number}", response_class=PlainTextResponse)
async def get_aircraft_curl(tail_number: str):
    """
    Get aircraft information by tail number in plain text format (alternative endpoint).
    Case-insensitive, optional N prefix.
    
    Args:
        tail_number: Aircraft tail number (N-Number), e.g., "N538CD", "538CD", "n538cd", "538cd"
                    All equivalent - case-insensitive with optional N prefix
    
    Returns:
        Plain text formatted aircraft data with vital stats
    """
    aircraft_data = get_aircraft_by_tail_number(tail_number)
    
    if not aircraft_data:
        raise HTTPException(
            status_code=404,
            detail=f"Aircraft with tail number {tail_number} not found"
        )
    
    text_output = format_aircraft_text_vital(aircraft_data)
    return PlainTextResponse(content=text_output)


# Stats HTML pages
@app.get("/debug/stats", response_class=HTMLResponse)
async def debug_stats_html():
    """Serve debug stats HTML page."""
    stats_path = Path(__file__).parent.parent.parent / "frontend" / "debug" / "stats.html"
    if stats_path.exists():
        return HTMLResponse(content=stats_path.read_text())
    raise HTTPException(status_code=404, detail="Stats page not found")


@app.get("/stats", response_class=HTMLResponse)
async def stats_html():
    """Serve stats HTML page."""
    stats_path = Path(__file__).parent.parent.parent / "frontend" / "stats.html"
    if stats_path.exists():
        return HTMLResponse(content=stats_path.read_text())
    raise HTTPException(status_code=404, detail="Stats page not found")


# Mount static files for frontend (if exists)
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=49080)

