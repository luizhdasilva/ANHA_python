#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 14:13:28 2024

@author: luiz

On terminal, run like this: python FixEra5.py {year}

The file name must have the following pattern:
    {var}_ERA5_y{year}.nc

Param:
    year : int
    Dataset year shown in the files name.        

"""

# %% Import libraries
# Import libraries
import xarray as xr
import os
import sys
import glob
import pandas as pd
from nco import Nco
nco = Nco()

# %% Set directories and global variables

dirOrigin = "/mnt/storage0/luiz/DATA/ATMOSPHERE/ERA5/ORIGINALS/"
dirDestin = "/mnt/storage0/luiz/DATA/ATMOSPHERE/ERA5/READY/"

# Input variable
year_list = sys.argv

# %%
for year in year_list[1:]:
	
	print('-----------------------------------')
	print(f'Running FixERA5: Year {year}')
	print('-----------------------------------')

	for file in glob.iglob(f"{dirOrigin}*_ERA5_y{year}.nc"):
    
    		print('')
    		print(f'Fixing ERA5 file: {file}')
    		print('...................................')
    
    		# open dataset
    		ds = xr.open_dataset(file)
    
    		# Rename time and drop unecessary variables
    		ds = (ds.rename_dims({"valid_time":"time"})
          		.rename_vars({"valid_time":"time"})
          		.drop_vars(["expver", "number", "time"], errors="ignore"))
    
    		# Get variable name
    		varName = [v for v in list(ds.variables.keys()) if v not in ['latitude','longitude']][0]
    
    		# Now, let's make a dataset from scratch to save only the information we need
    		## Get latitude and longitude from original file
    		lat = ds.coords['latitude'].data
    		lon = ds.coords['longitude'].data
    
    		# Make a new time array
    		time_reference = pd.date_range("1900-01-01 00:00:00", "2023-12-31 23:00:00", freq="h")
    		time_values = time_reference[time_reference.slice_indexer(year, year)]
    
    		print(f'Retrieving variable {varName} data.')
    		print('...................................')
    		# Get variable data and attributes
    		varAttrs = ds[varName].attrs
    		ds = ds[varName].data
    
    
    		# Make dataarray with all the information from above
    		ds = xr.Dataset(
    		data_vars={varName: (["time", 'latitude', 'longitude'], ds, varAttrs)}, 
    		coords={
        		"time": ("time", time_values),
        		"latitude": ("latitude", lat, {"units": "degrees_north"}),
        		"longitude": ("longitude", lon, {"units": "degrees_east"}),
       		 }
    		)
    
    		# Needs to correct units for radiation and precipitation variables
    		if varName in ['ssrd', 'strd']:
            
        		if varName == 'ssrd':
            			var = 'solar'
        		else:
            			var = 'therm'

        		print(f'Correcting {varName} units: from "J m**-2" to "W m**-2"')
        		print('...................................')
        		# Numerically changing unit:
        		ds = ds / 3600
        
        		# Change unit in the attrs
        		ds[varName].attrs["units"] = "W m**-2"
        
    		elif varName in ['tp', 'sf']:
            
        		if varName == 'tp':
            			var = 'precip'
        		else:
            			var = 'snow'

        		print(f'Correcting {varName} units: from "m" to "m/s"')
        		print('...................................')
        		# Numerically changing unit:
        		ds = ds / 3600
        
        		# Change unit in the attrs
        		ds[varName].attrs["units"] = "m/s"
        
        
    		else:
        		var = file.split('/')[-1].split('_')[0]
        
    		# NEMO doesn't like when the forcing data in the left bottom corner are (0, max)
    		# it MUST be (0,0). To fix that in ERA5 files, we need to flip the data in the
    		# latitude dimension.    
        		## flipping in latitude
    		print('Flipping in latitude dimension.')
    		print('...................................')
    		ds = ds.reindex(latitude=list(reversed(ds.latitude)))
    
    		oldFileName = file.split('/')[-1]
    		newFileName = f'NEMO_ERA5_{var}_y{year}.nc'
        
    		# Saving dataset as a temporary NetCDF
    		print('Saving as tempoerary float32 netcdf.')
    		print('...................................')
    		ds.to_netcdf(f'{dirDestin}TMP_{newFileName}')
    		del ds # saving memory
    
    		print('Converting float32 Netcdf to data type short.')
    		print('...................................')
    		# Final step, use NCO to convert to a less memory expensive data type
    		nco.ncap2(input=f'{dirDestin}TMP_{newFileName}', output=f'{dirDestin}{newFileName}', options=['-4', '-O', '-s', f'{varName}=pack({varName})'])

    		# Remove temporary BIG files
    		os.remove(f'{dirDestin}TMP_{newFileName}')
    
    		print(f'{oldFileName} done. Saved in {dirDestin} as {newFileName}')
    		print('------------------------------------')
    
print('End of program.')
