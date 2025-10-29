import requests
import os
import hashlib

# Define the URL and paths
url = 'https://registry.faa.gov/database/ardata.pdf'
download_path = 'doc/ardata.pdf'
temp_download_path = 'doc/temp/ardata_temp.pdf'

# Ensure the directories exist
os.makedirs('doc/temp', exist_ok=True)

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

# Function to download the file
def download_file(url, path, headers, max_retries=5, timeout=60):
    attempt = 1
    while attempt <= max_retries:
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=timeout)
            with open(path, 'wb') as file:
                for data in response.iter_content(1024):
                    file.write(data)
            print(f"Download complete: {path}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Retrying... (Attempt {attempt})")
        attempt += 1
    print("Failed to download the file.")
    return False

# Compare checksums and update the file if needed
def check_and_update_file(url, download_path, temp_download_path, headers):
    if download_file(url, temp_download_path, headers):
        if os.path.exists(download_path):
            original_md5 = calculate_md5(download_path)
            new_md5 = calculate_md5(temp_download_path)
            
            if original_md5 == new_md5:
                print("File is up-to-date. Skipping update.")
                os.remove(temp_download_path)  # Remove temp file if it's identical
                return False  # No update needed
            else:
                print("File has changed. Updating the file.")
        
        # Move temp file to the final destination
        os.rename(temp_download_path, download_path)
        print(f"File updated: {download_path}")
        return True  # Update happened
    else:
        return False  # Download failed

# Run the update process
if check_and_update_file(url, download_path, temp_download_path, headers):
    print(f"File has been successfully downloaded or updated: {download_path}")
else:
    print(f"No update required or download failed for: {download_path}")

