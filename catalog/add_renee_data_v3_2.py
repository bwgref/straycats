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


# Note, do this on the FULL DATA SET not on the incremental update for the v3_3
# March 2024 release!

sc2 = Table.read('fits/straycats_v3_2d.fits', format = 'fits')

for key in sc2.columns:
    if sc2[key].dtype.str.startswith('|S'):
        sc2[key] = sc2[key].astype('str') 
df = sc2.to_pandas()
df.columns
meta2 = Table.read('fits/straycats_v3_0.fits')

for key in meta2.columns:
    if meta2[key].dtype.str.startswith('|S'):
        meta2[key] = meta2[key].astype('str') 
df2 = meta2.to_pandas()


df = sc2.to_pandas()
# Remove whitesapce from GRs
df2 = meta2.to_pandas()
df2 = df2[df2['Classification'] != 'Duplicate'].copy()
df2['Classification'] = df2['Classification'].str.strip()



rows = len(df)
greenlist = []
for key in df2.columns:
    if key not in df.columns:
        if key not in ('STAYID', 'SEQID', 'MJD', 'Exposure'):
            print(key)
            greenlist = np.append(greenlist, key)
            newcol = [-999.0 for x in range(rows)]
            df[key] = newcol

print(key)
# We don't have the meta data yet, so don't copy this over

for key in greenlist:
    print(key)
    for row in df2.iterrows():
        df.loc[df['StrayID'] == row[1]['STRAYID'], key] = row[1][key]
#     

tab = Table.from_pandas(df)
tab.write('fits/straycats_v3_3d.fits', overwrite=True)