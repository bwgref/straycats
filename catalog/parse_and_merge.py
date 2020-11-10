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




# Read base CSV from the Google drive

df = pd.read_csv('csv/full_merged.csv')

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

# Set the "public" cutoff date to be June 1, 2020
cutoff_t = Time('2020-06-01T00:00:00.123456789', format='isot', scale='utc')
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

#df['END_TIME'] = [-1. for x in range(len(df['SEQID']))]

for si in np.unique(df['SEQID']):
#    print(dn.loc[dn['OBSID'] == si, 'TIME'].values[0])
    # Loop over A/B:
    for mod in ['A', 'B']:
        
        df.loc[(df['SEQID'] == si)&(df['Module'] == mod), 'TIME'] = dn.loc[dn['OBSID'] == si, 'TIME'].values[0]
        df.loc[(df['SEQID'] == si)&(df['Module'] == mod), 'END_TIME'] = dn.loc[dn['OBSID'] == si, 'END_TIME'].values[0]
        df.loc[(df['SEQID'] == si)&(df['Module'] == mod), 'Exposure'] = dn.loc[dn['OBSID'] == si, f'EXPOSURE_{mod}'].values[0]
 
   
#    df.loc[df['SEQID'] == si, 'TIME'] = dn.loc[dn['OBSID'] == si, 'TIME'].values[0]
#    df.loc[df['SEQID'] == si, 'END_TIME'] = dn.loc[dn['OBSID'] == si, 'END_TIME'].values[0]
#sys.exit()




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

for id in ['Unkn', 'Complex', 'Faint', 'GR']:
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
        
    result_table = Simbad.query_object(starget)


    ra_tab = result_table['RA'].data.data[0]
    dec_tab = result_table['DEC'].data.data[0]
    coord = SkyCoord(ra_tab, dec_tab, unit=(u.hourangle, u.deg))
    
    df2.loc[df2['SL Target'] == target, 'SIMBAD_ID'] = starget
    df2.loc[df2['SL Target'] == target, 'RA_SL'] = coord.ra.deg
    df2.loc[df2['SL Target'] == target, 'DEC_SL'] = coord.dec.deg






# Sort on RA of targeted source:
df2.sort_values(by=['RA', 'TIME', 'Module'], axis=0, inplace=True, ignore_index=True)

# Add catalog ID as column:
slid = [f'StrayCatsI_{x}' for x in df2.index]
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
tab.write('fits/straycats.fits', overwrite=True)
# # Now convert to FITS table with this horrible hack around:
# arr = df2.to_numpy()

# # Make the columns the silly way here:

# classification = fits.Column(name='CLASSIFICATION', format='10A', array=arr[:, 0])
# target = fits.Column(name='SL_SOURCE', format='10A', array=arr[:,1])
# ttype = fits.Column(name='TYPE', format='4A', array=arr[:,2])
# obsid = fits.Column(name='OBSID', format='12A', array=arr[:,3])
# mod = fits.Column(name='MODULE', format='2A', array=arr[:,4])
# primary = fits.Column(name='PRIMARY_TARGET', format = '30A', array=arr[:,5])
# exposure = fits.Column(name='EXPOSURE', format = 'E', array=[float(e) for e in arr[:,6]])
# ra = fits.Column(name='RA', format='E', array =  arr[:, 7])
# dec = fits.Column(name='DEC', format='E', array =  arr[:, 8])
# tstart = fits.Column(name='TIME', format='E', array = arr[:, 10])
# tend = fits.Column(name='TIME_END', format='E', array = arr[:, 11])
# notes = fits.Column(name='NOTES', format='30A', array = arr[:, 9])

# hdu = fits.BinTableHDU.from_columns([classification, target,ttype, obsid, mod, primary, exposure, ra, dec, tstart, tend, notes])
# hdu.writeto('fits/straycats.fits', overwrite=True)

# # FIN