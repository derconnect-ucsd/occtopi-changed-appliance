import pandas as pd
import plotly.express as px

# Define file paths
# Represents the first appliance (formerly water dispenser)
appliance_one_file_path = "C:/Users/User/Documents/Github/Changed Appliance Project/occtopi-changed-appliance/data/raw/water-data.csv"
# Represents the second appliance (formerly printer)
appliance_two_file_path = "c:/Users/User/Documents/Github/Changed Appliance Project/occtopi-changed-appliance/data/raw/printer_baseline_data.csv"


# Define statistic columns for consistent use
stat_columns_for_analysis = ['count', 'mean',
                             'std', 'min', '25%', '50%', '75%', 'max']

# Load raw data for both datasets, ensuring correct column names and types
appliance_one_raw_df = pd.read_csv(
    appliance_one_file_path, encoding='utf-8-sig')
rename_map_appliance_one = {appliance_one_raw_df.columns[0]: 'Timestamp',
                            appliance_one_raw_df.columns[1]: 'Value'}
appliance_one_raw_df.rename(columns=rename_map_appliance_one, inplace=True)
appliance_one_raw_df['Timestamp'] = pd.to_datetime(
    appliance_one_raw_df['Timestamp'])
appliance_one_raw_df['Value'] = pd.to_numeric(
    appliance_one_raw_df['Value'], errors='coerce')
appliance_one_raw_df.dropna(subset=['Value'], inplace=True)
# Sort by Timestamp before calculating elapsed time
appliance_one_raw_df.sort_values(
    by='Timestamp', inplace=True, ignore_index=True)
if not appliance_one_raw_df.empty:
    min_ts_appliance_one = appliance_one_raw_df['Timestamp'].iloc[0]
    appliance_one_raw_df['Hours_Elapsed'] = (
        appliance_one_raw_df['Timestamp'] - min_ts_appliance_one).dt.total_seconds() / 3600
else:
    appliance_one_raw_df['Hours_Elapsed'] = pd.Series(
        dtype='float64')  # Ensure column exists for concat
appliance_one_raw_df['DataSource'] = 'Appliance One'

# Determine the offset for the second appliance's data
max_hours_offset_for_appliance_two = 0.0
if 'Hours_Elapsed' in appliance_one_raw_df.columns and not appliance_one_raw_df['Hours_Elapsed'].dropna().empty:
    max_hours_offset_for_appliance_two = appliance_one_raw_df['Hours_Elapsed'].max(
    )

appliance_two_raw_df = pd.read_csv(
    appliance_two_file_path, encoding='utf-8-sig')

# Select and rename necessary columns for Appliance Two (Printer Baseline Data)
# Columns from printer_baseline_data.csv: _time, voltage, current
# This step also effectively removes unused columns as requested.
columns_to_select_appliance_two = ['_time', 'voltage', 'current']
appliance_two_raw_df = appliance_two_raw_df[columns_to_select_appliance_two]

rename_map_appliance_two = {'_time': 'Timestamp',
                            'voltage': 'Voltage',
                            'current': 'Current'}
appliance_two_raw_df.rename(columns=rename_map_appliance_two, inplace=True)

# Convert Timestamp to datetime
appliance_two_raw_df['Timestamp'] = pd.to_datetime(
    appliance_two_raw_df['Timestamp'], errors='coerce', format='mixed')

# Convert Voltage and Current to numeric, coercing errors
appliance_two_raw_df['Voltage'] = pd.to_numeric(
    appliance_two_raw_df['Voltage'], errors='coerce')
appliance_two_raw_df['Current'] = pd.to_numeric(
    appliance_two_raw_df['Current'], errors='coerce')

# Calculate Wattage (Value = Voltage * Current)
appliance_two_raw_df['Value'] = appliance_two_raw_df['Voltage'] * \
    appliance_two_raw_df['Current']

appliance_two_raw_df.dropna(subset=['Timestamp', 'Value'], inplace=True)
# Drop intermediate Voltage and Current columns as 'Value' (wattage) is the target
appliance_two_raw_df.drop(
    columns=['Voltage', 'Current'], inplace=True, errors='ignore')

# Sort by Timestamp before calculating elapsed time
appliance_two_raw_df.sort_values(
    by='Timestamp', inplace=True, ignore_index=True)

appliance_two_raw_df['Hours_Relative_Internal'] = pd.Series(
    dtype='float64')  # For its own first 4 hours
appliance_two_raw_df['Hours_Elapsed'] = pd.Series(
    dtype='float64')  # For combined timeline

if not appliance_two_raw_df.empty:
    min_ts_appliance_two = appliance_two_raw_df['Timestamp'].iloc[0]
    appliance_two_raw_df['Hours_Relative_Internal'] = (
        appliance_two_raw_df['Timestamp'] - min_ts_appliance_two).dt.total_seconds() / 3600
    # Add the offset from the first appliance's data
    appliance_two_raw_df['Hours_Elapsed'] = appliance_two_raw_df['Hours_Relative_Internal'] + \
        max_hours_offset_for_appliance_two
appliance_two_raw_df['DataSource'] = 'Appliance Two'

# Combine the processed data
combined_df = pd.concat(
    [appliance_one_raw_df, appliance_two_raw_df], ignore_index=True)

print("\n--- Combined Data DataFrame ---")
print(combined_df.head())

if not combined_df.empty and 'Hours_Elapsed' in combined_df.columns and not combined_df['Hours_Elapsed'].dropna().empty:
    fig_elapsed_time_comparison = px.line(
        combined_df,
        x='Hours_Elapsed',
        y='Value',
        color='DataSource',
        title='Comparison of Data by Hours Since Start (Appliance One vs. Appliance Two)',
        labels={'Hours_Elapsed': 'Hours Since Start of Data',
                'Value': 'Value (watts)'}
    )
    fig_elapsed_time_comparison.show()
