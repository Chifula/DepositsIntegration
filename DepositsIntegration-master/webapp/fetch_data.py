import pandas as pd
from sqlalchemy import text
from config import mssql_engine, mysql_engine
import time
import logging
logging.basicConfig(level=logging.DEBUG)

def fetch_data_from_mssql():
    query = text("SELECT VENDNAME, AUDTTIME, AUDTUSER, SHORTNAME, DATELASTMN FROM [INFDAT].[dbo].[APVEN]")
    
    try:
        start_time = time.time()
        with mssql_engine.connect().execution_options(stream_results=True) as connection:
            df = pd.read_sql(query, connection)
        end_time = time.time()
        print(f"Data fetched from MSSQL in {end_time - start_time:.2f} seconds")
        print(f"Number of rows fetched: {len(df)}")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error fetching data from MSSQL: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

def insert_data_into_mysql(df):
    if df.empty:
        print("No data fetched. Skipping MySQL insertion.")
        return
    
    try:
        # Rename columns to match MySQL table column names
        df.columns = ['vendor_name', 'audit_time', 'audit_user', 'short_name', 'date_last_modified']
        
        # Convert datetime columns
        # df['audit_time'] = pd.to_datetime(df['audit_time'], errors='coerce')
        # df['date_last_modified'] = pd.to_datetime(df['date_last_modified'], errors='coerce')
        
        # Drop rows with invalid datetime values
        df = df.dropna(subset=['audit_time', 'date_last_modified'])
        
        print("Data after cleaning:")
        print(df.head())
        df.to_csv('C:/Users/user/DataLoad/python-sql-project/vendorinfo.csv', index=False)
        
        start_time = time.time()
        with mysql_engine.connect() as connection:
            df.to_sql('webapp_vendorinfo', connection, if_exists='replace', index=False, method='multi', chunksize=1000)
            connection.commit()
            logging.debug("Data inserted into MySQL")
        end_time = time.time()
        
        print(f"Data inserted successfully into MySQL in {end_time - start_time:.2f} seconds")
        print(f"Number of rows inserted: {len(df)}")
    
    except Exception as e:
        print(f"Error inserting data into MySQL: {e}")

def save_data_to_csv(df, filepath):
    try:
        filepath='C:/Users/user/DataLoad/python-sql-project/vendorinfo.csv'
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

if __name__ == "__main__":
    data = fetch_data_from_mssql()
    insert_data_into_mysql(data)

    # Dispose engines after use
    mssql_engine.dispose()
    mysql_engine.dispose()