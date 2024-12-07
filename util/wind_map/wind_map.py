import xarray as xr
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
import numpy as np
from datetime import datetime, timedelta

def open_monthly_nc(variable, year, months, way, level=0):
    datasets = [xr.open_dataset(f'{way}{variable}/ERA5_{year}-{month}_{variable}.nc') for month in months]
    if variable == 'geopotential' and level != 0:
        datasets = [dataset.sel(level=level) for dataset in datasets]
    concated_datasets = xr.concat(datasets, dim='time')
    # reduce the size of the dataset by cutting the eu domain
    concated_datasets = concated_datasets.sel(latitude=slice(70, 34))
    return concated_datasets

def process_data(variable, year, way, level=0):

    year_next = year + 1
    month_act = [10, 11, 12]
    month_next = [1, 2, 3]

    # Open and concatenate datasets
    if year == 1990:
        dataset_act = open_monthly_nc(variable, str(year), month_next, way, level)
        dataset_next = open_monthly_nc(variable, str(year_next), month_next, way, level)
        dataset = xr.concat([dataset_act, dataset_next], dim='time')
        dataset = dataset.chunk({'time': 10})
    elif year == 2021:
        dataset = open_monthly_nc(variable, str(year), month_next, way, level)
    else:
        dataset_act = open_monthly_nc(variable, str(year), month_act, way, level)
        dataset_next = open_monthly_nc(variable, str(year_next), month_next, way, level)
        dataset = xr.concat([dataset_act, dataset_next], dim='time')
        dataset = dataset.chunk({'time': 10})
    
    # Determine the specific variable to extract
    specific_var = next(var for var in dataset.variables if var not in ['longitude', 'latitude', 'time', 'level'])

    return dataset, specific_var

def tiff_max_world(dataset, specific_var, storm_dates, output_file):

    time_landfall = storm_dates['eu_landfall_date'][0]
    time_end = storm_dates['end_date'][0]

    # slice the gust data to the time of landfall to end of storm

    global_storm = dataset.sel(time=slice(time_landfall, time_end))
    global_first_storm_max = global_storm.max(dim='time')

    # Assuming first_storm_max is your xarray DataArray with latitude and longitude
    # Example: first_storm_max['i10fg'] is the variable to plot

    # Step 1: Extract data and coordinates from the DataArray
    data = global_first_storm_max[specific_var].values  # Extract the data values
    lat = global_first_storm_max['latitude'].values  # Extract latitude values
    lon = global_first_storm_max['longitude'].values  # Extract longitude values

    # Step 2a : Wrap longitudes from 0-360 to -180-180
    lon = np.where(lon > 180, lon - 360, lon)  # Adjust longitudes to be in the range -180 to 180

    # Step 2b: Sort the longitude values and the corresponding data
    # This is necessary because the dataset might no longer be ordered properly after adjusting longitudes
    sorted_idx = np.argsort(lon)
    lon = lon[sorted_idx]
    data = data[:, sorted_idx]  # Sort the data accordingly


    # Step 2c: Define the affine transform (with a negative y pixel size to correct for the flipped map)
    transform = from_origin(lon.min(), lat.max(), lon[1] - lon[0], -(lat[1] - lat[0]))  # Note the negative value for the y-direction

    # Step 3: Define the CRS (Coordinate Reference System) for WGS84
    crs_wgs84 = CRS.from_string("EPSG:4326")#from_epsg(4326)  # EPSG code for WGS84

    # Step 4: Set metadata and save the raster file
    with rasterio.open(
        f'{output_file}.tif',  # Output filename
        'w',  # Write mode
        driver='GTiff',  # GeoTIFF format
        height=data.shape[0],  # Number of rows (height)
        width=data.shape[1],  # Number of columns (width)
        count=1,  # Number of bands
        dtype=data.dtype,  # Data type of the array (e.g., float32)
        crs=crs_wgs84,  # Coordinate Reference System (WGS84)
        transform=transform,  # Affine transformation matrix
        nodata=-9999  # Define NoData value
    ) as dst:
        # Step 5: Write the data to the raster file
        dst.write(data, 1)  # Write the first band

    print("Raster saved with WGS84 projection.")

