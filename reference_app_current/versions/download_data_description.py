import requests
import zipfile
import os
import hashlib
import datetime

# Define the URL and paths
url = 'https://registry.faa.gov/database/ardata.pdf'
extract_path = 'doc'
temp_extract_path = 'doc/temp'

# Custom headers to mimic a browser
headers = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/91.0.4472.114 Safari/537.36"),
}

# Function to calculate the MD5 checksum of a file
def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

# Function to download the ZIP file temporarily to check checksum
def download_file(url, path, headers, max_retries=5, timeout=60):
    attempt = 1
    while attempt <= max_retries:
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=timeout)
            with open(path, 'wb') as file:
                for data in response.iter_content(1024):
                    file.write(data)
            print("Download complete.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Retrying...")
        attempt += 1
    print("Failed to download the file.")
    return False

# Compare checksums and update the file if needed
def check_and_update_file(url, extract_path, temp_extract_path, headers):
    if download_file(url, extract_path, headers):
        if os.path.exists(extract_path):
            original_md5 = calculate_md5(extract_path)
            new_md5 = calculate_md5(temp_extract_path)
            
            if original_md5 == new_md5:
                print("File is up-to-date. Skipping download.")
                os.remove(temp_zip_path)
                return False  # No update needed
            else:
                print("File has changed. Updating with new download.")
        
        os.rename(temp_zip_path, zip_path)
        return True  # Update happened
    else:
        return False  # Download failed

# Extract the ZIP file
def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

# Run the update process
if check_and_update_file(url, extract_path, temp_extract_path, headers):
    # Set modification time to current time
    os.utime(zip_path, None)

