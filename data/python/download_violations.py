import requests
import pandas as pd
import time
import os

def download_school_zone_violations(output_file='../processed/school_zone_violations_2024.csv', batch_size=1_000_000):
    """
    Downloads NYC parking violations data for school zone speed violations in 2024 and saves to a CSV file (helped with Cursor).
    
    Args:
        output_file (str): Path to save the CSV file
        batch_size (int): Number of records to fetch per request
    """
    # Base URL for the NYC Open Parking and Camera Violations API
    base_url = 'https://data.cityofnewyork.us/resource/uvbq-3m68.json'
    
    offset = 0
    all_data = []
    total_records = 0
    
    print("Starting download of NYC school zone speed violations for 2024...")
    
    while True:
        # Build query parameters with pagination and filters
        params = {
            '$limit': batch_size,
            '$offset': offset,
            'violation': 'PHTO SCHOOL ZN SPEED VIOLATION',  # Filter for school zone violations
            # Filter for 2024 dates using LIKE operator to match MM/DD/2024 pattern, but account for the fact that issue_date is a string
            '$where': "issue_date LIKE '%/2024'"
        }
        
        print(f"Fetching records {offset} to {offset + batch_size}...")
        
        # Make the request
        response = requests.get(base_url, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            batch_data = response.json()
            batch_size_actual = len(batch_data)
            
            if batch_size_actual == 0:
                # No more data to fetch
                break
                
            all_data.extend(batch_data)
            total_records += batch_size_actual
            print(f"Downloaded {batch_size_actual} records. Total so far: {total_records}")
            
            # Move to the next batch
            offset += batch_size
            
            # Small delay to be nice to the API
            time.sleep(1)
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            break
    
    print(f"Download complete. Total records: {total_records}")
    
    # Convert to DataFrame
    if all_data:
        # transform to dataframe
        df = pd.DataFrame(all_data)
        
        # Save to CSV
        print('Saving to csv...')
        df.to_csv(output_file, index=False)
        print(f"Data saved to {os.path.abspath(output_file)}")
        
        return df
    else:
        print("No data was downloaded.")
        return None

download_school_zone_violations() 