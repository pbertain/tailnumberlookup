"""
Pydantic models for API responses.
"""
from typing import Optional
from pydantic import BaseModel, Field


class AircraftResponse(BaseModel):
    """Response model for aircraft data."""
    n_number: str = Field(..., alias="n_number", description="Aircraft tail number (N-Number)")
    serial_number: Optional[str] = Field(None, description="Serial number")
    mfr_model_code: Optional[str] = Field(None, description="Manufacturer model code")
    engine_mfr_model_code: Optional[str] = Field(None, description="Engine manufacturer model code")
    year_mfr: Optional[int] = Field(None, description="Year manufactured")
    type_registrant: Optional[str] = Field(None, description="Type of registrant")
    registrant_name: Optional[str] = Field(None, description="Registrant name")
    street1: Optional[str] = Field(None, description="Street address line 1")
    street2: Optional[str] = Field(None, description="Street address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="Zip code")
    registrant_region: Optional[str] = Field(None, description="Registrant region")
    county_mail_code: Optional[str] = Field(None, description="County code")
    country_mail_code: Optional[str] = Field(None, description="Country code")
    last_activity_date: Optional[str] = Field(None, description="Last activity date")
    cert_issue_date: Optional[str] = Field(None, description="Certificate issue date")
    cert_requested: Optional[str] = Field(None, description="Certification requested")
    type_aircraft: Optional[str] = Field(None, description="Type of aircraft")
    type_engine: Optional[str] = Field(None, description="Type of engine")
    status_code: Optional[str] = Field(None, description="Status code")
    mode_s_code: Optional[str] = Field(None, description="Mode S code")
    fractional_ownership: Optional[str] = Field(None, description="Fractional ownership indicator")
    airworthiness_date: Optional[str] = Field(None, description="Airworthiness date")
    other_name_1: Optional[str] = Field(None, description="Other name 1")
    other_name_2: Optional[str] = Field(None, description="Other name 2")
    other_name_3: Optional[str] = Field(None, description="Other name 3")
    other_name_4: Optional[str] = Field(None, description="Other name 4")
    other_name_5: Optional[str] = Field(None, description="Other name 5")
    expiration_date: Optional[str] = Field(None, description="Expiration date")
    unique_id: Optional[str] = Field(None, description="Unique ID")
    kit_mfr: Optional[str] = Field(None, description="Kit manufacturer")
    kit_model_code: Optional[str] = Field(None, description="Kit model code")
    mode_s_code_hex: Optional[str] = Field(None, description="Mode S code (hex)")
    
    # Joined data from aircraft_model table
    aircraft_manufacturer_name: Optional[str] = Field(None, description="Aircraft manufacturer name")
    aircraft_model_name: Optional[str] = Field(None, description="Aircraft model name")
    number_of_engines: Optional[int] = Field(None, description="Number of engines")
    number_of_seats: Optional[int] = Field(None, description="Number of seats")
    
    # Joined data from engine table
    engine_manufacturer_name: Optional[str] = Field(None, description="Engine manufacturer name")
    engine_model_name: Optional[str] = Field(None, description="Engine model name")
    horsepower: Optional[int] = Field(None, description="Engine horsepower")
    pounds_of_thrust: Optional[int] = Field(None, description="Engine thrust (lbs)")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "n_number": "N12345",
                "serial_number": "123456",
                "registrant_name": "John Doe",
                "city": "Los Angeles",
                "state": "CA",
                "aircraft_manufacturer_name": "Cessna",
                "aircraft_model_name": "172"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    database: str
    timestamp: str

