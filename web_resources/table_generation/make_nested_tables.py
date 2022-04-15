from astropy.table import Table
import numpy as np
import urllib

sf = '../../straycats.fits'
straycat = Table.read(sf)
for key in straycat.columns:
    if straycat[key].dtype.str.startswith('|S'):
        straycat[key] = straycat[key].astype('str') 
df = straycat.to_pandas()
df.columns

# Strip out unknowns:
sl = df[(df['Classification']=='SL') & (df['RA_SL'] > 0)].copy().reset_index(drop=True)
sl = sl.drop(['END_TIME', 'Multi'], axis=1)

# Get unique number of seqid rows:

uniq_sl = sl.copy()
uniq_sl['Number of Obs'] = ""

nobs = uniq_sl['SL Source'].value_counts()

for source in np.unique(uniq_sl['SL Source']):

    uniq_sl['Number of Obs'].loc[uniq_sl['SL Source'] == source] = nobs[source]
    
    
greenlist = ['SL Source', 'RA_SL', 'DEC_SL', 'Number of Obs']
for key in uniq_sl.columns:
    if key not in greenlist:
        uniq_sl = uniq_sl.drop(key, axis=1).reset_index(drop=True)
print(uniq_sl.columns)
uniq_sl = uniq_sl.drop_duplicates(subset=['SL Source']).reset_index(drop=True)
uniq_sl = uniq_sl.sort_values('RA_SL').reset_index(drop=True)

print(uniq_sl.head)


# seqid_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/seqid'
source_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/sources'

uniq_sl['SL Source'] = [f'<a href="{source_base}/{urllib.parse.quote(source)}" >{source} </a>' for source in uniq_sl['SL Source']]


# uniq_sl['SEQID'] = 

#sl['SL Target'] = [f'<a href="./sources/{source}" >{source} </a>' for source in sl['SL Target']]

sl_html = uniq_sl.to_html(classes=["table-bordered", "table-striped", "table-hover",],
                     index=False, justify="initial", escape=False)
with open('straycats_summary.html', 'w') as f:
    for line in sl_html:
        f.write(line)

