import pandas as pd
import xarray as xr
import time_series

def process_daily_climatology(file_path, cluster_data, name, lat_min=35, lat_max=75, lon_min=-10, lon_max=25):
    """
    Processes daily climatology data and assigns cluster information.

    Parameters:
        file_path (str): Path to the TIFF file containing climatology data.
        cluster_data (pd.DataFrame): DataFrame containing cluster data with 'Latitude', 'Longitude', and 'cluster_n' columns.
        name (str): Name to assign to the processed data (e.g., 'daily_with_storms', 'daily_without_storms').
        lat_min (float): Minimum latitude boundary for filtering data.
        lat_max (float): Maximum latitude boundary for filtering data.
        lon_min (float): Minimum longitude boundary for filtering data.
        lon_max (float): Maximum longitude boundary for filtering data.

    Returns:
        pd.DataFrame: Processed DataFrame with cluster information.
    """
    # Load climatology data
    climatology_df = time_series.tif_to_dataframe(file_path)#, '02_02')
    climatology_df = climatology_df.dropna()

    # Filter by latitude and longitude boundaries
    climatology_df = climatology_df[
        (climatology_df['latitude'] >= lat_min) & (climatology_df['latitude'] <= lat_max) &
        (climatology_df['longitude'] >= lon_min) & (climatology_df['longitude'] <= lon_max)
    ]

    # Add cluster number
    for idx, row in climatology_df.iterrows():
        lat, lon = row['latitude'], row['longitude']
        cluster_value = cluster_data.loc[
            (cluster_data['Latitude'] == lat) & (cluster_data['Longitude'] == lon), 'cluster_n'
        ]
        if not cluster_value.empty:
            climatology_df.loc[idx, 'cluster_n'] = cluster_value.values[0]

    # Assign name
    climatology_df['name'] = name

    return climatology_df

def process_hourly_climatology(dataset_path, cluster_data, name, lat_min=35, lat_max=75, lon_min=-10, lon_max=25):
    """
    Processes hourly climatology data and assigns cluster information.

    Parameters:
        dataset_path (str): Path to the NetCDF dataset.
        cluster_data (pd.DataFrame): DataFrame containing cluster data with 'Latitude', 'Longitude', and 'cluster_n' columns.
        name (str): Name to assign to the processed data (e.g., 'hourly_with_storms').
        lat_min (float): Minimum latitude boundary for filtering data.
        lat_max (float): Maximum latitude boundary for filtering data.
        lon_min (float): Minimum longitude boundary for filtering data.
        lon_max (float): Maximum longitude boundary for filtering data.

    Returns:
        pd.DataFrame: Processed DataFrame with wind speed and cluster information.
    """
    # Open dataset
    test = xr.open_dataset(dataset_path)
    hourly_all = []

    for i in range(24):
        # Select data for the current hour and preprocess
        test_test = test.sel(hour=i).to_dataframe().dropna()
        test_test = test_test.drop(columns=['hour', 'spatial_ref', 'band'])
        test_test = test_test.stack().reset_index()
        test_test = test_test.drop(columns=['level_2'])

        # Filter by latitude and longitude boundaries
        test_test = test_test[
            (test_test['latitude'] >= lat_min) & (test_test['latitude'] <= lat_max) &
            (test_test['longitude'] >= lon_min) & (test_test['longitude'] <= lon_max)
        ]

        # Add cluster number
        for idx, row in test_test.iterrows():
            lat, lon = row['latitude'], row['longitude']
            cluster_value = cluster_data.loc[
                (cluster_data['Latitude'] == lat) & (cluster_data['Longitude'] == lon), 'cluster_n'
            ]
            if not cluster_value.empty:
                test_test.loc[idx, 'cluster_n'] = cluster_value.values[0]

        hourly_all.append(test_test)

    # Concatenate all DataFrames
    hourly_all_df = pd.concat(hourly_all, ignore_index=True)

    # Rename column and add the provided name
    hourly_all_df_with = hourly_all_df.rename(columns={0: 'wind_speed_None'})
    hourly_all_df_with['name'] = name

    return hourly_all_df_with

def process_file(path, month, day, cluster_data):
    """
    Process a single file based on the path, month, and day.
    Returns the processed dataset or None if an error occurs.
    """
    try:
        if path == 'hourly_with_storms' or path == 'hourly_without_storms':
            file_path_hourly = f'data/climatology/{path}/climatology_europe_{month}_{day}.nc'
            return process_hourly_climatology(file_path_hourly, cluster_data, name=f'{path}_{month}_{day}')
        elif path == 'daily_with_storms' or path == 'daily_without_storms':
            file_path_daily = f'data/climatology/{path}/climatology_europe_{month}_{day}.tif'
            return process_daily_climatology(file_path_daily, cluster_data, name=f'{path}_{month}_{day}')
    except Exception as e:
        print(f"Error processing {path} for {month}_{day}: {e}")
        return None