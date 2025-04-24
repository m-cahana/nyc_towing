import pandas as pd
from sodapy import Socrata

# *********************
# data download
# *********************

app_token = 'GUfYzTijai2AtUmFol1JXFMpj'

client = Socrata("data.cityofnewyork.us", app_token)

# grab records
results = pd.DataFrame.from_records(
            client.get("pvqr-7yc4", 
            where='date_trunc_ymd(issue_date) >= "2024-01-01"',
            violation_code='36')
        )
)