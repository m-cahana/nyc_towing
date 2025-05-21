import pandas as pd
import numpy as np
from scipy import stats


# ******************
# read in
# ******************
fines = pd.read_csv('../processed/school_zone_fines_2024.csv')

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

fines = fines.drop_duplicates()

print(f'unique years: {fines.issue_date.dt.year.unique()}')



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

# **************
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
# save
# ******************

plot_data.to_csv('../../static/data/bar_plot_data.csv', index=False)

