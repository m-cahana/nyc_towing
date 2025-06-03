import pandas as pd
import datetime as dt
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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

plates_to_tow = plates_to_tow[plates_to_tow.tow_eligible_date >= '2024-01-01']

recent_tows = fine_agg.merge(tow_cases, left_on=['plate', 'state', 'license_type'], right_on=['plate_id', 'license_plate_issuing_state', 'license_plate_type'], how='inner')

recent_tows = recent_tows[recent_tows.first_action_date >= '2024-01-01']


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


post_eligible_plates = plates_to_tow[plates_to_tow.violations_post_tow_eligible > plates_to_tow.violations / 2]

print(f"""
    share of plates with most violations post tow eligible date: 
    
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



# *********************
# save
# *********************

plates_to_tow.to_csv('../../static/data/plates_to_tow.csv', index=False)



