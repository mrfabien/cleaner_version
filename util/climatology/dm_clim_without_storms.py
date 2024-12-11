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
custom_library_path = os.path.abspath('/work/FAC/FGSE/IDYST/tbeucler/default/freddy0218/fabienVED')
sys.path.append(custom_library_path)

import data_process

target_month = int(sys.argv[1])
target_day = int(sys.argv[2])
# Load time series dataset, which contains the landfall date of each storm (though the name of the column hasn't been not well chosen)
dates = pd.read_csv('/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/data/time_series_1h_EU/instantaneous_10m_wind_gust/instantaneous_10m_wind_gust_max.csv')['start_date']

# Load and preprocess the raster dataset
eu_final_raster = xr.open_dataset('/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/maps/eu_final_raster.tif', engine='rasterio').rename({'x': 'longitude', 'y': 'latitude'})

# Parse storm dates
storm_dates = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%S') for date in dates]

# Extract unique month-day combinations with landfall years
storm_month_day_year = [[date.month, date.day, date.year] for date in storm_dates]

ifg = '/work/FAC/FGSE/IDYST/tbeucler/default/raw_data/ECMWF/ERA5/SL/instantaneous_10m_wind_gust/'

# Date specification
year = np.arange(1990,2022,1)

# Define special exclusions for specific years based on month and day
exclusions = {
    (2, 19): [1997],
    (12, 15): [1999],
    (2, 25): [2002],
    (2, 3): [2011],
    (2, 1): [2016],
    (2, 8): [2016],
    (2, 16): [2020],
    (2, 28): [1990],
}

# Helper function to add wrap-around logic for days
def get_extended_days(target_month, target_day):
    base_date = datetime(2000, target_month, target_day)  # Use 2000 as a dummy year for simplicity
    extended_days = [(base_date - timedelta(days=1)).month, (base_date - timedelta(days=1)).day], \
                    [base_date.month, base_date.day], \
                    [(base_date + timedelta(days=1)).month, (base_date + timedelta(days=1)).day]
    return extended_days

# Get the extended range of days
extended_days = get_extended_days(target_month, target_day)

# Collect landfall years for all days in the extended range
landfall_years = []
for month, day in extended_days:
    landfall_years += [mdy[2] for mdy in storm_month_day_year if mdy[0] == month and mdy[1] == day]

# Exclude specific years
excluded_years = []
for month, day in extended_days:
    excluded_years += exclusions.get((month, day), [])
excluded_years += landfall_years
yearin = np.setdiff1d(year, excluded_years)

max_winds_europe = []
for yearz in tqdm(yearin):
    for month, day in extended_days:
        # Skip non-leap years for Feb 29
        if month == 2 and day == 29 and (yearz % 4 != 0 or (yearz % 100 == 0 and yearz % 400 != 0)):
            continue

        # Load dataset
        i10fgpath = f'{ifg}ERA5_{yearz}-{month}_instantaneous_10m_wind_gust.nc'
        i10fg = xr.open_dataset(glob.glob(i10fgpath)[0])

        # Parse date indices
        first_true_index, last_true_index = data_process.parse_date_and_output_list(i10fg, month, day)

        # Preprocess dataset
        i10fg['longitude'] = ((i10fg['longitude'] + 180) % 360) - 180
        i10fg = i10fg.sortby('longitude')
        i10fg_europe = i10fg.sel(latitude=slice(71, 30), longitude=slice(-15, 40))
        i10fg_europe_date = i10fg_europe.isel(time=slice(first_true_index, last_true_index + 1))

        # Calculate maximum wind speed
        max_wind_europe = i10fg_europe_date.max(dim='time')
        max_winds_europe.append(max_wind_europe)

        del i10fg, i10fg_europe
        gc.collect()

# Combine and save results
combined_max = xr.concat(max_winds_europe, dim="time").max('time')
dataset_cut = combined_max.where(eu_final_raster['band_data'] == 1).rio.write_crs("EPSG:4326").squeeze().drop_vars('spatial_ref')

output_path = f"/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/data/climatology/daily_without_storms/climatology_europe_{target_month}_{target_day}.tif"
#output_path = f"test/climatology_europe_{target_month}_{target_day}.tif"
dataset_cut.rio.to_raster(output_path)