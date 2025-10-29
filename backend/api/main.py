"""
FastAPI application for Tail Number Lookup API.
"""
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.openapi.utils import get_openapi
from datetime import datetime
from pathlib import Path

from .database import get_aircraft_by_tail_number, check_database_health
from .models import AircraftResponse, HealthResponse


# Create FastAPI app
app = FastAPI(
    title="Tail Number Lookup API",
    description="API for querying FAA aircraft registration data by tail number (N-Number)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


def format_aircraft_text(aircraft_data: dict) -> str:
    """Format aircraft data as plain text for cURL endpoint."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"AIRCRAFT INFORMATION - {aircraft_data.get('n_number', 'N/A')}")
    lines.append("=" * 60)
    lines.append("")
    
    # Aircraft Identification
    if aircraft_data.get('n_number'):
        lines.append(f"N-Number:             {aircraft_data['n_number']}")
    if aircraft_data.get('serial_number'):
        lines.append(f"Serial Number:         {aircraft_data['serial_number']}")
    if aircraft_data.get('aircraft_manufacturer_name'):
        lines.append(f"Manufacturer:          {aircraft_data['aircraft_manufacturer_name']}")
    if aircraft_data.get('aircraft_model_name'):
        lines.append(f"Model:                 {aircraft_data['aircraft_model_name']}")
    if aircraft_data.get('year_mfr'):
        lines.append(f"Year Manufactured:     {aircraft_data['year_mfr']}")
    
    lines.append("")
    lines.append("-" * 60)
    lines.append("ENGINE INFORMATION")
    lines.append("-" * 60)
    
    if aircraft_data.get('engine_manufacturer_name'):
        lines.append(f"Engine Manufacturer:   {aircraft_data['engine_manufacturer_name']}")
    if aircraft_data.get('engine_model_name'):
        lines.append(f"Engine Model:          {aircraft_data['engine_model_name']}")
    if aircraft_data.get('horsepower'):
        lines.append(f"Horsepower:            {aircraft_data['horsepower']}")
    if aircraft_data.get('pounds_of_thrust'):
        lines.append(f"Thrust (lbs):          {aircraft_data['pounds_of_thrust']}")
    
    lines.append("")
    lines.append("-" * 60)
    lines.append("REGISTRATION INFORMATION")
    lines.append("-" * 60)
    
    if aircraft_data.get('registrant_name'):
        lines.append(f"Registrant Name:       {aircraft_data['registrant_name']}")
    if aircraft_data.get('street1'):
        lines.append(f"Street:                {aircraft_data['street1']}")
    if aircraft_data.get('street2'):
        lines.append(f"Street 2:              {aircraft_data['street2']}")
    if aircraft_data.get('city'):
        lines.append(f"City:                  {aircraft_data['city']}")
    if aircraft_data.get('state'):
        lines.append(f"State:                 {aircraft_data['state']}")
    if aircraft_data.get('zip_code'):
        lines.append(f"Zip Code:              {aircraft_data['zip_code']}")
    if aircraft_data.get('country_mail_code'):
        lines.append(f"Country Code:          {aircraft_data['country_mail_code']}")
    
    lines.append("")
    lines.append("-" * 60)
    lines.append("CERTIFICATION & STATUS")
    lines.append("-" * 60)
    
    if aircraft_data.get('cert_issue_date'):
        lines.append(f"Cert Issue Date:       {aircraft_data['cert_issue_date']}")
    if aircraft_data.get('expiration_date'):
        lines.append(f"Expiration Date:       {aircraft_data['expiration_date']}")
    if aircraft_data.get('status_code'):
        lines.append(f"Status Code:           {aircraft_data['status_code']}")
    if aircraft_data.get('airworthiness_date'):
        lines.append(f"Airworthiness Date:    {aircraft_data['airworthiness_date']}")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


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


# Mount static files for frontend (if exists)
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=49080)

