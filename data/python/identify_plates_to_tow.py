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

fine_agg_2024 = pd.read_csv('../processed/fine_agg_2024.csv')

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