from astropy.table import Table
from astropy.io.fits import getdata
import pandas as pd
import astropy.units as u
from astropy.coordinates import SkyCoord

sf = '../catalog/fits/straycats.fits'

straycat = Table.read(sf)


for key in straycat.columns:
    if straycat[key].dtype.str.startswith('|S'):
        straycat[key] = straycat[key].astype('str') 
df = straycat.to_pandas()

# Create galactic coordiantes:

ra = df['RA'].values
dec = df['DEC'].values

coords = SkyCoord(ra, dec, unit = 'deg')
df['GalLon']= coords.galactic.l.deg
df['GalLat']= coords.galactic.b.deg

import plotly.express as px
import plotly.io as pio


fig = px.scatter(df, x='GalLon', y='GalLat'
                 ,size='Exposure (s)'
                  , hover_data=['SL Target', 'Primary Target', 'Exposure (s)', 'Notes']
                  ,color= 'Target Type')

fig.update_layout(template='plotly_white')
fig.update_layout(title='Catalog Snapshot')

fig.update_layout(yaxis=dict(range=[-100,100]))


pio.write_html(fig, file='straycat_galactic.html')


import plotly.express as px
import plotly.io as pio


fig = px.scatter(df, x='RA', y='DEC'
                 ,size='Exposure (s)'
                  , hover_data=['SL Target', 'Primary Target', 'Exposure (s)', 'Notes']
                  ,color= 'Target Type')

fig.update_layout(template='plotly_white')
fig.update_layout(title='Catalog Snapshot')

fig.update_layout(yaxis=dict(range=[-100,100]))


pio.write_html(fig, file='straycat_radec.html')


