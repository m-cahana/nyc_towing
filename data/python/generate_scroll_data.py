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


# *********************
# filter 
# *********************

# plates that require towing
plates_to_tow = fine_agg[fine_agg.tow_eligible_date.notna()]

plates_to_tow = plates_to_tow[plates_to_tow.tow_eligible_date.dt.year == 2024]

recent_tows = fine_agg.merge(tow_cases, left_on=['plate', 'state', 'license_type'], right_on=['plate_id', 'license_plate_issuing_state', 'license_plate_type'], how='inner')

recent_tows = recent_tows[recent_tows.first_action_date.dt.year == 2024]


# *********************
# plot
# *********************

# sketch plot to later createa in d3

# Set seaborn style
sns.set_style("whitegrid")

# aggregate to date level
plates_to_tow_agg = plates_to_tow.groupby('tow_eligible_date').agg(plates = ('plate', 'count')).reset_index()

recent_tows_agg = recent_tows.groupby('first_action_date').agg(plates = ('plate', 'count')).reset_index()


# create 7 day rolling averages
plates_to_tow_agg['plates_7day'] = plates_to_tow_agg['plates'].rolling(window=7).mean()

recent_tows_agg['plates_7day'] = recent_tows_agg['plates'].rolling(window=7).mean()



# plot
sns.lineplot(data=plates_to_tow_agg, x='tow_eligible_date', y='plates_7day', label='Plates Eligible for Tow')
sns.lineplot(data=recent_tows_agg, x='first_action_date', y='plates_7day', label='Plates Actually Towed')


# *********************
# metric
# *********************


post_eligible_plates = plates_to_tow[plates_to_tow.violations_post_tow_eligible > 0]

print(f"""
    share of plates with violations post tow eligible date: 
    
      {
        post_eligible_plates.shape[0] / plates_to_tow.shape[0]} or {post_eligible_plates.shape[0]} plates
""")

print(f"""
      stats among these plates:

     {
        round(post_eligible_plates.violations.mean(), 2)
      } violations on average


      {
        round(post_eligible_plates.violations_post_tow_eligible.mean(), 2)
      } violations post tow eligible on average
      """)

violation_post_tow_eligible_share = post_eligible_plates.shape[0] / plates_to_tow.shape[0]

# *********************
# sample
# *********************

fine_agg_daily_sample = pd.DataFrame()

for date in plates_to_tow.tow_eligible_date.unique():
    plates_to_tow_date = plates_to_tow[plates_to_tow.tow_eligible_date == date]

    n_plates = plates_to_tow_date.shape[0]
    if (random.random() < violation_post_tow_eligible_share):
        sample_plate = plates_to_tow_date[plates_to_tow_date.violations_post_tow_eligible > 0].sample(1)

        sample_plate['n_plates'] = n_plates

        fine_agg_daily_sample = pd.concat([fine_agg_daily_sample, sample_plate])
    else:
        sample_plate = plates_to_tow_date[plates_to_tow_date.violations_post_tow_eligible == 0].sample(1)
        sample_plate['n_plates'] = n_plates
        fine_agg_daily_sample = pd.concat([fine_agg_daily_sample, sample_plate])


# *********************
# save
# *********************

plates_to_tow.to_csv('../../static/data/plates_to_tow.csv', index=False)

fine_agg_daily_sample.to_csv('../../static/data/plates_to_tow_daily_sample.csv', index=False)



