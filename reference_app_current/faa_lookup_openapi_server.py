# Sample uvicorn commands:
# To run this API, use: `uvicorn faa_lookup_openapi_server:app --reload --port 5000`
# Or: `uvicorn faa_lookup_openapi_server:app --reload --host 0.0.0.0 --port 5000`

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
import logging
import os
from pydantic import BaseModel
import pymysql
import time
from typing import Optional

# Version number for the script
SCRIPT_VERSION = "23"

# Setup logging for access
access_logger = logging.getLogger("fastapi_access")
access_handler = logging.FileHandler("/var/log/fastapi/access.log")
access_handler.setLevel(logging.INFO)
access_format = logging.Formatter(
    'date="%(asctime)s" vhost="%(hostname)s" sip="%(server_ip)s" port="%(server_port)s" '
    'proto="HTTP/1.1" method="%(method)s" url="%(path)s" rcode="%(status_code)s" '
    'rsize="%(bytes_sent)s" rtime="%(request_time).4f" ua="%(user_agent)s" '
    'forwarded="%(forwarded_for)s"'
)
access_handler.setFormatter(access_format)
access_logger.addHandler(access_handler)
access_logger.setLevel(logging.INFO)

# Setup logging for errors
error_logger = logging.getLogger("fastapi_error")
error_handler = logging.FileHandler("/var/log/fastapi/error.log")
error_handler.setLevel(logging.ERROR)
error_format = logging.Formatter('%(asctime)s - %(message)s')
error_handler.setFormatter(error_format)
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)

app = FastAPI(
    title="FAA Aircraft Lookup API",
    description="API to lookup aircraft information.",
    version=SCRIPT_VERSION
)

# Middleware to capture request details
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Custom log details without 'asctime' (handled by the formatter)
    access_logger.info("", extra={
        "hostname": request.client.host,
        "server_ip": request.scope.get("server")[0],
        "server_port": request.scope.get("server")[1],
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "bytes_sent": response.headers.get("content-length", 0),
        "request_time": process_time,
        "user_agent": request.headers.get("user-agent", ""),
        "forwarded_for": request.headers.get("x-forwarded-for", request.client.host),
    })
    return response

@app.exception_handler(Exception)
async def log_exceptions(request: Request, exc: Exception):
    error_logger.error(f"Exception: {exc} at URL: {request.url}")
    return Response("Internal server error", status_code=500)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific domains as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "faa_user",  # Replace with your MySQL username
    "password": os.getenv("FAA_DB_PASSWORD"),  # Ensure FAA_DB_PASSWORD is set
    "database": "faa_aircraft"
}

# Aircraft response model
class AircraftResponseModel(BaseModel):
    n_number: str
    serial_number: Optional[str] = None
    aircraft_manufacturer_name: Optional[str] = None
    aircraft_model_name: Optional[str] = None
    engine_manufacturer: Optional[str] = None
    engine_model: Optional[str] = None
    engine_horsepower: Optional[int] = None
    mfr_model_code: Optional[str] = None
    model_name: Optional[str] = None  # New field for translated model name
    engine_mfr_model_code: Optional[str] = None
    year_mfr: Optional[int] = None
    type_registrant: Optional[str] = None
    registrant_name: Optional[str] = None
    street1: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    registrant_region: Optional[str] = None
    county_mail_code: Optional[str] = None
    country_mail_code: Optional[str] = None
    last_activity_date: Optional[str] = None
    certificate_issue_date: Optional[str] = None
    type_aircraft: Optional[str] = None
    type_engine: Optional[str] = None
    status_code: Optional[str] = None
    mode_s_code: Optional[str] = None
    fractional_ownership: Optional[str] = None
    airworthiness_date: Optional[str] = None
    unique_id: Optional[str] = None
    expiration_date: Optional[str] = None
    model_code: Optional[str] = None
    engine_code: Optional[str] = None

    class Config:
        protected_namespaces = ()  # Disables the protected namespaces warning

