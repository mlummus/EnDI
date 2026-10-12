# EnDI
Data and code used to create an Environmental Disturbance Index (EnDI) in High Mountain Asia

## Data Folder
all data can be found in the folder labeled "data." Here we have both the inputs and outputs of the create_endi_country_basins.py file

### create_endi_country_basins.py
`create_endi_country_basins.py` opens each of the input files from the "Data" folder and normalizes each according to the EnDI formula protocol. Unfortunately, because the glacier runoff is not present in all the basins in this study, the runoff and the other factors had issues combining. I had to save the runoff separately from the other factors and combine them spatially in QGIS. The partial EnDI and the runoff are saved as shapefiles `endi_partial` and `runoff_shapefile`. The spatially combined data can be found in the `endi_vars` shapefile. `create_endi_country_basins.py` later opens the `endi_vars` shapefile, computes the final EnDI sum, and saves our final dataset out as `endi_country_basins_fixed.nc`.

### country_basins_ERA5_global_1980_2022_glac_runoff_monthly.nc
`country_basins_ERA5_global_1980_2022_glac_runoff_monthly` is the monthly runoff in each basin from 1995-2022. The data comes from a global dataset of glacier runoff found using the Python Glacier Evolution Model (PyGEM) which models glacier runoff for each glacier outline using degree-day factors while accounting for debris cover, temperature threshold based accumulation, and refreezing based on annual air temperature -- all of which are important factors for estimating glacier runoff in High Mountain Asia (Rounce et al. 2023)

### snow_fraction_country_basins.nc
`snow_fraction_country_basins.nc` is the snow fraction, which comes from spatially and temporally complete raster images of snow cover and snow surface properties (Rittger 2025) derived from the MODIS Snow Covered Area and Grain-size (MODSCAG) and MODIS Dust Radiative Forcing in Snow (MODDRFS) data sets (Rittger et al. 2024) using historical surface reflectances from MODIS/Terra as input.

### permafrost_in_country_basins.nc
`permafrost_in_country_basins.nc` is the permafrost extent which comes from a 1 km dataset containing permafrost extent, monthly land surface temperatures (MLSTs), and mean annual ground temperatures (MAGTs) are gap-filled daily MODIS Terra/Aqua Land surface temperatures (LSTs) with downscaled Atmospheric Infra-Red Sounder (AIRS) skin surface temperatures (Kim et al. 2024).

### AQI_country_basins_fixed.nc
`AQI_country_basins_fixed.nc` The heat stress index, cold stress index, and air quality index are all derived from the Model for Atmospheric Transport and Chemistry in Asia (MATCHA) dataset (Kumar et al., 2024), which contains 12 km resolution simulated reanalysis of aerosol transport, chemistry, and deposition over High Mountain Asia (HMA) for 2003-2019. Air quality relates to the pollution in the air from surface ozone, PM2.5, PM10, CO, SO2, and NO2 based on the US EPA AQI index.

### UTCI_country_basins_fixed.nc
`UTCI_country_basins_fixed.nc` contains both heat stress and cold stress and is based on the Universal Thermal Climate index (UTCI). For this project we use the variables "strong_heat_stress_sum" and "strong_cold_stress_sum" within this file.

### LHI_ds_country_basins.nc
`LHI_ds_country_basins.nc` contains the Landslide Hazard Indicator (LHI) which is computed by inputting downscaled temperatures and precipitation for 1990 through 2014 to the ensemble climate model (Stanley et al., 2024). Our study uses the data from 2000-2014 to more closely align with the time periods of the other parameters in this study.

### extreme_precip_10mm_country_basins.nc
`extreme_precip_10mm_country_basins.nc` uses the GFDL FLOR Modeled Extreme Precipitation Indices which contain parameters that represent yearly precipitation maximums, precipitation frequencies, length of precipitation events, and precipitation totals at a spatial resolution of 0.625 degrees x 0.5 degrees over High Mountain Asia (Kirschbaum et al., 2018). The extreme precipitation index utilizes "R10mm," the number of days in a year that exceed 10mm of precipitation.
