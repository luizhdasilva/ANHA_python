#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 13:01:31 2024

@author: luiz

On terminal, run like this: python GetSpecHumERA5.py {year}
It can be run for more than an year: python GetSpecHumERA5.py {year1} {year2} ...

The input file names must have the following pattern:
    NEMO_d2_ERA5_y{year}.nc
    NEMO_msl_ERA5_y{year}.nc
Param:
    year : int
    Dataset year shown in the files name.        

"""

# %% Import libraries
# Import libraries
import xarray as xr
import os
import sys
import numpy as np
from nco import Nco
nco = Nco()

# %% Set directories and global variables

dirOrigin = "/mnt/storage0/luiz/DATA/ATMOSPHERE/ERA5/READY/"
dirDestin = "/mnt/storage0/luiz/DATA/ATMOSPHERE/ERA5/READY/"

# Input variable
year_list = sys.argv

# %%
for year in year_list[1:]:

    print('-----------------------------------')
    print(f'Running GetSpecHumERA5: Year {year}')
    print('-----------------------------------')
    
    # Dew point temperature. Also converts from Kelvin to Celsius 
    d2 = xr.open_dataset(f'{dirOrigin}NEMO_ERA5_d2_y{year}.nc', chunks="auto")-273.15
    
    # Mea sea level pressure. Also converts from Pascal to milibar
    msl = xr.open_dataset(f'{dirOrigin}NEMO_ERA5_msl_y{year}.nc', chunks="auto")/100
    
    # Calculate vapor pressure (in mb)
    vp = 6.112*np.exp((17.67*d2)/(d2+243.5))
    vp = vp.rename_vars({'d2m': 'vp'})
    
    # Calculate specific humidity
    q2data = (0.622*vp['vp'])/(msl['msl']-(0.378*vp['vp']))
    
    
    # Now, let's make a dataset from scratch to save only the information we need
    ## Get latitude and longitude from original file
    lat_val = d2.coords['latitude'].data
    lon_val = d2.coords['longitude'].data
    time_val = d2.coords['time'].data
    
    # Make dataarray with all the information from above
    q2 = xr.Dataset(
         data_vars={'q2m': (["time", 'latitude', 'longitude'], q2data.data, {'long_name': 'specific_humidity_2m'})},
         coords={
             "time": ("time", time_val),
             "latitude": ("latitude", lat_val, {"units": "degrees_north"}),
             "longitude": ("longitude", lon_val, {"units": "degrees_east"})
             }
         )

    # Saving as NETCDF file
    
    ## New file name
    newFileName = f'NEMO_ERA5_q2_y{year}.nc'
    
    # Saving dataset as a temporary NetCDF
    print('Saving as tempoerary float32 netcdf.')
    print('...................................')
    q2.to_netcdf(f'{dirDestin}TMP_{newFileName}')
    
    print('Converting float32 Netcdf to data type short.')
    print('...................................')
    # Final step, use NCO to convert to a less memory expensive data type
    nco.ncap2(input=f'{dirDestin}TMP_{newFileName}', output=f'{dirDestin}{newFileName}', options=['-4', '-O', '-s', 'q2m=pack(q2m*1)'])
    
    # Remove temporary BIG file
    os.remove(f'{dirDestin}TMP_{newFileName}')
    
        
    print(f'{year} done. New specific humidity file saved in {dirDestin} as {newFileName}')
    print('------------------------------------')   
