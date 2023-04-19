# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 16:54:00 2023

@author: m337l400
"""

import geopandas as gpd
import shapely.validation
import fiona

## Read in glacier shapefile
glac_path = "E:/Koshi/15_rgi60_SouthAsiaEast/15_rgi60_SouthAsiaEast.shp"
read_glac = gpd.read_file(glac_path)

## Read in the basin shapefile, find the geometry of the basin stored in the dataframe, make the geometry valid
basin_path = "F:/HMA_impact_index/glacier_index/Q_file_glacier_index/tamba_sun_kosi_basin.shp"
read_basin = gpd.read_file(basin_path)
geom = read_basin.iloc[0,:]['geometry']
basin_df = shapely.validation.make_valid(geom)
read_basin['geometry'] = basin_df

## Make the geometry of each glacier valid
valid_geom = [] ## Create an empty list
for index, thing in read_glac.iterrows(): ## For each row (index) and column (thing) of the dataframe
    g = thing['geometry']   ## The geomtry of this glacier is called g
    glac = shapely.validation.make_valid(g) ## Make the geomtry valid
    valid_geom.append(glac) ## Add the new, valid geometry to the list
read_glac['geometry'] = valid_geom ## Replace the old geomtry with the valid geomtry in the dataframe

## Calculate the percent overlap 
percent_overlap = [] ## create an empty list
for i in range(len(read_glac)): ## for all of the glaciers in the dataframe
    inter = read_glac['geometry'][i].intersection(basin_df) ## inter is the polygon shape of the intersection between the glacier and the basin
    a = read_glac.geometry[i].area ## a is the area of this glacier
    po = (inter.area/a) * 100 ## po is the Percent Overlap of the glacier and basin file
    percent_overlap.append(po) ## add the percent overlap to the empty list
read_glac['p_o'] = percent_overlap ## create a new column with the percent overlap

## Select only glaciers that are mostly in the basin
basin_glac = read_glac.loc[read_glac['p_o']>60] 

## Ensure the dataframes are GeoDataFrames
basin_glac_df = gpd.GeoDataFrame(basin_glac, geometry='geometry')
read_basin_df = gpd.GeoDataFrame(read_basin, geometry='geometry')

## Save the dataframes as shapefiles to be used later
with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
    basin_glac_df.to_file('F:/HMA_impact_index/glacier_index/glaciers_in_basin.shp')
    read_basin_df.to_file('F:/HMA_impact_index/glacier_index/basin_valid.shp')

## Save the dataframes as csv to be used later
# basin_glac_df.to_csv('F:/HMA_impact_index/glacier_index/glaciers_in_basin.csv')
# read_basin_df.to_csv('F:/HMA_impact_index/glacier_index/basin_valid.csv')