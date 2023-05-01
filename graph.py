import pandas as pd
import matplotlib.pyplot as plt

# sort stats.csv by 'L value' and ' P value' and 'S1 value' in file

# read data from stats.csv
df = pd.read_csv('stats.csv')

# remove any row with p_value = 0.5
df = df[df['P value'] != 0.5]
# convert non-numeric columns to numeric types
df['25 percentile'] = pd.to_numeric(df['25 percentile'], errors='coerce').fillna(0)
df['50 percentile'] = pd.to_numeric(df['50 percentile'], errors='coerce').fillna(0)
df['75 percentile'] = pd.to_numeric(df['75 percentile'], errors='coerce').fillna(0)
df['final percentile'] = pd.to_numeric(df['final percentile'], errors='coerce').fillna(0)

# group by 'L value' and ' P value' and 'S1 value' and calculate average of each group
grouped = df.groupby(['L value', 'P value', 'S1 value']).mean()
# remove from dataframe any group whos mean 25 percentile is more than 10% away from median 25 percentile
grouped = grouped[abs(grouped['25 percentile'] - grouped['25 percentile'].median()) < grouped['25 percentile'].median() * 0.1]
# remove from dataframe any group whos mean 50 percentile is more than 10% away from median 50 percentile
grouped = grouped[abs(grouped['50 percentile'] - grouped['50 percentile'].median()) < grouped['50 percentile'].median() * 0.1]
# remove from dataframe any group whos mean 75 percentile is more than 10% away from median 75 percentile
grouped = grouped[abs(grouped['75 percentile'] - grouped['75 percentile'].median()) < grouped['75 percentile'].median() * 0.1]
# display only first 5 rows
print(grouped)
# create new dataframe containing groups with L=0,1,3,5
grouped = grouped.loc[[0, 1, 3, 5]]
plt.figure(figsize=(20, 15))
for index, row in grouped.iterrows():
    if index[0] == 0:
        # make linestyle dashed if L=0
        linestyle = '--'
    elif index[0] == 1:
        # make linestyle dotted if L=1
        linestyle = ':'
    elif index[0] == 3:
        # make linestyle loose dotted if L=3
        linestyle = '-.'
    else:
        # make linestyle solid if L=5
        linestyle = '-'

# grouped = grouped.loc[[0, 5]]
#
# plt.figure(figsize=(20, 15))
# for index, row in grouped.iterrows():
#     if index[0] == 0:
#         linestyle = '--'
#     else:
#         linestyle = '-'
    plt.plot([25, 50, 75, row['final percentile']],
             [row['25 percentile'], row['50 percentile'], row['75 percentile'], 100],
             label='L: ' + str(index[0]) + ' P: ' + str(index[1]) + ' S1: ' + str(index[2]), linestyle=linestyle)
# set title and labels in big font
plt.title('L 0,1,3,5 vs P vs S1, 10% from median', fontsize=20)
plt.xlabel('percentile', fontsize=20)
plt.ylabel('generation', fontsize=20)

# make x axis ticks 25, 50, 75, 100
plt.xticks([25, 50, 75, 100])

# show legend on the right
plt.legend(loc='lower right')

# show graph
plt.show()
