import pandas as pd
import plotly.express as px
from datetime import date, timedelta, datetime

# Read the CSV file into a DataFrame
df = pd.read_csv(
    "C:/Users/User/Documents/Github/Changed Appliance Project/occtopi-changed-appliance/data/raw/water-dispenser-full-data.csv")
df.columns = ['Timestamp', 'Value']
# Convert the 'Timestamp' column to datetime objects. The format is already a string representation of a datetime.
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values(by='Timestamp').reset_index(drop=True)

print("--- Calculating Daily Statistics ---")
# Group by the date part of 'Timestamp' and get descriptive statistics for 'Value'

daily_summary_stats_df = df.groupby(df['Timestamp'].dt.date)[
    'Value'].describe()

daily_summary_stats_df.index = pd.to_datetime(daily_summary_stats_df.index)
daily_summary_stats_df.index.name = 'Date'

print("\n--- Daily Statistics Summary DataFrame (first 5 rows) ---")
print(daily_summary_stats_df.head())

print("\n--- Plotting Daily Statistics Over Time ---")

fig_daily_stats = px.line(
    daily_summary_stats_df,
    title='Daily Power Usage Statistics Over Time',
    labels={'value': 'Statistic Value', 'variable': 'Statistic Metric'},
    markers=True
)
fig_daily_stats.show()


print("\n--- Calculating 4-Hourly Statistics ---")

df['4Hour_Interval'] = df['Timestamp'].dt.floor(
    '4h')  # Create a new column for 4-hour intervals

# Group by the 4-hour interval and get descriptive statistics
four_hourly_summary_stats_df = df.groupby('4Hour_Interval')['Value'].describe()

print("\n--- 4-Hourly Statistics Summary DataFrame (first 5 rows) ---")
print(four_hourly_summary_stats_df.head())

print("\n--- Plotting 4-Hourly Statistics Over Time ---")

fig_four_hourly_stats = px.line(
    four_hourly_summary_stats_df,
    title='4-Hourly Power Usage Statistics Over Time',
    labels={'value': 'Statistic Value', 'variable': 'Statistic Metric'},
    markers=True
)
fig_four_hourly_stats.show()

# Plot a normal chart of the dataframe
print("\n--- Overall Power Usage Chart (All Data) ---")
fig = px.line(df,
              x='Timestamp',
              y='Value',
              title='Power Usage Chart (All Data)',
              labels={'Timestamp': 'Time (hours) and Day', 'Value': 'Watts'},
              markers=False
              )
fig.show()
