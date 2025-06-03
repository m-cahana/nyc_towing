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

plate = 'LER5337'

fines = fines[fines['plate'] == plate]

# *********************
# save
# *********************

fines.to_csv(f'../../static/data/fines_plate_{plate}.csv', index=False)