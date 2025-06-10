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
    'KJM6620', 'JCC5743', 'JUA957',
    '126BH0', 'LCT2817', 'LCB8694', 
    'W69PBV', 'JZH5211', 'RTH0590']

selected_fines = fines[fines['plate'].isin(plates)]

# *********************
# save
# *********************

for plate in plates:
    selected_fines[selected_fines['plate'] == plate].to_csv(f'../../static/data/fines_plate_{plate}.csv', index=False)