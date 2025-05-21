import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# *********************
# constants
# *********************

# Set seaborn style
sns.set_style("whitegrid")

current_date = pd.to_datetime(dt.datetime.now().date())
judgement_date_diff_min = 75 # days
tow_threshold = 350 # usd

# *********************
# data read in 
# *********************

tow_cases = pd.read_csv('../processed/scofftow_case_information.csv')

fine_agg = pd.read_csv('../processed/fine_agg.csv')

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

print(f"""
      {plates_to_tow.shape[0]} plates in judgement
      """)

print(f"""
      {plates_to_tow[plates_to_tow.case_number.isna()].shape[0]} plates never towed
      """)

print(f"""
      average fines in judgement among these plates:
      {plates_to_tow[plates_to_tow.case_number.isna()].fines_in_judgement.mean()}
      """)

# there's a really interesting pattern here where plates that get booted continue to speed a ton after the boot, and soon should be booted again - worth investigating
# pattern is specifically: speed, boot/tow, speed, boot/tow, etc.
plates_to_tow[plates_to_tow.case_number.notna()].sort_values(by='fines_in_judgement', ascending=False).head(10)

plates_to_tow[plates_to_tow.case_number.isna()].sort_values(by='fines_in_judgement', ascending=False).head(10)

# *********************
# plot runaways over time
# *********************

runaway_agg = fine_agg[fine_agg.tow_eligible_date.notna()].groupby('tow_eligible_date').agg(
      runaways = ('plate', 'count')
).reset_index().sort_values(by='tow_eligible_date')

runaway_agg['cumulative_runaways'] = runaway_agg['runaways'].cumsum()

runaway_agg['runaways_7day'] = runaway_agg['runaways'].rolling(window=7).mean()

runaway_agg.plot(x='tow_eligible_date', y='cumulative_runaways')

# *********************
# identify violations post tow eligible date
# *********************

print(f"""
      share of violations post tow eligible date:
      {fine_agg.violations_post_tow_eligible.sum() / fine_agg.violations.sum()}
      """)

print(f"""
      share and number of violations post tow eligible date among tow eligible plates:
      {fine_agg[fine_agg.tow_eligible_date.notna()].violations_post_tow_eligible.sum() / fine_agg[fine_agg.tow_eligible_date.notna()].violations.sum()}
      {fine_agg[fine_agg.tow_eligible_date.notna()].violations_post_tow_eligible.sum()}
      """)


# *********************
# bin
# *********************

# bin plates by violations (rounded to nearest 5)
# label bins as 1-5, 6-10, etc.
bin_ranges = list(range(0, 101, 5))
# lets add a bin for 100+
bin_labels = list([f'{i+1}-{i+5}' for i in bin_ranges[:-1]]) + ['100+']
bin_ranges = bin_ranges + [1e6]
plates_to_tow_2024['violations_bin'] = pd.cut(plates_to_tow_2024['violations'], bins=bin_ranges, labels=bin_labels)

tow_agg_2024 = plates_to_tow_2024.groupby('violations_bin').agg(
      n = ('plate', 'nunique'), 
      tow = ('towed', 'sum')
).reset_index()


tow_agg_2024['tow_share'] = tow_agg_2024.tow / tow_agg_2024.n


# Create bar plot for tow share by violations bin
sns.barplot(data=tow_agg_2024, x='violations_bin', y='tow_share')
plt.title('Share of Plates Towed by Number of Violations (2024)', pad=15)
plt.xlabel('Number of Violations')
plt.ylabel('Share of Plates Towed')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

sns.barplot(data=tow_agg_2024, x='violations_bin', y='n')
plt.title('Number of Plates by Number of Violations (2024)', pad=15)
plt.xlabel('Number of Violations')
plt.ylabel('Number of Plates')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# *********************
# plot entrances
# *********************

plates_to_tow_2024['boot_date'] = pd.to_datetime(plates_to_tow_2024['boot_date'])
plates_to_tow_2024['tow_eligible_date'] = pd.to_datetime(plates_to_tow_2024['tow_eligible_date'])

# Count of plates becoming eligible for tow each date
plates_by_date = plates_to_tow_2024.groupby('tow_eligible_date').agg(
      eligible_plates = ('plate', 'nunique')
).reset_index()

# Count of boots each date using the same dataframe
boots_by_date = plates_to_tow_2024[plates_to_tow_2024.boot_date.notna()].groupby('boot_date').agg(
      boots = ('plate', 'nunique')
).reset_index()

# Calculate 7-day rolling averages
plates_by_date['eligible_plates_7day'] = plates_by_date['eligible_plates'].rolling(window=7).mean()
boots_by_date['boots_7day'] = boots_by_date['boots'].rolling(window=7).mean()


# Plot both smoothed lines
plt.plot(plates_by_date['tow_eligible_date'], plates_by_date['eligible_plates_7day'], 
         label='Eligible for Tow (7-day avg)', linewidth=2)
plt.plot(boots_by_date['boot_date'], boots_by_date['boots_7day'], 
         label='Actually Booted (7-day avg)', linewidth=2)

# Add original data as light scatter points
plt.scatter(plates_by_date['tow_eligible_date'], plates_by_date['eligible_plates'], 
           alpha=0.2, color='blue', s=10)
plt.scatter(boots_by_date['boot_date'], boots_by_date['boots'], 
           alpha=0.2, color='orange', s=10)

plt.title('Daily Counts: Tow-Eligible Plates vs Actually Booted Plates (2024)\n7-Day Rolling Average')
plt.xlabel('Date')
plt.ylabel('Number of Plates')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()