# Route to serve the input form HTML page at the root
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, n_number: Optional[str] = None):
    # HTML interface with a search form and API documentation link
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FAA Aircraft Lookup</title>
        <link rel="stylesheet" href="https://www.airpuff.info/web/css/airpuff.css">
    </head>
    <body class="body_main">
        <header class="basic">
            <a href="https://www.airpuff.info/">
                <img width=50% height="auto" src="https://www.airpuff.info/images/tnl-logo-dark.png" alt="AirPuff Logo">
            </a>
            <h1 class="header-title">AirPuff <br>Tail Number Lookup</h1>
        </header>
        <main>
            <div class="header">Welcome to the AirPuff Aircraft Tail Number Lookup API</div>
            <div class="paragraph">
                <p>This API allows you to search for aircraft information by entering an N-Number.</p>
                
                <!-- Search Form -->
                <form method="get" action="/">
                    <label for="n_number" class="large-label">Enter N-Number:</label>
                    <input type="text" id="n_number" name="n_number" required>
                    <button type="submit">Search</button>
                </form>
                
                <!-- Button for API Documentation -->
                <p><a href="/docs" class="button-link">Access the API Documentation</a></p>
                
                <!-- Results Section -->
                <div id="result">{result}</div>
            </div>
        </main>
        <footer class="footer">
            <p>Powered by AirPuff.</p>
        </footer>
    </body>
    </html>
    """

    # Initialize empty result content
    result = ""

    # If the n_number is provided, process it by stripping any leading 'N' character
    if n_number:
        n_number = n_number.lstrip('Nn')  # Remove leading 'N' or 'n' if present
        try:
            # Execute the database query
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """
                    SELECT aircraft.*, aircraft_model.manufacturer_name AS aircraft_manufacturer_name,
                           aircraft_model.model_name AS aircraft_model_name, 
                           engine.manufacturer_name AS engine_manufacturer, 
                           engine.engine_model_name AS engine_model, 
                           engine.horsepower AS engine_horsepower
                    FROM aircraft
                    LEFT JOIN aircraft_model ON aircraft.mfr_model_code = aircraft_model.model_code
                    LEFT JOIN engine ON aircraft.engine_mfr_model_code = engine.engine_code
                    WHERE aircraft.n_number = %s
                """
                cursor.execute(sql_query, (n_number,))
                row = cursor.fetchone()

                # Format results as HTML or show an error if no data
                if row:
                    # Convert datetime fields to string
                    for date_field in ["last_activity_date", "certificate_issue_date", "airworthiness_date", "expiration_date"]:
                        if date_field in row and row[date_field]:
                            row[date_field] = row[date_field].strftime("%Y-%m-%d")
                    result = format_as_vertical_table(row)
                else:
                    result = "<p>Aircraft data not found for the specified N-Number.</p>"
        except Exception as e:
            result = f"<p>Error retrieving data: {e}</p>"

    # Render the final HTML response with the result embedded
    return HTMLResponse(content=html_content.format(result=result))

@app.get("/aircraft/{n_number}", response_model=AircraftResponseModel)
async def get_aircraft_by_n_number(n_number: str):
    n_number = n_number.lstrip("Nn")  # Strip any leading 'N' or 'n'
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql_query = """
                SELECT aircraft.*, aircraft_model.manufacturer_name AS aircraft_manufacturer_name,
                       aircraft_model.model_name AS aircraft_model_name, 
                       engine.manufacturer_name AS engine_manufacturer, 
                       engine.engine_model_name AS engine_model, 
                       engine.horsepower AS engine_horsepower
                FROM aircraft
                LEFT JOIN aircraft_model ON aircraft.mfr_model_code = aircraft_model.model_code
                LEFT JOIN engine ON aircraft.engine_mfr_model_code = engine.engine_code
                WHERE aircraft.n_number = %s
            """
            cursor.execute(sql_query, (n_number,))
            result = cursor.fetchone()
            if result:
                # Convert datetime fields to string if present
                for date_field in ["last_activity_date", "certificate_issue_date", "airworthiness_date", "expiration_date"]:
                    if date_field in result and result[date_field]:
                        result[date_field] = result[date_field].strftime("%Y-%m-%d")
                return AircraftResponseModel(**result)
            else:
                raise HTTPException(status_code=404, detail="Aircraft not found")
    finally:
        connection.close()

def format_as_vertical_table(data):
    fields_to_show = {
        "n_number": "Tail Number",
        "serial_number": "Serial Number",
        "aircraft_manufacturer_name": "Aircraft Manufacturer",
        "aircraft_model_name": "Aircraft Model",
        "engine_manufacturer": "Engine Manufacturer",
        "engine_model": "Engine Model",
        "engine_horsepower": "Horsepower",
        "mfr_model_code": "Manufacturer Model Code",
        "year_mfr": "Year Manufactured",
        "type_registrant": "Type of Registrant",
        "registrant_name": "Registrant Name",
        "street1": "Street 1",
        "street2": "Street 2",
        "city": "City",
        "state": "State",
        "zip_code": "ZIP Code",
        "registrant_region": "Region",
        "county_mail_code": "County",
        "country_mail_code": "Country",
        "last_activity_date": "Last Activity Date",
        "certificate_issue_date": "Certificate Issue Date",
        "airworthiness_date": "Airworthiness Date",
        "expiration_date": "Expiration Date"
    }

    table = "<table class='styled-table'><tbody>"
    for key, label in fields_to_show.items():
        value = data.get(key, "")
        table += f"<tr><th>{label}</th><td>{value}</td></tr>"
    table += "</tbody></table>"

    return table

