#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 15:08:11 2024

@author: luiz

File input must match the following patter:
    ERA5_year_vars.nc
    vars = TSPS or TDUVMSL
    
"""

import sys
import xarray as xr
from nco import Nco
nco = Nco()

# Input variable
file_list = sys.argv

var_dict ={
        'u10': 'u10',
        'v10': 'v10',
        't2m': 't2',
        'd2m': 'd2',
        'msl': 'msl',
        'ssrd': 'solar',
        'strd': 'thermal',
        'tp': 'precip',
        'sf': 'snow'
        }

for filename in file_list[1:]:
    
    # Verify year in the file name compating with the date
    # within the original NetCDF.
    print('-----------------------------------')
    print('Checking whether the date in the file name matches the one embeded in the NetCDF.')
    year = filename.split('_')[1]
    ds = xr.open_dataset(filename)
    fileyear = ds.valid_time[0].dt.year.data

    if int(year) != fileyear:
        print('Warning !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(f"Year in the file name ({year}) doesn't matches with the NetCDF attrs ({fileyear}).")
        print(f"Assuming {fileyear} as the real date. ")
        year = fileyear
        
    # Create a list with the variables available in the NetCDF
    file_vars = ds.data_vars

    print('-----------------------------------')
    print(f'Extracting variables: Year {year}')   
    for v in var_dict.keys():

        if v in file_vars:
            varname = var_dict[v]
            newfilename = f'{varname}_ERA5_y{year}.nc'
            
            print('-----------------------------------')
            print(f'Getting {v}: year {year}')
            
            nco.ncks(input=filename, output=newfilename, options=['-v', v])
            
            print('-----------------------------------')
            print(f'New file saved as {newfilename}')
        
        
    print('-----------------------------------')
    print(f'{filename} done.')
    
print('......................................')
print('End of program.')
