import pandas as pd
import datetime as dt
from tqdm import tqdm

# *********************
# constants
# *********************

current_date = pd.to_datetime(dt.datetime.now().date())
judgement_date_diff_min = 75 # days

# *********************
# functions
# *********************

def process_fines(fines):
    print("Converting dates...")
    fines['issue_date'] = pd.to_datetime(
        fines['issue_date'], 
        errors='coerce'
    )

    print("Calculating total fines...")
    fines['total_fine'] = (
        fines['fine_amount'] + 
        fines['penalty_amount'] + 
        fines['interest_amount'] - 
        fines['reduction_amount']
    )

    print("Calculating judgement status...")
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

    print("Removing duplicates...")
    # Drop duplicates treating NaN values as equal
    fines = fines.drop_duplicates()

    return fines


def aggregate_fines(fines):

    fines['post_tow_eligible'] = (
       fines['issue_date'] > fines['tow_eligible_date']
    )

    # Calculate total fines
    fine_agg = fines.groupby(['plate', 'state', 'license_type', 'tow_eligible_date'], dropna=False).agg(
        total_fines = ('total_fine', 'sum'), 
        amount_paid = ('payment_amount', 'sum'), 
        amount_due = ('amount_due', 'sum'), 
        violations = ('summons_number', 'nunique')
    ).reset_index()

    # calculate fines post tow eligible
    fines_post_tow_eligible = fines[fines['post_tow_eligible'] == True].groupby(['plate', 'state', 'license_type']).agg(
        total_fines_post_tow_eligible = ('total_fine', 'sum'), 
        amount_paid_post_tow_eligible = ('payment_amount', 'sum'), 
        amount_due_post_tow_eligible = ('amount_due', 'sum'), 
        violations_post_tow_eligible = ('summons_number', 'nunique')
    ).reset_index()

    # Calculate fines in judgement (only where in_judgement is True)
    judgement_fines = fines[fines['in_judgement'] == True].groupby(['plate', 'state', 'license_type']).agg(
        fines_in_judgement = ('amount_due', 'sum')
    ).reset_index()

    # Merge the three aggregations
    fine_agg = fine_agg.merge(judgement_fines, how='left', on=['plate', 'state', 'license_type']).merge(fines_post_tow_eligible, how='left', on=['plate', 'state', 'license_type'])

    # fill na with 0
    fine_agg[['fines_in_judgement', 'total_fines_post_tow_eligible', 'amount_paid_post_tow_eligible', 'amount_due_post_tow_eligible', 'violations_post_tow_eligible']] = fine_agg[['fines_in_judgement', 'total_fines_post_tow_eligible', 'amount_paid_post_tow_eligible', 'amount_due_post_tow_eligible', 'violations_post_tow_eligible']].fillna(0)

    fine_agg = fine_agg.reset_index()

    return fine_agg

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
    yearly_fines = process_fines(yearly_fines)
    fines = pd.concat([fines, yearly_fines])


# *********************
# find threshold crossing dates
# *********************

crossing_dates = get_threshold_crossing_dates(fines)

fines = fines.merge(crossing_dates[['plate', 'state', 'license_type', 'tow_eligible_date']], on=['plate', 'state', 'license_type'], how='left')

# *********************
# aggregate
# *********************

fine_agg = aggregate_fines(fines)

# *********************
# save output
# *********************

fine_agg.to_csv('../processed/fine_agg.csv', index=False)