def to_tiff(variable, storm_dates, input_path, output_path, year, nb_hours, level=0):

    #year = int(storm_dates['start_date'][index][0:4])

    dataset,*_ = process_data(variable, year, input_path, level=0)
    #dataset = xr.open_dataset('/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/data/i10fg_dataset/i10fg_dataset.nc')
    #dataset = dataset.sortby('time')

    land_sea_mask = xr.open_dataset('/work/FAC/FGSE/IDYST/tbeucler/default/raw_data/ECMWF/ERA5/SL/land_sea_mask/ERA5_2021-1_land_sea_mask.nc')
    # remove the time dimension
    land_sea_mask = land_sea_mask.sel(time='2021-01-01T00:00:00')

    print(f'Processing data for year {year}...')

   # Iterate through storm dates
    for index in storm_dates.index:
        # Check if the start_date of the storm matches the desired year
        start_date = storm_dates['start_date'][index]
        end_date = storm_dates['end_date'][index]

        # Parse dates into datetime objects
        start_date_dt = datetime.fromisoformat(start_date)
        end_date_dt = datetime.fromisoformat(end_date)
        
        # Define cutoff dates
        cutoff_date_current_year = datetime(year, 3, 31)  # March 31 of the current year
        cutoff_date_next_year = datetime(year + 1, 4, 1)  # March 31 of the next year

        # Check if the storm satisfies the conditions
        if year == 1990:
            if end_date_dt > cutoff_date_next_year:
                #print(f"Skipping storm {index}: Start date {start_date} or end date {end_date} is outside valid range.")
                continue
        else:
            if start_date_dt < cutoff_date_current_year or end_date_dt > cutoff_date_next_year:
                #print(f"Skipping storm {index}: Start date {start_date} or end date {end_date} is outside valid range.")
                continue
        print(f'Processing storm {index}...')
        try:
            time_landfall = storm_dates['eu_landfall_date'][index]
        except KeyError:
            time_landfall = storm_dates['landfall_eu'][index]
        time_end = storm_dates['end_date'][index]
        # skip storms that don't land in EU, denoted as -1 in the landfall date
        if time_landfall == '-1':
            return print(f'Storm that ended on {time_end} didn\'t land in EU')

        # Calculate time range for slicing
        if nb_hours is not None:
            time_landfall_dt = datetime.fromisoformat(time_landfall)
            new_time_landfall_dt = time_landfall_dt + timedelta(hours=nb_hours)
            time_landfall_plus_hours = new_time_landfall_dt.isoformat()
        else:
            time_landfall_plus_hours = time_end

        # Slice the dataset for the storm's time range
        global_storm = dataset.sel(time=slice(time_landfall, time_landfall_plus_hours))    

        if len(global_storm.dims) == 0 or len(global_storm.data_vars) == 0:
            print('Storm doesn\'t reach the number of hours specified')
        
        global_first_storm_max = global_storm.max(dim='time')


        #global_first_storm_max_eu = global_first_storm_max.roll(longitude=180, roll_coords='longitude').sel(latitude=slice(71, 33), longitude=slice(338, 40))
        #global_first_storm_max_eu = global_first_storm_max_eu.roll(longitude=90, roll_coords='longitude')

        land_wind = global_first_storm_max.where(land_sea_mask['lsm'] >= 0.5)
        land_wind = land_wind.assign_coords(time=time_landfall)

        try:
            storm_name_value = storm_dates['storm_name'][index]
        except KeyError:
            storm_name_value = storm_dates['name'][index]

        storm_index_value = storm_dates['storm_index'][index]
        storm_name = f'{storm_index_value}_{storm_name_value}'

        #sorted_data = land_wind[specific_var].sortby(['longitude', 'latitude'])

        land_wind['longitude'] = xr.where(land_wind['longitude'] > 180, land_wind['longitude'] - 360, land_wind['longitude'])

        # Step 2: Sort the dataset by longitude to ensure it's in the right order
        sorted_data = land_wind.sortby('longitude')

        sorted_data_eu = sorted_data.sel(latitude=slice(71, 33), longitude=slice(-12, 40))
        sorted_data_eu = sorted_data_eu.assign_coords(time=time_landfall)

        # setting the projection
        sorted_data_eu = sorted_data_eu.rio.write_crs("EPSG:4326")# sorted_data.rio.write_crs("EPSG:4326")

        sorted_data_reprojected = sorted_data_eu.rio.reproject(
            sorted_data_eu.rio.crs,
            resolution=0.25  # Setting the desired pixel size
        )
        print(f'Saving raster for storm {storm_name}...')
        sorted_data_reprojected.rio.to_raster(f'{output_path}/{storm_name}.tif')

    print(f'Processing for year {year} completed.')
    print('')
    #return sorted_data_reprojected.rio.to_raster(f'{output_path}/{storm_name}.tif')