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





df = pd.read_csv('csv/straycats3_merged.csv')
df['SEQID'] = pd.to_numeric(df['SEQID'])
df['Module'] = [mod.strip() for mod in df['Module']]

# Greenlist the columns that we want
greenlist = ['SL Target', 'SEQID', 'Module', 'Primary Target', 'Exposure (s)', 'RA',
       'DEC']
for col in df.columns:
    if col not in greenlist:
        df = df.drop(axis=1, labels=col)
        
# Drop everything with NaN in the SL Target column
df = df.dropna(subset=['SL Target'])

df = df.rename(columns={"Exposure (s)": "Exposure"})

df['SL Target'] = df['SL Target'].str.strip()
df['RA'] = pd.to_numeric(df['RA'])
df['DEC'] = pd.to_numeric(df['DEC'])



# Add the MJD start/stop from numaster and figure out if you're public or not

# Set the "public" cutoff date to be Jan 1, 2023
cutoff_t = Time('2023-01-01T00:00:00.123456789', format='isot', scale='utc')
cutoff_mjd = cutoff_t.mjd

numaster = Table.read('fits/numaster.fits', format = 'fits')
    
dn = numaster.to_pandas()

greenlist = ['NAME', 'RA', 'DEC', 'TIME', 'END_TIME',
       'OBSID', 'EXPOSURE_A', 'EXPOSURE_B', 'PUBLIC_DATE']
for col in dn.columns:
    if col not in greenlist:
        dn.drop(col, axis=1, inplace=True)

dn['OBSID'] = pd.to_numeric(dn['OBSID'])
dn['EXPOSURE_A'] = pd.to_numeric(dn['EXPOSURE_A'])
dn['EXPOSURE_B'] = pd.to_numeric(dn['EXPOSURE_B'])
dn['PUBLIC'] = np.where((dn['PUBLIC_DATE']<cutoff_mjd)&(dn['PUBLIC_DATE'] > 0), 'yes', 'no')


# Add MJD start/stop times
init_times = [-1. for x in range(len(df['SEQID']))]
df.insert(loc=4, column='TIME', value=init_times)
df.insert(loc=5, column='END_TIME', value=init_times)


for si in np.unique(df['SEQID']):

    for mod in ['A', 'B']:
        found = df.loc[(df['SEQID'] == si)&(df['Module'] == mod)]
        if len(found) == 0:
            continue
        
        df.loc[(df['SEQID'] == si)&(df['Module'] == mod), 'TIME'] = dn.loc[dn['OBSID'] == si, 'TIME'].values[0]
        df.loc[(df['SEQID'] == si)&(df['Module'] == mod), 'END_TIME'] = dn.loc[dn['OBSID'] == si, 'END_TIME'].values[0]
        df.loc[(df['SEQID'] == si)&(df['Module'] == mod), 'Exposure'] = dn.loc[dn['OBSID'] == si, f'EXPOSURE_{mod}'].values[0]
        


# Collate in the object type information
obj_type = pd.read_csv('csv/target_info.csv')
green_list = ['SL Target', 'Type']
for col in obj_type.columns:
    if col not in green_list:
        if col in obj_type.columns:
            obj_type = obj_type.drop(axis=1,labels=col)
obj_type.head()



# Add target classification and target type
df2 = df.copy()
nrows = len(df2['SEQID'])

classification= ['SL' for x in range(nrows) ]
targ_type= ['??' for x in range(nrows) ]


df2.insert(loc=0, column='Classification', value=classification)
df2.insert(loc=2, column='Target Type', value=targ_type)

for target, ttype in zip(obj_type['SL Target'], obj_type['Type']):
    df2.loc[df2['SL Target'] == target, 'Target Type'] = ttype

# Catch the classifications here    
df2.loc[df2['SL Target'] == '??', 'Classification'] = 'Unk'
## Reset SL Targets to ?? here for each class of object where things aren't clear:

for id in ['Unkn', 'Complex', 'Faint', 'GR', 'Duplicate']:
    df2.loc[df2['SL Target'] == id, 'Classification'] = id
    df2.loc[df2['SL Target'] == id, 'SL Target'] = '??'



