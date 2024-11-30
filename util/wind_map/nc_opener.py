import xarray as xr

def open_monthly_nc(variable, year, months, way, level=0):
    datasets = [xr.open_dataset(f'{way}{variable}/ERA5_{year}-{month}_{variable}.nc') for month in months]
    if variable == 'geopotential' and level != 0:
        datasets = [dataset.sel(level=level) for dataset in datasets]
    concated_datasets = xr.concat(datasets, dim='time')
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