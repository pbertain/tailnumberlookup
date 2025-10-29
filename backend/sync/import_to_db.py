"""
Import FAA CSV data into SQLite database with incremental update support.
"""
import csv
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

from .database import get_db_path, init_database


def truncate_string(value: Optional[str], max_length: int) -> Optional[str]:
    """Truncate string to avoid exceeding field length."""
    if not value:
        return None
    return value[:max_length].strip() or None


def calculate_md5(file_path: Path) -> str:
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def has_file_changed(cursor: sqlite3.Cursor, file_name: str, file_path: Path) -> bool:
    """
    Check if a file has changed by comparing MD5 and modification time.
    Returns True if file needs to be imported, False otherwise.
    """
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return False
    
    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    file_md5sum = calculate_md5(file_path)
    
    cursor.execute(
        "SELECT file_create_date, file_md5sum FROM file_metadata WHERE file_name = ?",
        (file_name,)
    )
    result = cursor.fetchone()
    
    if result:
        db_mtime = datetime.fromisoformat(result[0]) if result[0] else None
        db_md5sum = result[1]
        
        if db_mtime == file_mtime and db_md5sum == file_md5sum:
            return False
        else:
            # Update metadata
            cursor.execute(
                "UPDATE file_metadata SET file_create_date = ?, file_md5sum = ? WHERE file_name = ?",
                (file_mtime.isoformat(), file_md5sum, file_name)
            )
    else:
        # Insert new metadata
        cursor.execute(
            "INSERT INTO file_metadata (file_name, file_create_date, file_md5sum) VALUES (?, ?, ?)",
            (file_name, file_mtime.isoformat(), file_md5sum)
        )
    
    cursor.connection.commit()
    return True