# Add a flag to identify sequences with multiple SL sources
count = df2['SEQID'].value_counts()

multi = ['N' for x in range(nrows) ]
df2.insert(loc=5, column='Multi', value=multi)

for seq in count.keys():
    if count[seq] > 1:
        this_seq =df2[df2['SEQID'] == seq]
        mods = this_seq['Module'].value_counts()
        for mod in mods.keys():
            if mods[mod] > 1:
                df2.loc[(df2['SEQID'] == seq) & (df2['Module'] == mod), 'Multi'] = 'Y'
    

# Now we're going to add in the SL for the target location, if it's known.
# For simplicity, we're going to keep both the catalog name and the SIMBAD-safe
# source identifier below.

df2['SIMBAD_ID'] = 'NA'
df2['RA_SL'] = -999
df2['DEC_SL'] = -999



targets = df2['SL Target'].unique()
for target in targets:
    if 'Crab' in target:
        starget = 'Crab'
    elif '1145.1' in target:
        starget = '1E 1145.1-6141'
    elif target == '??':
        continue
    elif 'Streak' in target:
        continue
    elif '1716' in target:
        starget = 'GRS 1716-249'
    elif '16320' in target:
        starget = 'IGR J16320-4751'
    elif 'M1812' in target:
        starget = '4U 1812-12'
    elif '1348' in target:
        starget = 'MAXI J1348-630'
    elif 'J1535' in target:
        starget = 'MAXI J1535-571'
    elif 'J1820' in target:
        starget = 'MAXI J1820+070'
    elif 'Coma' in target:
        starget = 'Coma Cluster'
    elif 'MAXI J1621' in target:
        starget = 'MAXI J1621-501'
    elif 'X1908' in target:
        starget = '1E 1908.4+0730'
    else:
        starget = target
        
    print(starget)
    result_table = Simbad.query_object(starget)

    print(starget, result_table['RA'].data[0])
    ra_tab = result_table['RA'].data[0]
    dec_tab = result_table['DEC'].data[0]
    coord = SkyCoord(ra_tab, dec_tab, unit=(u.hourangle, u.deg))
    
    df2.loc[df2['SL Target'] == target, 'SIMBAD_ID'] = starget
    df2.loc[df2['SL Target'] == target, 'RA_SL'] = coord.ra.deg
    df2.loc[df2['SL Target'] == target, 'DEC_SL'] = coord.dec.deg






# Sort on RA of targeted source:
df2.sort_values(by=['RA', 'TIME', 'Module'], axis=0, inplace=True, ignore_index=True)

# Add catalog ID as column:
slid = [f'StrayCatsIII_{x}' for x in df2.index]
df2.insert(loc = 0, 
          column = 'STRAYID', 
          value = slid)


# Final editing:
# change SL Target to SL Source
df2 = df2.rename(columns={"SL Target": "SL Source"})
df2 = df2.rename(columns={"Primary Target": "Primary"})
df2 = df2.rename(columns={"RA": "RA_PRIMARY"})
df2 = df2.rename(columns={"DEC": "DEC_PRIMARY"})
df2 = df2.rename(columns={"Target Type": "SL Type"})

# Change ordering
exp = df2['Exposure']
df2.drop(labels=['Exposure'], axis=1,inplace = True)
df2.insert(6, 'Exposure', exp)

sl = df2['SL Source']
df2.drop(labels=['SL Source'], axis=1,inplace = True)
df2.insert(12, 'SL Source', sl)

sltype = df2['SL Type']
df2.drop(labels=['SL Type'], axis=1,inplace = True)
df2.insert(12, 'SL Type', sltype)




# Convert back to a FITS table and write this out
tab = Table.from_pandas(df2)
tab.write('fits/straycats_incr3.fits', overwrite=True)

# Read the v1
# from astropy.table import vstack
# 
# v1 = Table.read('fits/straycats2_0.fits', format = 'fits')
# v2_incr = Table.read('fits/straycats_incr3.fits', format = 'fits')
# v2 = vstack([v1, v2_incr])
# v2.write('fits/straycats_v.fits', overwrite=True)
# 


