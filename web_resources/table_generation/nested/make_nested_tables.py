from astropy.table import Table
import numpy as np
import urllib
from astropy.time import Time
import os
from glob import glob
import shutil

seqid_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/seqid'

sf = '../../../straycats.fits'
straycat = Table.read(sf)
for key in straycat.columns:
    if straycat[key].dtype.str.startswith('|S'):
        straycat[key] = straycat[key].astype('str') 
df = straycat.to_pandas()
df.columns

# Strip out unknowns:
sl = df[(df['Classification']=='SL') & (df['RA_SL'] > 0)].copy().reset_index(drop=True)
sl = sl.drop(['END_TIME', 'Multi'], axis=1)

# Reformat as necessary

sl['Exposure'] = sl['Exposure'] / 1e3
sl['Exposure (ks)'] = sl['Exposure'].map('{:.2f}'.format)
sl['MJD'] = sl['TIME'].map('{:.1f}'.format)
sl['Area (cm2)'] = sl['Area (cm2)'].map('{:.1f}'.format)
sl['Date'] = [Time(x, format = 'mjd').iso for x in sl['TIME']]

sl['Region'] = sl['SEQID'].astype(str)+sl['Module']+'_'+sl['STRAYID']


for key in ['HR', 'Error HR', '3-8 keV count/s/cm2', 'Error 3-8 keV count/s/cm2',
       '8-13 keV count/s/cm2', 'Error 8-13 keV count/s/cm2',
       '3-8 keV bkgd count/s/cm2', 'Error 3-8 keV bkgd count/s/cm2',
       '8-13 keV bkgd count/s/cm2', 'Error 8-13 keV bkgd count/s/cm2']:
    sl[key] = sl[key].map('{:.3f}'.format)


# Get unique number of seqid rows:

uniq_sl = sl.copy()
uniq_sl['Number of Obs'] = ""

nobs = uniq_sl['SL Source'].value_counts()

summary_redlist = ['SL Source', 'SL Type', 'RA_SL', 'DEC_SL', 'Number of Obs']
summary_greenlist = ['MJD', 'Date', 'Module',
                    'Classification', 'Primary', 
                    'SEQID','Exposure (ks)', 'Area (cm2)',
                    '3-8 keV count/s/cm2', '8-13 keV count/s/cm2', 'HR', 'Region']


for source in np.unique(uniq_sl['SL Source']):
    uniq_sl['Number of Obs'].loc[uniq_sl['SL Source'] == source] = nobs[source]
    this_src = uniq_sl[uniq_sl['SL Source'] == source].copy().reset_index(drop=True)
    
    sname = source.replace(" ", "")
    this_summary = f'{sname}_summary.html'
    
    this_src = this_src[summary_greenlist]
    this_src = this_src.sort_values('MJD', axis = 0)
    
    if not os.path.isdir(sname):
        print(os.path.isdir)
        os.mkdir(sname)
    this_summary = os.path.join(sname, this_summary)
    
#     for key in this_src.columns:
#         if key in summary_redlist:
#             this_src = this_src.drop(key, axis=1).reset_index(drop=True)

    this_src['SEQID'] = [f'<a href="{seqid_base}/{seqid}" >{seqid} </a>' for seqid in this_src['SEQID']]    

    for reg in this_src['Region']:
        rfile = os.path.join('./SL_regions', f'{reg}.reg')
        if os.path.isfile(rfile):
            shutil.copy(rfile, f'./{sname}')
    
        
    this_src['Region'] = [f'<a href="{reg}.reg" >{reg}.reg </a>' for reg in this_src['Region']]

    
    # Find the lightcurve PDF
    
    lcname = sname
    if '+' in lcname: 
        lcname = lcname.replace('+', 'p')
    if '-' in lcname:
        lcname = lcname.replace('-', 'm')
        
    src_query= f'./png/*{lcname}*png'
    lc_pdf = glob(src_query)
    if len(lc_pdf) != 1:
        no_lc = True
        print('########')
        print('LIGHTCURVE NOTE FOUND!!!!!!!')
        print(src_query)
        print(lc_pdf)
        print('########')
    else: 
        no_lc=False
        shutil.copy(lc_pdf[0], f'./{sname}/')
        lc_file = os.path.basename(lc_pdf[0])


    with open(this_summary, 'w') as f:
        f.write('<header>')
        f.write(f'<h1> {source}</h1>\n')
        f.write('</header>\n')
        f.write('<body>\n')
        f.write('<center>\n')
        if no_lc:
            f.write(f'<h2> Lightcurve not available </h2>\n')
        f.write(f'<embed src={lc_file} width="600pix" height="460pix" class="center"/>\n')
#        f.write(f'<img src={lc_file}  width="100%" height="460pix" class="center"/>\n')

        f.write('<p>\n')
        f.write('Blue is MAXI 3--20 keV, grey is BAT 15-50 keV (when available). ')
        f.write('Vertical red lines are focused NuSTAR observations, dashed black lines are the StrayCats observations listed below.')
        f.write('</p>\n')
        for line in this_src.to_html(classes=["table-bordered", "table-striped", "table-hover",],
                     index=False, justify="initial", escape=False):
            f.write(line)
        f.write('</center>')
        
    
    
    
    
greenlist = ['SL Source', 'SL Type', 'RA_SL', 'DEC_SL', 'Number of Obs']
for key in uniq_sl.columns:
    if key not in greenlist:
        uniq_sl = uniq_sl.drop(key, axis=1).reset_index(drop=True)
uniq_sl = uniq_sl.drop_duplicates(subset=['SL Source']).reset_index(drop=True)
uniq_sl = uniq_sl.sort_values('RA_SL').reset_index(drop=True)



# seqid_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/seqid'
source_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/sources'

#uniq_sl['SL Source'] = [f'<a href="{source_base}/{urllib.parse.quote(source)}" >{source} </a>' for source in uniq_sl['SL Source']]
uniq_sl['sname'] = [x.replace(' ' , '') for x in uniq_sl['SL Source']]
#uniq_sl['SL Source'] = [f'<a href={sname}/{sname}_summary.html > {sname} </a>' for sname in uniq_sl['sname']]
uniq_sl['SL Source'] = [f'[{sname}]({sname}/{sname}_summary.html)' for sname in uniq_sl['sname']]


uniq_sl = uniq_sl.drop(['sname'], axis=1).reset_index(drop=True)


sl_md = uniq_sl.to_markdown('straycats_summary.md', index=False)


uniq_sl.to_html('straycats_summary.html', index=False, escape=False,
    classes=["table-bordered", "table-striped", "table-hover"])

# 
# with open('straycats_summary.md', 'w') as f:
#     for line in sl_md:
#         f.write(line)