def load_aircraft_model_data(cursor: sqlite3.Cursor, file_path: Path) -> None:
    """Load aircraft model data from ACFTREF.txt."""
    print(f"Loading aircraft model data from {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        count = 0
        
        for row in csv_reader:
            model_code = truncate_string(row.get('CODE', ''), 7)
            if not model_code:
                continue
            
            cursor.execute("""
                INSERT OR REPLACE INTO aircraft_model (
                    model_code, manufacturer_name, model_name, type_aircraft, type_engine,
                    aircraft_category_code, builder_certification_code, number_of_engines,
                    number_of_seats, aircraft_weight_category, aircraft_cruising_speed,
                    tc_data_sheet, tc_data_holder
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model_code,
                truncate_string(row.get('MFR', ''), 30),
                truncate_string(row.get('MODEL', ''), 20),
                truncate_string(row.get('TYPE-ACFT', ''), 1),
                truncate_string(row.get('TYPE-ENG', ''), 2),
                truncate_string(row.get('AC-CAT', ''), 1),
                truncate_string(row.get('BUILD-CERT-IND', ''), 1),
                int(row.get('NO-ENG', '').strip() or 0),
                int(row.get('NO-SEATS', '').strip() or 0),
                truncate_string(row.get('AC-WEIGHT', ''), 7),
                int(row.get('SPEED', '').strip() or 0),
                truncate_string(row.get('TC-DATA-SHEET', ''), 15),
                truncate_string(row.get('TC-DATA-HOLDER', ''), 50)
            ))
            count += 1
            
            if count % 10000 == 0:
                cursor.connection.commit()
                print(f"  Processed {count} aircraft models...")
        
        cursor.connection.commit()
        print(f"  Loaded {count} aircraft models.")


def load_engine_data(cursor: sqlite3.Cursor, file_path: Path) -> None:
    """Load engine data from ENGINE.txt."""
    print(f"Loading engine data from {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        count = 0
        
        for row in csv_reader:
            engine_code = truncate_string(row.get('CODE', ''), 5)
            if not engine_code:
                continue
            
            cursor.execute("""
                INSERT OR REPLACE INTO engine (
                    engine_code, manufacturer_name, engine_model_name, type_engine,
                    horsepower, pounds_of_thrust
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                engine_code,
                truncate_string(row.get('MFR', ''), 50),
                truncate_string(row.get('MODEL', ''), 13),
                truncate_string(row.get('TYPE', ''), 2),
                int(row.get('HORSEPOWER', '').strip() or 0),
                int(row.get('THRUST', '').strip() or 0)
            ))
            count += 1
            
            if count % 5000 == 0:
                cursor.connection.commit()
                print(f"  Processed {count} engines...")
        
        cursor.connection.commit()
        print(f"  Loaded {count} engines.")


def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Parse date from FAA format (YYYYMMDD) to ISO format (YYYY-MM-DD)."""
    if not date_str or not date_str.strip():
        return None
    
    try:
        date_str = date_str.strip()
        if len(date_str) == 8:
            year = date_str[0:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{year}-{month}-{day}"
    except Exception:
        pass
    
    return None


def load_aircraft_data(cursor: sqlite3.Cursor, file_path: Path) -> None:
    """Load aircraft registration data from MASTER.txt."""
    print(f"Loading aircraft data from {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        count = 0
        
        for row in csv_reader:
            n_number = truncate_string(row.get('N-NUMBER', ''), 5)
            if not n_number:
                continue
            
            cursor.execute("""
                INSERT OR REPLACE INTO aircraft (
                    n_number, serial_number, mfr_model_code, engine_mfr_model_code, year_mfr,
                    type_registrant, registrant_name, street1, street2, city, state, zip_code,
                    registrant_region, county_mail_code, country_mail_code, last_activity_date,
                    cert_issue_date, cert_requested, type_aircraft, type_engine, status_code,
                    mode_s_code, fractional_ownership, airworthiness_date, other_name_1,
                    other_name_2, other_name_3, other_name_4, other_name_5, expiration_date,
                    unique_id, kit_mfr, kit_model_code, mode_s_code_hex
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                n_number,
                truncate_string(row.get('SERIAL NUMBER', ''), 30),
                truncate_string(row.get('MFR MDL CODE', ''), 7),
                truncate_string(row.get('ENG MFR MDL', ''), 5),
                int(row.get('YEAR MFR', '').strip() or 0) if row.get('YEAR MFR', '').strip() else None,
                truncate_string(row.get('TYPE REGISTRANT', ''), 1),
                truncate_string(row.get('NAME', ''), 50),
                truncate_string(row.get('STREET', ''), 33),
                truncate_string(row.get('STREET2', ''), 33),
                truncate_string(row.get('CITY', ''), 18),
                truncate_string(row.get('STATE', ''), 2),
                truncate_string(row.get('ZIP CODE', ''), 10),
                truncate_string(row.get('REGION', ''), 1),
                truncate_string(row.get('COUNTY', ''), 3),
                truncate_string(row.get('COUNTRY', ''), 2),
                parse_date(row.get('LAST ACTION DATE', '')),
                parse_date(row.get('CERT ISSUE DATE', '')),
                truncate_string(row.get('CERTIFICATION', ''), 10),
                truncate_string(row.get('TYPE AIRCRAFT', ''), 1),
                truncate_string(row.get('TYPE ENGINE', ''), 2),
                truncate_string(row.get('STATUS CODE', ''), 2),
                truncate_string(row.get('MODE S CODE', ''), 8),
                truncate_string(row.get('FRACT OWNER', ''), 1),
                parse_date(row.get('AIR WORTH DATE', '')),
                truncate_string(row.get('OTHER NAMES(1)', ''), 50),
                truncate_string(row.get('OTHER NAMES(2)', ''), 50),
                truncate_string(row.get('OTHER NAMES(3)', ''), 50),
                truncate_string(row.get('OTHER NAMES(4)', ''), 50),
                truncate_string(row.get('OTHER NAMES(5)', ''), 50),
                parse_date(row.get('EXPIRATION DATE', '')),
                truncate_string(row.get('UNIQUE ID', ''), 8),
                truncate_string(row.get('KIT MFR', ''), 30),
                truncate_string(row.get(' KIT MODEL', ''), 20),
                truncate_string(row.get('MODE S CODE HEX', ''), 10)
            ))
            count += 1
            
            if count % 50000 == 0:
                cursor.connection.commit()
                print(f"  Processed {count} aircraft...")
        
        cursor.connection.commit()
        print(f"  Loaded {count} aircraft.")


def load_data_if_changed(
    cursor: sqlite3.Cursor,
    file_name: str,
    file_path: Path,
    load_function: Callable
) -> bool:
    """Load data if the file has changed."""
    if has_file_changed(cursor, file_name, file_path):
        print(f"Changes detected for {file_name}. Loading data...")
        load_function(cursor, file_path)
        return True
    else:
        print(f"No changes detected for {file_name}, skipping load.")
        return False


def import_faa_data() -> None:
    """Main function to import FAA data into the database."""
    print("Initializing database...")
    conn = init_database()
    cursor = conn.cursor()
    
    # Get data directory
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "FAA_Database"
    
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}")
        print("Please run download_faa_data.py first.")
        return
    
    # Define file paths
    master_file = data_dir / 'MASTER.txt'
    acftref_file = data_dir / 'ACFTREF.txt'
    engine_file = data_dir / 'ENGINE.txt'
    
    # Load data for each file
    models_updated = load_data_if_changed(
        cursor, 'Aircraft Reference File', acftref_file, load_aircraft_model_data
    )
    engines_updated = load_data_if_changed(
        cursor, 'Engine Reference File', engine_file, load_engine_data
    )
    aircraft_updated = load_data_if_changed(
        cursor, 'Aircraft Registration Master File', master_file, load_aircraft_data
    )
    
    conn.commit()
    conn.close()
    
    if any([models_updated, engines_updated, aircraft_updated]):
        print("\n✓ Database update complete!")
    else:
        print("\n✓ Database is already up-to-date.")


if __name__ == "__main__":
    import_faa_data()

