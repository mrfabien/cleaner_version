import xarray as xr
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
import numpy as np

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