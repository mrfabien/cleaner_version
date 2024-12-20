import os
import sys
import pandas as pd

operating_system = 'curnagl'

if operating_system == 'win':
    os.chdir('C:/Users/fabau/OneDrive/Documents/GitHub/master-project-cleaned/')
elif operating_system == 'curnagl':
    os.chdir('/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/')
else:
    os.chdir('/Users/fabienaugsburger/Documents/GitHub/master-project-cleaned/')

# Add the path to the custom library

custom_library_path = os.path.abspath('util/wind_map/')
sys.path.append(custom_library_path)

import wind_map

# Define the path to the input data

input_path = '/work/FAC/FGSE/IDYST/tbeucler/default/raw_data/ECMWF/ERA5/SL/'
variable = 'instantaneous_10m_wind_gust'
storm_dates = pd.read_csv('pre_processing/tracks/storm_dates.csv', 
                          delimiter = ',')  
output_file = 'data/time_series_rasters_storms_15h'

# Process the data for each storm

#index = int(sys.argv[1])

#print('Processing storm number', index+1,' at index ', index)

index = int(sys.argv[1])
nb_hours = 15

# check if the storm exists already in the output folder
'''if os.path.exists(f'{output_file}/storm_{index}.tiff'):
    print('Storm number', index+1,' at index ', index, ' already exists')
    sys.exit()'''
#print('Processing date', storm_dates.loc['start_date'][index])
wind_map.to_tiff(variable, storm_dates, input_path, output_file, index, nb_hours, level=0)

# storm Xylia doesn't work, need to be done manually