else:
    print("\n--- No data to plot after processing. ---")

# --- Comparison: Appliance One (Last 4 Hrs) vs. Appliance Two (First 4 Hrs) ---
print("\n\n--- Comparison: Appliance One (Last 4 Hrs) vs. Appliance Two (First 4 Hrs) ---")

stats_last_4h_appliance_one = None
stats_first_4h_appliance_two = None

# 1. Prepare and get stats for Appliance One (Last 4 hours)
if not appliance_one_raw_df.empty and 'Hours_Elapsed' in appliance_one_raw_df.columns and not appliance_one_raw_df['Hours_Elapsed'].dropna().empty:
    max_hours_appliance_one = appliance_one_raw_df['Hours_Elapsed'].max()
    # Filter for the last 4 hours (or less if total duration is < 4 hours)
    last_4h_appliance_one_df = appliance_one_raw_df[
        (appliance_one_raw_df['Hours_Elapsed'] > max_hours_appliance_one - 4) &
        (appliance_one_raw_df['Hours_Elapsed'] <= max_hours_appliance_one)
    ]
    if not last_4h_appliance_one_df.empty:
        stats_last_4h_appliance_one = last_4h_appliance_one_df['Value'].describe(
        )
        print("\n--- Statistics for Appliance One (Last 4 Hours of its operation) ---")
        print(stats_last_4h_appliance_one)
    else:
        print("\n--- Appliance One has no data in its last 4 hours of operation (or ran for 0 hours). ---")
else:
    print("\n--- Appliance One data is empty or 'Hours_Elapsed' is missing/empty. Cannot analyze its last 4 hours. ---")

# 2. Prepare and get stats for Appliance Two (First 4 hours)
if not appliance_two_raw_df.empty and 'Hours_Relative_Internal' in appliance_two_raw_df.columns and not appliance_two_raw_df['Hours_Relative_Internal'].dropna().empty:
    # Filter for the first 4 hours (or less if total duration is < 4 hours)
    first_4h_appliance_two_df = appliance_two_raw_df[
        (appliance_two_raw_df['Hours_Relative_Internal'] >= 0) &
        # Using < 4 for 0-3.999... hours
        (appliance_two_raw_df['Hours_Relative_Internal'] < 4)
    ]
    if not first_4h_appliance_two_df.empty:
        stats_first_4h_appliance_two = first_4h_appliance_two_df['Value'].describe(
        )
        print("\n--- Statistics for Appliance Two (First 4 Hours of its operation) ---")
        print(stats_first_4h_appliance_two)
    else:
        print("\n--- Appliance Two has no data in its first 4 hours of operation (or ran for 0 hours). ---")
else:
    print("\n--- Appliance Two data is empty or 'Hours_Relative_Internal' is missing/empty. Cannot analyze its first 4 hours. ---")

# 3. Display and Compare Statistics
if stats_last_4h_appliance_one is not None and stats_first_4h_appliance_two is not None:
    print("\n\n--- Differences in Statistics (Appliance Two First 4Hrs - Appliance One Last 4Hrs) ---")
    any_meaningful_difference_printed_new_comp = False
    for stat_name in stat_columns_for_analysis:
        val_a1 = stats_last_4h_appliance_one.get(stat_name)
        val_a2 = stats_first_4h_appliance_two.get(stat_name)

        if pd.notna(val_a1) and pd.notna(val_a2):
            absolute_difference = val_a2 - val_a1
            print(f"\n  Statistic: {stat_name}")
            print(f"    Appliance One (Last 4H): {val_a1:,.4f}")
            print(f"    Appliance Two (First 4H): {val_a2:,.4f}")
            print(
                f"    Absolute Difference (A2 - A1): {absolute_difference:,.4f}")
            any_meaningful_difference_printed_new_comp = True

            if val_a1 != 0:
                percentage_difference = (absolute_difference / val_a1) * 100
                print(
                    f"    Percentage Difference: {percentage_difference:,.2f}% (relative to Appliance One's value)")
            else:
                if absolute_difference == 0:  # Implies A2 value was also 0
                    print(
                        f"    Percentage Difference: 0.00% (Appliance One value is 0, Appliance Two value is also 0)")
                else:  # A1 is 0, A2 is non-zero
                    print(
                        f"    Percentage Difference: Inf or N/A (Appliance One value is 0, Appliance Two value is {val_a2:,.4f})")
        elif pd.notna(val_a1) or pd.notna(val_a2):  # Only one has data for this stat
            print(f"\n  Statistic: {stat_name}")
            print(
                f"    Appliance One (Last 4H): {val_a1 if pd.notna(val_a1) else 'N/A'}")
            print(
                f"    Appliance Two (First 4H): {val_a2 if pd.notna(val_a2) else 'N/A'}")
            print(f"    Absolute Difference (A2 - A1): N/A (one or both values missing)")
            any_meaningful_difference_printed_new_comp = True  # Still print if one has data

    if not any_meaningful_difference_printed_new_comp:
        print("No comparable statistics found (e.g., one or both appliances had no data in the specified periods).")
elif stats_last_4h_appliance_one is None and stats_first_4h_appliance_two is None:
    print("\n--- Cannot compare: No statistics available for either Appliance One (last 4h) or Appliance Two (first 4h). ---")
else:
    print("\n--- Cannot compare: Statistics are missing for one of the appliances in the specified periods. ---")
