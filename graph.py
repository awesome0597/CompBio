import pandas as pd
import matplotlib.pyplot as plt

# read data from stats.csv
df = pd.read_csv('stats.csv')

# convert non-numeric columns to numeric types
df['25 percentile'] = pd.to_numeric(df['25 percentile'], errors='coerce')
df['50 percentile'] = pd.to_numeric(df['50 percentile'], errors='coerce')
df['75 percentile'] = pd.to_numeric(df['75 percentile'], errors='coerce')
df['final percentile'] = pd.to_numeric(df['final percentile'], errors='coerce')

# group by 'L value' and ' P value' and 'S1 value' and calculate average of each group
grouped = df.groupby(['L value', 'P value', 'S1 value']).mean()
print(grouped)
# for each row in grouped, plot a line graph using the values in the columns '25 percentile', '50 percentile', '75 percentile' and 'final percentile'
# y axis should be each column by order
# x axis should be the percentile
# increase size of plt
plt.figure(figsize=(20, 15))
for index, row in grouped.iterrows():
    if index[0] == 0:
        linestyle = '--'
    else:
        linestyle = '-'
    plt.plot([row['25 percentile'], row['50 percentile'],  row['75 percentile'], 100],
             [25, 50, 75, row['final percentile']],
             label='L: ' + str(index[0]) + ' P: ' + str(index[1]) + ' S1: ' + str(index[2]), linestyle=linestyle)
# set title and labels in big font
plt.title('L vs P vs S1', fontsize=20)
plt.xlabel('generation', fontsize=20)
plt.ylabel('percentile', fontsize=20)


# make x axis ticks 25, 50, 75, 100
plt.xticks([25, 50, 75, 100])

# show legend on the right
plt.legend(loc='lower right')

# show graph
plt.show()