"""
SQLite database schema and initialization for FAA aircraft data.
"""
import sqlite3
import os
from pathlib import Path


def get_db_path() -> Path:
    """Get the path to the SQLite database file."""
    # Get project root (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "faa_aircraft.db"


def init_database(db_path: Path = None) -> sqlite3.Connection:
    """
    Initialize the SQLite database with the schema.
    Creates tables if they don't exist.
    """
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    
    cursor = conn.cursor()
    
    # Aircraft Table (Master Registration Data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aircraft (
            n_number TEXT(6) PRIMARY KEY,
            serial_number TEXT(30),
            mfr_model_code TEXT(7),
            engine_mfr_model_code TEXT(5),
            year_mfr INTEGER,
            type_registrant TEXT(1),
            registrant_name TEXT(50),
            street1 TEXT(33),
            street2 TEXT(33),
            city TEXT(18),
            state TEXT(2),
            zip_code TEXT(10),
            registrant_region TEXT(1),
            county_mail_code TEXT(3),
            country_mail_code TEXT(2),
            last_activity_date DATE,
            cert_issue_date DATE,
            cert_requested TEXT(10),
            type_aircraft TEXT(1),
            type_engine TEXT(2),
            status_code TEXT(2),
            mode_s_code TEXT(8),
            fractional_ownership TEXT(1),
            airworthiness_date DATE,
            other_name_1 TEXT(50),
            other_name_2 TEXT(50),
            other_name_3 TEXT(50),
            other_name_4 TEXT(50),
            other_name_5 TEXT(50),
            expiration_date DATE,
            unique_id TEXT(8),
            kit_mfr TEXT(30),
            kit_model_code TEXT(20),
            mode_s_code_hex TEXT(10)
        )
    """)
    
    # Aircraft Reference Table (ACFTREF.txt Data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aircraft_model (
            model_code TEXT(7) PRIMARY KEY,
            manufacturer_name TEXT(30),
            model_name TEXT(20),
            type_aircraft TEXT(1),
            type_engine TEXT(2),
            aircraft_category_code TEXT(1),
            builder_certification_code TEXT(1),
            number_of_engines INTEGER,
            number_of_seats INTEGER,
            aircraft_weight_category TEXT(7),
            aircraft_cruising_speed INTEGER,
            tc_data_sheet TEXT(15),
            tc_data_holder TEXT(50)
        )
    """)
    
    # Engine Reference Table (ENGINE.txt Data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engine (
            engine_code TEXT(5) PRIMARY KEY,
            manufacturer_name TEXT(50),
            engine_model_name TEXT(13),
            type_engine TEXT(2),
            horsepower INTEGER,
            pounds_of_thrust INTEGER
        )
    """)
    
    # File Metadata Table for tracking file information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_metadata (
            file_name TEXT(50) PRIMARY KEY,
            file_create_date DATETIME,
            file_md5sum TEXT(32)
        )
    """)
    
    # Create indexes for performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_last_activity_date 
        ON aircraft (last_activity_date)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cert_requested 
        ON aircraft (cert_requested)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_mfr_model_code 
        ON aircraft (mfr_model_code)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_engine_mfr_model_code 
        ON aircraft (engine_mfr_model_code)
    """)
    
    conn.commit()
    return conn


if __name__ == "__main__":
    # Initialize database when run directly
    print(f"Initializing database at {get_db_path()}")
    conn = init_database()
    print("Database initialized successfully!")
    conn.close()

