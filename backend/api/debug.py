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
    
    # Search with LIKE pattern
    cursor.execute("""
        SELECT n_number, registrant_name, city, state 
        FROM aircraft 
        WHERE n_number LIKE ? 
        LIMIT 20
    """, (f"%{pattern.upper()}%",))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {
        "pattern": pattern,
        "count": len(results),
        "results": results
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

