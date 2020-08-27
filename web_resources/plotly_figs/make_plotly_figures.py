from astropy.table import Table
from astropy.io.fits import getdata
import pandas as pd
import astropy.units as u
from astropy.coordinates import SkyCoord
import numpy as np
from astroquery.simbad import Simbad

import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go


# Read and convert to pandas
sf = '../../catalog/fits/straycats.fits'
straycat = Table.read(sf)
for key in straycat.columns:
    if straycat[key].dtype.str.startswith('|S'):
        straycat[key] = straycat[key].astype('str') 
df = straycat.to_pandas()

# 
# 
# # Create galactic coordinates:
ra = df['RA'].values
dec = df['DEC'].values
coords = SkyCoord(ra, dec, unit = 'deg')
# Create galactic coordiantes:
ra = df['RA'].values
dec = df['DEC'].values
df['GalLon']= coords.galactic.l.deg
df['GalLat']= coords.galactic.b.deg
# 
# # Get the location of the SL targets
ra = []
dec = []
gal_lat = []
gal_lon =[]
names = []
sl = df[df['Classification'] == 'SL'].copy().reset_index(drop=True)
targets = sl['SL Target'].unique()
for target in targets:

    result_table = Simbad.query_object(target)
    if result_table is None:
        continue
    ra_tab = result_table['RA'].data.data[0]
    dec_tab = result_table['DEC'].data.data[0]
    coord = SkyCoord(ra_tab, dec_tab, unit=(u.hourangle, u.deg))
    
    ra = np.append(ra, coord.ra.deg)
    dec = np.append(dec, coord.dec.deg)
    gal_lat = np.append(gal_lat, coord.galactic.b.deg)
    gal_lon = np.append(gal_lon, coord.galactic.l.deg)
    names = np.append(names, target)
 

hover_list = ['SEQID','SL Target', 'Primary Target', 'TIME','Exposure', 'Classification', 'Notes']


######
## Make the galactic coordinates plot ##
######

df['PlotLon'] = (df['GalLon'] + 180)%360 - 180
fig = px.scatter(df, x='PlotLon', y='GalLat'
                 ,size='Exposure'
                  , hover_data=hover_list
                  ,color= 'Target Type')

fig.add_trace(go.Scatter(x=( (gal_lon + 180)%360-180), y= gal_lat,
                    mode='markers',
                    name='SL Sources',
                    text=names, marker_symbol='x'))
fig.update_layout(template='plotly_white')
fig.update_layout(title='Catalog Snapshot')

fig.update_layout(yaxis=dict(range=[-100,100]),xaxis=dict(range=[190, -190]))
pio.write_html(fig, file='straycat_galactic.html')
# 
# ######
# ## Do the RA/DEC one: ##
# ######
fig = px.scatter(df, x='RA', y='DEC'
                 ,size='Exposure'
                  , hover_data=hover_list
                  ,color= 'Target Type')
fig.add_trace(go.Scatter(x=ra, y= dec,
                    mode='markers',
                    name='SL Sources',
                    text=names, marker_symbol='x'))
fig.update_layout(template='plotly_white')
fig.update_layout(title='Catalog Snapshot')

fig.update_layout(yaxis=dict(range=[-95,95]),xaxis=dict(range=[360, 0]))
pio.write_html(fig, file='straycat_radec.html')

# 
# 
# 
# ######
# # Galactic overlay figure
# ######
# 
fig = go.Figure()
# Constants
img_width = 1600
img_height = 900
scale_factor = 0.5

scalex=scale_factor*img_width*( ( ( (360 - df['GalLon']) + 180) % 360) / 360)
scaley=0.5*scale_factor*img_height*(df['GalLat']/90) + 0.5*scale_factor*img_height

df['x'] = scalex
df['y'] = scaley

fig = px.scatter(df, x='x', y='y'
                 ,size='Exposure'
                  , hover_data=hover_list
                  ,color= 'Target Type', opacity=0.8)
                  
                  
fig.update_xaxes(
    visible=False,
    range=[0, img_width * scale_factor]
)

fig.update_yaxes(
    visible=False,
    range=[0, img_height * scale_factor],
    # the scaleanchor attribute ensures that the aspect ratio stays constant
    scaleanchor="x"
)


fig.add_layout_image(
        dict(
            source="https://cdn.eso.org/images/large/eso0932a.jpg",
            xref="x",
            yref="y",
            x=0,
            sizex=img_width * scale_factor,
            y=img_height * scale_factor,
            sizey=img_height * scale_factor,
            sizing="stretch",
            layer="below")
)


fig.update_layout(template='plotly_white')
fig.update_layout(title='Galaxy Overlay')
pio.write_html(fig, file='galaxy_overlay.html')

# 
# #By ESO/S. Brunier - http://www.eso.org/public/images/eso0932a/, CC BY 4.0, https://commons.wikimedia.org/w/index.php?curid=9559670
# 
