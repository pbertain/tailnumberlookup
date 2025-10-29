import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date
import numpy as np

# Database connection string with placeholder password
engine = create_engine('postgresql://postgres:secure_password@localhost:5432/faa_aircraft')
metadata = MetaData()

# Define table schemas explicitly
aircraft_model_table = Table(
    'aircraft_model', metadata,
    Column('mfr_mdl_code', String, primary_key=True),
    Column('manufacturer', String),
    Column('model', String)
)

engine_table = Table(
    'engine', metadata,
    Column('eng_mfr_mdl', String, primary_key=True),
    Column('manufacturer', String),
    Column('model', String)
)

aircraft_table = Table(
    'aircraft', metadata,
    Column('tail_number', String, primary_key=True),
    Column('serial_number', String),
    Column('mfr_mdl_code', String),
    Column('eng_mfr_mdl', String),
    Column('year_mfr', Integer),
    Column('owner_name', String),
    Column('street', String),
    Column('street2', String),
    Column('city', String),
    Column('state', String),
    Column('zip_code', String),
    Column('region', String),
    Column('county', String),
    Column('country', String),
    Column('cert_issue_date', Date),
    Column('certification', String),
    Column('type_aircraft', String),
    Column('type_engine', String),
    Column('air_worth_date', Date),
    Column('expiration_date', Date),
)

def drop_and_create_tables():
    # Drop tables in cascade
    with engine.connect() as connection:
        metadata.drop_all(engine, checkfirst=True)
        print("Dropped all tables successfully with CASCADE.")
        
        # Recreate tables
        metadata.create_all(engine)
        print("Recreated all tables successfully.")

def clean_data(df):
    # Convert year_mfr to integer where possible, otherwise replace with NaN
    df['year_mfr'] = pd.to_numeric(df['year_mfr'], errors='coerce')
    # Any other integer fields should follow a similar conversion approach
    
    # Convert date columns to datetime and replace errors with NaT
    date_cols = ['cert_issue_date', 'air_worth_date', 'expiration_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def load_data():
    # Load data from files
    aircraft_model_df = pd.read_fwf(
        'FAA_Database/ACFTREF.txt', colspecs=[(0, 7), (8, 38), (39, 59)],
        names=['mfr_mdl_code', 'manufacturer', 'model'], dtype=str
    )
    engine_df = pd.read_fwf(
        'FAA_Database/ENGINE.txt', colspecs=[(0, 5), (6, 16), (17, 30)],
        names=['eng_mfr_mdl', 'manufacturer', 'model'], dtype=str
    )
    aircraft_df = pd.read_fwf(
        'FAA_Database/MASTER.txt', colspecs=[(0, 5), (6, 36), (37, 44), (45, 50), (51, 55), (58, 108), (109, 142),
                                             (143, 176), (177, 195), (196, 198), (199, 209), (210, 211), (212, 215), 
                                             (216, 218), (228, 236), (237, 238), (248, 249), (250, 252), (267, 275), (531, 539)],
        names=["tail_number", "serial_number", "mfr_mdl_code", "eng_mfr_mdl", "year_mfr", 
               "owner_name", "street", "street2", "city", "state", "zip_code", "region", 
               "county", "country", "cert_issue_date", "certification", "type_aircraft", 
               "type_engine", "air_worth_date", "expiration_date"], dtype=str, skiprows=1
    )

    # Clean data
    aircraft_df = clean_data(aircraft_df)
    
    # Insert data into tables
    with engine.connect() as connection:
        aircraft_model_df.to_sql('aircraft_model', con=connection, if_exists='append', index=False)
        engine_df.to_sql('engine', con=connection, if_exists='append', index=False)
        aircraft_df.to_sql('aircraft', con=connection, if_exists='append', index=False)
        print("Data loaded into database successfully.")

def main():
    drop_and_create_tables()
    load_data()

if __name__ == '__main__':
    main()

