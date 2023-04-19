# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 11:57:27 2023

@author: m337l400
"""

## Glacier index for all glaciers in RGI 15

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
out_path = 'F:/HMA_impact_index/test/'

## PyGEM-OGGM dataset
PyGEM_OGGM_path = 'F:/HMA_impact_index/PyGEM_OGGM_Glacier_Projections/R15_glac_area_annual_50sets_2000_2100-rcp45.nc'
PyGEM_OGGM_ds = xr.open_dataset(PyGEM_OGGM_path)

## PyGEM dataset
PyGEM_path = "F:/HMA_impact_index/PyGEM_Glacier_projections/177232681/HMA_GL_RCP_R15_multigcm_rcp45_c2_ba1_100sets_2000_2100.nc"
PyGEM_netcdf_ds = xr.open_dataset(PyGEM_path)

os.chdir(in_path)
col = {"Ice_Volume_WT_km3" : [0],"Ice_Area_WT_km2" : [0],"Glacier_MB_WT_mmyr-1": [0],"Meltwater_Yield_Glaciers_mmyr-1" : [0]}
df = pd.DataFrame(col)
for file in glob.glob('glac*.shp'):
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
    netcdf_area_values = select_PyGEM_OGGM_ds['glac_area_annual'][0,:,0].values

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
    netcdf_volume_values = select_PyGEM_ds['glac_volume_annual'][:,0].values

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
    netcdf_mb_values = select_mb_PyGEM_ds['glac_massbaltotal_monthly'][:,0].values

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
    netcdf_melt_values = select_mb_PyGEM_ds['glac_melt_monthly'][:,0].values

    ## Average the values for the total glacier mass balance in the basin in the first year (mm we)
    netcdf_melt_avg = np.mean(netcdf_melt_values) * 1000
    
    ## SAVE IT TO DATAFRAME----------------------------------------------------
    ## create dictionary of data and their names
    data = [{"Ice_Volume_WT_km3" : netcdf_volume_sum,"Ice_Area_WT_km2" : netcdf_area_sum,"Glacier_MB_WT_mmyr-1": netcdf_mb_avg,"Meltwater_Yield_Glaciers_mmyr-1" : netcdf_melt_avg}]

    ## convert to a dataframe
    #df = pd.DataFrame(data)
    data_df = pd.DataFrame(data)
    df = pd.concat([df,data_df], axis=0)
    
    ## save as a csv file
    # df.to_csv((f"{out_path}index_{str(bas_name)}.csv"), header=True)
df.to_csv((f"{out_path}index.csv"), header=True)





## STOPPING POINT: NEED TO GET MORE PRECIP AREA TO RUN THIS CODE. PRECIP DOES NOT COVER ALL OF REGION 15
# os.chdir(in_path)
# for file in glob.glob('basin*.shp'):
#     read_basin = gpd.read_file(file)
    
#     ## Get the basin name & number
#     bas_name2 = file[6:-4]

#     ## set the paths and open the dataset with rioxarray
#     winter_precip_path = 'F:/HMA_impact_index/GFDL_FLOR_Precip/162904093/HMA_EAPrecip_FLOR_data_winter_nudged_1982-2017.nc'
#     summer_precip_path = 'F:/HMA_impact_index/GFDL_FLOR_Precip/162904094/HMA_EAPrecip_FLOR_data_summer_nudged_1982-2017.nc'
#     winter_precip_ds = rioxarray.open_rasterio(winter_precip_path)
#     summer_precip_ds = rioxarray.open_rasterio(summer_precip_path)

#     ## set CRS of the precip dataset
#     winter_precip_ds.rio.write_crs(4326, inplace=True)
#     summer_precip_ds.rio.write_crs(4326, inplace=True)

#     ## clip it using the basin file we already opened
#     clipped_winter_precip = winter_precip_ds.rio.clip(read_basin.geometry.values, read_basin.crs)
#     clipped_summer_precip = summer_precip_ds.rio.clip(read_basin.geometry.values, read_basin.crs)

#     ## Save out 
#     clipped_winter_precip.rio.to_raster('F:/HMA_impact_index/GFDL_FLOR_Precip/clipped_winter_precip.tif')
#     clipped_summer_precip.rio.to_raster('F:/HMA_impact_index/GFDL_FLOR_Precip/clipped_summer_precip.tif')

#     ## find the mean of each in kg m-2 s-1 
#     winter_precip_avg = np.mean(clipped_winter_precip.astype('int64'))
#     summer_precip_avg = np.mean(clipped_summer_precip.astype('int64'))

#     ## avg the means to get the annual average 
#     precip_per_sec = (winter_precip_avg + summer_precip_avg) / 2

#     ## convert to mmyr-1
#     annual_precip_dataarray = precip_per_sec * 31536000

#     annual_precip = np.array(annual_precip_dataarray)
    
#     data2 = [{"P_over_glacier_WT_mmyr-1" : annual_precip}]
#     df2 = pd.DataFrame(data2)
    
#     new_path = 'F:/HMA_impact_index/glacier_index/indexes/'
#     os.chdir(new_path)
#     for index_file in glob.glob('index*'):
#         index_name = index_file[6:-4]
#         if bas_name2 == index_name:
#             index_df = gpd.read_file(index_file)
#             index_df.join(df2)
            
#             ## save as a csv file
#             df.to_csv((f"{out_path}combined_index_{str(bas_name2)}.csv"), header=True)
#         else:
#             pass
    