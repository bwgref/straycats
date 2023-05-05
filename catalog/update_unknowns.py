import numpy as np
import pandas as pd
from astropy.table import Table
from astropy.io.fits import getdata
from astropy.time import Time
from astropy.io import fits
import sys
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u



sc2 = Table.read('fits/straycats_v3.fits', format = 'fits')

for key in sc2.columns:
    if sc2[key].dtype.str.startswith('|S'):
        sc2[key] = sc2[key].astype('str') 
df = sc2.to_pandas()
df.columns
meta2 = Table.read('fits/StrayCats_SLsources_3arcminbkg.fits')

for key in meta2.columns:
    if meta2[key].dtype.str.startswith('|S'):
        meta2[key] = meta2[key].astype('str') 
df2 = meta2.to_pandas()


df = sc2.to_pandas()
df = df[df['Classification'] != 'Duplicate'].copy()
# Remove whitesapce from GRs
df['Classification'] = df['Classification'].str.strip()
df2 = meta2.to_pandas()



rows = len(df)
greenlist = []
for key in df2.columns:
    if key not in df.columns:
        if key not in ('StrayID', 'ObsID', 'MJD', 'Exposure (s)'):
            print(key)
            greenlist = np.append(greenlist, key)
            newcol = [-999.0 for x in range(rows)]
            df[key] = newcol
            
            
for row in df2.iterrows():
    for key in greenlist:
        df[key].loc[df['STRAYID'] == row[1]['StrayID']] = row[1][key]
    

tab = Table.from_pandas(df)
tab.write('fits/straycats_v3.fits', overwrite=True)