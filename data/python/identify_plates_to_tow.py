import pandas as pd
import datetime as dt

# *********************
# constants
# *********************

current_date = pd.to_datetime(dt.datetime.now().date())
judgement_date_diff_min = 75 # days
tow_threshold = 350 # usd

# *********************
# data read in 
# *********************

tow_cases = pd.read_csv('../processed/scofftow_case_information.csv')

fine_agg = pd.read_csv('../processed/fine_agg.csv')

fines_2024 = pd.read_csv('../processed/school_zone_fines_2024.csv')

# *********************
# identify plates to tow
# *********************

plates_to_tow = fine_agg[fine_agg.fines_in_judgement > tow_threshold] 

print(f'plates to tow since 2015: {len(plates_to_tow)}')

plates_to_tow = plates_to_tow.merge(
    tow_cases.drop_duplicates(subset=['plate_id', 'license_plate_issuing_state', 'license_plate_type']), 
    left_on=['plate', 'state', 'license_type'], 
    right_on=['plate_id', 'license_plate_issuing_state', 'license_plate_type'], 
    how='left'
)

print(f"""
      {round(plates_to_tow[plates_to_tow.case_number.notna()].shape[0] / plates_to_tow.shape[0] * 100, 2)}% of plates actually towed
      """)

# *********************
# identify plates to tow - 2024 and later
# *********************


fines_2024['issue_date'] = pd.to_datetime(
    fines_2024['issue_date'], 
    errors='coerce'
)

fines_2024['total_fine'] = (
    fines_2024['fine_amount'] + 
    fines_2024['penalty_amount'] + 
    fines_2024['interest_amount'] - 
    fines_2024['reduction_amount']
)

fines_2024['in_judgement'] = (
    # fines have been issued for more than 75 days
    (
        (current_date - fines_2024['issue_date']).dt.days > judgement_date_diff_min
    ) &
    # fines are still outstanding
    (
        fines_2024['amount_due'] > 0
    )
)


# Calculate total fines
fine_agg_2024 = fines_2024.groupby(['plate', 'state', 'license_type']).agg(
    total_fines = ('total_fine', 'sum'), 
    amount_paid = ('payment_amount', 'sum'), 
    amount_due = ('amount_due', 'sum'), 
    violations = ('summons_number', 'nunique')
)


# Calculate fines in judgement (only where in_judgement is True)
judgement_fines_2024 = fines_2024[fines_2024['in_judgement'] == True].groupby('plate').agg(
    fines_in_judgement = ('amount_due', 'sum')
)

# Merge the two aggregations
fine_agg_2024 = fine_agg_2024.join(judgement_fines_2024, how='left')
fine_agg_2024['fines_in_judgement'] = fine_agg_2024['fines_in_judgement'].fillna(0)

fine_agg_2024 = fine_agg_2024.reset_index()


plates_to_tow_2024 = fine_agg_2024[fine_agg_2024.fines_in_judgement > tow_threshold] 

print(f'plates to tow since 2024: {len(plates_to_tow_2024)}')

plates_to_tow_2024 = plates_to_tow_2024.merge(
    tow_cases[tow_cases.boot_date >= '2024-01-01'].drop_duplicates(subset=['plate_id', 'license_plate_issuing_state', 'license_plate_type']), 
    left_on=['plate', 'state', 'license_type'], 
    right_on=['plate_id', 'license_plate_issuing_state', 'license_plate_type'], 
    how='left'
)

print(f"""
      {round(plates_to_tow_2024[plates_to_tow_2024.case_number.notna()].shape[0] / plates_to_tow_2024.shape[0] * 100, 2)}% of plates actually towed
      """)

# there's a really interesting pattern here where plates that get booted continue to speed a ton after the boot, and soon should be booted again - worth investigating
# pattern is specifically: speed, boot/tow, speed, boot/tow, etc.
plates_to_tow_2024[plates_to_tow_2024.case_number.notna()].sort_values(by='fines_in_judgement', ascending=False).head(10)

plates_to_tow_2024[plates_to_tow_2024.case_number.isna()].sort_values(by='fines_in_judgement', ascending=False).head(10)