import pandas as pd
import datetime as dt
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import random

# *********************
# data read in 
# *********************

tow_cases = pd.read_csv('../processed/scofftow_case_information.csv')

fine_agg = pd.read_csv('../processed/fine_agg.csv')

# *********************
# clean
# *********************

tow_cases.boot_date = pd.to_datetime(tow_cases.boot_date)
tow_cases.tow_date = pd.to_datetime(tow_cases.tow_date)
fine_agg.tow_eligible_date = pd.to_datetime(fine_agg.tow_eligible_date)

tow_cases['first_action_date'] = tow_cases[['boot_date', 'tow_date']].min(axis=1)
tow_cases['last_action_date'] = tow_cases[['boot_date', 'tow_date']].max(axis=1)

unique_tow_plates = tow_cases.groupby(['plate_id', 'license_plate_issuing_state', 'license_plate_type']).agg(
  first_action_date = ('first_action_date', 'min'),
  last_action_date = ('last_action_date', 'max')
).reset_index()

# *********************
# filter 
# *********************

fine_agg_with_tows = fine_agg.merge(
  unique_tow_plates,
  left_on=['plate', 'state', 'license_type'],
  right_on=['plate_id', 'license_plate_issuing_state', 'license_plate_type'], 
  how='left')


# plates that require towing
plates_to_tow = fine_agg_with_tows[fine_agg_with_tows.tow_eligible_date.notna()]

plates_to_tow = plates_to_tow[plates_to_tow.tow_eligible_date.dt.year == 2024]

# plates that were not towed
non_tows = fine_agg_with_tows[(fine_agg_with_tows.last_action_date.isna()) | (fine_agg_with_tows.last_action_date < fine_agg_with_tows.tow_eligible_date)]

non_tows = non_tows[non_tows.tow_eligible_date.dt.year == 2024]


comparison_df = plates_to_tow.merge(
  non_tows,
  on=['plate', 'state', 'license_type'],
  indicator=True,
  how='left',
  suffixes=('_tow', '_not_tow')
)

# *********************
# metric
# *********************

print(f"""
      {
        non_tows.shape[0] / plates_to_tow.shape[0]
      } share of plates not towed post eligibility
      """)

print(f"""
      {
        non_tows.shape[0] 
      } total plates not towed post eligibility
      """)

print(f"""
      {
        non_tows.amount_due_post_tow_eligible.sum()
      } total fines due post tow eligible, 
      from {
        non_tows.violations_post_tow_eligible.sum()
      } violations post tow eligible
      """)

print(f"""
      { round(
        non_tows.amount_due.sum(), 0)
      } total fines due, 
      """)

print(f"""
      {
        non_tows.amount_due_post_tow_eligible.sum() / non_tows.amount_due.sum()
      } share of total fines not paid post tow eligible
      """)



post_eligible_plates = plates_to_tow[plates_to_tow.violations_post_tow_eligible > 0]

post_eligible_non_tows = non_tows[non_tows.violations_post_tow_eligible > 0]

print(f"""
    share of plates with violations post tow eligible date: 
    
      {
        post_eligible_plates.shape[0] / plates_to_tow.shape[0]} or {post_eligible_plates.shape[0]} plates
""")

print(f"""
    share of non-towed plates with violations post tow eligible date: 
    
      {
        post_eligible_non_tows.shape[0] / non_tows.shape[0]} or {post_eligible_non_tows.shape[0]} plates
""")

print(f"""
      stats among these non-towed plates:

     {
        round(post_eligible_non_tows.violations.mean(), 2)
      } violations on average


      {
        round(post_eligible_non_tows.violations_post_tow_eligible.mean(), 2)
      } violations post tow eligible on average
      """)

violation_post_tow_eligible_share = post_eligible_non_tows.shape[0] / non_tows.shape[0]

# *********************
# sample
# *********************

fine_agg_daily_sample = pd.DataFrame()

for date in non_tows.tow_eligible_date.unique():
    non_tows_date = non_tows[non_tows.tow_eligible_date == date]

    n_plates = non_tows_date.shape[0]
    if (random.random() < violation_post_tow_eligible_share):
        sample_plate = non_tows_date[non_tows_date.violations_post_tow_eligible > 0].sample(1)

        sample_plate['n_plates'] = n_plates

        fine_agg_daily_sample = pd.concat([fine_agg_daily_sample, sample_plate])
    else:
        sample_plate = non_tows_date[non_tows_date.violations_post_tow_eligible == 0].sample(1)
        sample_plate['n_plates'] = n_plates
        fine_agg_daily_sample = pd.concat([fine_agg_daily_sample, sample_plate])


# *********************
# save
# *********************

plates_to_tow.to_csv('../../static/data/plates_to_tow.csv', index=False)

fine_agg_daily_sample.to_csv('../../static/data/plates_to_tow_daily_sample.csv', index=False)



