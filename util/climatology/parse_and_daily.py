import xarray as xr
import numpy as np
import pandas as pd
import glob
from datetime import datetime
import gc

def parse_date_and_output_list(u10,target_month,target_day):
    date_ctrl = []
    for i in range(len(u10['time'])):
        tempdate = datetime.strptime(str(u10['time'][i].data), '%Y-%m-%dT%H:%M:%S.%f000')
        if ((tempdate.month==int(target_month)) & (tempdate.day==int(target_day))):
            date_ctrl.append(True)
        else:
            date_ctrl.append(False)
    # Find the first True index
    first_true_index = date_ctrl.index(True) if True in date_ctrl else None
    # Find the last True index
    last_true_index = len(date_ctrl) - 1 - date_ctrl[::-1].index(True) if True in date_ctrl else None
    return first_true_index,last_true_index

def find_max_daily_wind(wspd,first_true_index,last_true_index):
    # Slice the dataset along time axis
    filtered_wspd = wspd.isel(time=slice(first_true_index, last_true_index + 1))
    # Get the maximum daily winds for every grid point
    max_wind = filtered_wspd.max(dim='time')
    return max_wind