# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 15:14:19 2023

@author: m337l400
"""

## Code for finding the glacier index in multiple basins

import geopandas as gpd
import shapely.validation
import fiona
import xarray as xr
import rioxarray
import numpy as np
import pandas as pd

## Read in glacier shapefile
glac_path = "E:/Koshi/15_rgi60_SouthAsiaEast/15_rgi60_SouthAsiaEast.shp"
read_glac = gpd.read_file(glac_path)
out_path= "F:/HMA_impact_index/glacier_index/sub_basin_info/"

## Read in the basin shapefile, find the geometry of the basin stored in the dataframe, make the geometry valid. https://data.apps.fao.org/catalog/dataset/ee616dc4-3118-4d67-ba05-6e93dd3e962f
basin_path = "F:/HMA_impact_index/water_towers/data/Basins/FAO/hydrobasins_asia/hydrobasins_asia.shp"
read_basin = gpd.read_file(basin_path)

## Make the geometry of each basin valid
valid_basin_geom = [] ## Create an empty list
for index, thing in read_basin.iterrows(): ## For each row (index) and column (thing) of the dataframe
    b = thing['geometry']   ## The geomtry of this basin is called b
    basin = shapely.validation.make_valid(b) ## Make the geomtry valid
    valid_basin_geom.append(basin) ## Add the new, valid geometry to the list
read_basin['geometry'] = valid_basin_geom ## Replace the old geomtry with the valid geomtry in the dataframe
read_basin_df = gpd.GeoDataFrame(read_basin, geometry='geometry')


## Make the geometry of each glacier valid
valid_glac_geom = [] ## Create an empty list
for index, thing in read_glac.iterrows(): ## For each row (index) and column (thing) of the dataframe
    g = thing['geometry']   ## The geomtry of this glacier is called g
    glac = shapely.validation.make_valid(g) ## Make the geomtry valid
    valid_glac_geom.append(glac) ## Add the new, valid geometry to the list
read_glac['geometry'] = valid_glac_geom ## Replace the old geomtry with the valid geomtry in the dataframe


for i in range(len(read_basin)):
    basin_num = read_basin_df['SUB_BAS'][i] ## get the basin numberr
    basin_name = read_basin_df['SUB_NAME'][i] ## get he basin name
    basin_name_file = basin_name.replace(' ','_').replace('/','_') ## format it to be saved out
    percent_overlap = {} ## create an empty dictionary
    for j in range(len(read_glac)): ## for all of the glaciers in the dataframe
        inter = read_glac['geometry'][j].intersection(read_basin_df['geometry'][i]) ## inter is the polygon shape of the intersection between the glacier and the basin  
        if inter.is_empty == True: 
            pass
        else: 
            a = read_glac.geometry[j].area ## a is the area of this glacier
            po = (inter.area/a) * 100 ## po is the Percent Overlap of the glacier and basin file
            glac_name = read_glac.RGIId[j] ## create variable that will isolate the RGIId
            percent_overlap[glac_name] = po ## add the percent overlap to the empty dictionary with the key as the RGIId and the value the percent overlap
    if len(percent_overlap) == 0:
        pass
    else:
        po_df = pd.DataFrame(percent_overlap.items(), columns=['RGIId','p_o'])
        read_glac1=read_glac.join(po_df.set_index('RGIId'), on='RGIId')
        basin_glac = read_glac1.loc[read_glac1['p_o']>60] ## Select only glaciers that are mostly in the basin
        basin_glac['Basin_ID'] = basin_num
        basin_glac['Basin_name'] = basin_name
        basin_glac_df = gpd.GeoDataFrame(basin_glac, geometry='geometry') ## Ensure the dataframes are GeoDataFrames
        basin = read_basin_df.loc[[i]]
        basin_df = gpd.GeoDataFrame(basin, geometry='geometry')
        
        ## Save the dataframes as shapefiles to be used later
        with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
            basin_glac_df.to_file(f"{out_path}glac_{str(basin_num)}_{basin_name_file}.shp")
            basin_df.to_file(f"{out_path}basin_{str(basin_num)}_{basin_name_file}.shp")