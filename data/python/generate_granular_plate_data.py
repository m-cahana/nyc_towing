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
    'KUB5440', 'KHD6094', 'MJF5321', 
    'LFM4533', 'KZB6485', 'LAC2752', 
    'K72RCF', 'JSF2653', 'KEE6882'
]

selected_fines = fines[fines['plate'].isin(plates)]

# *********************
# save
# *********************

for plate in plates:
    selected_fines[selected_fines['plate'] == plate].to_csv(f'../../static/data/fines_plate_{plate}.csv', index=False)