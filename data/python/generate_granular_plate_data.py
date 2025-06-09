import pandas as pd

# *********************
# data read in 
# *********************

fines = pd.concat([
    pd.read_csv('../processed/school_zone_fines_2023.csv'),
    pd.read_csv('../processed/school_zone_fines_2024.csv'),
    pd.read_csv('../processed/school_zone_fines_2025.csv')
])

# *********************
# clean
# *********************

plates = [
    'LLD1506', 'MBE1363', 'LEX6751',
    'LCJ3416', 'RDE3018', 'KV476H', 
    'JUA957', 'LNC2362', 'KJC7042']

selected_fines = fines[fines['plate'].isin(plates)]

# *********************
# save
# *********************

for plate in plates:
    selected_fines[selected_fines['plate'] == plate].to_csv(f'../../static/data/fines_plate_{plate}.csv', index=False)