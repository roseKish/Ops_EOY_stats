# Operations End of Year Analysis
# Plotting


import matplotlib.pyplot as plt


sns.lmplot(x='seconds_duration', y='size_mw', hue = 'Provider', data=df[df.size_mw < 500])
plt.xlabel('Duration (seconds)')
plt.ylabel('Area scanned (MW)')
plt.show()

sns.lmplot(x='seconds_duration', y='size_mw', hue = 'year', data=df[df.size_mw < 500])
plt.xlabel('Duration (seconds)')
plt.ylabel('Area scanned (MW)')
plt.show()

# pie chart for total GW
labels_GW = ['2017', '2018', '2019', '2020', '2021']
data_GW = [7.13, 15.46, 35.38, 28.42, 41.55]

# pie chart for total GW scanned by year
plt.pie(data_GW, labels = labels_GW, colors = colors, autopct='%.0f%%')
plt.show()

# bar chart for total GW scanned by year
plt.bar(labels_GW, height = data_st)
plt.xlabel('Year')
plt.ylabel('Total GW Scanned')
plt.show()

# pie chart for total sites scanned
labels_st = ['2017', '2018', '2019', '2020', '2021']
data_st = [586, 1238, 1533, 1870, 2803]

colors = sns.color_palette('colorblind')[0:5]

# pie chart for total sites scanned by year
plt.pie(data_st, labels = labels_st, colors = colors, autopct='%.0f%%')
plt.show()


# bar chart for total sites scanned by year
plt.bar(labels_st, height = data_st)
plt.xlabel('Year')
plt.ylabel('Total Sites Scanned')
plt.show()
