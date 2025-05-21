import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt

# ******************
# read in
# ******************
fines = pd.read_csv('../processed/school_zone_fines_2024.csv')

violations = pd.read_csv('../processed/school_zone_violations.csv')

# ******************
# clean
# ******************

fines['issue_date'] = pd.to_datetime(fines['issue_date'])

fines['total_fine'] = (
    fines['fine_amount'] + 
    fines['penalty_amount'] + 
    fines['interest_amount'] - 
    fines['reduction_amount']
)

print(f'unique years: {fines.issue_date.dt.year.unique()}')

# ******************
# explore
# ******************

print(f"""percent of fines still owed:
      {round((fines.amount_due.sum() / fines.total_fine.sum()) * 100, 2)}%
      """)

print(f"""percent of fines paid:
    {round((fines.payment_amount.sum() /
    fines.total_fine.sum() *  100), 2)}%
    """
)

print(f"""dollar amount still owed:
      ${round(fines.amount_due.sum(), 2)}
      """)

# ******************
# extreme offenders
# ******************

extreme_offenders = violations[
    (violations.school_zone_violations >=15) 
    ]

print(f'extreme offenders: {len(extreme_offenders)}')

extreme_offender_fines = fines.merge(
    extreme_offenders, 
    left_on = 'plate', 
    right_on = 'plate_id', 
    how = 'inner')

print(f""" share of fines from extreme offenders:
      {round(extreme_offender_fines.total_fine.sum() / fines.total_fine.sum() * 100, 2)}%
      """)


print(f"""extreme offenders: percent of fines still owed:
      {round((extreme_offender_fines.amount_due.sum() / extreme_offender_fines.total_fine.sum()) * 100, 2)}%
      """)

print(f"""extreme offenders: percent of fines paid:
    {round((extreme_offender_fines.payment_amount.sum() /
    extreme_offender_fines.total_fine.sum() *  100), 2)}%
    """
)

print(f"""extreme offenders: dollar amount still owed:
      ${round(extreme_offender_fines.amount_due.sum(), 2)}
      """)

# ******************
# aggregate by plate id
# ******************

plate_id_agg = fines.groupby('plate').agg(
    total_fines = ('total_fine', 'sum'),
    total_amount_due = ('amount_due', 'sum'),
    total_payment_amount = ('payment_amount', 'sum'),
    total_violations = ('plate', 'count'), 
    total_penalties = ('penalty_amount', 'sum'),
    total_interest = ('interest_amount', 'sum'),
).reset_index()

plate_id_agg['share_of_fines_paid'] = plate_id_agg['total_payment_amount'] / plate_id_agg['total_fines']

plate_id_agg = plate_id_agg.sort_values(by='total_violations', ascending=False)

# ******************
# aggregate by bin
# ******************


# bin plates by violations (rounded to nearest 5)
# label bins as 1-5, 6-10, etc.
bin_ranges = list(range(0, 101, 5))
# lets add a bin for 100+
bin_labels = list([f'{i+1}-{i+5}' for i in bin_ranges[:-1]]) + ['100+']
bin_ranges = bin_ranges + [1e6]
plate_id_agg['violations_bin'] = pd.cut(plate_id_agg['total_violations'], bins=bin_ranges, labels=bin_labels)


# compute share of fines paid by bin
plot_data = plate_id_agg.groupby('violations_bin').agg(
    fines_paid = ('total_payment_amount', 'sum'),
    total_fines = ('total_fines', 'sum'), 
    total_violations = ('total_violations', 'sum'),
    n_plates = ('plate', 'nunique'),
    total_penalties = ('total_penalties', 'sum'),
    total_interest = ('total_interest', 'sum'),
    share_of_fines_paid_driver_avg = ('share_of_fines_paid', 'mean'),
).reset_index()

# compute share of fines paid by bin
plot_data['share_of_fines_paid'] = (plot_data['fines_paid'] / plot_data['total_fines']) * 100
plot_data['share_of_fines_paid_driver_avg'] = (plot_data['share_of_fines_paid_driver_avg'] * 100)

# compute averages 
plot_data['average_fines'] = plot_data['total_fines'] / plot_data['n_plates']
plot_data['average_penalties'] = plot_data['total_penalties'] / plot_data['n_plates']
plot_data['average_interest'] = plot_data['total_interest'] / plot_data['n_plates']

# compute outstanding fines
plot_data['outstanding_fines'] = plot_data['total_fines'] - plot_data['fines_paid']
plot_data['average_outstanding_fine'] = plot_data['outstanding_fines'] / plot_data['n_plates']

# compute penalty share
plot_data['penalty_share'] = (plot_data['total_penalties'] / plot_data['total_fines']) * 100

# ******************
# plot 
# ******************

sns.set_theme(style="whitegrid")


# plot a barplot using seaborn
sns.barplot(x='violations_bin', y='share_of_fines_paid_driver_avg', data=plot_data)
plt.xticks(rotation=45)
# label 
plt.xlabel('School Zone Violations', fontsize=14)
plt.ylabel('Share of Fines Paid (%)', fontsize=14)
plt.title('Drivers are less likely \n to pay fines the more they violate', fontsize=16)
plt.tight_layout()
plt.savefig('figures/share_of_fines_paid.png')


# clear
plt.clf()

# plot outstanding fines
sns.barplot(x='violations_bin', y='average_outstanding_fine', data=plot_data)
plt.xticks(rotation=45)
plt.xlabel('School Zone Violations', fontsize=14)
plt.ylabel('Unpaid Fines per Driver ($)', fontsize=14)
plt.title('Extreme offenders have very large fines still unpaid', fontsize=16)
plt.tight_layout()
plt.savefig('figures/average_outstanding_fine.png')

plt.clf()

# plot penalties
sns.barplot(x='violations_bin', y='average_penalties', data=plot_data)
plt.xticks(rotation=45)
plt.xlabel('School Zone Violations', fontsize=14)
plt.ylabel('Penalties Charged per Driver ($)', fontsize=14)
plt.title("Because they don't pay on time, extreme offenders \n have accrued large penalties", fontsize=16)
plt.tight_layout()
plt.savefig('figures/average_penalties.png')


plt.clf()

# plot interest
sns.barplot(x='violations_bin', y='average_interest', data=plot_data)
plt.xticks(rotation=45)
plt.xlabel('School Zone Violations', fontsize=14)
plt.ylabel('Interest Charged per Driver ($)', fontsize=14)
plt.title("Because they don't pay on time, \n extreme offenders have accrued large interest fees", fontsize=16)
plt.tight_layout()
plt.savefig('figures/average_interest.png')

