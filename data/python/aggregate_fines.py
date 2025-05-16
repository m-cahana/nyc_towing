import pandas as pd
import datetime as dt

# *********************
    # constants
# *********************

current_date = pd.to_datetime(dt.datetime.now().date())
judgement_date_diff_min = 75 # days

# *********************
# functions
# *********************

def process_fines(fines):
    fines['issue_date'] = pd.to_datetime(
        fines['issue_date'], 
        errors='coerce'
    )

    fines['total_fine'] = (
        fines['fine_amount'] + 
        fines['penalty_amount'] + 
        fines['interest_amount'] - 
        fines['reduction_amount']
    )

    fines['in_judgement'] = (
        # fines have been issued for more than 75 days
        (
            (current_date - fines['issue_date']).dt.days > judgement_date_diff_min
        ) &
        # fines are still outstanding
        (
            fines['amount_due'] > 0
        )
    )

    # Drop duplicates treating NaN values as equal
    fines = fines.drop_duplicates()

    return fines

def aggregate_fines(fines):
    # Calculate total fines
    fine_agg = fines.groupby(['plate', 'state', 'license_type']).agg(
        total_fines = ('total_fine', 'sum'), 
        amount_paid = ('payment_amount', 'sum'), 
        amount_due = ('amount_due', 'sum'), 
        violations = ('summons_number', 'nunique')
    )

    # Calculate fines in judgement (only where in_judgement is True)
    judgement_fines = fines[fines['in_judgement'] == True].groupby(['plate', 'state', 'license_type']).agg(
        fines_in_judgement = ('amount_due', 'sum')
    )

    # Merge the two aggregations
    fine_agg = fine_agg.join(judgement_fines, how='left', on=['plate', 'state', 'license_type'])
    fine_agg['fines_in_judgement'] = fine_agg['fines_in_judgement'].fillna(0)

    fine_agg = fine_agg.reset_index()

    return fine_agg

# *********************
# special status: find threshold crossing date
# *********************
def get_threshold_crossing_dates(fines, threshold=350):
    # Only consider fines in judgement
    fines_in_judgement = fines[fines['in_judgement']].copy()
    # Sort by plate and issue_date
    fines_in_judgement = fines_in_judgement.sort_values(['plate', 'state', 'license_type', 'issue_date'])
    # Calculate cumulative sum of amount_due for each plate
    fines_in_judgement['cumulative_due'] = fines_in_judgement.groupby(['plate', 'state', 'license_type'])['amount_due'].cumsum()
    # Find the first fine where cumulative_due exceeds the threshold
    crossing = fines_in_judgement[fines_in_judgement['cumulative_due'] > threshold]
    # Keep only the first crossing per plate
    crossing = crossing.groupby(['plate', 'state', 'license_type']).first().reset_index()
    # Select relevant columns
    crossing = crossing[['plate', 'state', 'license_type', 'issue_date', 'cumulative_due']]
    crossing = crossing.rename(columns={'issue_date': 'tow_eligible_date'})

    return crossing

# *********************
# data read in 
# *********************

fines = pd.DataFrame()
for year in range(2015, 2026):
    print(f'year: {year}')
    yearly_fines = pd.read_csv(f'../processed/school_zone_fines_{year}.csv')
    fines = pd.concat([fines, yearly_fines])

fines_2024 = pd.read_csv('../processed/school_zone_fines_2024.csv')
# *********************
# data processing
# *********************

print(f'fines pre process: {fines.shape}')
fines = process_fines(fines)
print(f'fines post process: {fines.shape}')

print(f'fines_2024 pre process: {fines_2024.shape}')
fines_2024 = process_fines(fines_2024)
print(f'fines_2024 post process: {fines_2024.shape}')

# *********************
# aggregate
# *********************

fine_agg = aggregate_fines(fines)
fine_agg_2024 = aggregate_fines(fines_2024)

# *********************
# find threshold crossing dates
# *********************

crossing_dates = get_threshold_crossing_dates(fines)

crossing_dates_2024 = get_threshold_crossing_dates(fines_2024)

fine_agg = fine_agg.merge(crossing_dates[['plate', 'state', 'license_type', 'tow_eligible_date']], on=['plate', 'state', 'license_type'], how='left')

fine_agg_2024 = fine_agg_2024.merge(crossing_dates_2024[['plate', 'state', 'license_type', 'tow_eligible_date']], on=['plate', 'state', 'license_type'], how='left')

# *********************
# save output
# *********************

fine_agg.to_csv('../processed/fine_agg.csv', index=False)
fine_agg_2024.to_csv('../processed/fine_agg_2024.csv', index=False)
