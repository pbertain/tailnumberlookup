"""
Database connection and query functions for the API.
"""
import sqlite3
from typing import Optional, Dict, Any
from pathlib import Path

from ..sync.database import get_db_path, init_database


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection, initializing if needed."""
    db_path = get_db_path()
    
    # Initialize if database doesn't exist
    if not db_path.exists():
        init_database()
    
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_aircraft_by_tail_number(tail_number: str) -> Optional[Dict[str, Any]]:
    """
    Get aircraft information by tail number.
    Includes joined data from aircraft_model and engine tables.
    
    Args:
        tail_number: Aircraft tail number (N-Number), e.g., "N12345"
    
    Returns:
        Dictionary with aircraft data, or None if not found
    """
    # Normalize tail number (remove N prefix if present, ensure uppercase)
    tail_number = tail_number.upper().strip()
    if not tail_number.startswith('N'):
        tail_number = f"N{tail_number}"
    
    # Limit to 5 characters after N
    if len(tail_number) > 6:
        tail_number = tail_number[:6]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query with LEFT JOINs to get related data
    cursor.execute("""
        SELECT 
            a.*,
            am.manufacturer_name as aircraft_manufacturer_name,
            am.model_name as aircraft_model_name,
            am.number_of_engines,
            am.number_of_seats,
            e.manufacturer_name as engine_manufacturer_name,
            e.engine_model_name,
            e.horsepower,
            e.pounds_of_thrust
        FROM aircraft a
        LEFT JOIN aircraft_model am ON a.mfr_model_code = am.model_code
        LEFT JOIN engine e ON a.engine_mfr_model_code = e.engine_code
        WHERE a.n_number = ?
    """, (tail_number,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # Convert Row to dictionary
    return dict(row)


def check_database_health() -> bool:
    """Check if database is accessible and has data."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM aircraft")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False

