import gc
import glob
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
from tqdm import tqdm
import sys
import os
import pandas as pd

# Add the path to the custom library
custom_library_path = os.path.abspath('/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/util/climatology/')
sys.path.append(custom_library_path)

import parse_and_daily
from custom_pickle import save_to_pickle

target_month = int(sys.argv[1])
target_day = int(sys.argv[2])

target_month_day = [(target_month, target_day)]

# Load time series dataset, which contains the landfall date of each storm
wind_gust_data = pd.read_csv('/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/data/time_series_1h_EU/instantaneous_10m_wind_gust/instantaneous_10m_wind_gust_max.csv')

# load the storm_dates that contains all the end_date of the storms
storm_data = pd.read_csv('/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/tracks/storm_dates.csv')

# Load and preprocess the raster dataset
eu_final_raster = xr.open_dataset('/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/maps/eu_final_raster.tif', engine='rasterio').rename({'x': 'longitude', 'y': 'latitude'})

# Parse storm dates
#storm_dates = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%S') for date in dates]

# Extract unique month-day-year combinations with landfall years
#storm_month_day_year = [[date.month, date.day, date.year] for date in storm_dates]

ifg = '/work/FAC/FGSE/IDYST/tbeucler/default/raw_data/ECMWF/ERA5/SL/instantaneous_10m_wind_gust/'

# Date specification
year = np.arange(1990, 2022, 1)

# Define special exclusions for specific years based on month and day
#exclusions = {
#    (2, 19): [1997],
#    (12, 15): [1999],
#    (2, 25): [2002],
#    (2, 3): [2011],
#    (2, 1): [2016],
#    (2, 8): [2016],
#    (2, 16): [2020],
#    (2, 28): [1990],
#}

# Convert 'start_date' in wind_gust_data and 'end_date' in storm_data to datetime for matching
wind_gust_data['start_date'] = pd.to_datetime(wind_gust_data['start_date'])
storm_data['end_date'] = pd.to_datetime(storm_data['end_date'])

# Initialize the exclusions dictionary
exclusions = {}

# Loop through the wind_gust_data and match with the corresponding storm in storm_data
for _, gust_row in wind_gust_data.iterrows():
    start_day_month = (gust_row['start_date'].month, gust_row['start_date'].day)
    
    # Match the end_date using the storm_index from wind_gust_data
    matching_storm = storm_data[storm_data['storm_index'] == gust_row['storm_index']]
    
    if not matching_storm.empty:
        end_year = matching_storm.iloc[0]['end_date'].year
        
        # Populate the dictionary
        if start_day_month not in exclusions:
            exclusions[start_day_month] = []
        if end_year not in exclusions[start_day_month]:
            exclusions[start_day_month].append(end_year)

# Winter season months
#winter_months = [1, 2, 3, 10, 11, 12]

# Filter years to exclude storm landfall dates
yearin = year.copy()

# Process each year and winter month-day
daily_data_array = []
for yearz in tqdm(yearin):
    for month, day in target_month_day:
        if month == 2 and day == 29 and (yearz % 4 != 0 or (yearz % 100 == 0 and yearz % 400 != 0)):
            continue

        # Check exclusions
        if (month, day) in exclusions and yearz in exclusions[(month, day)]:
            continue

        # Load dataset
        try:
            i10fgpath = f'{ifg}ERA5_{yearz}-{month}_instantaneous_10m_wind_gust.nc'
            i10fg = xr.open_dataset(glob.glob(i10fgpath)[0])
        except IndexError:

            print(f"File not found for {yearz}-{month}")
            continue

        # Parse date indices
        try:
            first_true_index, last_true_index = parse_and_daily.parse_date_and_output_list(i10fg, month, day)
        except Exception as e:
            print(f"Error parsing dates for {yearz}-{month:02d}-{day:02d}: {e}")
            continue

        # Preprocess dataset
        i10fg['longitude'] = ((i10fg['longitude'] + 180) % 360) - 180
        i10fg = i10fg.sortby('longitude')
        i10fg_europe = i10fg.sel(latitude=slice(71, 30), longitude=slice(-15, 40))
        i10fg_europe_date = i10fg_europe.isel(time=slice(first_true_index, last_true_index + 1))

        # Calculate daily maximum wind speeds and store in a list
        daily_data = i10fg_europe_date.max(dim="time")
        daily_data_cut = daily_data.where(eu_final_raster['band_data'] == 1)
        daily_data_array.append(daily_data_cut)

        del i10fg, i10fg_europe
        gc.collect()

# Save results as a pickle file
output_path = f"/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/data/climatology/daily_winter_season_no_storms/climatology_europe_winter_{month}_{day}.pkl"
save_to_pickle(daily_data_array, output_path)