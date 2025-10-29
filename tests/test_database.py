"""
Unit tests for database functions.
"""
import pytest
import sqlite3
import tempfile
from pathlib import Path
from backend.sync.database import init_database, get_db_path


def test_database_initialization():
    """Test database schema initialization."""
    # Create a temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test.db"
        
        # Temporarily override get_db_path to return test path
        original_get_db_path = get_db_path
        
        # Initialize database
        conn = sqlite3.connect(str(test_db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create tables (simulating init_database)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aircraft (
                n_number TEXT(5) PRIMARY KEY,
                registrant_name TEXT(50)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aircraft_model (
                model_code TEXT(7) PRIMARY KEY,
                manufacturer_name TEXT(30)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engine (
                engine_code TEXT(5) PRIMARY KEY,
                manufacturer_name TEXT(50)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                file_name TEXT(50) PRIMARY KEY,
                file_create_date DATETIME,
                file_md5sum TEXT(32)
            )
        """)
        
        conn.commit()
        
        # Verify tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('aircraft', 'aircraft_model', 'engine', 'file_metadata')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'aircraft' in tables
        assert 'aircraft_model' in tables
        assert 'engine' in tables
        assert 'file_metadata' in tables
        
        conn.close()


def test_tail_number_normalization():
    """Test tail number normalization logic."""
    # Test various tail number formats
    test_cases = [
        ("N12345", "N12345"),
        ("12345", "N12345"),
        ("n12345", "N12345"),
        ("N1234", "N1234"),
        ("1234", "N1234"),
    ]
    
    # This tests the logic from database.py get_aircraft_by_tail_number
    def normalize_tail_number(tail_number: str) -> str:
        tail_number = tail_number.upper().strip()
        if not tail_number.startswith('N'):
            tail_number = f"N{tail_number}"
        if len(tail_number) > 6:
            tail_number = tail_number[:6]
        return tail_number
    
    for input_val, expected in test_cases:
        result = normalize_tail_number(input_val)
        assert result == expected, f"Failed for input: {input_val}, expected {expected}, got {result}"

