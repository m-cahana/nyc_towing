import pandas as pd
import datetime as dt
# *********************
# read in data
# *********************

fines = pd.read_csv('../processed/school_zone_fines_2024.csv')

tow_cases = pd.read_csv('../processed/scofftow_case_information.csv')

# *********************
# simplify
# *********************
tow_cases['boot_date'] = pd.to_datetime(tow_cases['boot_date'])
tow_cases = tow_cases[tow_cases.boot_date.dt.year == 2024]

tow_cases = tow_cases[
    ['plate_id', 'license_plate_issuing_state', 
    'license_plate_type', 
    'case_number',
    'boot_date', 'tow_date']
    ]

tow_cases = tow_cases.rename(
    columns={
        'license_plate_issuing_state': 'state', 
        'license_plate_type': 'license_type', 
        'boot_date': 'boot_date', 
        'tow_date': 'tow_date'
        })

fines['total_fine'] = (
    fines['fine_amount'] + 
    fines['penalty_amount'] + 
    fines['interest_amount'] - 
    fines['reduction_amount']
)

fines = fines[['plate', 'state', 'license_type', 
               'summons_number', 'issue_date', 'total_fine', 'amount_due', 'payment_amount']]

fines = fines.rename(
    columns={
        'plate': 'plate_id', 
    })

fines['dt'] = pd.to_datetime(fines['issue_date'])
tow_cases['dt'] = pd.to_datetime(tow_cases['boot_date'])

all_cols = list(set(tow_cases.columns) | set(fines.columns))

tow_cases = tow_cases.reindex(columns=all_cols)

fines = fines.reindex(columns=all_cols)

# *********************
# merge data 
# *********************

# combine data, and sort by plate, state, license_type, and dt
joined = pd.concat([fines, tow_cases], ignore_index=True)

joined = joined.sort_values(by=['plate_id', 'state', 'license_type', 'dt'])

# Assign type based on summons_number and tow_date
joined['type'] = 'fine'  # Default for violations
joined.loc[joined['summons_number'].isna() & joined['tow_date'].notna(), 'type'] = 'tow'
joined.loc[joined['summons_number'].isna() & joined['tow_date'].isna(), 'type'] = 'boot'

joined = joined[
    ['plate_id', 'state', 'license_type', 'dt', 'type', 'issue_date', 'boot_date', 'tow_date', 'total_fine', 'amount_due', 'payment_amount', 'summons_number', 'case_number']
    ]

# *********************
# aggregate data
# *********************

grouped = joined.groupby(['plate_id', 'state', 'license_type']).agg(
    violations = ('summons_number', 'nunique'),
    boots_tows = ('case_number', 'nunique'),
).reset_index()

grouped[grouped.violations > 0].sort_values(['boots_tows', 'violations'], ascending = False)


interesting_plate = 'LBM8337'

joined[
    joined.plate_id == interesting_plate
    ][['plate_id', 'state', 'license_type', 'dt', 'type']].to_csv(f'../processed/example_plate_{interesting_plate}.csv', index=False)


