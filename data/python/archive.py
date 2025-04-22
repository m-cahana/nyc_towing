

# create two bins: 1-14, and 15+
bin_ranges = [1, 14, 1e6]
bin_labels = ['1-14', '15+']
plate_id_agg['violations_bin_minimal'] = pd.cut(plate_id_agg['total_violations'], bins=bin_ranges, labels=bin_labels)


# compute share of fines paid by bin
plot_data_minimal = plate_id_agg.groupby('violations_bin_minimal').agg(
    fines_paid = ('total_payment_amount', 'sum'),
    total_fines = ('total_fines', 'sum'), 
    total_violations = ('total_violations', 'sum'),
    n_plates = ('plate', 'nunique'),
    total_penalties = ('total_penalties', 'sum'),
    total_interest = ('total_interest', 'sum'),
).reset_index()

plot_data_minimal['share_of_fines_paid'] = (plot_data_minimal['fines_paid'] / plot_data_minimal['total_fines']) * 100

plot_data_minimal['total_outstanding_fines'] = plot_data_minimal['total_fines'] - plot_data_minimal['fines_paid']

sns.barplot(x='violations_bin_minimal', y='share_of_fines_paid', data=plot_data_minimal)
plt.xticks(rotation=45)


sns.barplot(x='violations_bin_minimal', y='total_outstanding_fines', data=plot_data_minimal)
plt.xticks(rotation=45)

# plot penalties
sns.lineplot(x='violations_bin', y='penalty_share', data=plot_data[plot_data.violations_bin <= '91-100'])



# plot every point under 100 violations (using seaborn), and add a regression line
# this turns out to be totally unreadable, bin plot above is better
sns.regplot(x='total_violations', y='share_of_fines_paid', data=plate_id_agg[plate_id_agg.total_violations <= 100])
# label 
plt.xlabel('School Zone Violations', fontsize=14)
plt.ylabel('Share of Fines Paid (%)', fontsize=14)
plt.title('Drivers are less likely \n to pay fines the more they violate', fontsize=16)

plt.clf()

plt.plot(plot_data[(plot_data.violations_bin <= 100) & (plot_data.violations_bin > 30)]['violations_bin'], plot_data[(plot_data.violations_bin <= 100) & (plot_data.violations_bin > 30)]['n_plates'], marker='o')
plt.xlabel('Total Violations')
plt.ylabel('Number of Plates')