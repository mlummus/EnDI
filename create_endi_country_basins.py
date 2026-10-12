# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:36:43 2025

@author: m337l400
"""

import xarray as xr
import xvec
import geopandas as gpd
import pandas as pd
import rioxarray
import rasterio
import matplotlib.pyplot as plt
import contextily as cx
import matplotlib
from matplotlib import colors, cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import datetime
import xesmf as xe
from pyproj import CRS
import cartopy.crs as ccrs
from affine import Affine
import numpy as np

# identify file names
# runoff_fn = "F:/EnDI/EnDI_data/country_basin_endi/runoff_all_models_scenarioSSP2-45.nc"
runoff_fn = "F:/EnDI/EnDI_data/Glacier_non_projected/ERA5_global_1980_2022/glac_runoff_monthly/country_basins_ERA5_global_1980_2022_glac_runoff_monthly.nc"
snow_fn = "F:/EnDI/EnDI_data/country_basin_endi/snow_fraction_country_basins.nc"
permafrost_fn = "F:/EnDI/EnDI_data/country_basin_endi/permafrost_in_country_basins.nc"
# utci_fn = "F:/EnDI/EnDI_data/country_basin_endi/UTCI_country_basins.nc"
utci_fn = "F:/EnDI/EnDI_data/country_basin_endi/UTCI_country_basins_fixed.nc"
# aqi_fn = "F:/EnDI/EnDI_data/country_basin_endi/AQI_country_basins.nc"
aqi_fn = "F:/EnDI/EnDI_data/country_basin_endi/AQI_country_basins_fixed.nc"
ex_pr_fn = "F:/EnDI/EnDI_data/country_basin_endi/extreme_precip_10mm_country_basins.nc"
landslides_fn = "F:/EnDI/EnDI_data/country_basin_endi/LHI_ds_country_basins.nc"


# open files
runoff = xr.open_dataset(runoff_fn).xvec.decode_cf() # 1995-2022, monthly
snow = xr.open_dataset(snow_fn).xvec.decode_cf() # 2001- 2021, monthly
permafrost = xr.open_dataset(permafrost_fn).xvec.decode_cf() #2003-2014, annual♣
utci = xr.open_dataset(utci_fn).xvec.decode_cf() #2003-2019, monthly
aqi = xr.open_dataset(aqi_fn).xvec.decode_cf() # 2003-2019, monthly
ex_pr = xr.open_dataset(ex_pr_fn).xvec.decode_cf() # 2000-2016, annual
landslides = xr.open_dataset(landslides_fn).xvec.decode_cf() #2000-2021, monthly


#%% process runoff, snow, permafrost

## glacier runoff
# runoff_model_mean = runoff.runoff.mean(dim="model")
# # runoff_model_mean = runoff_model_mean.where(runoff_model_mean > 0, 0)
# timelist = runoff_model_mean.time.values
# runoff_model_mean['time'] = pd.to_datetime(timelist)
# runoff_slice = runoff_model_mean.isel(time = slice(0,432))
# runoff_annual_sum =  runoff_slice.resample(time = "YS").sum(skipna=False)
# roll_runoff = runoff_annual_sum.rolling(time=3).mean(axis=1)
# # roll_runoff = roll_runoff.where(roll_runoff > 0, 0)
# roll_diff = roll_runoff.isel(time=-1) - roll_runoff.isel(time=2)
# roll_diff_abs = abs(roll_diff)
# runoff_max = roll_diff_abs.max()
# runoff_min = roll_diff_abs.min()
# runoff_norm = (roll_diff_abs- runoff_min) / (runoff_max - runoff_min)
runoff_annual_sum = runoff.runoff.resample(time = "YE").sum()
runoff_roll = runoff_annual_sum.rolling(time=3).mean().dropna("time")
runoff_diff = runoff_roll.isel(time=-1)-runoff_roll.isel(time=0)
runoff_diff_abs = abs(runoff_diff)
runoff_diff_max = runoff_diff_abs.max()
runoff_diff_min = runoff_diff_abs.min()
runoff_norm = (runoff_diff_abs - runoff_diff_min) / (runoff_diff_max - runoff_diff_min)

# snow
snow_annual_max = snow.snow_fraction.resample(time = "YS").max()
snow_roll = snow_annual_max.rolling(time=3).mean().dropna("time")
snow_diff = snow_roll.isel(time=-1)-snow_roll.isel(time=0)
snow_diff_abs = abs(snow_diff)
snow_diff_max = snow_diff_abs.max()
snow_diff_min = snow_diff_abs.min()
snow_norm = (snow_diff_abs - snow_diff_min) / (snow_diff_max - snow_diff_min)


# permafrost 
perm_diff = permafrost.permafrost.isel(time=-1) - permafrost.permafrost.isel(time=0)
perm_diff_abs = abs(perm_diff)
perm_diff_max = perm_diff.max()
perm_diff_min = perm_diff.min()
perm_norm = (perm_diff - perm_diff_min) / (perm_diff_max - perm_diff_min)

#%% Process heat stress, cold stress, AQI, and extreme precip

utci['t'] = pd.to_datetime(utci['t'].values)
heat_stress_annually = utci.strong_heat_stress_sum.resample(t="YS").sum()
heat_stress_roll = heat_stress_annually.rolling(t=3).mean().dropna("t")
heat_stress_avg = heat_stress_roll.mean(dim='t')
heat_stress_min = heat_stress_avg.min()
heat_stress_max = heat_stress_avg.max()
heat_stress_norm = (heat_stress_avg - heat_stress_min)/ (heat_stress_max - heat_stress_min)

cold_stress_annually = utci.strong_cold_stress_sum.resample(t="YS").sum()
cold_stress_avg = cold_stress_annually.mean(dim='t')
cold_stress_min = cold_stress_avg.min()
cold_stress_max = cold_stress_avg.max()
cold_stress_norm = (cold_stress_avg - cold_stress_min)/ (cold_stress_max - cold_stress_min)

aqi_annually = aqi.unhealthy_sum.resample(t="YS").sum()
aqi_avg = aqi_annually.mean(dim="t")
aqi_min = aqi_avg.min()
aqi_max = aqi_avg.max()
aqi_norm = (aqi_avg - aqi_min)/ (aqi_max - aqi_min)

ex_pr_avg = ex_pr.p10mm.mean(dim="time")
ex_pr_min = ex_pr_avg.min()
ex_pr_max =  ex_pr_avg.max()
ex_pr_norm = (ex_pr_avg - ex_pr_min)/ (ex_pr_max - ex_pr_min)

#%%  process landslides

annual_landslide = landslides.LHI.resample(time="YS").mean() * 365
annual_landslide= annual_landslide.rename({'basin': 'geometry'})
annual_landslide_avg = annual_landslide.mean(dim="time")
landslide_min = annual_landslide_avg.min()
landslide_max = annual_landslide_avg.max()
landslide_norm = (annual_landslide_avg - landslide_min)/(landslide_max - landslide_min)

#%% make endi dataset

endi_data = xr.Dataset(
    data_vars=dict(
                   # runoff=(["geometry"], runoff_norm.values), 
                   snow=(["geometry"], (snow_norm.values)), 
                   permafrost=(["geometry"], (perm_norm.values)), 
                   aqi=(["geometry"], aqi_norm.values), 
                   heat_stress=(["geometry"], heat_stress_norm.values),
                   cold_stress=(["geometry"], cold_stress_norm.values),
                   ex_pr=(["geometry"], ex_pr_norm.values), 
                   landslides=(["geometry"], landslide_norm.values)),
    coords=dict({'geometry': snow_norm.geometry.values})
).xvec.set_geom_indexes("geometry", crs=snow.geometry.crs)

endi_gdf = endi_data.xvec.to_geodataframe(geometry="geometry")
runoff_gdf = runoff_norm.xvec.to_geodataframe(geometry="geometry")
endi_gdf.to_file("F:/EnDI/EnDI_data/country_basin_endi/endi_partial.shp", driver="ESRI Shapefile")
runoff_gdf.to_file("F:/EnDI/EnDI_data/country_basin_endi/runoff.shp", driver="ESRI Shapefile")
# Joined these in QGIS by turning the fixed geometry of the runoff into points 
# using "point on surface" and joining that to the fixed geometry of the partial 
# endi dataset with "join attributes by location." Saved the joined dataset as 
# 'endi_vars.shp.' Still needs final endi calculation variable--see cells below.

#%% unfortunately nothing in this cell works. I got pissed off and just 
# decided to save out the two dataframes and join them in QGIS. sigh

# gpd.sjoin(endi_gdf, runoff_gdf, how= "inner",  predicate="intersects")

# runoff_data = runoff_norm.to_dataset().xvec.set_geom_indexes("geometry", crs=runoff.geometry.crs)
# endi_data_aligned, runoff_data_aligned = xr.align(endi_data, runoff_data, join="outer")
# ds = xr.merge([endi_data_aligned, runoff_data_aligned],join="outer")
# xr.concat([endi_data, runoff_data], dim="geometry")


# runoffnonan = runoff_norm.fillna(0)
# permafrostnonan = perm_norm.fillna(0)
# landslidesnonnan = landslide_norm.fillna(0)

#%%

endi_vars_fn = "F:/EnDI/EnDI_data/country_basin_endi/endi_vars_fixed.shp"
endi_vars = gpd.read_file(endi_vars_fn)

endi_data = xr.Dataset(
    data_vars=dict(
                   runoff=(["geometry"], endi_vars.runoff), 
                   snow=(["geometry"], (endi_vars.snow)), 
                   permafrost=(["geometry"], (endi_vars.permafrost)), 
                   aqi=(["geometry"], endi_vars.aqi), 
                   heat_stress=(["geometry"], endi_vars.heat_stres),
                   cold_stress=(["geometry"], endi_vars.cold_stres),
                   ex_pr=(["geometry"], endi_vars.ex_pr), 
                   landslides=(["geometry"], endi_vars.landslides)),
    coords=dict({'geometry': endi_vars.geometry.values})
).xvec.set_geom_indexes("geometry", crs=endi_vars.geometry.crs)

endi_calc =np.nansum([endi_data.runoff.values, endi_data.snow.values, endi_data.permafrost.values, endi_data.aqi.values, endi_data.heat_stress.values, endi_data.cold_stress.values, endi_data.ex_pr.values, endi_data.landslides.values], axis =0)
# endi_calc = (runoffnonan.values) + (endi_data.snow.values) + (permafrostnonan.values) + endi_data.aqi.values + endi_data.heat_stress.values + endi_data.cold_stress.values + endi_data.ex_pr.values + landslidesnonnan.values
# diff_runoff + snow_diff + perm_diff + aqi + landslides + ex_pr + heat_stress + cold_stress

endi_data = endi_data.assign(endi_calc = (("geometry"), endi_calc))

endi_data= endi_data.xvec.set_geom_indexes("geometry", crs=runoff.geometry.crs)
encoded = endi_data.xvec.encode_cf()
encoded.to_netcdf("F:/EnDI/EnDI_data/country_basin_endi/endi_country_basins_fixed.nc")