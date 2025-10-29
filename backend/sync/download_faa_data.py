"""
Downloads and extracts FAA aircraft registration data.
"""
import requests
import zipfile
import os
import hashlib
from pathlib import Path
from typing import Tuple, Optional


# FAA data URL
FAA_DATA_URL = 'https://registry.faa.gov/database/ReleasableAircraft.zip'

# Custom headers to mimic a browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.114 Safari/537.36"
    ),
}


def get_data_directory() -> Path:
    """Get the path to the data directory."""
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def calculate_md5(file_path: Path) -> str:
    """Calculate the MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            md5.update(chunk)
    return md5.hexdigest()


def download_file(url: str, path: Path, headers: dict, max_retries: int = 5, timeout: int = 60) -> bool:
    """
    Download a file from a URL with retry logic.
    
    Args:
        url: URL to download from
        path: Local path to save the file
        headers: HTTP headers to use
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
    
    Returns:
        True if download succeeded, False otherwise
    """
    attempt = 1
    while attempt <= max_retries:
        try:
            print(f"Downloading from {url} (attempt {attempt}/{max_retries})...")
            response = requests.get(url, headers=headers, stream=True, timeout=timeout)
            response.raise_for_status()
            
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            
            print("Download complete.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Retrying...")
            attempt += 1
    
    print("Failed to download the file after all retries.")
    return False


def check_and_update_file(url: str, zip_path: Path, temp_zip_path: Path, headers: dict) -> Tuple[bool, bool]:
    """
    Check if the FAA data file has changed and update if necessary.
    
    Returns:
        Tuple of (update_happened, download_succeeded)
    """
    if not download_file(url, temp_zip_path, headers):
        return False, False
    
    # Check if existing file exists and compare checksums
    if zip_path.exists():
        original_md5 = calculate_md5(zip_path)
        new_md5 = calculate_md5(temp_zip_path)
        
        if original_md5 == new_md5:
            print("File is up-to-date. Skipping update.")
            os.remove(temp_zip_path)
            return False, True  # No update needed, but download succeeded
        else:
            print("File has changed. Updating with new download.")
    else:
        print("No existing file found. Creating new file.")
    
    # Replace old file with new one
    if zip_path.exists():
        os.remove(zip_path)
    os.rename(temp_zip_path, zip_path)
    return True, True  # Update happened


def extract_zip(zip_path: Path, extract_to: Path) -> None:
    """Extract a ZIP file to the specified directory."""
    print(f"Extracting {zip_path} to {extract_to}...")
    extract_to.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    print("Extraction complete.")


def download_and_extract_faa_data() -> Tuple[bool, bool]:
    """
    Main function to download and extract FAA data.
    
    Returns:
        Tuple of (update_happened, success)
    """
    data_dir = get_data_directory()
    zip_path = data_dir / "ReleasableAircraft.zip"
    temp_zip_path = data_dir / "temp_ReleasableAircraft.zip"
    extract_path = data_dir / "FAA_Database"
    
    update_happened, download_succeeded = check_and_update_file(
        FAA_DATA_URL, zip_path, temp_zip_path, HEADERS
    )
    
    if download_succeeded and update_happened:
        extract_zip(zip_path, extract_path)
        # Update modification time
        os.utime(zip_path, None)
        return True, True
    elif download_succeeded:
        # File was up-to-date, but ensure extraction exists
        if not extract_path.exists():
            print("Extracting existing file...")
            extract_zip(zip_path, extract_path)
        return False, True
    else:
        return False, False


if __name__ == "__main__":
    print("Starting FAA data download and extraction...")
    update_happened, success = download_and_extract_faa_data()
    
    if success:
        if update_happened:
            print("✓ FAA data updated and extracted successfully!")
        else:
            print("✓ FAA data is already up-to-date.")
    else:
        print("✗ Failed to download FAA data.")
        exit(1)

