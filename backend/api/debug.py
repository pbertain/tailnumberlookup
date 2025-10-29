"""
Debug endpoint for troubleshooting database queries.
"""
from fastapi import APIRouter
from backend.api.database import get_db_connection
import sqlite3

router = APIRouter()


@router.get("/api/debug/search/{pattern}")
async def search_aircraft_pattern(pattern: str):
    """Search for aircraft by pattern (for debugging)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Search with LIKE pattern (case-insensitive)
    cursor.execute("""
        SELECT n_number, registrant_name, city, state 
        FROM aircraft 
        WHERE UPPER(n_number) LIKE ? 
        LIMIT 20
    """, (f"%{pattern.upper()}%",))
    
    results = [dict(row) for row in cursor.fetchall()]
    
    # Also check with N prefix removed
    pattern_no_n = pattern.upper().lstrip('N')
    cursor.execute("""
        SELECT n_number, registrant_name, city, state 
        FROM aircraft 
        WHERE UPPER(SUBSTR(n_number, 2)) LIKE ? 
        LIMIT 20
    """, (f"%{pattern_no_n}%",))
    
    results_no_n = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "pattern": pattern,
        "count_with_n": len(results),
        "count_without_n": len(results_no_n),
        "results": results,
        "results_without_n_prefix": results_no_n
    }


@router.get("/api/debug/stats")
async def get_database_stats():
    """Get database statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM aircraft")
    aircraft_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM aircraft_model")
    model_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM engine")
    engine_count = cursor.fetchone()[0]
    
    # Sample tail numbers
    cursor.execute("SELECT n_number FROM aircraft LIMIT 10")
    sample_numbers = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "aircraft_count": aircraft_count,
        "model_count": model_count,
        "engine_count": engine_count,
        "sample_tail_numbers": sample_numbers
    }

