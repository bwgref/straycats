import numpy as np
import pandas as pd
from astropy.table import Table
from astropy.io.fits import getdata
from astropy.time import Time
from astropy.io import fits

# Read base CSV from the Google drive

df = pd.read_csv('csv/full_merged.csv')
df.head()

# Greenlist the columns that we want
greenlist = ['SL Target', 'SEQID', 'Module', 'Primary Target', 'Exposure (s)', 'RA',
       'DEC', 'Notes']
for col in df.columns:
    if col not in greenlist:
        df = df.drop(axis=1, labels=col)
        
# Drop everything with NaN in the SL Target column
df = df.dropna(subset=['SL Target'])

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
dn.columns

dn['PUBLIC'] = np.where((dn['PUBLIC_DATE']<cutoff_mjd)&(dn['PUBLIC_DATE'] > 0), 'yes', 'no')


# Add MJD start/stop times
df['TIME'] = [-1. for x in range(len(df['SEQID']))]
df['END_TIME'] = [-1. for x in range(len(df['SEQID']))]

for si in np.unique(df['SEQID']):
#    print(dn.loc[dn['OBSID'] == si, 'TIME'].values[0])
    df.loc[df['SEQID'] == si, 'TIME'] = dn.loc[dn['OBSID'] == si, 'TIME'].values[0]
    df.loc[df['SEQID'] == si, 'END_TIME'] = dn.loc[dn['OBSID'] == si, 'END_TIME'].values[0]


# Collate in the object type information
obj_type = pd.read_csv('csv/target_info.csv')
green_list = ['Confirmed Sources', 'Type']
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

for target, ttype in zip(obj_type['Confirmed Sources'], obj_type['Type']):
    df2.loc[df2['SL Target'] == target, 'Target Type'] = ttype
    
df2.loc[df2['SL Target'] == '??', 'Classification'] = 'Unk'



# Now convert to FITS table with this horrible hack around:
arr = df2.to_numpy()

# Make the columns the silly way here:

classification = fits.Column(name='CLASSIFICATION', format='10A', array=arr[:, 0])
target = fits.Column(name='SL_SOURCE', format='10A', array=arr[:,1])
ttype = fits.Column(name='TYPE', format='4A', array=arr[:,2])
obsid = fits.Column(name='OBSID', format='12A', array=arr[:,3])
mod = fits.Column(name='MODULE', format='2A', array=arr[:,4])
primary = fits.Column(name='PRIMARY_TARGET', format = '30A', array=arr[:,5])
exposure = fits.Column(name='EXPOSURE', format = 'E', array=[float(e) for e in arr[:,6]])
ra = fits.Column(name='RA', format='E', array =  arr[:, 7])
dec = fits.Column(name='DEC', format='E', array =  arr[:, 8])
tstart = fits.Column(name='TIME', format='E', array = arr[:, 10])
tend = fits.Column(name='TIME_END', format='E', array = arr[:, 11])
notes = fits.Column(name='NOTES', format='30A', array = arr[:, 9])

hdu = fits.BinTableHDU.from_columns([classification, target,ttype, obsid, mod, primary, exposure, ra, dec, tstart, tend, notes])
hdu.writeto('fits/straycats.fits', overwrite=True)

# FIN