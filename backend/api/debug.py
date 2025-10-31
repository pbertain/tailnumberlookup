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
    
    pattern_upper = pattern.upper().strip()
    
    # Try exact match with N
    cursor.execute("SELECT n_number, registrant_name, city, state FROM aircraft WHERE n_number = ?", (f"N{pattern_upper.lstrip('N')}",))
    exact_with_n = [dict(row) for row in cursor.fetchall()]
    
    # Try exact match without N
    pattern_no_n = pattern_upper.lstrip('N')
    cursor.execute("SELECT n_number, registrant_name, city, state FROM aircraft WHERE n_number = ?", (pattern_no_n,))
    exact_no_n = [dict(row) for row in cursor.fetchall()]
    
    # Search with LIKE pattern (case-insensitive)
    cursor.execute("""
        SELECT n_number, registrant_name, city, state 
        FROM aircraft 
        WHERE UPPER(n_number) LIKE ? 
        LIMIT 20
    """, (f"%{pattern_upper}%",))
    
    results = [dict(row) for row in cursor.fetchall()]
    
    # Also check with N prefix removed
    cursor.execute("""
        SELECT n_number, registrant_name, city, state 
        FROM aircraft 
        WHERE UPPER(SUBSTR(n_number, 2)) LIKE ? 
        LIMIT 20
    """, (f"%{pattern_no_n}%",))
    
    results_no_n = [dict(row) for row in cursor.fetchall()]
    
    # Show all n_numbers containing the pattern
    cursor.execute("SELECT DISTINCT n_number FROM aircraft WHERE n_number LIKE ? LIMIT 50", (f"%{pattern_upper}%",))
    all_matches = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "pattern": pattern,
        "normalized": f"N{pattern_no_n[:5]}",
        "exact_match_with_n": exact_with_n,
        "exact_match_no_n": exact_no_n,
        "count_like_with_n": len(results),
        "count_like_without_n": len(results_no_n),
        "results": results,
        "results_without_n_prefix": results_no_n,
        "all_matching_n_numbers": all_matches
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
    
    # Sample tail numbers with more detail
    cursor.execute("SELECT n_number, LENGTH(n_number) as len, registrant_name FROM aircraft LIMIT 20")
    sample_data = [{"n_number": row[0], "length": row[1], "owner": row[2]} for row in cursor.fetchall()]
    
    # Check for N538CD specifically
    cursor.execute("SELECT n_number FROM aircraft WHERE n_number LIKE '%538%' LIMIT 10")
    matches_538 = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "aircraft_count": aircraft_count,
        "model_count": model_count,
        "engine_count": engine_count,
        "sample_tail_numbers": sample_data,
        "matches_538_pattern": matches_538
    }

