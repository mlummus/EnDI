# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:16:51 2023

@author: m337l400
"""

import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

in_path = "F:/HMA_impact_index/time_test_basin_compile/"
out_path = 'F:/HMA_impact_index/plots/'

os.chdir(in_path)
for file in glob.glob('*index.csv'):
    df = pd.read_csv(file)
    year = df['Year']
    basin_name = df['Basin_ID'][0]
    for col in df.columns[3:]:
        fig, ax = plt.subplots()
        ax.plot(year, df[col])
        fig.suptitle(col, size=14)
        ax.set_xlabel("Year since 2000")
        ax.set_ylabel(col)
        
        from pathlib import Path
        new_out = f"{out_path}{basin_name}/"
        Path(new_out).mkdir(parents=True, exist_ok=True)
        
        plt.savefig((f"{new_out}{col}.png"), dpi=300)
        plt.close()
