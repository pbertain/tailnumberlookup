#!/usr/bin/env python3
"""
Main script to sync FAA data: download and import.
This is the entry point for systemd service.
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Change to project root directory
import os
os.chdir(project_root)

from backend.sync.download_faa_data import download_and_extract_faa_data
from backend.sync.import_to_db import import_faa_data


def main():
    """Main sync function: download and import."""
    print("=" * 60)
    print("FAA Aircraft Data Sync")
    print("=" * 60)
    print()
    
    # Step 1: Download data
    print("Step 1: Downloading FAA data...")
    update_happened, download_success = download_and_extract_faa_data()
    
    if not download_success:
        print("✗ Failed to download FAA data.")
        sys.exit(1)
    
    if update_happened:
        print("✓ FAA data downloaded and extracted.")
    else:
        print("✓ FAA data is up-to-date.")
    
    print()
    
    # Step 2: Import to database
    print("Step 2: Importing data to database...")
    try:
        # Force import if database is empty (handled inside import_faa_data)
        import_faa_data(force=False)  # Will auto-force if empty
        print("✓ Sync complete!")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error during import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

