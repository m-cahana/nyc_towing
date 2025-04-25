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
    judgement_fines = fines[fines['in_judgement'] == True].groupby('plate').agg(
        fines_in_judgement = ('amount_due', 'sum')
    )

    # Merge the two aggregations
    fine_agg = fine_agg.join(judgement_fines, how='left')
    fine_agg['fines_in_judgement'] = fine_agg['fines_in_judgement'].fillna(0)

    fine_agg = fine_agg.reset_index()

    return fine_agg

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

fines = process_fines(fines)
fines_2024 = process_fines(fines_2024)

# *********************
# aggregate
# *********************

fine_agg = aggregate_fines(fines)
fine_agg_2024 = aggregate_fines(fines_2024)

# *********************
# save output
# *********************

fine_agg.to_csv('../processed/fine_agg.csv', index=False)
fine_agg_2024.to_csv('../processed/fine_agg_2024.csv', index=False)
