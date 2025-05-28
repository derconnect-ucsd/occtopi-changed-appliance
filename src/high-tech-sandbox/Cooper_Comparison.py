import pandas as pd
import plotly.express as px

# Define file paths
water_dispenser_file_path = "C:/Users/User/Documents/Github/Changed Appliance Project/occtopi-changed-appliance/data/raw/water-data.csv"
printer_file_path = "c:/Users/User/Documents/Github/Changed Appliance Project/occtopi-changed-appliance/data/raw/printer-data.csv"  # Path from context

# Load raw data for both datasets, ensuring correct column names and types
water_dispenser_raw_df = pd.read_csv(
    water_dispenser_file_path, encoding='utf-8-sig')
rename_map_water = {water_dispenser_raw_df.columns[0]: 'Timestamp',
                    water_dispenser_raw_df.columns[1]: 'Value'}
water_dispenser_raw_df.rename(columns=rename_map_water, inplace=True)
water_dispenser_raw_df['Timestamp'] = pd.to_datetime(
    water_dispenser_raw_df['Timestamp'])
water_dispenser_raw_df['Value'] = pd.to_numeric(
    water_dispenser_raw_df['Value'], errors='coerce')
water_dispenser_raw_df.dropna(subset=['Value'], inplace=True)
# Sort by Timestamp before calculating elapsed time
water_dispenser_raw_df.sort_values(
    by='Timestamp', inplace=True, ignore_index=True)
if not water_dispenser_raw_df.empty:
    min_ts_water = water_dispenser_raw_df['Timestamp'].iloc[0]
    water_dispenser_raw_df['Hours_Elapsed'] = (
        water_dispenser_raw_df['Timestamp'] - min_ts_water).dt.total_seconds() / 3600
else:
    water_dispenser_raw_df['Hours_Elapsed'] = pd.Series(
        dtype='float64')  # Ensure column exists for concat
water_dispenser_raw_df['DataSource'] = 'Water Dispenser'

# Determine the offset for the printer data
max_hours_offset_for_printer = 0.0
if 'Hours_Elapsed' in water_dispenser_raw_df.columns and not water_dispenser_raw_df['Hours_Elapsed'].dropna().empty:
    max_hours_offset_for_printer = water_dispenser_raw_df['Hours_Elapsed'].max(
    )


printer_raw_df = pd.read_csv(printer_file_path, encoding='utf-8-sig')
rename_map_printer = {printer_raw_df.columns[0]: 'Timestamp',
                      printer_raw_df.columns[1]: 'Value'}
printer_raw_df.rename(columns=rename_map_printer, inplace=True)
printer_raw_df['Timestamp'] = pd.to_datetime(printer_raw_df['Timestamp'])
printer_raw_df['Value'] = pd.to_numeric(
    printer_raw_df['Value'], errors='coerce')
printer_raw_df.dropna(subset=['Value'], inplace=True)
# Sort by Timestamp before calculating elapsed time
printer_raw_df.sort_values(by='Timestamp', inplace=True, ignore_index=True)
if not printer_raw_df.empty:
    min_ts_printer = printer_raw_df['Timestamp'].iloc[0]
    # Calculate relative hours first
    printer_hours_relative = (
        printer_raw_df['Timestamp'] - min_ts_printer).dt.total_seconds() / 3600
    # Add the offset from the water dispenser data
    printer_raw_df['Hours_Elapsed'] = printer_hours_relative + \
        max_hours_offset_for_printer
else:
    printer_raw_df['Hours_Elapsed'] = pd.Series(
        dtype='float64')  # Ensure column exists for concat
printer_raw_df['DataSource'] = 'Printer'

# Combine the processed data
combined_df = pd.concat(
    [water_dispenser_raw_df, printer_raw_df], ignore_index=True)

print("\n--- Combined Data DataFrame ---")
print(combined_df.head())

if not combined_df.empty and 'Hours_Elapsed' in combined_df.columns and not combined_df['Hours_Elapsed'].dropna().empty:
    fig_elapsed_time_comparison = px.line(
        combined_df,
        x='Hours_Elapsed',
        y='Value',
        color='DataSource',
        title='Comparison of Data by Hours Since Start (Water Dispenser vs. Printer)',
        labels={'Hours_ Elapsed': 'Hours Since Start of Data',
                'Value': 'Value (watts)'}
    )
    fig_elapsed_time_comparison.show()
else:
    print("\n--- No data to plot after processing. ---")

# Calculate 4-hourly statistics for the combined data
print("\n--- Calculating 4-Hourly Statistics for Combined Data ---")

if not combined_df.empty and 'Hours_Elapsed' in combined_df.columns and not combined_df['Hours_Elapsed'].dropna().empty:
    combined_df['Elapsed_4H_Interval_Start'] = (
        combined_df['Hours_Elapsed'] // 4) * 4

    four_hourly_combined_stats_df = combined_df.groupby(
        ['Elapsed_4H_Interval_Start', 'DataSource'])['Value'].describe().reset_index()

    print("\n--- 4-Hourly Combined Statistics Summary DataFrame (first 5 rows) ---")
    print(four_hourly_combined_stats_df.head())

    print("\n--- Plotting 4-Hourly Combined Statistics by Elapsed Time ---")

    # Melt the DataFrame to long format for plotting multiple statistics
    four_hourly_combined_stats_melted = four_hourly_combined_stats_df.melt(
        id_vars=['Elapsed_4H_Interval_Start', 'DataSource'],
        value_vars=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'],
        var_name='Statistic Metric',
        value_name='Statistic Value'
    )

    fig_four_hourly_combined_stats = px.line(
        four_hourly_combined_stats_melted,
        x='Elapsed_4H_Interval_Start',
        y='Statistic Value',
        color='DataSource',
        line_dash='Statistic Metric',  # Use line_dash to differentiate metrics
        title='4-Hourly Combined Statistics by Elapsed Time',
        labels={'Elapsed_4H_Interval_Start': 'Start of 4-Hour Interval (Hours Since Start)',
                'Statistic Value': 'Statistic Value'},
        markers=True
    )
    fig_four_hourly_combined_stats.show()
else:
    print("\n--- Not enough data to calculate or plot 4-hourly statistics based on elapsed time. ---")
