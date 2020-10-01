from astropy.table import Table
sf = '../../catalog/fits/straycats.fits'
straycat = Table.read(sf)
for key in straycat.columns:
    if straycat[key].dtype.str.startswith('|S'):
        straycat[key] = straycat[key].astype('str') 
df = straycat.to_pandas()
df.columns

# Strip out unknowns:
sl = df[df['Classification']=='SL'].copy().reset_index(drop=True)
sl = sl.drop(['END_TIME', 'Multi', 'Classification'], axis=1)

# Get unique number of seqid rows:

#uniq_sl = sl.drop_duplicates(subset=['SEQID'])
uniq_sl = sl.copy()

seqid_base = 'https://github.com/bwgref/straycats/tree/master/web_resources/seqid'
source_base = 'https://github.com/bwgref/straycats/tree/master/web_resources/source'

uniq_sl['SEQID'] = [f'<a href="{seqid_base}/{seqid}" >{seqid} </a>' for seqid in uniq_sl['SEQID']]

#sl['SL Target'] = [f'<a href="./sources/{source}" >{source} </a>' for source in sl['SL Target']]

sl_html = uniq_sl.to_html(classes=["table-bordered", "table-striped", "table-hover",],
                     index=False, justify="initial", escape=False)
with open('straycats_table.html', 'w') as f:
    for line in sl_html:
        f.write(line)

# Same thing, but only unknowns

sl = df[df['Classification']=='Unkn'].copy().reset_index(drop=True)
sl = sl.drop(['END_TIME', 'Multi', 'Classification'], axis=1)

# Get unique number of seqid rows:

#uniq_sl = sl.drop_duplicates(subset=['SEQID'])
uniq_sl = sl.copy()

seqid_base = 'https://github.com/bwgref/straycats/tree/master/web_resources/seqid'
source_base = 'https://github.com/bwgref/straycats/tree/master/web_resources/source'



uniq_sl['SEQID'] = [f'<a href="{seqid_base}/{seqid}" >{seqid} </a>' for seqid in uniq_sl['SEQID']]

#sl['SL Target'] = [f'<a href="./sources/{source}" >{source} </a>' for source in sl['SL Target']]

sl_html = uniq_sl.to_html(classes=["table-bordered", "table-striped", "table-hover",],
                     index=False, justify="initial", escape=False)
with open('straycats_table_unknowns.html', 'w') as f:
    for line in sl_html:
        f.write(line)
        