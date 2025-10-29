import os
import pandas as pd
from datetime import datetime
import pytz

# Define paths
master_file_path = 'FAA_Database/MASTER.txt'
aircraft_ref_path = 'FAA_Database/ACFTREF.txt'
engine_ref_path = 'FAA_Database/ENGINE.txt'

# Load the MASTER.txt file into a DataFrame based on fixed-width format
def load_master_data(file_path):
    colspecs = [
        (0, 5), (6, 36), (37, 44), (45, 50), (51, 55), (58, 108), (109, 142),
        (143, 176), (177, 195), (196, 198), (199, 209), (210, 211), (212, 215), 
        (216, 218), (228, 236), (237, 238), (248, 249), (250, 252), (267, 275), (531, 539)
    ]
    col_names = [
        "N-NUMBER", "SERIAL NUMBER", "MFR MDL CODE", "ENG MFR MDL", "YEAR MFR", 
        "NAME", "STREET", "STREET2", "CITY", "STATE", "ZIP CODE", "REGION", 
        "COUNTY", "COUNTRY", "CERT ISSUE DATE", "CERTIFICATION", "TYPE AIRCRAFT", 
        "TYPE ENGINE", "AIR WORTH DATE", "EXPIRATION DATE"
    ]
    df = pd.read_fwf(file_path, colspecs=colspecs, names=col_names, dtype=str)
    return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Load the ACFTREF.txt file into a DataFrame
def load_aircraft_ref(file_path):
    colspecs = [(0, 7), (8, 38), (39, 59)]
    col_names = ["MFR MDL CODE", "ACFT MFR", "ACFT MODEL"]
    df = pd.read_fwf(file_path, colspecs=colspecs, names=col_names, dtype=str)
    return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Load the ENGINE.txt file into a DataFrame
def load_engine_ref(file_path):
    colspecs = [(0, 5), (6, 16), (17, 30)]
    col_names = ["ENG MFR MDL", "ENG MFR", "ENG MODEL"]
    df = pd.read_fwf(file_path, colspecs=colspecs, names=col_names, dtype=str)
    return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Merge data from MASTER, ACFTREF, and ENGINE
def merge_data(master_df, aircraft_ref_df, engine_ref_df):
    merged_df = master_df \
        .merge(aircraft_ref_df, on="MFR MDL CODE", how="left") \
        .merge(engine_ref_df, on="ENG MFR MDL", how="left")
    return merged_df

# Retrieve owner information including aircraft and engine details
def get_aircraft_info(merged_df, tail_number):
    stripped_tail_number = tail_number[1:].strip()
    record = merged_df[merged_df['N-NUMBER'] == stripped_tail_number]
    if not record.empty:
        info = record.iloc[0]
        return {
            "Tail Number": tail_number,
            "Serial Number": info['SERIAL NUMBER'],
            "Aircraft Manufacturer": info['ACFT MFR'],
            "Aircraft Model": info['ACFT MODEL'],
            "Engine Manufacturer": info['ENG MFR'],
            "Engine Model": info['ENG MODEL'],
            "Year Manufactured": info['YEAR MFR'],
            "Owner Name": info['NAME'],
            "Street": info['STREET'],
            "Street2": info['STREET2'],
            "City": info['CITY'],
            "State": info['STATE'],
            "Zip Code": info['ZIP CODE'],
            "Region": info['REGION'],
            "County": info['COUNTY'],
            "Country": info['COUNTRY'],
            "Cert Issue Date": info['CERT ISSUE DATE'],
            "Certification": info['CERTIFICATION'],
            "Type Aircraft": info['TYPE AIRCRAFT'],
            "Type Engine": info['TYPE ENGINE'],
            "Airworthiness Date": info['AIR WORTH DATE'],
            "Expiration Date": info['EXPIRATION DATE'],
        }
    else:
        return None

# Load and merge data
if os.path.exists(master_file_path) and os.path.exists(aircraft_ref_path) and os.path.exists(engine_ref_path):
    master_df = load_master_data(master_file_path)
    aircraft_ref_df = load_aircraft_ref(aircraft_ref_path)
    engine_ref_df = load_engine_ref(engine_ref_path)
    merged_df = merge_data(master_df, aircraft_ref_df, engine_ref_df)

    # Example usage with a tail number
    #tail_number = 'N538CD'
    tail_number = 'N6501M'
    aircraft_info = get_aircraft_info(merged_df, tail_number)

    if aircraft_info:
        print("Aircraft Information:")
        for key, value in aircraft_info.items():
            print(f"{key}: {value}")
    else:
        print("No information available for the specified tail number.")
else:
    print("Required files are missing. Please ensure the data download script has run and extracted files are available.")

