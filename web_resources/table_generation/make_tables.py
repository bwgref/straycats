from astropy.table import Table
sf = '../../straycats.fits'
straycat = Table.read(sf)
for key in straycat.columns:
    if straycat[key].dtype.str.startswith('|S'):
        straycat[key] = straycat[key].astype('str') 
df = straycat.to_pandas()
df.columns

# Strip out unknowns:
sl = df[df['Classification']=='SL'].copy().reset_index(drop=True)

sl = df.copy()
sl = sl.drop(['END_TIME', 'Multi'], axis=1)

# Get unique number of seqid rows:

#uniq_sl = sl.drop_duplicates(subset=['SEQID'])
uniq_sl = sl.copy()

seqid_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/seqid'
source_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/source'

uniq_sl['SEQID'] = [f'<a href="{seqid_base}/{seqid}" >{seqid} </a>' for seqid in uniq_sl['SEQID']]

#sl['SL Target'] = [f'<a href="./sources/{source}" >{source} </a>' for source in sl['SL Target']]

sl_html = uniq_sl.to_html(classes=["table-bordered", "table-striped", "table-hover",],
                     index=False, justify="initial", escape=False)
with open('straycats_table.html', 'w') as f:
    for line in sl_html:
        f.write(line)


# Sort on SL Source

sorted_uniq = uniq_sl[uniq_sl['Classification'] == 'SL']
sorted_uniq = sorted_uniq.sort_values(by='RA_SL')

sorted_sl_html = sorted_uniq.to_html(classes=["table-bordered", "table-striped", "table-hover",],
                     index=False, justify="initial", escape=False)
with open('straycats_sorted_table.html', 'w') as f:
    for line in sorted_sl_html:
        f.write(line)




# Same thing, but only unknowns and the streak

sl = df[df['Classification']=='Unkn'].copy().reset_index(drop=True)
sl = sl.drop(['END_TIME', 'Multi', 'Classification'], axis=1)

# Get unique number of seqid rows:

#uniq_sl = sl.drop_duplicates(subset=['SEQID'])
uniq_sl = sl.copy()

seqid_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/seqid'
source_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/source'



uniq_sl['SEQID'] = [f'<a href="{seqid_base}/{seqid}" >{seqid} </a>' for seqid in uniq_sl['SEQID']]

#sl['SL Target'] = [f'<a href="./sources/{source}" >{source} </a>' for source in sl['SL Target']]

sl_html = uniq_sl.to_html(classes=["table-bordered", "table-striped", "table-hover",],
                     index=False, justify="initial", escape=False)
with open('straycats_table_unknowns.html', 'w') as f:
    for line in sl_html:
        f.write(line)
        
        
# Same thing, but only complex:

# Strip out unknowns:
sl = df[df['Classification']=='Complex'].copy().reset_index(drop=True)
sl = sl.drop(['END_TIME', 'Multi', 'Module', 'Classification'], axis=1)

# Get unique number of seqid rows:

#uniq_sl = sl.drop_duplicates(subset=['SEQID'])
uniq_sl = sl.copy()

seqid_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/seqid'
source_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/source'

uniq_sl['SEQID'] = [f'<a href="{seqid_base}/{seqid}" >{seqid} </a>' for seqid in uniq_sl['SEQID']]

#sl['SL Target'] = [f'<a href="./sources/{source}" >{source} </a>' for source in sl['SL Target']]

sl_html = uniq_sl.to_html(classes=["table-bordered", "table-striped", "table-hover",],
                     index=False, justify="initial", escape=False)
with open('straycats_table_complex.html', 'w') as f:
    for line in sl_html:
        f.write(line)
        
# sl_md = sl.to_markdown(index=False)
# with open('straycats_table.md', 'w') as f:
#     for line in sl_md:
#         f.write(line)