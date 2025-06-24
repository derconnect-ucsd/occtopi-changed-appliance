import pandas as pd
from pathlib import Path
import os

import plotly.express as px
import plotly.graph_objects as go

# Set the path to the raw data folder
data_folder = Path("data/raw")

# Get all CSV files in the raw data folder
csv_files = list(data_folder.glob("*.csv"))

# Dictionary to store dataframes
dataframes = {}

# Process each CSV file
for csv_file in csv_files:
	# Read CSV into dataframe
	df = pd.read_csv(csv_file)
	
	# Store dataframe with filename as key
	file_key = csv_file.stem
	dataframes[file_key] = df
	
	# Create a basic plotly figure for each dataframe
	# Adjust the plot type based on your data structure
	if len(df.columns) >= 2:
		# Line plot using first two columns
		fig = px.line(df, x=df.columns[0], y=df.columns[1], 
					 title=f"Data from {file_key}")
	else:
		# Line plot for single column
		fig = px.line(df, y=df.columns[0], 
					 title=f"Data from {file_key}")
	
	# Show the figure
	fig.show()
	
	print(f"Processed {csv_file.name} - Shape: {df.shape}")

print(f"Total files processed: {len(dataframes)}")

# Keep the script running so figures can display
if dataframes:
	print("Figures should now be opening in your browser...")
	input("Press Enter to exit...")
else:
	print("No CSV files found in the data/raw folder.")