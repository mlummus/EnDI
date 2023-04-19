# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 13:34:54 2023

@author: m337l400
"""

## import packages
import xarray as xr
import numpy as np
import geopandas as gpd
import pandas as pd
import glob
import os
import rioxarray
import fiona

## set input path. Here we are using the folder with all basins and glaciers 
## that have been processed by the "select_glaciers_in_all_basins.py" code
in_path = "F:/HMA_impact_index/glacier_index/sub_basin_info"
#out_path = "F:/HMA_impact_index/glacier_index/indexes/"
out_path = 'F:/HMA_impact_index/time_test_basin_compile/'

## PyGEM-OGGM dataset
PyGEM_OGGM_path = 'F:/HMA_impact_index/PyGEM_OGGM_Glacier_Projections/R15_glac_area_annual_50sets_2000_2100-rcp45.nc'
PyGEM_OGGM_ds = xr.open_dataset(PyGEM_OGGM_path)

## PyGEM dataset
PyGEM_path = "F:/HMA_impact_index/PyGEM_Glacier_projections/177232681/HMA_GL_RCP_R15_multigcm_rcp45_c2_ba1_100sets_2000_2100.nc"
PyGEM_netcdf_ds = xr.open_dataset(PyGEM_path)


os.chdir(in_path)
#col = {"Ice_Volume_WT_km3" : [0],"Ice_Area_WT_km2" : [0],"Glacier_MB_WT_mmyr-1": [0],"Meltwater_Yield_Glaciers_mmyr-1" : [0]}
#df = pd.DataFrame(col)

for file in glob.glob('glac*.shp'):
    df= pd.DataFrame()
    for year in range(101):
        glacier_df = gpd.read_file(file)
        
        ## Get IDs of the glaciers
        IDs = glacier_df['RGIId']
        ID_list = IDs.tolist()
        
        ## Get Basin ID and Name
        bas_name = file[5:-4]
        
        ## AREA--------------------------------------------------------------------
        ## Get all the RGIId values from the netcdf dataset
        netcdf_rgi_list = PyGEM_OGGM_ds.RGIId.values
    
        ## Get indices in the netcdf of the RGI values that match basin ID_list
        rgi_indices = np.argwhere(np.isin(netcdf_rgi_list,ID_list)).ravel()
    
        ## Select data based off of RGI indices
        select_PyGEM_OGGM_ds = PyGEM_OGGM_ds.sel(glacier=rgi_indices)
    
        ## Get the values of the area for the first model in the first year
        netcdf_area_values = select_PyGEM_OGGM_ds['glac_area_annual'][0,:,year].values
    
        ## Sum the values for the total glacierized area in the basin in the first year (km2)
        netcdf_area_sum = np.sum(netcdf_area_values)/1000000
        
        
        ## VOLUME------------------------------------------------------------------
        ## Get all the RGIId values from the NetCDF dataset
        v_netcdf_rgi_list = PyGEM_netcdf_ds.RGIId.values
    
        ## Get indices in the netcdf of the RGI values that match basin ID_list
        v_rgi_indices = np.argwhere(np.isin(v_netcdf_rgi_list,ID_list)).ravel()
    
        ## Select data based off of RGI indices
        select_PyGEM_ds = PyGEM_netcdf_ds.sel(glac=v_rgi_indices, method='bfill')
    
        ## Get the values of the volume in the first year
        netcdf_volume_values = select_PyGEM_ds['glac_volume_annual'][:,year].values
    
        ## Sum the values for the total glacier volume in the basin in the first year (km3)
        netcdf_volume_sum = np.sum(netcdf_volume_values)
        
        
        ## MASS BALANCE------------------------------------------------------------
        ## Get all the RGIID values from this dataset (we've done this before already, but lets name it accordingly)
        mb_netcdf_rgi_list = PyGEM_netcdf_ds.RGIId.values
    
        ## Get indices in the netcdf of the RGI values that match basin ID_list
        mb_rgi_indices = np.argwhere(np.isin(mb_netcdf_rgi_list,ID_list)).ravel()
    
        ## Select data based off of RGI indices
        select_mb_PyGEM_ds = PyGEM_netcdf_ds.sel(glac=mb_rgi_indices, method='bfill')
    
        ## Get the values of the mass balance for all glaciers in the basin in the first year
        netcdf_mb_values = select_mb_PyGEM_ds['glac_massbaltotal_monthly'][:,year].values
    
        ## Average the values for the total glacier mass balance in the basin in the first year (mm we)
        netcdf_mb_avg = np.mean(netcdf_mb_values)*1000
        
        
        ## MELT--------------------------------------------------------------------
        ## Get all the RGIID values from this dataset (we've done this before already, but lets name it accordingly)
        melt_netcdf_rgi_list = PyGEM_netcdf_ds.RGIId.values
    
        ## Get indices in the netcdf of the RGI values that match basin ID_list
        melt_rgi_indices = np.argwhere(np.isin(melt_netcdf_rgi_list,ID_list)).ravel()
    
        ## Select data based off of RGI indices
        select_melt_PyGEM_ds = PyGEM_netcdf_ds.sel(glac=melt_rgi_indices, method='bfill')
    
        ## Get the values of the mass balance for all glaciers in the basin in the first year
        netcdf_melt_values = select_mb_PyGEM_ds['glac_melt_monthly'][:,year].values
    
        ## Average the values for the total glacier mass balance in the basin in the first year (mm we)
        netcdf_melt_avg = np.mean(netcdf_melt_values) * 1000
        
        ## SAVE IT TO DATAFRAME----------------------------------------------------
        ## create dictionary of data and their names
        data = [{"Year": year, "Basin_ID" : bas_name, "Ice_Volume_WT_km3" : netcdf_volume_sum,"Ice_Area_WT_km2" : netcdf_area_sum,"Glacier_MB_WT_mmyr-1": netcdf_mb_avg,"Meltwater_Yield_Glaciers_mmyr-1" : netcdf_melt_avg}]
    
        ## convert to a dataframe
        #df = pd.DataFrame(data)
        data_df = pd.DataFrame(data)
        df = pd.concat([df,data_df], axis=0)
        
        ## save as a csv file
        # df.to_csv((f"{out_path}index_{str(bas_name)}.csv"), header=True)
    df.to_csv((f"{out_path}{bas_name}index.csv"), header=True)