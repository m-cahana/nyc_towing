import pandas as pd

# *********************
# data read in 
# *********************

# sourced from https://data.cityofnewyork.us/City-Government/DOF-Scofftow-Case-Information/qmh3-uvgq/about_data
df = pd.read_csv('../raw/DOF_Scofftow_Case_Information_20250422.csv')

# *********************
# data cleaning
# *********************

# make all column names lowercase and replace spaces with underscores
df.columns = df.columns.str.lower().str.replace(' ', '_')

df['boot_date'] = pd.to_datetime(df['boot_date'])
df['tow_date'] = pd.to_datetime(df['tow_date'])
df['auction_date'] = pd.to_datetime(df['auction_date'])

df = df.rename(columns=
               {'license_plate_number': 'plate_id',
                'tow_(y/n)': 'towed', 
                'redeemed_(y/n)': 'redeemed',
                'auctioned_(y/n)': 'auctioned',
                })

df['towed'] = df['towed'].map({'Y': True, 'N': False})
df['redeemed'] = df['redeemed'].map({'Y': True, 'N': False})
df['auctioned'] = df['auctioned'].map({'Y': True, 'N': False})

# *********************
# save output
# *********************

df.to_csv('../processed/scofftow_case_information.csv', index=False)



